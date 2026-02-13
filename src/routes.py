from typing import Annotated, Dict

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile

from protocols import PDFProcessorProtocol, RAGServiceProtocol, VectorStoreProtocol
from schemas import QueryRequest, RAGResponse, StatsResponse, UploadResponse
from src.config import settings
from src.dependencies import get_pdf_processor, get_rag_service, get_vector_store

router = APIRouter()


@router.post("/upload", response_model=UploadResponse)
async def upload_pdf(
    pdf_processor: Annotated[PDFProcessorProtocol, Depends(get_pdf_processor)],
    vector_store: Annotated[VectorStoreProtocol, Depends(get_vector_store)],
    file: Annotated[UploadFile, File(description="PDF file to upload")],
) -> UploadResponse:
    """
    Upload a PDF file and add it to the vector store.
    """
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported")

    content = await file.read()
    if len(content) > settings.max_upload_size:
        raise HTTPException(
            status_code=400,
            detail=f"File size exceeds maximum allowed size of {settings.max_upload_size / (1024 * 1024):.1f} MB",
        )

    try:
        file_path = pdf_processor.save_uploaded_file(content, file.filename)
        pdf_result = pdf_processor.process_pdf(file_path, file.filename)

        vector_store.add_documents(pdf_result=pdf_result)
        total_docs = vector_store.count_documents()

        return UploadResponse(
            message="PDF uploaded and processed successfully",
            filename=file.filename,
            total_documents=total_docs,
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing PDF: {str(e)}")


@router.post("/query", response_model=RAGResponse)
async def query_rag(
    request: QueryRequest,
    rag_service: Annotated[RAGServiceProtocol, Depends(get_rag_service)],
):
    """
    Query the RAG system with a question.
    """
    try:
        response = await rag_service.query(
            question=request.question, top_k=request.top_k
        )
        return response

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing query: {str(e)}")


@router.get("/stats", response_model=StatsResponse)
async def get_stats(
    vector_store: Annotated[VectorStoreProtocol, Depends(get_vector_store)],
) -> StatsResponse:
    """
    Get statistics about the vector store.
    """
    try:
        total_chunks = vector_store.count_documents()
        unique_files = vector_store.get_all_filenames()

        return StatsResponse(
            total_documents=len(unique_files),
            total_chunks=total_chunks,
            unique_files=unique_files,
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving stats: {str(e)}")


@router.delete("/documents/{filename}")
async def delete_document(
    filename: str,
    vector_store: Annotated[VectorStoreProtocol, Depends(get_vector_store)],
    pdf_processor: Annotated[PDFProcessorProtocol, Depends(get_pdf_processor)],
) -> dict[str, str]:
    """
    Delete a document from the vector store and delete the PDF file from the upload directory.
    """
    try:
        vector_store.delete_by_filename(filename)
        pdf_processor.delete_file(filename)

        return {"message": f"Document '{filename}' deleted successfully"}

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error deleting document: {str(e)}"
        )


@router.post("/reset")
async def reset_database(
    vector_store: Annotated[VectorStoreProtocol, Depends(get_vector_store)],
) -> Dict[str, str]:
    """
    Reset the vector store.
    """
    try:
        vector_store.reset()

        return {"message": "Vector database reset successfully"}

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error resetting database: {str(e)}"
        )


@router.get("/health")
async def health_check() -> Dict[str, str]:
    """
    Health check endpoint.
    """
    return {
        "status": "healthy",
        "app": settings.app_name,
        "version": settings.app_version,
    }
