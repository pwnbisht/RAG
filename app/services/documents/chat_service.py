import logging
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.documents.documents import DocumentRepository
from .embeddings import EmbeddingService
from .llm_service import LLMService


logger = logging.getLogger(__name__)

class ChatService:
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
        query_embedding = await self.embedding_service.generate_embedding(message)
        
        # Find similar document sections
        context = await self.document_repo.find_similar_content(
            document_id=document_id,
            query_embedding=query_embedding,
            threshold=0.7,
            limit=3,
            session=session
        )
        
        logger.info(f"Context: {context}")
        
        if not context:
            return {
                "response": "I couldn’t find any relevant information in the document.",
                "sources": []
            }
        
        context = "\n\n".join(context)
        
        try:
            response = await self.llm_service.generate_response(query=message, context=context)
        except Exception as e:
            return {
                "response": "Sorry, I encountered an error processing your request.",
                "sources": []
            }
        
        # Return response and sources
        return {
            "response": response,
            "sources": context
        }