# Specification Standards Guide

## Overview

This guide defines the standards and best practices for creating and maintaining specifications in the `.kiro/specs/` directory.

## Required File Structure

Every specification MUST contain exactly three files:

### 1. requirements.md
**Purpose:** Define what the system should do
**Format:** EARS (Easy Approach to Requirements Syntax)

```markdown
# Requirements Document: [Spec Name]

## Introduction
[Brief description of the feature/system]

## Requirements

### Requirement 1: [Requirement Name]
**User Story:** As a [role], I want [feature], so that [benefit].

#### Acceptance Criteria
1. WHEN [condition] THEN the system SHALL [behavior]
2. WHEN [condition] THEN the system SHALL [behavior]

**Priority:** CRITICAL/HIGH/MEDIUM/LOW
```

### 2. design.md
**Purpose:** Define how the system will be built
**Format:** Technical architecture and implementation details

```markdown
# Design Document: [Spec Name]

## Overview
[System architecture overview]

## Components
[Detailed component descriptions]

## Data Models
[Data structures and schemas]

## Integration Points
[External system interfaces]

## Error Handling
[Error scenarios and recovery]

## Testing Strategy
[Testing approach and coverage]
```

### 3. tasks.md
**Purpose:** Define implementation steps
**Format:** Actionable task breakdown with acceptance criteria

```markdown
# Tasks: [Spec Name]

## Phase 1: [Phase Name]

### Task 1.1: [Task Name]
**Requirement:** REQ-1 ([Requirement Description])
**Estimated Effort:** [X hours]

**Steps:**
1. [Detailed implementation step]
2. [Detailed implementation step]

**Acceptance:**
- [Specific acceptance criteria]
- [Specific acceptance criteria]
```

## Lifecycle States

Every spec has a lifecycle state tracked in `.spec-state` file:

- **DRAFT** - Incomplete or under development
- **ACTIVE** - Complete and being implemented
- **COMPLETED** - Implementation finished
- **DEPRECATED** - No longer relevant
- **ARCHIVED** - Moved to archive for historical reference

## File Naming Conventions

- Use lowercase filenames: `requirements.md`, `design.md`, `tasks.md`
- Spec directory names use kebab-case: `my-feature-name`
- No spaces or special characters in directory names

## Content Standards

### Requirements (EARS Format)
- Use "WHEN...THEN...SHALL" structure
- Be specific and testable
- Include priority levels
- Reference user stories

### Design Documents
- Include component diagrams where helpful
- Specify data models and interfaces
- Address error handling and edge cases
- Define testing strategy

### Task Lists
- Reference specific requirements
- Include estimated effort
- Provide clear acceptance criteria
- Break down into manageable chunks

## Quality Gates

### Pre-commit Validation
All specs are validated before commit:
- Must have all three required files
- Files must not be empty
- No unapproved extra files

### Validation Commands
```bash
# Validate all specs
make spec-validate

# Validate specific spec
PYTHONPATH=src python -m spec_governance.cli validate --spec SPEC_NAME

# Generate quality report
make spec-report
```

## Creating New Specs

### Using Templates
```bash
# Create new spec with template
make spec-create NAME=my-feature DESC="Feature description"
```

### Manual Creation
1. Create directory: `.kiro/specs/my-feature-name/`
2. Create three required files with proper templates
3. Validate: `make spec-validate`
4. Commit when complete

## Extra Files Policy

### Allowed Extra Files
- `.spec-state` - Lifecycle state tracking
- `.spec-exempt` - Exemption from certain rules
- `.spec-extra-files` - Approved extra files list
- `dag-config.yml` - DAG execution configuration
- `DAG_EXECUTION_PLAN.md` - DAG planning documents
- `LAUNCH_READINESS.md` - Launch preparation documents

### Prohibited Extra Files
- Backup files (`*_backup.md`, `*_fixed.md`)
- Execution artifacts (`LAUNCH_SUMMARY.md`, `PARALLEL_DAG_LAUNCH.md`)
- Analysis files (unless approved in `.spec-extra-files`)

### File Organization
- **Archive:** `.kiro/archive/SPEC_NAME/` - For backup files
- **Execution Logs:** `.kiro/execution-logs/SPEC_NAME/` - For execution artifacts

## Troubleshooting

### Common Issues

#### "Spec is incomplete"
**Cause:** Missing required files
**Fix:** Create missing `requirements.md`, `design.md`, or `tasks.md`

#### "Extra files detected"
**Cause:** Unapproved files in spec directory
**Fix:** Move to appropriate location or add to `.spec-extra-files`

#### "Git commit blocked"
**Cause:** Pre-commit hook detected incomplete spec
**Fix:** Complete the spec or use `git commit --no-verify` (not recommended)

### Validation Commands
```bash
# Check specific spec
PYTHONPATH=src python -m spec_governance.cli validate --spec SPEC_NAME

# Get detailed report
make spec-report

# Check what's missing
PYTHONPATH=src python -m spec_governance.cli validate --all | grep "missing"
```

### Override Procedures
```bash
# Bypass pre-commit hook (emergency only)
git commit --no-verify -m "Emergency commit"

# Mark spec as exempt from validation
echo "reason: Emergency deployment" > .kiro/specs/SPEC_NAME/.spec-exempt
```

## Best Practices

### Requirements Writing
- Start with user stories
- Use measurable acceptance criteria
- Consider edge cases and error conditions
- Include performance requirements where relevant

### Design Documentation
- Keep diagrams simple and focused
- Document decision rationales
- Include security considerations
- Plan for monitoring and observability

### Task Planning
- Break large tasks into smaller ones
- Include testing tasks
- Estimate effort realistically
- Plan for integration and deployment

### Lifecycle Management
- Update lifecycle state as work progresses
- Archive completed specs appropriately
- Deprecate obsolete specs rather than deleting

## Compliance

### Automated Enforcement
- Pre-commit hooks prevent incomplete specs
- CI/CD validation on all pull requests
- Regular quality reports and metrics

### Manual Reviews
- Peer review of all new specs
- Architecture review for complex designs
- Quality gate reviews before implementation

### Metrics and Reporting
- Spec completion rate tracking
- Quality trend analysis
- Team adoption metrics

---

## Quick Reference

### Commands
```bash
make spec-validate          # Validate all specs
make spec-report           # Generate quality report
make spec-create NAME=...  # Create new spec
make spec-help            # Show all commands
```

### File Structure
```
.kiro/specs/my-feature/
├── requirements.md        # REQUIRED: What to build
├── design.md             # REQUIRED: How to build it
├── tasks.md              # REQUIRED: Implementation steps
├── .spec-state           # Lifecycle tracking
└── .spec-extra-files     # Approved extra files (if any)
```

### Lifecycle States
- `DRAFT` → `ACTIVE` → `COMPLETED` → `ARCHIVED`
- `DEPRECATED` (for obsolete specs)

---

*This guide is maintained by the Spec Consistency Governance system.*
*Last updated: {datetime.now().strftime("%Y-%m-%d")}*
