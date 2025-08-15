from __future__ import annotations
from langchain_core.tools import tool

@tool
def run_static_analysis(code_path: str, ruleset: str = "clang-tidy") -> dict:
    """Run static checks and return JSON {ok:bool, violations:[{id,line,msg,severity}], raw:str}.
    NOTE: This is a stub. Wire it to clang-tidy/cppcheck in your environment.
    """
    try:
        # TODO: subprocess to clang-tidy/cppcheck and parse output
        return {"ok": True, "violations": [], "raw": "stub"}
    except Exception as e:
        return {"ok": False, "violations": [], "error": str(e)}
