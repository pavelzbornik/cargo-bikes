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
            if title:
                # Map title to the MkDocs URL path
                url = file.dest_path.replace("\\", "/")
                if url.endswith("index.html"):
                    url = url[: -len("index.html")]
                elif url.endswith(".html"):
                    url = url[: -len(".html")] + "/"
                self.title_map[title] = "/" + url

            # Also map by filename stem
            stem = Path(file.src_path).stem
            if stem and stem != "index":
                if stem not in self.title_map:
                    url = file.dest_path.replace("\\", "/")
                    if url.endswith("index.html"):
                        url = url[: -len("index.html")]
                    elif url.endswith(".html"):
                        url = url[: -len(".html")] + "/"
                    self.title_map[stem] = "/" + url

        return files

    def on_page_markdown(
        self, markdown: str, *, page: Page, config: MkDocsConfig, files: Files
    ) -> str:
        """Convert [[wikilinks]] to [text](url) in page markdown."""

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
            if target in self.title_map:
                return f"[{display}]({self.title_map[target]})"

            # Case-insensitive fallback
            target_lower = target.lower()
            for title, url in self.title_map.items():
                if title.lower() == target_lower:
                    return f"[{display}]({url})"

            # Not found — render as plain text (no broken link)
            return f"**{display}**"

        return re.sub(r"\[\[([^\]]+)\]\]", replace_wikilink, markdown)
