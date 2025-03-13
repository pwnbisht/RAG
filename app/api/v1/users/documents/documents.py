from typing import List

from fastapi import APIRouter
from fastapi import BackgroundTasks
from fastapi import Depends
from fastapi import File
from fastapi import UploadFile
from sqlalchemy.ext.asyncio import AsyncSession
from app.controllers.documents.documents import DocumentController
from app.db.base import get_db
from app.core.factory.documentfactory import get_document_controller
from app.services.auth.auth import jwt_bearer
from app.schemas.documents.document_schemas import DocumentOut, ChatResponse, ChatRequest



router = APIRouter()


@router.get("/", response_model=List[DocumentOut])
async def get_documents(
    user: dict = Depends(jwt_bearer),
    controller: DocumentController = Depends(get_document_controller),
    session: AsyncSession = Depends(get_db)
):
    user_id = int(user.get("sub"))
    return await controller.get_documents(user_id, session)


@router.post(
    "/upload",
    dependencies=[Depends(jwt_bearer)],
    response_model=dict
)
async def upload_document(
    user: dict = Depends(jwt_bearer),
    files: List[UploadFile] = File(...),
    background_tasks: BackgroundTasks = BackgroundTasks(),
    controller: DocumentController = Depends(get_document_controller)
):
    return await controller.upload_document(
        user_id=int(user.get("sub")),
        files=files,
        background_tasks=background_tasks
    )


@router.post(
    "/{doc_id}/chat",
    dependencies=[Depends(jwt_bearer)],
    response_model=ChatResponse
)
async def chat(
    doc_id: int,
    chat_request: ChatRequest,
    user: dict = Depends(jwt_bearer),
    session: AsyncSession = Depends(get_db),
    controller: DocumentController = Depends(get_document_controller)
):
    return await controller.chat_with_document(
        user_id=int(user.get("sub")),
        document_id=doc_id,
        message=chat_request.query,
        session=session
    )