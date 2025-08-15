#!/usr/bin/env python
from pathlib import Path
import argparse
from rag.corpus import load_corpus

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dir", type=Path, default=Path("data/standards"))
    args = ap.parse_args()

    docs = load_corpus(args.dir)
    missing_rule, too_small = [], []
    for d in docs:
        if (d.metadata.get("standard","") or "").startswith("MISRA") and not d.metadata.get("rule_id"):
            missing_rule.append(d.metadata.get("source"))
        if len(d.page_content) < 300:
            too_small.append(d.metadata.get("source"))

    print(f"Found {len(docs)} docs")
    if missing_rule:
        print(f"⚠️ Missing rule_id in {len(missing_rule)} files:", missing_rule[:10], "...")
    if too_small:
        print(f"⚠️ Very short docs (<300 chars): {len(too_small)}:", too_small[:10], "...")
    if not missing_rule and not too_small:
        print("✅ Corpus looks good!")

if __name__ == "__main__":
    main()
