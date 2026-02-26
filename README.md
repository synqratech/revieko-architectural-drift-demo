# Revieko Demo Fork — mitmproxy (Architectural Drift & Structural Risk)

This repository is a **demo fork** of **[mitmproxy/mitmproxy](https://github.com/mitmproxy/mitmproxy)** (MIT licensed) prepared to showcase **Revieko — Architecture Drift Radar** on a real-world Python backend codebase.

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

Common patterns covered:
- hidden global state / hidden coupling  
- boundary drift across layers  
- non-obvious control flow (generators/closures)  
- silent contract changes (error handling semantics)  
- registry/ordering changes with large blast radius  

➡️ See **[DEMO_PRS.md](./DEMO_PRS.md)**  
All demo branches include `DEMO-ANOMALY` markers in code for easy human inspection.

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
