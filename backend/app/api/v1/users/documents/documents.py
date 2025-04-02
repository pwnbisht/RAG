from typing import List

from fastapi import APIRouter
from fastapi import BackgroundTasks
from fastapi import Depends
from fastapi import File
from fastapi import UploadFile
from sqlalchemy.ext.asyncio import AsyncSession
from app.controllers.documents.document_controller import DocumentController
from app.db.base import get_db
from app.core.factory.documentfactory import get_document_controller
from app.services.auth.auth_services import jwt_bearer
from app.schemas.documents.document_schemas import DocumentOut, ChatResponse, ChatRequest


router = APIRouter()


@router.get(
    "/",
    response_model=List[DocumentOut],
)
async def get_documents(
    user: dict = Depends(jwt_bearer),
    controller: DocumentController = Depends(get_document_controller),
    session: AsyncSession = Depends(get_db)
):
    """
    Get a list of all documents for the current user

    :param user: The current user
    :param controller: The document controller
    :param session: The database session
    :return: A list of documents for the current user
    """
    user_id = int(user.get("sub"))
    return await controller.get_documents(user_id, session)


@router.post(
    "/upload",
    dependencies=[Depends(jwt_bearer)],
    response_model=dict,
)
async def upload_document(
    user: dict = Depends(jwt_bearer),
    files: List[UploadFile] = File(...),
    background_tasks: BackgroundTasks = BackgroundTasks(),
    controller: DocumentController = Depends(get_document_controller)
):
    """
    Upload a list of files

    :param user: The current user
    :param files: The list of files to upload
    :param background_tasks: The background tasks
    :param controller: The document controller
    :return: A message indicating the upload status
    """
    return await controller.upload_document(
        user_id=int(user.get("sub")),
        files=files,
        background_tasks=background_tasks
    )


@router.post(
    "/{doc_id}/chat",
    dependencies=[Depends(jwt_bearer)],
    response_model=ChatResponse,
)
async def chat(
    doc_id: int,
    chat_request: ChatRequest,
    user: dict = Depends(jwt_bearer),
    session: AsyncSession = Depends(get_db),
    controller: DocumentController = Depends(get_document_controller)
):
    """
    Chat with a document

    :param doc_id: The ID of the document
    :param chat_request: The chat request
    :param user: The current user
    :param session: The database session
    :param controller: The document controller
    :return: The chat response
    """
    return await controller.chat_with_document(
        user_id=int(user.get("sub")),
        document_id=doc_id,
        message=chat_request.query,
        session=session
    )
