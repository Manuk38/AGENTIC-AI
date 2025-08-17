# Build FAISS + BM25 index for DO-178C notes JSONL
import sys, json, os, pickle
import numpy as np
from pathlib import Path
from sentence_transformers import SentenceTransformer
import faiss
from rank_bm25 import BM25Okapi

def doc_text(item):
    parts = [
        f"Objective {item.get('id','?')}: {item.get('title','')}",
        f"Guidance: {item.get('guidance','')}",
        f"References: {', '.join(item.get('references',[]))}",
    ]
    return "\n".join(p for p in parts if p and p.strip())

def build(jsonl_path: str, out_dir="kb/do178c"):
    items, texts = [], []
    for line in open(jsonl_path, encoding="utf-8"):
        r = json.loads(line)
        items.append(r); texts.append(doc_text(r))

    emb = SentenceTransformer("BAAI/bge-base-en-v1.5")
    doc_inputs = [f"passage: {t}" for t in texts]
    vecs = emb.encode(doc_inputs, normalize_embeddings=True, convert_to_numpy=True)
    index = faiss.IndexFlatIP(vecs.shape[1]); index.add(vecs)

    Path(out_dir).mkdir(parents=True, exist_ok=True)
    faiss.write_index(index, f"{out_dir}/faiss.index")
    with open(f"{out_dir}/texts.jsonl","w",encoding="utf-8") as f:
        for t in texts: f.write(t+"\n")
    with open(f"{out_dir}/meta.jsonl","w",encoding="utf-8") as f:
        for r in items: f.write(json.dumps(r, ensure_ascii=False)+"\n")

    tokenized = [t.split() for t in texts]
    bm25 = BM25Okapi(tokenized)
    with open(f"{out_dir}/bm25.pkl","wb") as f:
        pickle.dump({"bm25":bm25,"texts":texts,"items":items}, f)
    print(f"DO-178C KB built → {out_dir} ({len(items)} notes)")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python tools/build_do178c_kb.py parser/do178c_notes.jsonl [kb/do178c]")
        raise SystemExit(2)
    build(sys.argv[1], sys.argv[2] if len(sys.argv)>2 else "kb/do178c")
