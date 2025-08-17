from typing import List, Dict
import json, pickle
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer

# Load MISRA indices
MISRA_TEXTS = [t.rstrip("\n") for t in open("kb/misra/texts.jsonl",encoding="utf-8")] if ( __import__('os').path.exists("kb/misra/texts.jsonl") ) else []
MISRA_META  = [json.loads(l) for l in open("kb/misra/meta.jsonl",encoding="utf-8")] if ( __import__('os').path.exists("kb/misra/meta.jsonl") ) else []
MISRA_FAISS = faiss.read_index("kb/misra/faiss.index") if ( __import__('os').path.exists("kb/misra/faiss.index") ) else None
MISRA_BM25BLOB = pickle.load(open("kb/misra/bm25.pkl","rb")) if ( __import__('os').path.exists("kb/misra/bm25.pkl") ) else None

# Load DO-178C indices
DO_TEXTS = [t.rstrip("\n") for t in open("kb/do178c/texts.jsonl",encoding="utf-8")] if ( __import__('os').path.exists("kb/do178c/texts.jsonl") ) else []
DO_META  = [json.loads(l) for l in open("kb/do178c/meta.jsonl",encoding="utf-8")] if ( __import__('os').path.exists("kb/do178c/meta.jsonl") ) else []
DO_FAISS = faiss.read_index("kb/do178c/faiss.index") if ( __import__('os').path.exists("kb/do178c/faiss.index") ) else None
DO_BM25BLOB = pickle.load(open("kb/do178c/bm25.pkl","rb")) if ( __import__('os').path.exists("kb/do178c/bm25.pkl") ) else None

EMB = SentenceTransformer("BAAI/bge-base-en-v1.5")  # offline OK once cached

def _hybrid(question: str, texts: List[str], meta: List[Dict], index, bm25blob, top_k=6):
    if not texts or index is None or bm25blob is None:
        return []
    qv = EMB.encode([f"query: {question}"], normalize_embeddings=True, convert_to_numpy=True)
    sims, idxs = index.search(qv, top_k)
    vec_hits = [{"i": int(i), "score": float(s), "src": "vec"} for i, s in zip(idxs[0], sims[0])]

    bm25 = bm25blob["bm25"]; btxts = bm25blob["texts"]
    scores = bm25.get_scores(question.split())
    bm_idxs = np.argsort(scores)[::-1][:top_k]
    bm_hits = [{"i": int(i), "score": float(scores[i]), "src": "bm25"} for i in bm_idxs]

    def norm(hits):
        if not hits: return hits
        vals = np.array([h["score"] for h in hits])
        lo, hi = float(vals.min()), float(vals.max() or 1.0)
        for h in hits:
            h["score"] = 1.0 if hi==lo else (h["score"]-lo)/(hi-lo)
        return hits

    from collections import defaultdict
    agg = defaultdict(lambda: {"score": 0.0, "i": None, "seen": set()})
    for h in norm(vec_hits) + norm(bm_hits):
        a = agg[h["i"]]; a["i"] = h["i"]; a["score"] += h["score"]; a["seen"].add(h["src"]) 
    merged = sorted(agg.values(), key=lambda x: x["score"], reverse=True)[:top_k]
    return [{"rule_id": meta[m["i"]].get("rule_id", meta[m["i"]].get("id","?")),
             "title": meta[m["i"]].get("title") or f"Item {m['i']}",
             "section": "all",
             "snippet": texts[m["i"]][:600],
             "score": m["score"]} for m in merged]

def rule_search_misra(query: str, top_k: int = 6) -> Dict:
    hits = _hybrid(query, MISRA_TEXTS, MISRA_META, MISRA_FAISS, MISRA_BM25BLOB, top_k)
    return {"hits": hits}

def rule_search_do178c(query: str, top_k: int = 6) -> Dict:
    hits = _hybrid(query, DO_TEXTS, DO_META, DO_FAISS, DO_BM25BLOB, top_k)
    return {"hits": hits}

def kb_citation(rule_ids: list[str]) -> Dict:
    idset = set(rule_ids)
    rows = [r for r in MISRA_META if r.get("rule_id") in idset] + [r for r in DO_META if r.get("id") in idset]
    return {"rules_json": json.dumps(rows, ensure_ascii=False)}
