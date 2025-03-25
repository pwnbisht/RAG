import os
import re
import uuid
import asyncio
import aiofiles
import aiofiles.os as aios
from typing import List
import logging

import concurrent.futures

from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import UploadFile, BackgroundTasks

from langchain_community.document_loaders import PyPDFLoader
from langchain_community.document_loaders import Docx2txtLoader
from langchain_community.document_loaders import TextLoader
from langchain_community.document_loaders import CSVLoader
from langchain_community.document_loaders import UnstructuredExcelLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter

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
        content = "\n".join(doc.page_content for doc in docs)
    
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len,
        )
        return text_splitter.split_text(content)


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
    """
    This class provides methods for validating and handling file uploads.
    
    Attributes:
        allowed_extensions (Set[str]): The allowed file extensions.
        max_size (int): The maximum size of the file in bytes.
    """

    def __init__(self, config: Settings):
        self.allowed_extensions = config.ALLOWED_FILE_EXTENSIONS
        self.max_size = config.MAX_FILE_SIZE

    async def validate_file(self, file: UploadFile):
        """
        Validate the uploaded file.
        
        This method checks if the file has an allowed extension and is not too large.
        """
        self._validate_extension(file.filename)
        await self._validate_size(file)

    def _validate_extension(self, filename: str):
        """
        Check if the file has an allowed extension.
        
        Args:
            filename (str): The file name.
        """
        if not filename.lower().endswith(tuple(self.allowed_extensions)):
            raise BadRequestException(message="Unsupported file format")

    async def _validate_size(self, file: UploadFile):
        """
        Check if the file is not too large.
        
        Args:
            file (UploadFile): The uploaded file.
        """
        file.file.seek(0, os.SEEK_END)
        if file.file.tell() > self.max_size:
            raise BadRequestException(message="File too large")
        file.file.seek(0)

    def get_user_temp_dir(self, user_id: int) -> str:
        """
        Get the temporary directory for the given user.
        
        Args:
            user_id (int): The user id.
        
        Returns:
            str: The path of the temporary directory.
        """
        path = os.path.join(TEMP_UPLOAD_DIR, str(user_id))
        os.makedirs(path, exist_ok=True)
        return path

    async def save_temp_file(self, file: UploadFile, dest_dir: str) -> str:
        """
        Save the uploaded file to the temporary directory.
        
        Args:
            file (UploadFile): The uploaded file.
            dest_dir (str): The path of the temporary directory.
        
        Returns:
            str: The path of the saved file.
        """
        return await save_upload_file_async(file, dest_dir)

    async def cleanup_temp_file(self, path: str):
        """
        Delete the temporary file.
        
        Args:
            path (str): The path of the temporary file.
        """
        if await aios.path.exists(path):
            await aios.remove(path)


class DocumentService:
    """
    Service for handling document-related operations.

    This service provides methods to manage and process
    documents,
    including uploading, retrieving, and processing document
    contents.
    It utilizes various services such as file validation,
    embedding generation, and document repository interactions.
    """
    
    def __init__(
        self,
        file_service: FileService,
        document_repo: DocumentRepository,
        embedding_service: EmbeddingService
    ):
        """
        Initialize the DocumentService.

        Args:
            file_service (FileService): The file service instance for
            handling file operations.
            document_repo (DocumentRepository): The document repository
            instance for database interactions.
            embedding_service (EmbeddingService): The embedding service
            instance for generating embeddings.
        """
        self.file_service = file_service
        self.document_repo = document_repo
        self.embedding_service = embedding_service
        
    async def get_documents(
        self,
        user_id: int,
        session: AsyncSession
    ):
        """
        Retrieve a list of documents for a specific user.

        Args:
            user_id (int): The ID of the user.
            session (AsyncSession): The database session.

        Returns:
            list[Document]: A list of documents belonging to the user.
        """
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
        Get a single document by ID that belongs to the specified user.

        Args:
            user_id (int): The ID of the user.
            document_id (int): The ID of the document.
            session (AsyncSession): The database session.

        Returns:
            Document: The document object.

        Raises:
            BadRequestException: If the document processing is not completed yet.
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
        """
        Handle the upload of a list of files.

        This method validates and saves the uploaded files to a temporary directory
        and schedules their processing.

        Args:
            user_id (int): The ID of the user uploading the files.
            files (list[UploadFile]): The list of files to be uploaded.
            background_tasks (BackgroundTasks): The background tasks
            manager for scheduling async tasks.
        """
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
        """
        Process the uploaded document file.

        This method processes the content of the document, generates embeddings,
        and stores the processed chunks in the database.

        Args:
            temp_path (str): The temporary path of the saved file.
            user_id (int): The ID of the user who uploaded the file.
            original_filename (str): The original name of the uploaded file.
        """
        try:
            loop = asyncio.get_event_loop()
            
            # Load the file content using langchain loaders.
            content_list = await loop.run_in_executor(
                None,
                FileProcessor.process,
                temp_path
            )
            
            content = "\n".join(content_list)
            
            # Split the content into chunks
            chunks = self.chunk_document(content)
            document_data = {
                "file_name": original_filename,
                "user_id": user_id,
                "status": StatusEnum.PROCESSING
            }
            
            async with get_db_session() as session:
                
                document = await self.document_repo.create(
                    document_data, session
                )
                await session.commit()
                await session.refresh(document)
                
                document_id = document.id
                
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    cleaned_chunks = list(executor.map(ContentCleaner.clean, chunks))
                
                embeddings = await self.embedding_service.generate_embeddings(cleaned_chunks)
                
                chunk_data = [{
                    "document_id": document_id,
                    "content": chunk,
                    "embedding": embedding
                } for chunk, embedding in zip(cleaned_chunks, embeddings)]
                
                await self.document_repo.bulk_create_chunks(chunk_data, session)
                
                # Process each chunk and store in DocumentChunk table
                # for chunk_content in chunks:
                    
                #     # Clean and generate embedding for each chunk
                #     cleaned_chunk = await loop.run_in_executor(
                #         None,
                #         ContentCleaner.clean,
                #         chunk_content
                #     )
                    
                #     embedding = await self.embedding_service.generate_embeddings(cleaned_chunk)
                    
                #     chunk_data = {
                #         "document_id": document_id,
                #         "content": cleaned_chunk,
                #         "embedding": embedding
                #     }
                    # await self.document_repo.create_chunk(chunk_data, session)
                
                # Update document status to SUCCESS
                document.status = StatusEnum.SUCCESS
                await session.commit()
        except Exception as e:
            logger.error(
                f"Failed to process {original_filename} (user {user_id}): {str(e)}",
                exc_info=True
            )
            if session:
                await session.rollback()
        finally:
            await self.file_service.cleanup_temp_file(temp_path)
            
    def chunk_document(self, content: str) -> List[str]:
        """
        Split the document content into smaller chunks.

        Args:
            content (str): The full content of the document.

        Returns:
            List[str]: A list of chunked content strings.
        """
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1500,
            chunk_overlap=200,
            length_function=len,
        )
        return text_splitter.split_text(content)
