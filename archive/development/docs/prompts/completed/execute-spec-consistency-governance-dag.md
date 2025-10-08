# Execute Spec Consistency Governance DAG

**Prompt Type:** DAG Execution
**Spec:** `.kiro/specs/spec-consistency-governance`
**Status:** Ready for Execution
**PCA Applied:** Yes
**Priority:** CRITICAL

---

## Mission

Execute the Spec Consistency Governance DAG to systematically implement a governance system that ensures all 110+ specs maintain structural completeness, naming consistency, and proper lifecycle management. This addresses the critical gap where 23 specs (21%) are incomplete and establishes permanent prevention mechanisms.

---

## Context

### Current State
- **Total Specs:** 110 (increased from 105)
- **Incomplete Specs:** 23 (missing requirements.md, design.md, or tasks.md)
- **Specs with Extra Files:** 16 (DAG artifacts, backups, non-standard files)
- **Lifecycle Visibility:** 0% (no state tracking)
- **Validation Coverage:** 0% (no pre-commit enforcement)

### Target State
- **Spec Completeness:** 100%
- **Extra File Compliance:** 100%
- **Lifecycle Visibility:** 100%
- **Validation Coverage:** 100% (pre-commit hooks active)
- **Documentation:** Complete spec standards guide

### Why This Matters
Incomplete specifications create systematic development gaps. This governance system applies the **permanent corrective action framework** to prevent future spec inconsistencies while remediating existing issues.

---

## Execution Strategy

### Recommended: Hybrid Execution (4 weeks)

This balances thoroughness with efficiency by executing critical path first, then parallelizing where safe.

```bash
# Preview the full execution plan (DRY RUN)
./scripts/execute_spec_consistency_governance_dag.py --dry-run --strategy=hybrid

# Execute Phase 1 (Critical Infrastructure)
./scripts/execute_spec_consistency_governance_dag.py --phase=1

# After Phase 1 validated, continue with Phase 2
./scripts/execute_spec_consistency_governance_dag.py --phase=2

# Phases 3-4 can overlap (automation + advanced features)
./scripts/execute_spec_consistency_governance_dag.py --phase=3
./scripts/execute_spec_consistency_governance_dag.py --phase=4

# Phase 5 (final rollout after 3-4 complete)
./scripts/execute_spec_consistency_governance_dag.py --phase=5

# Generate final report
./scripts/execute_spec_consistency_governance_dag.py --report
```

---

## Phase-by-Phase Instructions

### Phase 1: Critical Infrastructure (Week 1, 25 hours)

**Goal:** Build validation and reporting foundation

**Critical Tasks:**
1. **Task 1.1** (2h): Create `src/spec_governance/` module structure
2. **Task 1.2** (8h): Implement `SpecValidator` - detect all 23 incomplete specs
3. **Task 1.3** (6h): Implement `SpecReporter` - generate markdown reports
4. **Task 1.4** (6h): Create CLI with `spec-governance validate` command
5. **Task 1.5** (1h): Remove empty `.kiro/specs/output/` directory
6. **Task 1.6** (2h): Add Makefile targets (`make spec-validate`)

**Validation Gate:**
```bash
# Verify Phase 1 complete
make spec-validate
# Should detect all 23 incomplete specs

make spec-report
# Should generate comprehensive report
```

**Acceptance Criteria:**
- [ ] `src/spec_governance/` package imports successfully
- [ ] `SpecValidator` detects all 23 incomplete specs
- [ ] Report matches manual analysis (23 incomplete, 16 with extras)
- [ ] CLI commands functional: `spec-governance validate --all`
- [ ] Makefile targets work: `make spec-validate`, `make spec-report`
- [ ] Validation completes in <5 seconds for all 110 specs

---

### Phase 2: Governance & Prevention (Week 2, 38 hours)

**Goal:** Establish lifecycle management and git hooks

**Critical Tasks:**
1. **Task 2.1** (8h): Build `SpecRegistry` with JSON index of all 110 specs
2. **Task 2.2** (6h): Implement `.spec-state` lifecycle tracking (draft/active/completed/deprecated)
3. **Task 2.3** (8h): Implement `SpecRemediator` with dry-run mode
4. **Task 2.4** (6h): Extra file management - move to `.kiro/execution-logs/`, `.kiro/archive/`
5. **Task 2.5** (6h): Create git pre-commit hook to block incomplete specs
6. **Task 2.6** (4h): Document spec standards in `.kiro/docs/spec-standards.md`

**Validation Gate:**
```bash
# Verify registry contains all specs
cat .kiro/spec-registry.json | jq '.specs | length'
# Should show 110

# Test git hook (create incomplete spec)
mkdir .kiro/specs/test-incomplete
touch .kiro/specs/test-incomplete/requirements.md
git add .kiro/specs/test-incomplete
git commit -m "test"
# Should BLOCK commit with error message
```

**Acceptance Criteria:**
- [ ] Registry JSON contains all 110 specs with metadata
- [ ] Lifecycle states persist in `.spec-state` files
- [ ] Remediator dry-run shows preview without changes
- [ ] Extra files categorized and moved correctly
- [ ] Git hook blocks commits with incomplete specs
- [ ] Spec standards documentation comprehensive

---

### Phase 3: Quality & Automation (Week 3, 24 hours)

**Goal:** Enable automated spec creation and fixing

**Critical Tasks:**
1. **Task 3.1** (8h): Template generator with EARS format examples
2. **Task 3.2** (6h): Automated stub generation for 23 incomplete specs
3. **Task 3.3** (4h): File naming standardization (lowercase enforcement)
4. **Task 3.4** (6h): Enhanced reporting with trend analysis

**Validation Gate:**
```bash
# Test template generation
make spec-create NAME=test-automation DESC="Test automated creation"
# Should create complete spec with requirements.md, design.md, tasks.md

# Generate stubs (dry-run first)
python -m spec_governance.cli remediate --create-stubs --dry-run
# Review output, then execute without --dry-run
```

**Acceptance Criteria:**
- [ ] `make spec-create` generates valid complete specs
- [ ] Templates follow EARS format (WHEN-THEN structure)
- [ ] Stub generation completes for all 23 incomplete specs
- [ ] File naming standardized (devpost-hackathon-integration fixed)
- [ ] Trend reports show quality improvement metrics

---

### Phase 4: Advanced Features (Week 3-4, 34 hours)

**Goal:** Duplicate detection and consolidation

**Tasks (can overlap with Phase 3):**
1. **Task 4.1** (8h): Levenshtein distance similarity detection
2. **Task 4.2** (10h): Interactive consolidation workflow
3. **Task 4.3** (6h): Pilot consolidation: spec-framework + spec-mode-framework
4. **Task 4.4** (4h): CI integration with JSON output
5. **Task 4.5** (6h): Performance optimization (parallel processing)

**Validation Gate:**
```bash
# Test similarity detection
python -m spec_governance.cli validate --check-duplicates
# Should flag 3 known pairs: spec-framework/spec-mode-framework,
# redis-dag-registry/unified-dag-registry,
# observatory-deployment-procedures/observatory-deployment-system

# Performance benchmark
time make spec-validate
# Should complete in <5 seconds
```

**Acceptance Criteria:**
- [ ] Similarity detection finds 3 known high-similarity pairs (>75%)
- [ ] Consolidation workflow preserves all information from both specs
- [ ] Pilot consolidation completes without data loss
- [ ] CI mode outputs valid JSON with correct exit codes
- [ ] Full validation <5s, incremental <1s

---

### Phase 5: Rollout & Remediation (Week 5, 30 hours)

**Goal:** Apply governance to all specs and train team

**Critical Tasks:**
1. **Task 5.1** (12h): Fix all 23 incomplete specs with enhanced stubs
2. **Task 5.2** (6h): Clean up extra files from 16 affected specs
3. **Task 5.3** (8h): Complete documentation and troubleshooting guides
4. **Task 5.4** (4h): Team training walkthrough

**Validation Gate:**
```bash
# Final validation - must achieve 100%
make spec-validate
# Should report: 0 incomplete specs, 0 unapproved extra files

# Verify lifecycle visibility
cat .kiro/spec-registry.json | jq '[.specs[] | select(.lifecycle_state == null)] | length'
# Should be 0 (all specs have lifecycle state)

# Test git hook on real workflow
# (Create new spec, try to commit with only requirements.md - should block)
```

**Acceptance Criteria:**
- [ ] All 110 specs have requirements.md, design.md, tasks.md
- [ ] All extra files in proper locations (execution-logs/ or archive/)
- [ ] All specs have `.spec-state` lifecycle metadata
- [ ] Git hooks active and preventing incomplete specs
- [ ] Documentation includes troubleshooting guide
- [ ] Team trained on new workflows

---

## Success Metrics

Track these throughout execution:

```bash
# Generate metrics report
make spec-report

# Key metrics to track:
# - Spec Completeness: Target 100% (start: 78%)
# - Extra File Compliance: Target 100% (start: 84%)
# - Lifecycle Visibility: Target 100% (start: 0%)
# - Validation Coverage: 100% of commits (start: 0%)
```

### Weekly Checkpoints

**Week 1 (Phase 1 complete):**
- [ ] Validation detects all known issues
- [ ] Report generation working
- [ ] CLI functional

**Week 2 (Phase 2 complete):**
- [ ] Registry tracks all 110 specs
- [ ] Git hooks active
- [ ] Standards documented

**Week 3 (Phases 3-4 complete):**
- [ ] Templates generate valid specs
- [ ] Similarity detection working
- [ ] Performance targets met

**Week 4 (Phase 5 complete):**
- [ ] **100% spec completeness**
- [ ] **100% lifecycle visibility**
- [ ] **100% validation coverage**
- [ ] Team adoption

---

## Permanent Corrective Action Framework

This execution applies the PCA pattern from `docs/cms/cms-auto-start-root-cause-analysis.md`:

### 1. Technical Fix (Phases 1-4)
**Problem:** 23 incomplete specs, no validation
**Solution:** Build validation/remediation tools, fix all specs

### 2. Operational Fix (Phases 2-3)
**Problem:** No prevention mechanism
**Solution:** Git hooks block incomplete specs, templates ensure compliance

### 3. Requirements Fix (Phases 2, 5)
**Problem:** Unclear spec standards
**Solution:** Document standards, train team, enforce systematically

### PCA Pattern Applied
```
Problem (23 incomplete specs, no governance)
    → Root Cause (No enforcement, unclear standards, no lifecycle tracking)
    → Solution (Validation + remediation + lifecycle management)
    → Prevention (Git hooks + templates + documentation)
    → Future Specs (Always complete, properly governed)
```

---

## Risk Management

### High-Risk Points

**Risk 1: Task 5.1 - Fixing 23 incomplete specs**
- **Mitigation:** Dry-run first, manual review of stubs, incremental commits
- **Rollback:** Git history preserves originals

**Risk 2: Task 2.5 - Git hooks may block legitimate work**
- **Mitigation:** Document override procedures, phased rollout
- **Override:** `git commit --no-verify` (requires justification)

**Risk 3: Task 4.3 - Consolidation may lose information**
- **Mitigation:** Backup originals to `.kiro/archive/`, manual review
- **Rollback:** Restore from archive, mark consolidation as failed

### Validation Gates

Stop and validate after each phase:
- **After Phase 1:** Validate detection accuracy (compare to manual analysis)
- **After Phase 2:** Test git hooks don't break workflow
- **After Phase 3:** Validate template quality
- **After Phase 4:** Verify no data loss in consolidation
- **After Phase 5:** Achieve 100% completion target

---

## Execution Commands Reference

### Start Execution
```bash
# Preview full DAG
./scripts/execute_spec_consistency_governance_dag.py --dry-run

# Execute phase-by-phase (recommended)
./scripts/execute_spec_consistency_governance_dag.py --phase=1
# Validate, then continue...
./scripts/execute_spec_consistency_governance_dag.py --phase=2
# ... and so on

# Execute specific tasks
./scripts/execute_spec_consistency_governance_dag.py --tasks=1.1,1.2,1.3
```

### Monitor Progress
```bash
# Generate status report
./scripts/execute_spec_consistency_governance_dag.py --report

# Check execution state
cat .kiro/execution-logs/spec-consistency-governance/execution-state.json | jq .

# View completed tasks
cat .kiro/execution-logs/spec-consistency-governance/execution-state.json | \
  jq '.tasks | to_entries[] | select(.value.status == "completed") | .key'
```

### Validation Commands
```bash
# Validate all specs
make spec-validate

# Generate quality report
make spec-report

# Create new spec from template
make spec-create NAME=my-feature DESC="Feature description"

# Check for duplicates
python -m spec_governance.cli validate --check-duplicates
```

### Remediation Commands
```bash
# Preview fixes (dry-run)
python -m spec_governance.cli remediate --auto --dry-run

# Create missing stub files
python -m spec_governance.cli remediate --create-stubs

# Move extra files to proper locations
python -m spec_governance.cli remediate --move-extras

# Apply all safe fixes
python -m spec_governance.cli remediate --auto --confirm
```

---

## Rollback Procedures

If execution fails or produces unexpected results:

### Rollback Single Remediation
```bash
# Check remediation log
cat .kiro/remediation-log.json

# Rollback by timestamp
python scripts/rollback_spec_remediation.py --timestamp YYYYMMDDHHMMSS
```

### Rollback Git Changes
```bash
# View recent commits
git log --oneline -10

# Rollback last commit
git reset --hard HEAD~1

# Rollback to specific commit
git reset --hard <commit-hash>
```

### Disable Git Hook
```bash
# Temporarily disable
rm .git/hooks/pre-commit

# Re-enable
python scripts/git_hooks/install_hooks.py
```

---

## Task-Specific Guidance

### Task 1.2: Implement SpecValidator
**Key Implementation:**
```python
# Must detect these 23 incomplete specs:
incomplete_specs = [
    "devpost-hackathon-integration",
    "anti-duplication-system",
    "artifact-classification-transfer-learning",
    "beast-mode-deployment-architecture",
    "beast-mode-reliability-requirements",
    # ... and 18 more (see requirements.md)
]

# Validation logic:
for spec in all_specs:
    has_requirements = (spec_path / "requirements.md").exists()
    has_design = (spec_path / "design.md").exists()
    has_tasks = (spec_path / "tasks.md").exists()

    if not (has_requirements and has_design and has_tasks):
        report_incomplete(spec)
```

### Task 2.5: Create Git Pre-commit Hook
**Hook Logic:**
```bash
# .git/hooks/pre-commit
#!/bin/bash

# Get modified spec directories
modified_specs=$(git diff --cached --name-only | grep '^\.kiro/specs/' | cut -d/ -f1-3 | sort -u)

# Validate each modified spec
for spec in $modified_specs; do
    python -m spec_governance.cli validate --spec "$spec" --ci
    if [ $? -ne 0 ]; then
        echo "❌ Commit blocked: Spec $spec is incomplete"
        exit 1
    fi
done
```

### Task 5.1: Fix All Incomplete Specs
**Affected Specs (23 total):**
```
devpost-hackathon-integration (also needs canonical file fix)
anti-duplication-system
artifact-classification-transfer-learning
beast-mode-deployment-architecture
beast-mode-reliability-requirements
directus-data-population
directus-schema-design
directus-ui-configuration
information-exhaust-preservation
meta-monitoring-experiment
meta-observatory-streaming
observatory-editorial-intelligence
observatory-emergency-repair
observatory-social-authentication
observatory-system-recovery
redis-dag-registry
beast-mode-rebuild
directus-cms-systematic-implementation
reflective-coordinator-system
subprocess-safety-requirements
bot-defense-command-center
competitive-launch-strategy
(+1 more to be discovered)
```

**Process:**
1. Generate stub for each spec
2. Review generated content
3. Enhance with actual information where available
4. Mark inactive specs for potential archival
5. Commit systematically (one spec per commit or batched by category)

---

## Documentation Artifacts

This execution will create/update:

### Created Files
- `src/spec_governance/*.py` - Core governance modules
- `.kiro/spec-registry.json` - Spec metadata index
- `.kiro/docs/spec-standards.md` - Comprehensive standards guide
- `.git/hooks/pre-commit` - Validation hook
- `makefiles/spec-governance.mk` - Make targets
- `.kiro/execution-logs/spec-consistency-governance/` - Execution logs

### Updated Files
- 23 incomplete specs (add missing files)
- 16 specs with extra files (move to proper locations)
- All 110 specs (add `.spec-state` lifecycle metadata)
- `.pre-commit-config.yaml` - Add spec validation
- Main `Makefile` - Include spec-governance.mk
- `CLAUDE.md` - Reference spec standards

---

## Final Verification Checklist

Before marking execution complete:

### System Level
- [ ] `make spec-validate` reports 0 incomplete specs
- [ ] `make spec-validate` reports 0 unapproved extra files
- [ ] All 110 specs have `.spec-state` files
- [ ] `.kiro/spec-registry.json` contains all 110 specs
- [ ] Git hooks prevent incomplete spec commits
- [ ] `make spec-create` generates valid specs

### Metrics Level
- [ ] Spec completeness: 100% (was 78%)
- [ ] Extra file compliance: 100% (was 84%)
- [ ] Lifecycle visibility: 100% (was 0%)
- [ ] Validation coverage: 100% of commits (was 0%)

### Documentation Level
- [ ] `.kiro/docs/spec-standards.md` comprehensive
- [ ] CLI help documentation complete
- [ ] Troubleshooting guide written
- [ ] Team training completed

### Quality Level
- [ ] Unit test coverage >90% for validator, remediator
- [ ] Integration tests pass
- [ ] Performance targets met (<5s validation)
- [ ] No regression in existing functionality

---

## Post-Execution

### Immediate (Week 5)
1. Generate final report: `make spec-report`
2. Archive execution logs
3. Update project documentation
4. Announce new workflows to team

### Week 6 (Monitor)
- Monitor git hook effectiveness
- Collect feedback on new workflows
- Address any edge cases discovered
- Refine documentation based on usage

### Month 2 (Optimize)
- Review spec quality trends
- Consider consolidating high-similarity pairs
- Optimize performance if needed
- Archive deprecated specs

---

## Success Definition

This DAG execution is **complete and successful** when:

1. ✅ All 110 specs structurally complete (requirements.md, design.md, tasks.md)
2. ✅ All extra files in proper locations
3. ✅ All specs have lifecycle state metadata
4. ✅ Git hooks active and preventing incomplete specs
5. ✅ Template generation working for new specs
6. ✅ Documentation complete and team trained
7. ✅ Validation runs on every commit
8. ✅ Quality metrics at 100%

**Expected Timeline:** 3-5 weeks (165 hours estimated)
**Risk Level:** Medium (managed via validation gates)
**Impact:** CRITICAL - Establishes systematic spec governance permanently

---

## Questions or Issues?

**Before starting:**
- Review `.kiro/specs/spec-consistency-governance/requirements.md` for detailed requirements
- Review `.kiro/specs/spec-consistency-governance/design.md` for architecture
- Review `.kiro/specs/spec-consistency-governance/dag-execution-plan.md` for dependency graph

**During execution:**
- Check execution state: `cat .kiro/execution-logs/spec-consistency-governance/execution-state.json`
- Generate status report: `./scripts/execute_spec_consistency_governance_dag.py --report`
- Review validation output: `make spec-validate`

**If blocked:**
- Check task dependencies in dag-execution-plan.md
- Review acceptance criteria for previous phase
- Verify validation gates passed
- Check rollback procedures if needed

---

**Prompt Status:** ✅ Ready for Execution
**Last Updated:** 2025-10-03
**Prepared By:** Claude Code - Beast Mode Framework
