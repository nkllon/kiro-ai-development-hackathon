"""
Core data models for Technical Debt Patch Annotation System.

This module provides the fundamental data structures for patch annotations,
including classification enums, validation results, and the core PatchAnnotation model.
"""

import re
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import List, Dict, Any, Optional, Union
from pathlib import Path


class DebtLevel(Enum):
    """Technical debt severity levels for patch classification."""
    LOW = "Low"           # Minor workaround, low maintenance burden
    MEDIUM = "Medium"     # Moderate impact, requires attention
    HIGH = "High"         # Significant impact, priority cleanup
    CRITICAL = "Critical" # Severe impact, immediate attention required


class BypassType(Enum):
    """Types of architectural bypasses that patches represent."""
    ARCHITECTURE = "Architecture"   # Bypasses architectural patterns
    SECURITY = "Security"          # Temporary security workaround
    PERFORMANCE = "Performance"    # Performance optimization patch
    INTEGRATION = "Integration"    # External system integration patch
    COMPLIANCE = "Compliance"      # Regulatory compliance workaround


@dataclass
class ValidationResult:
    """Result of patch annotation validation."""
    is_valid: bool
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ExtractionResult:
    """Result of patch annotation extraction from source code."""
    patches: List['PatchAnnotation'] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    file_path: Optional[str] = None
    total_lines_scanned: int = 0
    extraction_metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class PatchAnnotation:
    """
    Standardized patch annotation structure for tracking technical debt.
    
    This dataclass represents a complete patch annotation with all required
    metadata for systematic tracking and cleanup management.
    """
    # Core identification
    patch_id: str = field(default_factory=lambda: f"PATCH-{uuid.uuid4().hex[:8].upper()}")
    
    # Required metadata fields
    reason: str = ""                      # Why this patch was needed
    upstream_issue: str = ""              # Reference to root cause issue
    cleanup_task: str = ""                # Specific remediation guidance
    debt_level: DebtLevel = DebtLevel.MEDIUM
    bypass_type: BypassType = BypassType.ARCHITECTURE
    
    # Temporal tracking
    created_date: datetime = field(default_factory=datetime.now)
    expected_resolution: Optional[datetime] = None
    
    # System context
    component: str = ""                   # Affected system component
    file_path: str = ""                   # Source file location
    line_start: int = 0                   # Starting line number
    line_end: int = 0                     # Ending line number
    
    # Validation and cleanup
    validation_criteria: List[str] = field(default_factory=list)  # How to verify cleanup success
    
    # Metadata
    created_by: str = ""                  # Developer who created the patch
    assigned_to: str = ""                 # Developer responsible for cleanup
    tags: List[str] = field(default_factory=list)  # Additional classification tags
    
    def __post_init__(self):
        """Validate required fields after initialization."""
        if not self.patch_id:
            self.patch_id = f"PATCH-{uuid.uuid4().hex[:8].upper()}"
        
        # Ensure enums are properly set
        if isinstance(self.debt_level, str):
            self.debt_level = DebtLevel(self.debt_level)
        if isinstance(self.bypass_type, str):
            self.bypass_type = BypassType(self.bypass_type)
    
    def validate(self) -> ValidationResult:
        """
        Validate the patch annotation for completeness and correctness.
        
        Returns:
            ValidationResult with validation status and any errors/warnings
        """
        errors = []
        warnings = []
        
        # Required field validation
        if not self.reason.strip():
            errors.append("Reason field is required and cannot be empty")
        
        if not self.upstream_issue.strip():
            errors.append("Upstream issue reference is required")
        
        if not self.cleanup_task.strip():
            errors.append("Cleanup task description is required")
        
        if not self.component.strip():
            errors.append("Component field is required")
        
        # Validation criteria check
        if not self.validation_criteria:
            warnings.append("No validation criteria specified - cleanup verification may be difficult")
        
        # Date validation
        if self.expected_resolution and self.expected_resolution <= self.created_date:
            errors.append("Expected resolution date must be after creation date")
        
        # File path validation
        if self.file_path and not Path(self.file_path).exists():
            warnings.append(f"File path does not exist: {self.file_path}")
        
        # Line number validation
        if self.line_start > 0 and self.line_end > 0 and self.line_start > self.line_end:
            errors.append("Start line number cannot be greater than end line number")
        
        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
            metadata={
                "patch_id": self.patch_id,
                "validation_timestamp": datetime.now().isoformat()
            }
        )
    
    def to_annotation_format(self) -> str:
        """
        Convert patch annotation to standardized comment format.
        
        Returns:
            String representation suitable for embedding in source code
        """
        lines = [
            f"PATCH_START: {self.patch_id}",
            f"REASON: {self.reason}",
            f"UPSTREAM: {self.upstream_issue}",
            f"CLEANUP: {self.cleanup_task}",
            f"DEBT_LEVEL: {self.debt_level.value}",
            f"EXPECTED_RESOLUTION: {self.expected_resolution.isoformat() if self.expected_resolution else 'TBD'}",
            f"COMPONENT: {self.component}",
            f"BYPASS_TYPE: {self.bypass_type.value}",
        ]
        
        if self.validation_criteria:
            criteria_str = '", "'.join(self.validation_criteria)
            lines.append(f'VALIDATION: ["{criteria_str}"]')
        
        lines.append(f"PATCH_END: {self.patch_id}")
        
        return "\n".join(lines)
    
    @classmethod
    def from_annotation_format(cls, annotation_text: str, file_path: str = "", line_start: int = 0) -> 'PatchAnnotation':
        """
        Parse patch annotation from standardized comment format.
        
        Args:
            annotation_text: The annotation text to parse
            file_path: Source file path where annotation was found
            line_start: Starting line number of the annotation
            
        Returns:
            PatchAnnotation instance parsed from the text
            
        Raises:
            ValueError: If annotation format is invalid or required fields are missing
        """
        lines = [line.strip() for line in annotation_text.strip().split('\n')]
        
        # Extract patch ID from start/end markers
        patch_start_match = None
        patch_end_match = None
        
        for line in lines:
            if line.startswith("PATCH_START:"):
                patch_start_match = line.split(":", 1)[1].strip()
            elif line.startswith("PATCH_END:"):
                patch_end_match = line.split(":", 1)[1].strip()
        
        if not patch_start_match or not patch_end_match:
            raise ValueError("Invalid annotation format: missing PATCH_START or PATCH_END markers")
        
        if patch_start_match != patch_end_match:
            raise ValueError(f"Patch ID mismatch: START={patch_start_match}, END={patch_end_match}")
        
        # Parse annotation fields
        annotation_data = {"patch_id": patch_start_match}
        
        for line in lines:
            if ":" in line and not line.startswith(("PATCH_START:", "PATCH_END:")):
                key, value = line.split(":", 1)
                key = key.strip().lower()
                value = value.strip()
                
                if key == "reason":
                    annotation_data["reason"] = value
                elif key == "upstream":
                    annotation_data["upstream_issue"] = value
                elif key == "cleanup":
                    annotation_data["cleanup_task"] = value
                elif key == "debt_level":
                    try:
                        annotation_data["debt_level"] = DebtLevel(value)
                    except ValueError:
                        raise ValueError(f"Invalid debt level: {value}")
                elif key == "bypass_type":
                    try:
                        annotation_data["bypass_type"] = BypassType(value)
                    except ValueError:
                        raise ValueError(f"Invalid bypass type: {value}")
                elif key == "component":
                    annotation_data["component"] = value
                elif key == "expected_resolution":
                    if value != "TBD":
                        try:
                            annotation_data["expected_resolution"] = datetime.fromisoformat(value)
                        except ValueError:
                            raise ValueError(f"Invalid date format for expected_resolution: {value}")
                elif key == "validation":
                    # Parse validation criteria list
                    if value.startswith("[") and value.endswith("]"):
                        criteria_text = value[1:-1]  # Remove brackets
                        if criteria_text.strip():
                            # Split on '", "' and clean up quotes
                            criteria = [c.strip().strip('"') for c in criteria_text.split('", "')]
                            annotation_data["validation_criteria"] = criteria
        
        # Set file location metadata
        annotation_data["file_path"] = file_path
        annotation_data["line_start"] = line_start
        annotation_data["line_end"] = line_start + len(lines) - 1
        
        return cls(**annotation_data)


class AnnotationParser:
    """Parser for extracting patch annotations from source code."""
    
    # Regex patterns for finding patch annotations
    PATCH_START_PATTERN = re.compile(r'^\s*(?:#|//|\*|<!--)?\s*PATCH_START:\s*(.+?)(?:\s*-->)?$', re.MULTILINE)
    PATCH_END_PATTERN = re.compile(r'^\s*(?:#|//|\*|<!--)?\s*PATCH_END:\s*(.+?)(?:\s*-->)?$', re.MULTILINE)
    
    @classmethod
    def extract_annotations(cls, content: str, file_path: str = "") -> ExtractionResult:
        """
        Extract all patch annotations from source code content.
        
        Args:
            content: Source code content to scan
            file_path: Path to the source file being scanned
            
        Returns:
            ExtractionResult containing found patches and any errors
        """
        result = ExtractionResult(
            file_path=file_path,
            total_lines_scanned=len(content.split('\n'))
        )
        
        lines = content.split('\n')
        
        # Find all PATCH_START and PATCH_END markers
        start_matches = []
        end_matches = []
        
        for i, line in enumerate(lines):
            start_match = cls.PATCH_START_PATTERN.match(line)
            if start_match:
                start_matches.append((i + 1, start_match.group(1).strip()))
            
            end_match = cls.PATCH_END_PATTERN.match(line)
            if end_match:
                end_matches.append((i + 1, end_match.group(1).strip()))
        
        # Match start and end markers
        for start_line, start_id in start_matches:
            # Find corresponding end marker
            end_line = None
            end_id = None
            
            for end_line_candidate, end_id_candidate in end_matches:
                if end_id_candidate == start_id and end_line_candidate > start_line:
                    end_line = end_line_candidate
                    end_id = end_id_candidate
                    break
            
            if not end_line:
                result.errors.append(f"No matching PATCH_END found for PATCH_START at line {start_line} (ID: {start_id})")
                continue
            
            # Extract annotation content
            annotation_lines = lines[start_line - 1:end_line]
            annotation_text = '\n'.join(annotation_lines)
            
            try:
                patch = PatchAnnotation.from_annotation_format(
                    annotation_text, 
                    file_path=file_path, 
                    line_start=start_line
                )
                result.patches.append(patch)
            except ValueError as e:
                result.errors.append(f"Failed to parse annotation at line {start_line}: {str(e)}")
        
        result.extraction_metadata = {
            "patches_found": len(result.patches),
            "errors_count": len(result.errors),
            "start_markers_found": len(start_matches),
            "end_markers_found": len(end_matches)
        }
        
        return result


def validate_patch_annotation(patch: PatchAnnotation) -> ValidationResult:
    """
    Standalone validation function for patch annotations.
    
    Args:
        patch: PatchAnnotation instance to validate
        
    Returns:
        ValidationResult with validation status and details
    """
    return patch.validate()


def generate_patch_id() -> str:
    """
    Generate a unique patch identifier.
    
    Returns:
        String in format PATCH-XXXXXXXX where X is uppercase hex
    """
    return f"PATCH-{uuid.uuid4().hex[:8].upper()}"