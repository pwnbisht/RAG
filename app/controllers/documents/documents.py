from fastapi import UploadFile, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.documents.documentservice import DocumentService
from app.services.documents.chat_service import ChatService
from app.schemas.documents.document_schemas import DocumentOut


class DocumentController:
    """
    Controller for document related operations.

    Handles document upload, retrieval and chat functionality.
    """
    def __init__(
        self, document_service: DocumentService,
        chat_service: ChatService
    ):
        """
        Initialize the controller.

        Args:
            document_service (DocumentService): The document service.
            chat_service (ChatService): The chat service.
        """
        self.document_service = document_service
        self.chat_service = chat_service

    async def upload_document(
        self,
        user_id: int,
        files: list[UploadFile],
        background_tasks: BackgroundTasks
    ) -> dict:
        """
        Upload a list of documents.

        Args:
            user_id (int): The user id.
            files (list[UploadFile]): The list of files to upload.
            background_tasks (BackgroundTasks): The background tasks.

        Returns:
            dict: A message indicating the upload status.
        """
        await self.document_service.handle_upload(
            user_id=user_id,
            files=files,
            background_tasks=background_tasks
        )
        return {"message": "Files are being processed..."}
    
    async def get_documents(
        self, user_id: int,
        session: AsyncSession
    ) -> list[DocumentOut]:
        """
        Get a list of all documents for the current user.

        Args:
            user_id (int): The user id.
            session (AsyncSession): The database session.

        Returns:
            list[DocumentOut]: A list of documents for the current user.
        """
        return await self.document_service.get_documents(user_id, session)
    
    async def chat_with_document(
        self,
        user_id: int,
        document_id: int,
        message: str,
        session: AsyncSession
    ) -> dict:
        """
        Chat with a document.

        Args:
            user_id (int): The user id.
            document_id (int): The document id.
            message (str): The message.
            session (AsyncSession): The database session.

        Returns:
            dict: The chat response.
        """
        await self.document_service.get_user_document(
            user_id, 
            document_id,
            session
        )        
        return await self.chat_service.process_chat(
            document_id=document_id,
            message=message,
            session=session
        )
