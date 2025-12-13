"""Tests for utility functions."""

from __future__ import annotations

import pytest

from xposedornot.utils import validate_email, hash_password_keccak512


class TestValidateEmail:
    """Tests for email validation."""

    @pytest.mark.parametrize(
        "email",
        [
            "test@example.com",
            "user.name@domain.org",
            "user+tag@example.co.uk",
            "firstname.lastname@company.com",
            "email@subdomain.domain.com",
            "1234567890@example.com",
            "email@domain-one.com",
            "_______@example.com",
        ],
    )
    def test_valid_emails(self, email: str) -> None:
        """Test that valid emails pass validation."""
        assert validate_email(email) is True

    @pytest.mark.parametrize(
        "email",
        [
            "",
            "plainaddress",
            "@missinglocal.com",
            "missing@.com",
            "missing@domain",
            "spaces in@email.com",
            "email@domain..com",
        ],
    )
    def test_invalid_emails(self, email: str) -> None:
        """Test that invalid emails fail validation."""
        assert validate_email(email) is False


class TestHashPassword:
    """Tests for password hashing."""

    def test_hash_returns_10_chars(self) -> None:
        """Test that hash returns exactly 10 characters."""
        result = hash_password_keccak512("anypassword")
        assert len(result) == 10

    def test_hash_is_hexadecimal(self) -> None:
        """Test that hash contains only hexadecimal characters."""
        result = hash_password_keccak512("testpassword")
        assert all(c in "0123456789abcdef" for c in result)

    def test_hash_deterministic(self) -> None:
        """Test that hashing is deterministic."""
        password = "mypassword123"
        assert hash_password_keccak512(password) == hash_password_keccak512(password)

    def test_hash_different_passwords(self) -> None:
        """Test that different passwords produce different hashes."""
        hash1 = hash_password_keccak512("password1")
        hash2 = hash_password_keccak512("password2")
        hash3 = hash_password_keccak512("Password1")  # Case sensitive

        assert hash1 != hash2
        assert hash1 != hash3
        assert hash2 != hash3

    def test_hash_unicode_password(self) -> None:
        """Test hashing passwords with unicode characters."""
        result = hash_password_keccak512("пароль123")
        assert len(result) == 10
        assert all(c in "0123456789abcdef" for c in result)

    def test_hash_special_characters(self) -> None:
        """Test hashing passwords with special characters."""
        result = hash_password_keccak512("p@$$w0rd!#%^&*()")
        assert len(result) == 10
