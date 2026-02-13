import os
import uuid
import re
from pathlib import Path

from pypdf import PdfReader

from dtos import PDFResult
from src.config import settings


class PDFProcessor:
    def __init__(self):
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

    def _split_into_sentences(self, text: str) -> list[str]:
        """
        Split text into sentences.

        Args:
            text: Text to split

        Returns:
            List of sentences
        """
        sentence_pattern = r"(?<=[.!?])\s+(?=[A-Z])"
        sentences = re.split(sentence_pattern, text)

        sentences = [s.strip() for s in sentences if s.strip()]

        return sentences

    def process_pdf(self, pdf_path: str, filename: str) -> PDFResult:
        """
        Process a PDF file: extract text and create chunks.

        Args:
            pdf_path: Path to the PDF file
            filename: Original filename

        Returns:
            PDFResult containing chunks, metadatas, and ids
        """
        text = self.extract_text_from_pdf(pdf_path)

        if not text:
            raise ValueError("No text could be extracted from the PDF")

        sentences = self._split_into_sentences(text)

        return PDFResult(filename=filename, sentences=sentences)

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
