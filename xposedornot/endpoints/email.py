"""Email-related endpoints for the XposedOrNot API."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ..exceptions import ValidationError
from ..models import BreachAnalyticsResponse, EmailBreachResponse
from ..utils import validate_email

if TYPE_CHECKING:
    from ..client import XposedOrNot


class EmailEndpoint:
    """Handles email-related API endpoints."""

    def __init__(self, client: "XposedOrNot"):
        self._client = client

    def check(self, email: str) -> EmailBreachResponse:
        """Check if an email has been exposed in data breaches.

        Args:
            email: The email address to check.

        Returns:
            EmailBreachResponse containing list of breaches.

        Raises:
            ValidationError: If email format is invalid.
            NotFoundError: If email is not found in any breaches.
            RateLimitError: If rate limit is exceeded.
        """
        if not validate_email(email):
            raise ValidationError(f"Invalid email format: {email}")

        data = self._client._request("GET", f"/v1/check-email/{email}")
        return EmailBreachResponse.from_api_response(data)

    def analytics(self, email: str) -> BreachAnalyticsResponse:
        """Get detailed breach analytics for an email.

        Args:
            email: The email address to analyze.

        Returns:
            BreachAnalyticsResponse containing detailed breach information
            and metrics.

        Raises:
            ValidationError: If email format is invalid.
            NotFoundError: If email is not found in any breaches.
            RateLimitError: If rate limit is exceeded.
        """
        if not validate_email(email):
            raise ValidationError(f"Invalid email format: {email}")

        data = self._client._request("GET", "/v1/breach-analytics", params={"email": email})
        return BreachAnalyticsResponse.from_api_response(data)
