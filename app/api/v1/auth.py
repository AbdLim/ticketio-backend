from typing import Annotated

from fastapi import APIRouter, Depends, status

from app.schemas.user import UserCreate, UserWithToken, UserWithTokenAndBalance
from app.services import get_auth_service
from app.services.auth import AuthService

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post(
    "/register",
    response_model=UserWithTokenAndBalance,
    status_code=status.HTTP_201_CREATED,
)
async def register(
    user_create: UserCreate,
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
):
    """
    Register a new user with their wallet address.
    """
    return await auth_service.register_user(user_create)


@router.post("/login", response_model=UserWithTokenAndBalance)
async def login(
    wallet_address: str,
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
):
    """
    Login with wallet address and get current balance.
    """
    return await auth_service.login_user(wallet_address)


# @router.post("/create-account", response_model=UserWithTokenAndBalance, status_code=status.HTTP_201_CREATED)
# async def create_hedera_account(
#     name: str = None,
#     email: str = None,
#     auth_service: Annotated[AuthService, Depends(get_auth_service)],
# ):
#     """
#     Create a new Hedera account with initial balance.
#     This creates both a Hedera blockchain account and user profile.
#     """
#     return await auth_service.create_new_hedera_account(name, email)


@router.get("/balance")
async def get_wallet_balance(
    wallet_address: str,
):
    """
    Get current wallet balance for any Hedera account.
    """
    from app.services.hedera_wallet import hedera_wallet_service

    balance_info = await hedera_wallet_service.get_account_balance(wallet_address)

    if not balance_info["success"]:
        from fastapi import HTTPException

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Could not retrieve balance: {balance_info.get('error')}",
        )

    return {
        "wallet_address": wallet_address,
        "hbar_balance": balance_info["hbar_balance"],
        "last_updated": balance_info["last_updated"],
    }
