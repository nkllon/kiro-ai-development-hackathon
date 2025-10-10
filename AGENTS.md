# Repository Guidelines

## Project Structure & Module Organization
- `src/` houses production code; key domains include `src/beast_mode` (agent lifecycle), `src/rm_ddd` (ReflectiveModule core), `src/dag_orchestration` (graph governance), and `src/repository_discovery` (Git integration).
- `tests/` mirrors the `src` layout with `unit/`, `integration/`, and feature-specific suites; place new tests beside the feature they cover.
- `examples/` contains runnable demos (`examples/quick_start/`) that should stay green; update when changing surfaced APIs.
- `docs/` captures architecture, governance, and security references; link new specs in `docs/developer-guide/`.
- `src/makefile_toolkit/` packages the Makefile system tester, safety validator, and performance optimizer for reuse beyond this repo; legacy shims live in `scripts/` for compatibility.
- `scripts/` and `packages/` provide automation and reusable tooling; prefer extending these rather than duplicating logic.

## Build, Test, and Development Commands
```bash
make install          # bootstrap dependencies and .env
make quick-start      # run the demo agent for smoke verification
make dev-test         # targeted developer test run (pytest)
make dev-lint         # ruff lint pass; fails on warnings
make dev-format       # black --check enforcement
pytest -m "not slow"  # manual run excluding slow suites
pytest --cov=src --cov-report=term-missing  # coverage verification (target ≥90%)
```
Run from the repository root; container stacks live in `docker/` and `deployment/`.

## Coding Style & Naming Conventions
- Python is formatted with 4-space indentation, `black` line length 88, and `ruff` for lint/organisational checks.
- Type hints are required; enable `mypy` locally (`mypy src/ tests/`) before review.
- Modules and files use `snake_case`, classes `PascalCase`, constants `UPPER_SNAKE`, and tests `test_<feature>.py`.
- Document public APIs with concise docstrings; prefer module-level factories over ad-hoc scripts.

## Testing Guidelines
- Write unit tests in `tests/unit/<domain>/` and mirror complex flows in `tests/integration/`.
- Use pytest markers from `pytest.ini` (`@pytest.mark.slow`, `@pytest.mark.integration`) to classify scope.
- Maintain ≥90% coverage for touched modules and update `tests/fixtures/` helpers when altering shared schemas.

## Commit & Pull Request Guidelines
- Follow recent history: imperative summaries with optional emoji or prefixes (`feat:`, `fix:`) that describe scope, e.g. `feat: streamline DAG orchestration checks`.
- Reference issues with `Closes #123` in commit bodies or PR descriptions.
- Before opening a PR, run `make dev-lint`, `make dev-test`, and include output plus security checklist items in `.github/pull_request_template.md`.
- PRs should link impacted docs, note configuration updates, and attach screenshots for UI/observability changes.

## Security & Configuration
- Never commit secrets; configure `.env` via `.env.example` and document any new variables in `docs/security/SECURITY.md`.
- When integrating services, reuse helpers in `src/security/` and `scripts/deployment/` for credential handling.
- Validate observability changes with `make observatory-status` and log outcomes in `docs/operational-workflows/`.
