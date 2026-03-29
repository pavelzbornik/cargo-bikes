"""Claude Agent SDK and API wrappers for cargo-bikes enrichment.

Uses claude-agent-sdk for tool-enabled calls (WebSearch, WebFetch),
and the Anthropic API directly for simple content generation.
"""

from __future__ import annotations

import asyncio
import re
from typing import Any, Awaitable, Callable, TypeVar

import anthropic

from claude_agent_sdk import (
    AssistantMessage,
    ClaudeAgentOptions,
    ResultMessage,
    TextBlock,
    query,
)

T = TypeVar("T")


def _clean_response(text: str) -> str:
    """Clean Claude's response by removing code fences and thinking preamble."""
    if not text:
        return text

    # Normalize line endings (Agent SDK may return \r\n)
    text = text.replace("\r\n", "\n").replace("\r", "\n")

    # Strip markdown code fences wrapping the entire response
    fence_match = re.search(
        r"```(?:markdown)?\s*\n(.*?)```\s*$", text, re.DOTALL
    )
    if fence_match:
        text = fence_match.group(1)

    # Handle broken pattern: ---\n\n```\n---\n (empty frontmatter + fenced real frontmatter)
    broken_match = re.match(
        r"^---\s*\n\s*```(?:markdown)?\s*\n(---\n.*?)```\s*$", text, re.DOTALL
    )
    if broken_match:
        text = broken_match.group(1)

    # Also handle: ```\n---\n...\n---\n...\n``` at any position
    inner_match = re.search(
        r"```(?:markdown)?\s*\n(---\n.*?\n---\n.*?)```", text, re.DOTALL
    )
    if inner_match and inner_match.start() == 0:
        text = inner_match.group(1)

    # Remove thinking preamble before frontmatter
    fm_match = re.search(r"^---\s*\n", text, re.MULTILINE)
    if fm_match and fm_match.start() > 0:
        preamble = text[: fm_match.start()].strip()
        if preamble and not preamble.startswith("#"):
            text = text[fm_match.start() :]
    elif not fm_match and not text.strip().startswith("#"):
        # No frontmatter and no heading — likely just thinking text, discard
        return ""

    return text.strip()


async def call_api(
    prompt: str,
    system: str | None = None,
    model: str = "claude-sonnet-4-6",
) -> str:
    """Call Claude API directly for simple content generation (no tools).

    This is faster and more reliable than the Agent SDK for tasks
    that don't need file access or web search.
    """
    client = anthropic.AsyncAnthropic()

    kwargs: dict[str, Any] = {
        "model": model,
        "max_tokens": 16000,
        "messages": [{"role": "user", "content": prompt}],
    }
    if system:
        kwargs["system"] = system

    response = await client.messages.create(**kwargs)

    text = next(
        (block.text for block in response.content if block.type == "text"),
        "",
    )
    return _clean_response(text)


async def call_agent(
    prompt: str,
    system: str | None = None,
    model: str = "claude-sonnet-4-6",
    max_turns: int = 1,
    allowed_tools: list[str] | None = None,
) -> str:
    """Call the Claude Agent SDK for tool-enabled operations.

    Use this when you need WebSearch, WebFetch, Read, or other tools.
    For simple content generation without tools, use call_api() instead.
    """
    options = ClaudeAgentOptions(
        model=model,
        max_turns=max_turns,
        allowed_tools=allowed_tools or [],
    )
    if system:
        options.system_prompt = system

    accumulated_text: list[str] = []
    result_text = ""

    async for message in query(prompt=prompt, options=options):
        if isinstance(message, AssistantMessage):
            for block in message.content:
                if isinstance(block, TextBlock) or (
                    hasattr(block, "text")
                    and hasattr(block, "type")
                    and getattr(block, "type", None) == "text"
                ):
                    accumulated_text.append(block.text)
        elif isinstance(message, ResultMessage):
            result_text = message.result or ""

    final_text = result_text if result_text.strip() else "\n".join(accumulated_text)
    return _clean_response(final_text)


def call_agent_sync(
    prompt: str,
    system: str | None = None,
    model: str = "claude-sonnet-4-6",
    max_turns: int = 1,
    allowed_tools: list[str] | None = None,
) -> str:
    """Synchronous wrapper around call_agent."""
    return asyncio.run(
        call_agent(
            prompt=prompt,
            system=system,
            model=model,
            max_turns=max_turns,
            allowed_tools=allowed_tools,
        )
    )


async def run_concurrent(
    items: list[T],
    worker_fn: Callable[[T], Awaitable[Any]],
    concurrency: int = 3,
    on_progress: Callable[[], None] | None = None,
) -> list[Any]:
    """Run async worker function over items with bounded concurrency."""
    semaphore = asyncio.Semaphore(concurrency)

    async def bounded(item: T) -> Any:
        async with semaphore:
            result = await worker_fn(item)
            if on_progress:
                on_progress()
            return result

    return await asyncio.gather(*[bounded(item) for item in items])
