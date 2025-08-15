from __future__ import annotations
from pathlib import Path
from typing import List, Dict, Any
import re, yaml
from langchain_core.documents import Document

FRONT_MATTER_RE = re.compile(r"^---\n(.*?)\n---\n", re.DOTALL)

def parse_markdown_with_meta(path: Path) -> Document:
    text = path.read_text(encoding="utf-8")
    meta: Dict[str, Any] = {"source": path.name, "domain": None, "standard": None, "rule_id": None, "title": None}
    m = FRONT_MATTER_RE.match(text)
    if m:
        fm = yaml.safe_load(m.group(1)) or {}
        for k in ["domain","standard","rule_id","title","tags","sources","url","license","version"]:
            if k in fm:
                meta[k] = fm.get(k)
        content = text[m.end():].strip()
    else:
        content = text
    if meta.get("rule_id"):
        meta["rule_id"] = str(meta["rule_id"]).strip()
    return Document(page_content=content, metadata=meta)

def load_corpus(root: Path) -> List[Document]:
    docs: List[Document] = []
    for p in sorted(root.rglob("*.md")):
        docs.append(parse_markdown_with_meta(p))
    for p in sorted(root.rglob("*.txt")):
        docs.append(Document(page_content=p.read_text(encoding="utf-8"),
                             metadata={"source": p.name}))
    return docs
