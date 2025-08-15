#!/usr/bin/env python
import argparse
from pathlib import Path
from rag.index_builder import build_index
from rag.config import settings

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", type=Path, default=settings.data_dir)
    ap.add_argument("--out", type=Path, default=settings.index_dir)
    ap.add_argument("--store", type=str, default=settings.vector_store, choices=["faiss","chroma"])
    ap.add_argument("--chunk_size", type=int, default=800)
    ap.add_argument("--chunk_overlap", type=int, default=120)
    args = ap.parse_args()
    vs, loc = build_index(args.input, args.out, args.store, args.chunk_size, args.chunk_overlap)
    print(f"✅ Built {args.store.upper()} index at: {loc}")

if __name__ == "__main__":
    main()
