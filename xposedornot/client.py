"""Main client for the XposedOrNot API."""

from __future__ import annotations

import time
from typing import Any

import httpx

from .endpoints import BreachesEndpoint, EmailEndpoint, PasswordEndpoint
from .exceptions import (
    APIError,
    AuthenticationError,
    NotFoundError,
    RateLimitError,
    ServerError,
)
from .models import (
    Breach,
    BreachAnalyticsResponse,
    EmailBreachResponse,
    PasswordCheckResponse,
)


class XposedOrNot:
    """Client for interacting with the XposedOrNot API.

    Example:
        >>> from xposedornot import XposedOrNot
        >>> xon = XposedOrNot()
        >>> result = xon.check_email("test@example.com")
        >>> print(result.breaches)
    """

    DEFAULT_BASE_URL = "https://api.xposedornot.com"
    DEFAULT_TIMEOUT = 30.0
    RATE_LIMIT_DELAY = 1.0  # 1 request per second

    def __init__(
        self,
        api_key: str | None = None,
        base_url: str | None = None,
        timeout: float | None = None,
        rate_limit: bool = True,
    ):
        """Initialize the XposedOrNot client.

        Args:
            api_key: Optional API key for authenticated endpoints.
            base_url: Optional custom base URL for the API.
            timeout: Request timeout in seconds. Defaults to 30.
            rate_limit: Whether to enforce rate limiting. Defaults to True.
        """
        self._api_key = api_key
        self._base_url = base_url or self.DEFAULT_BASE_URL
        self._timeout = timeout or self.DEFAULT_TIMEOUT
        self._rate_limit = rate_limit
        self._last_request_time: float = 0

        self._client = httpx.Client(timeout=self._timeout)

        # Initialize endpoint handlers
        self._email = EmailEndpoint(self)
        self._breaches = BreachesEndpoint(self)
        self._password = PasswordEndpoint(self)

    def __enter__(self) -> "XposedOrNot":
        return self

    def __exit__(self, *args: Any) -> None:
        self.close()

    def close(self) -> None:
        """Close the HTTP client."""
        self._client.close()

    def _wait_for_rate_limit(self) -> None:
        """Wait if necessary to respect rate limits."""
        if not self._rate_limit:
            return

        elapsed = time.time() - self._last_request_time
        if elapsed < self.RATE_LIMIT_DELAY:
            time.sleep(self.RATE_LIMIT_DELAY - elapsed)

    def _request(
        self,
        method: str,
        path: str,
        params: dict[str, Any] | None = None,
        base_url: str | None = None,
    ) -> dict[str, Any]:
        """Make an HTTP request to the API.

        Args:
            method: HTTP method (GET, POST, etc.).
            path: API endpoint path.
            params: Optional query parameters.
            base_url: Optional override for base URL.

        Returns:
            JSON response as a dictionary.

        Raises:
            NotFoundError: If resource is not found.
            RateLimitError: If rate limit is exceeded.
            AuthenticationError: If authentication fails.
            ServerError: If server returns 5xx error.
            APIError: For other API errors.
        """
        self._wait_for_rate_limit()

        url = f"{base_url or self._base_url}{path}"
        headers = {}

        if self._api_key:
            headers["x-api-key"] = self._api_key

        try:
            response = self._client.request(method, url, params=params, headers=headers)
            self._last_request_time = time.time()

            if response.status_code == 404:
                raise NotFoundError("Resource not found")

            if response.status_code == 429:
                raise RateLimitError()

            if response.status_code == 401:
                raise AuthenticationError()

            if response.status_code >= 500:
                raise ServerError(
                    f"Server error: {response.status_code}",
                    status_code=response.status_code,
                )

            if response.status_code >= 400:
                raise APIError(f"API error: {response.text}", status_code=response.status_code)

            return response.json()

        except httpx.RequestError as e:
            raise APIError(f"Request failed: {str(e)}")

    # Convenience methods that delegate to endpoint handlers

    def check_email(self, email: str) -> EmailBreachResponse:
        """Check if an email has been exposed in data breaches.

        Args:
            email: The email address to check.

        Returns:
            EmailBreachResponse containing list of breaches.
        """
        return self._email.check(email)

    def breach_analytics(self, email: str) -> BreachAnalyticsResponse:
        """Get detailed breach analytics for an email.

        Args:
            email: The email address to analyze.

        Returns:
            BreachAnalyticsResponse with detailed breach information.
        """
        return self._email.analytics(email)

    def get_breaches(self, domain: str | None = None) -> list[Breach]:
        """Get a list of all known data breaches.

        Args:
            domain: Optional domain to filter breaches by.

        Returns:
            List of Breach objects.
        """
        return self._breaches.list(domain=domain)

    def check_password(self, password: str) -> PasswordCheckResponse:
        """Check if a password has been exposed in data breaches.

        Uses k-anonymity to protect the password.

        Args:
            password: The password to check.

        Returns:
            PasswordCheckResponse with exposure information.
        """
        return self._password.check(password)
