# Phase 2 Foundation Requirements Batch2 (105-136 min)

## Objective

Elaborate requirements elaboration for 7 specs in the Foundation layer (batch 2 of 2).

## Specs in This Batch

1. `directus-data-population`
2. `directus-reconciliation-systematic`
3. `directus-ai-memory-palace-integration`
4. `anti-duplication-system`
5. `spec-consistency-reconciliation`
6. `makefile-syntax-repair-governance`
7. `executable-patch-code-governance`

## Task

### 1. Load Phase 1 Analyses

```bash
cat .kiro/reports/constellation-inventory-2025.json
cat .kiro/reports/stakeholder-journey-maps.json
cat .kiro/reports/dimension-coverage-complete.json
cat .kiro/reports/gap-remediation-plan.yaml
```

### 2. For Each Spec in Batch

#### A. Read Existing Requirements (if present)

```bash
cat .kiro/specs/{spec}/requirements.md
```

#### B. Elaborate Requirements

Create or update `requirements.md` with:

**1. Stakeholder Requirements**

Based on stakeholder journey maps, add user stories for each relevant stakeholder:

```markdown
## Stakeholder Requirements

### Developer
- **R1**: As a Developer, I need clear API documentation so I can integrate quickly
- **R2**: As a Developer, I need examples so I can learn patterns
[Continue for all relevant stakeholders]

### DevOps
- **R3**: As a DevOps Engineer, I need deployment scripts so I can automate
[...]
```

**2. 22-Dimension Coverage**

Based on gap remediation plan, ensure coverage of all 22 dimensions:

```markdown
## Dimensional Requirements

### Problem Taxonomy
- Root cause analysis of the problem this spec solves
- Problem classification and scope

### Infrastructure Architecture
- Deployment requirements
- Resource requirements
- System dependencies

### Solution Architecture
- High-level design approach
- Key patterns and structures

[Continue for all 22 dimensions]
```

**3. CMS Dependencies**

Based on CMS analyses, document CMS requirements:

```markdown
## CMS Requirements

### Data Model
- Collections needed: [list]
- Fields required: [list]
- Relationships: [list]

### Capabilities
- APIs: [REST/GraphQL endpoints]
- Permissions: [roles and access control]
- Workflows: [automation needs]
- Integrations: [webhooks, hooks]
```

### 3. Save Updated Files

For each spec, save the updated `requirements.md` file:

```bash
# Example for first spec
cat > .kiro/specs/directus-data-population/requirements.md <<'EOF'
[content here]
EOF
```

### 4. Validation

Verify each spec now has:
- Updated requirements.md with comprehensive content
- All stakeholder requirements addressed
- All 22 dimensions covered
- CMS dependencies documented (if applicable)

## Deliverables

For each of the 7 specs:
- `.kiro/specs/{spec}/requirements.md` - Complete requirements elaboration

Summary report:
- `.kiro/reports/phase-2-foundation-batch2-summary.md` - Completion summary

## Timeline

**Duration:** 105-136 minutes
**Dependencies:** Phase 1 complete, previous batches if sequential
**Enables:** Next phase for these specs
