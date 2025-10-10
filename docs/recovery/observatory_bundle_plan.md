# Observatory Bundle Extraction Plan

**Date**: 2025-10-09  
**Author**: Observatory Modularization Sprint  
**Source Recon**: `docs/recovery/observatory-modularization-notes.md`, `reports/dev-test-report.md`

---

## 1. Overview

The observability stack currently lives in two top-level packages:

- `src/beast_mode/observatory/ai_consultation/`
- `src/beast_mode/directus_cms/`

The goal is to extract these into a standalone, installable bundle that can be reused across projects and developed independently of the core Beast Mode framework. This document outlines the proposed package structure, required dependencies, and phased migration steps.

---

## 2. Components to Include

### 2.1 Observatory AI Consultation

| Category | Key Files |
|----------|-----------|
| Core | `__init__.py`, `models.py`, `interfaces.py`, `exceptions.py`, `feature_flags.py` |
| Resilience | `circuit_breaker.py`, `health_checker.py`, `status_persistence.py`, `status_broadcaster.py` |
| Consultation Flow | `consultation_router.py`, `request_processor.py`, `realtime_chat_engine.py`, `llm_service.py`, `query_queue.py`, `batch_processor.py` |
| Support Services | `doctor_status_manager.py`, `observatory_context_provider.py`, `security_manager.py`, `email_notification_service.py`, `knowledge_base_search.py`, `results_storage.py` |
| Tooling | `visual_regression.py`, `doctor_status_indicator.py`, `database.py`, `repository.py`, `feature_flags.py` |
| Tests | `tests/unit/beast_mode/observatory/ai_consultation/...` (682+ tests) |

### 2.2 Directus CMS

| Category | Key Files |
|----------|-----------|
| Core | `__init__.py`, `orchestrator.py`, `schema_manager.py`, `data_populator.py`, `directus_client.py` |
| Database | `database_utils.py`, `population/`, `error_prevention/` |
| API | `api/configurator.py`, `api/graphql_config.py`, `api/rest_config.py` |
| UI | `ui/configurator.py`, `ui/navigation.py`, `ui/relationship_display.py` |
| Monitoring | `monitoring/structured_logger.py`, `monitoring/health_monitor.py`, `monitoring/pdca_orchestrator.py`, `monitoring/backup_recovery.py` |
| Tests | `tests/unit/beast_mode/directus_cms/...` (52 tests) |

---

## 3. External Dependencies

| Service / Tool | Purpose | Notes |
|----------------|---------|-------|
| Prometheus | Metrics scraping | Currently accessed via `PrometheusExporter`; bundle should expose CLI commands to stand up a local instance or connect to remote |
| Grafana | Dashboard visualization | Optional but recommended; examples live in `docker-compose` files |
| Redis | Queue + persistence | Used by AI Consultation components (`status_persistence`, `query_queue`) |
| PostgreSQL | Directus database | Required for Directus CMS operations; SQLite fallback for some workflows |
| Selenium + Chrome | Visual regression tests | Optional; controlled via `feature_flags` |
| Email SMTP | Notification service | Optional; fallback to logging if unavailable |

Bundle tooling should ship a set of Docker Compose profiles to provision the above locally, while also supporting “remote service” configuration via environment variables.

---

## 4. Shared Utilities & Interfaces

| Dependency | Location | Usage | Extraction Strategy |
|------------|----------|-------|---------------------|
| `ReflectiveModule`, `ModuleCapability` | `src/rm_ddd/core/unified_reflective_module.py` | All major components inherit from this base | Ship a lightweight copy (`observatory_bundle/reflection/`) or depend on a separately published `reflective-core` package |
| `BeastlyModule` | `src/beast_mode/core/beastly_module.py` | Used by Directus client | Either duplicate minimal functionality or factor into a shared dependency |
| `feature_flags` infrastructure | Already self-contained (ai_consultation) | Used for toggles and rollbacks | Keep as part of bundle |
| Logging utilities | Standard library + structured logger | No external dependencies | Keep as is |

**Recommendation**: Extract `ReflectiveModule` + `BeastlyModule` into a micro-package (`reflective-core`) shared between Beast Mode and Observatory Bundle to avoid duplication.

---

## 5. Proposed Package Layout

```
observatory-bundle/
├── pyproject.toml / setup.cfg
├── README.md
├── LICENSE
├── observatory_bundle/
│   ├── __init__.py
│   ├── reflection/                      # Optional shared ReflectiveModule copy
│   ├── observatory/
│   │   ├── __init__.py
│   │   ├── ai_consultation/             # Direct copy of current observatory module
│   │   └── monitoring/                  # Prometheus exporter shims, status CLI
│   └── directus/
│       ├── __init__.py
│       └── cms/                         # Directus CMS module
├── cli/
│   ├── __init__.py
│   └── main.py (entry point: `observatory-bundle`)
├── docker/
│   ├── docker-compose.dev.yml
│   ├── docker-compose.observability.yml
│   └── docker-compose.directus.yml
├── docs/
│   ├── overview.md
│   ├── configuration.md
│   ├── observability-guide.md
│   └── directus-guide.md
└── tests/
    ├── observatory/
    └── directus/
```

CLI Commands to expose:
- `observatory-bundle up` – launch Docker services locally
- `observatory-bundle status` – health checks for Prometheus/Grafana/Directus
- `observatory-bundle migrate` – Directus schema setup
- `observatory-bundle visual-test` – run visual regression suite

---

## 6. Migration Steps

### Phase 1 – Preparation
1. Extract `ReflectiveModule` + `BeastlyModule` into shared dependency (or create local copy).
2. Confirm observatory/directus tests pass in current repo (baseline already established).
3. Document environment variables required by both modules.

### Phase 2 – Package Skeleton
1. Scaffold new repository structure (`observatory-bundle/`).
2. Copy modules into `observatory_bundle/observatory` and `observatory_bundle/directus`.
3. Copy tests into corresponding `tests/` subdirectories.
4. Add pyproject metadata with dependency list (see Section 3).

### Phase 3 – Integration
1. Implement CLI entry point for service management.
2. Provide Docker Compose profiles for local Prometheus/Grafana/Directus.
3. Wire up configuration (YAML/ENV) to toggle local vs. remote services.

### Phase 4 – Backward Compatibility
1. In beast_mode repo, replace direct imports with bundle imports:
   - e.g., `from observatory_bundle.observatory.ai_consultation ...`
2. Provide transitional shims (deprecated warnings) to ease migration.
3. Update `Makefile` targets to call bundle CLI where appropriate.

### Phase 5 – Documentation & Release
1. Draft user guides (`docs/observability-guide.md`, `docs/directus-guide.md`).
2. Publish to PyPI (version 0.1.0) and tag repo.
3. Update Beast Mode documentation to reference new bundle.

---

## 7. Known Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Tight coupling with `ReflectiveModule` | Extraction blocked | Extract core reflective helpers into shared package first |
| Runtime dependencies heavy (Prometheus/Grafana) | Harder local setup | Provide Docker Compose + remote-service configuration options |
| Large test suite | Slower CI | Maintain “quick smoke test” subset plus full suite in nightly pipeline |
| Configuration drift | Misaligned env vars | Centralize configs under `observatory_bundle/config/` with templates |

---

## 8. Next Actions
1. Extract or publish `ReflectiveModule` foundation (`reflective-core` package).
2. Stand up new repo with skeleton layout.
3. Copy modules/tests and run baseline tests in isolation.
4. Implement CLI and Docker tooling.
5. Coordinate release plan with Beast Mode maintainers.

---

This plan can be refined once the discovery prompts finish and the dependency matrix is complete, but it provides a concrete roadmap to begin the extraction effort immediately.
