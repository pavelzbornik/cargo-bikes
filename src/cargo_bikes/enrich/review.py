"""Interactive review session for AI-generated content.

Provides Accept / Re-run with hint / Skip / Discard choices
for each item before writing changes.
"""

from __future__ import annotations

import sys
from dataclasses import dataclass
from typing import Any, Callable, Generic, TypeVar

from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax

T = TypeVar("T")


@dataclass
class ReviewItem(Generic[T]):
    """An item pending review."""

    data: T
    label: str
    diff: str  # Human-readable diff or preview


def _is_tty() -> bool:
    """Check if we're running in an interactive terminal."""
    return hasattr(sys.stdin, "isatty") and sys.stdin.isatty()


def run_review_session(
    items: list[ReviewItem[T]],
    rerun_callback: Callable[[T, str], T] | None = None,
    console: Console | None = None,
    entity_label: str = "item",
) -> tuple[list[T], list[T]]:
    """Run an interactive review session over pending items.

    Args:
        items: List of ReviewItem objects to review.
        rerun_callback: Optional function to re-run with a hint.
            Takes (data, hint) and returns updated data.
        console: Rich console for output.
        entity_label: Label for the entity type (e.g., "note", "component").

    Returns:
        Tuple of (accepted_items, discarded_items).
    """
    if console is None:
        console = Console()

    if not items:
        console.print(f"[dim]No {entity_label}s to review.[/dim]")
        return [], []

    if not _is_tty():
        console.print(
            f"[yellow]Non-interactive mode: auto-accepting {len(items)} {entity_label}(s)[/yellow]"
        )
        return [item.data for item in items], []

    accepted: list[T] = []
    discarded: list[T] = []

    for i, item in enumerate(items, 1):
        console.print(
            f"\n[bold]─── {entity_label} {i}/{len(items)}: {item.label} ───[/bold]"
        )

        if item.diff:
            console.print(
                Panel(
                    Syntax(item.diff, "yaml", theme="monokai"),
                    title="Changes",
                    border_style="blue",
                )
            )

        while True:
            console.print(
                "\n[bold]Choose:[/bold] "
                "[green](a)[/green]ccept  "
                "[yellow](r)[/yellow]e-run with hint  "
                "[dim](s)[/dim]kip  "
                "[red](d)[/red]iscard"
            )

            try:
                choice = input("> ").strip().lower()
            except (EOFError, KeyboardInterrupt):
                console.print("\n[yellow]Interrupted. Discarding remaining.[/yellow]")
                discarded.extend(remaining.data for remaining in items[i:])
                return accepted, discarded

            if choice in ("a", "accept", ""):
                accepted.append(item.data)
                console.print("[green]✓ Accepted[/green]")
                break
            elif choice in ("r", "rerun") and rerun_callback:
                hint = input("Hint: ").strip()
                if hint:
                    try:
                        updated = rerun_callback(item.data, hint)
                        item.data = updated
                        console.print("[yellow]↻ Re-run complete. Review again.[/yellow]")
                    except Exception as e:
                        console.print(f"[red]Re-run failed: {e}[/red]")
                continue
            elif choice in ("s", "skip"):
                console.print("[dim]⊘ Skipped[/dim]")
                break
            elif choice in ("d", "discard"):
                discarded.append(item.data)
                console.print("[red]✗ Discarded[/red]")
                break
            else:
                console.print("[dim]Invalid choice. Try a/r/s/d.[/dim]")

    console.print(
        f"\n[bold]Review complete:[/bold] "
        f"[green]{len(accepted)} accepted[/green], "
        f"[red]{len(discarded)} discarded[/red], "
        f"[dim]{len(items) - len(accepted) - len(discarded)} skipped[/dim]"
    )

    return accepted, discarded
