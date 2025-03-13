from datetime import datetime
from pydantic import BaseModel
from typing import List, Optional


class DocumentOut(BaseModel):
    id: int
    file_name: str
    user_id: int
    status: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ChatRequest(BaseModel):
    query: str


class ChatResponse(BaseModel):
    response: str
    sources: Optional[List[str]] = None
