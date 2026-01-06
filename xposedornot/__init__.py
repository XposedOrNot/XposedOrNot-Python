"""XposedOrNot API Client.

A Python client for the XposedOrNot API to check for data breaches
and exposed credentials.

Example:
    >>> from xposedornot import XposedOrNot
    >>> xon = XposedOrNot()
    >>> result = xon.check_email("test@example.com")
    >>> print(result.breaches)
"""

from .client import XposedOrNot
from .exceptions import (
    APIError,
    AuthenticationError,
    NotFoundError,
    RateLimitError,
    ServerError,
    ValidationError,
    XposedOrNotError,
)
from .models import (
    Breach,
    BreachAnalyticsResponse,
    BreachDetails,
    BreachInfo,
    BreachMetrics,
    EmailBreachDetailedResponse,
    EmailBreachResponse,
    PasswordCheckResponse,
)

__version__ = "1.0.0"

__all__ = [
    # Client
    "XposedOrNot",
    # Exceptions
    "XposedOrNotError",
    "APIError",
    "NotFoundError",
    "RateLimitError",
    "AuthenticationError",
    "ServerError",
    "ValidationError",
    # Models
    "EmailBreachResponse",
    "EmailBreachDetailedResponse",
    "BreachInfo",
    "BreachAnalyticsResponse",
    "BreachDetails",
    "BreachMetrics",
    "Breach",
    "PasswordCheckResponse",
]
