"""Utility functions for the XposedOrNot API client."""

import re

from Crypto.Hash import keccak


def validate_email(email: str) -> bool:
    """Validate email format.

    Args:
        email: Email address to validate.

    Returns:
        True if email format is valid, False otherwise.
    """
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9-]+(\.[a-zA-Z0-9-]+)*\.[a-zA-Z]{2,}$"
    if ".." in email:
        return False
    return bool(re.match(pattern, email))


def hash_password_keccak512(password: str) -> str:
    """Hash a password using original Keccak-512.

    Note: This uses the original Keccak-512 algorithm, NOT SHA3-512 (FIPS 202).
    Python's hashlib.sha3_512 is FIPS 202 which produces different output.

    Args:
        password: The password to hash.

    Returns:
        The first 10 characters of the Keccak-512 hash.
    """
    k = keccak.new(digest_bits=512)
    k.update(password.encode("utf-8"))
    return k.hexdigest()[:10]
