# agents/shared_llm.py
from langchain_community.llms import LlamaCpp
from langchain_core.runnables import RunnableLambda
import os, traceback

# === Set your model path here ===
MODEL_PATH = r"C:\New folder\AI\llama\Llama-3.2-3B-Instruct-Q8_0.gguf"

def _build_llm() -> LlamaCpp:
    if not os.path.exists(MODEL_PATH):
        raise FileNotFoundError(f"GGUF not found at: {MODEL_PATH}")
    return LlamaCpp(
        model_path=MODEL_PATH,
        n_ctx=131072,
        n_batch=256,  # lower to 2048 if memory is tight
        n_threads=min(8, os.cpu_count() or 4),
        n_gpu_layers=0,             # 0 = CPU-only; use -1 for full GPU offload if your wheel supports it
        f16_kv=True,
        temperature=0.2,            # low temp = more deterministic
        top_p=0.9,
        repeat_penalty=1.1,
        verbose=False,
    )

try:
    llm = _build_llm()
except Exception:
    _err = traceback.format_exc()

    def _raise(_input, _config=None):
        # Show the real underlying error
        raise RuntimeError(
            "Failed to load LlamaCpp. Fix MODEL_PATH and ensure the correct llama-cpp-python wheel is installed.\n"
            f"--- BEGIN STACK ---\n{_err}\n--- END STACK ---"
        )

    llm = RunnableLambda(_raise)
