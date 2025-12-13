"""Pytest configuration and fixtures."""

from __future__ import annotations

import pytest
import respx
from httpx import Response

from xposedornot import XposedOrNot


@pytest.fixture
def client() -> XposedOrNot:
    """Create a test client with rate limiting disabled."""
    return XposedOrNot(rate_limit=False)


@pytest.fixture
def mock_api() -> respx.MockRouter:
    """Create a mock API context."""
    with respx.mock(base_url="https://api.xposedornot.com") as respx_mock:
        yield respx_mock


@pytest.fixture
def mock_password_api() -> respx.MockRouter:
    """Create a mock password API context."""
    with respx.mock(base_url="https://passwords.xposedornot.com") as respx_mock:
        yield respx_mock


# Sample API responses for testing
SAMPLE_CHECK_EMAIL_RESPONSE = {"breaches": ["Adobe", "LinkedIn", "Dropbox"]}

SAMPLE_CHECK_EMAIL_NOT_FOUND = {"Error": "Not found"}

SAMPLE_BREACH_ANALYTICS_RESPONSE = {
    "BreachesSummary": {
        "exposures": 5,
        "site": 3,
        "first_breach": "2013-10-04",
    },
    "ExposedBreaches": {
        "breaches_details": [
            {
                "breach": "Adobe",
                "details": "Adobe breach description",
                "domain": "adobe.com",
                "industry": "Technology",
                "logo": "https://example.com/adobe.png",
                "password_risk": "high",
                "references": "https://example.com",
                "searchable": True,
                "verified": True,
                "xposed_data": "email,password",
                "xposed_date": "2013-10-04",
                "xposed_records": 152000000,
            }
        ]
    },
    "BreachMetrics": {
        "industry": [{"name": "Technology", "count": 1}],
        "passwords_strength": [{"name": "weak", "count": 1}],
        "risk": [{"name": "high", "count": 1}],
        "xposed_data": [{"name": "email", "count": 1}],
        "yearwise_details": [{"year": 2013, "count": 1}],
    },
    "PastesSummary": {"cnt": 2},
}

SAMPLE_BREACHES_RESPONSE = {
    "status": "success",
    "message": None,
    "exposedBreaches": [
        {
            "breachID": "adobe",
            "breachedDate": "2013-10-04",
            "domain": "adobe.com",
            "exposedData": ["Email addresses", "Passwords", "Usernames"],
            "exposedRecords": 152000000,
            "exposureDescription": "Adobe breach in 2013",
            "industry": "Technology",
            "logo": "https://example.com/adobe.png",
            "passwordRisk": "high",
            "referenceURL": "https://example.com",
            "searchable": True,
            "sensitive": False,
            "verified": True,
        },
        {
            "breachID": "linkedin",
            "breachedDate": "2012-06-05",
            "domain": "linkedin.com",
            "exposedData": ["Email addresses", "Passwords"],
            "exposedRecords": 164000000,
            "exposureDescription": "LinkedIn breach in 2012",
            "industry": "Social",
            "logo": "https://example.com/linkedin.png",
            "passwordRisk": "high",
            "referenceURL": "https://example.com",
            "searchable": True,
            "sensitive": False,
            "verified": True,
        },
    ]
}

SAMPLE_PASSWORD_RESPONSE = {
    "anon": "a1b2c3d4e5",
    "char": {"digits": 3, "alphabets": 8, "special": 0, "length": 11},
    "count": 12345,
}
