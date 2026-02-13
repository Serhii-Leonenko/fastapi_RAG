from contextlib import asynccontextmanager

from fastapi import FastAPI

from src.config import settings
from src.pdf_processor import PDFProcessor
from src.rag_service import RAGService
from src.routes import router
from src.vector_store import VectorStore


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for FastAPI application.
    Initializes services on startup and stores them in app.state.
    """
    print(f"Starting {settings.app_name} v{settings.app_version}")
    print(f"Mistral model: {settings.mistral_model}")
    print(f"ChromaDB persist directory: {settings.chroma_persist_directory}")

    print("Initializing services...")
    app.state.pdf_processor = PDFProcessor()
    app.state.vector_store = VectorStore()
    app.state.rag_service = RAGService(vector_store=app.state.vector_store)
    print("Services initialized and stored in app.state")

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
