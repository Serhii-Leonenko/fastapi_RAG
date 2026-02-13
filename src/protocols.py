from typing import Protocol, Any

from dtos import PDFResult


class PDFProcessorProtocol(Protocol):
    def save_uploaded_file(self, content: bytes, filename: str) -> str:
        pass

    def process_pdf(self, pdf_path: str, filename: str) -> PDFResult:
        pass

    def delete_file(self, file_path: str) -> None:
        pass


class VectorStoreProtocol(Protocol):
    def add_documents(self, pdf_result: PDFResult) -> None:
        pass

    def search(self, query: str, top_k: int = None) -> dict[str, Any]:
        pass

    def count_documents(self) -> int:
        pass

    def delete_by_filename(self, filename: str) -> None:
        pass

    def reset(self) -> None:
        pass

    def get_all_filenames(self) -> list[str]:
        pass


class RAGServiceProtocol(Protocol):
    async def query(self, question: str, top_k: int = None) -> str:
        pass
