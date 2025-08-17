from tools.compiler import compile_code
from tools.unit_test import build_and_run_tests
from tools.coverage import coverage_summary

def verify_all(code: str, llr: dict):
    build = compile_code(code, std="c99")
    tests = build_and_run_tests(code, llr)
    cov = coverage_summary()
    trace = [{"llr_id": i["id"], "code_refs": i.get("anchors", []), "test_ids": i.get("tests", [])}
             for i in (llr.get("items") or [])]
    return build, cov, trace
