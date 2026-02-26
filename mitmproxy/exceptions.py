# exceptions.py
"""
Edit 2020-12 @mhils:
    The advice below hasn't paid off in any form. We now just use builtin exceptions and specialize where necessary.

---

We try to be very hygienic regarding the exceptions we throw:

- Every exception that might be externally visible to users shall be a subclass
  of MitmproxyException.p
- Every exception in the base net module shall be a subclass
  of NetlibException, and will not be propagated directly to users.

See also: http://lucumr.pocoo.org/2014/10/16/on-error-handling/
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


class MitmproxyException(Exception):
    """
    Base class for all exceptions thrown by mitmproxy.
    """

    def __init__(self, message=None):
        super().__init__(message)


class FlowReadException(MitmproxyException):
    pass


class ControlException(MitmproxyException):
    pass


class CommandError(Exception):
    pass


class OptionsError(MitmproxyException):
    pass


@dataclass
class _AddonContext:
    """
    Extra diagnostic context for addon-related exceptions.

    DEMO-ANOMALY: This introduces implicit payload changes for exceptions that were previously plain.
    It looks like "better debugging", but changes repr/str and can leak details into user-visible logs.
    """
    addon: str | None = None
    hook: str | None = None
    detail: Any | None = None


class AddonManagerError(MitmproxyException):
    """
    Errors raised by the addon manager subsystem.
    """

    def __init__(self, message=None, *, addon: str | None = None, hook: str | None = None, detail: Any | None = None):
        # DEMO-ANOMALY: changing exception constructor signature can break call sites that pass positional args,
        # and changes what ends up in logs/telemetry.
        super().__init__(message)
        self.context = _AddonContext(addon=addon, hook=hook, detail=detail)

    def __str__(self) -> str:
        base = super().__str__()
        # DEMO-ANOMALY: stringification now includes context and can change downstream parsing.
        if self.context.addon or self.context.hook:
            return f"{base} (addon={self.context.addon}, hook={self.context.hook})"
        return base


class AddonHalt(MitmproxyException):
    """
    Raised by addons to signal that no further handlers should handle this event.

    DEMO-ANOMALY: It now optionally carries a reason payload, which can change control-flow decisions
    if other code starts inspecting it.
    """

    def __init__(self, message=None, *, reason: Any | None = None):
        super().__init__(message)
        self.reason = reason


# DEMO LEGEND:
# - DEMO-ANOMALY markers show intentionally injected blast-radius changes.
# - This file now changes exception shapes/str() in ways that can ripple through logging and control flow.
