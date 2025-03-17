import logging
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.documents.documents import DocumentRepository
from .embeddings import EmbeddingService
from .llm_service import LLMService


logger = logging.getLogger(__name__)


class ChatService:
    """
    Service for handling document chat functionality.

    Args:
        document_repo (DocumentRepository): The document repository instance.
        embedding_service (EmbeddingService): The embedding service instance.
        llm_service (LLMService): The LLM service instance.
    """

    def __init__(
        self,
        document_repo: DocumentRepository,
        embedding_service: EmbeddingService,
        llm_service: LLMService
    ):
        self.document_repo = document_repo
        self.embedding_service = embedding_service
        self.llm_service = llm_service

    async def process_chat(
        self,
        document_id: int,
        message: str,
        session: AsyncSession
    ) -> dict:
        """
        Process a chat message.

        Finds similar document sections to the given message
        and uses the LLM model to generate a response.

        Args:
            document_id (int): The document id.
            message (str): The message.
            session (AsyncSession): The database session.

        Returns:
            dict: A response dict with the response and sources.
        """
        query_embedding = await self.embedding_service.generate_embedding(message)
        
        chunks = await self.document_repo.find_similar_content(
            document_id=document_id,
            query_embedding=query_embedding,
            threshold=0.7,
            limit=5,
            session=session
        )
        if not chunks:
            return {
                "response": "I couldn’t find any relevant information in the document.",
                "sources": []
            }
        
        context = "\n\n".join(chunks)
        sources = [chunk[:50] + "..." for chunk in chunks]
        
        try:
            response = await self.llm_service.generate_response(query=message, context=context)
        except Exception as e:
            logger.error(f"Error processing chat: {e}")
            return {
                "response": "Sorry, I encountered an error processing your request.",
                "sources": []
            }
        return {
            "response": response,
            "sources": sources
        }
