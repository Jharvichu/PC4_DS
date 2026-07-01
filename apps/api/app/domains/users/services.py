"""User domain services (Business Logic - SRP)."""

from typing import Optional

from app.domains.users.repositories import UserRepository
from app.domains.users.schemas import UserCreate, UserResponse, LoginRequest
from app.infrastructure.auth import get_password_hash, verify_password
from app.shared.exceptions import NotFoundError, ValidationError, ConflictError


class UserService:
    """User service for business logic."""

    def __init__(self, repository: UserRepository):
        self.repository = repository

    async def register_user(self, user_data: UserCreate) -> UserResponse:
        """Register a new user."""
        # Validate email doesn't exist
        if await self.repository.exists_by_email(user_data.email):
            raise ConflictError("Email already registered")

        # Validate username doesn't exist
        if await self.repository.exists_by_username(user_data.username):
            raise ConflictError("Username already taken")

        # Hash password and create user
        password_hash = get_password_hash(user_data.password)
        db_user = await self.repository.create(user_data, password_hash)

        return UserResponse.from_orm(db_user)

    async def authenticate_user(self, email: str, password: str) -> Optional[UserResponse]:
        """Authenticate a user by email and password."""
        user = await self.repository.get_by_email(email)

        if not user:
            raise NotFoundError("User not found")

        if not verify_password(password, user.password_hash):
            raise ValidationError("Invalid password")

        return UserResponse.from_orm(user)

    async def get_user(self, user_id: str) -> UserResponse:
        """Get user by ID."""
        user = await self.repository.get_by_id(user_id)

        if not user:
            raise NotFoundError(f"User {user_id} not found")

        return UserResponse.from_orm(user)

    async def update_user(self, user_id: str, data: dict) -> UserResponse:
        """Update user data."""
        user = await self.repository.update(user_id, data)

        if not user:
            raise NotFoundError(f"User {user_id} not found")

        return UserResponse.from_orm(user)
