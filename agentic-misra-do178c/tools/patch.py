# Minimal diff apply: if diff contains a full replacement marker, use it; else return original.
# For production, integrate 'python-patch' or 'git apply' flow.
import regex as re

def apply_unified_diff(original: str, diff: str) -> str:
    # Very naive support: if diff contains a block '--- ORIGINAL\n+++ UPDATED\n@@' we skip and return original.
    # Allow a custom replacement format:
    # <<<NEW>>>\n<new code>\n<<<END>>>
    m = re.search(r"<<<NEW>>>\n(?P<new>.*)\n<<<END>>>", diff, re.S)
    if m:
        return m.group("new")
    return original
