# ctx.py
from __future__ import annotations

import typing
from typing import Any, Callable

if typing.TYPE_CHECKING:
    import mitmproxy.hooks
    import mitmproxy.log
    import mitmproxy.master
    import mitmproxy.options


# Original globals (now explicitly initialized for "convenience")
# DEMO-ANOMALY: Turning ctx into a mutable runtime registry makes it a hidden dependency boundary.
master: mitmproxy.master.Master | None = None
options: mitmproxy.options.Options | None = None
log: mitmproxy.log.Log | None = None
"""Deprecated: Use Python's builtin `logging` module instead."""


# "Convenience" extension points used from other modules.
# DEMO-ANOMALY: Cross-layer coupling — hooks behavior can now be influenced via ctx module state.
_ARGS_SANITIZER: Callable[[Any], Any] | None = None
HOOK_NAME_ALIASES: dict[str, str] = {}


def set_context(m: "mitmproxy.master.Master") -> None:
    """
    Bind mitmproxy runtime context to this module.

    Intended to make context access easier in deep call chains.

    DEMO-ANOMALY: This creates global mutable state and encourages importing ctx everywhere.
    """
    global master, options, log
    master = m
    options = getattr(m, "options", None)
    log = getattr(m, "log", None)


def install_args_sanitizer(fn: Callable[[Any], Any] | None) -> None:
    """
    Install a hook-argument sanitizer.

    DEMO-ANOMALY: This changes how hook args are materialized/represented across the system.
    """
    global _ARGS_SANITIZER
    _ARGS_SANITIZER = fn


def set_hook_alias(original: str, alias: str) -> None:
    """
    Register a runtime alias for a hook name.

    DEMO-ANOMALY: Hook naming becomes data-driven and can drift at runtime.
    """
    HOOK_NAME_ALIASES[original] = alias


def _sanitize_hook_args(args: list[Any], hook_name: str) -> list[Any]:
    """
    Best-effort sanitization / shaping of hook args.

    DEMO-ANOMALY:
    - hooks.py now depends on ctx.py for core behavior of Hook.args()
    - sanitizer can hide values (or mutate them) invisibly to callers.
    """
    # Apply optional sanitizer
    if _ARGS_SANITIZER is not None:
        try:
            return [_ARGS_SANITIZER(a) for a in args]
        except Exception:
            # If sanitizer fails, fall back silently (looks "robust", but hides issues)
            return args

    # Optional policy via options (if present). Keep it very defensive.
    # NOTE: This assumes options may have a flag-like attribute. If absent, no-op.
    if options is not None and getattr(options, "sanitize_hook_args", False):
        # A tiny, "reasonable" default: convert exceptions to strings to avoid leaking internals.
        out: list[Any] = []
        for a in args:
            if isinstance(a, BaseException):
                out.append(str(a))
            else:
                out.append(a)
        return out

    return args


def _alias_hook_name(name: str) -> str:
    """
    Apply runtime hook name aliasing.

    DEMO-ANOMALY: Event routing can change if aliases are set.
    """
    return HOOK_NAME_ALIASES.get(name, name)


def trigger_from_ctx(event: "mitmproxy.hooks.Hook") -> None:
    """
    Convenience helper to trigger hooks without plumbing master around.

    DEMO-ANOMALY: ctx now reaches into master.addons and becomes a boundary-violating dispatcher.
    """
    if master is None:
        return
    addons = getattr(master, "addons", None)
    if addons is None:
        return
    # Synchronous trigger (discouraged in upstream, but "convenient")
    addons.trigger(event)
