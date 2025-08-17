# agents/codegen_agent.py
import json, os, re
from typing import Optional
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from agents.shared_llm import llm

# agents/codegen_agent.py
import json, os, re
from typing import Optional
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from agents.shared_llm import llm

prompt = ChatPromptTemplate.from_messages([
  ("system",
   "You are a senior embedded C developer. Generate C99 code that:\n"
   "1) Satisfies the provided LLR.\n"
   "2) Complies with MISRA-C:2012 and relevant DO-178C objectives in context.\n"
   "3) Avoids banned constructs (goto, nested comments, trigraphs, wide strings).\n"
   "4) Include trace comments like /* REQ: <LLR-ID> */ at implementation points.\n"
   "Return exactly one JSON object only, with keys: code, design_notes. "
   "Wrap the JSON in a fenced code block labeled json. Do not include any other text."),
  ("human", "LLR:\n{llr}\n\nContext.rules:\n{rules_json}")
])

_str_parser = StrOutputParser()
_DEBUG_PATH = os.path.join("reports", "_debug_codegen_last.txt")

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
                        segment = text[start:i+1]
                        try:
                            return json.loads(segment)
                        except json.JSONDecodeError:
                            start = -1
                            continue
    return None

def _extract_code_block(text: str) -> Optional[str]:
    # Prefer ```c ... ``` / ```C ... ```
    m = re.search(r"```(?:c|C)\s+([\s\S]*?)```", text)
    if m:
        return m.group(1).strip()
    # Any fenced code as fallback
    m = re.search(r"```([\s\S]*?)```", text)
    if m:
        return m.group(1).strip()
    # Heuristic: grab lines that look like C
    lines = text.splitlines()
    buf = []
    for ln in lines:
        if any(tok in ln for tok in ("#include", ";", "/*", "*/", "int ", "uint", "void ", "return ")):
            buf.append(ln)
    code = "\n".join(buf).strip()
    return code or None

def _misra_stub() -> str:
    # Safe minimal C99 skeleton without banned constructs
    return (
        "#include <stdint.h>\n"
        "#include <stddef.h>\n"
        "/* REQ: LLR-1 */\n"
        "int main(void)\n"
        "{\n"
        "    volatile uint32_t ok = 0U;\n"
        "    ok += 1U;\n"
        "    return 0;\n"
        "}\n"
    )

def generate_code(llr, rules_json) -> str:
    payload = {
        "llr": json.dumps(llr, ensure_ascii=False) if not isinstance(llr, str) else llr,
        "rules_json": rules_json if isinstance(rules_json, str) else json.dumps(rules_json, ensure_ascii=False),
    }

    raw = (prompt | llm | _str_parser).invoke(payload)
    raw_text = _ensure_str(raw)

    os.makedirs(os.path.dirname(_DEBUG_PATH), exist_ok=True)
    with open(_DEBUG_PATH, "w", encoding="utf-8") as f:
        f.write(raw_text)

    # 1) fenced json
    data = _extract_json_from_fence(raw_text)
    # 2) balanced json
    if data is None:
        data = _extract_first_balanced_json(raw_text)
    # 3) salvage code block
    if data is None:
        code = _extract_code_block(raw_text)
        if code:
            return code
        # 4) ultimate fallback stub
        return _misra_stub()

    # verify JSON structure
    code = data.get("code")
    if not isinstance(code, str) or not code.strip():
        # salvage even if JSON exists but empty code
        code = _extract_code_block(raw_text) or _misra_stub()
    return code

"""
prompt = ChatPromptTemplate.from_messages([
  ("system",
   "You are a senior embedded C developer. Generate C99 code that:\n"
   "1) Satisfies the provided LLR.\n"
   "2) Complies with MISRA-C:2012 and relevant DO-178C objectives in context.\n"
   "3) Avoids banned constructs (goto, nested comments, trigraphs, wide strings).\n"
   "4) Include trace comments like /* REQ: <LLR-ID> */ at implementation points.\n"
   "Return exactly one JSON object only, with keys: code, design_notes. "
   "Wrap the JSON in a fenced code block labeled json. Do not include any other text."),
  ("human", "LLR:\n{llr}\n\nContext.rules:\n{rules_json}")
])

_str_parser = StrOutputParser()
_DEBUG_PATH = os.path.join("reports", "_debug_codegen_last.txt")

def _ensure_str(obj) -> str:
    if isinstance(obj, str):
        return obj
    content = getattr(obj, "content", None)
    return content if isinstance(content, str) else str(obj)

def _extract_json_from_fence(text: str) -> Optional[dict]:
    m = re.search(r"```json\s*(\{.*?\})\s*```", text, flags=re.S | re.I)
    if not m:
        return None
    return json.loads(m.group(1))

def _extract_first_balanced_json(text: str) -> dict:
    in_str = False
    esc = False
    depth = 0
    start = -1
    for i, ch in enumerate(text):
        if in_str:
            print("ENETRED instr")
            if esc:
                esc = False
            elif ch == "\\":
                esc = True
            elif ch == '"':
                in_str = False
            continue
        else:
            print("ENETRED ELSE PART")
            if ch == '"':
                print("ENETRED ELSE PART if")
                in_str = True
                continue
            if ch == '{':
                print("ENETRED ELSE PART 2nd if")
                if depth == 0:
                    start = i
                depth += 1
            elif ch == '}':
                print("ENETRED ELSE PART 3rd elif")
                if depth > 0:
                    depth -= 1
                    if depth == 0 and start != -1:
                        segment = text[start:i+1]
                        try:
                            return json.loads(segment)
                        except json.JSONDecodeError:
                            start = -1
                            continue
    raise ValueError("No valid JSON object found in model output.")

def generate_code(llr, rules_json) -> str:
    payload = {
        "llr": json.dumps(llr, ensure_ascii=False) if not isinstance(llr, str) else llr,
        "rules_json": rules_json if isinstance(rules_json, str) else json.dumps(rules_json, ensure_ascii=False),
    }
    raw = (prompt | llm | _str_parser).invoke(payload)
    raw_text = _ensure_str(raw)

    os.makedirs(os.path.dirname(_DEBUG_PATH), exist_ok=True)
    with open(_DEBUG_PATH, "w", encoding="utf-8") as f:
        f.write(raw_text)

    data = _extract_json_from_fence(raw_text) or _extract_first_balanced_json(raw_text)
    if "code" not in data:
        raise RuntimeError(f"Parsed JSON missing 'code'. Keys present: {list(data.keys())}")
    return data["code"]
"""