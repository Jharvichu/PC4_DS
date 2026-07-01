"""Global error handling middleware."""

from fastapi import Request, status
from fastapi.responses import JSONResponse

from app.shared.exceptions import AppException


async def exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Global exception handler for AppException."""
    if isinstance(exc, AppException):
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.message, "error": exc.__class__.__name__},
        )

    # Log unexpected errors
    print(f"Unexpected error: {exc}")

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Internal server error", "error": "InternalServerError"},
    )
