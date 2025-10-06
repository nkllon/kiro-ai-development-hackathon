#!/usr/bin/env python3
"""Generate Phase 5 breakdown prompts"""

from pathlib import Path

prompts = [
    # CMS Consolidation (5a series - 6 prompts)
    {
        "name": "phase-5a2-cms-api-consolidation",
        "title": "CMS API Consolidation",
        "time": "75-105",
        "objective": "Consolidate all CMS API requirements (REST, GraphQL, subscriptions) into comprehensive API specification.",
        "deps": "phase-5a1-cms-data-model-consolidation",
        "enables": "phase-5a3-cms-permissions-consolidation",
        "deliverable": ".kiro/specs/cms-architecture/cms-api-specification.yaml"
    },
    {
        "name": "phase-5a3-cms-permissions-consolidation",
        "title": "CMS Permissions Consolidation",
        "time": "60-90",
        "objective": "Consolidate all CMS permission requirements (roles, RBAC, field-level permissions) into comprehensive permission model.",
        "deps": "phase-5a2-cms-api-consolidation",
        "enables": "phase-5a4-cms-workflow-consolidation",
        "deliverable": ".kiro/specs/cms-architecture/cms-permissions-model.yaml"
    },
    {
        "name": "phase-5a4-cms-workflow-consolidation",
        "title": "CMS Workflow Consolidation",
        "time": "60-90",
        "objective": "Consolidate all CMS workflow requirements (automation, hooks, webhooks, state transitions).",
        "deps": "phase-5a3-cms-permissions-consolidation",
        "enables": "phase-5a5-cms-integration-consolidation",
        "deliverable": ".kiro/specs/cms-architecture/cms-workflows.yaml"
    },
    {
        "name": "phase-5a5-cms-integration-consolidation",
        "title": "CMS Integration Consolidation",
        "time": "60-90",
        "objective": "Consolidate all CMS integration requirements (external APIs, webhooks, event streaming).",
        "deps": "phase-5a4-cms-workflow-consolidation",
        "enables": "phase-5a6-cms-requirements-merge",
        "deliverable": ".kiro/specs/cms-architecture/cms-integrations.yaml"
    },
    {
        "name": "phase-5a6-cms-requirements-merge",
        "title": "CMS Requirements Merge",
        "time": "90-120",
        "objective": "Merge all CMS consolidations into comprehensive requirements.md for CMS Architecture spec.",
        "deps": "phase-5a1, phase-5a2, phase-5a3, phase-5a4, phase-5a5",
        "enables": "phase-5b1-cms-architecture-design-update",
        "deliverable": ".kiro/specs/cms-architecture/requirements.md (v3.0)"
    },

    # CMS Architecture Updates (5b series - 3 prompts)
    {
        "name": "phase-5b1-cms-architecture-design-update",
        "title": "CMS Architecture Design Update",
        "time": "90-120",
        "objective": "Update CMS Architecture design.md based on consolidated requirements, including complete system architecture.",
        "deps": "phase-5a6-cms-requirements-merge",
        "enables": "phase-5b2-cms-architecture-tasks-update",
        "deliverable": ".kiro/specs/cms-architecture/design.md (v3.0)"
    },
    {
        "name": "phase-5b2-cms-architecture-tasks-update",
        "title": "CMS Architecture Tasks Update",
        "time": "75-105",
        "objective": "Update CMS Architecture tasks.md with implementation roadmap based on updated design.",
        "deps": "phase-5b1-cms-architecture-design-update",
        "enables": "phase-5b3-cms-dependent-specs-update",
        "deliverable": ".kiro/specs/cms-architecture/tasks.md (v3.0)"
    },
    {
        "name": "phase-5b3-cms-dependent-specs-update",
        "title": "CMS-Dependent Specs Update",
        "time": "60-90",
        "objective": "Update all specs with CMS dependencies to reference the consolidated CMS Architecture spec.",
        "deps": "phase-5b2-cms-architecture-tasks-update",
        "enables": "phase-5c1-constellation-cms-mapping",
        "deliverable": "Updated requirements.md for all CMS-dependent specs"
    },

    # Constellation Mapping (5c series - 3 prompts)
    {
        "name": "phase-5c1-constellation-cms-mapping",
        "title": "Constellation CMS Mapping",
        "time": "60-90",
        "objective": "Update Repository Constellation spec to explicitly map CMS dependencies for all specs.",
        "deps": "phase-5b3-cms-dependent-specs-update",
        "enables": "phase-5c2-constellation-layer-analysis",
        "deliverable": ".kiro/specs/repository-constellation-specification/cms-dependency-map.md"
    },
    {
        "name": "phase-5c2-constellation-layer-analysis",
        "title": "Constellation Layer Analysis",
        "time": "75-105",
        "objective": "Analyze and document layer dependencies, critical paths, and execution order in constellation.",
        "deps": "phase-5c1-constellation-cms-mapping",
        "enables": "phase-5c3-constellation-spec-update",
        "deliverable": ".kiro/specs/repository-constellation-specification/layer-analysis.md"
    },
    {
        "name": "phase-5c3-constellation-spec-update",
        "title": "Constellation Spec Update",
        "time": "90-120",
        "objective": "Update Repository Constellation requirements.md, design.md, tasks.md with all findings.",
        "deps": "phase-5c2-constellation-layer-analysis",
        "enables": "phase-5d1-stakeholder-validation",
        "deliverable": ".kiro/specs/repository-constellation-specification/*.md (updated)"
    },

    # Final Validation (5d series - 4 prompts)
    {
        "name": "phase-5d1-stakeholder-validation",
        "title": "Stakeholder Requirements Validation",
        "time": "75-105",
        "objective": "Validate all stakeholder requirements are addressed across all 107 specs.",
        "deps": "phase-5c3-constellation-spec-update",
        "enables": "phase-5d2-dimension-coverage-validation",
        "deliverable": ".kiro/reports/stakeholder-validation-report.md"
    },
    {
        "name": "phase-5d2-dimension-coverage-validation",
        "title": "Dimension Coverage Validation",
        "time": "90-120",
        "objective": "Validate all 22 dimensions are covered across all 107 specs after elaboration.",
        "deps": "phase-5d1-stakeholder-validation",
        "enables": "phase-5d3-cms-integration-validation",
        "deliverable": ".kiro/reports/dimension-coverage-final.json"
    },
    {
        "name": "phase-5d3-cms-integration-validation",
        "title": "CMS Integration Validation",
        "time": "60-90",
        "objective": "Validate all CMS dependencies are properly documented and integrated.",
        "deps": "phase-5d2-dimension-coverage-validation",
        "enables": "phase-5d4-execution-roadmap",
        "deliverable": ".kiro/reports/cms-integration-validation.md"
    },
    {
        "name": "phase-5d4-execution-roadmap",
        "title": "Execution Roadmap Creation",
        "time": "90-120",
        "objective": "Create comprehensive execution roadmap based on all elaborated specs, with priorities and timeline.",
        "deps": "phase-5d1, phase-5d2, phase-5d3",
        "enables": "Implementation can begin!",
        "deliverable": ".kiro/reports/constellation-execution-roadmap.md"
    },
]

for prompt_data in prompts:
    filename = f"prompts/staging/{prompt_data['name']}.md"

    content = f"""# {prompt_data['name'].replace('-', ' ').title()} ({prompt_data['time']} min)

## Objective

{prompt_data['objective']}

## Task

### 1. Load Dependencies

```bash
cat .kiro/reports/constellation-inventory-2025.json
# Load other relevant Phase 1-4 outputs
```

### 2. Analysis and Processing

[Perform the specific analysis/consolidation for this prompt]

### 3. Create Deliverable

{prompt_data['deliverable']}

## Validation

- Verify completeness
- Check consistency with other phases
- Validate against requirements

## Deliverables

- {prompt_data['deliverable']}

## Timeline

**Duration:** {prompt_data['time']} minutes
**Dependencies:** {prompt_data['deps']}
**Enables:** {prompt_data['enables']}
"""

    with open(filename, 'w') as f:
        f.write(content)

    print(f"Created: {prompt_data['name']}")

print(f"\n✅ Created {len(prompts)} Phase 5 prompts")
