from datetime import datetime, timedelta
from typing import Optional
from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from . import models, schemas
from .database import get_db
from .email import send_verification_email
import os
from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))

router = APIRouter(prefix="/auth", tags=["auth"])

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def get_password_hash(password: str) -> str:
    """
    Hashes the provided password using bcrypt.

    Args:
        password (str): The plain text password.

    Returns:
        str: The hashed password.
    """
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verifies that a plain password matches the hashed password.

    Args:
        plain_password (str): The plain text password.
        hashed_password (str): The hashed password to compare against.

    Returns:
        bool: True if the password matches, False otherwise.
    """
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Generates a JWT access token.

    Args:
        data (dict): The data to include in the token payload.
        expires_delta (Optional[timedelta]): The token expiration time.

    Returns:
        str: The generated JWT token.
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def authenticate_user(db: Session, email: str, password: str):
    """
    Authenticates a user by verifying email and password.

    Args:
        db (Session): SQLAlchemy session for database access.
        email (str): The user's email.
        password (str): The user's password.

    Returns:
        User or None: The authenticated user or None if authentication fails.
    """
    user = db.query(models.User).filter(models.User.email == email).first()
    if not user or not verify_password(password, user.hashed_password):
        return None
    return user


async def get_current_user(
    token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)
):
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
    except JWTError:
        raise credentials_exception
    user = db.query(models.User).filter(models.User.email == email).first()
    if user is None:
        raise credentials_exception
    return user


def create_verification_token(email: str) -> str:
    """
    Creates a JWT token for email verification.

    Args:
        email (str): The email address to verify.

    Returns:
        str: The generated verification token.
    """
    expire = datetime.utcnow() + timedelta(hours=24)
    data = {"sub": email, "exp": expire}
    return jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)


@router.post(
    "/register",
    response_model=schemas.UserResponse,
    status_code=status.HTTP_201_CREATED,
)
def register_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    """
    Registers a new user and sends a verification email.

    Args:
        user (UserCreate): The user registration data.
        db (Session): SQLAlchemy session for database access.

    Returns:
        UserResponse: The registered user data.

    Raises:
        HTTPException: If the email is already registered.
    """
    existing_user = (
        db.query(models.User).filter(models.User.email == user.email).first()
    )
    if existing_user:
        raise HTTPException(status_code=409, detail="Email already registered")

    verification_token = create_verification_token(user.email)
    hashed_password = get_password_hash(user.password)
    db_user = models.User(
        username=user.username,
        email=user.email,
        hashed_password=hashed_password,
        verification_token=verification_token,
        is_verified=False,
        is_active=True,
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    send_verification_email(user.email, verification_token)

    return db_user


@router.get("/verify-email")
def verify_email(token: str, db: Session = Depends(get_db)):
    """
    Verifies a user's email address using a JWT token.

    Args:
        token (str): The verification token.
        db (Session): SQLAlchemy session for database access.

    Returns:
        dict: A success message if verification succeeds.

    Raises:
        HTTPException: If the token is invalid or the user is already verified.
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email = payload.get("sub")
        if not email:
            raise HTTPException(status_code=400, detail="Invalid token")

        user = db.query(models.User).filter(models.User.email == email).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        if user.is_verified:
            raise HTTPException(status_code=400, detail="User already verified")

        user.is_verified = True
        user.verification_token = None
        db.commit()

        return {"message": "Email successfully verified!"}
    except JWTError:
        raise HTTPException(status_code=400, detail="Invalid token or expired link")


@router.post("/login", response_model=schemas.Token)
def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)
):
    """
    Authenticates a user and returns a JWT access token.

    Args:
        form_data (OAuth2PasswordRequestForm): The login credentials.
        db (Session): SQLAlchemy session for database access.

    Returns:
        dict: The access token and token type.

    Raises:
        HTTPException: If authentication fails.
    """
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}
