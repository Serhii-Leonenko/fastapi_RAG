import re

import numpy as np
from langchain_text_splitters import RecursiveCharacterTextSplitter

from protocols import ChunkerProtocol
from src.config import settings


class SentenceChunker:
    """Splits text into sentences using punctuation boundaries."""

    _SENTENCE_PATTERN = re.compile(r"(?<=[.!?])\s+(?=[A-Z])")

    def split(self, text: str) -> list[str]:
        """
        Split text into sentences.

        Args:
            text: Text to split

        Returns:
            List of non-empty sentences
        """
        sentences = self._SENTENCE_PATTERN.split(text)
        return [s.strip() for s in sentences if s.strip()]


class RecursiveChunker:
    """Splits text into overlapping fixed-size chunks (LangChain recursive splitter)."""

    def __init__(self, chunk_size: int, chunk_overlap: int):
        self._splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
        )

    def split(self, text: str) -> list[str]:
        """
        Split text into overlapping chunks.

        Args:
            text: Text to split

        Returns:
            List of chunks
        """
        return self._splitter.split_text(text)


class SemanticChunker:
    """
    Groups consecutive sentences into chunks by meaning.

    Each sentence is embedded together with its neighbours. A new chunk starts
    wherever the cosine distance between neighbouring sentences is above the
    given percentile of all distances in the document.
    """

    def __init__(
        self,
        model_name: str,
        breakpoint_percentile: float = 90.0,
        buffer_size: int = 0,
        sentence_chunker: SentenceChunker | None = None,
    ):
        from sentence_transformers import SentenceTransformer

        self._model = SentenceTransformer(model_name)
        self._breakpoint_percentile = breakpoint_percentile
        self._buffer_size = buffer_size
        self._sentence_chunker = sentence_chunker or SentenceChunker()

    def _with_context(self, sentences: list[str]) -> list[str]:
        """Join each sentence with buffer_size neighbours on each side."""
        b = self._buffer_size
        return [
            " ".join(sentences[max(0, i - b) : i + b + 1])
            for i in range(len(sentences))
        ]

    def split(self, text: str) -> list[str]:
        """
        Split text into semantically coherent chunks.

        Args:
            text: Text to split

        Returns:
            List of chunks
        """
        sentences = self._sentence_chunker.split(text)
        if len(sentences) < 2:
            return sentences

        embeddings = self._model.encode(
            self._with_context(sentences), normalize_embeddings=True
        )
        # Cosine distance between each sentence and the next one
        distances = 1.0 - np.sum(embeddings[:-1] * embeddings[1:], axis=1)
        threshold = np.percentile(distances, self._breakpoint_percentile)

        chunks: list[str] = []
        current = [sentences[0]]
        for sentence, distance in zip(sentences[1:], distances):
            if distance > threshold:
                chunks.append(" ".join(current))
                current = []
            current.append(sentence)
        chunks.append(" ".join(current))

        return chunks


def create_chunker() -> ChunkerProtocol:
    """Build the chunker selected by settings.chunking_strategy."""
    if settings.chunking_strategy == "recursive":
        return RecursiveChunker(
            chunk_size=settings.chunk_size,
            chunk_overlap=settings.chunk_overlap,
        )
    if settings.chunking_strategy == "semantic":
        return SemanticChunker(
            model_name=settings.semantic_embedding_model,
            breakpoint_percentile=settings.semantic_breakpoint_percentile,
            buffer_size=settings.semantic_buffer_size,
        )
    return SentenceChunker()
