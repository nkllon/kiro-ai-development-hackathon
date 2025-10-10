## Draft Observability/Directus Bundle Plan

### Goal
Using `docs/recovery/observatory-modularization-notes.md`, outline a concrete extraction plan:

1. Package structure (`observatory-bundle/`, setup, CLI entry point).
2. Required modules and shared utilities.
3. Environment/service requirements (Prometheus, Grafana, Nginx, Redis).
4. Migration steps: code copy/move, config updates, Makefile targets, docs/tests.

### Deliverable
Create a new doc `docs/recovery/observatory_bundle_plan.md` containing:
- Overview
- File inclusion list
- Dependency matrix
- Proposed Make target / CLI commands
- Work breakdown (phased extraction steps)
