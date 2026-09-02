from dataclasses import dataclass
from pathlib import Path
import os
from typing import Optional

from dotenv import load_dotenv


PROJECT_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(Path(__file__).with_name(".env"))


@dataclass(frozen=True)
class Settings:
    ollama_model: str
    ollama_base_url: Optional[str]
    cors_origins: list[str]
    vector_store_path: Path


def get_settings() -> Settings:
    origins = os.getenv("CORS_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173")
    vector_store_path = Path(os.getenv("VECTOR_STORE_PATH", PROJECT_ROOT / ".vector_store"))
    if not vector_store_path.is_absolute():
        vector_store_path = PROJECT_ROOT / vector_store_path
    return Settings(
        ollama_model=os.getenv("OLLAMA_MODEL", "phi"),
        ollama_base_url=os.getenv("OLLAMA_BASE_URL") or None,
        cors_origins=[origin.strip() for origin in origins.split(",") if origin.strip()],
        vector_store_path=vector_store_path,
    )
