from __future__ import annotations
from pathlib import Path
from typing import List
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableLambda, RunnablePassthrough, RunnableConfig
from langchain_core.documents import Document

from rag.config import settings
from rag.hybrid_retriever import build_hybrid_runnable

def get_llm():
    try:
        backend = settings.llm_backend
        if backend == "openai":
            from langchain_openai import ChatOpenAI
            return ChatOpenAI(model=settings.openai_model)
        else:
            from langchain_ollama import ChatOllama
            return ChatOllama(model=settings.ollama_model)
    except Exception:
        from langchain_ollama import ChatOllama
        return ChatOllama(model="llama3")

PROMPT = ChatPromptTemplate.from_template(
    """Answer ONLY using CONTEXT. If not present, reply exactly: I don't know.
Add [index] citations (matching the blocks shown).

CONTEXT:
{context}

Q: {question}"""
)

def _fmt(docs: List[Document]) -> str:
    return "\n\n".join(f"[{i}] ({d.metadata.get('source','md')}) {d.page_content}" for i, d in enumerate(docs))

def build_answer_chain(kb_root: Path):
    retriever = build_hybrid_runnable(kb_root)
    llm = get_llm()
    chain = (
        {"context": retriever | RunnableLambda(_fmt), "question": RunnablePassthrough()}
        | PROMPT | llm | StrOutputParser()
    )
    return chain

if __name__ == "__main__":
    kb = Path("data/standards")
    chain = build_answer_chain(kb)
    cfg = RunnableConfig(max_retries=2, timeout=45)
    for chunk in chain.stream("How do I avoid goto per MISRA 14.4?"):
        print(chunk, end="", flush=True)
