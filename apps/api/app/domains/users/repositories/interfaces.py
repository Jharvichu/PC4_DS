"""User repository interfaces (DIP - Dependency Inversion Principle)."""

from abc import ABC, abstractmethod
from typing import Optional

from app.domains.users.models import User
from app.domains.users.schemas import UserCreate


class IUserRepository(ABC):
    """Interface for user repository operations."""

    @abstractmethod
    async def get_by_id(self, user_id: str) -> Optional[User]:
        """Get user by ID."""
        pass

    @abstractmethod
    async def get_by_email(self, email: str) -> Optional[User]:
        """Get user by email."""
        pass

    @abstractmethod
    async def get_by_username(self, username: str) -> Optional[User]:
        """Get user by username."""
        pass

    @abstractmethod
    async def create(self, user: UserCreate, password_hash: str) -> User:
        """Create a new user."""
        pass

    @abstractmethod
    async def update(self, user_id: str, data: dict) -> Optional[User]:
        """Update user data."""
        pass

    @abstractmethod
    async def exists_by_email(self, email: str) -> bool:
        """Check if user exists by email."""
        pass

    @abstractmethod
    async def exists_by_username(self, username: str) -> bool:
        """Check if user exists by username."""
        pass
