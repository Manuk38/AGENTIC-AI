from typing import TypedDict, List, Optional, Dict, Any

class Finding(TypedDict, total=False):
    rule_id: str
    msg: str
    severity: str
    line: int

class Patch(TypedDict, total=False):
    rule_id: str
    rationale: str
    diff: str

class TraceLink(TypedDict, total=False):
    llr_id: str
    code_refs: List[str]
    test_ids: List[str]

class BuildResult(TypedDict, total=False):
    ok: bool
    warnings: List[str]
    stderr: List[str]

class Coverage(TypedDict, total=False):
    lines: float
    branches: float
    mcdc_proxy: float

class State(TypedDict, total=False):
    nlr: str
    constraints: Dict[str, Any]
    llr: Dict[str, Any]
    question: str
    rule_hits: List[Dict[str, Any]]
    rules_json: str
    code: str
    findings: List[Finding]
    patches: List[Patch]
    patched_code: str
    build: BuildResult
    coverage: Coverage
    trace: List[TraceLink]
    report_path: str
    iterations: int
