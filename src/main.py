from fastapi import FastAPI
from contextlib import asynccontextmanager

from pdf_processor import get_pdf_processor
from rag_service import get_rag_service
from src.config import settings
from src.routes import router
from vector_store import get_vector_store


@asynccontextmanager
async def lifespan(app: FastAPI):
    print(f"Starting {settings.app_name} v{settings.app_version}")
    print(f"Mistral model: {settings.mistral_model}")
    print(f"ChromaDB persist directory: {settings.chroma_persist_directory}")

    print("Initializing services...")
    get_pdf_processor()
    get_vector_store()
    get_rag_service()
    print("Services initialized.")

    yield

    print("Shutting down application...")


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    lifespan=lifespan,
)

app.include_router(router, prefix="/api", tags=["RAG"])


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("src.main:app", host="127.0.0.1", port=8000, reload=settings.debug)
