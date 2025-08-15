#!/usr/bin/env python
import argparse
from pathlib import Path
from rag.answer_chain import build_answer_chain

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--q", "--question", dest="q", required=True)
    ap.add_argument("--kb", type=Path, default=Path("data/standards"))
    args = ap.parse_args()

    chain = build_answer_chain(args.kb)
    ans = chain.invoke(args.q)
    print("\n--- Answer ---\n" + ans)

if __name__ == "__main__":
    main()
