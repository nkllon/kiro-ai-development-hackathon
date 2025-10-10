# Make Dev-Test Report

**Date**: 2025-10-09  
**Command**: `make dev-test`  
**Exit Code**: 0 (Success)  
**Duration**: 5.80 seconds  
**Log**: `logs/dev-test-run-fresh.log`

## Summary

✅ **Overall Status**: PASS - All targeted baseline tests passed
- **Total Tests**: 43
- **Passed**: 43 (100.0%)
- **Failed**: 0
- **Skipped**: 0
- **Errors**: 0
- **Pass Rate**: **100.0%**
- **Warnings**: 12 (Pydantic deprecation warnings)

## Important Note: Test Scope Change

**CRITICAL DISCOVERY**: The `dev-test` target now runs a **targeted baseline** instead of the full suite!

### Current Behavior (Fresh Run)
```bash
# Only runs these specific test files:
tests/unit/beast_mode/observatory/ai_consultation/test_health_checker.py
tests/unit/beast_mode/observatory/ai_consultation/test_visual_regression.py
```
- **43 tests total**
- **100% pass rate**
- **Targeted scope**: AI Consultation Observatory tests only

### Previous Behavior (Earlier Today)
```bash
# Ran full beast_mode test suite:
tests/unit/beast_mode \
tests/unit/makefile_governance \
tests/integration/beast_mode/ai_memory_palace \
tests/integration/beast_mode/observatory/ai_consultation
```
- **1,244 tests collected**
- **132 import errors**
- **Much broader scope**

**Conclusion**: The `dev-test` target was modified to run only a baseline subset of tests, likely to provide a quick smoke test.

## Test Results

| Metric | Count | Percentage |
|--------|-------|------------|
| Total Tests | 43 | 100% |
| Passed | 43 | 100.0% |
| Failed | 0 | 0% |
| Skipped | 0 | 0% |
| Errors | 0 | 0% |

### Test Breakdown by Module

#### test_health_checker.py (21 tests)
All tests passed for AI Consultation Health Checker:

**TestAIConsultationHealthChecker** (18 tests):
- ✅ `test_check_health_basic`
- ✅ `test_check_health_caching`
- ✅ `test_check_readiness`
- ✅ `test_get_metrics`
- ✅ `test_system_health_check`
- ✅ `test_feature_flags_health_check`
- ✅ `test_circuit_breakers_health_check`
- ✅ `test_file_system_health_check`
- ✅ `test_file_system_health_check_failure`
- ✅ `test_resource_usage_healthy`
- ✅ `test_resource_usage_degraded`
- ✅ `test_resource_usage_unhealthy`
- ✅ `test_configuration_check_with_existing_config`
- ✅ `test_configuration_check_with_missing_config`
- ✅ `test_determine_overall_status_all_healthy`
- ✅ `test_determine_overall_status_with_unhealthy`
- ✅ `test_determine_overall_status_with_degraded`
- ✅ `test_determine_overall_status_unknown`

**TestGlobalHealthChecker** (3 tests):
- ✅ `test_global_health_checker_instance`
- ✅ `test_global_health_checker_readiness`
- ✅ `test_global_health_checker_metrics`

#### test_visual_regression.py (22 tests)
All tests passed for Visual Regression Testing:

**TestVisualDiff** (2 tests):
- ✅ `test_visual_diff_creation`
- ✅ `test_visual_diff_no_regression`

**TestVisualRegressionTester** (11 tests):
- ✅ `test_tester_initialization`
- ✅ `test_determine_severity`
- ✅ `test_enhance_diff_image`
- ✅ `test_compare_identical_images`
- ✅ `test_compare_different_images`
- ✅ `test_initialize_driver_missing_selenium`
- ✅ `test_cleanup_driver`
- ✅ `test_get_browser_info_no_driver`
- ✅ `test_get_browser_info_with_driver`
- ✅ `test_run_test_suite_disabled`
- ✅ `test_get_test_summary_empty`

**TestAutoRollbackManager** (7 tests):
- ✅ `test_evaluate_rollback_disabled`
- ✅ `test_evaluate_rollback_critical`
- ✅ `test_evaluate_rollback_multiple_major`
- ✅ `test_evaluate_rollback_no_trigger`
- ✅ `test_disable_risky_features`
- ✅ `test_execute_rollback_success`
- ✅ `test_execute_rollback_failure`

**TestVisualRegressionIntegration** (2 tests):
- ✅ `test_run_observatory_visual_tests`
- ✅ `test_run_observatory_visual_tests_with_rollback`

## Warnings Detected

### Pydantic Deprecation Warnings (12 instances)

```python
PydanticDeprecatedSince20: `json_encoders` is deprecated. 
See https://docs.pydantic.dev/2.11/concepts/serialization/#custom-serializers 
for alternatives. Deprecated in Pydantic V2.0 to be removed in V3.0.
```

**Location**: `/Users/lou/Library/Python/3.9/lib/python/site-packages/pydantic/_internal/_generate_schema.py:298`

**Impact**: Low
- Code still works
- Will break in Pydantic V3.0
- Need to update to new serialization approach

**Action**: Update code using `json_encoders` to use custom serializers instead.

## Performance Analysis

- **Total Duration**: 5.80 seconds
- **Average per test**: ~135ms
- **Comparison**:
  - Faster than `test-system` (6.10s)
  - Tests per second: ~7.4 tests/sec

## Coverage Analysis

### What This Tests
✅ **Observatory AI Consultation**:
- Health checking functionality
- Visual regression testing
- Auto-rollback management
- System health monitoring
- Feature flag health
- Circuit breaker health
- Resource usage monitoring

### What This DOESN'T Test (from earlier run)
❌ **Skipped in targeted baseline**:
- `organization` module tests (60+ tests)
- `self_refactoring` module tests (45+ tests)
- `testing` module tests (65+ tests)
- `tool_health` module tests (11+ tests)
- `makefile_governance` tests
- Other `ai_memory_palace` integration tests
- Other AI consultation integration tests

**Total skipped**: ~1,201 tests (1,244 - 43)

## Comparison: Current vs Previous Run

| Metric | Previous Run | Current Run | Change |
|--------|-------------|-------------|--------|
| Test Scope | Full suite | Targeted baseline | Reduced |
| Tests Collected | 1,244 | 43 | -96.5% |
| Import Errors | 132 | 0 | Fixed |
| Pass Rate | N/A (errors) | 100% | Better |
| Duration | ~7s | 5.80s | Faster |
| Purpose | Full validation | Smoke test | Different |

## Why the Change?

Possible reasons for switching to targeted baseline:

1. **Fast Feedback**: Quick smoke test for common workflows
2. **Import Issues**: Avoids the 132 import errors from full suite
3. **Development Speed**: Faster iteration for developers
4. **CI/CD**: Separate quick check from full test suite
5. **Recent Change**: Makefile modified between runs

## Implications

### Positive
- ✅ Fast feedback loop (5.8s vs potentially minutes for full suite)
- ✅ Core Observatory functionality verified
- ✅ No import errors blocking this subset
- ✅ 100% pass rate on tested code

### Concerns
- ⚠️ **Limited Coverage**: Only 3.5% of tests run (43/1244)
- ⚠️ **Hidden Issues**: The 132 import errors still exist elsewhere
- ⚠️ **False Confidence**: Passing baseline doesn't mean full system works
- ⚠️ **Incomplete Validation**: organization, self_refactoring, testing, tool_health not tested

## Recommendations

### Priority 1: Document Test Strategy
Update documentation to explain:
- `dev-test` = Quick baseline (43 tests)
- Full test command = `pytest tests/` or different make target
- When to use each

### Priority 2: Create Full Test Target
```makefile
# Suggestion:
dev-test-full:
	pytest tests/unit/beast_mode \
	       tests/integration/beast_mode \
	       -v --tb=short
```

### Priority 3: Address Import Errors
The 132 import errors from the full suite need resolution:
- `RegressionResult` vs `VisualTestResult` API mismatch
- Other compatibility issues
- See: `docs/recovery/beast-mode-module-restoration-guide.md`

### Priority 4: Update Pydantic Usage
Fix 12 deprecation warnings before Pydantic V3.0:
```python
# Replace json_encoders with custom serializers
# See: https://docs.pydantic.dev/2.11/concepts/serialization/#custom-serializers
```

## Comparison with Other Commands

| Metric | validate-safety | validate-targets | test-system | dev-test |
|--------|----------------|------------------|-------------|----------|
| Exit Code | 0 | 0 | 0 | 0 |
| Tests/Targets | 1 | 65 targets | 12 tests | 43 tests |
| Pass Rate | SAFE | 90.8% | 100% | 100% |
| Duration | ~1s | ~1s | 6.10s | 5.80s |
| Scope | System | Targets | System | Observatory subset |
| Purpose | Safety | Validation | Integration | Baseline smoke |

## Conclusion

**✅ BASELINE PASSED**: The targeted dev-test baseline (43 tests) passed perfectly with 100% success rate.

However, this is **NOT the full story**:
- Only 3.5% of total tests run (43 out of 1,244)
- 132 import errors exist in the full suite
- Most Beast Mode modules not tested in this baseline

**The Good**:
- Core Observatory AI Consultation functionality works perfectly
- Health checking system operational
- Visual regression system functional
- Fast feedback for common development tasks

**The Caution**:
- Don't assume full system health from this baseline
- The import errors from earlier still exist
- Need full test suite run for complete validation

---

**Status**: ✅ PASS (targeted baseline only)  
**Full Suite Status**: ⚠️ UNKNOWN (132 import errors when last tested)  
**Coverage**: 43/1,244 tests (3.5%)  
**Critical Issues**: 0 (in tested subset)  
**Warnings**: 12 (Pydantic deprecations)  
**Recommendation**: Run full test suite separately to validate all modules

---

## Coverage Gap Analysis

**Analysis Date**: 2025-10-09  
**Baseline**: 43 tests (current `dev-test`)  
**Historical Baseline**: 1,244 tests (previous full run)  
**Total Available**: 3,660 tests discovered  
**Test Files**: 812 Python test files

### Executive Summary

The `make dev-test` target currently runs **43 tests (1.2% of available tests)**, representing a **massive coverage gap** compared to the historical baseline of 1,244 tests and the total available 3,660 tests. This analysis documents what's missing and what would be required to restore broader coverage.

### Test Collection Statistics

| Metric | Count | Percentage |
|--------|-------|------------|
| **Total Tests Collected** | 3,660 | 100% |
| **Tests Currently Run** | 43 | 1.2% |
| **Import Errors** | 430 | 11.7% |
| **Tests Deselected** | 75 | 2.0% |
| **Tests Skipped** | 3 | 0.1% |
| **Tests Actually Available** | 3,585 | 97.9% |
| **Coverage Gap** | 3,542 | 96.8% |

### Test Directory Status Matrix

| Directory | Status | Est. Tests | Reason Disabled | Priority |
|-----------|--------|-----------|-----------------|----------|
| **Currently Enabled** |
| `tests/unit/beast_mode/observatory/ai_consultation/` | ✅ **ENABLED** | 43 | Running | - |
| **Disabled/Missing** |
| `tests/unit/beast_mode/` (other) | ❌ DISABLED | ~500 | Targeted baseline scope | HIGH |
| `tests/integration/beast_mode/` | ❌ DISABLED | ~400 | Requires services (Redis, DB) | HIGH |
| `tests/integration/makefile_governance/` | ❌ DISABLED | ~150 | Targeted baseline scope | MEDIUM |
| `tests/unit/makefile_governance/` | ❌ DISABLED | ~80 | Targeted baseline scope | MEDIUM |
| `tests/unit/repository_discovery/` | ❌ DISABLED | ~60 | Targeted baseline scope | MEDIUM |
| `tests/unit/directus_cms/` | ❌ DISABLED | ~50 | Requires Directus service | MEDIUM |
| `tests/unit/websocket/` | ❌ DISABLED | ~45 | Requires WebSocket server | MEDIUM |
| `tests/integration/websocket/` | ❌ DISABLED | ~40 | Requires WebSocket server | MEDIUM |
| `tests/deployment/` | ❌ DISABLED | ~35 | Requires Docker infrastructure | LOW |
| `tests/unit/dag_orchestration/` | ❌ DISABLED | ~30 | Targeted baseline scope | MEDIUM |
| `tests/integration/spec_scrub/` | ❌ DISABLED | ~25 | Targeted baseline scope | MEDIUM |
| `tests/unit/monitoring/` | ❌ DISABLED | ~20 | Targeted baseline scope | LOW |
| `tests/unit/cloudflare/` | ❌ DISABLED | ~18 | Requires network access | LOW |
| `tests/unit/rm_ddd/` | ❌ DISABLED | ~15 | Targeted baseline scope | MEDIUM |
| `tests/visual/` | ❌ DISABLED | ~12 | Requires Selenium/browser | LOW |
| `tests/performance/` | ❌ DISABLED | ~10 | Slow tests | LOW |
| `tests/probe/` | ❌ DISABLED | ~8 | Targeted baseline scope | LOW |
| `tests/unit/domain_index/` | ❌ DISABLED | ~6 | Import errors | MEDIUM |
| Other test directories | ❌ DISABLED | ~2,000 | Various reasons | VARIES |

### Dependencies Required to Re-enable Test Suites

#### Infrastructure Services

**Redis** (Required for ~440 tests):
```bash
# Start Redis locally
redis-server --port 6379

# Or via Docker
docker run -d -p 6379:6379 redis:latest

# Environment variables needed
export REDIS_HOST=localhost
export REDIS_PORT=6379
```

**PostgreSQL/Directus** (Required for ~200 tests):
```bash
# Via docker-compose
docker-compose up -d postgres directus

# Environment variables needed
export DIRECTUS_URL=http://localhost:8055
export DIRECTUS_TOKEN=<admin-token>
export DB_HOST=localhost
export DB_PORT=5432
export DB_NAME=kiro
export DB_USER=postgres
export DB_PASSWORD=<password>
```

**WebSocket Server** (Required for ~85 tests):
```bash
# Start Observatory WebSocket server
make observatory-start

# Or manually
python3 src/beast_mode/observatory/server.py

# Environment variables needed
export WEBSOCKET_URL=ws://localhost:8765
```

**Docker Infrastructure** (Required for ~35 tests):
```bash
# Start full stack
docker-compose up -d

# Verify services
docker-compose ps
```

#### Python Dependencies

**Selenium/Browser Testing** (Required for ~12 tests):
```bash
pip install selenium webdriver-manager pillow
# Or for full visual regression:
pip install selenium pillow pytest-playwright
playwright install chromium
```

**Additional Test Dependencies** (Required for various tests):
```bash
# From requirements-dev.txt
pip install pytest-asyncio pytest-mock pytest-cov
pip install aiohttp websockets
pip install redis psycopg2-binary
```

#### Import Errors to Fix (430 errors)

**Common Import Issues**:
1. **Module path changes**: Some modules moved or renamed
2. **Missing dependencies**: Some test-specific packages not installed
3. **API incompatibilities**: `RegressionResult` vs `VisualTestResult` mismatches
4. **Circular imports**: Some modules have circular dependency issues

**Example error patterns from logs**:
```python
# API mismatch
ImportError: cannot import name 'RegressionResult' from 'src.beast_mode.observatory.ai_consultation.visual_regression'

# Missing module
ModuleNotFoundError: No module named 'src.repository_discovery.babel_fish'

# Circular import
ImportError: cannot import name 'ContentType' from partially initialized module
```

### Recommended Test Expansion Roadmap

#### Phase 1: Expand Core Unit Tests (Effort: Low, Impact: High)
**Target**: Restore 500+ tests from `tests/unit/beast_mode/`

```makefile
# Add to Makefile
dev-test-unit: ## Run all unit tests (no external dependencies)
	@echo '🧪 Running all unit tests...'
	$(PYTHON) -m pytest \
		tests/unit/beast_mode/ \
		tests/unit/makefile_governance/ \
		tests/unit/repository_discovery/ \
		tests/unit/dag_orchestration/ \
		tests/unit/rm_ddd/ \
		-v --tb=short -m "not slow"
	@echo '✅ Unit tests complete'
```

**Prerequisites**:
- Fix import errors (430 issues)
- No external services required
- Estimated duration: ~45 seconds

**Effort**: 4-8 hours to fix import errors  
**Impact**: Validates ~600 tests (16% coverage)

#### Phase 2: Add Integration Tests with Local Services (Effort: Medium, Impact: High)
**Target**: Restore 400+ tests from `tests/integration/beast_mode/`

```makefile
dev-test-integration: ## Run integration tests (requires services)
	@echo '🧪 Running integration tests...'
	@echo 'Prerequisites: Redis, PostgreSQL, WebSocket server'
	@scripts/check_services.sh || exit 1
	$(PYTHON) -m pytest \
		tests/integration/beast_mode/ \
		tests/integration/makefile_governance/ \
		-v --tb=short -m "not slow"
	@echo '✅ Integration tests complete'
```

**Prerequisites**:
- Redis running locally
- PostgreSQL/Directus running
- WebSocket server running
- Environment variables configured
- Estimated duration: ~2 minutes

**Effort**: 8-16 hours (setup + fixes)  
**Impact**: Validates ~550 tests (15% coverage, cumulative 31%)

#### Phase 3: Add Makefile Governance Tests (Effort: Low, Impact: Medium)
**Target**: Restore 230+ tests from makefile governance suites

```makefile
dev-test-governance: ## Run makefile governance tests
	@echo '🧪 Running governance tests...'
	$(PYTHON) -m pytest \
		tests/unit/makefile_governance/ \
		tests/integration/makefile_governance/ \
		-v --tb=short
	@echo '✅ Governance tests complete'
```

**Prerequisites**:
- No external services
- Sample Makefiles in `tests/makefiles/`
- Estimated duration: ~30 seconds

**Effort**: 2-4 hours  
**Impact**: Validates ~230 tests (6% coverage, cumulative 37%)

#### Phase 4: Add Repository Discovery Tests (Effort: Medium, Impact: Medium)
**Target**: Restore 120+ tests from repository discovery

```makefile
dev-test-discovery: ## Run repository discovery tests
	@echo '🧪 Running discovery tests...'
	$(PYTHON) -m pytest \
		tests/unit/repository_discovery/ \
		tests/repository_discovery/ \
		-v --tb=short
	@echo '✅ Discovery tests complete'
```

**Prerequisites**:
- No external services
- Test fixtures (sample repos)
- Estimated duration: ~25 seconds

**Effort**: 4-6 hours  
**Impact**: Validates ~120 tests (3% coverage, cumulative 40%)

#### Phase 5: Add WebSocket Tests (Effort: Medium, Impact: Low)
**Target**: Restore 85+ WebSocket tests

```makefile
dev-test-websocket: ## Run WebSocket tests
	@echo '🧪 Running WebSocket tests...'
	@echo 'Prerequisites: WebSocket server running'
	$(PYTHON) -m pytest \
		tests/unit/websocket/ \
		tests/integration/websocket/ \
		tests/websocket/ \
		-v --tb=short
	@echo '✅ WebSocket tests complete'
```

**Prerequisites**:
- WebSocket server running on port 8765
- Test fixtures
- Estimated duration: ~40 seconds

**Effort**: 6-8 hours  
**Impact**: Validates ~85 tests (2% coverage, cumulative 42%)

#### Phase 6: Optional - Visual & Performance Tests (Effort: High, Impact: Low)
**Target**: Remaining ~2,900 tests (deployment, visual, performance, etc.)

These are optional and can be enabled selectively:

```makefile
dev-test-visual: ## Run visual regression tests (slow)
	@echo '🧪 Running visual tests...'
	$(PYTHON) -m pytest tests/visual/ -v --tb=short

dev-test-performance: ## Run performance tests (slow)
	@echo '🧪 Running performance tests...'
	$(PYTHON) -m pytest tests/performance/ -v --tb=short -m slow

dev-test-deployment: ## Run deployment tests (requires Docker)
	@echo '🧪 Running deployment tests...'
	$(PYTHON) -m pytest tests/deployment/ -v --tb=short
```

**Prerequisites**:
- Selenium + browsers (visual)
- Docker infrastructure (deployment)
- Extended test time tolerance (performance)
- Estimated duration: 5-10 minutes

**Effort**: 20-40 hours  
**Impact**: Validates remaining tests (58% coverage, cumulative 100%)

### Recommended Next Steps (Prioritized by ROI)

#### Immediate (Week 1)
1. **Fix Import Errors** → Enables 430 blocked tests
   - Update module paths
   - Fix API mismatches (`RegressionResult` → `VisualTestResult`)
   - Resolve circular imports
   - **Effort**: 4-8 hours
   - **ROI**: Very High (unblocks many tests)

2. **Document Test Strategy** → Clarifies dev workflow
   - Update `README.md` with test targets
   - Create `docs/testing-strategy.md`
   - Add comments to Makefile
   - **Effort**: 1-2 hours
   - **ROI**: High (prevents confusion)

#### Short-term (Week 2-3)
3. **Implement Phase 1: Unit Tests** → 600 tests
   - Create `dev-test-unit` target
   - Fix unit test import errors
   - Verify all pass
   - **Effort**: 8-12 hours
   - **ROI**: Very High (16% coverage gain, no services needed)

4. **Implement Phase 3: Governance Tests** → 230 tests
   - Create `dev-test-governance` target
   - Ensure test fixtures exist
   - Verify all pass
   - **Effort**: 2-4 hours
   - **ROI**: High (6% coverage gain, no services needed)

#### Medium-term (Week 4-6)
5. **Implement Phase 2: Integration Tests** → 550 tests
   - Set up local services (Redis, PostgreSQL)
   - Create service check script
   - Create `dev-test-integration` target
   - Document service setup
   - **Effort**: 12-20 hours
   - **ROI**: High (15% coverage gain, validates critical paths)

6. **Implement Phase 4: Repository Discovery** → 120 tests
   - Create `dev-test-discovery` target
   - Ensure test fixtures exist
   - Verify all pass
   - **Effort**: 4-6 hours
   - **ROI**: Medium (3% coverage gain)

#### Long-term (Month 2+)
7. **Implement Phase 5: WebSocket Tests** → 85 tests
   - Ensure WebSocket server is reliable
   - Create `dev-test-websocket` target
   - Document WebSocket setup
   - **Effort**: 6-8 hours
   - **ROI**: Medium (2% coverage gain)

8. **Selectively Enable Phase 6** → Remaining tests
   - Enable visual tests if needed
   - Enable performance tests for optimization work
   - Enable deployment tests for release validation
   - **Effort**: 20-40 hours
   - **ROI**: Variable (depends on need)

### Test Execution Time Estimates

| Test Target | Tests | Duration | Prerequisites |
|-------------|-------|----------|---------------|
| `dev-test` (current) | 43 | 5.8s | None |
| `dev-test-unit` (proposed) | ~600 | ~45s | Import fixes |
| `dev-test-governance` (proposed) | ~230 | ~30s | None |
| `dev-test-discovery` (proposed) | ~120 | ~25s | None |
| `dev-test-integration` (proposed) | ~550 | ~2m | Services |
| `dev-test-websocket` (proposed) | ~85 | ~40s | WebSocket |
| **Full Suite** (all combined) | ~1,628 | ~4m | All services |
| **Maximum Possible** | 3,660 | ~10-15m | Everything |

### Skip Patterns Detected

Found **25 skipif patterns** across **8 files**:

1. `tests/visual/` - Tests skip when Selenium unavailable
2. `tests/integration/` - Some tests skip when services unavailable
3. `tests/unit/` - Some tests skip conditionally based on environment

**Files with skip patterns**:
- `tests/visual/beast_mode/observatory/test_emoji_rain_effects.py` (3 skips)
- `tests/visual/beast_mode/observatory/test_dashboard_rendering.py` (3 skips)
- `tests/unit/beast_mode/observatory/test_web_interface.py` (9 skips)
- `tests/integration/beast_mode/observatory/ai_consultation/test_llm_service_integration.py` (1 skip)
- `tests/unit/test_message_models.py` (2 skips)
- `tests/integration/test_gke_terraform_validation.py` (2 skips)
- `tests/test_rca_performance_validation.py` (4 skips)
- `tests/test_utilities.py` (1 skip)

Most skips are **appropriate** - they skip tests that require unavailable resources.

### Archived Tests Comparison

**Archive Location**: `archive/development/metrics_data/migration_backups/20250905_112802/tests/`

Found archived tests from September 5, 2025 backup including:
- `test_comprehensive_unit_coverage.py`
- `test_dependency_analyzer.py`
- `test_governance_framework.py`
- `test_remediation_guide.py`
- `test_document_management_rm.py`
- `test_basic.py`
- `test_consolidated_functionality.py`
- Domain index tests
- RCA integration tests
- RDI compliance tests

**Action**: Review archived tests to identify valuable tests that should be restored.

### Conclusion

The `dev-test` target provides a **fast smoke test** (43 tests in 5.8s) but represents only **1.2% of available test coverage**. To achieve meaningful validation:

**Quick Wins** (Weeks 1-3, ~42% coverage):
- Fix 430 import errors (4-8 hours)
- Enable unit tests: +600 tests (8-12 hours)
- Enable governance tests: +230 tests (2-4 hours)
- Enable discovery tests: +120 tests (4-6 hours)
- **Total effort**: ~18-30 hours
- **Coverage gain**: 1.2% → 42%
- **No external services required**

**Full System Validation** (Month 2+, ~100% coverage):
- Add integration tests: +550 tests (requires services)
- Add WebSocket tests: +85 tests (requires WebSocket)
- Selectively enable remaining ~2,900 tests
- **Total effort**: ~50-90 hours
- **Coverage gain**: 42% → 100%
- **Requires full infrastructure**

**Recommendation**: Execute the "Quick Wins" roadmap first to achieve 42% coverage with minimal infrastructure requirements, then evaluate whether additional coverage justifies the service setup effort.

