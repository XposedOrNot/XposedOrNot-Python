"""Password-related endpoints for the XposedOrNot API.

SECURITY NOTE: Passwords are NEVER sent in clear text.
This module uses k-anonymity to check password exposure without
revealing the actual password to the API server.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from ..models import PasswordCheckResponse
from ..utils import hash_password_keccak512

if TYPE_CHECKING:
    from ..client import XposedOrNot


class PasswordEndpoint:
    """Handles password-related API endpoints using k-anonymity.

    SECURITY: Your password is never transmitted over the network.
    Only a partial hash (first 10 chars of SHA3-512) is sent to the API.
    """

    PASSWORD_API_BASE = "https://passwords.xposedornot.com"

    def __init__(self, client: "XposedOrNot"):
        self._client = client

    def check(self, password: str) -> PasswordCheckResponse:
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
            PasswordCheckResponse containing exposure count and characteristics.

        Raises:
            NotFoundError: If password hash prefix is not found.
            RateLimitError: If rate limit is exceeded.
        """
        # Hash password locally - only the hash prefix is sent, never the password
        hash_prefix = hash_password_keccak512(password)

        data = self._client._request(
            "GET",
            f"/v1/pass/anon/{hash_prefix}",
            base_url=self.PASSWORD_API_BASE,
        )
        return PasswordCheckResponse.from_api_response(data)
