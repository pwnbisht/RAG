from fastapi import APIRouter, Depends, Request
# from fastapi.security import OAuth2PasswordRequestForm
from app.core.factory.userfactory import get_auth_controller
from app.core.exceptions import ForbiddenException
from app.controllers.users.auth_controller import AuthController
from app.schemas.users.users import UserCreate, TokenSchema, LoginUser
from app.services.auth.auth_services import jwt_bearer

from .auth_response import AuthResponse, LogoutResponse

router = APIRouter()

@router.post("/signup")
async def signup(
    user: UserCreate,
    auth_controller: AuthController = Depends(get_auth_controller)
) -> dict:
    """
    Creates a new user.

    Args:
        user (UserCreate): The user to be created.

    Returns:
        dict: A message indicating successful signup.
    """
    await auth_controller.signup(user)
    return {"message": "Signup successful"}


@router.post("/login", response_model=TokenSchema)
async def login(
    # form_data: OAuth2PasswordRequestForm = Depends(),
    login_data: LoginUser,
    auth_controller: AuthController = Depends(get_auth_controller)
) -> TokenSchema:
    """
    Logs in a user.

    Args:
        login_data (LoginUser): The user to be logged in.

    Returns:
        TokenSchema: The access and refresh tokens.
    """
    tokens = await auth_controller.login(
        login_data.username, login_data.password
    )
    return AuthResponse(
        content={"message": "Login successful"},
        tokens=tokens
    )


@router.post("/logout", dependencies=[Depends(jwt_bearer)])
async def logout(
    token_data: dict = Depends(jwt_bearer),
    auth_controller: AuthController = Depends(get_auth_controller)
) -> LogoutResponse:
    """
    Logs out a user.

    Args:
        token_data (dict): The token data containing the user id.
        auth_controller (AuthController): The authentication controller.

    Returns:
        LogoutResponse: The response with a message indicating the logout result.
    """
    user_id = int(token_data.get("sub"))
    await auth_controller.logout(user_id)
    return LogoutResponse(
        content={"message": "Logout successful"}
    )


@router.post("/refresh")
async def refresh_tokens(
    request: Request,
    auth_controller: AuthController = Depends(get_auth_controller)
) -> AuthResponse:
    """
    Refreshes the access and refresh tokens.

    Args:
        request (Request): The request containing the refresh token.
        auth_controller (AuthController): The authentication controller.

    Returns:
        AuthResponse: The response with the refreshed tokens.
    """
    refresh_token = request.cookies.get("_rt")
    if not refresh_token:
        raise ForbiddenException(message="Unauthorized")

    return AuthResponse(
        content={"message": "Tokens refreshed successfully"},
        tokens=await auth_controller.refresh_tokens(refresh_token)
    )
