"""Utility functions for the XposedOrNot API client."""

import hashlib
import re


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
    """Hash a password using SHA3-Keccak-512.

    Args:
        password: The password to hash.

    Returns:
        The first 10 characters of the SHA3-512 (Keccak) hash.
    """
    # Python's hashlib sha3_512 is the FIPS 202 SHA3, not Keccak
    # For the XposedOrNot API, we use SHA3-512 which is available in hashlib
    hash_obj = hashlib.sha3_512(password.encode("utf-8"))
    full_hash = hash_obj.hexdigest()
    return full_hash[:10]
