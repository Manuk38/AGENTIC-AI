from langgraph.graph import StateGraph, END
from .state import State

MAX_ITERS = 3

def node_plan(s: State) -> State:
    s["question"] = f"Which rules affect: {s['nlr']}"
    s["iterations"] = 0
    return s

def node_requirements(s: State) -> State:
    from agents.requirements_agent import to_llr
    s["llr"] = to_llr(s["nlr"], s.get("constraints", {}))
    return s

def node_retrieve(s: State) -> State:
    from agents.retrieval_agent import retrieve_rules
    hits, rules_json = retrieve_rules(s["question"])
    s["rule_hits"], s["rules_json"] = hits, rules_json
    return s

def node_codegen(s: State) -> State:
    from agents.codegen_agent import generate_code
    s["code"] = generate_code(s["llr"], s["rules_json"])
    return s

def node_audit(s: State) -> State:
    from agents.auditor_agent import audit_code
    s["findings"] = audit_code(s["code"], s["rules_json"])
    return s

def need_repair(s: State):
    return "verify" if not s.get("findings") else "repair"

def node_repair(s: State) -> State:
    from agents.repair_agent import suggest_patches
    patches, patched = suggest_patches(s["code"], s["findings"], s["rules_json"])
    s["patches"], s["patched_code"] = patches, patched
    return s

def node_verify(s: State) -> State:
    from agents.verify_agent import verify_all
    s["build"], s["coverage"], s["trace"] = verify_all(s.get("patched_code") or s["code"], s["llr"])
    return s

def judge_accept(s: State):
    # Simple judge: accept if compiles OK or iterations exhausted
    ok = s["build"]["ok"]
    if ok or s["iterations"] >= MAX_ITERS:
        return "report"
    else:
        s["iterations"] += 1
        return "retrieve"

def node_report(s: State) -> State:
    from agents.report_agent import write_report
    s["report_path"] = write_report(
        llr=s["llr"],
        rules_json=s["rules_json"],
        code=s.get("patched_code") or s["code"],
        build=s["build"],
        coverage=s["coverage"],
        findings=s.get("findings", []),
        trace=s.get("trace", [])
    )
    return s

graph = StateGraph(State)
graph.add_node("plan", node_plan)
graph.add_node("requirements", node_requirements)
graph.add_node("retrieve", node_retrieve)
graph.add_node("codegen", node_codegen)
graph.add_node("audit", node_audit)
graph.add_node("repair", node_repair)
graph.add_node("verify", node_verify)
graph.add_node("report", node_report)

graph.set_entry_point("plan")
graph.add_edge("plan", "requirements")
graph.add_edge("requirements", "retrieve")
graph.add_edge("retrieve", "codegen")
graph.add_edge("codegen", "audit")
graph.add_conditional_edges("audit", need_repair, {"repair": "repair", "verify": "verify"})
graph.add_conditional_edges("verify", judge_accept, {"report": "report", "retrieve": "retrieve"})
graph.add_edge("report", END)
app = graph.compile()
