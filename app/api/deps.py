from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError

from app.core.jwt import verify_token
from app.services import get_auth_service
from app.services.auth import AuthService
from app.db.models import User, UserRole
from app.db.session import get_session

# Alias for backward compatibility
get_db = get_session

# OAuth2-style JWT Bearer token scheme
jwt_bearer_scheme = HTTPBearer(
    scheme_name="JWT Bearer",
    description="JWT Bearer token authentication",
    auto_error=True,
)


async def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(jwt_bearer_scheme)],
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
) -> User:
    """
    Get the current authenticated user from the JWT token.
    Uses OAuth2-style Bearer token authentication with JWT.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        # Extract token from credentials
        token = credentials.credentials
        payload = verify_token(token)
        wallet_address: str = payload.get("sub")
        if wallet_address is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = await auth_service.get_user_by_wallet(wallet_address)
    if user is None:
        raise credentials_exception

    return user


async def get_current_active_user(
    current_user: Annotated[User, Depends(get_current_user)],
) -> User:
    """
    Ensure the current user is active.
    """
    return current_user


async def get_current_organizer(
    current_user: Annotated[User, Depends(get_current_user)],
) -> User:
    """
    Ensure the current user is an organizer.
    """
    if current_user.role != UserRole.ORGANIZER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to perform this action",
        )
    return current_user


async def get_current_staff(
    current_user: Annotated[User, Depends(get_current_user)],
) -> User:
    """
    Ensure the current user is a staff member.
    """
    if current_user.role != UserRole.STAFF:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to perform this action",
        )
    return current_user
