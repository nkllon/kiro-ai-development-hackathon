# Spec Consistency Governance Specification

**Status:** ✅ Ready for DAG Execution
**Last Updated:** 2025-10-03
**Context:** 105 specs in .kiro/specs/ requiring systematic consistency governance

---

## Quick Start

### Execute DAG

```bash
# Validate DAG structure
python scripts/execute_spec_consistency_dag.py --validate

# Show current status
python scripts/execute_spec_consistency_dag.py --status

# Execute Phase 1 (Critical Infrastructure)
python scripts/execute_spec_consistency_dag.py --phase 1 --dry-run

# Execute specific task
python scripts/execute_spec_consistency_dag.py --task 1.1

# Execute all phases
python scripts/execute_spec_consistency_dag.py --phase all
```

---

## Specification Files

| File | Purpose | Status |
|------|---------|--------|
| `requirements.md` | 11 requirements addressing spec inconsistencies | ✅ Complete |
| `design.md` | System architecture and component design | ✅ Complete |
| `tasks.md` | 25 tasks across 5 phases | ✅ Complete |
| `dag-execution-plan.md` | Complete DAG structure and execution strategy | ✅ Complete |
| `README.md` | This file - quick reference | ✅ Complete |

---

## Overview

This specification addresses **systematic spec inconsistency** issues identified in `.kiro/specs/`:

### Current State (105 Specs)
- **23 incomplete specs** (22%) missing required files (requirements.md, design.md, tasks.md)
- **16 specs with extra files** (15%) containing artifacts, backups, revisions
- **3 high-similarity pairs** indicating potential duplication
- **1 empty directory** ("output") serving no purpose
- **No lifecycle governance** leading to abandoned/incomplete specs

### Core Philosophy
**"Complete Specs Enable Complete Solutions"** - systematic specification completeness is a prerequisite for systematic development.

---

## Key Features

### 1. Structural Completeness Enforcement
- Automatic validation for required files (requirements.md, design.md, tasks.md)
- Pre-commit hooks prevent incomplete specs
- Remediation reports show exactly what's missing
- .spec-exempt markers for legitimate exceptions

### 2. File Naming Standardization
- Enforce lowercase kebab-case for directories
- Canonical filenames: requirements.md, design.md, tasks.md (lowercase)
- Detect and fix variants (Requirements.md, REQUIREMENTS.md, etc.)
- Migration commands for renaming

### 3. Extra File Governance
- Execution artifacts moved to `.kiro/execution-logs/{spec-name}/`
- Backups archived to `.kiro/archive/{spec-name}/`
- DAG configs allowed with `.spec-extra-files-approved` marker
- Validation flags unauthorized files

### 4. Duplicate Detection
- Name similarity using Levenshtein distance
- Content similarity analysis
- Consolidation workflows with merge commands
- Manual review for >75% similarity

### 5. Lifecycle State Management
- `.spec-state` files track status (draft, active, deprecated, archived)
- State transitions validated
- Automatic state detection
- Cleanup workflows for archived specs

---

## DAG Execution Strategy

### Total Scope
- **Total Tasks:** 25 across 5 phases
- **Total Time:** 165 hours (~4 weeks)
- **Critical Path:** Phase 1 → Phase 2 → Phase 5

### Phase Breakdown

**Phase 1: Critical Infrastructure (Week 1) - 25 hours**
- Core module structure
- SpecValidator implementation
- CLI interface
- Makefile integration
- **Immediate Impact:** Identify all 23 incomplete specs

**Phase 2: Governance & Prevention (Week 2) - 38 hours**
- Spec registry (JSON index)
- Lifecycle tracking
- Auto-remediation framework
- Git pre-commit hooks
- **Prevents:** Future incomplete specs

**Phase 3: Quality & Automation (Week 3) - 28 hours**
- Template generator for new specs
- Automated stub generation
- File naming fixes
- Enhanced reporting with trends
- **Streamlines:** Spec creation process

**Phase 4: Advanced Features (Week 4) - 42 hours**
- Similarity detection algorithms
- Consolidation workflows
- CI/CD integration
- Performance optimization
- **Eliminates:** Duplicate specs

**Phase 5: Rollout & Remediation (Week 5) - 32 hours**
- Fix all 23 incomplete specs
- Clean 16 specs with extra files
- Complete documentation
- Team training
- **Result:** 100% spec compliance

---

## Task Dependencies

```
Phase 1 (Foundation - Some parallelism)
├── 1.1 Core Module (start)
├── 1.2 SpecValidator (depends: 1.1)
├── 1.3 SpecReporter (depends: 1.1)
├── 1.4 CLI Interface (depends: 1.2, 1.3)
├── 1.5 Remove Empty Dir (independent)
└── 1.6 Makefile Targets (depends: 1.4)

Phase 2 (Parallel after Phase 1)
├── 2.1 Spec Registry (depends: 1.2)
├── 2.2 Lifecycle Tracking (depends: 2.1)
├── 2.3 Remediator Foundation (depends: 1.2)
├── 2.4 Extra File Management (depends: 2.3)
├── 2.5 Git Pre-commit Hook (depends: 2.2)
└── 2.6 Document Standards (independent)

Phase 3 (Parallel options)
├── 3.1 Template Generator (depends: 2.1)
├── 3.2 Automated Stubs (depends: 3.1, 2.3)
├── 3.3 File Naming Fixes (depends: 2.3)
└── 3.4 Enhanced Reporting (depends: 1.3, 2.1)

Phase 4 (Parallel options)
├── 4.1 Similarity Detection (depends: 2.1)
├── 4.2 Consolidation Workflow (depends: 4.1)
├── 4.3 Pilot Consolidation (depends: 4.2)
├── 4.4 CI Integration (depends: 1.4)
└── 4.5 Performance Optimization (depends: 1.2)

Phase 5 (Remediation - Sequential)
├── 5.1 Fix Incomplete Specs (depends: 3.2)
├── 5.2 Clean Extra Files (depends: 2.4)
├── 5.3 Complete Documentation (depends: 2.6)
└── 5.4 Team Training (depends: 5.1, 5.2, 5.3)
```

---

## Success Metrics

### Phase 1 Success
- [ ] All 23 incomplete specs identified in validation report
- [ ] All 16 specs with extra files flagged
- [ ] CLI commands functional
- [ ] Make targets working

### Phase 2 Success
- [ ] All 105 specs indexed in registry
- [ ] Git hooks prevent incomplete commits
- [ ] Remediation framework operational
- [ ] Standards documented

### Phase 3 Success
- [ ] Templates generate valid specs
- [ ] Stubs created for incomplete specs
- [ ] File naming normalized
- [ ] Trend reports available

### Phase 4 Success
- [ ] Duplicate pairs identified
- [ ] Consolidation successful (pilot)
- [ ] CI/CD validation active
- [ ] Performance <3s for all specs

### Phase 5 Success (Final Goal)
- [ ] **100% spec completeness** (0 missing files)
- [ ] **Zero extra files** (all moved to proper locations)
- [ ] **Duplicate specs consolidated**
- [ ] **Team trained on governance**

---

## Requirements Traceability

| Requirement | Component | Tasks | Validation |
|-------------|-----------|-------|------------|
| REQ-1: Structural Completeness | SpecValidator | 1.2, 5.1 | Pre-commit hook |
| REQ-2: File Naming | SpecValidator | 1.2, 3.3 | Naming validation |
| REQ-3: Extra File Governance | Remediator | 2.3, 2.4, 5.2 | File location check |
| REQ-4: Duplicate Detection | Similarity Engine | 4.1, 4.2, 4.3 | Pair analysis |
| REQ-5: Lifecycle Management | Lifecycle Tracker | 2.2 | State validation |
| REQ-6: Empty Dir Cleanup | Manual Task | 1.5 | Directory scan |
| REQ-7: Automated Tooling | CLI + Remediator | 1.4, 2.3 | CLI tests |
| REQ-8: Git Integration | Pre-commit Hook | 2.5 | Hook tests |
| REQ-9: Template System | Template Generator | 3.1, 3.2 | Generated output |
| REQ-10: Traceability | Reporter | 1.3, 3.4 | Report content |
| REQ-11: CI Integration | GitHub Actions | 4.4 | Workflow tests |

---

## Architecture Components

### Core Classes
- `SpecValidator` (ReflectiveModule) - Validates spec structure
- `SpecReporter` (ReflectiveModule) - Generates quality reports
- `SpecRemediator` (ReflectiveModule) - Auto-fixes issues
- `SpecRegistry` - JSON index of all specs
- `LifecycleTracker` - Manages spec states
- `SimilarityDetector` - Finds duplicates
- `TemplateGenerator` - Creates new specs

### Integration Points
- **Git Hooks:** Pre-commit validation
- **CI/CD:** GitHub Actions workflow
- **Makefile:** `make spec-validate`, `make spec-report`
- **CLI:** `spec-governance` command

---

## Files to be Created

### Phase 1 - Critical Infrastructure
```
src/spec_governance/
├── __init__.py
├── models.py
├── validator.py
├── reporter.py
└── cli.py

tests/unit/spec_governance/
├── __init__.py
├── test_validator.py
└── test_reporter.py

tests/integration/spec_governance/
└── test_cli.py
```

### Phase 2 - Governance
```
src/spec_governance/
├── registry.py
├── lifecycle.py
├── remediator.py

.kiro/
└── spec-registry.json

.git/hooks/
└── pre-commit-spec-governance

scripts/
└── install_spec_governance_hooks.sh

docs/spec-governance/
├── standards.md
└── workflow.md
```

### Phase 3 - Quality
```
src/spec_governance/
└── templates.py

templates/spec-template/
├── requirements.md.j2
├── design.md.j2
└── tasks.md.j2
```

### Phase 4 - Advanced
```
src/spec_governance/
└── similarity.py

.github/workflows/
└── spec-governance.yml
```

---

## Risk Mitigation

### Technical Risks

| Risk | Mitigation | Status |
|------|-----------|--------|
| Data loss during remediation | Dry-run mode, rollback capability | ✅ Designed |
| Git history corruption | Non-destructive moves, preserve history | ✅ Designed |
| Performance with 105 specs | Parallel processing, caching | ✅ Task 4.5 |
| False duplicate detection | Manual review required for >75% | ✅ Designed |

### Operational Risks

| Risk | Mitigation | Status |
|------|-----------|--------|
| Team resistance | Gradual rollout, clear benefits | ✅ Phase 5 |
| Workflow disruption | Hooks can be bypassed, training | ✅ Task 5.4 |
| Tool complexity | Simple CLI, good docs | ✅ Task 2.6 |
| Incomplete adoption | CI enforcement, required validation | ✅ Task 4.4 |

---

## Execution Timeline

### Week 1: Critical Infrastructure
**Goal:** Build validation and reporting foundation

| Day | Tasks | Hours | Deliverable |
|-----|-------|-------|-------------|
| 1 | 1.1, 1.2 | 10h | Validator working |
| 2 | 1.3, 1.4 | 12h | CLI functional |
| 3 | 1.5, 1.6 | 3h | Makefile integrated |

**Week 1 End:** Can validate all specs, generate reports

### Week 2: Governance & Prevention
**Goal:** Establish lifecycle management and prevention

| Day | Tasks | Hours | Deliverable |
|-----|-------|-------|-------------|
| 1-2 | 2.1, 2.2 | 14h | Registry + Lifecycle |
| 3-4 | 2.3, 2.4 | 14h | Remediation working |
| 5 | 2.5, 2.6 | 10h | Hooks + Docs |

**Week 2 End:** Git hooks active, remediation ready

### Week 3: Quality & Automation
**Goal:** Streamline spec creation

| Day | Tasks | Hours | Deliverable |
|-----|-------|-------|-------------|
| 1-2 | 3.1, 3.2 | 14h | Templates + Stubs |
| 3 | 3.3 | 4h | Naming fixes |
| 4-5 | 3.4 | 10h | Enhanced reporting |

**Week 3 End:** Automated stub generation

### Week 4: Advanced Features
**Goal:** Eliminate duplicates, optimize performance

| Day | Tasks | Hours | Deliverable |
|-----|-------|-------|-------------|
| 1-2 | 4.1, 4.2 | 22h | Similarity detection |
| 3 | 4.3 | 8h | Pilot consolidation |
| 4-5 | 4.4, 4.5 | 12h | CI + Performance |

**Week 4 End:** Duplicate detection working

### Week 5: Rollout & Remediation
**Goal:** Achieve 100% compliance

| Day | Tasks | Hours | Deliverable |
|-----|-------|-------|-------------|
| 1-3 | 5.1 | 16h | All specs complete |
| 4 | 5.2 | 8h | Extra files cleaned |
| 5 | 5.3, 5.4 | 8h | Docs + Training |

**Week 5 End:** 100% spec compliance achieved

---

## Quality Gates

### Per-Phase Gates

**Phase 1 Gate:**
- Validation detects known issues (23 incomplete, 16 extra files)
- Reports accurate and readable
- CLI commands work
- Tests >90% coverage

**Phase 2 Gate:**
- Registry indexes all 105 specs
- Hooks prevent incomplete commits
- Remediation safe (no data loss in testing)
- Standards clear and complete

**Phase 3 Gate:**
- Templates generate valid specs
- Stubs pass validation
- Naming fixes preserve git history
- Trend reports accurate

**Phase 4 Gate:**
- Duplicates identified correctly
- Consolidation doesn't lose data
- CI runs successfully
- Performance <3s

**Phase 5 Gate:**
- All 23 incomplete specs fixed
- All 16 extra file specs cleaned
- Zero validation errors
- Team trained successfully

---

## Impact Analysis

### Immediate Impact (After Phase 1)
- **Visibility:** All 23 incomplete specs identified
- **Metrics:** Quality baseline established
- **Tooling:** Validation available on-demand

### Short-term Impact (After Phase 2)
- **Prevention:** Git hooks stop new incomplete specs
- **Automation:** Remediation reduces manual work
- **Governance:** Lifecycle tracking active

### Medium-term Impact (After Phase 3)
- **Efficiency:** Template generation speeds spec creation
- **Quality:** Automated stubs ensure completeness
- **Trends:** Quality improvements tracked over time

### Long-term Impact (After Phase 5)
- **Compliance:** 100% spec completeness
- **Consistency:** Standardized structure across all specs
- **Sustainability:** Governance prevents regression
- **Productivity:** Reduced cognitive load, clearer specs

---

## Related Documents

- **Spec Analysis:** `.kiro/specs/spec-consistency-governance/.spec-state`
- **Similar Specs:** `spec-consistency-reconciliation`, `spec-scrub-rdi-consistency`
- **Governance Docs:** `.kiro/steering/` (to be created)

---

## Next Steps

### Immediate Actions (Today)
1. ✅ Validate spec completeness - **DONE**
2. ✅ Create DAG orchestrator - **DONE**
3. ✅ Validate DAG structure - **DONE**
4. ⏳ Execute Task 1.1 (Core Module Structure)

### This Week
1. Execute Phase 1 (Critical Infrastructure)
2. Generate first validation report
3. Identify all incomplete specs
4. Plan remediation strategy

### Next Week
1. Execute Phase 2 (Governance & Prevention)
2. Implement git hooks
3. Build remediation framework
4. Document standards

---

## Contact & Support

For questions or issues with this specification:
1. Review requirements.md for detailed acceptance criteria
2. Check design.md for architectural details
3. Consult tasks.md for implementation guidance
4. Run DAG validation to ensure structure integrity

---

**Last Validation:** 2025-10-03 22:17:30
**DAG Status:** ✓ Valid structure, 25 tasks, 3 ready to execute
**Next Executable:**
- Task 1.1: Core Module Structure (2h)
- Task 1.5: Remove Empty Directory (1h)
- Task 2.6: Document Standards (4h)
