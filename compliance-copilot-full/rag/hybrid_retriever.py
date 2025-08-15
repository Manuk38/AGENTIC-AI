from __future__ import annotations
from typing import List
from pathlib import Path
from langchain_core.documents import Document
from langchain_core.runnables import RunnableLambda
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_community.retrievers import BM25Retriever

# Optional cross-encoder reranker
try:
    from sentence_transformers import CrossEncoder
    _RERANKER = CrossEncoder("BAAI/bge-reranker-base")
except Exception:
    _RERANKER = None

def build_docs_from_markdown_dir(md_root: Path) -> List[Document]:
    from langchain_community.document_loaders import TextLoader
    docs: List[Document] = []
    for p in md_root.rglob("*.md"):
        docs.extend(TextLoader(str(p), encoding="utf-8").load())
    return docs

def build_hybrid_runnable(md_root: Path, chunk_size=800, chunk_overlap=120, k=8) -> RunnableLambda:
    docs = build_docs_from_markdown_dir(md_root)
    splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    splits = splitter.split_documents(docs)
    emb = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    # Vector (FAISS in-memory) + BM25
    vs = FAISS.from_documents(splits, emb)
    vect = vs.as_retriever(search_kwargs={"k": k})
    bm25 = BM25Retriever.from_documents(splits); bm25.k = k

    def multiquery(q: str) -> list[str]:
        ql = q.lower()
        extras = []
        if "misra" in ql or "embedded" in ql: extras.append(q + " embedded systems example")
        if "matlab" in ql: extras.append(q + " matlab example")
        return [q] + extras

    def union_and_rerank(q: str, pools: List[List[Document]], topn=6) -> List[Document]:
        uniq = {id(d): d for pool in pools for d in pool}.values()
        if _RERANKER is None:
            return list(uniq)[:topn]
        pairs = [[q, d.page_content] for d in uniq]
        scores = _RERANKER.predict(pairs)
        ranked = sorted(zip(uniq, scores), key=lambda t: t[1], reverse=True)
        return [d for d, _ in ranked[:topn]]

    def search(q: str) -> List[Document]:
        qs = multiquery(q)
        pools = []
        for qq in qs:
            pools.append(vect.invoke(qq))
            pools.append(bm25.get_relevant_documents(qq))
        return union_and_rerank(q, pools, topn=6)

    return RunnableLambda(lambda q: search(q))
