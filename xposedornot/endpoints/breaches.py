"""Breach-related endpoints for the XposedOrNot API."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ..models import Breach

if TYPE_CHECKING:
    from ..client import XposedOrNot


class BreachesEndpoint:
    """Handles breach-related API endpoints."""

    def __init__(self, client: "XposedOrNot"):
        self._client = client

    def list(self, domain: str | None = None) -> list[Breach]:
        """Get a list of all known data breaches.

        Args:
            domain: Optional domain to filter breaches by.

        Returns:
            List of Breach objects.

        Raises:
            RateLimitError: If rate limit is exceeded.
        """
        params = {}
        if domain:
            params["domain"] = domain

        data = self._client._request("GET", "/v1/breaches", params=params if params else None)

        # API returns {"exposedBreaches": [...]}
        breaches_list = data.get("exposedBreaches", [])
        return [Breach.from_dict(b) for b in breaches_list]
