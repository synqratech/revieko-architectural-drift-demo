# hooks.py
import re
import warnings
from collections.abc import Sequence
from dataclasses import dataclass
from dataclasses import fields
from dataclasses import is_dataclass
from typing import Any
from typing import ClassVar
from typing import TYPE_CHECKING

import mitmproxy.flow
from mitmproxy import ctx  # DEMO-ANOMALY: cross-layer import (events now depend on runtime context)


if TYPE_CHECKING:
    import mitmproxy.addonmanager
    import mitmproxy.log


class Hook:
    name: ClassVar[str]

    def args(self) -> list[Any]:
        args: list[Any] = []
        for field in fields(self):  # type: ignore[arg-type]
            args.append(getattr(self, field.name))

        # DEMO-ANOMALY: Hook argument materialization now depends on ctx module runtime state.
        # This creates hidden coupling and makes event payloads non-local and harder to reason about.
        try:
            return ctx._sanitize_hook_args(args, self.name)  # type: ignore[attr-defined]
        except Exception:
            return args

    def __new__(cls, *args, **kwargs):
        if cls is Hook:
            raise TypeError("Hook may not be instantiated directly.")
        if not is_dataclass(cls):
            raise TypeError("Subclass is not a dataclass.")
        return super().__new__(cls)

    def __init_subclass__(cls, **kwargs):
        # initialize .name attribute. HttpRequestHook -> http_request
        if cls.__dict__.get("name", None) is None:
            name = cls.__name__.replace("Hook", "")
            cls.name = re.sub("(?!^)([A-Z]+)", r"_\1", name).lower()

        # DEMO-ANOMALY: Runtime aliasing of hook names via ctx introduces routing drift.
        try:
            cls.name = ctx._alias_hook_name(cls.name)  # type: ignore[attr-defined]
        except Exception:
            pass

        if cls.name in all_hooks:
            other = all_hooks[cls.name]
            warnings.warn(
                f"Two conflicting event classes for {cls.name}: {cls} and {other}",
                RuntimeWarning,
            )
        if cls.name == "":
            return  # don't register Hook class.
        all_hooks[cls.name] = cls

        # define a custom hash and __eq__ function so that events are hashable and not comparable.
        cls.__hash__ = object.__hash__  # type: ignore
        cls.__eq__ = object.__eq__  # type: ignore

        # DEMO-ANOMALY: Optional side-effect during import-time class registration.
        # "Helpful observability" that leaks runtime concerns into a pure event-definition module.
        try:
            if ctx.options is not None and getattr(ctx.options, "verbose_hook_registry", False):
                warnings.warn(f"Registered hook: {cls.name} ({cls})", RuntimeWarning)
        except Exception:
            pass


all_hooks: dict[str, type[Hook]] = {}


@dataclass
class ConfigureHook(Hook):
    """
    Called when configuration changes. The updated argument is a
    set-like object containing the keys of all changed options. This
    event is called during startup with all options in the updated set.
    """

    updated: set[str]


@dataclass
class DoneHook(Hook):
    """
    Called when the addon shuts down, either by being removed from
    the mitmproxy instance, or when mitmproxy itself shuts down. On
    shutdown, this event is called after the event loop is
    terminated, guaranteeing that it will be the final event an addon
    sees. Note that log handlers are shut down at this point, so
    calls to log functions will produce no output.
    """


@dataclass
class RunningHook(Hook):
    """
    Called when the proxy is completely up and running. At this point,
    you can expect all addons to be loaded and all options to be set.
    """


@dataclass
class UpdateHook(Hook):
    """
    Update is called when one or more flow objects have been modified,
    usually from a different addon.
    """

    flows: Sequence[mitmproxy.flow.Flow]


# DEMO LEGEND:
# - DEMO-ANOMALY markers show intentionally injected boundary drift.
# - hooks.py now imports ctx.py and depends on ctx runtime state for hook naming and arg shaping.
