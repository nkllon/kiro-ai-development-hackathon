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

## Implementation Tasks

### Task 1: Dependency Management Tooling
- Add pip-tools to dev dependencies in pyproject.toml
- Create scripts/generate_requirements.py for automated generation
- Add Makefile targets for dependency management
- Test pip-compile functionality

### Task 2: Validation Infrastructure
- Create pre-commit hook for dependency sync validation
- Update Dockerfile with import validation
- Add CI/CD workflow for dependency validation
- Test validation mechanisms

### Task 3: Documentation and Process
- Create comprehensive dependency management documentation
- Update README with new process
- Create troubleshooting guide
- Document governance in Beast Mode framework

### Task 4: Production Deployment
- Regenerate requirements.txt using new process
- Rebuild Docker images with validation
- Deploy to production environment
- Verify health and functionality

## Success Metrics

- **100% automation**: No manual dependency management required
- **Zero drift**: Pre-commit and CI/CD prevent sync issues
- **Fast failure**: Docker builds fail immediately on import issues
- **Complete documentation**: All processes clearly documented
- **Production stability**: Observatory remains healthy after rebuild

## Risk Mitigation

- **Rollback plan**: Keep current working containers as backup
- **Validation testing**: Test all changes in local environment first
- **Incremental deployment**: Deploy changes in phases
- **Health monitoring**: Continuous monitoring during deployment

## Related Documentation

- Observatory Fix Summary: docs/observatory/OBSERVATORY-FIX-SUMMARY.md
- Local Development Setup: docs/observatory/LOCAL-DEVELOPMENT-SETUP.md
- Recovery Summary: OBSERVATORY-RECOVERY-SUCCESS.md