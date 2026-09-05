import os
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent.parent
UPLOAD_DIR = BASE_DIR / "uploads"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=[str(BASE_DIR.parent / ".env"), str(BASE_DIR / ".env")],
        env_file_encoding="utf-8",
        extra="ignore"
    )
    PROJECT_NAME: str = "AI Teacher - Human-Like Adaptive AI Educator"
    API_V1_STR: str = "/api"
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", os.getenv("GOOGLE_API_KEY", ""))
    DEFAULT_LLM_MODEL: str = os.getenv("DEFAULT_LLM_MODEL", "gemini-3.7-flash")
    UPLOAD_DIR: Path = UPLOAD_DIR
    HOST: str = "127.0.0.1"
    PORT: int = 8000
    CORS_ORIGINS: list[str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "*"
    ]
    # RAG Subsystem Settings
    RAG_CHUNK_SIZE: int = 500
    RAG_CHUNK_OVERLAP: int = 100
    RAG_MIN_RELEVANCE_SCORE: float = 0.35
    EMBEDDING_PROVIDER: str = "auto"
    EMBEDDING_MODEL: str = "models/text-embedding-004"
    RAG_MAX_FILE_SIZE_MB: int = 50

    # Video Engine Subsystem (Agent 4)
    VIDEO_PROVIDER: str = os.getenv("VIDEO_PROVIDER", "opencv_pil")
    VIDEO_MODEL: str = os.getenv("VIDEO_MODEL", "deterministic_v1")
    TTS_PROVIDER: str = os.getenv("TTS_PROVIDER", "mock_agent5")
    AVATAR_PROVIDER: str = os.getenv("AVATAR_PROVIDER", "mock_agent5")
    VIDEO_OUTPUT_DIR: Path = UPLOAD_DIR / "video_assets"
    VIDEO_RESOLUTION: str = os.getenv("VIDEO_RESOLUTION", "1920x1080")
    VIDEO_FORMAT: str = os.getenv("VIDEO_FORMAT", "mp4")
    DEMO_MODE: bool = os.getenv("DEMO_MODE", "true").lower() in ("true", "1", "yes")
    ENABLE_MOCK_PROVIDERS: bool = True
    MAX_RETEACH_ATTEMPTS: int = 2
    LOG_LEVEL: str = "INFO"
    APP_ENV: str = "development"

    # Provider Configuration
    LLM_PROVIDER: str = "gemini"
    VOICE_PROVIDER: str = os.getenv("VOICE_PROVIDER", "mock")  # mock, elevenlabs, openai
    VOICE_API_KEY: str = os.getenv("VOICE_API_KEY", "")
    VOICE_DEFAULT_ID: str = os.getenv("VOICE_DEFAULT_ID", "teacher_voice_01")
    AVATAR_PROVIDER: str = os.getenv("AVATAR_PROVIDER", "mock")  # mock, did, heygen
    AVATAR_API_KEY: str = os.getenv("AVATAR_API_KEY", "")
    AVATAR_DEFAULT_ID: str = os.getenv("AVATAR_DEFAULT_ID", "teacher_avatar_01")
    VECTOR_STORE: str = "in_memory_keyword"

    # Avatar & Voice Engine Subsystem (Agent 5)
    VOICE_CACHE_DIR: Path = BASE_DIR / "data" / "cache" / "voice"
    AVATAR_CACHE_DIR: Path = BASE_DIR / "data" / "cache" / "avatar"
    MAX_PROVIDER_RETRIES: int = 2
    MAX_DURATION_DRIFT_SECONDS: float = 0.5

settings = Settings()
settings.VOICE_CACHE_DIR.mkdir(parents=True, exist_ok=True)
settings.AVATAR_CACHE_DIR.mkdir(parents=True, exist_ok=True)
settings.VIDEO_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

