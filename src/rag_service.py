from typing import Any

import logfire
from pydantic_ai import Agent
from pydantic_ai.models.mistral import MistralModel
from pydantic_ai.providers.mistral import MistralProvider

from protocols import VectorStoreProtocol
from schemas import RAGResponse
from src.config import settings


class RAGService:
    """Handles RAG operations using Pydantic AI and Mistral."""

    def __init__(self, vector_store: VectorStoreProtocol):
        self.vector_store = vector_store

        self.provider = MistralProvider(api_key=settings.mistral_api_key)
        self.model = MistralModel(
            model_name=settings.mistral_model, provider=self.provider
        )

        logfire.configure(token=settings.logfire_token)
        logfire.instrument_pydantic_ai()

        self.agent = Agent(
            model=self.model,
            output_type=RAGResponse,
            system_prompt=self._get_system_prompt(),
            max_concurrency=settings.concurrency,
        )

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
                answer="I don't have any documents to answer your question. Please upload some PDF documents first.",
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
