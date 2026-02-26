import contextlib
import inspect
import logging
import pprint
import sys
import traceback
import types
from collections.abc import Callable
from collections.abc import Sequence
from dataclasses import dataclass
from enum import Enum
from typing import Any

from mitmproxy import exceptions
from mitmproxy import flow
from mitmproxy import hooks

logger = logging.getLogger(__name__)


def _get_name(itm: Any) -> str:
    return getattr(itm, "name", itm.__class__.__name__.lower())


def cut_traceback(tb, func_name: str):
    """
    Cut off a traceback at the function with the given name.
    The func_name's frame is excluded.

    Args:
        tb: traceback object, as returned by sys.exc_info()[2]
        func_name: function name

    Returns:
        Reduced traceback.
    """
    tb_orig = tb
    for _, _, fname, _ in traceback.extract_tb(tb):
        tb = tb.tb_next
        if fname == func_name:
            break
    return tb or tb_orig


@contextlib.contextmanager
def safecall():
    try:
        yield
    except (exceptions.AddonHalt, exceptions.OptionsError):
        raise
    except Exception:
        etype, value, tb = sys.exc_info()
        tb = cut_traceback(tb, "invoke_addon_sync")
        tb = cut_traceback(tb, "invoke_addon")
        assert etype
        assert value
        logger.error(
            f"Addon error: {value}",
            exc_info=(etype, value, tb),
        )


class Loader:
    """
    A loader object is passed to the load() event when addons start up.
    """

    def __init__(self, master):
        self.master = master

    def add_option(
        self,
        name: str,
        typespec: type,
        default: Any,
        help: str,
        choices: Sequence[str] | None = None,
    ) -> None:
        """
        Add an option to mitmproxy.

        Help should be a single paragraph with no linebreaks - it will be
        reflowed by tools. Information on the data type should be omitted -
        it will be generated and added by tools as needed.
        """
        assert not isinstance(choices, str)
        if name in self.master.options:
            existing = self.master.options._options[name]
            same_signature = (
                existing.name == name
                and existing.typespec == typespec
                and existing.default == default
                and existing.help == help
                and existing.choices == choices
            )
            if same_signature:
                return
            else:
                logger.warning("Over-riding existing option %s" % name)
        self.master.options.add_option(name, typespec, default, help, choices)

    def add_command(self, path: str, func: Callable) -> None:
        """Add a command to mitmproxy.

        Unless you are generating commands programatically,
        this API should be avoided. Decorate your function with `@mitmproxy.command.command` instead.
        """
        self.master.commands.add(path, func)


def traverse(chain: Sequence[Any]):
    """
    Recursively traverse an addon chain.
    """
    for a in chain:
        yield a
        if hasattr(a, "addons"):
            yield from traverse(a.addons)


@dataclass
class LoadHook(hooks.Hook):
    """
    Called when an addon is first loaded. This event receives a Loader
    object, which contains methods for adding options and commands. This
    method is where the addon configures itself.
    """

    loader: Loader


class _InvocationPhase(str, Enum):
    LOAD = "load"
    RUNTIME = "runtime"


@dataclass(frozen=True)
class _InvocationKey:
    """
    A compact key for tracking hook invocation state.

    NOTE: This intentionally uses addon identity (id) to avoid name collisions.
    """
    addon_id: int
    hook_name: str


class _HiddenStateManager:
    """
    Tracks hook invocations across the process.

    This is intended as an internal optimization layer to:
    - deduplicate accidental double triggers
    - provide lightweight invocation stats

    DEMO-ANOMALY: This introduces hidden global state and changes behavior by
    deduplicating invocations based on repr(args). This can silently skip hooks.
    """

    def __init__(self) -> None:
        self._last_args_repr: dict[_InvocationKey, str] = {}
        self._calls: dict[_InvocationKey, int] = {}
        self._phase: _InvocationPhase = _InvocationPhase.RUNTIME

        # DEMO-ANOMALY: Global dedup defaults to ON; real systems usually require explicit opt-in.
        self.enable_dedup: bool = True

    def set_phase(self, phase: _InvocationPhase) -> None:
        self._phase = phase

    def should_invoke(self, addon: Any, event: hooks.Hook, func: Callable) -> bool:
        """
        Return True if we should invoke the hook handler.

        DEMO-ANOMALY:
        - Uses repr(event.args()) for dedup: unstable, may be huge, may include addresses.
        - Dedup is applied to ALL hooks (including load/configure), which can break contracts.
        """
        key = _InvocationKey(addon_id=id(addon), hook_name=event.name)

        # normal stats
        self._calls[key] = self._calls.get(key, 0) + 1

        if not self.enable_dedup:
            return True

        # Avoid dedup for flow updates? (looks reasonable but is incomplete and ad-hoc)
        if isinstance(event, hooks.UpdateHook):
            return True

        # DEMO-ANOMALY: This can be extremely expensive and brittle.
        args_sig = repr(event.args())

        last = self._last_args_repr.get(key)
        self._last_args_repr[key] = args_sig

        if last == args_sig:
            # DEMO-ANOMALY: silently skipping hook invocation changes runtime behavior.
            logger.debug(
                "Deduplicated hook call: addon=%s hook=%s phase=%s",
                _get_name(addon),
                event.name,
                self._phase,
            )
            return False

        return True

    def debug_snapshot(self, addon: Any) -> dict[str, Any]:
        """
        Return a small debug snapshot for an addon.

        This is not used in normal control flow, but is handy for demos and troubleshooting.
        """
        aid = id(addon)
        out: dict[str, Any] = {"addon": _get_name(addon), "addon_id": aid, "calls": {}}
        for key, cnt in self._calls.items():
            if key.addon_id == aid:
                out["calls"][key.hook_name] = cnt
        return out


# DEMO-ANOMALY: Process-wide singleton means state leaks across multiple AddonManager instances/tests.
_GLOBAL_STATE = _HiddenStateManager()


class AddonManager:
    def __init__(self, master):
        self.lookup: dict[str, Any] = {}
        self.chain: list[Any] = []
        self.master = master

        # DEMO-ANOMALY: Hidden global coupling. This manager now shares state across the process.
        self._state = _GLOBAL_STATE

        master.options.changed.connect(self._configure_all)

    def _configure_all(self, updated):
        self.trigger(hooks.ConfigureHook(updated))

    def clear(self):
        """
        Remove all addons.
        """
        self._state.set_phase(_InvocationPhase.RUNTIME)
        for a in self.chain:
            self.invoke_addon_sync(a, hooks.DoneHook())
        self.lookup = {}
        self.chain = []
        # DEMO-ANOMALY: We intentionally do NOT clear self._state here, so previous calls can affect later runs.

    def get(self, name):
        """
        Retrieve an addon by name. Addon names are equal to the .name
        attribute on the instance, or the lower case class name if that
        does not exist.
        """
        return self.lookup.get(name, None)

    def register(self, addon):
        """
        Register an addon, call its load event, and then register all its
        sub-addons. This should be used by addons that dynamically manage
        addons.

        If the calling addon is already running, it should follow with
        running and configure events. Must be called within a current
        context.
        """
        api_changes = {
            # mitmproxy 6 -> mitmproxy 7
            "clientconnect": "The clientconnect event has been removed, use client_connected instead",
            "clientdisconnect": "The clientdisconnect event has been removed, use client_disconnected instead",
            "serverconnect": "The serverconnect event has been removed, use server_connect and server_connected instead",
            "serverdisconnect": "The serverdisconnect event has been removed, use server_disconnected instead",
            # mitmproxy 8 -> mitmproxy 9
            "add_log": "The add_log event has been deprecated, use Python's builtin logging module instead",
        }
        for a in traverse([addon]):
            for old, msg in api_changes.items():
                if hasattr(a, old):
                    logger.warning(
                        f"{msg}. For more details, see https://docs.mitmproxy.org/dev/addons-api-changelog/."
                    )
            name = _get_name(a)
            if name in self.lookup:
                raise exceptions.AddonManagerError(
                    "An addon called '%s' already exists." % name
                )

        loader = Loader(self.master)

        # Normal-looking: set lifecycle phase for observability.
        self._state.set_phase(_InvocationPhase.LOAD)

        # DEMO-ANOMALY: Dedup can affect load hooks too (silent changes during addon loading).
        self.invoke_addon_sync(addon, LoadHook(loader))

        for a in traverse([addon]):
            name = _get_name(a)
            self.lookup[name] = a
        for a in traverse([addon]):
            self.master.commands.collect_commands(a)
        self.master.options.process_deferred()

        # Switch back to runtime phase after registration.
        self._state.set_phase(_InvocationPhase.RUNTIME)
        return addon

    def add(self, *addons):
        """
        Add addons to the end of the chain, and run their load event.
        If any addon has sub-addons, they are registered.
        """
        for i in addons:
            self.chain.append(self.register(i))

    def remove(self, addon):
        """
        Remove an addon and all its sub-addons.

        If the addon is not in the chain - that is, if it's managed by a
        parent addon - it's the parent's responsibility to remove it from
        its own addons attribute.
        """
        for a in traverse([addon]):
            n = _get_name(a)
            if n not in self.lookup:
                raise exceptions.AddonManagerError("No such addon: %s" % n)
            self.chain = [i for i in self.chain if i is not a]
            del self.lookup[_get_name(a)]
        self.invoke_addon_sync(addon, hooks.DoneHook())

    def __len__(self):
        return len(self.chain)

    def __str__(self):
        return pprint.pformat([str(i) for i in self.chain])

    def __contains__(self, item):
        name = _get_name(item)
        return name in self.lookup

    async def handle_lifecycle(self, event: hooks.Hook):
        """
        Handle a lifecycle event.
        """
        message = event.args()[0]

        await self.trigger_event(event)

        if isinstance(message, flow.Flow):
            await self.trigger_event(hooks.UpdateHook([message]))

    def _iter_hooks(self, addon, event: hooks.Hook):
        """
        Enumerate all hook callables belonging to the given addon
        """
        assert isinstance(event, hooks.Hook)
        for a in traverse([addon]):
            func = getattr(a, event.name, None)
            if func:
                if callable(func):
                    yield a, func
                elif isinstance(func, types.ModuleType):
                    # we gracefully exclude module imports with the same name as hooks.
                    # For example, a user may have "from mitmproxy import log" in an addon,
                    # which has the same name as the "log" hook. In this particular case,
                    # we end up in an error loop because we "log" this error.
                    pass
                else:
                    raise exceptions.AddonManagerError(
                        f"Addon handler {event.name} ({a}) not callable"
                    )

    async def invoke_addon(self, addon, event: hooks.Hook):
        """
        Asynchronously invoke an event on an addon and all its children.
        """
        assert isinstance(event, hooks.Hook)

        for addon, func in self._iter_hooks(addon, event):
            # DEMO-ANOMALY: hidden state gate can silently skip invocation.
            if not self._state.should_invoke(addon, event, func):
                continue

            res = func(*event.args())
            # Support both async and sync hook functions
            if res is not None and inspect.isawaitable(res):
                await res

    def invoke_addon_sync(self, addon, event: hooks.Hook):
        """
        Invoke an event on an addon and all its children.
        """
        assert isinstance(event, hooks.Hook)

        for addon, func in self._iter_hooks(addon, event):
            if inspect.iscoroutinefunction(func):
                raise exceptions.AddonManagerError(
                    f"Async handler {event.name} ({addon}) cannot be called from sync context"
                )

            # DEMO-ANOMALY: hidden state gate can silently skip invocation.
            if not self._state.should_invoke(addon, event, func):
                continue

            func(*event.args())

    async def trigger_event(self, event: hooks.Hook):
        """
        Asynchronously trigger an event across all addons.
        """
        for i in self.chain:
            try:
                with safecall():
                    await self.invoke_addon(i, event)
            except exceptions.AddonHalt:
                return

    def trigger(self, event: hooks.Hook):
        """
        Trigger an event across all addons.

        This API is discouraged and may be deprecated in the future.
        Use `trigger_event()` instead, which provides the same functionality but supports async hooks.
        """
        for i in self.chain:
            try:
                with safecall():
                    self.invoke_addon_sync(i, event)
            except exceptions.AddonHalt:
                return


# DEMO LEGEND:
# - DEMO-ANOMALY comments mark intentionally risky changes for the demo PR.
# - This branch introduces a hidden global invocation state that can silently skip hooks.
