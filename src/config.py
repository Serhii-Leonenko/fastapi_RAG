from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_name: str = "FastAPI RAG Application"
    app_version: str = "0.1.0"
    debug: bool = False

    # Google Gemini API Settings
    gemini_api_key: str = ""
    gemini_model: str = "gemini-2.5-flash"
    gemini_timeout_seconds: float = 20.0  # per HTTP request to Gemini
    gemini_max_attempts: int = 3  # total attempts, including the first one
    gemini_retry_initial_delay: float = 1.0  # seconds, grows exponentially
    gemini_retry_max_delay: float = 10.0  # seconds, cap for backoff delay

    # ChromaDB Settings
    chroma_persist_directory: str = "./chroma_db"
    chroma_collection_name: str = "pdf_documents"

    # Upload Settings
    upload_dir: str = "./uploads"
    max_upload_size: int = 10 * 1024 * 1024  # 10 MB

    # Chunking Settings
    chunking_strategy: Literal["sentence", "recursive", "semantic"] = "sentence"
    chunk_size: int = 1000  # characters, recursive strategy only
    chunk_overlap: int = 200  # characters, recursive strategy only
    semantic_embedding_model: str = "all-MiniLM-L6-v2"  # semantic strategy only
    semantic_breakpoint_percentile: float = 90.0  # higher = fewer, larger chunks
    semantic_buffer_size: int = 0  # neighbouring sentences embedded with each one

    # RAG Settings
    retrieval_top_k: int = 5
    concurrency: int = 10

    # Logfire
    logfire_token: str = ""


settings = Settings()
