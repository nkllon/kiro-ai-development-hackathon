# Master Constellation Elaboration Executor

## Executive Summary

This master prompt orchestrates the complete elaboration of all 108 specifications in the repository constellation, ensuring comprehensive requirements, designs, and tasks are developed for each spec while maintaining consistency with the 22-dimension project ontology and identifying all CMS dependencies.

## Execution Context

**Repository State:**
- 108 specification directories in `.kiro/specs/`
- Repository Constellation defined with 4-layer architecture (Bootstrap, Foundation, Intelligence, Application)
- 22-dimension ontology framework established
- CMS Architecture specification with comprehensive stakeholder requirements
- Repository Content Discovery & Indexing ready for implementation

**Objectives:**
1. Elaborate all incomplete specifications with comprehensive requirements, designs, and tasks
2. Ensure all specifications align with the 22-dimension ontology
3. Identify and document CMS dependencies for each specification
4. Update CMS Architecture spec to support all identified requirements
5. Update Repository Constellation spec with explicit CMS dependency mapping
6. Create comprehensive stakeholder analysis for all specs

## Parallelization Strategy

### Phase 1: Discovery and Analysis (Parallel Execution - Day 1)
Execute all Phase 1 prompts in parallel as they are independent:
- `phase-1a-constellation-inventory.md` - Inventory all 108 specs
- `phase-1b-stakeholder-landscape-mapping.md` - Map all stakeholders
- `phase-1c-cms-dependency-discovery.md` - Discover existing CMS dependencies
- `phase-1d-ontology-gap-analysis.md` - Analyze gaps against 22 dimensions

**Dependencies:** None (all can run simultaneously)
**Deliverables:**
- Complete spec inventory with completion status
- Stakeholder requirements matrix
- Initial CMS dependency map
- Ontology coverage analysis

### Phase 2: Requirements Elaboration (Parallel by Layer - Days 2-4)
Execute in layers with parallelization within each layer:

**Layer 0 - Bootstrap (Parallel):**
- `phase-2-bootstrap-requirements.md` - Elaborate all bootstrap spec requirements

**Layer 1 - Foundation (Parallel, depends on Layer 0):**
- `phase-2-foundation-requirements.md` - Elaborate all foundation spec requirements

**Layer 2 - Intelligence (Parallel, depends on Layer 1):**
- `phase-2-intelligence-requirements.md` - Elaborate all intelligence spec requirements

**Layer 3 - Application (Parallel, depends on Layer 2):**
- `phase-2-application-requirements.md` - Elaborate all application spec requirements

**Dependencies:** Sequential by layer, parallel within each layer
**Deliverables:**
- Complete requirements.md for all 108 specs
- Stakeholder acceptance criteria for all requirements
- 22-dimension validation for each spec
- CMS integration requirements identified

### Phase 3: Design Development (Parallel by Layer - Days 5-7)
Execute in layers with parallelization within each layer:

**Layer 0 - Bootstrap (Parallel):**
- `phase-3-bootstrap-designs.md` - Develop all bootstrap spec designs

**Layer 1 - Foundation (Parallel, depends on Layer 0):**
- `phase-3-foundation-designs.md` - Develop all foundation spec designs

**Layer 2 - Intelligence (Parallel, depends on Layer 1):**
- `phase-3-intelligence-designs.md` - Develop all intelligence spec designs

**Layer 3 - Application (Parallel, depends on Layer 2):**
- `phase-3-application-designs.md` - Develop all application spec designs

**Dependencies:** Sequential by layer, parallel within each layer
**Deliverables:**
- Complete design.md for all 108 specs
- Architecture diagrams and component designs
- Interface specifications and API contracts
- Data models and integration patterns

### Phase 4: Task Breakdown (Parallel by Layer - Days 8-10)
Execute in layers with parallelization within each layer:

**Layer 0 - Bootstrap (Parallel):**
- `phase-4-bootstrap-tasks.md` - Break down all bootstrap spec tasks

**Layer 1 - Foundation (Parallel, depends on Layer 0):**
- `phase-4-foundation-tasks.md` - Break down all foundation spec tasks

**Layer 2 - Intelligence (Parallel, depends on Layer 1):**
- `phase-4-intelligence-tasks.md` - Break down all intelligence spec tasks

**Layer 3 - Application (Parallel, depends on Layer 2):**
- `phase-4-application-tasks.md` - Break down all application spec tasks

**Dependencies:** Sequential by layer, parallel within each layer
**Deliverables:**
- Complete tasks.md for all 108 specs
- Task dependencies and execution DAGs
- Resource estimates and timelines
- Testing and validation criteria

### Phase 5: CMS Integration & Consolidation (Sequential - Days 11-12)
Execute sequentially as each depends on previous:

1. `phase-5a-cms-requirements-consolidation.md` - Consolidate all CMS requirements
2. `phase-5b-cms-architecture-update.md` - Update CMS Architecture spec
3. `phase-5c-constellation-cms-mapping.md` - Update Constellation spec with CMS dependencies
4. `phase-5d-stakeholder-validation.md` - Validate stakeholder coverage

**Dependencies:** All Phase 1-4 outputs
**Deliverables:**
- Updated CMS Architecture requirements.md with all dependencies
- Updated Repository Constellation spec with CMS dependency mapping
- Stakeholder validation report
- Final constellation execution roadmap

## Master Execution Command

```bash
# Phase 1: Discovery (All in parallel)
claude < prompts/staging/phase-1a-constellation-inventory.md &
claude < prompts/staging/phase-1b-stakeholder-landscape-mapping.md &
claude < prompts/staging/phase-1c-cms-dependency-discovery.md &
claude < prompts/staging/phase-1d-ontology-gap-analysis.md &
wait

# Phase 2: Requirements by Layer
# Layer 0
claude < prompts/staging/phase-2-bootstrap-requirements.md
# Layer 1
claude < prompts/staging/phase-2-foundation-requirements.md
# Layer 2
claude < prompts/staging/phase-2-intelligence-requirements.md
# Layer 3
claude < prompts/staging/phase-2-application-requirements.md

# Phase 3: Designs by Layer
# Layer 0
claude < prompts/staging/phase-3-bootstrap-designs.md
# Layer 1
claude < prompts/staging/phase-3-foundation-designs.md
# Layer 2
claude < prompts/staging/phase-3-intelligence-designs.md
# Layer 3
claude < prompts/staging/phase-3-application-designs.md

# Phase 4: Tasks by Layer
# Layer 0
claude < prompts/staging/phase-4-bootstrap-tasks.md
# Layer 1
claude < prompts/staging/phase-4-foundation-tasks.md
# Layer 2
claude < prompts/staging/phase-4-intelligence-tasks.md
# Layer 3
claude < prompts/staging/phase-4-application-tasks.md

# Phase 5: CMS Integration (Sequential)
claude < prompts/staging/phase-5a-cms-requirements-consolidation.md
claude < prompts/staging/phase-5b-cms-architecture-update.md
claude < prompts/staging/phase-5c-constellation-cms-mapping.md
claude < prompts/staging/phase-5d-stakeholder-validation.md
```

## Success Criteria

### Completeness Metrics
- ✅ 100% of specs have requirements.md with 22-dimension validation
- ✅ 100% of specs have design.md with architecture and interfaces
- ✅ 100% of specs have tasks.md with DAG and dependencies
- ✅ 100% of stakeholder concerns addressed across all specs
- ✅ 100% of CMS dependencies identified and documented

### Quality Metrics
- ✅ All requirements trace to stakeholder needs
- ✅ All designs align with Beast Mode architecture patterns
- ✅ All tasks include validation criteria and success metrics
- ✅ All CMS requirements consolidated in CMS Architecture spec
- ✅ Repository Constellation updated with complete dependency graph

### Consistency Metrics
- ✅ No duplicate requirements across specifications
- ✅ No conflicting architectural decisions
- ✅ No circular dependencies in task execution
- ✅ Consistent stakeholder analysis across all specs
- ✅ Unified CMS integration strategy

## Timeline

**Total Duration:** 12 working days

**Phase 1 (Day 1):** Discovery and Analysis - All parallel
**Phase 2 (Days 2-4):** Requirements Elaboration - Layer-by-layer
**Phase 3 (Days 5-7):** Design Development - Layer-by-layer
**Phase 4 (Days 8-10):** Task Breakdown - Layer-by-layer
**Phase 5 (Days 11-12):** CMS Integration - Sequential

## Dependencies and Prerequisites

**Required:**
- Access to all 108 spec directories in `.kiro/specs/`
- Repository Constellation specification
- CMS Architecture specification
- 22-dimension ontology framework
- Beast Mode architecture patterns
- Stakeholder requirements templates

**Outputs:**
- Complete requirements.md for 108 specs
- Complete design.md for 108 specs
- Complete tasks.md for 108 specs
- Updated CMS Architecture spec
- Updated Repository Constellation spec
- Stakeholder validation report

## Execution Notes

1. **Parallelization:** Phase 1 prompts can all run in parallel. Phases 2-4 are layer-sequential but can be parallelized within each layer if multiple agents are available.

2. **Checkpointing:** Each phase produces artifacts that can be validated before proceeding. If issues are found, re-run specific phase prompts.

3. **Incremental Delivery:** Specifications can be validated and used as soon as their phase completes, enabling early implementation starts.

4. **CMS Integration:** CMS dependencies are discovered throughout Phases 1-4 and consolidated in Phase 5.

5. **Stakeholder Validation:** Stakeholder concerns are tracked throughout all phases and validated in Phase 5.

## Next Steps

1. Review and approve this master execution strategy
2. Create all phase-specific prompts (see below)
3. Execute Phase 1 prompts in parallel
4. Validate Phase 1 outputs before proceeding
5. Execute Phases 2-4 layer-by-layer
6. Execute Phase 5 sequentially
7. Validate final constellation completeness
