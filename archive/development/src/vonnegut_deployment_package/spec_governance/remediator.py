"""
Spec Remediator - Automated remediation for spec consistency issues.

Provides functionality to fix incomplete specs, move extra files, and apply
systematic corrections to maintain spec governance.
"""

from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime
import json
import shutil

from .validator import SpecValidator, ValidationResult


@dataclass
class RemediationAction:
    """Represents a remediation action to be taken."""
    action_type: str  # 'create_file', 'move_file', 'rename_file', 'remove_file'
    source_path: Optional[str] = None
    target_path: Optional[str] = None
    description: str = ""
    backup_path: Optional[str] = None


@dataclass
class RemediationResult:
    """Result of remediation operation."""
    spec_name: str
    actions_taken: List[RemediationAction]
    success: bool
    error_message: Optional[str] = None
    backup_created: bool = False


class SpecRemediator:
    """Automated remediation for spec consistency issues."""
    
    def __init__(self, specs_dir: Path = None, validator: SpecValidator = None):
        self.specs_dir = specs_dir or Path(".kiro/specs")
        self.validator = validator or SpecValidator(self.specs_dir)
        
        # Create backup and archive directories
        self.archive_dir = Path(".kiro/archive")
        self.execution_logs_dir = Path(".kiro/execution-logs")
        self.archive_dir.mkdir(parents=True, exist_ok=True)
        self.execution_logs_dir.mkdir(parents=True, exist_ok=True)
    
    def create_missing_files(self, spec_name: str, dry_run: bool = False) -> RemediationResult:
        """Create missing required files for a spec."""
        validation_result = self.validator.validate_spec(spec_name)
        
        if validation_result.is_complete:
            return RemediationResult(
                spec_name=spec_name,
                actions_taken=[],
                success=True,
                error_message="Spec is already complete"
            )
        
        spec_path = self.specs_dir / spec_name
        actions = []
        
        # Find missing files
        missing_files = []
        for issue in validation_result.issues:
            if issue.issue_type == "missing_file":
                filename = issue.description.split(": ")[1]
                missing_files.append(filename)
        
        # Create actions for missing files
        for filename in missing_files:
            target_path = spec_path / filename
            actions.append(RemediationAction(
                action_type="create_file",
                target_path=str(target_path),
                description=f"Create missing {filename} with template content"
            ))
        
        if dry_run:
            return RemediationResult(
                spec_name=spec_name,
                actions_taken=actions,
                success=True
            )
        
        # Execute actions
        try:
            for action in actions:
                if action.action_type == "create_file":
                    self._create_template_file(Path(action.target_path))
            
            return RemediationResult(
                spec_name=spec_name,
                actions_taken=actions,
                success=True
            )
        
        except Exception as e:
            return RemediationResult(
                spec_name=spec_name,
                actions_taken=[],
                success=False,
                error_message=str(e)
            )
    
    def move_extra_files(self, spec_name: str, dry_run: bool = False) -> RemediationResult:
        """Move extra files to appropriate locations."""
        validation_result = self.validator.validate_spec(spec_name)
        
        if not validation_result.extra_files:
            return RemediationResult(
                spec_name=spec_name,
                actions_taken=[],
                success=True,
                error_message="No extra files to move"
            )
        
        spec_path = self.specs_dir / spec_name
        actions = []
        
        # Categorize extra files and create move actions
        for extra_file in validation_result.extra_files:
            source_path = spec_path / extra_file
            
            if any(pattern in extra_file.lower() for pattern in 
                   ['backup', '_fixed', '_backpropagated']):
                # Move to archive
                target_dir = self.archive_dir / spec_name
                target_path = target_dir / extra_file
                actions.append(RemediationAction(
                    action_type="move_file",
                    source_path=str(source_path),
                    target_path=str(target_path),
                    description=f"Move backup file {extra_file} to archive"
                ))
            
            elif any(pattern in extra_file.lower() for pattern in 
                     ['launch_summary', 'parallel_dag', 'execution']):
                # Move to execution logs
                target_dir = self.execution_logs_dir / spec_name
                target_path = target_dir / extra_file
                actions.append(RemediationAction(
                    action_type="move_file",
                    source_path=str(source_path),
                    target_path=str(target_path),
                    description=f"Move execution artifact {extra_file} to execution logs"
                ))
        
        if dry_run:
            return RemediationResult(
                spec_name=spec_name,
                actions_taken=actions,
                success=True
            )
        
        # Execute actions
        try:
            for action in actions:
                if action.action_type == "move_file":
                    source = Path(action.source_path)
                    target = Path(action.target_path)
                    target.parent.mkdir(parents=True, exist_ok=True)
                    shutil.move(str(source), str(target))
            
            return RemediationResult(
                spec_name=spec_name,
                actions_taken=actions,
                success=True
            )
        
        except Exception as e:
            return RemediationResult(
                spec_name=spec_name,
                actions_taken=[],
                success=False,
                error_message=str(e)
            )
    
    def _create_template_file(self, file_path: Path):
        """Create a template file with appropriate content."""
        filename = file_path.name
        spec_name = file_path.parent.name
        
        if filename == "requirements.md":
            content = f"""# Requirements Document: {spec_name.replace('-', ' ').title()}

## Introduction

This specification defines the requirements for {spec_name.replace('-', ' ')}.

### Current State Evidence

[Document the current state and evidence that led to this specification]

### Target Audience

- [Define who will use this system]
- [Define who will maintain this system]

---

## Requirements

### Requirement 1: [Primary Requirement]

**User Story:** As a [user type], I want [functionality], so that [benefit].

#### Acceptance Criteria

1. WHEN [condition] THEN the system SHALL [behavior]
2. WHEN [condition] THEN the system SHALL [behavior]
3. WHEN [condition] THEN the system SHALL [behavior]

**Priority:** CRITICAL/HIGH/MEDIUM/LOW

---

### Requirement 2: [Secondary Requirement]

**User Story:** As a [user type], I want [functionality], so that [benefit].

#### Acceptance Criteria

1. WHEN [condition] THEN the system SHALL [behavior]
2. WHEN [condition] THEN the system SHALL [behavior]

**Priority:** CRITICAL/HIGH/MEDIUM/LOW

---

## Success Metrics

- [Define measurable success criteria]
- [Define performance targets]
- [Define quality gates]

## Implementation Priorities

### Phase 1: [Priority Description]
- [List high-priority requirements]

### Phase 2: [Priority Description]  
- [List medium-priority requirements]

---

## Risk Mitigation

- [Identify technical risks and mitigation strategies]
- [Identify operational risks and mitigation strategies]
- [Identify business risks and mitigation strategies]
"""

        elif filename == "design.md":
            content = f"""# Design Document: {spec_name.replace('-', ' ').title()}

## Overview

This design document provides the systematic architecture for {spec_name.replace('-', ' ')}.

## Architecture

### Core Components

#### 1. [Primary Component]
```python
class [ComponentName]:
    \"\"\"[Component description and purpose].\"\"\"
    
    def __init__(self):
        # Component initialization
        pass
    
    def [primary_method](self) -> [ReturnType]:
        \"\"\"[Method description].\"\"\"
        pass
```

#### 2. [Secondary Component]
```python
class [SecondaryComponent]:
    \"\"\"[Component description and purpose].\"\"\"
    
    def __init__(self):
        # Component initialization
        pass
```

### Component Interactions

[Describe how components interact with each other]

## Data Models

### [Primary Data Model]
```python
@dataclass
class [ModelName]:
    \"\"\"[Model description].\"\"\"
    
    field1: str
    field2: int
    field3: Optional[str] = None
```

## Integration Points

### [External System Integration]
- **Interface:** [Description of interface]
- **Protocol:** [Communication protocol]
- **Error Handling:** [How errors are handled]

## Error Handling

### [Error Category]
- **Detection:** [How errors are detected]
- **Recovery:** [How system recovers]
- **Logging:** [What is logged]

## Testing Strategy

### Unit Tests
- [Component testing approach]

### Integration Tests
- [Integration testing approach]

### End-to-End Tests
- [E2E testing approach]

## Security Considerations

- [Security requirements and implementations]
- [Authentication and authorization]
- [Data protection measures]

## Performance Considerations

- [Performance requirements]
- [Optimization strategies]
- [Scalability considerations]

## Deployment Considerations

### Rollout Strategy
- [Deployment approach]
- [Rollback procedures]

### Monitoring Integration
- [Monitoring and observability]
- [Alerting strategies]
"""

        elif filename == "tasks.md":
            content = f"""# Tasks: {spec_name.replace('-', ' ').title()}

## Task Breakdown

This document provides a systematic task breakdown for implementing {spec_name.replace('-', ' ')}.

---

## Phase 1: [Phase Name] (Week 1)

### Task 1.1: [Task Name]
**Requirement:** REQ-1 ([Requirement Description])
**Estimated Effort:** [X hours]

**Steps:**
1. [Detailed step 1]
2. [Detailed step 2]
3. [Detailed step 3]

**Acceptance:**
- [Acceptance criteria 1]
- [Acceptance criteria 2]

---

### Task 1.2: [Task Name]
**Requirement:** REQ-2 ([Requirement Description])
**Estimated Effort:** [X hours]

**Steps:**
1. [Detailed step 1]
2. [Detailed step 2]

**Acceptance:**
- [Acceptance criteria 1]
- [Acceptance criteria 2]

---

## Phase 2: [Phase Name] (Week 2)

### Task 2.1: [Task Name]
**Requirement:** REQ-3 ([Requirement Description])
**Estimated Effort:** [X hours]

**Steps:**
1. [Detailed step 1]
2. [Detailed step 2]

**Acceptance:**
- [Acceptance criteria 1]
- [Acceptance criteria 2]

---

## Testing Tasks

### Task T.1: Unit Test Coverage
**Estimated Effort:** [X hours]

**Coverage Targets:**
- [Component 1]: >90%
- [Component 2]: >90%

---

### Task T.2: Integration Testing
**Estimated Effort:** [X hours]

**Test Scenarios:**
1. [Integration scenario 1]
2. [Integration scenario 2]

---

## Success Criteria

### Completion Definition
All tasks marked complete when:
- Code implemented and reviewed
- Unit tests pass with coverage targets
- Integration tests pass
- Documentation complete

### System-Level Success Metrics
- [Metric 1]: [Target value]
- [Metric 2]: [Target value]

---

## Risk Mitigation

**Risk:** [Risk description]
**Mitigation:** [Mitigation strategy]

**Risk:** [Risk description]
**Mitigation:** [Mitigation strategy]

---

## Estimated Total Effort

- **Phase 1:** [X hours]
- **Phase 2:** [X hours]
- **Testing:** [X hours]

**Total:** ~[X hours] (~[X weeks] at [full/part] time)
"""

        else:
            content = f"# {filename}\n\n[Template content for {spec_name}]\n"
        
        # Create the file
        file_path.parent.mkdir(parents=True, exist_ok=True)
        with open(file_path, 'w') as f:
            f.write(content)