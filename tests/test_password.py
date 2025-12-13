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
    """Tests for the check_password endpoint."""

    @respx.mock
    def test_check_password_found(self) -> None:
        """Test checking a password that has been exposed."""
        # Get the hash prefix for "password123"
        hash_prefix = hash_password_keccak512("password123")

        respx.get(f"https://passwords.xposedornot.com/v1/pass/anon/{hash_prefix}").mock(
            return_value=Response(200, json=SAMPLE_PASSWORD_RESPONSE)
        )

        client = XposedOrNot(rate_limit=False)
        result = client.check_password("password123")

        assert isinstance(result, PasswordCheckResponse)
        assert result.count == 12345
        assert result.anon == "a1b2c3d4e5"
        assert result.characteristics["digits"] == 3
        assert result.characteristics["alphabets"] == 8

    @respx.mock
    def test_check_password_not_found(self) -> None:
        """Test checking a password that hasn't been exposed."""
        hash_prefix = hash_password_keccak512("super-unique-password-xyz123!")

        respx.get(f"https://passwords.xposedornot.com/v1/pass/anon/{hash_prefix}").mock(
            return_value=Response(404, json={"Error": "Not found"})
        )

        client = XposedOrNot(rate_limit=False)

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
