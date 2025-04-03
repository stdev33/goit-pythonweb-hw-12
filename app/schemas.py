from pydantic import BaseModel, EmailStr
from datetime import date, datetime
from typing import Optional
from .enums import UserRole


class ContactBase(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    phone: str
    birthday: Optional[date] = None
    additional_info: Optional[str] = None


class ContactCreate(ContactBase):
    pass


class ContactUpdate(ContactBase):
    pass


class ContactResponse(ContactBase):
    id: int

    model_config = {"from_attributes": True}


class UserCreate(BaseModel):
    """
    Schema for user registration request.

    Attributes:
        username (str): The username of the user.
        email (EmailStr): The email address of the user.
        password (str): The password for the user's account.
    """

    username: str
    email: EmailStr
    password: str
    role: Optional[UserRole] = UserRole.user


class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    is_active: bool
    is_verified: bool
    avatar_url: Optional[str] = None
    last_password_reset: datetime | None = None
    role: UserRole

    model_config = {"from_attributes": True}


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str


class RefreshTokenResponse(BaseModel):
    """
    Schema for returning a refresh token from the API.

    Attributes:
        refresh_token (str): The refresh token string.
    """

    refresh_token: str
