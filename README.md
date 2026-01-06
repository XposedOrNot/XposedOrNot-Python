# XposedOrNot Python Client

A Python client for the [XposedOrNot API](https://xposedornot.com) to check for data breaches and exposed credentials.

## Installation

```bash
pip install xposedornot
```

## Quick Start

### Free API (No API Key Required)

```python
from xposedornot import XposedOrNot

# Initialize the client
xon = XposedOrNot()

# Check if an email has been exposed (returns breach names only)
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

# Check if a password has been exposed
# SECURE: Password is hashed locally, only partial hash sent to API
pwd_result = xon.check_password("password123")
print(f"Password exposed {pwd_result.count} times")
```

### xonPlus API (API Key Required)

For commercial use with higher rate limits and detailed breach information, get an API key from [console.xposedornot.com](https://console.xposedornot.com).

```python
from xposedornot import XposedOrNot

# Initialize with API key - automatically uses Plus API for email checks
xon = XposedOrNot(api_key="your-api-key")

# Check email - returns detailed breach information
result = xon.check_email("test@example.com")
print(f"Status: {result.status}")
print(f"Email: {result.email}")

for breach in result.breaches:
    print(f"  - {breach.breach_id}")
    print(f"    Domain: {breach.domain}")
    print(f"    Records: {breach.xposed_records}")
    print(f"    Risk: {breach.password_risk}")
    print(f"    Data exposed: {breach.xposed_data}")
```

## Features

- **Email Breach Check**: Check if an email has been exposed in known data breaches
- **xonPlus Integration**: Commercial API with detailed breach info and higher rate limits
- **Breach Analytics**: Get detailed analytics including metrics by industry, risk level, and year
- **Breach Database**: Access the full database of known breaches with filtering
- **Secure Password Check**: Check passwords without exposing them - uses k-anonymity (password is hashed locally, only partial hash sent)
- **Type Hints**: Full type annotations for IDE support

## API Reference

### XposedOrNot Client

```python
from xposedornot import XposedOrNot

# Basic initialization (free API)
xon = XposedOrNot()

# With API key (Plus API - higher rate limits, detailed responses)
xon = XposedOrNot(
    api_key="your-api-key",      # From console.xposedornot.com
    timeout=30.0,                 # Request timeout in seconds
)

# Use as context manager
with XposedOrNot() as xon:
    result = xon.check_email("test@example.com")
```

**Rate Limits**:
- **Free API** (no key): Client enforces 1 request/second, plus the API has hourly/daily caps
- **Plus API** (with key): No client-side throttling - server enforces your tier limit (50-5000 RPM depending on plan)
- **Auto-retry**: On 429 errors, the client automatically retries up to 3 times with exponential backoff (1s, 2s, 4s)
- Commercial plans at [plus.xposedornot.com/products/api](https://plus.xposedornot.com/products/api)

### Methods

#### `check_email(email: str) -> EmailBreachResponse | EmailBreachDetailedResponse`

Check if an email has been exposed in data breaches.

- **Without API key**: Uses free API, returns `EmailBreachResponse` with breach names only
- **With API key**: Uses Plus API (`plus-api.xposedornot.com`), returns `EmailBreachDetailedResponse` with full breach details

```python
# Free API (no key)
xon = XposedOrNot()
result = xon.check_email("test@example.com")
print(result.breaches)  # ['Adobe', 'LinkedIn', ...]

# Plus API (with key)
xon = XposedOrNot(api_key="your-key")
result = xon.check_email("test@example.com")
print(result.breaches[0].breach_id)    # 'Adobe'
print(result.breaches[0].xposed_records)  # 152000000
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

Check if a password has been exposed in data breaches.

**SECURITY: Your password is NEVER sent over the network.** This method uses k-anonymity protection:
1. The password is hashed locally using SHA3-512 (Keccak)
2. Only the first 10 characters of the hash are sent to the API
3. The API returns matches for that hash prefix
4. Your actual password never leaves your machine

```python
# Your password is safe - only a partial hash is sent, never the password itself
result = xon.check_password("mypassword")
print(result.count)            # Times this password was found in breaches
print(result.characteristics)  # Password traits (length, digits, etc.)
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

- `EmailBreachResponse` - Contains list of breach names (free API)
- `EmailBreachDetailedResponse` - Detailed breach info with metadata (Plus API)
- `BreachInfo` - Individual breach details from Plus API (breach_id, domain, password_risk, etc.)
- `BreachAnalyticsResponse` - Detailed analytics with metrics
- `BreachDetails` - Individual breach information from analytics endpoint
- `BreachMetrics` - Analytics breakdown
- `Breach` - Breach database entry
- `PasswordCheckResponse` - Password exposure data

## Links

- [XposedOrNot Website](https://xposedornot.com)
- [API Documentation](https://xposedornot.com/api_doc)
- [GitHub Repository](https://github.com/XposedOrNot/XposedOrNot-Python)

## License

MIT License
