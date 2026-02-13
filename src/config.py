from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_name: str = "FastAPI RAG Application"
    app_version: str = "0.1.0"
    debug: bool = False

    # Mistral API Settings
    mistral_api_key: str = ""
    mistral_model: str = "mistral-small-latest"

    # ChromaDB Settings
    chroma_persist_directory: str = "./chroma_db"
    chroma_collection_name: str = "pdf_documents"

    # Upload Settings
    upload_dir: str = "./uploads"
    max_upload_size: int = 10 * 1024 * 1024  # 10 MB

    # RAG Settings
    retrieval_top_k: int = 5
    concurrency: int = 10

    # Logfire
    logfire_token: str = ""


settings = Settings()
