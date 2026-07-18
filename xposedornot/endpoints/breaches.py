"""Breach-related endpoints for the XposedOrNot API."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ..exceptions import AuthenticationError
from ..models import Breach, DomainBreachesResponse

if TYPE_CHECKING:
    from ..client import XposedOrNot


class BreachesEndpoint:
    """Handles breach-related API endpoints."""

    def __init__(self, client: "XposedOrNot"):
        self._client = client

    def list(self, domain: str | None = None, breach_id: str | None = None) -> list[Breach]:
        """Get a list of all known data breaches.

        Args:
            domain: Optional domain to filter breaches by.
            breach_id: Optional breach ID to fetch a specific breach.

        Returns:
            List of Breach objects.

        Raises:
            RateLimitError: If rate limit is exceeded.
        """
        params = {}
        if domain:
            params["domain"] = domain
        if breach_id:
            params["breach_id"] = breach_id

        data = self._client._request("GET", "/v1/breaches", params=params if params else None)

        # API returns {"exposedBreaches": [...]}
        breaches_list = data.get("exposedBreaches", [])
        return [Breach.from_dict(b) for b in breaches_list]

    def domain_breaches(self) -> DomainBreachesResponse:
        """Get breach information for domains verified against the API key.

        Requires an API key with verified domains configured at
        console.xposedornot.com.

        Returns:
            DomainBreachesResponse with metrics and exposed email records.

        Raises:
            AuthenticationError: If no API key is configured or the key is invalid.
            RateLimitError: If rate limit is exceeded.
        """
        if not self._client._api_key:
            raise AuthenticationError(
                "An API key is required for domain breach monitoring. "
                "Get one at console.xposedornot.com"
            )

        data = self._client._request("POST", "/v1/domain-breaches")
        return DomainBreachesResponse.from_api_response(data)
