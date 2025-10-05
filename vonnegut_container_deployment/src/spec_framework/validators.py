"""
Document validation components for the Spec Framework.

This module provides document structure validation, EARS format checking,
workflow compliance validation, and remediation guidance generation.
"""

import os
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any, Set
from dataclasses import dataclass

from .models import (
    SpecificationDocument,
    ValidationResult,
    ValidationError,
    ValidationWarning,
    RemediationGuide,
    DocumentTemplate,
    WorkflowStage,
    ApprovalStatus,
)


@dataclass
class ValidationCache:
    """Cache for validation results with timestamp tracking."""
    spec_id: str
    result: ValidationResult
    timestamp: datetime
    file_hash: str
    
    def is_expired(self, ttl_seconds: int = 300) -> bool:
        """Check if cache entry is expired (default 5 minutes)."""
        return (datetime.now() - self.timestamp).total_seconds() > ttl_seconds


class DocumentValidator:
    """Enhanced document validator with remediation guidance and caching."""
    
    def __init__(self, cache_ttl_seconds: int = 300):
        """Initialize validator with caching configuration."""
        self.cache_ttl_seconds = cache_ttl_seconds
        self._validation_cache: Dict[str, ValidationCache] = {}
        
        # EARS format patterns
        self.ears_patterns = {
            "when_then": re.compile(r"WHEN\s+.+\s+THEN\s+.+\s+SHALL\s+.+", re.IGNORECASE),
            "if_then": re.compile(r"IF\s+.+\s+THEN\s+.+\s+SHALL\s+.+", re.IGNORECASE),
            "while_then": re.compile(r"WHILE\s+.+\s+THEN\s+.+\s+SHALL\s+.+", re.IGNORECASE),
        }
        
        # Required sections for each workflow stage
        self.required_sections = {
            WorkflowStage.REQUIREMENTS: ["Introduction", "Requirements"],
            WorkflowStage.DESIGN: ["Introduction", "Requirements", "Overview", "Architecture", "Components"],
            WorkflowStage.TASKS: ["Introduction", "Requirements", "Overview", "Architecture", "Components", "Implementation Plan"],
            WorkflowStage.COMPLETE: ["Introduction", "Requirements", "Overview", "Architecture", "Components", "Implementation Plan"]
        }
    
    def validate_structure(self, spec_doc: SpecificationDocument) -> ValidationResult:
        """Validate specification document structure with caching."""
        # Check cache first
        cached_result = self._get_cached_validation(spec_doc, "structure")
        if cached_result:
            return cached_result
        
        errors = []
        warnings = []
        
        # Validate file existence
        if not os.path.exists(spec_doc.requirements_path):
            errors.append(ValidationError(
                error_type="missing_file",
                message=f"Requirements file not found: {spec_doc.requirements_path}",
                location=spec_doc.requirements_path,
                severity="error"
            ))
        else:
            # Validate requirements file structure
            req_errors, req_warnings = self._validate_requirements_structure(spec_doc.requirements_path)
            errors.extend(req_errors)
            warnings.extend(req_warnings)
        
        # Validate design file if in design stage or later
        if spec_doc.workflow_stage in [WorkflowStage.DESIGN, WorkflowStage.TASKS, WorkflowStage.COMPLETE]:
            if not spec_doc.design_path:
                errors.append(ValidationError(
                    error_type="workflow_violation",
                    message="Design stage requires design_path to be set",
                    location="design_path",
                    severity="error"
                ))
            elif not os.path.exists(spec_doc.design_path):
                errors.append(ValidationError(
                    error_type="missing_file",
                    message=f"Design file not found: {spec_doc.design_path}",
                    location=spec_doc.design_path,
                    severity="error"
                ))
            else:
                design_errors, design_warnings = self._validate_design_structure(spec_doc.design_path)
                errors.extend(design_errors)
                warnings.extend(design_warnings)
        
        # Validate tasks file if in tasks stage or later
        if spec_doc.workflow_stage in [WorkflowStage.TASKS, WorkflowStage.COMPLETE]:
            if not spec_doc.tasks_path:
                errors.append(ValidationError(
                    error_type="workflow_violation",
                    message="Tasks stage requires tasks_path to be set",
                    location="tasks_path",
                    severity="error"
                ))
            elif not os.path.exists(spec_doc.tasks_path):
                errors.append(ValidationError(
                    error_type="missing_file",
                    message=f"Tasks file not found: {spec_doc.tasks_path}",
                    location=spec_doc.tasks_path,
                    severity="error"
                ))
            else:
                tasks_errors, tasks_warnings = self._validate_tasks_structure(spec_doc.tasks_path)
                errors.extend(tasks_errors)
                warnings.extend(tasks_warnings)
        
        result = ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
            validation_timestamp=datetime.now()
        )
        
        # Cache result
        self._cache_validation_result(spec_doc, "structure", result)
        
        return result
    
    def validate_ears_format(self, requirements_file: str) -> ValidationResult:
        """Validate EARS format compliance in requirements."""
        errors = []
        warnings = []
        
        if not os.path.exists(requirements_file):
            errors.append(ValidationError(
                error_type="missing_file",
                message=f"Requirements file not found: {requirements_file}",
                location=requirements_file
            ))
            return ValidationResult(is_valid=False, errors=errors)
        
        try:
            with open(requirements_file, 'r') as f:
                content = f.read()
            
            # Find acceptance criteria sections
            acceptance_sections = re.findall(
                r'#### Acceptance Criteria\s*\n(.*?)(?=###|\Z)',
                content,
                re.DOTALL | re.IGNORECASE
            )
            
            for i, section in enumerate(acceptance_sections):
                section_errors, section_warnings = self._validate_ears_section(section, i + 1)
                errors.extend(section_errors)
                warnings.extend(section_warnings)
            
            if not acceptance_sections:
                warnings.append(ValidationWarning(
                    warning_type="missing_ears",
                    message="No 'Acceptance Criteria' sections found",
                    location=requirements_file
                ))
        
        except Exception as e:
            errors.append(ValidationError(
                error_type="file_read_error",
                message=f"Failed to read requirements file: {e}",
                location=requirements_file
            ))
        
        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
            validation_timestamp=datetime.now()
        )
    
    def validate_completeness(self, spec_doc: SpecificationDocument) -> ValidationResult:
        """Validate document completeness for current workflow stage."""
        errors = []
        warnings = []
        
        required_sections = self.required_sections.get(spec_doc.workflow_stage, [])
        
        # Check requirements file sections
        if os.path.exists(spec_doc.requirements_path):
            req_sections = self._extract_sections(spec_doc.requirements_path)
            missing_req_sections = set(["Introduction", "Requirements"]) - req_sections
            
            for section in missing_req_sections:
                errors.append(ValidationError(
                    error_type="missing_section",
                    message=f"Missing required section: {section}",
                    location=spec_doc.requirements_path
                ))
        
        # Check design file sections if applicable
        if spec_doc.design_path and os.path.exists(spec_doc.design_path):
            design_sections = self._extract_sections(spec_doc.design_path)
            required_design_sections = set(["Overview", "Architecture", "Components"]) & set(required_sections)
            missing_design_sections = required_design_sections - design_sections
            
            for section in missing_design_sections:
                errors.append(ValidationError(
                    error_type="missing_section",
                    message=f"Missing required design section: {section}",
                    location=spec_doc.design_path
                ))
        
        # Check tasks file sections if applicable
        if spec_doc.tasks_path and os.path.exists(spec_doc.tasks_path):
            tasks_sections = self._extract_sections(spec_doc.tasks_path)
            if "Implementation Plan" in required_sections and "Implementation Plan" not in tasks_sections:
                errors.append(ValidationError(
                    error_type="missing_section",
                    message="Missing required section: Implementation Plan",
                    location=spec_doc.tasks_path
                ))
        
        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
            validation_timestamp=datetime.now()
        )
    
    def validate_workflow_compliance(self, spec_doc: SpecificationDocument) -> ValidationResult:
        """Validate workflow stage compliance and progression rules."""
        errors = []
        warnings = []
        
        # Check workflow progression rules
        if spec_doc.workflow_stage == WorkflowStage.DESIGN:
            if not spec_doc.design_path:
                errors.append(ValidationError(
                    error_type="workflow_violation",
                    message="Design stage requires design document",
                    location="workflow_stage"
                ))
        
        elif spec_doc.workflow_stage == WorkflowStage.TASKS:
            if not spec_doc.design_path:
                errors.append(ValidationError(
                    error_type="workflow_violation",
                    message="Tasks stage requires design document to be completed first",
                    location="workflow_stage"
                ))
            if not spec_doc.tasks_path:
                errors.append(ValidationError(
                    error_type="workflow_violation",
                    message="Tasks stage requires tasks document",
                    location="workflow_stage"
                ))
        
        elif spec_doc.workflow_stage == WorkflowStage.COMPLETE:
            if not all([spec_doc.design_path, spec_doc.tasks_path]):
                errors.append(ValidationError(
                    error_type="workflow_violation",
                    message="Complete stage requires all documents (requirements, design, tasks)",
                    location="workflow_stage"
                ))
        
        # Check approval status consistency
        if spec_doc.approval_status == ApprovalStatus.APPROVED:
            if spec_doc.workflow_stage == WorkflowStage.REQUIREMENTS:
                warnings.append(ValidationWarning(
                    warning_type="approval_inconsistency",
                    message="Approved status unusual for Requirements stage",
                    location="approval_status"
                ))
        
        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
            validation_timestamp=datetime.now()
        )
    
    def generate_validation_report(self, spec_doc: SpecificationDocument) -> str:
        """Generate comprehensive validation report."""
        structure_result = self.validate_structure(spec_doc)
        ears_result = self.validate_ears_format(spec_doc.requirements_path)
        completeness_result = self.validate_completeness(spec_doc)
        workflow_result = self.validate_workflow_compliance(spec_doc)
        
        report = []
        report.append(f"Validation Report for {spec_doc.name}")
        report.append("=" * 50)
        report.append(f"Specification ID: {spec_doc.id}")
        report.append(f"Version: {spec_doc.version}")
        report.append(f"Workflow Stage: {spec_doc.workflow_stage.value}")
        report.append(f"Approval Status: {spec_doc.approval_status.value}")
        report.append(f"Report Generated: {datetime.now().isoformat()}")
        report.append("")
        
        # Structure validation
        report.append("Structure Validation:")
        report.append(f"  Status: {'PASS' if structure_result.is_valid else 'FAIL'}")
        if structure_result.errors:
            report.append(f"  Errors: {len(structure_result.errors)}")
            for error in structure_result.errors:
                report.append(f"    - {error.message}")
        
        # EARS format validation
        report.append("\nEARS Format Validation:")
        report.append(f"  Status: {'PASS' if ears_result.is_valid else 'FAIL'}")
        if ears_result.errors:
            report.append(f"  Errors: {len(ears_result.errors)}")
            for error in ears_result.errors:
                report.append(f"    - {error.message}")
        
        # Completeness validation
        report.append("\nCompleteness Validation:")
        report.append(f"  Status: {'PASS' if completeness_result.is_valid else 'FAIL'}")
        if completeness_result.errors:
            report.append(f"  Errors: {len(completeness_result.errors)}")
            for error in completeness_result.errors:
                report.append(f"    - {error.message}")
        
        # Workflow validation
        report.append("\nWorkflow Validation:")
        report.append(f"  Status: {'PASS' if workflow_result.is_valid else 'FAIL'}")
        if workflow_result.errors:
            report.append(f"  Errors: {len(workflow_result.errors)}")
            for error in workflow_result.errors:
                report.append(f"    - {error.message}")
        
        # Overall status
        overall_valid = all([
            structure_result.is_valid,
            ears_result.is_valid,
            completeness_result.is_valid,
            workflow_result.is_valid
        ])
        
        report.append(f"\nOverall Status: {'PASS' if overall_valid else 'FAIL'}")
        
        return "\n".join(report)
    
    def generate_remediation_guidance(self, validation_result: ValidationResult) -> RemediationGuide:
        """Generate specific remediation guidance for validation failures."""
        if validation_result.is_valid:
            return RemediationGuide(
                error_type="none",
                specific_guidance="No issues found. Document is valid."
            )
        
        # Categorize errors by type
        error_types = {}
        for error in validation_result.errors:
            if error.error_type not in error_types:
                error_types[error.error_type] = []
            error_types[error.error_type].append(error)
        
        # Generate guidance for the most critical error type
        primary_error_type = max(error_types.keys(), key=lambda k: len(error_types[k]))
        
        guidance_map = {
            "missing_file": self._generate_missing_file_guidance,
            "missing_section": self._generate_missing_section_guidance,
            "ears_format_error": self._generate_ears_format_guidance,
            "workflow_violation": self._generate_workflow_guidance,
        }
        
        guidance_generator = guidance_map.get(primary_error_type, self._generate_generic_guidance)
        return guidance_generator(error_types[primary_error_type])
    
    def _validate_requirements_structure(self, file_path: str) -> tuple[List[ValidationError], List[ValidationWarning]]:
        """Validate requirements file structure."""
        errors = []
        warnings = []
        
        try:
            with open(file_path, 'r') as f:
                content = f.read()
            
            # Check for required sections
            if "# " not in content and "## Introduction" not in content:
                errors.append(ValidationError(
                    error_type="missing_section",
                    message="Requirements file missing title or Introduction section",
                    location=file_path
                ))
            
            if "## Requirements" not in content:
                errors.append(ValidationError(
                    error_type="missing_section",
                    message="Requirements file missing Requirements section",
                    location=file_path
                ))
            
            # Check for user stories
            user_story_pattern = re.compile(r'\*\*User Story:\*\*', re.IGNORECASE)
            if not user_story_pattern.search(content):
                warnings.append(ValidationWarning(
                    warning_type="missing_user_stories",
                    message="No user stories found in requirements",
                    location=file_path
                ))
        
        except Exception as e:
            errors.append(ValidationError(
                error_type="file_read_error",
                message=f"Failed to read requirements file: {e}",
                location=file_path
            ))
        
        return errors, warnings
    
    def _validate_design_structure(self, file_path: str) -> tuple[List[ValidationError], List[ValidationWarning]]:
        """Validate design file structure."""
        errors = []
        warnings = []
        
        try:
            with open(file_path, 'r') as f:
                content = f.read()
            
            required_sections = ["Overview", "Architecture", "Components"]
            for section in required_sections:
                if f"## {section}" not in content and f"# {section}" not in content:
                    errors.append(ValidationError(
                        error_type="missing_section",
                        message=f"Design file missing {section} section",
                        location=file_path
                    ))
        
        except Exception as e:
            errors.append(ValidationError(
                error_type="file_read_error",
                message=f"Failed to read design file: {e}",
                location=file_path
            ))
        
        return errors, warnings
    
    def _validate_tasks_structure(self, file_path: str) -> tuple[List[ValidationError], List[ValidationWarning]]:
        """Validate tasks file structure."""
        errors = []
        warnings = []
        
        try:
            with open(file_path, 'r') as f:
                content = f.read()
            
            # Check for implementation plan
            if "Implementation Plan" not in content and "# " not in content:
                errors.append(ValidationError(
                    error_type="missing_section",
                    message="Tasks file missing Implementation Plan section",
                    location=file_path
                ))
            
            # Check for task checkboxes
            checkbox_pattern = re.compile(r'- \[ \]', re.MULTILINE)
            if not checkbox_pattern.search(content):
                warnings.append(ValidationWarning(
                    warning_type="missing_tasks",
                    message="No task checkboxes found in tasks file",
                    location=file_path
                ))
        
        except Exception as e:
            errors.append(ValidationError(
                error_type="file_read_error",
                message=f"Failed to read tasks file: {e}",
                location=file_path
            ))
        
        return errors, warnings
    
    def _validate_ears_section(self, section: str, section_num: int) -> tuple[List[ValidationError], List[ValidationWarning]]:
        """Validate EARS format in acceptance criteria section."""
        errors = []
        warnings = []
        
        # Find numbered criteria
        criteria_pattern = re.compile(r'^\s*\d+\.\s+(.+)$', re.MULTILINE)
        criteria = criteria_pattern.findall(section)
        
        if not criteria:
            warnings.append(ValidationWarning(
                warning_type="no_criteria",
                message=f"No numbered acceptance criteria found in section {section_num}",
                location=f"acceptance_criteria_{section_num}"
            ))
            return errors, warnings
        
        for i, criterion in enumerate(criteria):
            # Check if criterion matches EARS patterns
            matches_ears = any(pattern.search(criterion) for pattern in self.ears_patterns.values())
            
            if not matches_ears:
                errors.append(ValidationError(
                    error_type="ears_format_error",
                    message=f"Criterion {i+1} in section {section_num} does not follow EARS format: {criterion[:50]}...",
                    location=f"acceptance_criteria_{section_num}.{i+1}"
                ))
        
        return errors, warnings
    
    def _extract_sections(self, file_path: str) -> Set[str]:
        """Extract section headers from markdown file."""
        sections = set()
        
        try:
            with open(file_path, 'r') as f:
                content = f.read()
            
            # Find markdown headers
            header_pattern = re.compile(r'^#+\s+(.+)$', re.MULTILINE)
            headers = header_pattern.findall(content)
            
            for header in headers:
                sections.add(header.strip())
        
        except Exception:
            pass  # Return empty set on error
        
        return sections
    
    def _get_cached_validation(self, spec_doc: SpecificationDocument, validation_type: str) -> Optional[ValidationResult]:
        """Get cached validation result if still valid."""
        cache_key = f"{spec_doc.id}_{validation_type}"
        
        if cache_key not in self._validation_cache:
            return None
        
        cached = self._validation_cache[cache_key]
        
        if cached.is_expired(self.cache_ttl_seconds):
            del self._validation_cache[cache_key]
            return None
        
        return cached.result
    
    def _cache_validation_result(self, spec_doc: SpecificationDocument, validation_type: str, result: ValidationResult):
        """Cache validation result with timestamp."""
        cache_key = f"{spec_doc.id}_{validation_type}"
        
        # Simple file hash for cache invalidation
        file_hash = str(hash(str(spec_doc.updated_at)))
        
        self._validation_cache[cache_key] = ValidationCache(
            spec_id=spec_doc.id,
            result=result,
            timestamp=datetime.now(),
            file_hash=file_hash
        )
    
    def _generate_missing_file_guidance(self, errors: List[ValidationError]) -> RemediationGuide:
        """Generate guidance for missing file errors."""
        return RemediationGuide(
            error_type="missing_file",
            specific_guidance="Create the missing files using the provided templates. Ensure file paths are correct and files are accessible.",
            examples=[
                "Create requirements.md with Introduction and Requirements sections",
                "Create design.md with Overview, Architecture, and Components sections",
                "Create tasks.md with Implementation Plan section"
            ],
            templates=[
                DocumentTemplate(
                    name="Requirements Template",
                    content="# {spec_name} Requirements\n\n## Introduction\n\n[Provide introduction]\n\n## Requirements\n\n### Requirement 1: [Name]\n\n**User Story:** As a [role], I want [feature], so that [benefit]\n\n#### Acceptance Criteria\n\n1. WHEN [event] THEN [system] SHALL [response]",
                    description="Basic requirements document template"
                )
            ]
        )
    
    def _generate_missing_section_guidance(self, errors: List[ValidationError]) -> RemediationGuide:
        """Generate guidance for missing section errors."""
        return RemediationGuide(
            error_type="missing_section",
            specific_guidance="Add the missing sections to your documents. Each workflow stage requires specific sections to be present.",
            examples=[
                "Add ## Introduction section with overview of the specification",
                "Add ## Requirements section with user stories and acceptance criteria",
                "Add ## Architecture section with system design details"
            ]
        )
    
    def _generate_ears_format_guidance(self, errors: List[ValidationError]) -> RemediationGuide:
        """Generate guidance for EARS format errors."""
        return RemediationGuide(
            error_type="ears_format_error",
            specific_guidance="Rewrite acceptance criteria using EARS (Easy Approach to Requirements Syntax) format. Each criterion should follow the pattern: WHEN [event] THEN [system] SHALL [response]",
            examples=[
                "WHEN user clicks submit button THEN system SHALL validate form data",
                "IF user is authenticated THEN system SHALL display dashboard",
                "WHEN validation fails THEN system SHALL display error message"
            ]
        )
    
    def _generate_workflow_guidance(self, errors: List[ValidationError]) -> RemediationGuide:
        """Generate guidance for workflow violation errors."""
        return RemediationGuide(
            error_type="workflow_violation",
            specific_guidance="Follow the systematic workflow progression: Requirements → Design → Tasks → Complete. Each stage requires specific documents and approvals.",
            examples=[
                "Complete requirements document before moving to design stage",
                "Create design document before moving to tasks stage",
                "Ensure all documents are present before marking as complete"
            ]
        )
    
    def _generate_generic_guidance(self, errors: List[ValidationError]) -> RemediationGuide:
        """Generate generic guidance for unspecified error types."""
        return RemediationGuide(
            error_type="generic",
            specific_guidance="Review the validation errors and address each issue systematically. Refer to the specification framework documentation for detailed guidance.",
            examples=[
                "Check file paths and ensure all referenced files exist",
                "Verify document structure follows the required format",
                "Ensure workflow stage progression is followed correctly"
            ]
        )