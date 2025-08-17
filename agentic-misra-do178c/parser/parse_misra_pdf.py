# parse_misra_pdf.py
# pip install pdfminer.six regex
from pdfminer.high_level import extract_text
import regex as re
import json
from pathlib import Path
from typing import Dict, List

HEADINGS = [
    "Interpretation",
    "Functional specification",
    "Precaution",
    "Limitation",
    "note", "Note", "[note]"
]

RULE_HDR = re.compile(
    r'(?m)^\s*(?P<section>\d+(?:\.\d+)+)\.\s*Rule\s+(?P<rule_id>\d+)\s*(?P<ns>\(Not supported\))?\s*$'
)

CAT_LINE = re.compile(r'(?mi)^\s*\((?P<cat>required|advisory)\)\s*:\s*(?P<req>.+?)\s*$')

def normalize(txt: str) -> str:
    # Remove page gutters like "-  - 22", weird bullets, smart quotes, repeated spaces
    txt = re.sub(r'\s*-\s*-\s*\d+\s*$', '', txt, flags=re.M)
    txt = txt.replace('�', '').replace('“','"').replace('”','"').replace('‘',"'").replace('’',"'")
    txt = re.sub(r'[ \t]+$', '', txt, flags=re.M)
    return txt

def split_rules(txt: str) -> List[Dict]:
    rules = []
    matches = list(RULE_HDR.finditer(txt))
    for i, m in enumerate(matches):
        start = m.end()
        end = matches[i+1].start() if i+1 < len(matches) else len(txt)
        block = txt[start:end].strip()
        rule_id = m.group('rule_id')
        not_supported = bool(m.group('ns'))
        # category + requirement text: may be on the next line(s)
        catm = CAT_LINE.search(block)
        category, requirement = None, None
        if catm:
            category = catm.group('cat').lower()
            requirement = catm.group('req').strip()

        def extract_section(name: str) -> str:
            # get text between heading and next heading
            pat = re.compile(rf'(?mi)^\s*{re.escape(name)}\s*$', flags=re.M)
            found = list(pat.finditer(block))
            if not found:
                return ""
            s = found[0].end()
            # find next heading
            nextpos = min([n.start() for h in HEADINGS
                           for n in [re.search(rf'(?mi)^\s*{re.escape(h)}\s*$', block[s:])]
                           if n] or [len(block)-s])
            return block[s:s+nextpos].strip()

        data = {
            "rule_id": rule_id,
            "support_status": "not_supported" if not_supported else "supported",
            "category": category,  # "required" | "advisory" | None when missing
            "requirement_text": requirement,
            "interpretation": extract_section("Interpretation"),
            "functional_specification": extract_section("Functional specification"),
            "precaution": extract_section("Precaution"),
            "limitation": extract_section("Limitation"),
            "source_doc": "local_pdf",
            "standard": "MISRA-C-2012",
            "version": "2025-08-15"
        }
        rules.append(data)
    return rules

def main(pdf_path: str, out_path="misra_rules.jsonl"):
    raw = extract_text(pdf_path)
    txt = normalize(raw)
    items = split_rules(txt)
    with open(out_path, "w", encoding="utf-8") as f:
        for it in items:
            f.write(json.dumps(it, ensure_ascii=False) + "\n")
    print(f"Extracted {len(items)} rules → {out_path}")

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python parse_misra_pdf.py /path/to/misra_rules.pdf")
        raise SystemExit(2)
    main(sys.argv[1])
