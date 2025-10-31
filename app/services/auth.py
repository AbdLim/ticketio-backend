from typing import Optional
from uuid import uuid4

from fastapi import HTTPException, status

from app.core.jwt import create_access_token
from app.db.repositories.user import UserRepository
from app.db.models.user import User
from app.schemas.user import UserCreate, UserWithToken, UserWithTokenAndBalance


class AuthService:
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository

    async def register_user(self, user_create: UserCreate) -> UserWithTokenAndBalance:
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

        # Get wallet balance
        from app.services.hedera_wallet import hedera_wallet_service

        balance_info = await hedera_wallet_service.get_account_balance(
            user.wallet_address
        )

        return UserWithTokenAndBalance(
            id=user.id,
            wallet_address=user.wallet_address,
            name=user.name,
            email=user.email,
            role=user.role,
            created_at=user.created_at,
            token=token,
            hbar_balance=balance_info["hbar_balance"],
            last_balance_check=balance_info["last_updated"],
        )

    async def login_user(self, wallet_address: str) -> UserWithTokenAndBalance:
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

        # Get current wallet balance
        from app.services.hedera_wallet import hedera_wallet_service

        balance_info = await hedera_wallet_service.get_account_balance(
            user.wallet_address
        )

        return UserWithTokenAndBalance(
            id=user.id,
            wallet_address=user.wallet_address,
            name=user.name,
            email=user.email,
            role=user.role,
            created_at=user.created_at,
            token=token,
            hbar_balance=balance_info["hbar_balance"],
            last_balance_check=balance_info["last_updated"],
        )

    async def get_user_by_wallet(self, wallet_address: str) -> Optional[User]:
        """
        Get user by wallet address.
        """
        return await self.user_repository.get_by_wallet(wallet_address)

    async def create_new_hedera_account(
        self,
        name: Optional[str] = None,
        email: Optional[str] = None,
        role: Optional[str] = None,
    ) -> UserWithTokenAndBalance:
        """
        Create a new Hedera account and user profile.
        """
        from app.services.hedera_wallet import hedera_wallet_service

        # Create new Hedera account
        account_result = await hedera_wallet_service.create_new_hedera_account(
            initial_balance_hbar=10.0  # Give new users 10 HBAR to start
        )

        if not account_result["success"]:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to create Hedera account: {account_result.get('error')}",
            )

        # Create user profile with new wallet address
        user_dict = {
            "id": str(uuid4()),
            "wallet_address": account_result["account_id"],
            "name": name,
            "email": email,
            "role": role,
        }

        user = await self.user_repository.create(user_dict)

        # Create access token
        token = create_access_token(user.wallet_address)

        return UserWithTokenAndBalance(
            id=user.id,
            wallet_address=user.wallet_address,
            name=user.name,
            email=user.email,
            role=user.role,
            created_at=user.created_at,
            token=token,
            hbar_balance=account_result["initial_balance"],
            last_balance_check=account_result["created_at"],
        )
