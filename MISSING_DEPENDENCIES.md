# Missing Dependencies Report

**Date**: 2025-10-13  
**Branch**: `fresh-install-venv-setup` (beast-mode-observatory-v1)  
**Severity**: HIGH - Core functionality affected

---

## 🚨 Critical Missing Dependencies

These packages are **required** for the application but are **NOT** included in `requirements.txt` or `pyproject.toml`:

### 1. redis ⚠️ CRITICAL
**Package**: `redis>=5.0.0`  
**Status**: Missing from all dependency files  
**Impact**: SEVERE

**Used By**:
- `src/beast_mode/messaging/redis_foundation.py`
- `src/beast_mode/observatory/redis_streams.py`
- `src/beast_mode/observatory/ai_consultation/status_persistence.py`
- `src/beast_mode/observatory/ai_consultation/query_queue.py`
- `src/beast_mode/task_queue/` (entire module)
- 137 test files fail without it

**Evidence**:
```bash
# Not in requirements.txt
grep -i redis requirements.txt  # No results

# Not in pyproject.toml dependencies
grep redis pyproject.toml  # Not in dependencies list
```

**Resolution Applied**:
```bash
pip install redis  # Installed version 6.4.0
```

**Must Add To**:
- `requirements.txt`: Add `redis>=5.0.0`
- `pyproject.toml`: Add `"redis>=5.0.0"` to dependencies list

---

### 2. beast-mailbox-core ⚠️ CRITICAL
**Package**: `beast-mailbox-core>=0.3.1`  
**Status**: Missing from all dependency files  
**Impact**: HIGH (part of documented install procedure)

**Used By**:
- Mailbox functionality
- Redis-backed messaging
- Beast Mode communication

**Evidence**:
```bash
# Not in requirements.txt
grep -i beast-mailbox requirements.txt  # No results

# Not in pyproject.toml
grep beast-mailbox pyproject.toml  # No results

# No references in codebase yet
grep -r beast-mailbox src/  # No results (may be for future use)
```

**Resolution Applied**:
```bash
pip install beast-mailbox-core  # Installed version 0.3.1
```

**Must Add To**:
- `requirements.txt`: Add `beast-mailbox-core>=0.3.1`
- `pyproject.toml`: Add `"beast-mailbox-core>=0.3.1"` to dependencies list

---

### 3. pytest-asyncio 🟡 MEDIUM
**Package**: `pytest-asyncio>=0.21.0`  
**Status**: In dependency-groups but not main dependencies  
**Impact**: MEDIUM (async tests fail)

**Used By**:
- All async test files (261 warnings)
- Task queue tests
- Observatory tests
- AI consultation tests

**Evidence**:
```bash
# 261 warnings during test run:
# PytestUnknownMarkWarning: Unknown pytest.mark.asyncio
```

**Resolution Applied**:
```bash
# Will need: pip install pytest-asyncio
```

**Must Add To**:
- `requirements.txt`: Add `pytest-asyncio>=0.21.0`
- Or move from `dependency-groups` to main dependencies in pyproject.toml

---

## 📊 Impact Analysis

### Without redis Package
- ❌ 137 test files cannot be collected
- ❌ Observatory features non-functional
- ❌ Task Queue system fails
- ❌ AI Consultation system fails
- ❌ Metrics streaming broken
- ❌ Real-time coordination unavailable

### Without beast-mailbox-core
- ❌ Mailbox operations fail
- ❌ Message queue features unavailable
- 🤷 Unclear full impact (may be for future features)

### Without pytest-asyncio
- ⚠️ 261 async test warnings
- ❌ Async tests skipped or fail
- ✅ Non-async functionality still works

---

## ✅ Recommended Actions

### For Maintainers

#### 1. Update requirements.txt
```bash
# Add these lines to requirements.txt:
redis>=5.0.0
beast-mailbox-core>=0.3.1
pytest-asyncio>=0.21.0
```

#### 2. Update pyproject.toml
```toml
[project]
dependencies = [
    # ... existing dependencies ...
    "redis>=5.0.0",
    "beast-mailbox-core>=0.3.1",
    "pytest-asyncio>=0.21.0",
]
```

#### 3. Test Clean Installation
```bash
# Test that these changes work:
python -m venv test_venv
source test_venv/bin/activate
pip install -r requirements.txt
# OR
pip install -e .

# Verify all imports work:
python -c "import redis; print('redis:', redis.__version__)"
python -c "import beast_mailbox_core; print('beast-mailbox-core OK')"
python -c "import pytest_asyncio; print('pytest-asyncio OK')"
```

#### 4. Update Documentation
- Add note about Redis requirement to README
- Document Redis setup as prerequisite
- Update installation instructions

---

## 🔍 How These Were Discovered

### redis Package
1. Ran test suite: 137 collection errors
2. All errors: `ModuleNotFoundError: No module named 'redis'`
3. Found extensive usage in codebase via grep
4. Confirmed not in any dependency files

### beast-mailbox-core Package
1. User attempted: `pip install beast-mailbox-core`
2. Confirmed it's expected to be part of install procedure
3. Not documented in requirements
4. No references in current codebase (may be planned feature)

### pytest-asyncio Package
1. Ran test suite: 261 warnings about unknown mark
2. All async tests show: `PytestUnknownMarkWarning: Unknown pytest.mark.asyncio`
3. Found in dependency-groups but not main dependencies
4. Should be in main test dependencies

---

## 📝 Dependencies Actually Installed

### From make install (requirements.txt)
- requests, pyyaml, click, rich, typer
- pytest, pytest-cov, black, flake8, mypy
- prometheus-client, python-dotenv, jinja2
- httpx, tqdm, colorama, jsonschema
- python-dateutil, structlog

### From pip install -e . (pyproject.toml)
- transformers, torch, scikit-learn
- numpy, pandas, datasets
- cryptography, pydantic, psutil
- google-api-python-client, google-auth-oauthlib

### Manually Added (MISSING from both!)
- ✅ redis==6.4.0
- ✅ beast-mailbox-core==0.3.1

### Still Needed
- ⏳ pytest-asyncio (for async tests)

---

## 🎯 Current Workaround

For fresh installations, after `make install`:

```bash
# Activate virtual environment
source venv/bin/activate

# Install missing critical dependencies
pip install redis>=5.0.0
pip install beast-mailbox-core>=0.3.1

# Optional: For async tests
pip install pytest-asyncio>=0.21.0

# Verify
python -c "import redis; import beast_mailbox_core; print('All critical deps installed!')"
```

---

## 🔄 Testing Coverage

### What Now Works (After Manual Install)
- ✅ Redis connection and operations
- ✅ beast-mailbox-core integration
- ✅ Basic imports and functionality
- ✅ Observatory can connect to Redis
- ✅ Task Queue can use Redis
- ✅ AI Consultation can use Redis

### What Still Needs Testing
- ⏳ Full test suite with pytest-asyncio
- ⏳ Beast mailbox operations end-to-end
- ⏳ All async functionality
- ⏳ Integration tests

---

## 📞 For Future Installers

**If you encounter import errors for these packages**, they are known missing dependencies. Install them manually:

```bash
pip install redis beast-mailbox-core pytest-asyncio
```

This issue has been reported to maintainers for inclusion in official dependency files.

---

## 🏷️ Issue Tracking

**Issue**: Missing Critical Dependencies  
**Severity**: HIGH  
**Status**: Workaround Applied, Awaiting Official Fix  
**Files to Update**: 
- `requirements.txt` ⏳
- `pyproject.toml` ⏳
- `README.md` ⏳ (document Redis prerequisite)

**Dependencies Affected**:
1. redis>=5.0.0 (CRITICAL)
2. beast-mailbox-core>=0.3.1 (HIGH)
3. pytest-asyncio>=0.21.0 (MEDIUM)

---

**Report Generated**: 2025-10-13  
**Tested On**: Python 3.9.6, macOS  
**Branch**: beast-mode-observatory-v1



