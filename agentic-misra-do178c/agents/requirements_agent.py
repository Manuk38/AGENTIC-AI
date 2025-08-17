import json
def to_llr(nlr: str, constraints: dict):
    # Deterministic LLR skeleton for offline start. Replace with LLM chain if desired.
    return {
        "items": [
            {"id": "LLR-1", "text": f"Implement: {nlr}", "tests": ["T-1"], "anchors": []}
        ],
        "constraints": constraints
    }
