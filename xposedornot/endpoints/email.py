"""Email-related endpoints for the XposedOrNot API."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ..exceptions import ValidationError
from ..models import BreachAnalyticsResponse, EmailBreachDetailedResponse, EmailBreachResponse
from ..utils import validate_email

if TYPE_CHECKING:
    from ..client import XposedOrNot


class EmailEndpoint:
    """Handles email-related API endpoints."""

    PLUS_API_BASE = "https://plus-api.xposedornot.com"

    def __init__(self, client: "XposedOrNot"):
        self._client = client

    def check(self, email: str) -> EmailBreachResponse | EmailBreachDetailedResponse:
        """Check if an email has been exposed in data breaches.

        When an API key is configured, uses the Plus API (plus-api.xposedornot.com)
        which returns detailed breach information. Without an API key, uses the
        free API which returns only breach names.

        Args:
            email: The email address to check.

        Returns:
            EmailBreachDetailedResponse if API key is set (Plus API),
            EmailBreachResponse if no API key (free API).

        Raises:
            ValidationError: If email format is invalid.
            NotFoundError: If email is not found in any breaches.
            RateLimitError: If rate limit is exceeded.
            AuthenticationError: If API key is invalid (Plus API only).
        """
        if not validate_email(email):
            raise ValidationError(f"Invalid email format: {email}")

        if self._client._api_key:
            # Use Plus API for authenticated requests
            data = self._client._request(
                "GET",
                f"/v3/check-email/{email}",
                params={"detailed": "true"},
                base_url=self.PLUS_API_BASE,
            )
            return EmailBreachDetailedResponse.from_api_response(data)
        else:
            # Use free API for unauthenticated requests
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
