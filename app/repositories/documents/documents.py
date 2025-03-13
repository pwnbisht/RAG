from sqlalchemy.future import select
from sqlalchemy.orm import load_only
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models.documents import Document
from app.core.exceptions import NotFoundException


class DocumentRepository:
    async def create(self, document_data: dict, session: AsyncSession):
        document = Document(**document_data)
        session.add(document)
        await session.commit()
        await session.refresh(document)
        return document
    
    async def get_documents_by_user(self, user_id: int, session: AsyncSession):
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
    ) -> str:
        query = select(Document.content).where(
                    Document.id == document_id,
                    Document.embedding.cosine_distance(
                        query_embedding
                    ) < threshold
                ).order_by(
                    Document.embedding.cosine_distance(
                        query_embedding
                        )
                ).limit(limit)
        result = await session.execute(query)
        return result.scalars().all()
        # return "\n".join([row[0] for row in result.all()])