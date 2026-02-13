import os
from typing import List, Dict, Any
import chromadb
from chromadb.config import Settings as ChromaSettings

from dtos import PDFResult
from src.config import settings


class VectorStore:
    """Manages vector storage and retrieval using ChromaDB."""

    def __init__(self):
        self.client = chromadb.PersistentClient(
            path=settings.chroma_persist_directory,
            settings=ChromaSettings(anonymized_telemetry=False, allow_reset=True),
        )

        self.collection = self.client.get_or_create_collection(
            name=settings.chroma_collection_name,
        )

    def _create_directory(self) -> None:
        """Create directory if it doesn't exist."""
        os.makedirs(settings.chroma_persist_directory, exist_ok=True)

    def add_documents(self, pdf_result: PDFResult) -> None:
        """
        Add documents to the vector store.

        Args:
            pdf_result: PDFResult object containing filename, sentences
        """
        ids = []
        metadatas = []
        for i, sentence in enumerate(pdf_result.sentences):
            ids.append(f"{pdf_result.filename}-{i}")
            metadatas.append({"filename": pdf_result.filename, "chunk_index": i})

        self.collection.add(
            ids=ids, metadatas=metadatas, documents=pdf_result.sentences
        )

    def search(self, query: str, top_k: int = None) -> Dict[str, Any]:
        """
        Search for similar documents in the vector store.

        Args:
            query: Search query text
            top_k: Number of results to return (defaults to settings.retrieval_top_k)

        Returns:
            Dictionary containing documents, metadatas, and distances
        """
        if top_k is None:
            top_k = settings.retrieval_top_k

        results = self.collection.query(n_results=top_k, query_texts=[query])

        return results

    def delete_by_filename(self, filename: str) -> None:
        """
        Delete all documents associated with a specific filename.

        Args:
            filename: Name of the file to delete documents for
        """
        # Get all documents with this filename
        results = self.collection.get(
            where={"filename": filename}, include=["metadatas"]
        )

        if results["ids"]:
            self.collection.delete(ids=results["ids"])

    def get_all_filenames(self) -> List[str]:
        """
        Get list of all unique filenames in the vector store.

        Returns:
            List of unique filenames
        """
        all_docs = self.collection.get(include=["metadatas"])
        filenames = set()

        for metadata in all_docs.get("metadatas", []):
            if "filename" in metadata:
                filenames.add(metadata["filename"])

        return sorted(list(filenames))

    def count_documents(self) -> int:
        """
        Get total count of documents in the vector store.

        Returns:
            Number of documents
        """
        return self.collection.count()

    def reset(self) -> None:
        """Delete all documents from the collection."""
        self.client.delete_collection(name=settings.chroma_collection_name)
        self.collection = self.client.get_or_create_collection(
            name=settings.chroma_collection_name,
        )


# Singleton instance
_vector_store_instance = None


def get_vector_store() -> VectorStore:
    """
    Get or create the singleton VectorStore instance.

    Returns:
        VectorStore instance
    """
    global _vector_store_instance
    if _vector_store_instance is None:
        _vector_store_instance = VectorStore()
    return _vector_store_instance
