from fastapi import APIRouter
from .users.auth import auth
from .users.documents import documents

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(documents.router, prefix="/docs", tags=["docs"])
