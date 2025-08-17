import json
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from agents.shared_llm import llm
from tools.patch import apply_unified_diff
# agents/repair_agent.py
import json, os, re
from typing import Optional, Dict, Any
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from agents.shared_llm import llm
from tools.patch import apply_unified_diff

prompt = ChatPromptTemplate.from_messages([
  ("system",
   "Suggest minimal unified diffs to resolve findings without introducing MISRA-banned constructs. "
   "Only reference rules included in context.rules. "
   "Return exactly one JSON object with key 'patches' (array of objects with rule_id, rationale, diff). "
   "Wrap the JSON in a fenced json code block. No extra text."),
  ("human",
   "Original:\n```c\n{code}\n```\nFindings:\n{findings_json}\nContext.rules:\n{rules_json}")
])

_str = StrOutputParser()
_DEBUG_PATH = os.path.join("reports", "_debug_repair_last.txt")

def _ensure_str(obj) -> str:
    if isinstance(obj, str):
        return obj
    content = getattr(obj, "content", None)
    return content if isinstance(content, str) else str(obj)

def _extract_json(text: str) -> Dict[str, Any]:
    m = re.search(r"""```json\s*(\{.*?\})\s*```""", text, flags=re.S | re.I)
    if m:
        return json.loads(m.group(1))
    # fallback: first balanced object
    in_str = False; esc = False; depth = 0; start = -1
    for i, ch in enumerate(text):
        if in_str:
            if esc: esc = False
            elif ch == "\\": esc = True
            elif ch == '"': in_str = False
            continue
        else:
            if ch == '"': in_str = True; continue
            if ch == '{':
                if depth == 0: start = i
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
    return {"patches": []}

def suggest_patches(code: str, findings, rules_json):
    payload = {
        "code": code,
        "findings_json": json.dumps(findings, ensure_ascii=False),
        "rules_json": rules_json if isinstance(rules_json, str) else json.dumps(rules_json, ensure_ascii=False),
    }
    raw = (prompt | llm | _str).invoke(payload)
    raw_text = _ensure_str(raw)

    os.makedirs(os.path.dirname(_DEBUG_PATH), exist_ok=True)
    with open(_DEBUG_PATH, "w", encoding="utf-8") as f:
        f.write(raw_text)

    data = _extract_json(raw_text)
    patches = data.get("patches", [])
    patched = code
    for p in patches:
        diff = p.get("diff", "")
        patched = apply_unified_diff(patched, diff)
    return patches, patched

"""
prompt = ChatPromptTemplate.from_messages([
  ("system",
   "Suggest minimal unified diffs to resolve findings without introducing MISRA-banned constructs. "
   "Only reference rules included in context.rules. "
   "Output format: respond ONLY with JSON having key 'patches' (array of objects with "
   "fields 'rule_id', 'rationale', 'diff')."),
  ("human",
   "Original:\n```c\n{code}\n```\nFindings:\n{findings_json}\nContext.rules:\n{rules_json}")
])
parser = JsonOutputParser()

def suggest_patches(code: str, findings, rules_json):
    payload = {
        "code": code,
        "findings_json": json.dumps(findings, ensure_ascii=False),
        "rules_json": rules_json if isinstance(rules_json, str) else json.dumps(rules_json, ensure_ascii=False),
    }
    out = (prompt | llm | parser).invoke(payload)
    patched = code
    for p in out.get("patches", []):
        patched = apply_unified_diff(patched, p["diff"])
    return out.get("patches", []), patched
"""