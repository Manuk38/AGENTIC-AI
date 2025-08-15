from __future__ import annotations
from typing import List, Optional
from pydantic import BaseModel, Field
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.sqlite import SqliteSaver

from agent.schemas import Plan, PatchOut
from rag.answer_chain import build_answer_chain
from langchain_core.prompts import ChatPromptTemplate
from pathlib import Path

class GState(BaseModel):
    question: str
    plan: Optional[Plan] = None
    citations: List[str] = Field(default_factory=list)
    patch: Optional[PatchOut] = None
    violations: List[dict] = Field(default_factory=list)
    confidence: float = 0.0
    iters: int = 0
    max_iters: int = 3
    human_approved: bool = True   # flip to False to require approval interrupt

def n_plan(s: GState):
    steps = ["Research", "ProposeFix", "Verify"]
    return {"plan": Plan(intent="compliance_refactor", steps=steps, expected_rules=[])}

def n_research(s: GState):
    chain = build_answer_chain(Path("data/standards"))
    ans = chain.invoke(s.question)
    conf = 0.6 if "[" in ans and "]" in ans else 0.3
    cites = []
    for part in ans.split("["):
        if "]" in part:
            idx = part.split("]")[0]
            if idx.isdigit():
                cites.append(idx)
    return {"citations": cites, "confidence": conf}

_refactor_prompt = ChatPromptTemplate.from_template(
    """You refactor code to comply with rules. Return a unified diff and rationale.
Q: {question}
Output:
PATCH:
<unified_diff>
RATIONALE:
<why>
"""
)

def n_refactor(s: GState):
    return {"patch": PatchOut(patch_unified="---diff---", rationale="placeholder", touched_files=[])}

def n_verify(s: GState):
    return {"violations": []}

def n_critic(s: GState):
    if s.violations:
        return {"iters": s.iters + 1}
    return {}

def n_emit(s: GState):
    return {}

def decide_from_research(s: GState):
    return "Refactor" if s.confidence >= 0.6 else "Emit"

def decide_post_verify(s: GState):
    if s.violations and s.iters < s.max_iters:
        return "Critic"
    return "Emit"

def build_graph():
    g = StateGraph(GState)
    g.add_node("Plan", n_plan)
    g.add_node("Research", n_research)
    g.add_node("Refactor", n_refactor)
    g.add_node("Verify", n_verify)
    g.add_node("Critic", n_critic)
    g.add_node("Emit", n_emit)
    g.add_edge("Plan", "Research")
    g.add_conditional_edges("Research", decide_from_research, {"Refactor": "Refactor", "Emit": "Emit"})
    g.add_edge("Refactor", "Verify")
    g.add_conditional_edges("Verify", decide_post_verify, {"Critic": "Critic", "Emit": "Emit"})
    g.add_edge("Critic", "Refactor")
    g.add_edge("Emit", END)
    memory = SqliteSaver("checkpoint.sqlite")
    return g.compile(checkpointer=memory)

if __name__ == "__main__":
    app = build_graph()
    final = app.invoke(GState(question="Refactor to comply with MISRA 14.4"))
    print(final)
