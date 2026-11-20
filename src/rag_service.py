from typing import Any

import logfire
from google import genai
from google.genai import types
from pydantic_ai import Agent
from pydantic_ai.models.google import GoogleModel
from pydantic_ai.providers.google import GoogleProvider

from protocols import VectorStoreProtocol
from schemas import RAGResponse
from src.config import settings


class RAGService:
    """Handles RAG operations using Pydantic AI and Google Gemini."""

    def __init__(self, vector_store: VectorStoreProtocol):
        self.vector_store = vector_store

        self.provider = GoogleProvider(client=self._create_genai_client())
        self.model = GoogleModel(
            model_name=settings.gemini_model, provider=self.provider
        )

        logfire.configure(token=settings.logfire_token)
        logfire.instrument_pydantic_ai()

        self.agent = Agent(
            model=self.model,
            output_type=RAGResponse,
            system_prompt=self._get_system_prompt(),
            max_concurrency=settings.concurrency,
        )

    def _create_genai_client(self) -> genai.Client:
        """
        Create a Gemini client with a per-request timeout and automatic retries
        (exponential backoff with jitter) on transient errors: 408, 429 and 5xx.

        Returns:
            Configured google-genai Client
        """
        http_options = types.HttpOptions(
            timeout=int(settings.gemini_timeout_seconds * 1000),  # milliseconds
            retry_options=types.HttpRetryOptions(
                attempts=settings.gemini_max_attempts,
                initial_delay=settings.gemini_retry_initial_delay,
                max_delay=settings.gemini_retry_max_delay,
            ),
        )
        return genai.Client(api_key=settings.gemini_api_key, http_options=http_options)

    def _get_system_prompt(self) -> str:
        """
        Get the system prompt for the RAG agent.

        Returns:
            System prompt string
        """
        return """You are a helpful AI assistant that answers questions based on the provided context.

        Your task is to:
        1. Carefully read and understand the context provided from the documents
        2. Answer the user's question based ONLY on the information in the context
        3. If the context doesn't contain enough information to answer the question, clearly state that
        4. Be concise but comprehensive in your answers
        5. Cite specific parts of the context when relevant
        6. If you're uncertain, express that uncertainty
        
        Remember: Only use information from the provided context. Do not use external knowledge."""

    def _format_context(
        self, documents: list[str], metadatas: list[dict[str, Any]]
    ) -> str:
        """
        Format retrieved documents into context string.

        Args:
            documents: List of retrieved document texts
            metadatas: List of metadata for each document

        Returns:
            Formatted context string
        """
        context_parts = []

        for i, (doc, metadata) in enumerate(zip(documents, metadatas), 1):
            filename = metadata.get("filename", "Unknown")
            chunk_index = metadata.get("chunk_index", "?")

            context_parts.append(
                f"[Document {i} - Source: {filename}, Chunk: {chunk_index}]\n{doc}\n"
            )

        return "\n".join(context_parts)

    async def query(self, question: str, top_k: int = None) -> RAGResponse:
        """
        Query the RAG system with a question.

        Args:
            question: User's question
            top_k: Number of documents to retrieve (defaults to settings.retrieval_top_k)

        Returns:
            RAGResponse containing answer and sources
        """
        # Retrieve relevant documents
        search_results = self.vector_store.search(question, top_k=top_k)

        if not search_results["documents"] or not search_results["documents"][0]:
            return RAGResponse(
                answer="I don't have any documents to answer your question. Please upload some PDF, TXT documents first.",
                sources=[],
                confidence="low",
            )

        documents = search_results["documents"][0]
        metadatas = search_results["metadatas"][0]

        context = self._format_context(documents, metadatas)

        prompt = f"""Context from documents:{context}
        
        Question: {question}
        
        Please provide a detailed answer based on the context above."""

        result = await self.agent.run(prompt)

        return result.output
