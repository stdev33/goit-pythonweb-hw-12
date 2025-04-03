from . import models, schemas
from .database import get_db
from .models import User
from .redis_cache import get_redis_client
from dotenv import load_dotenv
from fastapi import HTTPException, Depends, status, Request
from fastapi.responses import RedirectResponse
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session
import json
import os


load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
REDIS_CACHE_EXPIRATION = int(os.getenv("REDIS_CACHE_EXPIRATION", 300))

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


async def get_current_user(
    token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)
) -> schemas.UserResponse:
    """
    Retrieves the current user based on the provided JWT token.

    Args:
        token (str): The JWT token.
        db (Session): SQLAlchemy session for database access.

    Returns:
        User: The current authenticated user.

    Raises:
        HTTPException: If the token is invalid or user is not found.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception

        token_iat = payload.get("iat")
        if token_iat is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    redis_client = get_redis_client()

    redis_key = f"user:{email}"
    cached_user = redis_client.get(redis_key)

    if cached_user:
        user = schemas.UserResponse(**json.loads(cached_user))
        if (
            user.last_password_reset
            and token_iat < user.last_password_reset.timestamp()
        ):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token is no longer valid. Please log in again.",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return user

    user = db.query(models.User).filter(models.User.email == email).first()
    if user is None:
        raise credentials_exception

    if user.last_password_reset and token_iat < user.last_password_reset.timestamp():
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token is no longer valid. Please log in again.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    redis_user = schemas.UserResponse.model_validate(user)
    redis_client.set(redis_key, redis_user.model_dump_json(), ex=REDIS_CACHE_EXPIRATION)

    return schemas.UserResponse.model_validate(user)


def get_current_user_or_redirect(
    request: Request, db: Session = Depends(get_db)
) -> User:
    token = request.cookies.get("access_token")
    if not token:
        return RedirectResponse("/auth/login-form")

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email = payload.get("sub")
        if email is None:
            return RedirectResponse("/auth/login-form")
        user = db.query(User).filter(User.email == email).first()
        if not user:
            return RedirectResponse("/auth/login-form")
        return user
    except JWTError:
        return RedirectResponse("/auth/login-form")
