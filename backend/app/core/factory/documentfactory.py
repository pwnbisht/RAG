from fastapi import Depends
from app.core.config import get_settings
from app.services.documents.documentservice import DocumentService, FileService
from app.services.documents.embeddings import EmbeddingService
from app.services.documents.chat_service import ChatService
from app.services.documents.llm_service import LLMService
from app.controllers.documents.documents import DocumentController
from app.repositories.documents.documents import DocumentRepository


def get_document_repo() -> DocumentRepository:
    """
    Get the document repository.

    Returns:
        DocumentRepository: The document repository.
    """
    return DocumentRepository()

def get_file_service() -> FileService:
    """
    Get the file service.

    Returns:
        FileService: The file service.
    """
    return FileService(get_settings())

def get_embedding_service() -> EmbeddingService:
    """
    Get the embedding service.

    Returns:
        EmbeddingService: The embedding service instance.
    """
    return EmbeddingService()

def get_llm_service() -> LLMService:
    """
    Get the LLM service.

    Returns:
        LLMService: The LLM service instance.
    """
    return LLMService()


def get_document_service(
    file_service: FileService = Depends(get_file_service),
    document_repo: DocumentRepository = Depends(get_document_repo),
    embedding_service: EmbeddingService = Depends(get_embedding_service)
) -> DocumentService:
    """
    Get the document service.

    Args:
        file_service (FileService): The file service instance.
        document_repo (DocumentRepository): The document repository instance.
        embedding_service (EmbeddingService): The embedding service instance.

    Returns:
        DocumentService: The document service instance.
    """
    return DocumentService(file_service, document_repo, embedding_service)


def get_chat_services(
    document_repo: DocumentRepository = Depends(get_document_repo),
    embedding_service: EmbeddingService = Depends(get_embedding_service),
    llm_service: LLMService = Depends(get_llm_service)
) -> ChatService:
    """
    Get the chat service.

    Args:
        document_repo (DocumentRepository): The document repository instance.
        embedding_service (EmbeddingService): The embedding service instance.
        llm_service (LLMService): The LLM service instance.

    Returns:
        ChatService: The chat service instance.
    """
    return ChatService(document_repo, embedding_service, llm_service)


def get_document_controller(
    document_service: DocumentService = Depends(get_document_service),
    chat_service: ChatService = Depends(get_chat_services)
) -> DocumentController:
    """
    Get the document controller.

    Args:
        document_service (DocumentService): The document service instance.
        chat_service (ChatService): The chat service instance.

    Returns:
        DocumentController: The document controller instance.
    """
    return DocumentController(document_service, chat_service)

    