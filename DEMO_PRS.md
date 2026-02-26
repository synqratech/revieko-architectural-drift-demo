# Demo PR Scenarios (Revieko)

This repository is a demo fork prepared to showcase **Revieko — Architecture Drift Radar** on a real-world Python backend codebase.

**How to use:**  
1) Fork this repo (do **not** fork only the default branch).  
2) Install the GitHub App: https://github.com/apps/revieko-architecture-drift-radar  
3) Open a PR from one of the `demo/pr-XX-*` branches into your default branch (`main`).  
4) Review the Revieko comment + HTML report.

> All demo branches include `DEMO-ANOMALY` markers in code to make injected risks easy to spot by humans.

---

## Quick Index

| Branch | Theme | What to look for |
|---|---|---|
| `demo/pr-01-hidden-state-manager` | Hidden global state / behavior drift | Silent skipping, cross-run coupling, global singletons |
| `demo/pr-02-control-flow-generator-pipeline` | Control-flow complexity | Generators, closures, late execution, tricky stack traces |
| `demo/pr-03-silent-contract-error-handling` | Silent contract drift | Errors swallowed, fallbacks, semantics change without API change |
| `demo/pr-04-boundary-drift-ctx-imports` | Boundary drift via context | Cross-layer imports, global context registry, runtime shaping |
| `demo/pr-05-hook-registry-blast-radius` | Hook registry blast radius | Naming normalization, aliasing, ordering changes, routing drift |

---

## PR-01 — Hidden State Manager

**Branch:** `demo/pr-01-hidden-state-manager`  
**Primary file(s):** `addonmanager.py`  
**Story:** “Lightweight invocation tracking and dedup to reduce duplicate hook calls.”

### Injected risk patterns
- **Hidden global singleton** used by the dispatch path (cross-instance coupling).
- **Implicit behavior change**: deduplication can silently skip hook handlers.
- **Performance risk**: `repr(event.args())` on hot path can be expensive/brittle.
- **Observability drift**: behavior changes are logged at debug level, not surfaced.

### DEMO-ANOMALY markers
Search in code for: `DEMO-ANOMALY:`

---

## PR-02 — Generator Pipeline & Closures

**Branch:** `demo/pr-02-control-flow-generator-pipeline`  
**Primary file(s):** `addonmanager.py`  
**Story:** “Optimize hook dispatch: build a lazy pipeline to reduce allocations.”

### Injected risk patterns
- **Non-obvious control flow**: generator pipeline + `next()` draining.
- **Closure capture hazards**: loop variables captured late → wrong handler may execute.
- **Debuggability regression**: stack traces become less direct.
- **Silent behavior drift**: unexpected awaitables in sync path are ignored.

### DEMO-ANOMALY markers
Search in code for: `DEMO-ANOMALY:`

---

## PR-03 — Silent Contract Drift (Error Handling)

**Branch:** `demo/pr-03-silent-contract-error-handling`  
**Primary file(s):** `addonmanager.py`  
**Story:** “Improve resilience: don’t let one addon break the chain.”

### Injected risk patterns
- **Contract change without API change**:
  - selected hooks become “best effort”
  - `AddonHalt` / `OptionsError` may be swallowed
- **Fallback semantics**: load-time failures may be ignored and addon still registered.
- **Observability downgrade**: warnings instead of failing fast.

### DEMO-ANOMALY markers
Search in code for: `DEMO-ANOMALY:`

---

## PR-04 — Boundary Drift via `ctx` Imports

**Branch:** `demo/pr-04-boundary-drift-ctx-imports`  
**Primary file(s):** `ctx.py`, `hooks.py`, `addonmanager.py`  
**Story:** “Convenient access to runtime context and consistent hook behavior.”

### Injected risk patterns
- **Boundary drift / cross-layer coupling**:
  - `hooks.py` imports `ctx` and relies on runtime state to shape `Hook.args()`
- **Global mutable context**:
  - `ctx` becomes a runtime registry for master/options/log + policies
- **Runtime routing drift**:
  - hook name aliasing based on global context
- **Hidden dependency chain**:
  - behavior depends on initialization order (who calls `ctx.set_context` first)

### DEMO-ANOMALY markers
Search in code for: `DEMO-ANOMALY:`

---

## PR-05 — Hook Registry Blast Radius

**Branch:** `demo/pr-05-hook-registry-blast-radius`  
**Primary file(s):** `hooks.py`, `addonmanager.py`, `addons/__init__.py` *(and optionally `exceptions.py`)*  
**Story:** “Unify hook naming and default addon registration for consistency.”

### Injected risk patterns
- **Hook registry behavior becomes fragile**:
  - name normalization changes + alias registration in the same registry
  - deterministic but arbitrary conflict resolution
- **Dispatch becomes sensitive to registry details**:
  - addon dispatch resolves aliases from hooks registry
- **Addon ordering becomes behavior**:
  - default addons derived from registry + sorted by `(phase, key)`
  - small key/phase tweaks reorder execution and change runtime outcomes
- **Exception shape drift (optional)**:
  - richer context on exceptions changes `str()`/signature and downstream parsing

### DEMO-ANOMALY markers
Search in code for: `DEMO-ANOMALY:`

---

## Notes for reviewers

These PRs are intentionally designed to be *plausible* changes that could appear in production:
- “Optimization”
- “Resilience”
- “Convenience”
- “Unification / refactor”

…but each injects a risk pattern that tends to slip through superficial review.

If you want to explore further, compare:
- dependency boundaries (imports)
- control flow (lazy generators / closures)
- error semantics (swallow vs fail-fast)
- routing rules (hook registry + aliasing)
- ordering effects (addon registry / sorting)

---

## Support

- GitHub App: https://github.com/apps/revieko-architecture-drift-radar  
- Docs: https://synqra.tech/revieko-docs  
- Contact: *(add your preferred email/LinkedIn here)*
