"""Endpoint modules for the XposedOrNot API."""

from .breaches import BreachesEndpoint
from .email import EmailEndpoint
from .password import PasswordEndpoint

__all__ = ["EmailEndpoint", "BreachesEndpoint", "PasswordEndpoint"]
