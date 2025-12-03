from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.base import get_db
from app.core.security import decode_token
from app.models.user import User, UserRole
from app.schemas.auth import TokenPayload

security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db),
) -> User:
    """Get current authenticated user"""
    token = credentials.credentials
    payload = decode_token(token)

    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token_data = TokenPayload(**payload)

    if token_data.type != "access":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token type",
            headers={"WWW-Authenticate": "Bearer"},
        )

    result = await db.execute(select(User).where(User.id == token_data.sub))
    user = result.scalar_one_or_none()

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user",
        )

    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """Get current active user"""
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


def require_role(allowed_roles: list[UserRole]):
    """Dependency to check if user has required role"""

    async def role_checker(current_user: User = Depends(get_current_user)) -> User:
        if current_user.is_superuser:
            return current_user

        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"User role '{current_user.role}' is not authorized. Required roles: {[r.value for r in allowed_roles]}",
            )
        return current_user

    return role_checker


# Pre-defined role dependencies
async def require_admin(current_user: User = Depends(get_current_user)) -> User:
    """Require admin role"""
    if not current_user.is_superuser and current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required",
        )
    return current_user


async def require_hr_or_admin(current_user: User = Depends(get_current_user)) -> User:
    """Require HR Manager or Admin role"""
    if (
        not current_user.is_superuser
        and current_user.role not in [UserRole.ADMIN, UserRole.HR_MANAGER]
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="HR Manager or Admin privileges required",
        )
    return current_user


async def require_recruiter_or_above(current_user: User = Depends(get_current_user)) -> User:
    """Require Recruiter, HR Manager, or Admin role"""
    if (
        not current_user.is_superuser
        and current_user.role not in [UserRole.ADMIN, UserRole.HR_MANAGER, UserRole.RECRUITER]
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Recruiter privileges or higher required",
        )
    return current_user
