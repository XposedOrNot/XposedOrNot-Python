"""Tests for password endpoint."""

from __future__ import annotations

import pytest
import respx
from httpx import Response

from xposedornot import XposedOrNot, NotFoundError
from xposedornot.models import PasswordCheckResponse
from xposedornot.utils import hash_password_keccak512

from .conftest import SAMPLE_PASSWORD_RESPONSE


class TestCheckPassword:
    """Tests for the check_password endpoint.

    Note: The password is NEVER sent to the API. It is hashed locally
    using SHA3-512 (Keccak), and only the first 10 characters of the
    hash are sent for k-anonymity lookup.
    """

    @respx.mock
    def test_check_password_found(self) -> None:
        """Test checking a password that has been exposed.

        The password is hashed locally using Keccak-512 - only the first 10 chars
        of the hash prefix are sent to the API, never the password itself.
        """
        # Get the hash prefix for "password123" - this is what gets sent, not the password
        hash_prefix = hash_password_keccak512("password123")

        respx.get(f"https://passwords.xposedornot.com/api/v1/pass/anon/{hash_prefix}").mock(
            return_value=Response(200, json=SAMPLE_PASSWORD_RESPONSE)
        )

        client = XposedOrNot()
        result = client.check_password("password123")

        assert isinstance(result, PasswordCheckResponse)
        assert result.count == 12345
        assert result.anon == "aa77c1b9b7"
        assert result.characteristics["digits"] == 3
        assert result.characteristics["alphabets"] == 8

    @respx.mock
    def test_check_password_not_found(self) -> None:
        """Test checking a password that hasn't been exposed."""
        hash_prefix = hash_password_keccak512("super-unique-password-xyz123!")

        respx.get(f"https://passwords.xposedornot.com/api/v1/pass/anon/{hash_prefix}").mock(
            return_value=Response(404, json={"Error": "Not found"})
        )

        client = XposedOrNot()

        with pytest.raises(NotFoundError):
            client.check_password("super-unique-password-xyz123!")


class TestPasswordHashing:
    """Tests for password hashing utility."""

    def test_hash_password_consistency(self) -> None:
        """Test that the same password always produces the same hash prefix."""
        password = "testpassword"
        hash1 = hash_password_keccak512(password)
        hash2 = hash_password_keccak512(password)

        assert hash1 == hash2
        assert len(hash1) == 10  # First 10 characters

    def test_hash_password_different_inputs(self) -> None:
        """Test that different passwords produce different hashes."""
        hash1 = hash_password_keccak512("password1")
        hash2 = hash_password_keccak512("password2")

        assert hash1 != hash2

    def test_hash_password_empty(self) -> None:
        """Test hashing an empty password."""
        hash_result = hash_password_keccak512("")
        assert len(hash_result) == 10
        assert hash_result.isalnum()
