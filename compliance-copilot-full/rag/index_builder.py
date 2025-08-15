from __future__ import annotations
from pathlib import Path
from typing import Tuple
from rag.config import settings
from rag.corpus import load_corpus
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS, Chroma

def split_docs(docs, chunk_size=800, chunk_overlap=120):
    return RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap).split_documents(docs)

def get_embeddings():
    return HuggingFaceEmbeddings(model_name=settings.embed_model)

def build_index(input_dir: Path, out_dir: Path, store: str = None, chunk_size=800, chunk_overlap=120):
    store = (store or settings.vector_store).lower()
    docs = load_corpus(input_dir)
    if not docs:
        raise SystemExit(f"No notes found in {input_dir}.")
    splits = split_docs(docs, chunk_size, chunk_overlap)
    emb = get_embeddings()
    out_dir.mkdir(parents=True, exist_ok=True)
    if store == "chroma":
        persist_dir = out_dir / "chroma"
        persist_dir.mkdir(parents=True, exist_ok=True)
        vs = Chroma.from_documents(splits, emb, persist_directory=str(persist_dir))
        return vs, persist_dir
    else:
        vs = FAISS.from_documents(splits, emb)
        (out_dir / "faiss").mkdir(parents=True, exist_ok=True)
        vs.save_local(str(out_dir / "faiss"))
        return vs, out_dir / "faiss"
