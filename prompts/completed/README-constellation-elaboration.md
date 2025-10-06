# Repository Constellation Elaboration - Complete Prompt Suite

## Overview

This directory contains a comprehensive, interdependent set of prompts to elaborate all 108 specifications in the repository constellation with complete requirements, designs, and tasks that are consistent with the 22-dimension project ontology and explicitly identify all CMS dependencies.

## Execution Summary

**Total Duration:** 12 working days
**Total Prompts:** 18 prompts across 5 phases
**Specs Elaborated:** 108 specifications
**Layers Covered:** 4 constellation layers (Bootstrap, Foundation, Intelligence, Application)
**Dimensions Validated:** 22 project ontology dimensions
**Stakeholders Addressed:** 15+ stakeholder types

## Prompt Suite Structure

### Master Execution Prompt
- **File:** `master-constellation-elaboration-executor.md`
- **Purpose:** Orchestrates entire elaboration process with parallelization strategy
- **Duration:** 12 days
- **Dependencies:** None (entry point)

### Phase 1: Discovery and Analysis (Day 1 - Parallel)

All Phase 1 prompts can execute in parallel:

1. **phase-1a-constellation-inventory.md**
   - Inventory all 108 specs with completion status
   - Classify by constellation layer
   - Identify missing artifacts
   - Duration: 4-6 hours
   - Dependencies: None
   - Outputs: `.kiro/reports/constellation-inventory-2025.json`

2. **phase-1b-stakeholder-landscape-mapping.md**
   - Map all stakeholder types across constellation
   - Extract existing stakeholder requirements
   - 22-dimension priority analysis per stakeholder
   - Duration: 6-8 hours
   - Dependencies: None
   - Outputs: `.kiro/reports/stakeholder-requirements-matrix.md`

3. **phase-1c-cms-dependency-discovery.md**
   - Discover explicit and implicit CMS dependencies
   - Map CMS capability requirements
   - Define CMS data model needs
   - Duration: 6-8 hours
   - Dependencies: None
   - Outputs: `.kiro/reports/cms-dependency-catalog.json`

4. **phase-1d-ontology-gap-analysis.md**
   - Analyze existing specs against 22 dimensions
   - Identify cross-cutting dimension gaps
   - Prioritize gap remediation
   - Duration: 8-10 hours
   - Dependencies: None (but needs existing requirements.md files)
   - Outputs: `.kiro/reports/dimension-coverage-analysis.md`

**Phase 1 Total:** 1 day (24-32 hours of work parallelized)

### Phase 2: Requirements Elaboration (Days 2-4 - Layer Sequential)

Process by constellation layer, parallelizable within each layer:

5. **phase-2-bootstrap-requirements.md**
   - Elaborate requirements for all Bootstrap (Layer 0) specs
   - Ensure 22-dimension coverage
   - Address Phase 1d gaps
   - Duration: 1.5-2 days
   - Dependencies: Phase 1 complete
   - Outputs: Updated requirements.md for bootstrap specs

6. **phase-2-foundation-requirements.md**
   - Elaborate requirements for all Foundation (Layer 1) specs
   - Focus on reliability, monitoring, governance
   - Duration: 1.5-2 days
   - Dependencies: Phase 1 complete, Bootstrap requirements complete
   - Outputs: Updated requirements.md for foundation specs

7. **phase-2-intelligence-requirements.md**
   - Elaborate requirements for all Intelligence (Layer 2) specs
   - Heavy CMS integration focus
   - Duration: 2-3 days
   - Dependencies: Phase 1 complete, Foundation requirements complete
   - Outputs: Updated requirements.md for intelligence specs

8. **phase-2-application-requirements.md**
   - Elaborate requirements for all Application (Layer 3) specs
   - All stakeholder coverage validation
   - Duration: 1.5-2 days
   - Dependencies: Phase 1 complete, Intelligence requirements complete
   - Outputs: Updated requirements.md for application specs

**Phase 2 Total:** 3 days (sequential by layer)

### Phase 3: Design Development (Days 5-7 - Layer Sequential)

9. **phase-3-bootstrap-designs.md**
   - Create comprehensive designs for bootstrap specs
   - Installation architecture, CLI design
   - Duration: 1.5-2 days
   - Dependencies: Phase 2 bootstrap requirements complete
   - Outputs: design.md for all bootstrap specs

10. **phase-3-foundation-designs.md**
    - Create comprehensive designs for foundation specs
    - Service health, auto-start, CMS architecture
    - Duration: 1.5-2 days
    - Dependencies: Phase 2 foundation requirements complete
    - Outputs: design.md for all foundation specs

11. **phase-3-intelligence-designs.md**
    - Create comprehensive designs for intelligence specs
    - Discovery algorithms, analysis frameworks
    - Duration: 2-3 days
    - Dependencies: Phase 2 intelligence requirements complete
    - Outputs: design.md for all intelligence specs

12. **phase-3-application-designs.md**
    - Create comprehensive designs for application specs
    - UI/UX, intelligence consumers, dashboards
    - Duration: 1.5-2 days
    - Dependencies: Phase 2 application requirements complete
    - Outputs: design.md for all application specs

**Phase 3 Total:** 3 days (sequential by layer)

### Phase 4: Task Breakdown (Days 8-10 - Layer Sequential)

13. **phase-4-bootstrap-tasks.md**
    - Create task breakdowns with DAGs for bootstrap specs
    - Installation, validation, cleanup tasks
    - Duration: 1.5-2 days
    - Dependencies: Phase 3 bootstrap designs complete
    - Outputs: tasks.md for all bootstrap specs

14. **phase-4-foundation-tasks.md**
    - Create task breakdowns with DAGs for foundation specs
    - Service setup, monitoring, CMS implementation tasks
    - Duration: 1.5-2 days
    - Dependencies: Phase 3 foundation designs complete
    - Outputs: tasks.md for all foundation specs

15. **phase-4-intelligence-tasks.md**
    - Create task breakdowns with DAGs for intelligence specs
    - Discovery, analysis, AI/ML pipeline tasks
    - Duration: 2-3 days
    - Dependencies: Phase 3 intelligence designs complete
    - Outputs: tasks.md for all intelligence specs

16. **phase-4-application-tasks.md**
    - Create task breakdowns with DAGs for application specs
    - UI development, integration, dashboard tasks
    - Duration: 1.5-2 days
    - Dependencies: Phase 3 application designs complete
    - Outputs: tasks.md for all application specs

**Phase 4 Total:** 3 days (sequential by layer)

### Phase 5: CMS Integration & Consolidation (Days 11-12 - Sequential)

17. **phase-5a-cms-requirements-consolidation.md**
    - Consolidate all CMS requirements from Phases 1-4
    - Deduplicate and resolve conflicts
    - Create unified CMS data model
    - Duration: 1 day
    - Dependencies: Phases 1-4 complete
    - Outputs: `.kiro/reports/cms-requirements-consolidated.yaml`

18. **phase-5b-cms-architecture-update.md**
    - Update CMS Architecture spec with consolidated requirements
    - Add complete data model to design
    - Update implementation tasks
    - Duration: 1 day
    - Dependencies: Phase 5a complete
    - Outputs: Updated CMS Architecture spec v3.0

19. **phase-5c-constellation-cms-mapping.md**
    - Update Repository Constellation spec with CMS dependencies
    - Add CMS integration architecture section
    - Update critical path with CMS gating
    - Duration: 0.5 days
    - Dependencies: Phase 5a, 5b complete
    - Outputs: Updated Repository Constellation spec

20. **phase-5d-stakeholder-validation.md**
    - Validate all stakeholder coverage
    - Validate 22-dimension constellation coverage
    - Create final execution roadmap
    - Duration: 1 day
    - Dependencies: All previous phases complete
    - Outputs: Final validation reports and execution roadmap

**Phase 5 Total:** 2 days (sequential)

## Execution Dependency Graph

See `constellation-execution-dag.mmd` for visual DAG.

**Critical Path:**
```
Phase 1 (parallel)
  → Phase 2 Bootstrap
  → Phase 2 Foundation
  → Phase 2 Intelligence
  → Phase 2 Application
  → Phase 3 Bootstrap
  → Phase 3 Foundation
  → Phase 3 Intelligence
  → Phase 3 Application
  → Phase 4 Bootstrap
  → Phase 4 Foundation
  → Phase 4 Intelligence
  → Phase 4 Application
  → Phase 5 (sequential a→b→c→d)
```

## Parallelization Opportunities

**Maximum Parallelization:**
- Phase 1: 4 prompts in parallel (max 4 agents)
- Within each Phase 2/3/4 layer: All specs in that layer can be processed in parallel
- Phase 5: Sequential (no parallelization)

**Practical Parallelization (2 agents):**
- Phase 1: 2+2 prompts (6-8 hours per pair)
- Phase 2/3/4: Process multiple specs per layer in parallel
- Phase 5: Sequential

## Key Outputs

### Reports Generated
- `.kiro/reports/constellation-inventory-2025.json` - Complete spec inventory
- `.kiro/reports/stakeholder-requirements-matrix.md` - Stakeholder analysis
- `.kiro/reports/cms-dependency-catalog.json` - CMS dependencies
- `.kiro/reports/dimension-coverage-analysis.md` - 22-dimension coverage
- `.kiro/reports/cms-requirements-consolidated.yaml` - Consolidated CMS needs
- `.kiro/reports/cms-unified-data-model.yaml` - Complete CMS schema
- `.kiro/reports/constellation-execution-roadmap-final.md` - Implementation roadmap
- `.kiro/reports/constellation-elaboration-complete.md` - Completion certificate

### Specs Updated
- 108 specs with requirements.md (v2.0)
- 108 specs with design.md (v2.0)
- 108 specs with tasks.md (v2.0)
- CMS Architecture spec (v3.0)
- Repository Constellation spec (updated with CMS mapping)

## Success Criteria

✅ 100% of 108 specs have complete requirements.md with 22-dimension coverage
✅ 100% of 108 specs have complete design.md with architecture and interfaces
✅ 100% of 108 specs have complete tasks.md with execution DAGs
✅ All stakeholder concerns addressed across constellation
✅ All CMS dependencies identified and consolidated
✅ CMS Architecture updated with complete requirements
✅ Repository Constellation updated with CMS dependency mapping
✅ Final execution roadmap created with clear phases

## Validation Checklist

For each spec after elaboration:
- ✅ requirements.md has 90%+ dimension coverage (20/22 dimensions)
- ✅ All CRITICAL dimensions for that layer are addressed
- ✅ All applicable stakeholder requirements present
- ✅ CMS dependencies explicitly identified (if any)
- ✅ design.md has complete architecture and component designs
- ✅ design.md has CMS integration design (if applicable)
- ✅ tasks.md has complete task breakdown with DAG
- ✅ tasks.md has resource estimates and testing requirements
- ✅ No conflicts with other specs
- ✅ Dependencies properly documented

## Usage Instructions

### Option 1: Automated Sequential Execution

Execute the master prompt with all phase prompts in sequence:

```bash
claude < prompts/staging/master-constellation-elaboration-executor.md
```

### Option 2: Manual Phase-by-Phase Execution

**Day 1 - Phase 1 (Parallel):**
```bash
# Execute all in parallel or in sequence
claude < prompts/staging/phase-1a-constellation-inventory.md &
claude < prompts/staging/phase-1b-stakeholder-landscape-mapping.md &
claude < prompts/staging/phase-1c-cms-dependency-discovery.md &
claude < prompts/staging/phase-1d-ontology-gap-analysis.md &
wait
```

**Days 2-4 - Phase 2 (By Layer):**
```bash
claude < prompts/staging/phase-2-bootstrap-requirements.md
claude < prompts/staging/phase-2-foundation-requirements.md
claude < prompts/staging/phase-2-intelligence-requirements.md
claude < prompts/staging/phase-2-application-requirements.md
```

**Days 5-7 - Phase 3 (By Layer):**
```bash
claude < prompts/staging/phase-3-bootstrap-designs.md
claude < prompts/staging/phase-3-foundation-designs.md
claude < prompts/staging/phase-3-intelligence-designs.md
claude < prompts/staging/phase-3-application-designs.md
```

**Days 8-10 - Phase 4 (By Layer):**
```bash
claude < prompts/staging/phase-4-bootstrap-tasks.md
claude < prompts/staging/phase-4-foundation-tasks.md
claude < prompts/staging/phase-4-intelligence-tasks.md
claude < prompts/staging/phase-4-application-tasks.md
```

**Days 11-12 - Phase 5 (Sequential):**
```bash
claude < prompts/staging/phase-5a-cms-requirements-consolidation.md
claude < prompts/staging/phase-5b-cms-architecture-update.md
claude < prompts/staging/phase-5c-constellation-cms-mapping.md
claude < prompts/staging/phase-5d-stakeholder-validation.md
```

## Troubleshooting

**If a phase fails:**
1. Review the output for errors
2. Fix any issues in the source specs
3. Re-run just that phase prompt
4. Validate outputs before proceeding to next phase

**If dimension coverage is low:**
1. Review dimension-requirement-templates.md from Phase 1d
2. Add missing dimension requirements to specs
3. Re-run the requirements elaboration for affected specs

**If CMS consolidation finds major conflicts:**
1. Review conflict resolution log
2. Update conflicting specs with resolutions
3. Re-run Phase 5a consolidation
4. Validate all specs accept the resolution

## Next Steps After Completion

1. Review `.kiro/reports/constellation-elaboration-complete.md`
2. Review `.kiro/reports/constellation-execution-roadmap-final.md`
3. Review `.kiro/reports/gap-remediation-plan.md`
4. Begin implementation following the execution roadmap
5. Start with Bootstrap layer (repository-setup-and-installation)
6. Proceed through Foundation, Intelligence, Application layers

## Maintainers

This prompt suite is part of the Beast Mode Framework repository constellation.

**Last Updated:** 2025-10-04
**Version:** 1.0
**Status:** Ready for execution
