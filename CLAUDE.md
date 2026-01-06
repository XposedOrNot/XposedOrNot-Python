# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is the official Python client library for the XposedOrNot API - a service for checking if emails or passwords have been exposed in data breaches. The package is published to PyPI as `xposedornot`.

## Development Commands

```bash
# Install dev dependencies
pip install -e ".[dev]"

# Run all tests
pytest

# Run a single test file
pytest tests/test_client.py

# Run a specific test
pytest tests/test_client.py::TestClientInitialization::test_default_initialization

# Format code
black xposedornot tests

# Lint (configured in pyproject.toml)
ruff check xposedornot tests
```

## Architecture

### Package Structure

- `xposedornot/client.py` - Main `XposedOrNot` client class with HTTP handling, rate limiting, and error mapping
- `xposedornot/endpoints/` - Endpoint handlers that delegate from the main client:
  - `email.py` - Email breach check and analytics
  - `password.py` - Password exposure check (uses k-anonymity with SHA3-512 hash prefix)
  - `breaches.py` - Breach database queries
- `xposedornot/models.py` - Dataclass response models with `from_api_response()` factory methods
- `xposedornot/exceptions.py` - Exception hierarchy rooted at `XposedOrNotError`
- `xposedornot/utils.py` - Email validation and password hashing utilities

### Key Patterns

**Client delegates to endpoints**: The `XposedOrNot` class provides convenience methods (`check_email`, `breach_analytics`, `get_breaches`, `check_password`) that delegate to endpoint handler classes.

**Response parsing**: Each model has a `from_api_response()` or `from_dict()` class method that handles API response transformation.

**Three API base URLs**:
- `api.xposedornot.com` - Free API for email checks and breach analytics
- `plus-api.xposedornot.com` - xonPlus commercial API for detailed email checks (requires API key from console.xposedornot.com)
- `passwords.xposedornot.com` - Password exposure checks

**Automatic API selection for email checks**: When `api_key` is provided to the client, `check_email()` automatically uses the Plus API (`/v3/check-email/{email}?detailed=true`) and returns `EmailBreachDetailedResponse`. Without an API key, it uses the free API (`/v1/check-email/{email}`) and returns `EmailBreachResponse`.

**Rate limiting**: Client-side rate limiting (1 req/sec) only applies to free API (no API key). Plus API users have tier-based limits handled server-side - no client throttling. On 429 errors, the client auto-retries up to 3 times with exponential backoff (1s, 2s, 4s). Commercial plans at https://plus.xposedornot.com/products/api

**Password security (k-anonymity)**: The `check_password()` method never sends passwords over the network. Passwords are hashed locally with SHA3-512, and only the first 10 characters of the hash are sent to `passwords.xposedornot.com`.

### Testing

Tests use `respx` to mock HTTP responses. The client has built-in rate limiting (1 req/sec) for free API which is respected during tests.

### Commit Message Style

Use conventional commits with emoji prefixes (same style as XposedOrNot-API):

```
[emoji] [type]: [description]
```

| Emoji | Type | Use Case |
|-------|------|----------|
| ✨ | `feat:` | New features |
| 🐛 | `fix:` | Bug fixes |
| 🔒 | `security:` | Security updates |
| ⚡ | `perf:` | Performance improvements |
| 🧹 | `chore:` | Maintenance, cleanup |
| 📝 | `docs:` | Documentation changes |
| ♻️ | `refactor:` | Code refactoring |
| ✅ | `test:` | Test additions/changes |
| ⏪ | `revert:` | Rollback changes |

Example: `✨ feat: Add xonPlus API support for detailed email breach checks`
