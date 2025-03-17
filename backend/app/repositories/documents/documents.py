from sqlalchemy.future import select
from sqlalchemy.orm import load_only
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models.documents import Document, DocumentChunk
from app.core.exceptions import NotFoundException


class DocumentRepository:
    """
    Repository for document related operations
    """

    async def create(self, document_data: dict, session: AsyncSession):
        """
        Create a new document

        Args:
            document_data (dict): The document data
            session (AsyncSession): The database session

        Returns:
            Document: The created document
        """
        document = Document(**document_data)
        session.add(document)
        await session.commit()
        await session.refresh(document)
        return document
    
    async def create_chunk(self, chunk_data: dict, session: AsyncSession):
        """
        Create a new document chunk

        Args:
            chunk_data (dict): The chunk data
            session (AsyncSession): The database session

        Returns:
            DocumentChunk: The created chunk
        """
        chunk = DocumentChunk(**chunk_data)
        session.add(chunk)
        await session.commit()
        await session.refresh(chunk)
        return chunk

    async def get_documents_by_user(
        self, 
        user_id: int,
        session: AsyncSession
    ) -> list[Document]:
        """
        Get a list of all documents for the current user

        Args:
            user_id (int): The user id
            session (AsyncSession): The database session

        Returns:
            list[Document]: A list of documents for the current user
        """
        query = select(Document).where(Document.user_id == user_id)
        result = await session.execute(query)
        documents = result.scalars().all()
        return documents
    
    async def get_document_by_user_and_id(
        self, 
        user_id: int,
        document_id: int,
        session: AsyncSession
    ) -> Document:
        """
        Get a single document by ID that belongs to the specified user

        Args:
            user_id (int): The user id
            document_id (int): The document id
            session (AsyncSession): The database session

        Returns:
            Document: The document for the user and id
        """
        result = await session.execute(
            select(Document)
            .options(load_only(Document.id, Document.status))
            .where(
                Document.id == document_id,
                Document.user_id == user_id
            )
        )
        document = result.scalar_one_or_none()
        
        if not document:
            raise NotFoundException(message="Document not found")
            
        return document
    
    async def find_similar_content(
        self,
        document_id: int,
        query_embedding: list,
        threshold: float,
        limit: int,
        session: AsyncSession,
    ) -> list[str]:
        """
        Find similar content to a query in a document

        Args:
            document_id (int): The document id
            query_embedding (list): The query embedding
            threshold (float): The maximum cosine distance
            limit (int): The maximum number of results
            session (AsyncSession): The database session

        Returns:
            list[str]: A list of similar content
        """
        query = select(DocumentChunk.content).where(
                    DocumentChunk.document_id == document_id,
                    DocumentChunk.embedding.cosine_distance(
                        query_embedding
                    ) < threshold
                ).order_by(
                    DocumentChunk.embedding.cosine_distance(
                        query_embedding
                        )
                ).limit(limit)
        result = await session.execute(query)
        return result.scalars().all()
