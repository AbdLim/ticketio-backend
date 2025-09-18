from typing import Annotated
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_session
from app.core.jwt import create_access_token
from app.db.repositories.user import UserRepository
from app.schemas.user import UserCreate, UserWithToken

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post(
    "/register", response_model=UserWithToken, status_code=status.HTTP_201_CREATED
)
async def register(
    user_create: UserCreate,
    db: Annotated[AsyncSession, Depends(get_session)],
):
    """
    Register a new user with their wallet address.
    """
    user_repo = UserRepository(db)

    # Check if user already exists
    if await user_repo.get_by_wallet(user_create.wallet_address):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this wallet address already exists",
        )

    # Create user with UUID
    user_dict = user_create.model_dump()
    user_dict["id"] = str(uuid4())
    user = await user_repo.create(user_dict)

    # Create access token
    token = create_access_token(user.wallet_address)

    return UserWithToken(
        id=user.id,
        wallet_address=user.wallet_address,
        name=user.name,
        email=user.email,
        role=user.role,
        created_at=user.created_at,
        token=token,
    )


@router.post("/login", response_model=UserWithToken)
async def login(
    wallet_address: str,
    db: Annotated[AsyncSession, Depends(get_session)],
):
    """
    Login with wallet address.
    In a real application, this would verify a wallet signature,
    but for this example we'll just check if the wallet exists.
    """
    user_repo = UserRepository(db)
    user = await user_repo.get_by_wallet(wallet_address)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid wallet address",
        )

    # Create access token
    token = create_access_token(user.wallet_address)

    return UserWithToken(
        id=user.id,
        wallet_address=user.wallet_address,
        name=user.name,
        email=user.email,
        role=user.role,
        created_at=user.created_at,
        token=token,
    )
