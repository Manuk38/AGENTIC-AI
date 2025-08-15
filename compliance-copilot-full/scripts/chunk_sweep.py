#!/usr/bin/env python
import argparse, json, time
from pathlib import Path
from itertools import product
from statistics import mean

from rag.corpus import load_corpus
from rag.index_builder import split_docs
from rag.config import settings
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS

def load_seed_qas(path: Path):
    items = []
    if not path.exists():
        return items
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                items.append(json.loads(line))
    return items

def build_inmemory_vs(docs, chunk_size, chunk_overlap):
    splits = split_docs(docs, chunk_size, chunk_overlap)
    emb = HuggingFaceEmbeddings(model_name=settings.embed_model)
    vs = FAISS.from_documents(splits, emb)
    return vs

def evaluate(vs, qas, k=4):
    retriever = vs.as_retriever(search_kwargs={"k": k})
    hits = []
    for ex in qas:
        q = ex["q"]
        expect = set([str(x).strip() for x in ex.get("expect_rule_ids", [])])
        docs = retriever.invoke(q)
        found = set()
        for d in docs:
            rid = d.metadata.get("rule_id")
            if rid:
                found.add(str(rid).strip())
        hits.append(1 if (expect & found) else 0)
    return {"recall_at_k": (mean(hits) if hits else 0.0)}

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--notes", type=Path, default=Path("data/standards"))
    ap.add_argument("--qa", type=Path, default=Path("data/qa/seed_qa.jsonl"))
    ap.add_argument("--k", type=int, default=4)
    args = ap.parse_args()

    docs = load_corpus(args.notes)
    qas = load_seed_qas(args.qa)

    chunk_sizes = [400, 600, 800, 1000]
    overlaps    = [60, 120, 160, 200]

    results = []
    t0 = time.time()
    for cs, ov in product(chunk_sizes, overlaps):
        vs = build_inmemory_vs(docs, cs, ov)
        metrics = evaluate(vs, qas, k=args.k)
        results.append({"chunk_size": cs, "chunk_overlap": ov, **metrics})
        print(f"cs={cs:4d} ov={ov:4d} -> recall@{args.k}={metrics['recall_at_k']:.3f}")

    results.sort(key=lambda r: (r["recall_at_k"], -r["chunk_size"]), reverse=True)
    best = results[0] if results else None
    print("\nBest:", best)
    print(f"Elapsed: {time.time()-t0:.1f}s")

    out = Path("data/qa/chunk_sweep_results.csv")
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", encoding="utf-8") as f:
        f.write("chunk_size,chunk_overlap,recall_at_k\n")
        for r in results:
            f.write(f"{r['chunk_size']},{r['chunk_overlap']},{r['recall_at_k']:.3f}\n")
    print(f"Saved: {out}")

if __name__ == "__main__":
    main()
