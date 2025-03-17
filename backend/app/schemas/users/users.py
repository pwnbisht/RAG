import datetime
from pydantic import BaseModel, EmailStr


class UserCreate(BaseModel):
    """
    Schema for creating a new user.

    Attributes:
        username (str): The username of the user.
        email (EmailStr): The email address of the
        user.
        password (str): The password for the user
        account.
    """
    username: str
    email: EmailStr
    password: str


class LoginUser(BaseModel):
    """
    Schema for logging in a user.

    Attributes:
        username (str): The username of the user.
        password (str): The password for the user
        account.
    """
    username: str
    password: str


class UserResponse(BaseModel):
    """
    Represents a user response model with attributes
    for user identification.

    Attributes:
        id (int): The unique identifier for the user.
        username (str): The username of the user.
        email (EmailStr): The email address of the
        user.

    Config:
        from_attributes (bool): Enables model creation
        from ORM objects.
    """
    id: int
    username: str
    email: EmailStr

    class Config:
        from_attributes = True


class TokenCreate(BaseModel):
    """
    Represents a token creation model for user
    authentication.

    Attributes:
        user_id (str): The unique identifier for the
        user.
        access_token (str): The token used for
        accessing resources.
        refresh_token (str): The token used to refresh
        the access token.
        status (bool): Indicates whether the token is
        active.
        created_date (datetime.datetime): The date and
        time when the token was created.
    """
    user_id:str
    access_token:str
    refresh_token:str
    status:bool
    created_date:datetime.datetime


class TokenSchema(BaseModel):
    """
    Schema for representing authentication tokens.

    Attributes:
        access_token (str): The token used for accessing
        resources.
        refresh_token (str): The token used to obtain
        a new access token.
    """
    access_token: str
    refresh_token: str