import enum
from datetime import datetime, timezone
from pgvector.sqlalchemy import Vector
from sqlalchemy import Column
from sqlalchemy import Integer 
from sqlalchemy import String, Text
from sqlalchemy import DateTime
from sqlalchemy import ForeignKey
from sqlalchemy import Index
from sqlalchemy import Enum
from sqlalchemy.orm import relationship

from app.db.base import Base


class StatusEnum(enum.Enum):
    FAILED = "Failed"
    SUCCESS = "Success"
    PROCESSING = "Processing"


class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    file_name = Column(String, nullable=False)
    chunks = relationship("DocumentChunk", backref="document")
    user_id = Column(Integer, ForeignKey("users.id"), index=True, nullable=False)
    user = relationship("User", back_populates="documents")
    status = Column(Enum(StatusEnum), nullable=True, default=StatusEnum.PROCESSING)
    created_at = Column(DateTime(timezone=True), default=datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=datetime.now(timezone.utc))
    
    __table_args__ = (
        Index('ix_document_user', 'user_id'),
        # Index(
        #     'ix_document_embedding',
        #     'embedding',
        #     postgresql_using='ivfflat',
        #     postgresql_ops={'embedding': 'vector_l2_ops'}
        # ),
    )


class DocumentChunk(Base):
    __tablename__ = "document_chunks"
    id = Column(Integer, primary_key=True)
    document_id = Column(Integer, ForeignKey("documents.id"))
    content = Column(Text)
    embedding = Column(Vector(2048), nullable=False)