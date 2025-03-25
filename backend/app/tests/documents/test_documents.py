import pytest
from datetime import datetime
from fastapi import UploadFile, BackgroundTasks
from fastapi.testclient import TestClient
from fastapi.exceptions import HTTPException

from app.api.v1.users.documents.documents import get_documents
from app.main import app
from app.schemas.documents.document_schemas import DocumentOut
from app.api.v1.users.documents.documents import upload_document
from app.controllers.documents.documents import DocumentController
from app.services.documents.documentservice import DocumentService


client = TestClient(app)

@pytest.mark.asyncio
async def test_get_documents_unauthorized(mocker):
    """
    Test that get_documents returns a 403 Unauthorized response when the request is missing the access token cookie.
    """
    mock_db = mocker.AsyncMock()
    mocker.patch("app.db.base.get_db", return_value=mock_db)
    response = client.get("/api/v1/docs/")

    assert response.status_code == 403
    assert response.json() == {"detail": "Missing access token cookie"}


@pytest.mark.asyncio
async def test_get_documents_returns_list_for_valid_user(mocker):
    """
    Test that get_documents returns a list of documents for a valid user.
    """
    mock_user = {"sub": "123"}
    mock_session = mocker.AsyncMock()

    mock_controller = mocker.AsyncMock()
    mock_documents = [
        DocumentOut(
            id=1,
            file_name="test.pdf",
            user_id=123,
            status="processed",
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
    ]
    mock_controller.get_documents.return_value = mock_documents

    result = await get_documents(
        user=mock_user,
        controller=mock_controller,
        session=mock_session
    )

    assert result == mock_documents
    mock_controller.get_documents.assert_called_once_with(123, mock_session)


@pytest.mark.asyncio
async def test_upload_single_file_success(mocker):
    """
    Test that a single file is successfully uploaded with a valid user.
    """
    mock_user = {"sub": "1"}
    mock_file = mocker.MagicMock(spec=UploadFile)
    mock_background_tasks = mocker.MagicMock(spec=BackgroundTasks)
    mock_controller = mocker.MagicMock(spec=DocumentController)
    mock_controller.upload_document.return_value = {"message": "Files are being processed..."}

    result = await upload_document(
        user=mock_user,
        files=[mock_file],
        background_tasks=mock_background_tasks,
        controller=mock_controller
    )

    mock_controller.upload_document.assert_called_once_with(
        user_id=1,
        files=[mock_file],
        background_tasks=mock_background_tasks
    )

    assert result == {"message": "Files are being processed..."}

@pytest.mark.asyncio
async def test_upload_multiple_files_success(mocker):
    """
    Test that a list of files is successfully uploaded with a valid user.
    """
    mock_user = {"sub": "1"}
    mock_files = [mocker.MagicMock(spec=UploadFile) for _ in range(3)]
    mock_background_tasks = mocker.MagicMock(spec=BackgroundTasks)
    mock_controller = mocker.MagicMock(spec=DocumentController)
    mock_controller.upload_document.return_value = {"message": "Files are being processed..."}

    result = await upload_document(
        user=mock_user,
        files=mock_files,
        background_tasks=mock_background_tasks,
        controller=mock_controller
    )

    mock_controller.upload_document.assert_called_once_with(
        user_id=1,
        files=mock_files,
        background_tasks=mock_background_tasks
    )
    assert result == {"message": "Files are being processed..."}


@pytest.mark.asyncio
async def test_handle_upload_invalid_file(mocker):
    """
    Test that handle_upload raises an HTTPException for invalid file types.
    """
    mock_file_service = mocker.MagicMock()
    mock_file_service.validate_file.side_effect = HTTPException(400, "Invalid file type")
    
    service = DocumentService(mock_file_service, mocker.MagicMock(), mocker.MagicMock())
    
    with pytest.raises(HTTPException) as exc:
        await service.handle_upload(123, [UploadFile(file="bad.exe")], BackgroundTasks())
    
    assert "Invalid file type" in str(exc.value.detail)
    

@pytest.mark.asyncio
async def test_controller_chat_with_document_success(mocker):
    """
    Test that the chat_with_document method successfully returns a response
    when the document status is SUCCESS and chat processing is successful.
    """
    document = mocker.MagicMock()
    document.status = "SUCCESS"
    
    doc_service = mocker.MagicMock()
    doc_service.get_user_document = mocker.AsyncMock(return_value=document)
    
    chat_response = {"reply": "Hello"}
    
    chat_service = mocker.MagicMock()
    chat_service.process_chat = mocker.AsyncMock(return_value=chat_response)
    
    controller = DocumentController(document_service=doc_service, chat_service=chat_service)
    
    user_id = 1
    document_id = 101
    message = "Hiiiiiiii"
    test_session = mocker.MagicMock()
    
    response = await controller.chat_with_document(
        user_id=user_id,
        document_id=document_id,
        message=message,
        session=test_session
    )
    
    doc_service.get_user_document.assert_awaited_once_with(user_id, document_id, test_session)
    
    chat_service.process_chat.assert_awaited_once_with(
        document_id=document_id,
        message=message,
        session=test_session
    )
    
    assert response == chat_response
