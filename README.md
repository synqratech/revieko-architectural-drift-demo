# Revieko Demo Fork — mitmproxy (Architectural Drift & Structural Risk)

This repository is a **demo fork** of **[mitmproxy/mitmproxy](https://github.com/mitmproxy/mitmproxy)** (MIT licensed) used to showcase **Revieko — Architecture Drift Radar** on a real-world Python backend codebase.

- Upstream project: https://github.com/mitmproxy/mitmproxy  
- License: MIT (see [LICENSE](./LICENSE))  
- Fork notice: see [UPSTREAM.md](./UPSTREAM.md)

> Looking for the original mitmproxy docs and installation? Use the upstream links below.

---

## What this demo is for

Modern PRs (especially large or AI-assisted ones) can look safe:
- CI passes
- tests are green
- the diff “reads fine”

…and still drift architecture, expand blast radius, or introduce hidden coupling.

This repo is prepared to let you **fork → open a prebuilt PR → get a Revieko report** in minutes.

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
You need the demo branches too.

### 2) Install the Revieko GitHub App
Install: https://github.com/apps/revieko-architecture-drift-radar

Grant it access to your fork (repository permissions as requested by GitHub during install).

### 3) Open a demo PR
In your fork, create a pull request from a demo branch into your default branch (usually `main`).

- Demo branches are named: `demo/pr-XX-...`
- A list of scenarios will be tracked in: **DEMO_PRS.md** *(placeholder — to be added)*

### 4) View the report
Revieko will comment on the PR with:
- a short summary
- a link to the full HTML report

---

## Demo PR scenarios (placeholder)

We will add a set of intentionally-designed PRs that simulate common real-world risk patterns:

- hidden coupling across layers
- API boundary drift
- runtime side effects / state leaks
- performance regressions via algorithmic complexity
- “safe-looking” refactors with high blast radius

➡️ See **DEMO_PRS.md** *(to be added)*

---

## Need help?

- Documentation: https://synqra.tech/revieko-docs  
- GitHub App: https://github.com/apps/revieko-architecture-drift-radar  
- Contact (placeholder):  
  - Email: `hello@synqra.tech`  
  - LinkedIn: `https://www.linkedin.com/in/<your-handle>`  

*(Replace placeholders with your actual contacts.)*

---

## Upstream project (mitmproxy)

``mitmproxy`` is an interactive, SSL/TLS-capable intercepting proxy with a console
interface for HTTP/1, HTTP/2, and WebSockets.

``mitmdump`` is the command-line version of mitmproxy. Think tcpdump for HTTP.

``mitmweb`` is a web-based interface for mitmproxy.

Installation instructions (upstream):  
https://docs.mitmproxy.org/stable/overview-installation

Contributing guide (upstream):  
[CONTRIBUTING.md](./CONTRIBUTING.md)
