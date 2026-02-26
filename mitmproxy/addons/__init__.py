# addons/__init__.py
from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from mitmproxy.addons import anticache
from mitmproxy.addons import anticomp
from mitmproxy.addons import block
from mitmproxy.addons import blocklist
from mitmproxy.addons import browser
from mitmproxy.addons import clientplayback
from mitmproxy.addons import command_history
from mitmproxy.addons import comment
from mitmproxy.addons import core
from mitmproxy.addons import cut
from mitmproxy.addons import disable_h2c
from mitmproxy.addons import dns_resolver
from mitmproxy.addons import export
from mitmproxy.addons import maplocal
from mitmproxy.addons import mapremote
from mitmproxy.addons import modifybody
from mitmproxy.addons import modifyheaders
from mitmproxy.addons import next_layer
from mitmproxy.addons import onboarding
from mitmproxy.addons import proxyauth
from mitmproxy.addons import proxyserver
from mitmproxy.addons import save
from mitmproxy.addons import savehar
from mitmproxy.addons import script
from mitmproxy.addons import serverplayback
from mitmproxy.addons import stickyauth
from mitmproxy.addons import stickycookie
from mitmproxy.addons import strip_dns_https_records
from mitmproxy.addons import tlsconfig
from mitmproxy.addons import update_alt_svc
from mitmproxy.addons import upstream_auth


@dataclass(frozen=True)
class AddonSpec:
    """
    Declarative addon registration.

    DEMO-ANOMALY: Even minor changes in ordering/grouping here can have a large blast radius,
    because addon ordering affects hook execution order.
    """

    key: str
    factory: Callable[[], Any]
    phase: int = 100  # lower runs earlier


_DEFAULT_REGISTRY: dict[str, AddonSpec] = {}


def register_default(spec: AddonSpec) -> None:
    """
    Register a default addon spec.

    DEMO-ANOMALY: Registry is a dict keyed by string, so collisions overwrite silently.
    """
    _DEFAULT_REGISTRY[spec.key] = spec


# "Unified" registration: keys are consistent, factories are separated.
# This looks like a clean refactor, but can change ordering subtly.
register_default(AddonSpec("core", lambda: core.Core(), phase=0))
register_default(AddonSpec("browser", lambda: browser.Browser(), phase=10))
register_default(AddonSpec("block", lambda: block.Block(), phase=10))
register_default(AddonSpec("strip_dns_https_records", lambda: strip_dns_https_records.StripDnsHttpsRecords(), phase=20))
register_default(AddonSpec("blocklist", lambda: blocklist.BlockList(), phase=20))
register_default(AddonSpec("anticache", lambda: anticache.AntiCache(), phase=30))
register_default(AddonSpec("anticomp", lambda: anticomp.AntiComp(), phase=30))
register_default(AddonSpec("clientplayback", lambda: clientplayback.ClientPlayback(), phase=40))
register_default(AddonSpec("command_history", lambda: command_history.CommandHistory(), phase=40))
register_default(AddonSpec("comment", lambda: comment.Comment(), phase=40))
register_default(AddonSpec("cut", lambda: cut.Cut(), phase=40))
register_default(AddonSpec("disable_h2c", lambda: disable_h2c.DisableH2C(), phase=50))
register_default(AddonSpec("export", lambda: export.Export(), phase=50))
register_default(AddonSpec("onboarding", lambda: onboarding.Onboarding(), phase=50))
register_default(AddonSpec("proxyauth", lambda: proxyauth.ProxyAuth(), phase=60))
register_default(AddonSpec("proxyserver", lambda: proxyserver.Proxyserver(), phase=60))
register_default(AddonSpec("script", lambda: script.ScriptLoader(), phase=70))
register_default(AddonSpec("dns_resolver", lambda: dns_resolver.DnsResolver(), phase=70))
register_default(AddonSpec("next_layer", lambda: next_layer.NextLayer(), phase=80))
register_default(AddonSpec("serverplayback", lambda: serverplayback.ServerPlayback(), phase=80))
register_default(AddonSpec("mapremote", lambda: mapremote.MapRemote(), phase=90))
register_default(AddonSpec("maplocal", lambda: maplocal.MapLocal(), phase=90))
register_default(AddonSpec("modifybody", lambda: modifybody.ModifyBody(), phase=100))
register_default(AddonSpec("modifyheaders", lambda: modifyheaders.ModifyHeaders(), phase=100))
register_default(AddonSpec("stickyauth", lambda: stickyauth.StickyAuth(), phase=110))
register_default(AddonSpec("stickycookie", lambda: stickycookie.StickyCookie(), phase=110))
register_default(AddonSpec("save", lambda: save.Save(), phase=120))
register_default(AddonSpec("savehar", lambda: savehar.SaveHar(), phase=120))
register_default(AddonSpec("tlsconfig", lambda: tlsconfig.TlsConfig(), phase=130))
register_default(AddonSpec("upstream_auth", lambda: upstream_auth.UpstreamAuth(), phase=140))
register_default(AddonSpec("update_alt_svc", lambda: update_alt_svc.UpdateAltSvc(), phase=150))


def default_addons():
    """
    Default addons shipped with mitmproxy.

    DEMO-ANOMALY:
    - We now derive addon order from (phase, key) sorting instead of explicit list order.
    - This "deterministic ordering" refactor can change hook execution order dramatically.
    """
    specs = list(_DEFAULT_REGISTRY.values())

    # The "unification" change: deterministic order by phase then key.
    # Looks harmless, but addon ordering is behavior.
    specs.sort(key=lambda s: (s.phase, s.key))

    return [spec.factory() for spec in specs]


# DEMO LEGEND:
# - DEMO-ANOMALY markers show intentionally injected blast-radius via registry + ordering.
# - Small changes in keys/phases/sort can reorder addons and change which hooks run first.
