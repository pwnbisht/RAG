import datetime

from sqlalchemy import (
    Column, Integer, String, Boolean,
    DateTime, Index
)
from app.db.base import Base
from sqlalchemy.orm import relationship


class User(Base):
    """
    Represents a user in the system.

    Attributes:
        id (int): The primary key for the user.
        username (str): The unique username of the user.
        email (str): The unique email address of the user.
        hashed_password (str): The hashed password of the user.
        is_active (bool): Indicates if the user is active.
        Defaults to True.
        is_superuser (bool): Indicates if the user has superuser
        privileges. Defaults to False.
    """
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    
    documents = relationship("Document", back_populates="user")
    

class TokenTable(Base):
    """
    Production-level Token model.

    Attributes:
        id (int): Auto-generated primary key.
        user_id (int): ID of the user associated with the token.
        access_token (str): The JWT access token.
        refresh_token (str): The refresh token.
        status (bool): True if token is active; False otherwise.
        created_at (datetime): Timestamp when the token was created.
    """
    __tablename__ = "token"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True, nullable=False)
    access_token = Column(String(450), unique=True, index=True, nullable=False)
    refresh_token = Column(String(450), nullable=False)
    status = Column(Boolean, default=True, index=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    __table_args__ = (
        Index("ix_user_status", "user_id", "status"),
    )
