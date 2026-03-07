class ApplicationError(Exception):
    """Base exception for all application-level errors."""

    def __init__(self, message: str = "An application error occurred.", *, extra: dict | None = None):
        super().__init__(message)
        self.message = message
        self.extra = extra or {}


class NotFoundError(ApplicationError):
    """Raised when a requested resource does not exist."""

    def __init__(self, message: str = "Resource not found.", *, extra: dict | None = None):
        super().__init__(message, extra=extra)


class ValidationError(ApplicationError):
    """Raised when input data fails validation."""

    def __init__(self, message: str = "Validation error.", *, extra: dict | None = None):
        super().__init__(message, extra=extra)


class PermissionDeniedError(ApplicationError):
    """Raised when the user lacks permission for the requested action."""

    def __init__(self, message: str = "Permission denied.", *, extra: dict | None = None):
        super().__init__(message, extra=extra)
