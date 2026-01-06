"""Pytest configuration and fixtures."""

from __future__ import annotations

import pytest
import respx
from httpx import Response

from xposedornot import XposedOrNot


@pytest.fixture
def client() -> XposedOrNot:
    """Create a test client."""
    return XposedOrNot()


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


@pytest.fixture
def mock_plus_api() -> respx.MockRouter:
    """Create a mock Plus API context."""
    with respx.mock(base_url="https://plus-api.xposedornot.com") as respx_mock:
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

# Plus API (xonPlus) sample responses
SAMPLE_PLUS_CHECK_EMAIL_RESPONSE = {
    "status": "success",
    "email": "test@example.com",
    "breaches": [
        {
            "breach_id": "Poshmark",
            "breached_date": "2018-05-01T00:00:00+00:00",
            "logo": "https://xposedornot.com/static/logos/Poshmark.png",
            "password_risk": "hardtocrack",
            "searchable": "Yes",
            "xposed_data": "Email addresses;Usernames;Passwords",
            "xposed_records": 36758793,
            "xposure_desc": "Poshmark suffered a data breach in 2019.",
            "domain": "poshmark.com",
            "seniority": None,
        },
        {
            "breach_id": "Adobe",
            "breached_date": "2013-10-04T00:00:00+00:00",
            "logo": "https://xposedornot.com/static/logos/Adobe.png",
            "password_risk": "easytocrack",
            "searchable": "Yes",
            "xposed_data": "Email addresses;Passwords;Password hints",
            "xposed_records": 152000000,
            "xposure_desc": "Adobe breach exposed millions of users.",
            "domain": "adobe.com",
            "seniority": None,
        },
    ],
}

SAMPLE_PLUS_CHECK_EMAIL_NOT_FOUND = {
    "detail": {"status": "error", "message": "Email not found in any breaches"}
}

SAMPLE_PLUS_INVALID_API_KEY = {
    "detail": {"status": "error", "message": "Invalid API key"}
}

SAMPLE_PLUS_INVALID_EMAIL = {
    "detail": {"status": "error", "message": "Invalid email format"}
}
