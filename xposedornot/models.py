"""Response models for the XposedOrNot API."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class EmailBreachResponse:
    """Response from the check-email endpoint."""

    breaches: list[str]
    """List of breach names where the email was found."""

    @classmethod
    def from_api_response(cls, data: dict[str, Any]) -> "EmailBreachResponse":
        """Create from API response."""
        # API returns {"breaches": ["breach1", "breach2"]} on success
        return cls(breaches=data.get("breaches", []))


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
    """Password characteristics (digits, alphabets, special chars, length)."""

    count: int
    """Number of times this password was found in breaches."""

    @classmethod
    def from_api_response(cls, data: dict[str, Any]) -> "PasswordCheckResponse":
        """Create from API response."""
        return cls(
            anon=data.get("anon", ""),
            characteristics=data.get("char", {}),
            count=data.get("count", 0),
        )
