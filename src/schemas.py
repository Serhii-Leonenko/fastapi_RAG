from typing import Any

from pydantic import BaseModel, Field


class QueryRequest(BaseModel):
    question: str = Field(description="The question to ask")
    top_k: int | None = Field(
        default=None,
        description="Number of documents to retrieve (optional)",
        ge=1,
        le=20,
    )


class UploadResponse(BaseModel):
    message: str
    filename: str
    total_documents: int


class DocumentInfo(BaseModel):
    filename: str
    chunk_count: int


class StatsResponse(BaseModel):
    total_documents: int
    total_chunks: int
    unique_files: list[str]


class RAGResponse(BaseModel):
    answer: str = Field(description="The generated answer based on the context")
    sources: list[dict[str, Any]] = Field(
        default_factory=list, description="Source documents used to generate the answer"
    )
