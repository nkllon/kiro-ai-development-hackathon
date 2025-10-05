# Observatory Permanent Fix and Governance Implementation

## Context

The Observatory system was degraded due to missing ML dependencies (numpy, scikit-learn, pandas, scipy) in the Docker container. This was caused by `requirements.txt` being out of sync with `pyproject.toml`. A temporary fix was applied by manually installing dependencies in the running container, but permanent corrective actions are needed.

## Current State

### Temporary Fixes Applied ✅
1. Installed ML dependencies in running container: `docker exec beast-mode-observatory pip install numpy scikit-learn pandas scipy`
2. Manually updated `requirements.txt` with ML dependencies
3. Created `docker-compose.local.yml` for local development
4. Documented issues in `docs/observatory/`

### Issues Remaining ⚠️
1. **requirements.txt manually maintained** - Will drift out of sync again
2. **No build validation** - Container builds succeed even if critical imports fail
3. **No governance on dependency management** - Process not documented
4. **Docker image not rebuilt** - Running containers have fix, but image doesn't
5. **No pre-commit hooks** - Nothing prevents pyproject.toml/requirements.txt drift

## Required Permanent Actions

### 1. Establish Dependency Management Governance

**Create**: `.kiro/specs/dependency-management-governance/requirements.md`

**Requirements**:
- Single source of truth: `pyproject.toml`
- Auto-generate `requirements.txt` from `pyproject.toml` using pip-tools
- Pre-commit hook validates sync between files
- Docker build includes import smoke tests
- CI/CD validates dependency completeness

### 2. Implement Auto-Generation of requirements.txt

**Tasks**:
- [ ] Add `pip-tools` to dev dependencies in `pyproject.toml`
- [ ] Create `scripts/generate_requirements.py` that runs `pip-compile`
- [ ] Add `make requirements` target to regenerate requirements.txt
- [ ] Document process in `docs/development/DEPENDENCY-MANAGEMENT.md`

**Command to implement**:
```bash
# Generate requirements.txt from pyproject.toml
pip-compile pyproject.toml -o requirements.txt --resolver=backtracking
```

### 3. Add Build Validation to Dockerfile

**Update**: `deployment/observatory/Dockerfile`

**Add after pip install** (around line 12):
```dockerfile
# Validate critical imports
RUN python3 -c "\
import sys; \
failures = []; \
try: \
    import numpy; \
except ImportError as e: \
    failures.append(f'numpy: {e}'); \
try: \
    import sklearn; \
except ImportError as e: \
    failures.append(f'sklearn: {e}'); \
try: \
    import pandas; \
except ImportError as e: \
    failures.append(f'pandas: {e}'); \
try: \
    import scipy; \
except ImportError as e: \
    failures.append(f'scipy: {e}'); \
if failures: \
    print('❌ ML dependency validation failed:', file=sys.stderr); \
    for f in failures: print(f'  - {f}', file=sys.stderr); \
    sys.exit(1); \
print('✅ All critical dependencies validated')" || exit 1
```

### 4. Create Pre-Commit Hook for Dependency Sync

**Create**: `.pre-commit-hooks/validate-dependencies.sh`

```bash
#!/bin/bash
# Validate pyproject.toml and requirements.txt are in sync

echo "🔍 Validating dependency sync..."

# Extract dependencies from pyproject.toml
PYPROJECT_DEPS=$(python3 -c "
import toml
data = toml.load('pyproject.toml')
deps = data['project']['dependencies']
for dep in sorted(deps):
    print(dep.split('>=')[0].split('==')[0].strip())
")

# Check each dependency exists in requirements.txt
MISSING=()
for dep in $PYPROJECT_DEPS; do
    if ! grep -q "^${dep}" requirements.txt; then
        MISSING+=("$dep")
    fi
done

if [ ${#MISSING[@]} -gt 0 ]; then
    echo "❌ Dependencies in pyproject.toml but not in requirements.txt:"
    for dep in "${MISSING[@]}"; do
        echo "  - $dep"
    done
    echo ""
    echo "Run: make requirements"
    exit 1
fi

echo "✅ Dependency sync validated"
exit 0
```

**Add to**: `.pre-commit-config.yaml`

```yaml
  - repo: local
    hooks:
      - id: validate-dependencies
        name: Validate dependency sync
        entry: .pre-commit-hooks/validate-dependencies.sh
        language: script
        files: '(pyproject\.toml|requirements\.txt)$'
        pass_filenames: false
```

### 5. Rebuild and Redeploy Observatory

**Tasks**:
- [ ] Regenerate requirements.txt: `pip-compile pyproject.toml -o requirements.txt`
- [ ] Rebuild Docker image: `docker-compose build observatory`
- [ ] Test locally: `docker-compose -f docker-compose.local.yml up -d`
- [ ] Verify health: `curl localhost:8888/api/observatory/status`
- [ ] Deploy to production: Update image on Vonnegut server
- [ ] Verify production: `curl https://observatory.nkllon.com/api/observatory/status`

### 6. Update Makefile with Dependency Targets

**Add to**: `Makefile`

```makefile
# Dependency Management
.PHONY: requirements requirements-check requirements-upgrade

requirements: ## Regenerate requirements.txt from pyproject.toml
	@echo "📦 Regenerating requirements.txt from pyproject.toml..."
	pip-compile pyproject.toml -o requirements.txt --resolver=backtracking
	@echo "✅ requirements.txt updated"

requirements-check: ## Validate pyproject.toml and requirements.txt are in sync
	@echo "🔍 Checking dependency sync..."
	@.pre-commit-hooks/validate-dependencies.sh

requirements-upgrade: ## Upgrade all dependencies to latest versions
	@echo "⬆️  Upgrading dependencies..."
	pip-compile --upgrade pyproject.toml -o requirements.txt --resolver=backtracking
	@echo "✅ Dependencies upgraded"
```

### 7. Create Governance Specification

**Create**: `.kiro/specs/observatory-dependency-governance/requirements.md`

**Content**:
```markdown
# Observatory Dependency Governance

## Requirements

### REQ-1: Single Source of Truth
- pyproject.toml is the authoritative source for all Python dependencies
- requirements.txt is auto-generated from pyproject.toml
- Manual edits to requirements.txt are prohibited

### REQ-2: Automated Sync
- Pre-commit hook validates sync before every commit
- CI/CD pipeline validates sync on every PR
- `make requirements` command regenerates requirements.txt

### REQ-3: Build Validation
- Dockerfile validates critical imports after pip install
- Build fails fast if ML dependencies (numpy, sklearn, pandas, scipy) are missing
- No silent failures allowed

### REQ-4: Documentation
- DEPENDENCY-MANAGEMENT.md documents the process
- README includes "make requirements" in setup instructions
- Troubleshooting guide includes dependency sync issues

### REQ-5: Monitoring
- Observatory health check includes dependency validation
- Startup logs clearly show which dependencies loaded successfully
- Prometheus metrics track import failures

## Acceptance Criteria

- [ ] pyproject.toml → requirements.txt sync is automated
- [ ] Pre-commit hook prevents out-of-sync commits
- [ ] Docker build fails if critical imports don't work
- [ ] Documentation is complete and clear
- [ ] Production Observatory rebuilt with new process
- [ ] Zero manual dependency management required
```

### 8. Create CI/CD Validation

**Create**: `.github/workflows/validate-dependencies.yml`

```yaml
name: Validate Dependencies

on:
  pull_request:
    paths:
      - 'pyproject.toml'
      - 'requirements.txt'
  push:
    branches:
      - master
      - 'release/**'
    paths:
      - 'pyproject.toml'
      - 'requirements.txt'

jobs:
  validate-sync:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.9'

      - name: Install pip-tools
        run: pip install pip-tools toml

      - name: Validate dependency sync
        run: |
          chmod +x .pre-commit-hooks/validate-dependencies.sh
          ./.pre-commit-hooks/validate-dependencies.sh

      - name: Test requirements.txt generation
        run: |
          pip-compile pyproject.toml -o requirements-test.txt --resolver=backtracking
          diff requirements.txt requirements-test.txt || \
            (echo "❌ requirements.txt not in sync with pyproject.toml" && \
             echo "Run: make requirements" && \
             exit 1)
```

## Implementation Plan

### Phase 1: Governance & Tooling (1-2 hours)
1. Create dependency governance spec
2. Add pip-tools to dev dependencies
3. Create generate_requirements.py script
4. Add Makefile targets
5. Document process

### Phase 2: Validation & Safety (1 hour)
1. Update Dockerfile with import validation
2. Create pre-commit hook
3. Add CI/CD workflow
4. Test locally

### Phase 3: Deployment (30 min - 1 hour)
1. Regenerate requirements.txt properly
2. Rebuild Docker images
3. Test in local environment
4. Deploy to production
5. Verify all systems healthy

### Phase 4: Documentation & Handoff (30 min)
1. Update README with new process
2. Create troubleshooting guide
3. Document in Beast Mode governance
4. Close out Observatory recovery

## Success Criteria

- ✅ Single command regenerates requirements.txt: `make requirements`
- ✅ Pre-commit hook prevents drift
- ✅ Docker build validates imports
- ✅ CI/CD catches sync issues
- ✅ Production Observatory rebuilt with validated image
- ✅ Health status remains "healthy" after rebuild
- ✅ Process documented and governed
- ✅ Zero manual intervention needed going forward

## Verification Commands

```bash
# Test dependency sync
make requirements-check

# Regenerate requirements.txt
make requirements

# Test Docker build with validation
cd deployment/observatory
docker-compose build observatory

# Verify build succeeded and validation passed
docker logs $(docker-compose ps -q observatory) | grep "✅ All critical dependencies validated"

# Test locally
docker-compose -f docker-compose.local.yml up -d
curl localhost:8888/api/observatory/status | python3 -m json.tool

# Deploy to production (on Vonnegut)
docker-compose pull
docker-compose up -d
curl https://observatory.nkllon.com/api/observatory/status | python3 -m json.tool
```

## Related Documentation

- **Current Fix**: [docs/observatory/OBSERVATORY-FIX-SUMMARY.md](../../docs/observatory/OBSERVATORY-FIX-SUMMARY.md)
- **Local Setup**: [docs/observatory/LOCAL-DEVELOPMENT-SETUP.md](../../docs/observatory/LOCAL-DEVELOPMENT-SETUP.md)
- **Recovery Summary**: [OBSERVATORY-RECOVERY-SUCCESS.md](../../OBSERVATORY-RECOVERY-SUCCESS.md)
- **Quick Reference**: [docs/observatory/QUICK-REFERENCE.md](../../docs/observatory/QUICK-REFERENCE.md)

## Deliverables

1. ✅ **requirements.txt** - Already updated with ML dependencies
2. ⏳ **scripts/generate_requirements.py** - Auto-generation script
3. ⏳ **.pre-commit-hooks/validate-dependencies.sh** - Validation hook
4. ⏳ **Makefile** - Dependency management targets
5. ⏳ **deployment/observatory/Dockerfile** - Build validation
6. ⏳ **.github/workflows/validate-dependencies.yml** - CI/CD validation
7. ⏳ **.kiro/specs/observatory-dependency-governance/** - Governance spec
8. ⏳ **docs/development/DEPENDENCY-MANAGEMENT.md** - Process documentation
9. ⏳ **Rebuilt Docker images** - With validated dependencies
10. ⏳ **Production deployment** - Verified healthy

## Expected Outcome

After completing this work:
- Observatory dependency management is fully automated
- Sync drift is impossible (blocked by pre-commit + CI/CD)
- Docker builds fail fast with clear errors
- Process is documented and governed
- Production runs on validated, reproducible builds
- Future developers follow clear, automated process

This establishes systematic prevention rather than reactive fixes.
