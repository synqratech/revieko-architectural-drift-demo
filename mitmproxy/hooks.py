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

if TYPE_CHECKING:
    import mitmproxy.addonmanager
    import mitmproxy.log


def _legacy_hook_name(class_name: str) -> str:
    """
    Legacy naming: HttpRequestHook -> http_request
    (Matches the original behavior.)
    """
    name = class_name.replace("Hook", "")
    return re.sub("(?!^)([A-Z]+)", r"_\1", name).lower()


def _unified_hook_name(class_name: str) -> str:
    """
    Unified naming: more "consistent" splitting across capitals.

    DEMO-ANOMALY: This looks like a harmless normalization tweak,
    but it can rename a large set of hooks and create collisions/aliases.
    """
    name = class_name.replace("Hook", "")
    # NOTE: splits on every capital, not on groups.
    return re.sub(r"(?<!^)([A-Z])", r"_\1", name).lower()


all_hooks: dict[str, type["Hook"]] = {}

# Maps legacy -> canonical
hook_aliases: dict[str, str] = {}

# A small, deterministic tiebreaker to "resolve" conflicts.
# DEMO-ANOMALY: changing conflict resolution changes which hook class wins.
_hook_precedence: dict[str, int] = {}


def _register_hook(name: str, cls: type["Hook"], *, alias_of: str | None = None) -> None:
    """
    Register a hook class under a name.

    DEMO-ANOMALY:
    - Overwrites are resolved deterministically (module/name based), which can silently change routing.
    - Aliases participate in the same registry, so an alias can override a real hook.
    """
    if name == "":
        return

    if name in all_hooks:
        other = all_hooks[name]
        # deterministic precedence key
        other_key = f"{other.__module__}:{other.__qualname__}"
        new_key = f"{cls.__module__}:{cls.__qualname__}"

        # Prefer "smaller" key lexicographically (deterministic, but arbitrary).
        # This can flip behavior depending on import order and packaging changes.
        if _hook_precedence.get(name) is None:
            _hook_precedence[name] = 0

        if new_key < other_key:
            warnings.warn(
                f"Hook registry override for '{name}': {other} -> {cls}"
                + (f" (alias of '{alias_of}')" if alias_of else ""),
                RuntimeWarning,
            )
            all_hooks[name] = cls
        else:
            warnings.warn(
                f"Hook registry conflict for '{name}': keeping {other}, ignoring {cls}"
                + (f" (alias of '{alias_of}')" if alias_of else ""),
                RuntimeWarning,
            )
            return
    else:
        all_hooks[name] = cls


class Hook:
    name: ClassVar[str]

    def args(self) -> list[Any]:
        args: list[Any] = []
        for field in fields(self):  # type: ignore[arg-type]
            args.append(getattr(self, field.name))
        return args

    def __new__(cls, *args, **kwargs):
        if cls is Hook:
            raise TypeError("Hook may not be instantiated directly.")
        if not is_dataclass(cls):
            raise TypeError("Subclass is not a dataclass.")
        return super().__new__(cls)

    def __init_subclass__(cls, **kwargs):
        # initialize .name attribute unless explicitly set
        explicit = cls.__dict__.get("name", None) is not None
        if not explicit:
            unified = _unified_hook_name(cls.__name__)
            legacy = _legacy_hook_name(cls.__name__)

            # Canonical name becomes the "unified" one.
            cls.name = unified

            # Register canonical
            _register_hook(unified, cls)

            # Register legacy alias to preserve compatibility.
            # DEMO-ANOMALY: This can introduce collisions and override unrelated hooks.
            if legacy != unified:
                hook_aliases[legacy] = unified
                _register_hook(legacy, cls, alias_of=unified)
        else:
            # Explicitly named hooks still go into registry as-is.
            _register_hook(cls.name, cls)

        if cls.name == "":
            return  # don't register Hook class.

        # define a custom hash and __eq__ function so that events are hashable and not comparable.
        cls.__hash__ = object.__hash__  # type: ignore
        cls.__eq__ = object.__eq__  # type: ignore


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
# - DEMO-ANOMALY markers show intentionally injected hook registry risk.
# - This branch changes hook name normalization and adds legacy aliases into the same registry,
#   so small naming/ordering changes can cause large routing ("blast radius") effects.
