# How to Fix Dependencies - Quick Guide

**Based on**: beast-mailbox-core best practices  
**Priority**: HIGH  
**Time**: 15 minutes

---

## 🎯 The Problem

Current state has **missing critical dependencies**:
- ❌ `redis` not declared (breaks 137 tests!)
- ❌ `beast-mailbox-core` not declared  
- ❌ `pytest-asyncio` not in main deps
- ❌ Async tests not configured

## ✅ The Solution (3 Steps)

### Step 1: Update pyproject.toml

```bash
cd /Volumes/lemon/cursor/kiro-ai-development-hackathon
```

Add to the `dependencies` list in `pyproject.toml`:

```toml
[project]
dependencies = [
    # ... existing dependencies ...
    
    # ADD THESE THREE LINES:
    "redis>=5.0.0",
    "beast-mailbox-core>=0.3.1",
    "pytest-asyncio>=0.21.0",
]
```

Add to pytest configuration:

```toml
[tool.pytest.ini_options]
minversion = "7.0"
asyncio_mode = "auto"  # ← ADD THIS LINE
addopts = "-ra -q --strict-markers --strict-config"
testpaths = ["tests"]
# ... rest of config ...
```

### Step 2: Update requirements.txt

Add these lines to `requirements.txt`:

```
# Redis infrastructure (CRITICAL - was missing!)
redis>=5.0.0
beast-mailbox-core>=0.3.1

# Async testing (CRITICAL - was missing!)
pytest-asyncio>=0.21.0
```

### Step 3: Test Clean Installation

```bash
# Create test environment
python3 -m venv test_install
source test_install/bin/activate

# Test installation
pip install -e .

# Verify critical imports
python -c "import redis; print('✅ redis:', redis.__version__)"
python -c "import beast_mailbox_core; print('✅ beast-mailbox-core')"
python -c "import pytest_asyncio; print('✅ pytest-asyncio')"

# Clean up
deactivate
rm -rf test_install
```

---

## 🔍 What We Learned from beast-mailbox-core

### Their pyproject.toml (Perfect Example)

```toml
[project]
name = "beast-mailbox-core"
version = "0.3.1"
requires-python = ">=3.9"

dependencies = [
  "redis>=5.0.0",  # ← Explicitly declared!
]

[project.optional-dependencies]
dev = [
  "pytest>=7.0.0",
  "pytest-asyncio>=0.21.0",  # ← In optional deps
  "pytest-cov>=4.0.0",
]

[tool.pytest.ini_options]
asyncio_mode = "auto"  # ← Key for async tests!
```

### Key Insights

1. **Single Source of Truth**: They use ONLY `pyproject.toml` (no requirements.txt)
2. **Explicit Dependencies**: All deps clearly declared
3. **Async Configuration**: `asyncio_mode = "auto"` handles async tests
4. **Clean Separation**: Main deps vs dev deps
5. **It Works**: 59 tests, 90% coverage, zero defects

---

## 📊 Before vs After

### Before (Broken)
```bash
make install
# Missing: redis, beast-mailbox-core, pytest-asyncio
# Result: 137 test collection errors
# Fix: Manual pip install redis beast-mailbox-core
```

### After (Fixed)
```bash
make install
# Includes: redis, beast-mailbox-core, pytest-asyncio
# Result: All dependencies satisfied
# Bonus: Async tests work correctly
```

---

## 🚀 Verification Checklist

After making changes:

- [ ] `redis>=5.0.0` in pyproject.toml dependencies
- [ ] `beast-mailbox-core>=0.3.1` in pyproject.toml dependencies
- [ ] `pytest-asyncio>=0.21.0` in pyproject.toml dependencies
- [ ] Same three packages in requirements.txt
- [ ] `asyncio_mode = "auto"` in pytest config
- [ ] Clean install test passes
- [ ] All imports work
- [ ] Test suite runs (may still have other errors)

---

## 📝 Files to Modify

1. **pyproject.toml** (lines ~12):
   - Add to `dependencies` list

2. **pyproject.toml** (lines ~39):
   - Add `asyncio_mode = "auto"` to `[tool.pytest.ini_options]`

3. **requirements.txt** (lines ~41):
   - Add three packages

---

## ⚡ One-Command Test

After making changes:

```bash
python3 -m venv quick_test && \
source quick_test/bin/activate && \
pip install -e . && \
python -c "import redis, beast_mailbox_core, pytest_asyncio; print('✅ All deps OK!')" && \
deactivate && \
rm -rf quick_test
```

Expected output:
```
✅ All deps OK!
```

---

## 🎓 Further Reading

- **DEPENDENCY_MANAGEMENT_LESSONS.md** - Complete analysis
- **MISSING_DEPENDENCIES.md** - Detailed problem report
- **beast-mailbox-core repo**: https://github.com/nkllon/beast-mailbox-core

---

**TL;DR**: Add `redis`, `beast-mailbox-core`, and `pytest-asyncio` to both dependency files, plus `asyncio_mode = "auto"` to pytest config. Test it. Done! ✅



