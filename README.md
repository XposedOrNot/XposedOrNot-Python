# XposedOrNot Python Client

A Python client for the [XposedOrNot API](https://xposedornot.com) to check for data breaches and exposed credentials.

## Installation

```bash
pip install xposedornot
```

## Quick Start

```python
from xposedornot import XposedOrNot

# Initialize the client
xon = XposedOrNot()

# Check if an email has been exposed
result = xon.check_email("test@example.com")
print(f"Found in {len(result.breaches)} breaches: {result.breaches}")

# Get detailed breach analytics
analytics = xon.breach_analytics("test@example.com")
print(f"Total exposures: {analytics.exposures_count}")
print(f"First breach: {analytics.first_breach}")

for breach in analytics.breaches_details:
    print(f"  - {breach.breach}: {breach.xposed_records} records")

# Get all known breaches
breaches = xon.get_breaches()
print(f"Total breaches in database: {len(breaches)}")

# Filter breaches by domain
adobe_breaches = xon.get_breaches(domain="adobe.com")

# Check if a password has been exposed (uses k-anonymity)
pwd_result = xon.check_password("password123")
print(f"Password exposed {pwd_result.count} times")
```

## Features

- **Email Breach Check**: Check if an email has been exposed in known data breaches
- **Breach Analytics**: Get detailed analytics including metrics by industry, risk level, and year
- **Breach Database**: Access the full database of known breaches with filtering
- **Password Check**: Securely check passwords using k-anonymity (only hash prefix sent)
- **Rate Limiting**: Built-in rate limiting (1 request/second) to respect API limits
- **Type Hints**: Full type annotations for IDE support

## API Reference

### XposedOrNot Client

```python
from xposedornot import XposedOrNot

# Basic initialization
xon = XposedOrNot()

# With options
xon = XposedOrNot(
    api_key="your-api-key",      # For authenticated endpoints
    timeout=30.0,                 # Request timeout in seconds
    rate_limit=True,              # Enable/disable rate limiting
)

# Use as context manager
with XposedOrNot() as xon:
    result = xon.check_email("test@example.com")
```

### Methods

#### `check_email(email: str) -> EmailBreachResponse`

Check if an email has been exposed in data breaches.

```python
result = xon.check_email("test@example.com")
print(result.breaches)  # ['Adobe', 'LinkedIn', ...]
```

#### `breach_analytics(email: str) -> BreachAnalyticsResponse`

Get detailed breach analytics for an email.

```python
analytics = xon.breach_analytics("test@example.com")
print(analytics.exposures_count)      # Total exposures
print(analytics.breaches_count)       # Number of breaches
print(analytics.first_breach)         # Date of first breach
print(analytics.breaches_details)     # List of BreachDetails
print(analytics.metrics)              # BreachMetrics with industry, risk, etc.
```

#### `get_breaches(domain: str = None) -> list[Breach]`

Get all known breaches, optionally filtered by domain.

```python
# All breaches
all_breaches = xon.get_breaches()

# Filter by domain
adobe = xon.get_breaches(domain="adobe.com")
```

#### `check_password(password: str) -> PasswordCheckResponse`

Check if a password has been exposed using k-anonymity.

```python
result = xon.check_password("mypassword")
print(result.count)            # Times found in breaches
print(result.characteristics)  # Password traits
```

## Error Handling

```python
from xposedornot import (
    XposedOrNot,
    NotFoundError,
    RateLimitError,
    ValidationError,
)

xon = XposedOrNot()

try:
    result = xon.check_email("test@example.com")
except NotFoundError:
    print("Email not found in any breaches")
except RateLimitError:
    print("Rate limit exceeded, please wait")
except ValidationError as e:
    print(f"Invalid input: {e}")
```

## Response Models

All responses are typed dataclasses:

- `EmailBreachResponse` - Contains list of breach names
- `BreachAnalyticsResponse` - Detailed analytics with metrics
- `BreachDetails` - Individual breach information
- `BreachMetrics` - Analytics breakdown
- `Breach` - Breach database entry
- `PasswordCheckResponse` - Password exposure data

## Links

- [XposedOrNot Website](https://xposedornot.com)
- [API Documentation](https://xposedornot.com/api_doc)
- [GitHub Repository](https://github.com/XposedOrNot/xposedornot-python)

## License

MIT License
