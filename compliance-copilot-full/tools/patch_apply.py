from __future__ import annotations
from langchain_core.tools import tool

@tool
def apply_patch(original_path: str, unified_diff: str) -> dict:
    """Safely write a .patch next to the file. Returns paths. (Does not execute code.)"""
    try:
        patch_path = original_path + ".refactor.patch"
        with open(patch_path, "w", encoding="utf-8") as f:
            f.write(unified_diff)
        return {"patch_path": patch_path}
    except Exception as e:
        return {"error": str(e)}
