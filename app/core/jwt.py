from datetime import datetime, timedelta
from typing import Any, Dict

from jose import jwt
from app.core.config import Settings

settings = Settings()


def create_access_token(subject: str, extra_data: Dict[str, Any] = None) -> str:
    """
    Create a JWT access token.

    Args:
        subject: The subject of the token (usually user ID or wallet address)
        extra_data: Additional data to include in the token

    Returns:
        str: The encoded JWT token
    """
    if extra_data is None:
        extra_data = {}

    expires_delta = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    expire = datetime.utcnow() + expires_delta

    to_encode = {"exp": expire, "sub": str(subject), **extra_data}

    encoded_jwt = jwt.encode(
        to_encode, settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM
    )

    return encoded_jwt


def verify_token(token: str) -> Dict[str, Any]:
    """
    Verify and decode a JWT token.

    Args:
        token: The JWT token to verify

    Returns:
        Dict[str, Any]: The decoded token payload

    Raises:
        JWTError: If token is invalid or expired
    """
    payload = jwt.decode(
        token, settings.SECRET_KEY, algorithms=[settings.JWT_ALGORITHM]
    )
    return payload
