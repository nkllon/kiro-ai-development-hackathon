#!/usr/bin/env python3
"""
Generate Phase 2-4 Batch Prompts

Creates 60 batch prompts for requirements, designs, and tasks across the 4 constellation layers.
Each prompt elaborates 5-10 specs in a batch.
"""

import json
from pathlib import Path

# Get all specs
specs_dir = Path(".kiro/specs")
all_specs = sorted([d.name for d in specs_dir.iterdir() if d.is_dir()])

print(f"Found {len(all_specs)} specs")

# Layer classification (based on repository constellation)
layers = {
    "bootstrap": [
        "repository-setup-and-installation",
    ],
    "foundation": [
        "spec-framework",
        "spec-consistency-governance",
        "system-health-mitigation-framework",
        "service-auto-start-governance",
        "cms-architecture",
        "directus-cms-systematic-implementation",
        "directus-schema-design",
        "directus-ui-configuration",
        "directus-data-population",
        "directus-reconciliation-systematic",
        "directus-ai-memory-palace-integration",
        "anti-duplication-system",
        "spec-consistency-reconciliation",
        "makefile-syntax-repair-governance",
        "executable-patch-code-governance",
    ],
    "intelligence": [],  # Will auto-populate
    "application": [],  # Will auto-populate
}

# Auto-classify remaining specs (simple heuristic)
classified = set()
for layer_specs in layers.values():
    classified.update(layer_specs)

remaining = [s for s in all_specs if s not in classified]

# Intelligence layer: monitoring, discovery, rm-ddd, observatory
intelligence_keywords = ["monitor", "discover", "observatory", "rm-ddd", "rmddd", "analysis", "prometheus", "metrics", "index", "constellation"]
application_keywords = ["bot", "discord", "mcp", "google", "calendar", "engagement", "devpost", "launch"]

for spec in remaining:
    spec_lower = spec.lower()
    if any(kw in spec_lower for kw in intelligence_keywords):
        layers["intelligence"].append(spec)
    elif any(kw in spec_lower for kw in application_keywords):
        layers["application"].append(spec)
    else:
        # Default to intelligence
        layers["intelligence"].append(spec)

# Create batches (5-10 specs per batch)
BATCH_SIZE = 8

def create_batches(specs):
    """Split specs into batches of ~8"""
    batches = []
    for i in range(0, len(specs), BATCH_SIZE):
        batches.append(specs[i:i + BATCH_SIZE])
    return batches

layer_batches = {
    layer: create_batches(specs)
    for layer, specs in layers.items()
}

print("\nLayer breakdown:")
for layer, batches in layer_batches.items():
    print(f"  {layer}: {len(layers[layer])} specs in {len(batches)} batches")

# Generate prompts for each phase (2, 3, 4) × each layer × each batch
prompts_created = []

for phase_num, phase_name, phase_desc in [
    (2, "requirements", "Requirements Elaboration"),
    (3, "design", "Design Documentation"),
    (4, "tasks", "Task Breakdown"),
]:
    for layer in ["bootstrap", "foundation", "intelligence", "application"]:
        batches = layer_batches[layer]

        for batch_idx, batch_specs in enumerate(batches, 1):
            batch_num = batch_idx
            total_batches = len(batches)

            prompt_name = f"phase-{phase_num}-{layer}-{phase_name}-batch{batch_num}"
            prompt_file = Path(f"prompts/staging/{prompt_name}.md")

            # Calculate estimated time
            time_per_spec = {
                "requirements": 15,  # 15 min per spec
                "design": 18,        # 18 min per spec
                "tasks": 12,         # 12 min per spec
            }

            est_min = len(batch_specs) * time_per_spec[phase_name]
            est_range = f"{est_min}-{int(est_min * 1.3)}"

            # Create prompt content
            content = f"""# {prompt_name.replace('-', ' ').title()} ({est_range} min)

## Objective

Elaborate {phase_desc.lower()} for {len(batch_specs)} specs in the {layer.title()} layer (batch {batch_num} of {total_batches}).

## Specs in This Batch

{chr(10).join(f"{i+1}. `{spec}`" for i, spec in enumerate(batch_specs))}

## Task

### 1. Load Phase 1 Analyses

```bash
cat .kiro/reports/constellation-inventory-2025.json
cat .kiro/reports/stakeholder-journey-maps.json
cat .kiro/reports/dimension-coverage-complete.json
cat .kiro/reports/gap-remediation-plan.yaml
```

### 2. For Each Spec in Batch

"""

            if phase_name == "requirements":
                content += """#### A. Read Existing Requirements (if present)

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

"""
            elif phase_name == "design":
                content += """#### A. Read Requirements

```bash
cat .kiro/specs/{spec}/requirements.md
```

#### B. Elaborate Design

Create or update `design.md` with:

**1. Architecture Overview**

```markdown
## Architecture

### System Context
[How this spec fits in constellation]

### Component Diagram
[Key components and relationships]

### Data Flow
[How data moves through the system]
```

**2. Detailed Design**

```markdown
## Detailed Design

### Component 1: [Name]
**Responsibilities:**
- [What it does]

**Interfaces:**
- [APIs exposed]

**Dependencies:**
- [What it needs]

**Implementation Notes:**
- [Key decisions, patterns]

[Continue for all components]
```

**3. CMS Integration Design**

If spec has CMS dependencies:

```markdown
## CMS Integration

### Schema Design
\`\`\`yaml
collections:
  {collection_name}:
    fields:
      - name: id
        type: uuid
      [...]
\`\`\`

### API Endpoints
- POST /items/{collection}
- GET /items/{collection}
[...]

### Workflows
- On create: [automation]
- On update: [automation]
```

**4. Risk Mitigation**

Based on dimension analysis:

```markdown
## Risk Mitigation

### Performance Risks
- [Risk]: [Mitigation]

### Security Risks
- [Risk]: [Mitigation]

### Operational Risks
- [Risk]: [Mitigation]
```

"""
            else:  # tasks
                content += """#### A. Read Requirements and Design

```bash
cat .kiro/specs/{spec}/requirements.md
cat .kiro/specs/{spec}/design.md
```

#### B. Elaborate Tasks

Create or update `tasks.md` with:

**1. Task Breakdown**

```markdown
## Implementation Tasks

### Phase 1: Foundation
- [ ] T1.1: Set up project structure
- [ ] T1.2: Implement core interfaces
- [ ] T1.3: Set up testing framework

### Phase 2: Core Implementation
- [ ] T2.1: Implement Component A
- [ ] T2.2: Implement Component B
- [ ] T2.3: Integration tests

### Phase 3: CMS Integration
- [ ] T3.1: Define CMS schema
- [ ] T3.2: Implement CMS API integration
- [ ] T3.3: Set up permissions
- [ ] T3.4: Test CMS workflows

### Phase 4: Documentation & Deployment
- [ ] T4.1: API documentation
- [ ] T4.2: User guide
- [ ] T4.3: Deployment scripts
- [ ] T4.4: Monitoring setup

[Continue with specific tasks based on design]
```

**2. Dependencies**

```markdown
## Dependencies

### Spec Dependencies
- Requires: [other specs that must be complete first]
- Enables: [specs that depend on this]

### Technical Dependencies
- Libraries: [required packages]
- Services: [required infrastructure]
- Tools: [required dev tools]
```

**3. Acceptance Criteria**

```markdown
## Acceptance Criteria

- [ ] All requirements from requirements.md implemented
- [ ] All components from design.md built
- [ ] Unit test coverage > 80%
- [ ] Integration tests pass
- [ ] Documentation complete
- [ ] CMS integration tested (if applicable)
- [ ] All 22 dimensions addressed
```

"""

            content += f"""### 3. Save Updated Files

For each spec, save the updated `{phase_name}.md` file:

```bash
# Example for first spec
cat > .kiro/specs/{batch_specs[0]}/{phase_name}.md <<'EOF'
[content here]
EOF
```

### 4. Validation

Verify each spec now has:
- Updated {phase_name}.md with comprehensive content
- All stakeholder requirements addressed
- All 22 dimensions covered
- CMS dependencies documented (if applicable)

## Deliverables

For each of the {len(batch_specs)} specs:
- `.kiro/specs/{{spec}}/{phase_name}.md` - Complete {phase_desc.lower()}

Summary report:
- `.kiro/reports/phase-{phase_num}-{layer}-batch{batch_num}-summary.md` - Completion summary

## Timeline

**Duration:** {est_range} minutes
**Dependencies:** Phase 1 complete, previous batches if sequential
**Enables:** Next phase for these specs
"""

            # Write prompt file
            with open(prompt_file, 'w') as f:
                f.write(content)

            prompts_created.append(prompt_name)
            print(f"Created: {prompt_name}")

print(f"\n✅ Created {len(prompts_created)} batch prompts")
print(f"\nSummary:")
print(f"  Phase 2 (requirements): {len([p for p in prompts_created if 'phase-2' in p])} prompts")
print(f"  Phase 3 (design): {len([p for p in prompts_created if 'phase-3' in p])} prompts")
print(f"  Phase 4 (tasks): {len([p for p in prompts_created if 'phase-4' in p])} prompts")
