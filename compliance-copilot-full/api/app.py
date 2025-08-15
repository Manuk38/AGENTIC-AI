from __future__ import annotations
from fastapi import FastAPI, Body
from fastapi.responses import StreamingResponse, JSONResponse
from pathlib import Path

from rag.answer_chain import build_answer_chain
from agent.graph import build_graph, GState

api = FastAPI(title="Compliance Copilot API")

@api.get("/rag")
def rag(q: str):
    chain = build_answer_chain(Path("data/standards"))
    def gen():
        for chunk in chain.stream(q):
            yield chunk
    return StreamingResponse(gen(), media_type="text/plain")

@api.post("/graph/run")
def graph_run(payload: dict = Body(...)):
    question = payload.get("question", "")
    if not question:
        return JSONResponse({"error": "Missing question"}, status_code=400)
    app = build_graph()
    out = app.invoke(GState(question=question))
    return JSONResponse(out.dict())
