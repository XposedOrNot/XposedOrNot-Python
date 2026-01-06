"""Tests for email-related endpoints."""

from __future__ import annotations

import pytest
import respx
from httpx import Response

from xposedornot import XposedOrNot, NotFoundError, ValidationError, AuthenticationError
from xposedornot.models import EmailBreachResponse, EmailBreachDetailedResponse, BreachAnalyticsResponse

from .conftest import (
    SAMPLE_CHECK_EMAIL_RESPONSE,
    SAMPLE_BREACH_ANALYTICS_RESPONSE,
    SAMPLE_PLUS_CHECK_EMAIL_RESPONSE,
    SAMPLE_PLUS_INVALID_API_KEY,
)


class TestCheckEmail:
    """Tests for the check_email endpoint."""

    @respx.mock
    def test_check_email_found(self) -> None:
        """Test checking an email that exists in breaches."""
        respx.get("https://api.xposedornot.com/v1/check-email/test@example.com").mock(
            return_value=Response(200, json=SAMPLE_CHECK_EMAIL_RESPONSE)
        )

        client = XposedOrNot()
        result = client.check_email("test@example.com")

        assert isinstance(result, EmailBreachResponse)
        assert result.breaches == ["Adobe", "LinkedIn", "Dropbox"]
        assert len(result.breaches) == 3

    @respx.mock
    def test_check_email_not_found(self) -> None:
        """Test checking an email that doesn't exist in breaches."""
        respx.get("https://api.xposedornot.com/v1/check-email/clean@example.com").mock(
            return_value=Response(404, json={"Error": "Not found"})
        )

        client = XposedOrNot()

        with pytest.raises(NotFoundError):
            client.check_email("clean@example.com")

    def test_check_email_invalid_format(self) -> None:
        """Test checking an invalid email format."""
        client = XposedOrNot()

        with pytest.raises(ValidationError) as exc_info:
            client.check_email("not-an-email")

        assert "Invalid email format" in str(exc_info.value)

    def test_check_email_empty(self) -> None:
        """Test checking an empty email."""
        client = XposedOrNot()

        with pytest.raises(ValidationError):
            client.check_email("")


class TestBreachAnalytics:
    """Tests for the breach_analytics endpoint."""

    @respx.mock
    def test_breach_analytics_success(self) -> None:
        """Test getting breach analytics for an email."""
        respx.get(
            "https://api.xposedornot.com/v1/breach-analytics",
            params={"email": "test@example.com"},
        ).mock(return_value=Response(200, json=SAMPLE_BREACH_ANALYTICS_RESPONSE))

        client = XposedOrNot()
        result = client.breach_analytics("test@example.com")

        assert isinstance(result, BreachAnalyticsResponse)
        assert result.exposures_count == 5
        assert result.breaches_count == 3
        assert result.first_breach == "2013-10-04"
        assert result.pastes_count == 2
        assert len(result.breaches_details) == 1

        # Check breach details
        breach = result.breaches_details[0]
        assert breach.breach == "Adobe"
        assert breach.domain == "adobe.com"
        assert breach.xposed_records == 152000000
        assert breach.verified is True

        # Check metrics
        assert result.metrics is not None
        assert len(result.metrics.industry) == 1

    @respx.mock
    def test_breach_analytics_not_found(self) -> None:
        """Test analytics for an email not in breaches."""
        respx.get(
            "https://api.xposedornot.com/v1/breach-analytics",
            params={"email": "clean@example.com"},
        ).mock(return_value=Response(404, json={"Error": "Not found"}))

        client = XposedOrNot()

        with pytest.raises(NotFoundError):
            client.breach_analytics("clean@example.com")

    def test_breach_analytics_invalid_email(self) -> None:
        """Test analytics with invalid email format."""
        client = XposedOrNot()

        with pytest.raises(ValidationError):
            client.breach_analytics("invalid-email")


class TestCheckEmailPlus:
    """Tests for the Plus API check_email endpoint (with API key)."""

    @respx.mock
    def test_check_email_with_api_key_uses_plus_api(self) -> None:
        """Test that providing an API key uses the Plus API endpoint."""
        route = respx.get(
            "https://plus-api.xposedornot.com/v3/check-email/test@example.com",
            params={"detailed": "true"},
        ).mock(return_value=Response(200, json=SAMPLE_PLUS_CHECK_EMAIL_RESPONSE))

        client = XposedOrNot(api_key="test-api-key")
        result = client.check_email("test@example.com")

        assert route.called
        request = route.calls[0].request
        assert request.headers.get("x-api-key") == "test-api-key"

        assert isinstance(result, EmailBreachDetailedResponse)
        assert result.status == "success"
        assert result.email == "test@example.com"
        assert len(result.breaches) == 2

    @respx.mock
    def test_check_email_plus_breach_details(self) -> None:
        """Test that Plus API returns detailed breach information."""
        respx.get(
            "https://plus-api.xposedornot.com/v3/check-email/test@example.com",
            params={"detailed": "true"},
        ).mock(return_value=Response(200, json=SAMPLE_PLUS_CHECK_EMAIL_RESPONSE))

        client = XposedOrNot(api_key="test-api-key")
        result = client.check_email("test@example.com")

        assert isinstance(result, EmailBreachDetailedResponse)

        # Check first breach details
        breach = result.breaches[0]
        assert breach.breach_id == "Poshmark"
        assert breach.domain == "poshmark.com"
        assert breach.password_risk == "hardtocrack"
        assert breach.xposed_records == 36758793
        assert "Poshmark" in breach.xposure_desc

        # Check second breach
        breach2 = result.breaches[1]
        assert breach2.breach_id == "Adobe"
        assert breach2.xposed_records == 152000000

    @respx.mock
    def test_check_email_plus_invalid_api_key(self) -> None:
        """Test handling of invalid API key error."""
        respx.get(
            "https://plus-api.xposedornot.com/v3/check-email/test@example.com",
            params={"detailed": "true"},
        ).mock(return_value=Response(401, json=SAMPLE_PLUS_INVALID_API_KEY))

        client = XposedOrNot(api_key="invalid-key")

        with pytest.raises(AuthenticationError):
            client.check_email("test@example.com")

    @respx.mock
    def test_check_email_plus_not_found(self) -> None:
        """Test handling of email not found in Plus API."""
        respx.get(
            "https://plus-api.xposedornot.com/v3/check-email/clean@example.com",
            params={"detailed": "true"},
        ).mock(return_value=Response(404, json={"detail": {"status": "error", "message": "Not found"}}))

        client = XposedOrNot(api_key="test-api-key")

        with pytest.raises(NotFoundError):
            client.check_email("clean@example.com")

    def test_check_email_plus_invalid_email_format(self) -> None:
        """Test validation error for invalid email with API key."""
        client = XposedOrNot(api_key="test-api-key")

        with pytest.raises(ValidationError) as exc_info:
            client.check_email("not-an-email")

        assert "Invalid email format" in str(exc_info.value)

    @respx.mock
    def test_without_api_key_uses_free_api(self) -> None:
        """Test that without an API key, the free API is used."""
        route = respx.get("https://api.xposedornot.com/v1/check-email/test@example.com").mock(
            return_value=Response(200, json=SAMPLE_CHECK_EMAIL_RESPONSE)
        )

        client = XposedOrNot()  # No API key
        result = client.check_email("test@example.com")

        assert route.called
        assert isinstance(result, EmailBreachResponse)
        assert result.breaches == ["Adobe", "LinkedIn", "Dropbox"]
