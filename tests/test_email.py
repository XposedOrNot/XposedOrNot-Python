"""Tests for email-related endpoints."""

from __future__ import annotations

import pytest
import respx
from httpx import Response

from xposedornot import XposedOrNot, NotFoundError, ValidationError
from xposedornot.models import EmailBreachResponse, BreachAnalyticsResponse

from .conftest import (
    SAMPLE_CHECK_EMAIL_RESPONSE,
    SAMPLE_BREACH_ANALYTICS_RESPONSE,
)


class TestCheckEmail:
    """Tests for the check_email endpoint."""

    @respx.mock
    def test_check_email_found(self) -> None:
        """Test checking an email that exists in breaches."""
        respx.get("https://api.xposedornot.com/v1/check-email/test@example.com").mock(
            return_value=Response(200, json=SAMPLE_CHECK_EMAIL_RESPONSE)
        )

        client = XposedOrNot(rate_limit=False)
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

        client = XposedOrNot(rate_limit=False)

        with pytest.raises(NotFoundError):
            client.check_email("clean@example.com")

    def test_check_email_invalid_format(self) -> None:
        """Test checking an invalid email format."""
        client = XposedOrNot(rate_limit=False)

        with pytest.raises(ValidationError) as exc_info:
            client.check_email("not-an-email")

        assert "Invalid email format" in str(exc_info.value)

    def test_check_email_empty(self) -> None:
        """Test checking an empty email."""
        client = XposedOrNot(rate_limit=False)

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

        client = XposedOrNot(rate_limit=False)
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

        client = XposedOrNot(rate_limit=False)

        with pytest.raises(NotFoundError):
            client.breach_analytics("clean@example.com")

    def test_breach_analytics_invalid_email(self) -> None:
        """Test analytics with invalid email format."""
        client = XposedOrNot(rate_limit=False)

        with pytest.raises(ValidationError):
            client.breach_analytics("invalid-email")
