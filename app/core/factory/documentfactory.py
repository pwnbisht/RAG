from fastapi import Depends
from app.core.config import get_settings
from app.services.documents.documentservice import DocumentService, FileService
from app.services.documents.embeddings import EmbeddingService
from app.services.documents.chat_service import ChatService
from app.services.documents.llm_service import LLMService
from app.controllers.documents.documents import DocumentController
from app.repositories.documents.documents import DocumentRepository


def get_document_repo() -> DocumentRepository:
    return DocumentRepository()

def get_file_service() -> FileService:
    return FileService(get_settings())

def get_embedding_service() -> EmbeddingService:
    return EmbeddingService()

def get_llm_service() -> LLMService:
    return LLMService()


def get_document_service(
    file_service: FileService = Depends(get_file_service),
    document_repo: DocumentRepository = Depends(get_document_repo),
    embedding_service: EmbeddingService = Depends(get_embedding_service)
) -> DocumentService:
    return DocumentService(file_service, document_repo, embedding_service)


def get_chat_services(
    document_repo: DocumentRepository = Depends(get_document_repo),
    embedding_service: EmbeddingService = Depends(get_embedding_service),
    llm_service: LLMService = Depends(get_llm_service)
) -> ChatService:
    return ChatService(document_repo, embedding_service, llm_service)


def get_document_controller(
    document_service: DocumentService = Depends(get_document_service),
    chat_service: ChatService = Depends(get_chat_services)
) -> DocumentController:
    return DocumentController(document_service, chat_service)

    