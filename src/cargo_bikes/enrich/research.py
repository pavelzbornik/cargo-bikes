"""Research flagged notes using web search to fill missing frontmatter fields.

Processes notes with needs_research: true, uses Claude Agent SDK with
WebSearch/WebFetch to find missing specs, then merges via Pydantic extraction.
"""

from __future__ import annotations

import asyncio
import json
import re
from pathlib import Path
from typing import Any

import yaml
from claude_agent_sdk import (
    AssistantMessage,
    ClaudeAgentOptions,
    ResultMessage,
    TextBlock,
)
from claude_agent_sdk import (
    query as sdk_query,
)

from cargo_bikes.enrich.agent import _clean_response
from cargo_bikes.enrich.prompts import RESEARCH_SYSTEM
from cargo_bikes.enrich.schemas import BikeExtraction, BrandExtraction
from cargo_bikes.vault.frontmatter import extract_frontmatter


def _strip_frontmatter(content: str) -> str:
    """Return body content without YAML frontmatter."""
    match = re.match(r"^---\s*\n.*?\n---\s*\n", content, re.DOTALL)
    return content[match.end() :] if match else content


def _scan_flagged(vault_path: Path, brand: str | None = None) -> list[Path]:
    """Find all notes with needs_research: true."""
    bikes_dir = vault_path / "notes" / "bikes"
    flagged: list[Path] = []

    dirs = [bikes_dir / brand] if brand else sorted(bikes_dir.iterdir())

    for brand_dir in dirs:
        if not brand_dir.is_dir():
            continue
        for md_file in sorted(brand_dir.glob("*.md")):
            if md_file.name == "index.md" or md_file.name.endswith(".fr.md"):
                continue
            if "accessories" in md_file.parts:
                continue
            try:
                fm = extract_frontmatter(md_file.read_text(encoding="utf-8"))
                if fm and fm.get("needs_research"):
                    flagged.append(md_file)
            except Exception:
                continue

    return flagged


async def _research_one(
    file_path: Path,
    model: str,
) -> dict[str, Any] | None:
    """Research a single flagged note using web search."""
    content = file_path.read_text(encoding="utf-8")
    fm = extract_frontmatter(content)
    if not fm:
        return None

    note_type = fm.get("type", "")
    if note_type == "bike":
        schema = BikeExtraction
    elif note_type in ("brand", "brand-index"):
        schema = BrandExtraction
    else:
        return None

    title = fm.get("title", file_path.stem)
    brand = fm.get("brand", "")
    url = fm.get("url", "")
    topics = fm.get("research_topics", [])

    if not topics:
        return None

    # Build field descriptions from schema
    schema_json = schema.model_json_schema()
    props = schema_json.get("properties", {})
    field_desc = "\n".join(
        f"  {name}: {info.get('description', 'any')}"
        for name, info in props.items()
        if name in topics
    )

    prompt = f"""Research this cargo bike and extract missing specifications.

Bike: {title}
Brand: {brand}
URL: {url}

Missing fields to find:
{field_desc}

Search the web for "{title}" specifications. Check the manufacturer website{f" at {url}" if url else ""} and review sites.
Return ONLY a JSON object with the fields you found. Use null for fields not found.
No markdown, no explanation, no code fences."""

    try:
        options = ClaudeAgentOptions(
            model=model,
            max_turns=5,
            allowed_tools=["WebSearch", "WebFetch"],
        )
        options.system_prompt = RESEARCH_SYSTEM

        accumulated: list[str] = []
        result_text = ""
        async for msg in sdk_query(prompt=prompt, options=options):
            if isinstance(msg, AssistantMessage):
                for block in msg.content:
                    if isinstance(block, TextBlock) or (
                        hasattr(block, "text")
                        and hasattr(block, "type")
                        and getattr(block, "type", None) == "text"
                    ):
                        accumulated.append(block.text)
            elif isinstance(msg, ResultMessage):
                result_text = msg.result or ""

        raw = result_text if result_text.strip() else "\n".join(accumulated)
        result = _clean_response(raw)
        if not result and raw:
            print(f"    [DBG] raw={len(raw)}b cleaned to empty. First 100: {raw[:100]}")
    except Exception as e:
        print(f"  [WARN] Research failed for {file_path.name}: {e}")
        return None

    if not result:
        return None

    # Parse JSON from response
    result = result.replace("\r\n", "\n").strip()
    fence_match = re.search(r"```(?:json)?\s*\n(.*?)```", result, re.DOTALL)
    if fence_match:
        result = fence_match.group(1).strip()

    json_match = re.search(r"\{.*\}", result, re.DOTALL)
    if not json_match:
        print(f"    [DBG] no JSON in: {result[:100]}")
        return None

    try:
        data = json.loads(json_match.group(0))
        # Coerce types: Claude sometimes returns int for string fields
        for k, v in list(data.items()):
            if isinstance(v, (int, float)) and k in (
                "wheels_front_size_in",
                "wheels_rear_size_in",
                "drivetrain_speeds",
                "price_amount",
                "range_estimate_km",
                "battery_charging_time_h",
                "frame_size",
            ):
                data[k] = str(v)
        extracted = schema(**data)
    except Exception as e:
        print(f"    [DBG] parse error: {e}")
        return None

    # Find which fields are already filled
    filled = {k for k, v in fm.items() if v is not None and v != "" and v != []}

    new_fields = {
        k: v
        for k, v in extracted.model_dump().items()
        if v is not None and k not in filled
    }

    if not new_fields:
        return None

    return {
        "file_path": file_path,
        "extracted": new_fields,
        "title": title,
        "topics": topics,
    }


def _apply_research(file_path: Path, extracted: dict[str, Any]) -> None:
    """Merge researched fields and clear the needs_research flag."""
    content = file_path.read_text(encoding="utf-8")

    fm_match = re.match(r"^---\s*\n(.*?)\n---\s*\n", content, re.DOTALL)
    if not fm_match:
        return

    fm = yaml.safe_load(fm_match.group(1))
    if not isinstance(fm, dict):
        return

    body = content[fm_match.end() :]

    # Merge new fields
    for key, value in extracted.items():
        if key not in fm or fm[key] is None or fm[key] == "":
            fm[key] = value

    # Update research_topics: remove found fields
    remaining = [t for t in fm.get("research_topics", []) if t not in extracted]
    if remaining:
        fm["research_topics"] = remaining
    else:
        # All topics resolved — clear the flag
        fm.pop("needs_research", None)
        fm.pop("research_topics", None)

    new_fm = yaml.dump(
        fm, default_flow_style=False, allow_unicode=True, sort_keys=False
    )
    file_path.write_text(f"---\n{new_fm}---\n{body}", encoding="utf-8")


def research_notes(
    vault_path: Path = Path("vault"),
    brand: str | None = None,
    auto: bool = False,
    dry_run: bool = False,
    model: str = "claude-sonnet-4-6",
    concurrency: int = 2,
) -> None:
    """Research flagged notes using web search to fill missing specs.

    Args:
        vault_path: Path to vault root.
        brand: If set, only research this brand.
        auto: Skip interactive review.
        dry_run: Show what would be researched.
        model: Claude model to use.
        concurrency: Max concurrent web searches.
    """
    from rich.console import Console

    from cargo_bikes.enrich.review import ReviewItem, run_review_session

    console = Console()

    # Find flagged notes
    flagged = _scan_flagged(vault_path, brand=brand)
    console.print(f"[bold]Found {len(flagged)} notes with needs_research: true[/bold]")

    if not flagged:
        return

    if dry_run:
        for f in flagged:
            fm = extract_frontmatter(f.read_text(encoding="utf-8"))
            topics = fm.get("research_topics", []) if fm else []
            console.print(
                f"  [dim]{f.parent.name}/{f.name}: {len(topics)} missing fields[/dim]"
            )
        return

    # Research sequentially, writing results immediately
    console.print("Researching (writing results as they come)...")

    updated = 0
    skipped = 0

    async def _run_all() -> None:
        nonlocal updated, skipped
        for i, file_path in enumerate(flagged, 1):
            console.print(
                f"  [{i}/{len(flagged)}] {file_path.parent.name}/{file_path.name}...",
                end=" ",
            )
            result = await _research_one(file_path, model)
            if result:
                if auto:
                    _apply_research(result["file_path"], result["extracted"])
                    remaining = len(result["topics"]) - len(result["extracted"])
                    status = "done" if remaining <= 0 else f"{remaining} left"
                    console.print(
                        f"[green]+{len(result['extracted'])} fields ({status})[/green]"
                    )
                    updated += 1
                else:
                    review_items = [
                        ReviewItem(
                            data=result,
                            label=result["title"],
                            diff="\n".join(
                                f"+{k}: {v}" for k, v in result["extracted"].items()
                            ),
                        )
                    ]
                    accepted, _ = run_review_session(
                        review_items, console=console, entity_label="research result"
                    )
                    if accepted:
                        _apply_research(
                            accepted[0]["file_path"], accepted[0]["extracted"]
                        )
                        updated += 1
            else:
                console.print("[dim]no data[/dim]")
                skipped += 1

    asyncio.run(_run_all())
    console.print(f"\n[bold]Updated {updated}, skipped {skipped}[/bold]")
