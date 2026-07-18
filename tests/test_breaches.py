"""Tests for breaches endpoint."""

from __future__ import annotations

import pytest
import respx
from httpx import Response

from xposedornot import AuthenticationError, XposedOrNot
from xposedornot.models import Breach, DomainBreachesResponse

from .conftest import SAMPLE_BREACHES_RESPONSE, SAMPLE_DOMAIN_BREACHES_RESPONSE


class TestGetBreaches:
    """Tests for the get_breaches endpoint."""

    @respx.mock
    def test_get_all_breaches(self) -> None:
        """Test getting all breaches."""
        respx.get("https://api.xposedornot.com/v1/breaches").mock(
            return_value=Response(200, json=SAMPLE_BREACHES_RESPONSE)
        )

        client = XposedOrNot()
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
            "exposedBreaches": [SAMPLE_BREACHES_RESPONSE["exposedBreaches"][0]],
        }
        respx.get(
            "https://api.xposedornot.com/v1/breaches",
            params={"domain": "adobe.com"},
        ).mock(return_value=Response(200, json=filtered_response))

        client = XposedOrNot()
        result = client.get_breaches(domain="adobe.com")

        assert len(result) == 1
        assert result[0].domain == "adobe.com"

    @respx.mock
    def test_get_breaches_by_breach_id(self) -> None:
        """Test fetching a specific breach by ID."""
        filtered_response = {
            "status": "success",
            "exposedBreaches": [SAMPLE_BREACHES_RESPONSE["exposedBreaches"][0]],
        }
        route = respx.get(
            "https://api.xposedornot.com/v1/breaches",
            params={"breach_id": "adobe"},
        ).mock(return_value=Response(200, json=filtered_response))

        client = XposedOrNot()
        result = client.get_breaches(breach_id="adobe")

        assert route.called
        assert len(result) == 1
        assert result[0].breach_id == "adobe"

    @respx.mock
    def test_get_breaches_empty(self) -> None:
        """Test getting breaches when none exist."""
        respx.get("https://api.xposedornot.com/v1/breaches").mock(
            return_value=Response(200, json={"status": "success", "exposedBreaches": []})
        )

        client = XposedOrNot()
        result = client.get_breaches()

        assert result == []


class TestDomainBreaches:
    """Tests for the get_domain_breaches endpoint."""

    @respx.mock
    def test_domain_breaches_success(self) -> None:
        """Test getting domain breaches with an API key."""
        route = respx.post("https://api.xposedornot.com/v1/domain-breaches").mock(
            return_value=Response(200, json=SAMPLE_DOMAIN_BREACHES_RESPONSE)
        )

        client = XposedOrNot(api_key="test-api-key")
        result = client.get_domain_breaches()

        assert route.called
        request = route.calls[0].request
        assert request.headers.get("x-api-key") == "test-api-key"

        assert isinstance(result, DomainBreachesResponse)
        assert result.status == "success"
        assert result.yearly_metrics == {"2013": 1, "2012": 1}
        assert result.domain_summary == {"example.com": 2}
        assert result.breach_summary == {"Adobe": 1, "LinkedIn": 1}
        assert result.top10_breaches == {"Adobe": 152000000, "LinkedIn": 164000000}
        assert "Adobe" in result.detailed_breach_info

        assert len(result.breaches_details) == 2
        first = result.breaches_details[0]
        assert first.email == "alice@example.com"
        assert first.domain == "example.com"
        assert first.breach == "Adobe"

    def test_domain_breaches_without_api_key(self) -> None:
        """Test that calling without an API key raises AuthenticationError."""
        client = XposedOrNot()

        with pytest.raises(AuthenticationError) as exc_info:
            client.get_domain_breaches()

        assert "API key is required" in str(exc_info.value)

    @respx.mock
    def test_domain_breaches_invalid_api_key(self) -> None:
        """Test handling of invalid API key."""
        respx.post("https://api.xposedornot.com/v1/domain-breaches").mock(
            return_value=Response(401, json={"Error": "Unauthorized"})
        )

        client = XposedOrNot(api_key="invalid-key")

        with pytest.raises(AuthenticationError):
            client.get_domain_breaches()
