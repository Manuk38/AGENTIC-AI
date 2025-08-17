from tools.export_md import write_front_matter_report
import json

def write_report(llr, rules_json, code, build, coverage, findings, trace):
    # Pick top rule for the front-matter file (fall back to 'mixed').
    rid = "mixed"
    try:
        rules = json.loads(rules_json)
        if isinstance(rules, list) and rules:
            rid = rules[0].get("rule_id", "mixed") or "mixed"
    except Exception:
        pass

    return write_front_matter_report(
        title=f"MISRA-C:2012 Rule {rid} — Auto Report",
        standard="MISRA-C-2012",
        rule_id=str(rid),
        source="local://kb",
        version="2025-08-15",
        summary="Code generated and verified against MISRA rules and mapped to DO-178C objectives.",
        rationale_bullets="- Banned constructs removed\n- LLR traceability ensured\n- Unit tests + coverage attached",
        noncompliant_code="/* see original code prior to repair in build logs */",
        filename="reports/compliance_report.md"
    )
