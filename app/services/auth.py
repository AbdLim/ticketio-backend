from typing import Optional
from uuid import uuid4

from fastapi import HTTPException, status

from app.core.jwt import create_access_token
from app.db.repositories.user import UserRepository
from app.db.models.user import User
from app.schemas.user import UserCreate, UserWithToken


class AuthService:
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository

    async def register_user(self, user_create: UserCreate) -> UserWithToken:
        """
        Register a new user with their wallet address.
        """
        # Check if user already exists
        existing_user = await self.user_repository.get_by_wallet(
            user_create.wallet_address
        )
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User with this wallet address already exists",
            )

        # Create user with UUID
        user_dict = user_create.model_dump()
        user_dict["id"] = str(uuid4())
        user = await self.user_repository.create(user_dict)

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

    async def login_user(self, wallet_address: str) -> UserWithToken:
        """
        Login with wallet address.
        """
        user = await self.user_repository.get_by_wallet(wallet_address)
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

    async def get_user_by_wallet(self, wallet_address: str) -> Optional[User]:
        """
        Get user by wallet address.
        """
        return await self.user_repository.get_by_wallet(wallet_address)
