from pathlib import Path

TEMPLATE = """---
title: "{title}"
domain: "embedded_c"
tags: ["misra","control-flow"]
standard: "{standard}"
rule_id: "{rule_id}"
source_type: "local"
sources:
  - "{source}"
license: "unknown"
version: "{version}"
---

## Summary
{summary}

## Rationale
{rationale_bullets}

## Example (Non-compliant)
```c
{noncompliant_code}
```
"""

def write_front_matter_report(title:str, standard:str, rule_id:str, source:str, version:str,
                              summary:str, rationale_bullets:str, noncompliant_code:str,
                              filename:str="reports/misra_report.md") -> str:
    md = TEMPLATE.format(
        title=title, standard=standard, rule_id=rule_id, source=source, version=version,
        summary=summary, rationale_bullets=rationale_bullets, noncompliant_code=noncompliant_code
    )
    Path(filename).parent.mkdir(parents=True, exist_ok=True)
    Path(filename).write_text(md, encoding="utf-8")
    return filename
