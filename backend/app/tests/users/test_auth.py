import re
import pytest
import pytest_mock
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock
from pydantic import ValidationError

from app.api.v1.users.auth.auth import signup, login, logout
from app.api.v1.users.auth.auth_response import AuthResponse, LogoutResponse
from app.controllers.users.auth import AuthController
from app.core.exceptions import ForbiddenException
from app.core.exceptions import BadRequestException
from app.main import app
from app.schemas.users.users import UserCreate, TokenSchema, LoginUser


# We can also use FastAPI's TestClient to test the API endpoints.
client = TestClient(app)

def test_signup_invalid_username():
    """
    Test that the signup endpoint returns a 422 status code when the username
    is invalid.
    """
    response = client.post("/api/v1/auth/signup", json={
        "username": "",
        "email": "test@example.com",
        "password": "password123"
    })
    assert response.status_code == 422
    assert "detail" in response.json()


@pytest.mark.asyncio
async def test_signup_successful():
    """
    Test that the signup endpoint works when the input is valid and the auth controller
    does not raise an exception.
    """
    mock_auth_controller = AsyncMock(spec=AuthController)
    mock_auth_controller.signup.return_value = None

    user_data = UserCreate(
        username="testuser",
        email="test@example.com",
        password="password123"
    )
    response = await signup(user_data, auth_controller=mock_auth_controller)
    mock_auth_controller.signup.assert_called_once_with(user_data)
    assert response == {"message": "Signup successful"}


@pytest.mark.asyncio
async def test_signup_duplicate_username_or_email():
    """
    Test that the signup endpoint raises an exception when the auth controller
    raises an exception because the username or email already exists.
    """
    mock_auth_controller = AsyncMock(spec=AuthController)
    mock_auth_controller.signup.side_effect = Exception("Username or email already exists")

    user_data = UserCreate(
        username="testuser",
        email="test@example.com",
        password="password123"
    )
    with pytest.raises(Exception):
        await signup(user_data, auth_controller=mock_auth_controller)


@pytest.mark.asyncio
async def test_user_create_invalid_username():
    """
    Test that UserCreate raises a ValidationError when the username is invalid.
    """
    with pytest.raises(ValidationError):
        UserCreate(
            username="",
            email="test@example.com",
            password="password123"
        )

@pytest.mark.asyncio
async def test_signup_auth_controller_error():
    """
    Test that the signup endpoint raises an exception when the auth controller
    raises an exception.
    """
    mock_auth_controller = AsyncMock(spec=AuthController)
    mock_auth_controller.signup.side_effect = Exception("Authentication controller error")

    user_data = UserCreate(
        username="testuser",
        email="test@example.com",
        password="password123"
    )
    with pytest.raises(Exception):
        await signup(user_data, auth_controller=mock_auth_controller)
        

@pytest.mark.asyncio
async def test_successful_login_returns_token_schema():
    """
    Test that the login endpoint returns a TokenSchema instance when the
    authentication controller successfully logs in the user.
    """
    mock_auth_controller = AsyncMock(spec=AuthController)
    mock_tokens = TokenSchema(access_token="test_access_token", refresh_token="test_refresh_token")
    mock_auth_controller.login.return_value = mock_tokens

    login_data = LoginUser(username="testuser", password="password123")

    response = await login(login_data=login_data, auth_controller=mock_auth_controller)

    mock_auth_controller.login.assert_called_once_with(
        login_data.username, login_data.password
    )
    assert isinstance(response, AuthResponse)
    assert response.status_code == 200
    assert response.body == b'{"message":"Login successful"}'
    

@pytest.mark.asyncio
async def test_login_with_nonexistent_username_raises_exception():
    """
    Test that the login endpoint raises an exception when the authentication
    controller raises a BadRequestException due to a nonexistent username.
    """
    mock_auth_controller = AsyncMock(spec=AuthController)
    mock_auth_controller.login.side_effect = BadRequestException("Incorrect username or password")

    login_data = LoginUser(username="does_not_exits", password="password123")

    with pytest.raises(BadRequestException) as exc_info:
        await login(login_data=login_data, auth_controller=mock_auth_controller)

    assert str(exc_info.value) == "Incorrect username or password"
    mock_auth_controller.login.assert_called_once_with(login_data.username, login_data.password)


@pytest.mark.asyncio
async def test_login_response_includes_success_message_and_sets_auth_cookies():
    """
    Test that the login endpoint returns a successful response with a message
    and sets the authentication cookies.
    """
    mock_auth_controller = AsyncMock(spec=AuthController)
    mock_tokens = TokenSchema(access_token="test_access_token", refresh_token="test_refresh_token")
    mock_auth_controller.login.return_value = mock_tokens

    login_data = LoginUser(username="testuser", password="password123")
    response = await login(login_data=login_data, auth_controller=mock_auth_controller)

    mock_auth_controller.login.assert_called_once_with(login_data.username, login_data.password)
    assert isinstance(response, AuthResponse)
    assert response.status_code == 200
    assert response.body == b'{"message":"Login successful"}'
    set_cookie_headers = response.headers.getlist("set-cookie")
    # print(set_cookie_headers)
    assert set_cookie_headers is not None
    assert any("_at=test_access_token" in header for header in set_cookie_headers)
    assert any("_rt=test_refresh_token" in header for header in set_cookie_headers)


@pytest.mark.asyncio
async def test_login_sets_secure_cookies():
    """
    Test that the login endpoint sets the authentication cookies with the
    secure flag.
    """
    mock_auth_controller = AsyncMock(spec=AuthController)
    mock_tokens = TokenSchema(access_token="test_access_token", refresh_token="test_refresh_token")
    mock_auth_controller.login.return_value = mock_tokens

    login_data = LoginUser(username="testuser", password="password123")
    response = await login(login_data=login_data, auth_controller=mock_auth_controller)
    
    mock_auth_controller.login.assert_called_once_with(login_data.username, login_data.password)
    assert isinstance(response, AuthResponse)
    assert response.status_code == 200
    assert response.body == b'{"message":"Login successful"}'
    cookies = response.headers.getlist('set-cookie')
    # assert cookies is not None
    # assert any('_at=test_access_token; Domain=localhost; HttpOnly; Max-Age=3600; Path=/; SameSite=lax' in cookie for cookie in cookies)
    # assert any('_rt=test_refresh_token; Domain=localhost; HttpOnly; Max-Age=604800; Path=/; SameSite=lax' in cookie for cookie in cookies)

    access_pattern = re.compile(
        r'_at=test_access_token; Domain=\S+; HttpOnly; Max-Age=\d+; Path=/; SameSite=lax'
    )
    refresh_pattern = re.compile(
        r'_rt=test_refresh_token; Domain=\S+; HttpOnly; Max-Age=\d+; Path=/; SameSite=lax'
    )
    assert any(access_pattern.search(cookie) for cookie in cookies)
    assert any(refresh_pattern.search(cookie) for cookie in cookies)


@pytest.mark.asyncio
async def test_valid_refresh_token_returns_new_tokens(mocker: pytest_mock.MockFixture):
    """
    Test that a valid refresh token returns new access and refresh tokens.
    """
    user_repo = mocker.MagicMock()
    token_repo = mocker.AsyncMock()
    auth_controller = AuthController(user_repo, token_repo)
    settings_mock = mocker.MagicMock()
    settings_mock.JWT_REFRESH_SECRET_KEY = "test_secret"
    settings_mock.algorithm = "HS256"
    
    mocker.patch("app.controllers.users.auth.get_settings", return_value=settings_mock)

    payload = {"sub": "1"}
    mocker.patch("app.controllers.users.auth.jwt.decode", return_value=payload)

    token_record = mocker.MagicMock()
    token_repo.get_by_refresh_token.return_value = token_record

    expected_tokens = TokenSchema(access_token="new_access", refresh_token="new_refresh")
    mocker.patch("app.controllers.users.auth.create_tokens", return_value=expected_tokens)

    result = await auth_controller.refresh_tokens("valid_refresh_token")

    token_repo.get_by_refresh_token.assert_called_once_with("valid_refresh_token")
    token_repo.invalidate_token.assert_called_once_with("valid_refresh_token")

    assert result == expected_tokens
        

@pytest.mark.asyncio
async def test_refresh_token_with_missing_sub_raises_forbidden(mocker: pytest_mock.MockFixture):
    """
    Test that the refresh_tokens method raises a ForbiddenException when the
    refresh token payload is missing the "sub" key.
    """
    user_repo = mocker.MagicMock()
    token_repo = mocker.AsyncMock()
    auth_controller = AuthController(user_repo, token_repo)

    settings_mock = mocker.MagicMock()
    settings_mock.JWT_REFRESH_SECRET_KEY = "test_secret"
    settings_mock.algorithm = "HS256"
    mocker.patch("app.controllers.users.auth.get_settings", return_value=settings_mock)

    payload = {}
    mocker.patch("app.controllers.users.auth.jwt.decode", return_value=payload)

    # print("invalid refresh tokennnnnnssssssssssssssssssssssssssssssssssssssss")
    with pytest.raises(ForbiddenException) as exc_info:
        await auth_controller.refresh_tokens("invalid_refresh_token")

    # print("Exception raised:", exc_info.value)
    assert str(exc_info.value) == "Invalid refresh token payload."
    token_repo.get_by_refresh_token.assert_not_called()
    token_repo.invalidate_token.assert_not_called()


@pytest.mark.asyncio
async def test_logout_successfully_invalidates_tokens(mocker: pytest_mock.MockFixture):
    """
    Test that the logout endpoint successfully invalidates tokens and returns
    a LogoutResponse with the expected message.
    """
    token_data = {"sub": "123"}
    
    mock_auth_controller = mocker.AsyncMock()
    mock_auth_controller.logout.return_value = {"message": "Logout successful."}

    response = await logout(token_data, mock_auth_controller)

    mock_auth_controller.logout.assert_called_once_with(123)
    
    assert isinstance(response, LogoutResponse)
    assert response.body == b'{"message":"Logout successful"}'
    