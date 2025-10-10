"""
Makefile Syntax Validator

Validates and repairs GNU Make syntax compliance with embedded Python code support.
"""

import re
import ast
import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from enum import Enum

from src.rm_ddd.core.unified_reflective_module import ReflectiveModule, ModuleStatus, ModuleCapability, ModuleHealth


class SyntaxErrorType(Enum):
    """Types of makefile syntax errors."""
    MISSING_SEPARATOR = "missing_separator"
    INVALID_RECIPE = "invalid_recipe"
    MALFORMED_TARGET = "malformed_target"
    INVALID_PYTHON_CODE = "invalid_python_code"
    MISSING_PHONY = "missing_phony"
    INVALID_VARIABLE = "invalid_variable"


@dataclass
class SyntaxError:
    """Represents a makefile syntax error."""
    error_type: SyntaxErrorType
    line_number: int
    line_content: str
    message: str
    suggested_fix: Optional[str] = None
    severity: str = "error"


@dataclass
class ValidationResult:
    """Result of makefile syntax validation."""
    is_valid: bool
    errors: List[SyntaxError]
    warnings: List[SyntaxError]
    repaired_content: Optional[str] = None
    backup_path: Optional[str] = None


class MakefileSyntaxValidator(ReflectiveModule):
    """
    Makefile syntax validator with automatic repair capabilities.
    
    Validates GNU Make syntax compliance and repairs common syntax errors
    including embedded Python code validation.
    """
    
    def __init__(self):
        super().__init__()
        self.module_id = "makefile_syntax_validator"
        self._logger = logging.getLogger(__name__)
        
        # Validation patterns
        self._target_pattern = re.compile(r'^([^:]+):\s*(.*)$')
        self._variable_pattern = re.compile(r'^([A-Z_][A-Z0-9_]*)\s*[:?+]?=\s*(.*)$')
        self._phony_pattern = re.compile(r'^\.PHONY:\s*(.+)$')
        self._python_block_pattern = re.compile(r'python3?\s+-c\s*["\']([^"\']*)["\']', re.MULTILINE | re.DOTALL)
        
        # Statistics
        self._validation_count = 0
        self._repair_count = 0
        self._error_count = 0
    
    def get_module_info(self) -> Dict[str, Any]:
        """Get module information."""
        return {
            "module_id": self.module_id,
            "name": "Makefile Syntax Validator",
            "version": "1.0.0",
            "description": "Validates and repairs GNU Make syntax compliance",
            "capabilities": [cap.value for cap in self.get_capabilities()],
            "statistics": {
                "validations_performed": self._validation_count,
                "repairs_performed": self._repair_count,
                "errors_detected": self._error_count
            }
        }
    
    def get_capabilities(self) -> List[ModuleCapability]:
        """Get module capabilities."""
        return [
            ModuleCapability.VALIDATION,
            ModuleCapability.DATA_PROCESSING,
            ModuleCapability.CORE_FUNCTIONALITY
        ]
    
    def get_health_status(self) -> ModuleHealth:
        """Get module health status."""
        # Calculate health score based on error rate
        if self._validation_count == 0:
            health_score = 1.0
            status = ModuleStatus.HEALTHY
        else:
            error_rate = self._error_count / self._validation_count
            if error_rate < 0.1:
                health_score = 1.0
                status = ModuleStatus.HEALTHY
            elif error_rate < 0.3:
                health_score = 0.7
                status = ModuleStatus.WARNING
            else:
                health_score = 0.3
                status = ModuleStatus.ERROR
        
        issues = []
        if self._error_count > 0:
            issues.append(f"Detected {self._error_count} syntax errors")
        
        return ModuleHealth(
            module_id=self.module_id,
            status=status,
            health_score=health_score,
            issues=issues,
            last_check=self._last_activity,
            uptime_seconds=(self._last_activity - self._start_time).total_seconds(),
            error_count=self._error_count,
            warning_count=0
        )
    
    def graceful_degradation(self):
        """Perform graceful degradation."""
        from src.rm_ddd.core.unified_reflective_module import GracefulDegradationResult
        
        # In degraded mode, only perform basic validation
        return GracefulDegradationResult(
            success=True,
            degraded_capabilities=[ModuleCapability.DATA_PROCESSING],
            remaining_capabilities=[ModuleCapability.VALIDATION, ModuleCapability.CORE_FUNCTIONALITY],
            error_message=None
        )
    
    def validate_makefile(self, file_path: Path) -> ValidationResult:
        """
        Validate a makefile for syntax compliance.
        
        Args:
            file_path: Path to the makefile to validate
            
        Returns:
            ValidationResult with errors, warnings, and suggested repairs
        """
        with self.trace_operation("validate_makefile", file_path=str(file_path)) as trace:
            self._validation_count += 1
            self._update_activity()
            
            try:
                if not file_path.exists():
                    error = SyntaxError(
                        error_type=SyntaxErrorType.MALFORMED_TARGET,
                        line_number=0,
                        line_content="",
                        message=f"Makefile not found: {file_path}"
                    )
                    return ValidationResult(is_valid=False, errors=[error], warnings=[])
                
                with open(file_path, 'r') as f:
                    content = f.read()
                
                errors = []
                warnings = []
                
                # Validate syntax
                errors.extend(self._validate_syntax(content))
                errors.extend(self._validate_python_code(content))
                warnings.extend(self._validate_conventions(content))
                
                # Update error count
                self._error_count += len(errors)
                
                is_valid = len(errors) == 0
                
                result = ValidationResult(
                    is_valid=is_valid,
                    errors=errors,
                    warnings=warnings
                )
                
                trace.output_result = {
                    "is_valid": is_valid,
                    "error_count": len(errors),
                    "warning_count": len(warnings)
                }
                
                return result
                
            except Exception as e:
                self._increment_error_count()
                self._logger.error(f"Validation failed for {file_path}: {e}")
                raise
    
    def repair_makefile(self, file_path: Path, create_backup: bool = True) -> ValidationResult:
        """
        Repair makefile syntax errors automatically.
        
        Args:
            file_path: Path to the makefile to repair
            create_backup: Whether to create a backup before repair
            
        Returns:
            ValidationResult with repaired content and backup path
        """
        with self.trace_operation("repair_makefile", file_path=str(file_path), create_backup=create_backup) as trace:
            self._repair_count += 1
            self._update_activity()
            
            try:
                # First validate to identify errors
                validation_result = self.validate_makefile(file_path)
                
                if validation_result.is_valid:
                    return validation_result
                
                # Create backup if requested
                backup_path = None
                if create_backup:
                    backup_path = self._create_backup(file_path)
                
                # Read original content
                with open(file_path, 'r') as f:
                    content = f.read()
                
                # Apply repairs
                repaired_content = self._apply_repairs(content, validation_result.errors)
                
                # Validate repaired content
                repaired_result = self._validate_content(repaired_content)
                
                result = ValidationResult(
                    is_valid=repaired_result.is_valid,
                    errors=repaired_result.errors,
                    warnings=repaired_result.warnings,
                    repaired_content=repaired_content,
                    backup_path=str(backup_path) if backup_path else None
                )
                
                trace.output_result = {
                    "repair_successful": repaired_result.is_valid,
                    "errors_fixed": len(validation_result.errors) - len(repaired_result.errors),
                    "backup_created": backup_path is not None
                }
                
                return result
                
            except Exception as e:
                self._increment_error_count()
                self._logger.error(f"Repair failed for {file_path}: {e}")
                raise
    
    def _validate_syntax(self, content: str) -> List[SyntaxError]:
        """Validate basic makefile syntax."""
        errors = []
        lines = content.split('\n')
        
        for i, line in enumerate(lines, 1):
            line = line.rstrip()
            
            # Skip empty lines and comments
            if not line or line.startswith('#'):
                continue
            
            # Check for missing separator (common error)
            if ':' in line and not line.startswith('\t'):
                # This should be a target line
                if not self._target_pattern.match(line):
                    # Check if it's missing a tab separator
                    if line.strip() and not line.startswith('.') and '=' not in line:
                        errors.append(SyntaxError(
                            error_type=SyntaxErrorType.MISSING_SEPARATOR,
                            line_number=i,
                            line_content=line,
                            message="Missing separator (tab character required for recipe)",
                            suggested_fix=f"\t{line.strip()}"
                        ))
            
            # Check for invalid recipes (should start with tab)
            elif line.startswith(' ') and not line.startswith('\t'):
                errors.append(SyntaxError(
                    error_type=SyntaxErrorType.INVALID_RECIPE,
                    line_number=i,
                    line_content=line,
                    message="Recipe should start with tab, not spaces",
                    suggested_fix=line.replace('    ', '\t').replace('  ', '\t')
                ))
        
        return errors
    
    def _validate_python_code(self, content: str) -> List[SyntaxError]:
        """Validate embedded Python code in makefiles."""
        errors = []
        
        # Find Python code blocks
        for match in self._python_block_pattern.finditer(content):
            python_code = match.group(1)
            
            try:
                # Try to parse the Python code
                ast.parse(python_code)
            except SyntaxError as e:
                # Find line number in makefile
                line_number = content[:match.start()].count('\n') + 1
                
                errors.append(SyntaxError(
                    error_type=SyntaxErrorType.INVALID_PYTHON_CODE,
                    line_number=line_number,
                    line_content=match.group(0),
                    message=f"Invalid Python syntax: {e.msg}",
                    suggested_fix=None
                ))
        
        return errors
    
    def _validate_conventions(self, content: str) -> List[SyntaxError]:
        """Validate makefile conventions (generates warnings)."""
        warnings = []
        lines = content.split('\n')
        
        # Track targets for PHONY checking
        targets = []
        phony_targets = set()
        
        for i, line in enumerate(lines, 1):
            line = line.strip()
            
            # Extract targets
            target_match = self._target_pattern.match(line)
            if target_match:
                target_name = target_match.group(1).strip()
                targets.append((target_name, i))
            
            # Extract PHONY declarations
            phony_match = self._phony_pattern.match(line)
            if phony_match:
                phony_list = phony_match.group(1).split()
                phony_targets.update(phony_list)
        
        # Check for missing PHONY declarations
        for target_name, line_num in targets:
            if self._should_be_phony(target_name) and target_name not in phony_targets:
                warnings.append(SyntaxError(
                    error_type=SyntaxErrorType.MISSING_PHONY,
                    line_number=line_num,
                    line_content=f"{target_name}:",
                    message=f"Target '{target_name}' should be declared as .PHONY",
                    suggested_fix=f".PHONY: {target_name}",
                    severity="warning"
                ))
        
        return warnings
    
    def _should_be_phony(self, target_name: str) -> bool:
        """Check if a target should be declared as PHONY."""
        phony_keywords = [
            'help', 'clean', 'test', 'install', 'deploy', 'build',
            'run', 'start', 'stop', 'restart', 'status', 'check',
            'lint', 'format', 'validate', 'setup', 'init'
        ]
        
        return any(keyword in target_name.lower() for keyword in phony_keywords)
    
    def _apply_repairs(self, content: str, errors: List[SyntaxError]) -> str:
        """Apply automatic repairs to makefile content."""
        lines = content.split('\n')
        
        # Sort errors by line number in reverse order to avoid index shifting
        sorted_errors = sorted(errors, key=lambda e: e.line_number, reverse=True)
        
        for error in sorted_errors:
            if error.suggested_fix and error.line_number <= len(lines):
                line_index = error.line_number - 1
                
                if error.error_type == SyntaxErrorType.MISSING_SEPARATOR:
                    # Replace the line with the suggested fix
                    lines[line_index] = error.suggested_fix
                elif error.error_type == SyntaxErrorType.INVALID_RECIPE:
                    # Fix spacing issues
                    lines[line_index] = error.suggested_fix
        
        return '\n'.join(lines)
    
    def _validate_content(self, content: str) -> ValidationResult:
        """Validate makefile content without file I/O."""
        errors = []
        warnings = []
        
        errors.extend(self._validate_syntax(content))
        errors.extend(self._validate_python_code(content))
        warnings.extend(self._validate_conventions(content))
        
        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings
        )
    
    def _create_backup(self, file_path: Path) -> Path:
        """Create a backup of the makefile."""
        from datetime import datetime
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = file_path.parent / f"{file_path.name}.backup_{timestamp}"
        
        import shutil
        shutil.copy2(file_path, backup_path)
        
        return backup_path