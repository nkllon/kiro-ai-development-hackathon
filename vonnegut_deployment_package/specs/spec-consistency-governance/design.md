# Design Document: Spec Inconsistency Resolution System

## Architecture Overview

The Spec Inconsistency Resolution System is designed as a systematic validation and remediation framework integrated into the Beast Mode ecosystem. It provides automated detection, reporting, and fixing of spec structure issues through CLI tools, git hooks, and continuous monitoring.

### System Context

```
┌─────────────────────────────────────────────────────────────┐
│                    Beast Mode Framework                      │
│  ┌─────────────────────────────────────────────────────────┐│
│  │      Spec Consistency Governance System                 ││
│  │                                                          ││
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐ ││
│  │  │   Validator  │  │  Remediator  │  │   Reporter   │ ││
│  │  └──────────────┘  └──────────────┘  └──────────────┘ ││
│  │         │                  │                  │         ││
│  │         └──────────────────┴──────────────────┘         ││
│  │                           │                              ││
│  │                    ┌──────────────┐                     ││
│  │                    │ Spec Registry│                     ││
│  │                    └──────────────┘                     ││
│  └─────────────────────────────────────────────────────────┘│
│                              │                               │
│                              │                               │
│           ┌──────────────────┼──────────────────┐           │
│           │                  │                  │           │
│  ┌────────▼──────┐  ┌────────▼──────┐  ┌───────▼───────┐  │
│  │  Git Hooks    │  │  CLI Tools    │  │  Make Targets │  │
│  └───────────────┘  └───────────────┘  └───────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

---

## Component Design

### 1. Spec Validator (`src/spec_governance/validator.py`)

**Purpose:** Scans `.kiro/specs/` to detect structural inconsistencies.

**Responsibilities:**
- Scan all spec directories for required files (requirements.md, design.md, tasks.md)
- Detect extra/non-standard files
- Calculate name similarity scores for duplicate detection
- Identify empty or orphaned directories
- Validate lifecycle state metadata

**Key Methods:**
```python
class SpecValidator(ReflectiveModule):
    def validate_all_specs(self) -> ValidationReport
    def validate_spec(self, spec_path: Path) -> SpecValidation
    def check_required_files(self, spec_path: Path) -> FileCompleteness
    def detect_extra_files(self, spec_path: Path) -> List[ExtraFile]
    def compute_similarity(self, spec1: str, spec2: str) -> float
    def find_duplicates(self, threshold: float = 0.75) -> List[SpecPair]
```

**Output:** `ValidationReport` object with structured findings

---

### 2. Spec Remediator (`src/spec_governance/remediator.py`)

**Purpose:** Automatically fix safe inconsistencies and generate remediation scripts.

**Responsibilities:**
- Create missing stub files for incomplete specs
- Move extra files to appropriate locations (.kiro/execution-logs/, .kiro/archive/)
- Rename files to canonical names
- Remove empty directories
- Generate interactive consolidation workflows

**Key Methods:**
```python
class SpecRemediator(ReflectiveModule):
    def create_missing_files(self, spec_path: Path, dry_run: bool = True) -> RemediationResult
    def move_extra_files(self, spec_path: Path, dry_run: bool = True) -> RemediationResult
    def fix_file_naming(self, spec_path: Path, dry_run: bool = True) -> RemediationResult
    def remove_empty_dirs(self, dry_run: bool = True) -> RemediationResult
    def generate_consolidation_script(self, spec1: Path, spec2: Path) -> str
```

**Safety:** All operations support `dry_run` mode; generates preview before execution

---

### 3. Spec Reporter (`src/spec_governance/reporter.py`)

**Purpose:** Generate comprehensive reports on spec quality and inconsistencies.

**Responsibilities:**
- Generate markdown reports with metrics and findings
- Track quality trends over time
- Create visualization-friendly data exports
- Integrate with CI/CD for quality gates

**Key Methods:**
```python
class SpecReporter(ReflectiveModule):
    def generate_report(self, validation: ValidationReport) -> str
    def compute_metrics(self, validation: ValidationReport) -> SpecMetrics
    def compare_historical(self, current: ValidationReport, previous: ValidationReport) -> TrendAnalysis
    def export_for_dashboard(self, validation: ValidationReport) -> Dict[str, Any]
```

**Output Formats:** Markdown, JSON, CSV for different consumers

---

### 4. Spec Registry (`src/spec_governance/registry.py`)

**Purpose:** Maintain centralized index of all specs with metadata.

**Responsibilities:**
- Cache spec structure for fast lookups
- Track lifecycle states (draft, active, completed, deprecated, archived)
- Store similarity scores and relationships
- Provide query interface for tooling

**Data Model:**
```python
@dataclass
class SpecMetadata:
    name: str
    path: Path
    lifecycle_state: LifecycleState
    has_requirements: bool
    has_design: bool
    has_tasks: bool
    extra_files: List[str]
    created_date: datetime
    last_modified: datetime
    similar_specs: List[Tuple[str, float]]  # (spec_name, similarity_score)
```

**Storage:** JSON file at `.kiro/spec-registry.json` with auto-regeneration

---

### 5. Spec Template Generator (`src/spec_governance/template_generator.py`)

**Purpose:** Create new specs with proper structure from the start.

**Responsibilities:**
- Generate requirements.md with EARS format examples
- Generate design.md with architecture sections
- Generate tasks.md with traceability columns
- Check for name conflicts before creation
- Initialize lifecycle state

**Key Methods:**
```python
class SpecTemplateGenerator(ReflectiveModule):
    def create_spec(self, name: str, description: str) -> Path
    def generate_requirements_template(self, spec_name: str, description: str) -> str
    def generate_design_template(self, spec_name: str) -> str
    def generate_tasks_template(self, spec_name: str) -> str
    def check_name_conflict(self, name: str) -> Optional[List[str]]
```

---

## Integration Points

### Git Hooks Integration

**Pre-commit Hook:** `.git/hooks/pre-commit`
- Runs `spec-validate` on modified spec directories
- Blocks commits if validation fails
- Provides clear error messages with remediation guidance

**Implementation:**
```python
# scripts/git_hooks/pre_commit_spec_validate.py
def validate_modified_specs():
    modified_files = get_git_modified_files()
    specs_to_check = extract_spec_dirs(modified_files)
    validator = SpecValidator()

    for spec in specs_to_check:
        result = validator.validate_spec(spec)
        if not result.is_valid:
            print_error_message(result)
            sys.exit(1)
```

---

### Makefile Integration

New targets in `makefiles/spec-governance.mk`:

```makefile
.PHONY: spec-validate spec-fix-auto spec-complete-missing spec-report spec-create

spec-validate:
	@python -m spec_governance.cli validate --all

spec-fix-auto:
	@python -m spec_governance.cli remediate --auto --confirm

spec-complete-missing:
	@python -m spec_governance.cli remediate --create-stubs

spec-report:
	@python -m spec_governance.cli report --format markdown --output .kiro/reports/

spec-create:
	@python -m spec_governance.cli create --name $(NAME) --description "$(DESC)"
```

---

### CLI Design

**Command Structure:**
```
spec-governance
├── validate
│   ├── --all                 # Validate all specs
│   ├── --spec NAME           # Validate specific spec
│   └── --ci                  # CI-friendly output
├── remediate
│   ├── --auto                # Fix safe issues automatically
│   ├── --create-stubs        # Create missing files
│   ├── --move-extras         # Move extra files
│   └── --dry-run             # Preview changes
├── report
│   ├── --format (md|json)    # Output format
│   ├── --output DIR          # Output directory
│   └── --compare PREVIOUS    # Compare with previous report
├── create
│   ├── --name NAME           # Spec name
│   └── --description DESC    # Brief description
└── consolidate
    ├── --spec1 NAME          # First spec
    ├── --spec2 NAME          # Second spec
    └── --interactive         # Interactive merge workflow
```

---

## Data Flow

### Validation Flow
```
1. User runs: make spec-validate
2. CLI loads SpecValidator
3. Validator scans .kiro/specs/
4. For each spec directory:
   - Check required files
   - Detect extra files
   - Validate naming
   - Check lifecycle metadata
5. Reporter generates markdown report
6. Report saved to .kiro/reports/spec-quality-{date}.md
7. Exit code indicates pass/fail for CI integration
```

### Remediation Flow
```
1. User runs: make spec-fix-auto
2. CLI loads SpecRemediator
3. Remediator loads validation report
4. For each fixable issue:
   - Preview change
   - Request confirmation (unless --confirm flag)
   - Execute fix
   - Log action
5. Generate summary report of changes
6. Update spec registry
```

---

## File Organization

```
src/spec_governance/
├── __init__.py
├── validator.py              # Validation logic
├── remediator.py            # Remediation logic
├── reporter.py              # Report generation
├── registry.py              # Spec registry management
├── template_generator.py    # New spec templates
├── similarity.py            # Duplicate detection algorithms
└── cli.py                   # CLI interface

scripts/git_hooks/
├── pre_commit_spec_validate.py
└── install_hooks.py

makefiles/
└── spec-governance.mk       # Make targets

.kiro/
├── spec-registry.json       # Cached spec metadata
├── reports/                 # Quality reports
│   └── spec-quality-YYYYMMDD.md
├── execution-logs/          # Execution artifacts moved here
│   └── {spec-name}/
└── archive/                 # Archived files
    └── {spec-name}/
```

---

## Error Handling

### Validation Errors
- **Missing files:** Generate stub creation commands
- **Extra files:** Provide move/archive commands
- **Naming issues:** Generate rename commands
- **Empty dirs:** Generate safe removal commands

### Remediation Errors
- **File conflicts:** Interactive resolution prompts
- **Permission issues:** Clear error messages with sudo guidance
- **Git conflicts:** Abort with rollback instructions

### Rollback Strategy
All remediation operations:
1. Create backup in `.kiro/archive/remediation-backup-{timestamp}/`
2. Log all changes to `.kiro/remediation-log.json`
3. Provide rollback script: `scripts/rollback_spec_remediation.py --timestamp YYYYMMDDHHMMSS`

---

## Performance Considerations

- **Caching:** Spec registry cached in memory, regenerated only when `.kiro/specs/` modified
- **Incremental validation:** Git hooks only validate changed specs, not all 105
- **Parallel processing:** Validation can process specs in parallel using multiprocessing
- **Lazy loading:** Only load full spec content when needed (e.g., similarity analysis)

**Target Performance:**
- Full validation: <5 seconds for 105 specs
- Incremental validation: <1 second for single spec
- Registry rebuild: <2 seconds

---

## Security Considerations

- **Path traversal:** All file operations validate paths are within `.kiro/specs/`
- **Command injection:** No shell execution; use subprocess with argument lists
- **Arbitrary file writes:** Remediation operations limited to approved directories
- **Git hook bypass:** Document override procedures requiring justification

---

## Testing Strategy

### Unit Tests
- `tests/unit/spec_governance/test_validator.py` - Validation logic
- `tests/unit/spec_governance/test_remediator.py` - Remediation logic
- `tests/unit/spec_governance/test_similarity.py` - Duplicate detection

### Integration Tests
- `tests/integration/spec_governance/test_full_workflow.py` - End-to-end validation and remediation
- `tests/integration/spec_governance/test_git_hooks.py` - Pre-commit hook testing

### Test Fixtures
- `tests/fixtures/specs/` - Sample spec directories (complete, incomplete, with-extras)

---

## Monitoring and Observability

Implements ReflectiveModule for systematic observability:

**Metrics:**
- `spec_governance.validation.duration` - Time to validate all specs
- `spec_governance.validation.failures` - Count of validation failures
- `spec_governance.remediation.operations` - Count of auto-fix operations
- `spec_governance.specs.total` - Total spec count
- `spec_governance.specs.complete` - Complete spec count (%)

**Logging:**
- Structured logs with spec name, operation, result
- Integration with Beast Mode logging framework

---

## Migration Plan

### Phase 1: Foundation (Days 1-3)
- Implement Validator, Reporter, Registry
- Create CLI with validate and report commands
- Generate initial report on current state

### Phase 2: Remediation (Days 4-6)
- Implement Remediator
- Add auto-fix capabilities
- Test on subset of specs

### Phase 3: Prevention (Days 7-9)
- Implement Template Generator
- Add git hooks
- Update Makefile

### Phase 4: Advanced (Days 10-14)
- Implement similarity detection
- Add consolidation workflows
- Write documentation

---

## Future Enhancements

- **AI-assisted consolidation:** Use LLM to suggest requirement merges
- **Visual spec browser:** Web UI for exploring spec relationships
- **Automated archival:** Auto-archive specs with no git activity in 90 days
- **Spec dependency graph:** Visualize inter-spec dependencies
- **Quality scoring:** Numeric quality scores based on completeness, freshness, usage
