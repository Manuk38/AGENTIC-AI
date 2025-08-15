# Compliance Copilot — Agentic RAG + LangGraph + Tools

This repository showcases LCEL-first RAG, a hybrid retriever (BM25 + Vectors + reranker),
and a multi-agent LangGraph orchestration for compliance-aware code refactoring.

## Quickstart
```bash
python -m venv .venv && source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
cp .env.example .env

# Build the baseline index (optional for Phase-1)
python scripts/build_index.py --input ./data/standards --out ./data/index --store faiss

# Ask a question (Phase-1 LCEL RAG using hybrid retriever on MD files)
python scripts/ask.py --q "What does MISRA 14.4 say about goto?"
```
