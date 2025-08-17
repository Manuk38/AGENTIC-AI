
import json
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from agents.shared_llm import llm
from tools.lint_misra_light import lint_code
# agents/auditor_agent.py
import json, os, re
from typing import Optional, List, Dict, Any
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from agents.shared_llm import llm
from tools.lint_misra_light import lint_code

prompt = ChatPromptTemplate.from_messages([
  ("system",
   "Act as a strict MISRA/DO-178C auditor. Only cite rules present in context.rules. "
   "Return exactly one JSON object with key 'findings' (array of objects with fields: "
   "rule_id, msg, severity, optional line). Wrap the JSON in a fenced json code block. "
   "No extra text before or after."),
  ("human", "Code:\n```c\n{code}\n```\nContext.rules:\n{rules_json}\nLint:\n{lint_json}")
])

_str = StrOutputParser()
_DEBUG_PATH = os.path.join("reports", "_debug_auditor_last.txt")

def _ensure_str(obj) -> str:
    if isinstance(obj, str):
        return obj
    content = getattr(obj, "content", None)
    return content if isinstance(content, str) else str(obj)

def _extract_json_from_fence(text: str) -> Optional[dict]:
    m = re.search(r"""```json\s*(\{.*?\})\s*```""", text, flags=re.S | re.I)
    if not m:
        return None
    return json.loads(m.group(1))

def _extract_first_balanced_json(text: str) -> Optional[dict]:
    in_str = False
    esc = False
    depth = 0
    start = -1
    for i, ch in enumerate(text):
        if in_str:
            if esc:
                esc = False
            elif ch == "\\":
                esc = True
            elif ch == '"':
                in_str = False
            continue
        else:
            if ch == '"':
                in_str = True
                continue
            if ch == '{':
                if depth == 0:
                    start = i
                depth += 1
            elif ch == '}':
                if depth > 0:
                    depth -= 1
                    if depth == 0 and start != -1:
                        seg = text[start:i+1]
                        try:
                            return json.loads(seg)
                        except json.JSONDecodeError:
                            start = -1
                            continue
    return None

def audit_code(code: str, rules_json: str) -> List[Dict[str, Any]]:
    lint = lint_code(code)
    payload = {
        "code": code,
        "rules_json": rules_json if isinstance(rules_json, str) else json.dumps(rules_json, ensure_ascii=False),
        "lint_json": json.dumps(lint, ensure_ascii=False),
    }

    raw = (prompt | llm | _str).invoke(payload)
    raw_text = _ensure_str(raw)

    os.makedirs(os.path.dirname(_DEBUG_PATH), exist_ok=True)
    with open(_DEBUG_PATH, "w", encoding="utf-8") as f:
        f.write(raw_text)

    data = _extract_json_from_fence(raw_text) or _extract_first_balanced_json(raw_text) or {"findings": []}

    findings = data.get("findings", [])
    if not isinstance(findings, list):
        findings = []

    # Merge deterministic lint findings (and de-dupe)
    findings.extend(lint["findings"])
    uniq = {(f.get("rule_id"), f.get("line"), f.get("msg")): f for f in findings if isinstance(f, dict)}
    return list(uniq.values())

"""
critic = ChatPromptTemplate.from_messages([
  ("system",
   "Be a strict MISRA/DO-178C auditor. Only cite rules present in context.rules.\n"
   "Output format: respond ONLY with JSON having key 'findings' (array of objects with "
   "fields 'rule_id', 'msg', 'severity', and optional 'line')."),
  ("human", "Code:\n```c\n{code}\n```\nContext.rules:\n{rules_json}\nLint:\n{lint_json}")
])
parser = JsonOutputParser()

def audit_code(code: str, rules_json: str):
    lint = lint_code(code)
    payload = {
        "code": code,
        "rules_json": rules_json if isinstance(rules_json, str) else json.dumps(rules_json, ensure_ascii=False),
        "lint_json": json.dumps(lint, ensure_ascii=False),
    }
    out = (critic | llm | parser).invoke(payload)
    findings = out.get("findings", [])
    findings.extend(lint["findings"])
    uniq = {(f.get("rule_id"), f.get("line"), f.get("msg")): f for f in findings}
    return list(uniq.values())
"""