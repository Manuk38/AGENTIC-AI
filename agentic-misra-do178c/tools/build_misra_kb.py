# Build FAISS + BM25 index for MISRA rules JSONL
import sys, json, os, pickle
import numpy as np
from pathlib import Path
from sentence_transformers import SentenceTransformer
import faiss
from rank_bm25 import BM25Okapi

def doc_text(rule):
    parts = [
        f"Rule {rule['rule_id']} ({rule.get('category')}) — {rule.get('requirement_text','')}",
        f"Interpretation: {rule.get('interpretation','')}",
        f"Functional specification: {rule.get('functional_specification','')}",
        f"Precaution: {rule.get('precaution','')}",
        f"Limitation: {rule.get('limitation','')}",
    ]
    return "\n".join(p for p in parts if p and p.strip())

def build(jsonl_path: str, out_dir="kb/misra"):
    rules, texts = [], []
    for line in open(jsonl_path, encoding="utf-8"):
        r = json.loads(line)
        rules.append(r); texts.append(doc_text(r))

    emb = SentenceTransformer("BAAI/bge-base-en-v1.5")
    doc_inputs = [f"passage: {t}" for t in texts]
    vecs = emb.encode(doc_inputs, normalize_embeddings=True, convert_to_numpy=True)
    index = faiss.IndexFlatIP(vecs.shape[1]); index.add(vecs)

    Path(out_dir).mkdir(parents=True, exist_ok=True)
    faiss.write_index(index, f"{out_dir}/faiss.index")
    with open(f"{out_dir}/texts.jsonl","w",encoding="utf-8") as f:
        for t in texts: f.write(t+"\n")
    with open(f"{out_dir}/meta.jsonl","w",encoding="utf-8") as f:
        for r in rules: f.write(json.dumps(r, ensure_ascii=False)+"\n")

    tokenized = [t.split() for t in texts]
    bm25 = BM25Okapi(tokenized)
    with open(f"{out_dir}/bm25.pkl","wb") as f:
        pickle.dump({"bm25":bm25,"texts":texts,"rules":rules}, f)
    print(f"MISRA KB built → {out_dir} ({len(rules)} rules)")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python tools/build_misra_kb.py parser/misra_rules.jsonl [kb/misra]")
        raise SystemExit(2)
    build(sys.argv[1], sys.argv[2] if len(sys.argv)>2 else "kb/misra")
