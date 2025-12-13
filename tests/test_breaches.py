"""Tests for breaches endpoint."""

from __future__ import annotations

import respx
from httpx import Response

from xposedornot import XposedOrNot
from xposedornot.models import Breach

from .conftest import SAMPLE_BREACHES_RESPONSE


class TestGetBreaches:
    """Tests for the get_breaches endpoint."""

    @respx.mock
    def test_get_all_breaches(self) -> None:
        """Test getting all breaches."""
        respx.get("https://api.xposedornot.com/v1/breaches").mock(
            return_value=Response(200, json=SAMPLE_BREACHES_RESPONSE)
        )

        client = XposedOrNot(rate_limit=False)
        result = client.get_breaches()

        assert isinstance(result, list)
        assert len(result) == 2
        assert all(isinstance(b, Breach) for b in result)

        # Check first breach
        adobe = result[0]
        assert adobe.breach_id == "adobe"
        assert adobe.domain == "adobe.com"
        assert adobe.exposed_records == 152000000
        assert adobe.industry == "Technology"
        assert adobe.verified is True

        # Check second breach
        linkedin = result[1]
        assert linkedin.breach_id == "linkedin"
        assert linkedin.domain == "linkedin.com"

    @respx.mock
    def test_get_breaches_by_domain(self) -> None:
        """Test filtering breaches by domain."""
        filtered_response = {
            "status": "success",
            "exposedBreaches": [SAMPLE_BREACHES_RESPONSE["exposedBreaches"][0]]
        }
        respx.get(
            "https://api.xposedornot.com/v1/breaches",
            params={"domain": "adobe.com"},
        ).mock(return_value=Response(200, json=filtered_response))

        client = XposedOrNot(rate_limit=False)
        result = client.get_breaches(domain="adobe.com")

        assert len(result) == 1
        assert result[0].domain == "adobe.com"

    @respx.mock
    def test_get_breaches_empty(self) -> None:
        """Test getting breaches when none exist."""
        respx.get("https://api.xposedornot.com/v1/breaches").mock(
            return_value=Response(200, json={"status": "success", "exposedBreaches": []})
        )

        client = XposedOrNot(rate_limit=False)
        result = client.get_breaches()

        assert result == []
