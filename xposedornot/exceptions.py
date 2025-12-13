"""Custom exceptions for the XposedOrNot API client."""

from __future__ import annotations


class XposedOrNotError(Exception):
    """Base exception for all XposedOrNot errors."""

    pass


class APIError(XposedOrNotError):
    """Base exception for API-related errors."""

    def __init__(self, message: str, status_code: int | None = None):
        super().__init__(message)
        self.status_code = status_code


class NotFoundError(APIError):
    """Raised when the requested resource is not found (404)."""

    def __init__(self, message: str = "Resource not found"):
        super().__init__(message, status_code=404)


class RateLimitError(APIError):
    """Raised when the API rate limit is exceeded (429)."""

    def __init__(self, message: str = "Rate limit exceeded. Please wait before retrying."):
        super().__init__(message, status_code=429)


class AuthenticationError(APIError):
    """Raised when authentication fails (401)."""

    def __init__(self, message: str = "Invalid or unauthorized API key"):
        super().__init__(message, status_code=401)


class ServerError(APIError):
    """Raised when the server encounters an error (5xx)."""

    def __init__(self, message: str = "Server error occurred", status_code: int = 500):
        super().__init__(message, status_code=status_code)


class ValidationError(XposedOrNotError):
    """Raised when input validation fails."""

    pass
