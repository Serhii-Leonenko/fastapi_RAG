from fastapi import Request

from protocols import PDFProcessorProtocol, VectorStoreProtocol, RAGServiceProtocol


def get_pdf_processor(request: Request) -> PDFProcessorProtocol:
    return request.app.state.pdf_processor


def get_vector_store(request: Request) -> VectorStoreProtocol:
    return request.app.state.vector_store


def get_rag_service(request: Request) -> RAGServiceProtocol:
    return request.app.state.rag_service

