import regex as re
# tools/lint_misra_light.py
import re

# Simple, deterministic scans for common MISRA bans.
# NOTE: These are heuristic (not a full C parser).

import re
# tools/lint_misra_light.py
import re

import re

BANNED_PATTERNS = {
    "14.4": re.compile(r"\bgoto\b"),                       # goto banned
    "7.8":  re.compile(r"""L"[^"]*"|L'[^']*'"""),          # wide strings/chars
    "7.7":  re.compile(r"\?\?[=/'()!<>-]"),                # trigraphs
}

def _has_nested_comments(code: str) -> bool:
    i = 0
    n = len(code)
    while i < n:
        if i + 1 < n and code[i] == '/' and code[i + 1] == '*':
            i += 2  # enter comment
            while i < n:
                if i + 1 < n and code[i] == '/' and code[i + 1] == '*':
                    return True  # nested start before closing
                if i + 1 < n and code[i] == '*' and code[i + 1] == '/':
                    i += 2  # close comment
                    break
                i += 1
            continue
        i += 1
    return False

def lint_code(code: str):
    findings = []

    # Rule 7.9 — comments shall not be nested (approx)
    if _has_nested_comments(code):
        findings.append({
            "rule_id": "7.9",
            "msg": "Nested comments detected",
            "severity": "error",
            "line": 1,
        })

    # Regex bans
    for rule, pat in BANNED_PATTERNS.items():
        for m in pat.finditer(code):
            line = code.count("\n", 0, m.start()) + 1
            findings.append({
                "rule_id": rule,
                "msg": "Banned construct",
                "severity": "error",
                "line": line,
            })
    return {"findings": findings}


