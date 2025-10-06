# Requirements Document: Spec Inconsistency Resolution System

## Introduction

The **Spec Inconsistency Resolution System** is a systematic approach to ensuring all specifications in `.kiro/specs/` maintain structural completeness, naming consistency, and proper lifecycle management. This system addresses the critical gap where 22 of 105 specs (21%) are incomplete and 16 specs (15%) contain non-standard files that create confusion and reduce systematic traceability.

### Current State Evidence

Analysis of `.kiro/specs/` reveals systematic structural issues:
- **23 incomplete specs** missing required files (requirements.md, design.md, tasks.md)
- **16 specs with extra files** (DAG artifacts, revisions, backups) reducing clarity
- **3 high-similarity spec pairs** indicating potential duplication
- **1 empty directory** ("output") serving no purpose
- **No lifecycle governance** leading to abandoned/incomplete specs

### Core Philosophy

**"Complete Specs Enable Complete Solutions"** - systematic specification completeness is a prerequisite for systematic development. Every spec MUST have requirements, design, and tasks to enable proper implementation and traceability.

### Target Audience

- **Spec authors** needing clear guidelines and validation
- **Framework maintainers** requiring consistency enforcement
- **Developers** seeking complete, traceable specifications
- **Quality assurance** validating systematic compliance

---

## Requirements

### Requirement 1: Structural Completeness Enforcement

**User Story:** As a spec author, I want automatic validation that ensures all specs have the three required files, so that incomplete specifications cannot exist in the repository.

#### Acceptance Criteria

1. WHEN a spec directory is created THEN the system SHALL require requirements.md, design.md, and tasks.md
2. WHEN validating existing specs THEN the system SHALL identify all specs missing any required file
3. WHEN a spec is missing files THEN the system SHALL generate a remediation report showing exactly which files are missing
4. WHEN running pre-commit hooks THEN the system SHALL prevent commits that create incomplete spec directories
5. IF a spec legitimately cannot have all files THEN it SHALL be marked with a .spec-exempt marker file with documented justification

**Priority:** CRITICAL
**Affected Specs:** 23 incomplete specs require immediate remediation

---

### Requirement 2: File Naming and Format Standardization

**User Story:** As a framework maintainer, I want standardized file naming across all specs, so that tooling can reliably locate and process specification files.

#### Acceptance Criteria

1. WHEN creating spec files THEN the system SHALL enforce lowercase kebab-case naming for directories
2. WHEN naming standard files THEN the system SHALL use exactly "requirements.md", "design.md", "tasks.md" (lowercase)
3. WHEN detecting variant names THEN the system SHALL flag "Requirements.md", "REQUIREMENTS.md", "requirement.md" as non-compliant
4. WHEN validating specs THEN the system SHALL detect and flag backup files (*.backup.md, *_fixed.md, *_backpropagated.md)
5. IF variant files exist THEN the system SHALL provide migration commands to rename to canonical names

**Priority:** HIGH
**Affected Specs:** devpost-hackathon-integration, spec-scrub-rdi-consistency

---

### Requirement 3: Extra File Governance

**User Story:** As a developer, I want clear rules about when extra files are allowed in spec directories, so that I know what belongs in specs versus external locations.

#### Acceptance Criteria

1. WHEN a spec execution creates artifacts THEN the system SHALL store LAUNCH_SUMMARY.md, PARALLEL_DAG_LAUNCH.md in `.kiro/execution-logs/{spec-name}/`
2. WHEN DAG configurations are needed THEN dag-config.yml SHALL be allowed with .spec-extra-files-approved marker
3. WHEN backup files are created THEN the system SHALL automatically move them to `.kiro/archive/{spec-name}/` with timestamps
4. WHEN validating specs THEN the system SHALL flag all files beyond the standard three unless explicitly approved
5. IF extra files are required THEN the spec SHALL include .spec-extra-files with JSON listing approved files and justifications

**Priority:** HIGH
**Affected Specs:** 16 specs with execution artifacts, backups, or specialized files

---

### Requirement 4: Duplicate and Similarity Detection

**User Story:** As an architect, I want automatic detection of similar or duplicate specs, so that I can consolidate overlapping work and maintain single sources of truth.

#### Acceptance Criteria

1. WHEN validating specs THEN the system SHALL compute name similarity scores using Levenshtein distance
2. WHEN spec names are >75% similar THEN the system SHALL generate a similarity report requiring manual review
3. WHEN specs have overlapping purposes THEN the system SHALL analyze requirements.md content similarity
4. WHEN duplicates are confirmed THEN the system SHALL provide consolidation workflows with merge commands
5. IF similar specs serve different purposes THEN maintainers SHALL document distinctions in each spec's requirements.md

**Priority:** MEDIUM
**Affected Specs:** spec-framework vs spec-mode-framework, redis-dag-registry vs unified-dag-registry, observatory-deployment-procedures vs observatory-deployment-system

---

### Requirement 5: Spec Lifecycle State Management

**User Story:** As a project manager, I want clear lifecycle states for all specs, so that I can distinguish active, completed, deprecated, and archived specifications.

#### Acceptance Criteria

1. WHEN creating a spec THEN it SHALL start in "draft" state with .spec-state file containing JSON metadata
2. WHEN a spec is being implemented THEN it SHALL be marked "active" with implementation start date
3. WHEN implementation is complete THEN it SHALL be marked "completed" with completion date and verification signature
4. WHEN a spec is superseded THEN it SHALL be marked "deprecated" with pointer to replacement spec
5. IF a spec is abandoned THEN it SHALL be moved to `.kiro/specs-archived/` with archived state and reason

**Priority:** HIGH
**Impact:** Provides visibility into 105 specs' true status

---

### Requirement 6: Empty and Orphaned Directory Cleanup

**User Story:** As a repository maintainer, I want automatic detection and removal of empty or orphaned directories, so that the spec tree remains clean and meaningful.

#### Acceptance Criteria

1. WHEN validating specs THEN the system SHALL identify directories with zero markdown files
2. WHEN empty directories are found THEN the system SHALL generate removal commands with safety confirmations
3. WHEN directories contain only hidden files THEN the system SHALL treat them as empty
4. WHEN removing directories THEN the system SHALL check git history for accidental deletions
5. IF a directory is intentionally empty THEN it SHALL contain .spec-placeholder with documented purpose

**Priority:** LOW
**Affected Specs:** output/ directory (immediate removal)

---

### Requirement 7: Automated Remediation Tooling

**User Story:** As a developer, I want automated tools to fix common spec inconsistencies, so that remediation is fast, safe, and systematic.

#### Acceptance Criteria

1. WHEN running `make spec-validate` THEN the system SHALL generate a comprehensive inconsistency report
2. WHEN running `make spec-fix-auto` THEN the system SHALL automatically fix safe issues (file naming, extra file moves)
3. WHEN running `make spec-complete-missing` THEN the system SHALL generate stub files for missing requirements/design/tasks
4. WHEN running `make spec-archive-inactive` THEN the system SHALL interactively archive specs marked deprecated/abandoned
5. IF manual intervention is needed THEN the system SHALL generate detailed remediation scripts with explanations

**Priority:** CRITICAL
**Scope:** Must handle all 23 incomplete specs, 16 specs with extra files

---

### Requirement 8: Spec Template Generation

**User Story:** As a spec author, I want automatic template generation for new specs, so that all required files are created with proper structure from the start.

#### Acceptance Criteria

1. WHEN running `make spec-create NAME=feature-name` THEN the system SHALL create directory with all three template files
2. WHEN generating templates THEN requirements.md SHALL include Introduction, Requirements sections with EARS format examples
3. WHEN generating templates THEN design.md SHALL include Architecture, Components, Integration sections
4. WHEN generating templates THEN tasks.md SHALL include task breakdown template with traceability columns
5. IF the spec name conflicts THEN the system SHALL detect duplicates and suggest alternatives

**Priority:** MEDIUM
**Impact:** Prevents future incomplete specs

---

### Requirement 9: Continuous Validation and Git Hooks

**User Story:** As a framework maintainer, I want pre-commit validation that prevents spec inconsistencies from entering the repository, so that systematic quality is maintained automatically.

#### Acceptance Criteria

1. WHEN committing changes THEN git pre-commit hooks SHALL run `spec-validate` on modified spec directories
2. WHEN validation fails THEN the commit SHALL be blocked with detailed error messages
3. WHEN creating new specs THEN the hook SHALL require all three standard files
4. WHEN modifying specs THEN the hook SHALL validate file naming and extra file governance
5. IF urgent commits are needed THEN developers SHALL use documented override procedures with justification

**Priority:** HIGH
**Integration:** Adds to existing `.pre-commit-config.yaml`

---

### Requirement 10: Traceability and Reporting

**User Story:** As a quality assurance engineer, I want comprehensive reports showing spec completeness, lifecycle states, and inconsistencies, so that I can track systematic quality over time.

#### Acceptance Criteria

1. WHEN running `make spec-report` THEN the system SHALL generate markdown report with all inconsistencies
2. WHEN generating reports THEN the system SHALL include metrics: completion rate, avg files per spec, lifecycle distribution
3. WHEN tracking over time THEN the system SHALL store reports in `.kiro/reports/spec-quality-YYYYMMDD.md`
4. WHEN comparing reports THEN the system SHALL show trend lines for completion rates and inconsistencies
5. IF quality degrades THEN the system SHALL generate alerts for CI/CD pipeline integration

**Priority:** MEDIUM
**Format:** Markdown reports suitable for documentation and dashboards

---

### Requirement 11: Migration and Consolidation Workflows

**User Story:** As a maintainer resolving duplicates, I want guided workflows to merge similar specs, so that consolidation is systematic and preserves all valuable information.

#### Acceptance Criteria

1. WHEN consolidating specs THEN the system SHALL provide merge workflows that combine requirements from both specs
2. WHEN merging design documents THEN the system SHALL create unified design with architecture from both sources
3. WHEN combining tasks THEN the system SHALL deduplicate and merge task lists with proper traceability
4. WHEN consolidation is complete THEN the superseded spec SHALL be marked deprecated with pointer to consolidated version
5. IF conflicts arise THEN the system SHALL generate side-by-side diffs for manual resolution

**Priority:** MEDIUM
**Scope:** Initially target 3 high-similarity pairs

---

### Requirement 12: Documentation and Training

**User Story:** As a new contributor, I want comprehensive documentation about spec standards and tooling, so that I can create compliant specifications from the start.

#### Acceptance Criteria

1. WHEN onboarding THEN developers SHALL have access to `.kiro/docs/spec-standards.md` with complete guidelines
2. WHEN learning workflows THEN the documentation SHALL include examples of compliant and non-compliant specs
3. WHEN using tools THEN each command SHALL have `--help` output with examples and common use cases
4. WHEN making mistakes THEN error messages SHALL include links to documentation sections
5. IF standards evolve THEN documentation SHALL be updated synchronously with tooling changes

**Priority:** MEDIUM
**Deliverable:** Comprehensive spec authoring guide

---

## Implementation Priorities

### Phase 1: Critical Infrastructure (Week 1)
- Requirement 7: Automated remediation tooling
- Requirement 1: Structural completeness enforcement
- Requirement 6: Empty directory cleanup (immediate: remove output/)

### Phase 2: Governance and Prevention (Week 2)
- Requirement 5: Lifecycle state management
- Requirement 3: Extra file governance
- Requirement 9: Git hooks and continuous validation

### Phase 3: Quality and Automation (Week 3)
- Requirement 8: Template generation
- Requirement 10: Traceability and reporting
- Requirement 2: File naming standardization

### Phase 4: Advanced Features (Week 4)
- Requirement 4: Duplicate detection
- Requirement 11: Migration workflows
- Requirement 12: Documentation and training

---

## Success Metrics

- **Spec Completeness:** 100% of active specs have all three required files (currently 78%)
- **Extra File Compliance:** 0 unapproved extra files in spec directories (currently 16 specs affected)
- **Lifecycle Visibility:** 100% of specs have documented lifecycle states (currently 0%)
- **Duplicate Reduction:** <5% spec name similarity scores >75% (currently 3 pairs at 77-85%)
- **Validation Coverage:** 100% of spec changes validated pre-commit (currently 0%)
