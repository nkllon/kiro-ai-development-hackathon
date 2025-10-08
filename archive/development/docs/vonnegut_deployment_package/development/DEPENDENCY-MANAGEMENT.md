# Observatory Dependency Management

## Overview

This document describes the systematic dependency management process for the Observatory system, designed to prevent the ML dependency sync issues that caused system degradation.

## Core Principles

### Single Source of Truth
- **`pyproject.toml`** is the authoritative source for all Python dependencies
- **`requirements.txt`** is auto-generated from `pyproject.toml`
- **Manual edits to `requirements.txt` are prohibited**

### Automated Synchronization
- Pre-commit hooks prevent out-of-sync commits
- CI/CD pipelines validate dependency consistency
- Docker builds include import validation
- Make targets provide easy dependency management

## Quick Start

### Daily Development Workflow

```bash
# Check if dependencies are in sync
make requirements-check
K
# Regenerate requirements.txt from pyproject.toml
make requirements

# Upgrade all dependencies to latest versions
make requirements-upgrade

# Validate critical ML dependencies are present
make requirements-validate
```

### Adding New Dependencies

1. **Add to pyproject.toml**:
   ```toml
   [project]
   dependencies = [
       "numpy>=1.21.0",
       "scikit-learn>=1.0.0",
       "pandas>=1.3.0",
       "scipy>=1.7.0",
       "your-new-package>=1.0.0",  # Add here
   ]
   ```

2. **Regenerate requirements.txt**:
   ```bash
   make requirements
   ```

3. **Validate the change**:
   ```bash
   make requirements-check
   make requirements-validate
   ```

4. **Test Docker build**:
   ```bash
   cd deployment/observatory
   docker-compose build observatory
   ```

## Detailed Process

### Dependency Generation Process

The `scripts/generate_requirements.py` script:

1. **Validates pyproject.toml** exists and has proper structure
2. **Installs pip-tools** if not available
3. **Runs pip-compile** with backtracking resolver
4. **Adds custom header** to requirements.txt
5. **Validates critical dependencies** are present
6. **Reports generation statistics**

### Validation Process

The `.pre-commit-hooks/validate-dependencies.sh` hook:

1. **Extracts dependencies** from pyproject.toml
2. **Checks each dependency** exists in requirements.txt
3. **Validates critical ML dependencies** specifically
4. **Verifies auto-generated header** is present
5. **Reports sync status** and provides fix instructions

### Docker Build Validation

The Observatory Dockerfile includes import validation:

```dockerfile
# Validate critical imports
RUN python3 -c "\
import sys; \
failures = []; \
try: \
    import numpy; \
except ImportError as e: \
    failures.append(f'numpy: {e}'); \
# ... (additional imports) \
if failures: \
    print('❌ ML dependency validation failed:', file=sys.stderr); \
    for f in failures: print(f'  - {f}', file=sys.stderr); \
    sys.exit(1); \
print('✅ All critical dependencies validated')" || exit 1
```

This ensures the Docker build fails fast if critical imports don't work.

## Critical Dependencies

The Observatory system requires these ML dependencies:

- **numpy**: Numerical computing foundation
- **scikit-learn**: Machine learning algorithms
- **pandas**: Data manipulation and analysis
- **scipy**: Scientific computing utilities

These are validated at multiple stages:
- Pre-commit hook validation
- Requirements generation validation
- Docker build import testing
- CI/CD pipeline checks

## Makefile Targets

### `make requirements`
Regenerates `requirements.txt` from `pyproject.toml` using pip-compile.

**Usage:**
```bash
make requirements
```

**Output:**
- Updated `requirements.txt` with pinned versions
- Custom header indicating auto-generation
- Validation of critical dependencies

### `make requirements-check`
Validates that `pyproject.toml` and `requirements.txt` are synchronized.

**Usage:**
```bash
make requirements-check
```

**Validation includes:**
- All pyproject.toml dependencies present in requirements.txt
- Critical ML dependencies specifically checked
- Auto-generated header verification
- Format validation

### `make requirements-upgrade`
Upgrades all dependencies to their latest compatible versions.

**Usage:**
```bash
make requirements-upgrade
```

**Process:**
- Runs pip-compile with `--upgrade` flag
- Updates all packages to latest versions
- Maintains compatibility constraints from pyproject.toml
- Validates critical dependencies after upgrade

### `make requirements-validate`
Validates that critical dependencies are present without regenerating.

**Usage:**
```bash
make requirements-validate
```

**Checks:**
- Critical ML dependencies present
- Requirements.txt format validation
- No generation, validation only

## Pre-Commit Integration

### Setup Pre-Commit Hooks

1. **Install pre-commit**:
   ```bash
   pip install pre-commit
   ```

2. **Install hooks**:
   ```bash
   pre-commit install
   ```

3. **Test hooks**:
   ```bash
   pre-commit run --all-files
   ```

### Hook Configuration

Add to `.pre-commit-config.yaml`:

```yaml
repos:
  - repo: local
    hooks:
      - id: validate-dependencies
        name: Validate dependency sync
        entry: .pre-commit-hooks/validate-dependencies.sh
        language: script
        files: '(pyproject\.toml|requirements\.txt)'
        pass_filenames: false
```

## CI/CD Integration

The `.github/workflows/validate-dependencies.yml` workflow:

1. **Validates dependency sync** on every PR
2. **Tests requirements generation** process
3. **Validates critical dependencies** are present
4. **Tests Docker build validation** logic
5. **Scans for security vulnerabilities** in dependencies

### Workflow Triggers

- Pull requests affecting dependency files
- Pushes to main/master branches
- Changes to dependency management scripts

## Troubleshooting

### Common Issues

#### "Dependencies in pyproject.toml but not in requirements.txt"

**Cause:** requirements.txt is out of sync with pyproject.toml

**Fix:**
```bash
make requirements
git add requirements.txt
git commit -m "Update requirements.txt from pyproject.toml"
```

#### "Critical ML dependencies missing"

**Cause:** Required ML packages not in pyproject.toml

**Fix:**
1. Add missing dependencies to pyproject.toml:
   ```toml
   dependencies = [
       "numpy>=1.21.0",
       "scikit-learn>=1.0.0", 
       "pandas>=1.3.0",
       "scipy>=1.7.0",
   ]
   ```
2. Regenerate requirements.txt:
   ```bash
   make requirements
   ```

#### "Docker build fails with import errors"

**Cause:** Dependencies not properly installed in container

**Fix:**
1. Verify requirements.txt is up to date:
   ```bash
   make requirements-check
   ```
2. Rebuild Docker image:
   ```bash
   cd deployment/observatory
   docker-compose build --no-cache observatory
   ```

#### "pip-compile not found"

**Cause:** pip-tools not installed

**Fix:**
```bash
pip install pip-tools
# Or let the script install it automatically
make requirements
```

### Validation Commands

```bash
# Full validation sequence
make requirements-check
make requirements-validate
python scripts/generate_requirements.py --validate-only

# Test Docker build
cd deployment/observatory
docker-compose build observatory

# Verify container health
docker-compose up -d observatory
curl localhost:8888/api/observatory/status
```

## Security Considerations

### Dependency Security

1. **Regular security scans** with `safety check`
2. **Automated vulnerability detection** in CI/CD
3. **Version pinning** to prevent supply chain attacks
4. **Minimal dependency principle** - only include necessary packages

### Secret Management

- **Never hardcode credentials** in dependency files
- **Use environment variables** for sensitive configuration
- **Validate no secrets** in requirements.txt or pyproject.toml

## Migration from Manual Management

### For Existing Projects

1. **Audit current requirements.txt**:
   ```bash
   pip freeze > current-requirements.txt
   ```

2. **Create pyproject.toml** with core dependencies
3. **Generate new requirements.txt**:
   ```bash
   make requirements
   ```
4. **Compare and validate**:
   ```bash
   diff current-requirements.txt requirements.txt
   ```
5. **Test thoroughly** before deployment

### Rollback Plan

If issues occur:

1. **Keep backup** of working requirements.txt
2. **Revert to manual management** temporarily:
   ```bash
   cp requirements.txt.backup requirements.txt
   ```
3. **Fix issues** in pyproject.toml
4. **Re-attempt automated generation**

## Best Practices

### Development Workflow

1. **Always use make targets** instead of direct pip-compile
2. **Validate before committing** with `make requirements-check`
3. **Test Docker builds** after dependency changes
4. **Review generated requirements.txt** for unexpected changes

### Dependency Selection

1. **Pin major versions** to prevent breaking changes
2. **Use compatible release** specifiers (`~=1.0.0`) when appropriate
3. **Document dependency rationale** in pyproject.toml comments
4. **Regular dependency audits** for security and maintenance

### Production Deployment

1. **Test in staging** with new requirements.txt
2. **Validate health endpoints** after deployment
3. **Monitor for import errors** in application logs
4. **Have rollback plan** ready

## Related Documentation

- [Observatory Fix Summary](../observatory/OBSERVATORY-FIX-SUMMARY.md)
- [Local Development Setup](../observatory/LOCAL-DEVELOPMENT-SETUP.md)
- [Docker Deployment Guide](../deployment/DOCKER-DEPLOYMENT.md)
- [Security Guidelines](../security/SECURITY-GUIDELINES.md)

## Support

For issues with dependency management:

1. **Check this documentation** first
2. **Run validation commands** to diagnose issues
3. **Review CI/CD logs** for detailed error messages
4. **Test locally** before seeking help

---

**Last Updated:** January 27, 2025  
**Version:** 1.0  
**Maintainer:** Observatory Team