# UPSTREAM.md

## Upstream Source

This repository is a fork of the original **mitmproxy** project:

* Upstream repository: [https://github.com/mitmproxy/mitmproxy](https://github.com/mitmproxy/mitmproxy)
* Original authors and contributors: mitmproxy project maintainers
* License: MIT License (see `LICENSE` file in this repository)

At the time of forking, this repository was based on the upstream `main` branch at the commit referenced in the fork history.

---

## Purpose of This Fork

This fork is maintained by SynqraTech as a **demonstration environment** for structural risk and architectural drift analysis.

The goal of this repository is to:

* Provide a real-world Python backend codebase for evaluation
* Introduce intentionally designed pull request scenarios
* Demonstrate how architectural risk can exist even when CI passes and tests are green
* Showcase automated structural analysis tooling in a realistic context

This repository is **not an official mirror** of mitmproxy and is not affiliated with or endorsed by the original maintainers.

---

## Modifications

Compared to upstream, this repository may:

* Remove non-essential directories (e.g. docs, release tooling, web UI)
* Simplify the structure to focus on backend logic
* Add dedicated `demo/*` branches containing intentionally risky changes
* Include additional documentation describing demonstration scenarios

Core project license terms remain unchanged.

---

## License Notice

The original mitmproxy project is licensed under the MIT License.
This fork preserves the original license in full.

All modifications in this repository are distributed under the same MIT License terms unless explicitly stated otherwise.
