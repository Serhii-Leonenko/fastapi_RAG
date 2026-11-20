from fastapi import Request

from protocols import FileProcessorProtocol, VectorStoreProtocol, RAGServiceProtocol


def get_file_processors(request: Request) -> dict[str, FileProcessorProtocol]:
    """
    Return the registry of file processors keyed by lowercase file extension (e.g. ".pdf").
    """
    return request.app.state.file_processors


def get_vector_store(request: Request) -> VectorStoreProtocol:
    return request.app.state.vector_store


def get_rag_service(request: Request) -> RAGServiceProtocol:
    return request.app.state.rag_service
