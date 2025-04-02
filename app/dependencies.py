from . import schemas
from .database import get_db
from .enums import UserRole
from .security import get_current_user
from fastapi import Request, Depends, HTTPException, status
from sqlalchemy.orm import Session


async def require_admin_user(
    current_user: schemas.UserResponse = Depends(get_current_user),
) -> schemas.UserResponse:
    """
    Dependency that ensures the current user has admin role.

    Raises:
        HTTPException: If the user is not an admin.
    """
    if current_user.role != UserRole.admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied. Admin privileges required.",
        )
    return current_user


def get_token_from_cookie(request: Request) -> str:
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return token


async def get_current_user_from_cookie(
    token: str = Depends(get_token_from_cookie),
    db: Session = Depends(get_db),
) -> schemas.UserResponse:
    return await get_current_user(token=token, db=db)


async def require_admin_user_from_cookie(
    current_user: schemas.UserResponse = Depends(get_current_user_from_cookie),
) -> schemas.UserResponse:
    if current_user.role != UserRole.admin:
        raise HTTPException(status_code=403, detail="Admin access required")
    return current_user
