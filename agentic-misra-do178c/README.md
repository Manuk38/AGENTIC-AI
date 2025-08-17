# Agentic MISRA + DO-178C Code Generation (LangGraph/LCEL)

Production-style, offline-friendly Agentic AI system for generating **MISRA-C:2012** and **DO-178C** conformant C code using **LangGraph** (multi-agent), **LCEL**, hybrid RAG, and verification loops.

## Features
- Multi-agent orchestration (Planner → Retrieval → Codegen → Audit → Repair → Verify → Judge → Report)
- Hybrid RAG (FAISS + BM25) with asymmetric embeddings (BGE)
- MISRA guardrails + light static checks
- DO-178C process evidence stubs (traceability, compile/test/coverage)
- Front-matter Markdown export for MISRA rule summaries (your preferred schema)
- Works offline with `llama.cpp` GGUF (bring-your-own model)

## Quickstart

1. **Create virtual env** (Python 3.10+ recommended).
2. Install dependencies (edit `pyproject.toml` or `requirements.txt`).
3. Parse your MISRA PDF to structured JSONL:
   ```bash
   python parser/parse_misra_pdf.py "C:/games/LangChain/compliance-copilot/data/RULECHECKER.pdf"
   ```
   Then build the vector store and BM25 for MISRA:
   ```bash
   python tools/build_misra_kb.py parser/misra_rules.jsonl
   ```
4. (Optional) Prepare DO-178C *notes* (your own summarized notes/YAML) and index them:
   ```bash
   python parser/parse_do178c_notes.py data/do178c_notes.yaml
   python tools/build_do178c_kb.py parser/do178c_notes.jsonl
   ```
5. Configure your LLM in `agents/shared_llm.py` (LlamaCpp path to your GGUF).
6. Run demo:
   ```bash
   python run_demo.py
   ```

## Notes
- This project ships with **stubs** for compiler/tests/coverage and a **light** MISRA linter.
  Replace with your toolchain (gcc/clang, Unity/CUnit, gcov/lcov) as needed.
- DO-178C copyrighted text is **not** included. Provide your own summarized notes and parse them.
- The report writer follows your MISRA front-matter schema for rule summaries.
