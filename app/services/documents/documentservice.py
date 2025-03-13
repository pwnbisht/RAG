import os
import re
import uuid
import asyncio
import aiofiles
import aiofiles.os as aios
import logging
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import UploadFile, BackgroundTasks

from langchain_community.document_loaders import PyPDFLoader
from langchain_community.document_loaders import Docx2txtLoader
from langchain_community.document_loaders import TextLoader
from langchain_community.document_loaders import CSVLoader
from langchain_community.document_loaders import UnstructuredExcelLoader

from app.db.base import get_db_session
from app.db.models.documents import Document, StatusEnum
from app.core.config import Settings
from app.core.exceptions import BadRequestException
from app.repositories.documents.documents import DocumentRepository
from .embeddings import EmbeddingService


logger = logging.getLogger(__name__)

TEMP_UPLOAD_DIR = "temp_uploads"


# async def save_upload_file_async(
#     upload_file: UploadFile,
#     temp_dir: str
# ) -> str:
#     """
#     Saves an uploaded file to the specified temp directory
#     using a unique filename.
#     """
#     file_ext = upload_file.filename.split('.')[-1]
#     unique_filename = f"{uuid.uuid4()}.{file_ext}"
#     file_path = os.path.join(temp_dir, unique_filename)
#     contents = await upload_file.read()
#     with open(file_path, "wb") as f:
#         f.write(contents)
#     return file_path

async def save_upload_file_async(
    upload_file: UploadFile,
    temp_dir: str
) -> str:
    """
    Saves an uploaded file to the specified temp directory
    using a unique filename with async I/O.
    Args:
        upload_file (UploadFile): The uploaded file to be saved.
        temp_dir (str): The directory where the file will be saved.

    Returns:
        str: The path of the saved file.
    """
    await aios.makedirs(temp_dir, exist_ok=True)
    file_ext = upload_file.filename.split('.')[-1]
    unique_filename = f"{uuid.uuid4()}.{file_ext}"
    file_path = os.path.join(temp_dir, unique_filename)
    
    async with aiofiles.open(file_path, "wb") as f:
        content = await upload_file.read()
        await f.write(content)
    
    return file_path


class FileProcessor:
    """
    This class is responsible for processing files and loading 
    their content using appropriate loaders based on the file extension.
    """

    @staticmethod
    def get_loader(file_path: str):
        """
        Get the appropriate loader for the given file based on its extension.
        """
        ext = os.path.splitext(file_path)[1].lower()
        if ext == '.pdf':
            return PyPDFLoader(file_path)
        elif ext == '.docx':
            return Docx2txtLoader(file_path)
        elif ext == '.txt':
            return TextLoader(file_path)
        elif ext == '.csv':
            return CSVLoader(file_path)
        elif ext in ('.xls', '.xlsx'):
            return UnstructuredExcelLoader(file_path)
        else:
            raise ValueError(f"Unsupported file type: {ext}")

    @staticmethod
    def process(file_path: str) -> str:
        loader = FileProcessor.get_loader(file_path)
        docs = loader.load()
        return "\n".join(doc.page_content for doc in docs)
    


class ContentCleaner:
    """
    This class contains methods for cleaning text content.
    """

    @staticmethod
    def clean(content: str) -> str:
        content = re.sub(r'\s+', ' ', content)
        return ''.join(
            c for c in content if c.isprintable()
        ).strip()


class FileService:
    def __init__(self, config: Settings):
        self.allowed_extensions = config.ALLOWED_FILE_EXTENSIONS
        self.max_size = config.MAX_FILE_SIZE

    async def validate_file(self, file: UploadFile):
        self._validate_extension(file.filename)
        await self._validate_size(file)

    def _validate_extension(self, filename: str):
        if not filename.lower().endswith(tuple(self.allowed_extensions)):
            raise BadRequestException(message="Unsupported file format")

    async def _validate_size(self, file: UploadFile):
        file.file.seek(0, os.SEEK_END)
        if file.file.tell() > self.max_size:
            raise BadRequestException(message="File too large")
        file.file.seek(0)

    def get_user_temp_dir(self, user_id: int) -> str:
        path = os.path.join(TEMP_UPLOAD_DIR, str(user_id))
        os.makedirs(path, exist_ok=True)
        return path

    async def save_temp_file(self, file: UploadFile, dest_dir: str) -> str:
        return await save_upload_file_async(file, dest_dir)

    async def cleanup_temp_file(self, path: str):
        if await aios.path.exists(path):
            await aios.remove(path)


class DocumentService:
    def __init__(
        self,
        file_service: FileService,
        document_repo: DocumentRepository,
        embedding_service: EmbeddingService
    ):
        self.file_service = file_service
        self.document_repo = document_repo
        self.embedding_service = embedding_service
        
    async def get_documents(
        self,
        user_id: int,
        session: AsyncSession
    ):
        return await self.document_repo.get_documents_by_user(
            user_id, session
        )
        
    async def get_user_document(
        self,
        user_id: int,
        document_id: int,
        session: AsyncSession
    ) -> Document:
        """
        Get a single document by ID that belongs to the specified user
        """
        document = await self.document_repo.get_document_by_user_and_id(
            user_id=user_id,
            document_id=document_id,
            session=session
        )
        
        if document.status != StatusEnum.SUCCESS:
            raise BadRequestException(
                message="Document processing not completed yet"
            )
            
        return document

    async def handle_upload(
        self, user_id: int,
        files: list[UploadFile],
        background_tasks: BackgroundTasks
    ):
        for file in files:
            await self.file_service.validate_file(file)
        
        user_temp_dir = self.file_service.get_user_temp_dir(user_id)
        
        for file in files:
            temp_path = await self.file_service.save_temp_file(
                file, user_temp_dir
            )
            background_tasks.add_task(
                self.process_document,
                temp_path=temp_path,
                user_id=user_id,
                original_filename=file.filename
            )

    async def process_document(
        self, temp_path: str,
        user_id: int, original_filename: str
    ):
        try:
            loop = asyncio.get_event_loop()
            
            # Load the file content using langchain loaders.
            # content = FileProcessor.process(temp_path)
            content = await loop.run_in_executor(
                None,
                FileProcessor.process,
                temp_path
            )
            
            # Clean the content.
            # cleaned_content = ContentCleaner.clean(content)
            cleaned_content = await loop.run_in_executor(
                None,
                ContentCleaner.clean,
                content
            )
            
            # Generate embedding.
            embedding = await self.embedding_service.generate_embedding(cleaned_content)
            # logger.info(f"Generated embedding for {original_filename}")
            # logger.info(f"Dimensions: {len(embedding)}")
            # embedding = await loop.run_in_executor(
            #     None,
            #     embedding_service.generate_embedding,
            #     cleaned_content
            # )
            
            document_data = {
                "file_name": original_filename,
                "content": cleaned_content,
                "embedding": embedding,
                "user_id": user_id
            }
            
            try:
                async with get_db_session() as session:
                    await self.document_repo.create(document_data, session)
            finally:
                await session.close()
        except Exception as e:
            logger.error(
                f"Failed to process {original_filename} (user {user_id}): {str(e)}",
                exc_info=True
            )
            if session:
                await session.rollback()
        finally:
            await self.file_service.cleanup_temp_file(temp_path)
            
