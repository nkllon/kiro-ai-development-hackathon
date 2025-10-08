# Phase 2: Spec Batch Requirements Template

## Template Usage

This template should be instantiated for each batch of 5-10 specs.

**Example Instances:**
- `phase-2-bootstrap-batch1.md` - Specs: repository-setup-and-installation, developer-onboarding, environment-standardization
- `phase-2-foundation-batch1.md` - Specs: spec-consistency-governance, system-health-mitigation, service-auto-start-governance
- `phase-2-intelligence-batch1.md` - Specs: repository-content-discovery, ghostbusters-framework, rm-ddd-framework, pdca-orchestrator, rca-tools

## Template Structure

```markdown
# Phase 2: [Layer Name] Requirements - Batch [N]

## Specs in This Batch

1. [spec-name-1]
2. [spec-name-2]
3. [spec-name-3]
4. [spec-name-4]
5. [spec-name-5]

## Objective

Elaborate comprehensive requirements.md for the above [N] specifications.

## Context

**Layer:** [Bootstrap/Foundation/Intelligence/Application]
**Batch Size:** [N] specs
**Input Dependencies:**
- Phase 1a: Constellation inventory
- Phase 1b: Stakeholder requirements
- Phase 1c: CMS dependencies
- Phase 1d: Ontology gaps

## Task

For EACH spec in this batch:

### 1. Read Inputs

- Phase 1a inventory entry for this spec
- Phase 1b stakeholder requirements for this spec
- Phase 1c CMS dependencies for this spec
- Phase 1d ontology gaps for this spec
- Current requirements.md (if exists)

### 2. Write Comprehensive Requirements.md

Follow structure from `phase-2-bootstrap-requirements.md` detailed template:

- Overview with single responsibility
- Stakeholder requirements (all applicable types)
- Functional requirements
- Non-functional requirements
- 22-dimension coverage analysis
- CMS integration analysis
- Dependencies and integration
- Success criteria
- Compliance and governance

### 3. Create Validation Report

For each spec: `.kiro/specs/[spec-name]/requirements-validation-2025.md`

## Per-Spec Checklist

For each spec, validate:
- ✅ All Phase 1d gaps addressed
- ✅ All stakeholder types addressed
- ✅ 90%+ dimension coverage (20/22)
- ✅ CMS dependencies explicit
- ✅ Success criteria measurable

## Deliverables

- requirements.md for each spec in batch
- requirements-validation-2025.md for each spec
- Batch completion report

## Estimated Time

**Per Spec:** 75-90 minutes
**Batch Total:** [N × 75-90] minutes = [calculated time]

## Timeline

**Duration:** [batch-specific time]
**Dependencies:** Phase 1a, 1b, 1c, 1d complete
**Parallelization:** Can run in parallel with other batches in same layer
```

## Batch Creation Guidelines

### Batch Size

**Optimal:** 5 specs per batch
- 5 specs × 80 min = 400 min (6.67 hours)
- Keeps each prompt under 7 hours
- Allows good parallelization

**Maximum:** 10 specs per batch
- Only for simple specs (e.g., small application specs)
- 10 specs × 75 min = 750 min (12.5 hours)
- Still allows some parallelization

### Batch Grouping Strategy

**Group by:**
1. **Constellation layer** (required)
2. **Related functionality** (preferred)
3. **Similar complexity** (preferred)

**Example Good Batches:**
- Observatory specs together (all related)
- Directus CMS specs together (all related)
- Monitoring specs together (similar domain)

**Example Bad Batches:**
- Mix of simple and complex specs (uneven time)
- Unrelated specs (harder to maintain context)

## Automation

Can generate batch prompts automatically:

```python
# Pseudocode
specs_by_layer = get_specs_from_phase1a()

for layer in ['bootstrap', 'foundation', 'intelligence', 'application']:
    specs = specs_by_layer[layer]
    batches = chunk_specs(specs, batch_size=5)

    for i, batch in enumerate(batches):
        create_prompt(
            name=f"phase-2-{layer}-batch{i+1}.md",
            template="phase-2-spec-batch-template.md",
            specs=batch
        )
```
