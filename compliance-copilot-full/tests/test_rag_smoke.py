from pathlib import Path
from rag.answer_chain import build_answer_chain

def test_smoke_chain():
    chain = build_answer_chain(Path("data/standards"))
    out = chain.invoke("State the rule that forbids goto in MISRA C 2012.")
    assert isinstance(out, str)
