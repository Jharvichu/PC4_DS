"""Custom application exceptions."""


class AppException(Exception):
    """Base exception for application."""

    def __init__(self, message: str, status_code: int = 500):
        self.message = message
        self.status_code = status_code
        super().__init__(message)


class NotFoundError(AppException):
    """Resource not found."""

    def __init__(self, message: str = "Resource not found"):
        super().__init__(message, status_code=404)


class ValidationError(AppException):
    """Validation failed."""

    def __init__(self, message: str = "Validation failed"):
        super().__init__(message, status_code=422)


class UnauthorizedError(AppException):
    """User is not authenticated."""

    def __init__(self, message: str = "Unauthorized"):
        super().__init__(message, status_code=401)


class ForbiddenError(AppException):
    """User does not have permission."""

    def __init__(self, message: str = "Forbidden"):
        super().__init__(message, status_code=403)


class ConflictError(AppException):
    """Resource already exists."""

    def __init__(self, message: str = "Conflict"):
        super().__init__(message, status_code=409)


class BusinessLogicError(AppException):
    """Business logic violation."""

    def __init__(self, message: str = "Business logic error"):
        super().__init__(message, status_code=400)
