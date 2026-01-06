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
    EmailBreachDetailedResponse,
    EmailBreachResponse,
    PasswordCheckResponse,
)


class XposedOrNot:
    """Client for interacting with the XposedOrNot API.

    The free API has rate limits of 1 request/second, plus hourly and daily limits.
    For higher rate limits, commercial plans are available at:
    https://plus.xposedornot.com/products/api

    Example:
        >>> from xposedornot import XposedOrNot
        >>> xon = XposedOrNot()
        >>> result = xon.check_email("test@example.com")
        >>> print(result.breaches)
    """

    DEFAULT_BASE_URL = "https://api.xposedornot.com"
    DEFAULT_TIMEOUT = 30.0
    RATE_LIMIT_DELAY = 1.0  # 1 request per second for free API
    MAX_RETRIES = 3  # Max retries on 429
    RETRY_BASE_DELAY = 1.0  # Base delay for exponential backoff

    def __init__(
        self,
        api_key: str | None = None,
        base_url: str | None = None,
        timeout: float | None = None,
    ):
        """Initialize the XposedOrNot client.

        Args:
            api_key: API key from console.xposedornot.com for Plus API access.
                     When provided, check_email() uses the Plus API with
                     detailed breach information and higher rate limits.
            base_url: Optional custom base URL for the API.
            timeout: Request timeout in seconds. Defaults to 30.
        """
        self._api_key = api_key
        self._base_url = base_url or self.DEFAULT_BASE_URL
        self._timeout = timeout or self.DEFAULT_TIMEOUT
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
        """Wait if necessary to respect API rate limits.

        Rate limiting is only applied for free API (no API key).
        Plus API users have tier-based limits handled by the server.
        """
        # Skip rate limiting for Plus API users - they have their own tier-based limits
        if self._api_key:
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

        Automatically retries with exponential backoff on 429 (rate limit) errors.

        Args:
            method: HTTP method (GET, POST, etc.).
            path: API endpoint path.
            params: Optional query parameters.
            base_url: Optional override for base URL.

        Returns:
            JSON response as a dictionary.

        Raises:
            NotFoundError: If resource is not found.
            RateLimitError: If rate limit is exceeded after all retries.
            AuthenticationError: If authentication fails.
            ServerError: If server returns 5xx error.
            APIError: For other API errors.
        """
        self._wait_for_rate_limit()

        url = f"{base_url or self._base_url}{path}"
        headers = {}

        if self._api_key:
            headers["x-api-key"] = self._api_key

        last_exception: RateLimitError | None = None

        for attempt in range(self.MAX_RETRIES + 1):
            try:
                response = self._client.request(method, url, params=params, headers=headers)
                self._last_request_time = time.time()

                if response.status_code == 404:
                    raise NotFoundError("Resource not found")

                if response.status_code == 429:
                    last_exception = RateLimitError()
                    if attempt < self.MAX_RETRIES:
                        # Exponential backoff: 1s, 2s, 4s
                        delay = self.RETRY_BASE_DELAY * (2 ** attempt)
                        time.sleep(delay)
                        continue
                    raise last_exception

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

        # Should not reach here, but just in case
        if last_exception:
            raise last_exception
        raise APIError("Request failed after retries")

    # Convenience methods that delegate to endpoint handlers

    def check_email(self, email: str) -> EmailBreachResponse | EmailBreachDetailedResponse:
        """Check if an email has been exposed in data breaches.

        When an API key is configured, uses the Plus API (plus-api.xposedornot.com)
        which returns detailed breach information with higher rate limits.
        Without an API key, uses the free API which returns only breach names.

        Args:
            email: The email address to check.

        Returns:
            EmailBreachDetailedResponse if API key is set (Plus API),
            EmailBreachResponse if no API key (free API).
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

        SECURITY: Your password is NEVER sent over the network.
        This method uses k-anonymity protection:
        1. The password is hashed locally using SHA3-512 (Keccak)
        2. Only the first 10 characters of the hash are sent to the API
        3. The API returns matches for that hash prefix
        4. Your actual password never leaves your machine

        Args:
            password: The password to check (hashed locally, never transmitted).

        Returns:
            PasswordCheckResponse with exposure count and characteristics.
        """
        return self._password.check(password)
