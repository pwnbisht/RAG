from fastapi import UploadFile, BackgroundTasks, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.documents.documentservice import DocumentService
from app.services.documents.chat_service import ChatService

class DocumentController:
    def __init__(
        self, document_service: DocumentService,
        chat_service: ChatService
    ):
        self.document_service = document_service
        self.chat_service = chat_service

    async def upload_document(
        self,
        user_id: int,
        files: list[UploadFile],
        background_tasks: BackgroundTasks
    ):
        await self.document_service.handle_upload(
            user_id=user_id,
            files=files,
            background_tasks=background_tasks
        )
        return {"message": "Files are being processed..."}
    
    async def get_documents(self, user_id: int, session):
        return await self.document_service.get_documents(user_id, session)
    
    async def chat_with_document(
        self,
        user_id: int,
        document_id: int,
        message: str,
        session: AsyncSession,
    ) -> dict:
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
