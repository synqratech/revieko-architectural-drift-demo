# Revieko Demo Fork — mitmproxy (Architectural Drift & Structural Risk)

This repository is a **demo fork** of **[mitmproxy/mitmproxy](https://github.com/mitmproxy/mitmproxy)** (MIT licensed), prepared to showcase **Revieko — Architecture Drift Radar** on a real-world Python backend codebase.

- Upstream project: https://github.com/mitmproxy/mitmproxy  
- License: MIT (see [LICENSE](./LICENSE))  
- Fork notice: see [UPSTREAM.md](./UPSTREAM.md)

> Looking for the original mitmproxy documentation and installation instructions? Use the upstream links at the bottom.

---

## What this demo is for

Modern PRs (especially large or AI-assisted ones) can look safe:
- CI passes
- tests are green
- the diff “reads fine”

…and still drift architecture, expand blast radius, or introduce hidden coupling.

This repo is prepared so you can **fork → open a prebuilt PR → get a Revieko report** in minutes.

---

## Why this codebase (and this module)

This demo focuses on a classic **blast-radius hotspot**: an **event dispatcher / addon manager**.
Small “refactors”, “optimizations”, or “resilience improvements” in dispatch code can silently change system semantics:
- whether handlers run at all
- ordering and routing behavior
- error semantics (fail-fast vs swallow)
- cross-run coupling via hidden shared state

Those changes often slip through superficial review because the code still looks reasonable and CI can remain green.

---

## What you should see in the demo

After you open a demo PR and Revieko is installed on your fork, you should see:
- a **PR comment** with a short risk summary
- a link to a **full HTML report**
- a **Hotspots** table that points to the highest-risk lines first

---

## What is Revieko?

**Revieko — Architecture Drift Radar** is a GitHub App that generates a **risk-first review report** for pull requests:
- highlights *where* trust is required first  
- flags structural/architectural risk signals  
- helps reviewers focus on the highest blast-radius areas  

GitHub App: https://github.com/apps/revieko-architecture-drift-radar  
Docs: https://synqra.tech/revieko-docs

---

## Quickstart (5–10 minutes)

### 1) Fork this repository
When forking, **do not fork only the default branch**.  
You need the `demo/pr-*` branches too.

### 2) Install the Revieko GitHub App
Install: https://github.com/apps/revieko-architecture-drift-radar

Grant access to your fork (permissions are requested by GitHub during install).

### 3) Open a demo PR
In your fork, create a pull request from a demo branch into your default branch (usually `main`).

- Demo branches follow the convention: `demo/pr-XX-...`
- The full scenario list is in: **[DEMO_PRS.md](./DEMO_PRS.md)**

### 4) View the report
Revieko will comment on the PR with:
- a short summary
- a link to the full HTML report

---

## Demo PR scenarios

Each demo PR is intentionally designed to be *plausible* (“optimization”, “resilience”, “refactor”, “unification”), while injecting a clear risk pattern that tends to slip through superficial review.

### Demo matrix (PR → pattern → what to look for)

| Demo PR | Pattern | What changes | Where you should see hotspots first |
|---|---|---|---|
| PR-01 | Hidden coupling | Global singleton + dispatch gate | Dedup/state + invocation gate in dispatcher |
| PR-02 | Non-obvious control flow | Generator/closure pipeline | Pipeline builder (`yield step`) + sync/async boundary |
| PR-03 | Silent contract drift | Error semantics become “best effort” | Best-effort safecall + trigger branches + load-time swallow |
| PR-04 | Boundary drift | Cross-layer imports + global context | `hooks` ↔ `ctx` dependency + args/routing shaped by runtime state |
| PR-05 | Registry blast radius | Naming/aliasing/ordering becomes behavior | Hook registry normalization + alias conflicts + addon ordering |

➡️ See **[DEMO_PRS.md](./DEMO_PRS.md)**  
All demo branches include `DEMO-ANOMALY` markers in code for easy human inspection.

---

## How to read the report

Revieko is a **risk-first radar**. The goal is to help you decide **where to look first**, not to prove correctness.

- **`risk_level`**: overall risk label for the PR/file(s).
- **`struct_risk (0–100)`**: aggregate structural risk. *Not* “probability of a bug”.
- **Hotspots**
  - **`Score`**: local anomaly strength (higher = more abnormal).
  - **`Kind`**
    - `struct_pattern_break`: a local break in an expected structural pattern.
    - `depth_spike`: localized complexity increase (nesting/shape change).
    - `control_outlier`: unusual control-flow shape compared to nearby code.
    - `mixed`: multiple weaker structural signals at the same location.
  - **`Effects/Taint/Control`**: heuristic tags (best-effort). They may be empty or occasionally inaccurate.

---

## What to do with a hotspot (reviewer checklist)

Hotspots are most valuable in **blast-radius modules** (dispatchers, registries, boundary layers).

When a hotspot is in a dispatcher/manager module, ask:
- Does this change **whether** handlers run (skip paths / gates / dedup)?
- Does this introduce **global/shared state** or cross-run coupling?
- Does this change **ordering/routing** semantics?
- Does this change **error semantics** (swallow vs fail-fast)?
- Does this blur **sync/async** contracts?
- Is there a test that proves the contract still holds?

---

## Non-goals (what this demo/app is not)

- Not a bug finder.
- Not a security scanner.
- Not a linter or style checker.
- Not a replacement for tests, CodeQL, SAST, or standard review.

It’s a **structural + semantic radar** for architectural drift and blast-radius risk.

---

## Troubleshooting

### I don’t see a Revieko comment
- Confirm the app is installed: https://github.com/apps/revieko-architecture-drift-radar  
- Confirm the app has access to **your fork** (GitHub install permissions).
- Confirm the PR is opened **in the fork** where the app is installed.

### My fork doesn’t have `demo/pr-*` branches
- When forking, make sure you don’t fork only the default branch.
- If you already forked default-only, re-fork with all branches (or fetch branches manually).

### The PR uses the wrong base branch
- Open the PR from `demo/pr-XX-*` **into your default branch** (usually `main`).

### CI shows `warn`
Some demo PRs intentionally include refactors that may cause warnings. The focus is the **architecture/risk report**, not CI perfection.

---

## Need help?

- Documentation: https://synqra.tech/revieko-docs  
- GitHub App: https://github.com/apps/revieko-architecture-drift-radar  
- Contact:
  - Email: `anton.f@synqra.tech`
  - LinkedIn: `https://www.linkedin.com/in/anvifedotov/`

---

## Upstream project (mitmproxy)

`mitmproxy` is an interactive, SSL/TLS-capable intercepting proxy with a console interface for HTTP/1, HTTP/2, and WebSockets.

`mitmdump` is the command-line version of mitmproxy. Think tcpdump for HTTP.

`mitmweb` is a web-based interface for mitmproxy.

Upstream installation instructions:  
https://docs.mitmproxy.org/stable/overview-installation

Upstream contributing guide:  
[CONTRIBUTING.md](./CONTRIBUTING.md)
