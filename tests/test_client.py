"""Tests for the main client class."""

from __future__ import annotations

import pytest
import respx
from httpx import Response

from xposedornot import (
    XposedOrNot,
    APIError,
    AuthenticationError,
    RateLimitError,
    ServerError,
)


class TestClientInitialization:
    """Tests for client initialization."""

    def test_default_initialization(self) -> None:
        """Test client with default settings."""
        client = XposedOrNot()

        assert client._base_url == "https://api.xposedornot.com"
        assert client._timeout == 30.0
        assert client._rate_limit is True
        assert client._api_key is None

    def test_custom_initialization(self) -> None:
        """Test client with custom settings."""
        client = XposedOrNot(
            api_key="test-key",
            base_url="https://custom.api.com",
            timeout=60.0,
            rate_limit=False,
        )

        assert client._base_url == "https://custom.api.com"
        assert client._timeout == 60.0
        assert client._rate_limit is False
        assert client._api_key == "test-key"

    def test_context_manager(self) -> None:
        """Test client as context manager."""
        with XposedOrNot() as client:
            assert client is not None


class TestErrorHandling:
    """Tests for error handling."""

    @respx.mock
    def test_rate_limit_error(self) -> None:
        """Test handling of rate limit errors."""
        respx.get("https://api.xposedornot.com/v1/breaches").mock(
            return_value=Response(429, json={"error": "Rate limit exceeded"})
        )

        client = XposedOrNot(rate_limit=False)

        with pytest.raises(RateLimitError):
            client.get_breaches()

    @respx.mock
    def test_authentication_error(self) -> None:
        """Test handling of authentication errors."""
        respx.get("https://api.xposedornot.com/v1/breaches").mock(
            return_value=Response(401, json={"error": "Unauthorized"})
        )

        client = XposedOrNot(rate_limit=False)

        with pytest.raises(AuthenticationError):
            client.get_breaches()

    @respx.mock
    def test_server_error(self) -> None:
        """Test handling of server errors."""
        respx.get("https://api.xposedornot.com/v1/breaches").mock(
            return_value=Response(500, json={"error": "Internal server error"})
        )

        client = XposedOrNot(rate_limit=False)

        with pytest.raises(ServerError) as exc_info:
            client.get_breaches()

        assert exc_info.value.status_code == 500

    @respx.mock
    def test_generic_api_error(self) -> None:
        """Test handling of generic API errors."""
        respx.get("https://api.xposedornot.com/v1/breaches").mock(
            return_value=Response(400, text="Bad request")
        )

        client = XposedOrNot(rate_limit=False)

        with pytest.raises(APIError) as exc_info:
            client.get_breaches()

        assert exc_info.value.status_code == 400


class TestAPIKeyHandling:
    """Tests for API key handling."""

    @respx.mock
    def test_api_key_sent_in_header(self) -> None:
        """Test that API key is sent in request header."""
        route = respx.get("https://api.xposedornot.com/v1/breaches").mock(
            return_value=Response(200, json={"Breaches": []})
        )

        client = XposedOrNot(api_key="my-secret-key", rate_limit=False)
        client.get_breaches()

        assert route.called
        request = route.calls[0].request
        assert request.headers.get("x-api-key") == "my-secret-key"

    @respx.mock
    def test_no_api_key_header_when_not_set(self) -> None:
        """Test that no API key header is sent when not configured."""
        route = respx.get("https://api.xposedornot.com/v1/breaches").mock(
            return_value=Response(200, json={"Breaches": []})
        )

        client = XposedOrNot(rate_limit=False)
        client.get_breaches()

        assert route.called
        request = route.calls[0].request
        assert "x-api-key" not in request.headers
