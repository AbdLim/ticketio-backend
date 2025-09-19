from typing import Annotated

from fastapi import APIRouter, Depends, status

from app.schemas.user import UserCreate, UserWithToken
from app.services import get_auth_service
from app.services.auth import AuthService

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post(
    "/register", response_model=UserWithToken, status_code=status.HTTP_201_CREATED
)
async def register(
    user_create: UserCreate,
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
):
    """
    Register a new user with their wallet address.
    """
    return await auth_service.register_user(user_create)


@router.post("/login", response_model=UserWithToken)
async def login(
    wallet_address: str,
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
):
    """
    Login with wallet address.
    In a real application, this would verify a wallet signature,
    but for this example we'll just check if the wallet exists.
    """
    return await auth_service.login_user(wallet_address)
