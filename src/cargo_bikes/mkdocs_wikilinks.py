"""MkDocs plugin to convert [[wikilinks]] to markdown links at build time.

Resolves wikilinks by frontmatter title (not filename), which is what
obsidian-bridge can't do. Runs during the build — source files are untouched.
"""

from __future__ import annotations

import re
from pathlib import Path

import yaml
from mkdocs.config.defaults import MkDocsConfig
from mkdocs.plugins import BasePlugin
from mkdocs.structure.files import Files
from mkdocs.structure.pages import Page


class WikilinksPlugin(BasePlugin):
    """Convert [[wikilinks]] to proper markdown links during MkDocs build."""

    def __init__(self) -> None:
        super().__init__()
        self.title_map: dict[str, str] = {}

    def on_files(self, files: Files, *, config: MkDocsConfig) -> Files:
        """Build title→URL map from all pages."""
        docs_dir = Path(config["docs_dir"])

        for file in files.documentation_pages():
            file_path = docs_dir / file.src_path
            try:
                content = file_path.read_text(encoding="utf-8")
            except Exception:
                continue

            # Extract title from frontmatter
            fm_match = re.match(r"^---\s*\n(.*?)\n---\s*\n", content, re.DOTALL)
            if not fm_match:
                continue

            try:
                fm = yaml.safe_load(fm_match.group(1))
            except yaml.YAMLError:
                continue

            if not isinstance(fm, dict):
                continue

            title = fm.get("title", "")
            src = file.src_path.replace("\\", "/")

            if title:
                self.title_map[title] = src

            # Also map by filename stem
            stem = Path(file.src_path).stem
            if stem and stem != "index":
                if stem not in self.title_map:
                    self.title_map[stem] = src

        return files

    def on_page_markdown(
        self, markdown: str, *, page: Page, config: MkDocsConfig, files: Files
    ) -> str:
        """Convert [[wikilinks]] to [text](url) in page markdown."""
        # Calculate relative path from current page to target
        current_dir = str(Path(page.file.src_path).parent).replace("\\", "/")

        def _relative_path(target_src: str) -> str:
            """Calculate relative path from current page to target src_path."""
            from posixpath import relpath
            return relpath(target_src, current_dir)

        def replace_wikilink(m: re.Match) -> str:
            inner = m.group(1)

            # Parse [[Target|Display]] or [[Target]]
            if "|" in inner:
                target, display = inner.split("|", 1)
            else:
                target = inner
                display = inner

            target = target.strip()
            display = display.strip()

            # Look up by title (exact)
            url = None
            if target in self.title_map:
                url = self.title_map[target]
            else:
                # Case-insensitive fallback
                target_lower = target.lower()
                for title, u in self.title_map.items():
                    if title.lower() == target_lower:
                        url = u
                        break

            if url:
                rel = _relative_path(url)
                return f"[{display}]({rel})"

            # Not found — render as plain text (no broken link)
            return f"**{display}**"

        return re.sub(r"\[\[([^\]]+)\]\]", replace_wikilink, markdown)
