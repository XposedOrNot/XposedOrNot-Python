"""Response models for the XposedOrNot API."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class EmailBreachResponse:
    """Response from the free check-email endpoint.

    Returns only breach names. For detailed breach information,
    use the Plus API by providing an API key.
    """

    breaches: list[str]
    """List of breach names where the email was found."""

    @classmethod
    def from_api_response(cls, data: dict[str, Any]) -> "EmailBreachResponse":
        """Create from API response."""
        # API returns {"breaches": ["breach1", "breach2"]} on success
        return cls(breaches=data.get("breaches", []))


@dataclass
class BreachInfo:
    """Detailed information about a single breach from the Plus API."""

    breach_id: str
    """Unique identifier for the breach."""

    breached_date: str
    """Date when the breach occurred."""

    logo: str
    """URL to the organization's logo."""

    password_risk: str
    """Risk level of password exposure (e.g., 'hardtocrack', 'easytocrack')."""

    searchable: str
    """Whether the breach is searchable ('Yes'/'No')."""

    xposed_data: str
    """Types of data exposed (e.g., 'Email addresses;Usernames;Passwords')."""

    xposed_records: int
    """Number of records exposed in the breach."""

    xposure_desc: str
    """Description of the breach incident."""

    domain: str
    """Domain of the breached organization."""

    seniority: str | None = None
    """Seniority information if available."""


@dataclass
class EmailBreachDetailedResponse:
    """Response from the Plus API check-email endpoint.

    Requires an API key from console.xposedornot.com.
    Returns detailed breach information including logos, risk levels, and descriptions.
    """

    status: str
    """Response status ('success' or 'error')."""

    email: str
    """The email address that was checked."""

    breaches: list[BreachInfo]
    """List of detailed breach information."""

    @classmethod
    def from_api_response(cls, data: dict[str, Any]) -> "EmailBreachDetailedResponse":
        """Create from Plus API response."""
        breaches = []
        for b in data.get("breaches", []):
            breaches.append(
                BreachInfo(
                    breach_id=b.get("breach_id", ""),
                    breached_date=b.get("breached_date", ""),
                    logo=b.get("logo", ""),
                    password_risk=b.get("password_risk", ""),
                    searchable=b.get("searchable", ""),
                    xposed_data=b.get("xposed_data", ""),
                    xposed_records=b.get("xposed_records", 0),
                    xposure_desc=b.get("xposure_desc", ""),
                    domain=b.get("domain", ""),
                    seniority=b.get("seniority"),
                )
            )
        return cls(
            status=data.get("status", ""),
            email=data.get("email", ""),
            breaches=breaches,
        )


@dataclass
class BreachDetails:
    """Details of a single breach."""

    breach: str
    """Name of the breach."""

    details: str
    """Description of the breach."""

    domain: str
    """Domain affected by the breach."""

    industry: str
    """Industry of the breached organization."""

    logo: str
    """URL to the organization's logo."""

    password_risk: str
    """Risk level of password exposure."""

    references: str
    """References/sources about the breach."""

    searchable: bool
    """Whether the breach is searchable."""

    verified: bool
    """Whether the breach is verified."""

    xposed_data: str
    """Types of data exposed in the breach."""

    xposed_date: str
    """Date of the breach."""

    xposed_records: int
    """Number of records exposed."""


@dataclass
class BreachMetrics:
    """Analytics metrics for breaches."""

    industry: list[dict[str, Any]] = field(default_factory=list)
    """Breakdown by industry."""

    passwords_strength: list[dict[str, Any]] = field(default_factory=list)
    """Password strength distribution."""

    risk: list[dict[str, Any]] = field(default_factory=list)
    """Risk level distribution."""

    xposed_data: list[dict[str, Any]] = field(default_factory=list)
    """Types of exposed data."""

    yearwise_details: list[dict[str, Any]] = field(default_factory=list)
    """Year-by-year breakdown."""


@dataclass
class BreachAnalyticsResponse:
    """Response from the breach-analytics endpoint."""

    breaches_details: list[BreachDetails] = field(default_factory=list)
    """Detailed information about each breach."""

    metrics: BreachMetrics | None = None
    """Analytics metrics."""

    exposures_count: int = 0
    """Total number of exposures."""

    breaches_count: int = 0
    """Total number of breaches."""

    first_breach: str = ""
    """Date of first breach."""

    pastes_count: int = 0
    """Number of pastes found."""

    @classmethod
    def from_api_response(cls, data: dict[str, Any]) -> "BreachAnalyticsResponse":
        """Create from API response."""
        exposed_breaches = data.get("ExposedBreaches", {})
        breaches_details_raw = exposed_breaches.get("breaches_details", [])
        breach_metrics_raw = data.get("BreachMetrics", {})
        breaches_summary = data.get("BreachesSummary", {})

        breaches_details = []
        for b in breaches_details_raw:
            breaches_details.append(
                BreachDetails(
                    breach=b.get("breach", ""),
                    details=b.get("details", ""),
                    domain=b.get("domain", ""),
                    industry=b.get("industry", ""),
                    logo=b.get("logo", ""),
                    password_risk=b.get("password_risk", ""),
                    references=b.get("references", ""),
                    searchable=b.get("searchable", False),
                    verified=b.get("verified", False),
                    xposed_data=b.get("xposed_data", ""),
                    xposed_date=b.get("xposed_date", ""),
                    xposed_records=b.get("xposed_records", 0),
                )
            )

        metrics = BreachMetrics(
            industry=breach_metrics_raw.get("industry", []),
            passwords_strength=breach_metrics_raw.get("passwords_strength", []),
            risk=breach_metrics_raw.get("risk", []),
            xposed_data=breach_metrics_raw.get("xposed_data", []),
            yearwise_details=breach_metrics_raw.get("yearwise_details", []),
        )

        return cls(
            breaches_details=breaches_details,
            metrics=metrics,
            exposures_count=breaches_summary.get("exposures", 0),
            breaches_count=breaches_summary.get("site", 0),
            first_breach=breaches_summary.get("first_breach", ""),
            pastes_count=data.get("PastesSummary", {}).get("cnt", 0),
        )


@dataclass
class Breach:
    """Information about a data breach."""

    breach_id: str
    """Unique identifier for the breach."""

    breached_date: str
    """Date when the breach occurred."""

    domain: str
    """Domain of the breached organization."""

    exposed_data: list[str]
    """Types of data exposed."""

    exposed_records: int
    """Number of records exposed."""

    exposure_description: str
    """Description of the breach."""

    industry: str
    """Industry of the breached organization."""

    logo: str
    """URL to the organization's logo."""

    password_risk: str
    """Risk level of password exposure."""

    reference_url: str
    """Reference URL about the breach."""

    searchable: bool
    """Whether the breach is searchable."""

    sensitive: bool
    """Whether the breach contains sensitive data."""

    verified: bool
    """Whether the breach is verified."""

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Breach":
        """Create from API response dict."""
        exposed_data = data.get("exposedData", [])
        if isinstance(exposed_data, str):
            exposed_data = [exposed_data] if exposed_data else []

        return cls(
            breach_id=data.get("breachID", ""),
            breached_date=data.get("breachedDate", ""),
            domain=data.get("domain", ""),
            exposed_data=exposed_data,
            exposed_records=data.get("exposedRecords", 0),
            exposure_description=data.get("exposureDescription", ""),
            industry=data.get("industry", ""),
            logo=data.get("logo", ""),
            password_risk=data.get("passwordRisk", ""),
            reference_url=data.get("referenceURL", ""),
            searchable=data.get("searchable", False),
            sensitive=data.get("sensitive", False),
            verified=data.get("verified", False),
        )


@dataclass
class PasswordCheckResponse:
    """Response from the password check endpoint."""

    anon: str
    """The hash prefix used for the check."""

    characteristics: dict[str, Any]
    """Password characteristics: digits, alphabets, special chars, length."""

    count: int
    """Number of times this password was found in breaches."""

    @classmethod
    def from_api_response(cls, data: dict[str, Any]) -> "PasswordCheckResponse":
        """Create from API response.

        API returns: {"SearchPassAnon": {"anon": "...", "char": "D:3;A:8;S:0;L:11", "count": "62703"}}
        """
        # Extract nested data from SearchPassAnon
        pass_data = data.get("SearchPassAnon", {})

        # Parse char string like "D:3;A:8;S:0;L:11" into dict
        char_str = pass_data.get("char", "")
        characteristics: dict[str, Any] = {}
        if char_str:
            char_map = {"D": "digits", "A": "alphabets", "S": "special", "L": "length"}
            for part in char_str.split(";"):
                if ":" in part:
                    key, value = part.split(":", 1)
                    if key in char_map:
                        characteristics[char_map[key]] = int(value)

        # Count is returned as string
        count_str = pass_data.get("count", "0")
        count = int(count_str) if count_str else 0

        return cls(
            anon=pass_data.get("anon", ""),
            characteristics=characteristics,
            count=count,
        )
