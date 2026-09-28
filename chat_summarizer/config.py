"""Environment-driven configuration."""
import os
from dataclasses import dataclass, field

from dotenv import load_dotenv

load_dotenv()


def _split(value: str) -> list[str]:
    return [item.strip() for item in value.split(",") if item.strip()]


@dataclass
class Settings:
    storage_backend: str = "memory"
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_db: int = 0
    openai_api_key: str | None = None
    cors_origins: list[str] = field(default_factory=lambda: ["http://localhost:8000"])
    use_ml_models: bool = False

    @classmethod
    def from_env(cls) -> "Settings":
        return cls(
            storage_backend=os.getenv("STORAGE_BACKEND", "memory").lower(),
            redis_host=os.getenv("REDIS_HOST", "localhost"),
            redis_port=int(os.getenv("REDIS_PORT", "6379")),
            redis_db=int(os.getenv("REDIS_DB", "0")),
            openai_api_key=os.getenv("OPENAI_API_KEY") or None,
            cors_origins=_split(os.getenv("CORS_ORIGINS", "http://localhost:8000")),
            use_ml_models=os.getenv("USE_ML_MODELS", "false").lower() == "true",
        )
