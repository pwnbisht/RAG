from jose import jwt
from jose.exceptions import JWTError
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials  # noqa: F401
from fastapi import Request, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.core.config import get_settings
from app.db.base import get_db
from app.db.models.users import TokenTable

def decodeJWT(jwtoken: str):
    try:
        settings = get_settings()
        payload = jwt.decode(
            jwtoken, settings.JWT_SECRET_KEY,
            algorithms=[settings.algorithm]
        )
        return payload
    except JWTError as e:
        print(e)
        return None
    

# class JWTBearer(HTTPBearer):
#     """Verify and decode JWT token."""

#     def __init__(self, auto_error: bool = True):
#         """Initialize JWTBearer.

#         Args:
#             auto_error (bool, optional): Automatically raise exceptions.
#             Defaults to True.
#         """
#         super().__init__(auto_error=auto_error)

#     async def __call__(self, request: Request, db: AsyncSession = Depends(get_db)):
#         """Verify and decode JWT token.

#         Args:
#             request (Request): FastAPI request object.

#         Returns:
#             str: Decoded JWT token.
#         """
#         credentials: HTTPAuthorizationCredentials = await super().__call__(request)
#         if not credentials:
#             raise HTTPException(
#                 status_code=403,
#                 detail="Invalid authorization code."
#             )
#         try:
#             payload = decodeJWT(credentials.credentials)
#             if not payload:
#                 raise HTTPException(
#                     status_code=403,
#                     detail="Invalid or expired token."
#                 )
#             query = select(TokenTable).filter(
#                 TokenTable.access_token == credentials.credentials,
#                 TokenTable.status
#             )
#             result = await db.execute(query)
#             token_record = result.scalars().first()
#             if token_record is None:
#                 raise HTTPException(
#                     status_code=403,
#                     detail="Token has been invalidated or does not exist."
#                 )
#             return payload
#         except JWTError:
#             raise HTTPException(
#                 status_code=403,
#                 detail="Invalid or expired token."
#             )

class JWTBearer(HTTPBearer):
    async def __call__(self, request: Request, db: AsyncSession = Depends(get_db)):
        # Get token from cookie
        access_token = request.cookies.get("_at")
        if not access_token:
            raise HTTPException(
                status_code=403,
                detail="Missing access token cookie"
            )

        try:
            payload = decodeJWT(access_token)
            if not payload:
                raise HTTPException(
                    status_code=403,
                    detail="Invalid or expired token."
                )
            query = select(TokenTable).filter(
                TokenTable.access_token == access_token,
                TokenTable.status
            )
            result = await db.execute(query)
            token_record = result.scalars().first()
            
            if token_record is None:
                raise HTTPException(
                    status_code=403,
                    detail="Token invalidated"
                )
            return payload
        except JWTError:
            raise HTTPException(
                status_code=403,
                detail="Invalid token"
            )

jwt_bearer = JWTBearer()