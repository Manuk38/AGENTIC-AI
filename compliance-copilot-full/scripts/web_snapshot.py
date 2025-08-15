# Optional: Playwright-based snapshotper; fill allowlists before use.
from __future__ import annotations
from pathlib import Path
from typing import List
from bs4 import BeautifulSoup
from langchain_community.document_loaders import PlaywrightURLLoader

def snapshot(urls: List[str], out_dir: Path):
    loader = PlaywrightURLLoader(urls=urls, remove_selectors=["nav","footer","header"])
    docs = loader.load()
    out_dir.mkdir(parents=True, exist_ok=True)
    for i, d in enumerate(docs):
        html = d.page_content
        title = d.metadata.get("title") or f"page_{i}"
        text = BeautifulSoup(html, "html.parser").get_text("\n", strip=True)
        (out_dir / f"{title}.md").write_text(text, encoding="utf-8")
