"""User domain routes."""

from datetime import timedelta

from fastapi import APIRouter, Depends, status

from app.core.dependencies import get_user_service, get_current_user
from app.domains.users.schemas import UserCreate, UserResponse, LoginRequest, TokenResponse
from app.domains.users.services import UserService
from app.infrastructure.auth import create_access_token
from app.config import get_settings

router = APIRouter(prefix="/auth", tags=["auth"])
settings = get_settings()


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserCreate,
    service: UserService = Depends(get_user_service),
):
    """Register a new user."""
    return await service.register_user(user_data)


@router.post("/login", response_model=TokenResponse)
async def login(
    credentials: LoginRequest,
    service: UserService = Depends(get_user_service),
):
    """Login user and return access token."""
    user = await service.authenticate_user(credentials.email, credentials.password)

    access_token = create_access_token(
        data={"sub": user.id, "email": user.email},
        expires_delta=timedelta(hours=settings.JWT_EXPIRATION_HOURS),
    )

    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        user=user,
    )


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: UserResponse = Depends(get_current_user),
):
    """Get current authenticated user."""
    return current_user


@router.put("/me", response_model=UserResponse)
async def update_current_user(
    user_data: dict,
    current_user: UserResponse = Depends(get_current_user),
    service: UserService = Depends(get_user_service),
):
    """Update current user."""
    return await service.update_user(current_user.id, user_data)


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: str,
    service: UserService = Depends(get_user_service),
):
    """Get user by ID."""
    return await service.get_user(user_id)
