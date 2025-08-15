from pydantic import BaseModel
from dotenv import load_dotenv
from pathlib import Path
import os

load_dotenv()

class Settings(BaseModel):
    llm_backend: str = os.getenv("LLM_BACKEND", "ollama")
    ollama_model: str = os.getenv("OLLAMA_MODEL", "llama3")
    openai_model: str = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    embed_model: str = os.getenv("EMBED_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
    vector_store: str = os.getenv("VECTOR_STORE", "faiss")
    data_dir: Path = Path(os.getenv("DATA_DIR", "./data/standards"))
    index_dir: Path = Path(os.getenv("INDEX_DIR", "./data/index"))

settings = Settings()
settings.index_dir.mkdir(parents=True, exist_ok=True)
