import os
import uuid
from pathlib import Path

from pypdf import PdfReader

from dtos import PDFResult
from protocols import ChunkerProtocol
from src.config import settings


class PDFProcessor:
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

    def extract_text_from_pdf(self, pdf_path: str) -> str:
        """
        Extract text from a PDF file.

        Args:
            pdf_path: Path to the PDF file

        Returns:
            Extracted text from the PDF

        Raises:
            Exception: If PDF cannot be read
        """
        try:
            reader = PdfReader(pdf_path)
            text = ""

            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"

            return text.strip()
        except Exception as e:
            raise Exception(f"Error reading PDF: {str(e)}")

    def process_pdf(self, pdf_path: str, filename: str) -> PDFResult:
        """
        Process a PDF file: extract text and create chunks.

        Args:
            pdf_path: Path to the PDF file
            filename: Original filename

        Returns:
            PDFResult containing filename and chunks
        """
        text = self.extract_text_from_pdf(pdf_path)

        if not text:
            raise ValueError("No text could be extracted from the PDF")

        chunks = self.chunker.split(text)

        return PDFResult(filename=filename, chunks=chunks)

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
