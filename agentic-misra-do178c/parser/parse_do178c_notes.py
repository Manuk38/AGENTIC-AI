# parse_do178c_notes.py
# Converts your own DO-178C summarized notes (YAML) into JSONL for RAG.
import yaml, json, sys
from pathlib import Path

def main(yaml_path: str, out_path="parser/do178c_notes.jsonl"):
    data = yaml.safe_load(open(yaml_path, encoding="utf-8"))
    # Expected top-level: list of {id, title, objective, guidance, references}
    Path(out_path).parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        for item in data:
            item.setdefault("standard", "DO-178C")
            f.write(json.dumps(item, ensure_ascii=False) + "\n")
    print(f"Wrote {out_path} with {len(data)} items.")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python parser/parse_do178c_notes.py notes.yaml [out.jsonl]")
        raise SystemExit(2)
    main(sys.argv[1], sys.argv[2] if len(sys.argv)>2 else "parser/do178c_notes.jsonl")
