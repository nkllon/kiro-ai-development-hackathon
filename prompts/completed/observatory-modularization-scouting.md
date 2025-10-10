## Task: Scout Observatory/Directus Modularization Opportunities

### Objective
Gather enough information to propose a clean extraction of the observability/Directus stack into a standalone package. Focus on cataloging entry points, shared dependencies, and required services—do not modify code.

### Key Artifacts to Review
- `reports/makefile-system-validation-summary.md` – highlights Prometheus/Grafana dependencies.
- `src/beast_mode/observatory/ai_consultation/` and `src/beast_mode/directus_cms/` – core modules.
- `docs/recovery/archive-module-index.md` – see which pieces were archived.
- `reports/dev-test-report.md` – shows currently verified observability tests.

### Suggested Read-Only Checks
- `rg "Prometheus" src/` to find integration points.
- `rg "Directus" -n docs/ src/` to list configuration documentation.
- `python3 -m pytest tests/unit/beast_mode/directus_cms --collect-only` to confirm test coverage (do not run tests).
- `cat docker-compose*.yml | rg "(prometheus|grafana)" -n` to identify runtime expectations.

### Deliverable
Create a new markdown file `docs/recovery/observatory-modularization-notes.md` summarizing:
1. Core modules/files to include in the package.
2. External services required (Prometheus/Grafana/Nginx/etc.).
3. Shared utilities the package would need from `src/beast_mode`.
4. Potential migration steps (config, tests, docs).

No edits to existing code or configs—this is purely reconnaissance.
