import os
import uuid
from abc import ABC, abstractmethod
from pathlib import Path

from pypdf import PdfReader

from dtos import FileResult
from protocols import ChunkerProtocol
from src.config import settings


class BaseFileProcessor(ABC):
    """
    Shared logic for all file processors: saving, deleting and chunking.
    Subclasses only need to implement text extraction for their file type.
    """

    def __init__(self, chunker: ChunkerProtocol):
        self.chunker = chunker
        self._create_directory(settings.upload_dir)

    def _create_directory(self, directory_path: str) -> None:
        """
        Create a directory if it doesn't exist.

        Args:
            directory_path: Path to the directory
        """
        if not os.path.exists(directory_path):
            os.makedirs(directory_path)

    @abstractmethod
    def extract_text(self, file_path: str) -> str:
        """
        Extract text from a file.

        Args:
            file_path: Path to the file

        Returns:
            Extracted text
        """

    def process_file(self, file_path: str, filename: str) -> FileResult:
        """
        Process a file: extract text and create chunks.

        Args:
            file_path: Path to the file
            filename: Original filename

        Returns:
            FileResult containing filename and chunks
        """
        text = self.extract_text(file_path)

        if not text:
            raise ValueError(f"No text could be extracted from '{filename}'")

        chunks = self.chunker.split(text)

        return FileResult(filename=filename, chunks=chunks)

    def save_uploaded_file(self, file_content: bytes, filename: str) -> str:
        """
        Save uploaded file to disk.

        Args:
            file_content: File content as bytes
            filename: Original filename

        Returns:
            Path to saved file
        """
        file_path = Path(settings.upload_dir) / filename

        if file_path.exists():
            stem = file_path.stem
            suffix = file_path.suffix
            timestamp = uuid.uuid4().hex[:8]
            filename = f"{stem}_{timestamp}{suffix}"
            file_path = Path(settings.upload_dir) / filename

        with open(file_path, "wb") as f:
            f.write(file_content)

        return str(file_path)

    def delete_file(self, file_path: str) -> None:
        """
        Delete a file from disk.

        Args:
            file_path: Path to file to delete
        """
        if os.path.exists(file_path):
            os.remove(file_path)


class PDFFileProcessor(BaseFileProcessor):
    def extract_text(self, file_path: str) -> str:
        """
        Extract text from a PDF file.

        Raises:
            Exception: If PDF cannot be read
        """
        try:
            reader = PdfReader(file_path)
            text = ""

            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"

            return text.strip()
        except Exception as e:
            raise Exception(f"Error reading PDF: {str(e)}")


class TXTFileProcessor(BaseFileProcessor):
    def extract_text(self, file_path: str) -> str:
        """
        Extract text from a plain text file (UTF-8).

        Raises:
            Exception: If the file cannot be read or decoded
        """
        try:
            return Path(file_path).read_text(encoding="utf-8").strip()
        except Exception as e:
            raise Exception(f"Error reading TXT file: {str(e)}")
