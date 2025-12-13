"""Password-related endpoints for the XposedOrNot API."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ..models import PasswordCheckResponse
from ..utils import hash_password_keccak512

if TYPE_CHECKING:
    from ..client import XposedOrNot


class PasswordEndpoint:
    """Handles password-related API endpoints."""

    PASSWORD_API_BASE = "https://passwords.xposedornot.com"

    def __init__(self, client: "XposedOrNot"):
        self._client = client

    def check(self, password: str) -> PasswordCheckResponse:
        """Check if a password has been exposed in data breaches.

        This uses an anonymous k-anonymity approach where only the first
        10 characters of the SHA3-512 hash are sent to the API.

        Args:
            password: The password to check.

        Returns:
            PasswordCheckResponse containing exposure count and characteristics.

        Raises:
            NotFoundError: If password is not found in any breaches.
            RateLimitError: If rate limit is exceeded.
        """
        hash_prefix = hash_password_keccak512(password)

        data = self._client._request(
            "GET",
            f"/v1/pass/anon/{hash_prefix}",
            base_url=self.PASSWORD_API_BASE,
        )
        return PasswordCheckResponse.from_api_response(data)
