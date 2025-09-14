"""
Validation Models for DevPost Integration

This module contains validation-related classes and error handling
for the DevPost integration system.

RM-DDD Compliance:
- Each class implements ReflectiveModule interface
- Health monitoring and metrics tracking
- Registry integration
- Configuration management
- Under 300 lines per module
"""

import logging
from datetime import datetime
from .reflective_module import ReflectiveModule, register_module, ModuleHealth, ModuleStatus, ModuleCapability
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)


class ValidationResult(ReflectiveModule):
def register_with_registry(self, registry):
        """Register this module with the RM registry."""
        if registry:
            registry.register_module(self)
            self.add_capability("registry_registered")
    
    def get_module_metadata(self) -> Dict[str, any]:
        """Get module metadata for registry."""
        return {
            "module_id": self.module_id,
            "module_type": self.module_type,
            "capabilities": self.capabilities,
            "dependencies": self.dependencies,
            "health_status": self.health_status,
            "last_updated": self.last_updated
        }
def get_health_indicators(self) -> Dict[str, any]:
        """Get health indicators for this module."""
        return {
            "module_id": self.module_id,
            "status": self.health_status,
            "last_updated": self.last_updated,
            "capabilities_count": len(self.capabilities),
            "dependencies_count": len(self.dependencies)
        }
    
    def get_status_report(self) -> Dict[str, any]:
        """Get comprehensive status report for this module."""
        return {
            "module_id": self.module_id,
            "health_status": self.health_status,
            "capabilities": self.capabilities,
            "dependencies": self.dependencies,
            "last_updated": self.last_updated,
            "performance_metrics": self.get_metrics()
        }
    """
    Manages validation results and error tracking.
    
    This class handles validation outcomes, error collection,
    and provides detailed validation reporting.
    """
    
    def __init__(self, validation_data: Dict[str, Any] = None):
        """Initialize validation result."""
        super().__init__()
        self.module_id = "validation_result"
        self.version = "1.0.0"
        self.validation_data = validation_data or {}
        self.errors = []
        self.warnings = []
        self.is_valid = True
        self.validation_time = datetime.now()
        self._operation_count = 0
        self._errors = 0
        register_module(self)
    
    def get_module_info(self) -> Dict[str, Any]:
        """Get module information."""
        return {
            "module_id": self.module_id,
            "version": self.version,
            "is_valid": self.is_valid,
            "error_count": len(self.errors),
            "warning_count": len(self.warnings)
        }
    
    def get_capabilities(self) -> List[ModuleCapability]:
        """Get module capabilities."""
        return [
            ModuleCapability.VALIDATION,
            ModuleCapability.ERROR_HANDLING,
            ModuleCapability.MONITORING,
            ModuleCapability.REPORTING
        ]
    
    def get_dependencies(self) -> List[str]:
        """Get module dependencies."""
        return ["reflective_module", "datetime", "typing"]
    
    def check_health(self) -> ModuleHealth:
        """Check module health."""
        issues = []
        health_score = self._calculate_health_score()
        
        if self._errors > 0:
            issues.append(f"{self._errors} internal errors occurred")
        
        if len(self.errors) > 10:
            issues.append(f"High error count: {len(self.errors)}")
        
        if not self.validation_data:
            issues.append("No validation data available")
        
        status = ModuleStatus.HEALTHY if health_score >= 0.9 else ModuleStatus.WARNING
        
        return ModuleHealth(
            module_id=self.module_id,
            status=status,
            health_score=health_score,
            issues=issues,
            capabilities=self.get_capabilities(),
            dependencies=self.get_dependencies(),
            metrics=self.get_metrics(),
            last_check=datetime.now()
        )
    
    def _calculate_health_score(self) -> float:
        """Calculate health score."""
        score = 1.0
        
        # Penalize internal errors
        if self._errors > 0:
            score -= min(0.5, self._errors * 0.1)
        
        # Penalize high validation error count
        if len(self.errors) > 10:
            score -= 0.2
        
        return max(0.0, score)
    
    def _identify_health_issues(self) -> List[str]:
        """Identify health issues."""
        issues = []
        
        if self._errors > 0:
            issues.append(f"Internal errors: {self._errors}")
        
        if len(self.errors) > 10:
            issues.append(f"High validation error count: {len(self.errors)}")
        
        return issues
    
    def get_configuration(self) -> Dict[str, Any]:
        """Get module configuration."""
        return {
            "max_errors": 100,
            "max_warnings": 200,
            "validation_timeout": 30,
            "strict_mode": False
        }
    
    def update_configuration(self, config: Dict[str, Any]) -> bool:
        """Update module configuration."""
        try:
            # Update configuration logic here
            return True
        except Exception as e:
            logger.error(f"Failed to update configuration: {e}")
            return False
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get module metrics."""
        return {
            "operation_count": self._operation_count,
            "error_count": self._errors,
            "validation_errors": len(self.errors),
            "validation_warnings": len(self.warnings),
            "is_valid": self.is_valid,
            "validation_time": self.validation_time.isoformat()
        }
    
    def reset_metrics(self) -> None:
        """Reset module metrics."""
        self._operation_count = 0
        self._errors = 0
        self.errors.clear()
        self.warnings.clear()
        self.is_valid = True
    
    def add_error(self, error_message: str, field: str = None) -> None:
        """Add validation error."""
        try:
            error = {
                "message": error_message,
                "field": field,
                "timestamp": datetime.now().isoformat()
            }
            self.errors.append(error)
            self.is_valid = False
            self._operation_count += 1
        except Exception as e:
            logger.error(f"Failed to add error: {e}")
            self._errors += 1
    
    def add_warning(self, warning_message: str, field: str = None) -> None:
        """Add validation warning."""
        try:
            warning = {
                "message": warning_message,
                "field": field,
                "timestamp": datetime.now().isoformat()
            }
            self.warnings.append(warning)
            self._operation_count += 1
        except Exception as e:
            logger.error(f"Failed to add warning: {e}")
            self._errors += 1
    
    def clear_errors(self) -> None:
        """Clear all validation errors."""
        try:
            self.errors.clear()
            self.is_valid = True
            self._operation_count += 1
        except Exception as e:
            logger.error(f"Failed to clear errors: {e}")
            self._errors += 1
    
    def clear_warnings(self) -> None:
        """Clear all validation warnings."""
        try:
            self.warnings.clear()
            self._operation_count += 1
        except Exception as e:
            logger.error(f"Failed to clear warnings: {e}")
            self._errors += 1
    
    def get_validation_summary(self) -> Dict[str, Any]:
        """Get validation summary."""
        return {
            "is_valid": self.is_valid,
            "error_count": len(self.errors),
            "warning_count": len(self.warnings),
            "validation_time": self.validation_time.isoformat(),
            "errors": self.errors,
            "warnings": self.warnings
        }
    
    def validate_data(self, data: Dict[str, Any], rules: Dict[str, Any]) -> bool:
        """Validate data against rules."""
        try:
            self.clear_errors()
            self.clear_warnings()
            
            # Basic validation logic
            for field, rule in rules.items():
                if field not in data:
                    self.add_error(f"Missing required field: {field}", field)
                elif rule.get("required") and not data[field]:
                    self.add_error(f"Required field is empty: {field}", field)
            
            self.is_valid = len(self.errors) == 0
            self._operation_count += 1
            return self.is_valid
        except Exception as e:
            logger.error(f"Data validation failed: {e}")
            self._errors += 1
            return False
    
    def _update_metrics(self, operation: str) -> None:
        """Update internal metrics."""
        self._operation_count += 1
        logger.debug(f"Validation result: {operation}")