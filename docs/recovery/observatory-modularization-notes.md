# Observatory/Directus Modularization Reconnaissance Notes

**Date**: 2025-10-09  
**Task**: Scout modularization opportunities for Observatory/Directus stack  
**Purpose**: Gather information to propose clean extraction into a standalone package  
**Scope**: Read-only reconnaissance—no code modifications

---

## Executive Summary

The Observatory and Directus CMS systems form a cohesive observability stack that could be extracted into a standalone package. This reconnaissance identified:

- **Core Modules**: 2 primary modules (Observatory AI Consultation + Directus CMS) with 52+ files
- **External Services**: 4 runtime dependencies (Prometheus, Grafana, Redis, PostgreSQL)
- **Shared Utilities**: Heavy reliance on `ReflectiveModule` and `BeastlyModule` from `src/rm_ddd/core` and `src/beast_mode/core`
- **Test Coverage**: 734+ tests across both modules (52 Directus, 682+ Observatory)
- **Migration Complexity**: Medium—requires careful handling of ReflectiveModule dependencies

---

## 1. Core Modules/Files to Include in Package

### 1.1 Observatory AI Consultation Module

**Location**: `src/beast_mode/observatory/ai_consultation/`  
**Files**: 26 Python files + tests

**Core Components**:
```
ai_consultation/
├── __init__.py                           # Main package exports
├── models.py                             # Data models (ProcessingMode, QueryPriority, etc.)
├── exceptions.py                         # Custom exceptions
├── interfaces.py                         # Service interfaces (ABC)
├── feature_flags.py                      # Feature flag management
├── circuit_breaker.py                    # Resilience patterns
├── health_checker.py                     # Health monitoring (21 tests)
├── visual_regression.py                  # Visual testing (22 tests)
├── doctor_status_manager.py              # "Doctor Is In/Out" state management
├── doctor_status_indicator.py            # Status indicator component
├── database.py                           # SQLite database management
├── status_broadcaster.py                 # WebSocket broadcasting
├── status_persistence.py                 # Status persistence layer
├── observatory_context_provider.py       # Metrics/alerts context provider
├── security_manager.py                   # RBAC & authentication
├── consultation_router.py                # Request routing logic
├── request_processor.py                  # Query processing pipeline
├── realtime_chat_engine.py              # Real-time chat support
├── llm_service.py                        # LLM provider abstraction
├── query_queue.py                        # Queue-based processing
├── batch_processor.py                    # Batch query optimization (23 tests)
├── email_notification_service.py         # Email notifications
├── knowledge_base_search.py              # KB search functionality
├── results_storage.py                    # Result caching/storage
├── repository.py                         # Data repository pattern
└── notification_integration.py           # Notification integration
```

**Key Dependencies**:
- Internal models and interfaces (self-contained within module)
- No direct imports from other `src.beast_mode` modules (good isolation!)
- Optional dependencies gracefully handled (PyJWT, selenium, etc.)

**Test Coverage**: 682+ tests collected (note: 9 import errors during collection)
- `test_batch_processor.py` - 23 tests
- `test_circuit_breaker.py` - 16 tests  
- `test_consultation_router.py` - 20 tests
- `test_database.py` - 7+ tests
- Plus: health_checker, visual_regression, status management tests

### 1.2 Directus CMS Module

**Location**: `src/beast_mode/directus_cms/`  
**Files**: 25+ Python files + tests

**Core Components**:
```
directus_cms/
├── __init__.py                           # Package exports
├── orchestrator.py                       # Main orchestrator
├── schema_manager.py                     # Database schema management
├── data_populator.py                     # Data population logic
├── database_utils.py                     # Database connection utilities
├── directus_client.py                    # Directus API client
├── api/
│   ├── __init__.py
│   ├── configurator.py                   # API configuration
│   ├── rest_config.py                    # REST API manager
│   └── graphql_config.py                 # GraphQL configuration
├── ui/
│   ├── __init__.py
│   ├── configurator.py                   # UI configuration
│   ├── navigation.py                     # Navigation setup
│   └── relationship_display.py           # Relationship UI
├── population/
│   ├── __init__.py
│   ├── orchestrator.py                   # Population orchestrator
│   └── spec_importer.py                  # Specification importer
├── error_prevention/
│   ├── __init__.py
│   ├── error_prevention.py               # Error prevention orchestrator
│   ├── api_handler.py                    # API error handling
│   ├── auth_validator.py                 # Authentication validation
│   └── schema_validator.py               # Schema validation
└── monitoring/
    ├── structured_logger.py              # Structured logging
    ├── health_monitor.py                 # Health monitoring
    ├── pdca_orchestrator.py              # PDCA lifecycle management
    └── backup_recovery.py                # Backup/recovery system
```

**Key Dependencies**:
- `src.rm_ddd.core.unified_reflective_module` (ReflectiveModule base class) - **CRITICAL**
- `src.beast_mode.core.beastly_module` (BeastlyModule for DirectusClient) - **IMPORTANT**
- `psycopg2` (optional PostgreSQL support)
- `requests` (Directus API client)

**Test Coverage**: 52 tests collected (all passed in collection phase)
- `test_data_populator.py` - 18 tests + integration test
- `test_schema_manager.py` - 18 tests + integration test
- `test_phase5_integration.py` - 16 tests (health, PDCA, backup/recovery)

### 1.3 Observatory Server & Infrastructure

**Additional Observatory Files** (beyond AI Consultation):
```
src/beast_mode/observatory/
├── server.py                             # Observatory web server
├── infrastructure_discovery.py           # Infrastructure scanning
├── openmetrics_discovery.py              # Prometheus metrics discovery
├── diagram_generator.py                  # Architecture diagram generation
├── feature_flag_manager.py               # Feature flag management
├── status_announcer.py                   # Status announcements
├── direct_status_broadcast.py            # Direct broadcasting
├── ace_reporter_factory.py               # ACE reporter factory pattern
├── enhanced_ace_reporter.py              # Enhanced ACE reporter
├── enhanced_ace_reporter_with_error_handling.py
├── monitoring/
│   └── metrics_collector.py              # Metrics collection
├── engagement/
│   ├── monitoring/
│   │   ├── prometheus_integration.py     # Engagement Prometheus integration
│   │   ├── health_integration.py         # Health check integration
│   │   └── engagement_metrics.py         # Engagement metrics
│   └── integration/
│       └── server_integration.py         # Server integration
└── static/
    └── data_insights.js                  # Frontend visualization
```

**Note**: The observatory has 192 files total (177 Python, 11 JavaScript, 4 HTML), suggesting significant additional functionality beyond AI Consultation. Full extraction scope needs further definition.

### 1.4 Prometheus Exporter Integration

**Location**: `src/beast_mode/monitoring/prometheus_exporter.py`  
**Size**: 1,165+ lines
**Purpose**: Prometheus metrics export endpoint

**Key Features**:
- Integrates with existing Beast Mode monitoring infrastructure
- Exposes `/metrics` HTTP endpoint for Prometheus scraping
- Graceful degradation when Prometheus client unavailable
- Counter, Gauge, Histogram, Summary metric types
- Performance monitoring system integration

**Integration Points**:
```python
from src.beast_mode.performance.performance_monitoring_system import PerformanceMonitoringSystem
```

**Known Issues** (per validation reports):
- ❌ Initialization error: `__init__() got an unexpected keyword argument 'prometheus_url'`
- ❌ Redis registration failed: missing `module_id` attribute
- ❌ Cleanup error: missing `logger` attribute in `__del__`

---

## 2. External Services Required

### 2.1 Prometheus (Metrics Collection)

**Service**: `prom/prometheus:latest`  
**Port**: 9090  
**Purpose**: Time-series metrics storage and querying

**Configuration**: `config/prometheus.yml`
```yaml
scrape_configs:
  - job_name: 'beast-mode'
    static_configs:
      - targets: ['beast-mode:8080']
    metrics_path: '/metrics'
    scrape_interval: 10s
```

**Data Volume**: `prometheus-data` (persistent storage)

**Required By**:
- Observatory metrics collection
- Performance monitoring
- Health checks and alerting
- AI Memory Palace event capture
- System architecture discovery

**Integration Files** (101 files reference Prometheus):
- `src/beast_mode/monitoring/prometheus_exporter.py`
- `src/beast_mode/monitoring/prometheus_config.py`
- `src/beast_mode/monitoring/test_prometheus_integration.py`
- `src/beast_mode/observatory/engagement/monitoring/prometheus_integration.py`
- `src/runtime_state_registry/collectors/prometheus_integration_collector.py`
- Various system architecture and monitoring modules

### 2.2 Grafana (Visualization)

**Service**: `grafana/grafana:latest`  
**Port**: 3000  
**Purpose**: Metrics visualization and dashboards

**Configuration**:
- Admin password: `GF_SECURITY_ADMIN_PASSWORD=admin`
- Datasources: `config/grafana/datasources/`
- Dashboards: `config/grafana/dashboards/`

**Data Volume**: `grafana-data` (persistent dashboards/config)

**Dependency**: Prometheus (as datasource)

**Optional Proxy**: `docker-compose.proxy.yml` includes nginx-based proxies for both Prometheus and Grafana to forward to remote instances.

### 2.3 Redis (Caching & State)

**Service**: `redis:7-alpine`  
**Port**: 6379  
**Purpose**: Distributed caching, session storage, state management

**Configuration**: `config/redis.conf`

**Data Volume**: `redis-data` (persistent storage)

**Required By**:
- Doctor status management (status broadcasting)
- Query queue management
- Batch processor caching
- Result caching
- Session management
- Distributed locking

**Health Check**: `redis-cli ping`

**Known Issues**:
- ❌ Redis registration failures due to missing `module_id` attribute in validators

### 2.4 PostgreSQL (Optional/Development)

**Service**: `postgres:15-alpine`  
**Port**: 5432  
**Purpose**: Relational database for advanced features (dev environment only)

**Configuration** (docker-compose.dev.yml):
```yaml
environment:
  POSTGRES_DB: beast_mode_dev
  POSTGRES_USER: beast_mode
  POSTGRES_PASSWORD: development
```

**Data Volume**: `postgres-dev-data`

**Usage**:
- Directus CMS can use PostgreSQL instead of SQLite
- Schema manager has optional `psycopg2` support
- Not required for production (SQLite is default)

### 2.5 SMTP/Email Service (Optional)

**Development**: `mailhog:latest` (port 1025/8025) in dev environment  
**Production**: External SMTP service

**Required By**:
- `email_notification_service.py` for AI consultation alerts
- Notification integration system

### 2.6 Nginx (Optional Proxy)

**Purpose**: Reverse proxy for Prometheus/Grafana (remote deployment)

**Configuration**:
- `config/nginx/prometheus-proxy.conf`
- `config/nginx/grafana-proxy.conf`

**Usage**: `docker-compose.proxy.yml` when services run on separate hosts

---

## 3. Shared Utilities the Package Would Need

### 3.1 ReflectiveModule (Critical Dependency)

**Location**: `src/rm_ddd/core/unified_reflective_module.py`  
**Used By**: ALL Directus CMS modules, plus DirectusClient

**Imports**:
```python
from src.rm_ddd.core.unified_reflective_module import (
    ReflectiveModule,
    ModuleHealth,
    ModuleStatus,
    ModuleCapability,
    GracefulDegradationResult,
)
```

**Purpose**: 
- Base class providing systematic execution patterns
- Health reporting and graceful degradation
- Capability registration and discovery
- Module lifecycle management
- Observation emission

**Files Dependent on ReflectiveModule** (11+ in Directus alone):
- `directus_cms/orchestrator.py`
- `directus_cms/schema_manager.py`
- `directus_cms/data_populator.py`
- `directus_cms/ui/*.py` (3 files)
- `directus_cms/population/*.py` (2 files)
- `directus_cms/monitoring/*.py` (2 files)
- `directus_cms/api/rest_config.py`

**Migration Challenge**: HIGH
- Either bundle ReflectiveModule with the package
- Or make it an external dependency/requirement
- Or refactor to remove ReflectiveModule dependency (significant work)

**Recommendation**: Bundle a lightweight version of ReflectiveModule into the extracted package, or make `rm_ddd.core` a separate installable dependency.

### 3.2 BeastlyModule (Important Dependency)

**Location**: `src/beast_mode/core/beastly_module.py`  
**Used By**: `DirectusClient` (extends BeastlyModule)

**Purpose**:
- Enhanced ReflectiveModule with distributed tracing (Jaeger)
- Observation emission with trace correlation
- Performance monitoring integration
- Graceful degradation when tracing unavailable

**Inheritance Chain**:
```
BeastlyModule → ReflectiveModule
```

**Optional Dependencies**:
- `src.beast_mode.tracing.tracer` (graceful fallback if unavailable)

**Impact**: Medium—only used by DirectusClient, could be refactored to use plain ReflectiveModule.

### 3.3 Other Beast Mode Utilities

**Analysis**: AI Consultation module has NO direct imports from other `src.beast_mode` modules! This is excellent for extraction.

**Directus CMS imports**:
- `src.beast_mode.core.beastly_module` (DirectusClient only)
- Internal dependencies: `schema_manager.py` ↔ `database_utils.py` ↔ `data_populator.py`

**Conclusion**: Observatory AI Consultation is well-isolated. Directus has minimal external dependencies (just ReflectiveModule + BeastlyModule).

### 3.4 Python Package Dependencies

**Required** (from imports and usage):
```
# Core
pydantic>=2.0                # Data validation (12 deprecation warnings to fix)
aiosqlite                    # Async SQLite support
asyncio                      # Async/await patterns
logging                      # Standard logging

# External services
redis                        # Redis client
requests                     # HTTP client for Directus API

# Monitoring
prometheus-client            # Prometheus metrics export (optional)

# Optional
psycopg2                     # PostgreSQL support (optional)
PyJWT                        # JWT authentication (optional, graceful degradation)
selenium                     # Visual regression testing (optional)

# Development/Testing
pytest>=8.4                  # Testing framework
pytest-asyncio               # Async test support
pytest-cov                   # Coverage reporting
```

**Pydantic Issue**: 12 deprecation warnings about `json_encoders`. Need to migrate to custom serializers before Pydantic V3.0.

---

## 4. Potential Migration Steps

### 4.1 Phase 1: Extract Core Modules (Weeks 1-2)

**Tasks**:
1. Create new package structure:
   ```
   observatory-package/
   ├── pyproject.toml
   ├── README.md
   ├── src/
   │   └── kiro_observatory/
   │       ├── __init__.py
   │       ├── ai_consultation/          # Copy from src/beast_mode/observatory/ai_consultation/
   │       ├── directus/                  # Copy from src/beast_mode/directus_cms/
   │       ├── monitoring/                # Copy prometheus_exporter + related
   │       └── core/                      # Extract ReflectiveModule/BeastlyModule
   └── tests/
       ├── unit/
       └── integration/
   ```

2. Copy source files:
   - AI Consultation module (26 files)
   - Directus CMS module (25 files)
   - Prometheus exporter (1 file)
   - Observatory server components (as needed)

3. Extract shared utilities:
   - Option A: Bundle minimal `ReflectiveModule` implementation
   - Option B: Create `kiro-core` separate package for `rm_ddd.core`
   - Option C: Remove ReflectiveModule dependency (refactor)

4. Update imports:
   ```python
   # From:
   from src.beast_mode.observatory.ai_consultation import ...
   from src.beast_mode.directus_cms import ...
   from src.rm_ddd.core.unified_reflective_module import ...
   
   # To:
   from kiro_observatory.ai_consultation import ...
   from kiro_observatory.directus import ...
   from kiro_observatory.core import ReflectiveModule, ...
   ```

5. Create `pyproject.toml`:
   ```toml
   [project]
   name = "kiro-observatory"
   version = "0.1.0"
   description = "Observatory monitoring and Directus CMS package"
   dependencies = [
       "pydantic>=2.0,<3.0",
       "aiosqlite>=0.17.0",
       "redis>=4.0.0",
       "requests>=2.28.0",
       "prometheus-client>=0.15.0",
   ]
   
   [project.optional-dependencies]
   postgresql = ["psycopg2>=2.9.0"]
   auth = ["PyJWT>=2.6.0"]
   testing = ["selenium>=4.0.0"]
   ```

**Challenges**:
- ReflectiveModule migration decision
- Import path updates throughout
- Ensuring no circular dependencies

### 4.2 Phase 2: Migrate Configuration (Week 3)

**Tasks**:
1. Extract configuration files:
   - `config/prometheus.yml` → package default config
   - `config/redis.conf` → package default config
   - Feature flags config (`config/ai_consultation_feature_flags.json`)
   - Environment variable templates (`.env.example`)

2. Create configuration module:
   ```python
   # kiro_observatory/config.py
   class ObservatoryConfig:
       PROMETHEUS_URL: str = "http://localhost:9090"
       GRAFANA_URL: str = "http://localhost:3000"
       REDIS_URL: str = "redis://localhost:6379"
       DATABASE_PATH: str = "data/observatory.db"
       # ... etc
   ```

3. Update configuration loading:
   - Support environment variables
   - Support config files (YAML/TOML)
   - Provide sensible defaults
   - Document all config options

4. Create Docker Compose templates:
   - `docker-compose.observatory.yml` (production stack)
   - `docker-compose.observatory-dev.yml` (development stack)

**Deliverables**:
- Configuration documentation
- Environment variable guide
- Docker deployment guide

### 4.3 Phase 3: Migrate Tests (Week 4)

**Tasks**:
1. Copy test files:
   - `tests/unit/beast_mode/observatory/ai_consultation/` → `tests/unit/ai_consultation/`
   - `tests/unit/beast_mode/directus_cms/` → `tests/unit/directus/`
   - Associated fixtures and test utilities

2. Update test imports:
   ```python
   # From:
   from src.beast_mode.observatory.ai_consultation import ...
   
   # To:
   from kiro_observatory.ai_consultation import ...
   ```

3. Fix test collection issues:
   - Resolve 9 import errors in Observatory tests
   - Ensure all 52 Directus tests pass
   - Ensure 682+ Observatory tests pass

4. Add integration tests:
   - Test with real Prometheus/Grafana/Redis
   - Test Docker Compose stack deployment
   - Test configuration loading
   - Test graceful degradation scenarios

5. Update `pytest.ini`:
   ```ini
   [pytest]
   testpaths = tests
   python_files = test_*.py
   python_classes = Test*
   python_functions = test_*
   asyncio_mode = auto
   ```

**Challenges**:
- Mocking external services properly
- Fixing existing import errors
- Maintaining high test coverage (≥90%)

### 4.4 Phase 4: Documentation (Week 5)

**Tasks**:
1. Create comprehensive README:
   - Overview of Observatory/Directus stack
   - Installation instructions
   - Quick start guide
   - Architecture overview
   - Configuration guide

2. API documentation:
   - All public classes and functions
   - Usage examples
   - Integration patterns

3. Deployment guides:
   - Docker Compose deployment
   - Kubernetes deployment (optional)
   - Service dependencies setup
   - Monitoring setup (Prometheus/Grafana)

4. Migration guide:
   - For existing Beast Mode users
   - Breaking changes from extraction
   - Import path updates
   - Configuration migration

5. Developer guide:
   - Contributing guidelines
   - Testing procedures
   - Release process
   - Architecture deep-dive

**Reference Documentation** (already exists):
- `docs/recovery/beast-mode-module-restoration-guide.md`
- `reports/makefile-system-validation-summary.md` (observability issues)
- `reports/dev-test-report.md` (test baseline)
- Various CMS architecture docs in `docs/cms/`

### 4.5 Phase 5: Address Known Issues (Week 6)

**Critical Fixes**:

1. **Prometheus Exporter Initialization** (`src/beast_mode/monitoring/prometheus_exporter.py:163`):
   ```python
   # ERROR: __init__() got an unexpected keyword argument 'prometheus_url'
   # Fix: Update parameter name or constructor signature
   ```

2. **Redis Registration** (multiple files):
   ```python
   # ERROR: '<Validator>' object has no attribute 'module_id'
   # Fix: Add module_id to all validator classes
   ```

3. **PrometheusExporter Cleanup** (`src/beast_mode/monitoring/prometheus_exporter.py:1130`):
   ```python
   # ERROR: AttributeError: 'PrometheusExporter' object has no attribute 'logger'
   # Fix: Check for logger existence in __del__ method
   ```

4. **Pydantic Deprecation Warnings** (12 instances):
   ```python
   # WARNING: json_encoders is deprecated
   # Fix: Migrate to custom serializers
   # See: https://docs.pydantic.dev/2.11/concepts/serialization/#custom-serializers
   ```

5. **Test Import Errors** (9 errors during Observatory test collection):
   - Investigate and resolve import path issues
   - Update stale test fixtures
   - Fix API compatibility issues

**Priority**: 
- Items 1-3 are non-blocking (observability only)
- Item 4 is important (Pydantic V3.0 prep)
- Item 5 is critical for test suite health

### 4.6 Phase 6: Publishing & CI/CD (Week 7)

**Tasks**:
1. Set up PyPI publishing:
   - Create PyPI account/project
   - Configure `twine` for uploads
   - Test on TestPyPI first

2. Create GitHub Actions workflows:
   ```yaml
   # .github/workflows/test.yml
   name: Test
   on: [push, pull_request]
   jobs:
     test:
       runs-on: ubuntu-latest
       services:
         redis:
           image: redis:7-alpine
         prometheus:
           image: prom/prometheus:latest
       steps:
         - uses: actions/checkout@v3
         - name: Run tests
           run: pytest tests/ --cov=src --cov-report=term-missing
   ```

3. Set up continuous deployment:
   - Auto-publish on version tags
   - Generate release notes
   - Update documentation on releases

4. Create versioning strategy:
   - Semantic versioning (SemVer)
   - Changelog maintenance
   - Migration guides for breaking changes

**Deliverables**:
- Published package on PyPI
- CI/CD pipeline functional
- Release automation

---

## 5. Package Scope Options

### Option A: Minimal (AI Consultation Only)

**Includes**:
- `src/beast_mode/observatory/ai_consultation/` (26 files)
- Minimal ReflectiveModule implementation
- Prometheus/Redis/SQLite support

**Excludes**:
- Directus CMS
- Full Observatory server
- Grafana integration

**Pros**: Faster extraction, cleaner scope  
**Cons**: Incomplete observability stack

### Option B: Moderate (AI Consultation + Directus)

**Includes**:
- AI Consultation (26 files)
- Directus CMS (25 files)
- Prometheus exporter
- ReflectiveModule + BeastlyModule
- All shared utilities

**Excludes**:
- Full Observatory server components (192 files)
- System architecture discovery
- Other Beast Mode monitoring modules

**Pros**: Cohesive package, manageable scope  
**Cons**: Missing some Observatory features

**Recommendation**: ⭐ **THIS OPTION** — Best balance of functionality and extraction effort.

### Option C: Complete (Full Observatory Stack)

**Includes**:
- Everything in Option B
- Full Observatory server (192 files)
- Infrastructure discovery
- Diagram generation
- Engagement monitoring
- All static assets (HTML/JS)

**Pros**: Complete feature set  
**Cons**: Very large scope, longer extraction time, more dependencies

---

## 6. Risk Assessment

### 6.1 Technical Risks

| Risk | Severity | Likelihood | Mitigation |
|------|----------|------------|------------|
| ReflectiveModule dependency complexity | HIGH | HIGH | Bundle minimal version or create separate package |
| Test import errors (9 in Observatory) | MEDIUM | HIGH | Fix before extraction, ensure clean test baseline |
| Prometheus integration issues | MEDIUM | MEDIUM | Address known bugs first, test thoroughly |
| Configuration management complexity | MEDIUM | MEDIUM | Create comprehensive config module |
| Breaking changes for existing users | HIGH | CERTAIN | Provide migration guide, maintain compatibility layer |

### 6.2 Operational Risks

| Risk | Severity | Likelihood | Mitigation |
|------|----------|------------|------------|
| Service dependency management | HIGH | MEDIUM | Provide Docker Compose stack, document extensively |
| Redis/Prometheus version compatibility | MEDIUM | MEDIUM | Test with multiple versions, document requirements |
| Production deployment complexity | MEDIUM | HIGH | Create deployment guides, provide examples |
| Performance regression | MEDIUM | LOW | Maintain performance tests, benchmark before/after |

### 6.3 Maintenance Risks

| Risk | Severity | Likelihood | Mitigation |
|------|----------|------------|------------|
| Divergence from Beast Mode codebase | HIGH | HIGH | Maintain sync process, shared issue tracking |
| Dependency version conflicts | MEDIUM | MEDIUM | Pin versions, test dependency upgrades |
| Documentation drift | MEDIUM | HIGH | Auto-generate docs, CI checks for doc updates |

---

## 7. Estimated Effort

### Time Estimates (Conservative)

| Phase | Duration | Key Activities |
|-------|----------|----------------|
| Phase 1: Extract core modules | 2 weeks | Source file migration, import updates, initial testing |
| Phase 2: Migrate configuration | 1 week | Config extraction, environment setup, Docker templates |
| Phase 3: Migrate tests | 1 week | Test migration, fixing import errors, integration tests |
| Phase 4: Documentation | 1 week | README, API docs, deployment guides, migration guide |
| Phase 5: Fix known issues | 1 week | Prometheus bugs, Pydantic updates, test fixes |
| Phase 6: Publishing & CI/CD | 1 week | PyPI setup, GitHub Actions, release automation |
| **Total** | **7 weeks** | **For Option B (Moderate scope)** |

### Dependencies & Parallel Work

- Phases 1-2 can overlap (config during module extraction)
- Phase 3 depends on Phase 1 completion
- Phase 4 can start during Phase 3
- Phase 5 can run parallel to Phases 1-4
- Phase 6 is final and sequential

### Team Requirements

- 1-2 developers for extraction work
- 1 DevOps engineer for Docker/deployment
- 1 technical writer for documentation (part-time)
- QA/testing support during Phase 3

---

## 8. Success Criteria

### Must-Have (Launch Blockers)

- ✅ All 52 Directus tests pass
- ✅ All 682+ Observatory tests pass (after fixing 9 import errors)
- ✅ Package installable via `pip install kiro-observatory`
- ✅ Docker Compose stack works out-of-the-box
- ✅ Configuration via environment variables
- ✅ Core documentation complete (README, API docs)
- ✅ Migration guide for Beast Mode users
- ✅ Test coverage ≥90%

### Should-Have (Post-Launch)

- 📋 Prometheus bugs fixed (3 known issues)
- 📋 Pydantic V3.0 compatibility (fix 12 warnings)
- 📋 Kubernetes deployment guide
- 📋 Performance benchmarks documented
- 📋 CI/CD pipeline with auto-publishing
- 📋 Comprehensive integration test suite

### Nice-to-Have (Future Enhancements)

- 💡 Helm charts for Kubernetes
- 💡 Monitoring dashboard templates
- 💡 CLI tool for common operations
- 💡 Plugin architecture for extensibility
- 💡 Example integrations with popular frameworks

---

## 9. Next Steps (Recommendations)

### Immediate Actions (Week 1)

1. **Decision**: Choose scope (recommend Option B: Moderate)
2. **Spike**: Test ReflectiveModule extraction viability
   - Create minimal standalone ReflectiveModule
   - Test with DirectusClient
   - Validate no circular dependencies
3. **Fix**: Resolve 9 Observatory test import errors
   - Document root causes
   - Fix before extraction begins
4. **Document**: Create detailed extraction plan
   - File-by-file migration checklist
   - Import path mapping document
   - Risk mitigation strategies

### Short-Term Actions (Weeks 2-4)

1. Execute Phase 1 (core module extraction)
2. Execute Phase 2 (configuration migration)
3. Execute Phase 3 (test migration)
4. Begin Phase 4 (documentation)

### Medium-Term Actions (Weeks 5-7)

1. Complete Phase 4 (documentation)
2. Execute Phase 5 (fix known issues)
3. Execute Phase 6 (publishing & CI/CD)
4. Internal beta testing with Beast Mode users

### Long-Term Actions (Post-Launch)

1. Gather user feedback
2. Address post-launch issues
3. Plan feature enhancements
4. Consider extracting other Beast Mode modules

---

## 10. Appendix: File Inventory

### Core Files Count

| Component | Files | Tests | Total Lines (Est.) |
|-----------|-------|-------|-------------------|
| AI Consultation | 26 | 682+ tests | 8,000+ |
| Directus CMS | 25 | 52 tests | 6,000+ |
| Prometheus Exporter | 1 | Integration tests | 1,165+ |
| ReflectiveModule (extract) | 1 | N/A | 500+ (minimal) |
| BeastlyModule (extract) | 1 | N/A | 150+ (minimal) |
| Configuration | New | New | 200+ |
| **Total** | **~55** | **734+** | **~16,000+** |

### External Service Dependencies

- ✅ Redis 7-alpine (required)
- ✅ Prometheus latest (required)
- ✅ Grafana latest (recommended)
- ⚠️ PostgreSQL 15-alpine (optional, dev only)
- ⚠️ Mailhog latest (optional, dev only)
- ⚠️ Nginx alpine (optional, proxy deployment)

### Key Configuration Files

- `config/prometheus.yml` (metrics scraping)
- `config/redis.conf` (Redis configuration)
- `config/ai_consultation_feature_flags.json` (feature flags)
- `.env.example` (environment template)
- `docker-compose.yml` (production stack)
- `docker-compose.dev.yml` (development stack)
- `docker-compose.proxy.yml` (proxy deployment)

---

## Conclusion

**Feasibility**: HIGH — The Observatory/Directus stack is well-isolated and extraction is viable.

**Complexity**: MEDIUM — Primary challenge is ReflectiveModule dependency management.

**Recommendation**: Proceed with **Option B (Moderate scope)** including AI Consultation + Directus CMS.

**Timeline**: 7 weeks for full extraction, testing, documentation, and publishing.

**Next Decision Point**: Choose extraction scope and resolve ReflectiveModule dependency strategy (Week 1).

---

**End of Reconnaissance Report**  
**No code modifications made during this investigation.**

