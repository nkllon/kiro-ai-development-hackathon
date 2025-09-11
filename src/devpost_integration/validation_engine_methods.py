from .reflective_module import ReflectiveModule, register_module, ModuleCapability, ModuleHealth, ModuleStatus, ModuleConfiguration
from datetime import datetime
from typing import Dict, Any, List, Optional
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

class ValidationEngine(ReflectiveModule):
    """
    Refactored validation engine for Devpost project validation.
    
    Orchestrates specialized validation rules to provide comprehensive
    project validation with actionable feedback.
    """
    
    def __init__(self, project_id: str):
        super().__init__(module_id="validation_engine", version="1.0.0")
        self._start_time = datetime.now()
        register_module(self)

        """
        Initialize validation engine.
        
        Args:
            project_id: Unique identifier for the project
        """
        self.project_id = project_id
        self.validation_rules = self._initialize_validation_rules()
        
        # Statistics
        self.stats = {
            'total_validations': 0,
            'successful_validations': 0,
            'failed_validations': 0,
            'last_validation': None
        }
    
    def _initialize_validation_rules(self) -> List[Any]:
        """Initialize all validation rules."""
        return [
            RequiredFieldRule(),
            ContentQualityRule(),
            FormatValidationRule(),
            ConsistencyRule(),
            LinkValidationRule(),
            TeamValidationRule(),
            TagValidationRule()
        ]
    
    def validate_project(self, metadata: ProjectMetadata, context: Optional[ValidationContext] = None) -> ValidationReport:
        """
        Validate project metadata comprehensively.
        
        Args:
            metadata: Project metadata to validate
            context: Optional validation context
            
        Returns:
            Comprehensive validation report
        """
        logger.info(f"Starting validation for project: {self.project_id}")
        
        # Create validation report
        report = ValidationReport(
            project_id=self.project_id,
            validation_timestamp=context.validation_timestamp if context else None,
            context=context
        )
        
        # Run all validation rules
        for rule in self.validation_rules:
            try:
                rule_issues = rule.validate(metadata, context)
                for issue in rule_issues:
                    report.add_issue(issue)
                
                logger.debug(f"Rule '{rule.name}' found {len(rule_issues)} issues")
                
            except Exception as e:
                logger.error(f"Error in validation rule '{rule.name}': {e}")
                # Add error issue
                report.add_issue(ValidationIssue(
                    field="validation_engine",
                    message=f"Validation rule '{rule.name}' failed: {str(e)}",
                    severity=ValidationSeverity.HIGH,
                    category=ValidationCategory.FORMAT,
                    suggestion="Check validation engine configuration",
                    fix_action="Review validation rule implementation"
                ))
        
        # Calculate final score and generate recommendations
        report.calculate_score()
        report.generate_recommendations()
        
        # Update statistics
        self._update_statistics(report)
        
        logger.info(f"Validation complete: {report.overall_score:.1f}/100, {report.total_issues} issues")
        return report
    
    def validate_field(self, field_name: str, value: Any, metadata: ProjectMetadata, 
                      context: Optional[ValidationContext] = None) -> List[ValidationIssue]:
        """
        Validate specific field.
        
        Args:
            field_name: Name of field to validate
            value: Field value to validate
            metadata: Complete project metadata
            context: Optional validation context
            
        Returns:
            List of validation issues for the field
        """
        issues = []
        
        # Find relevant rules for the field
        relevant_rules = [rule for rule in self.validation_rules 
                         if hasattr(rule, 'validate_field')]
        
        for rule in relevant_rules:
            try:
                rule_issues = rule.validate_field(field_name, value, metadata, context)
                issues.extend(rule_issues)
            except Exception as e:
                logger.error(f"Error validating field '{field_name}' with rule '{rule.name}': {e}")
        
        return issues
    
    def get_validation_summary(self, report: ValidationReport) -> Dict[str, Any]:
        """
        Get validation summary.
        
        Args:
            report: Validation report to summarize
            
        Returns:
            Dictionary with validation summary
        """
        return {
            'project_id': report.project_id,
            'overall_score': report.overall_score,
            'is_valid': report.is_valid,
            'total_issues': report.total_issues,
            'critical_issues': report.critical_issues,
            'high_issues': report.high_issues,
            'medium_issues': report.medium_issues,
            'low_issues': report.low_issues,
            'info_issues': report.info_issues,
            'categories': {cat.value: count for cat, count in report.categories.items()},
            'recommendations': report.recommendations
        }
    
    def get_validation_statistics(self) -> Dict[str, Any]:
        """Get validation engine statistics."""
        return {
            **self.stats,
            'total_rules': len(self.validation_rules),
            'rule_names': [rule.name for rule in self.validation_rules]
        }
    
    def add_custom_rule(self, rule: Any) -> None:
        """
        Add custom validation rule.
        
        Args:
            rule: Custom validation rule instance
        """
        if hasattr(rule, 'validate') and hasattr(rule, 'name'):
            self.validation_rules.append(rule)
            logger.info(f"Added custom validation rule: {rule.name}")
        else:
            logger.error("Custom rule must have 'validate' method and 'name' attribute")
    
    def remove_rule(self, rule_name: str) -> bool:
        """
        Remove validation rule by name.
        
        Args:
            rule_name: Name of rule to remove
            
        Returns:
            True if rule was removed, False if not found
        """
        for i, rule in enumerate(self.validation_rules):
            if rule.name == rule_name:
                del self.validation_rules[i]
                logger.info(f"Removed validation rule: {rule_name}")
                return True
        
        logger.warning(f"Validation rule not found: {rule_name}")
        return False
    
    def _update_statistics(self, report: ValidationReport) -> None:
        """Update validation statistics."""
        self.stats['total_validations'] += 1
        
        if report.is_valid:
            self.stats['successful_validations'] += 1
        else:
            self.stats['failed_validations'] += 1
        
        self.stats['last_validation'] = report.validation_timestamp
    
    def get_module_info(self) -> Dict[str, Any]:
        """Get module information"""
        return {
            "name": self.__class__.__name__,
            "version": self.version,
            "module_id": self.module_id,
            "description": "Validation engine for Devpost project validation"
        }
    
    def get_capabilities(self) -> List[ModuleCapability]:
        """Get module capabilities"""
        return [ModuleCapability.CORE_FUNCTIONALITY, ModuleCapability.VALIDATION]
    
    def get_dependencies(self) -> List[str]:
        """Get module dependencies"""
        return ["reflective_module", "validation_rules", "core_models"]
    
    def check_health(self) -> ModuleHealth:
        """Check module health"""
        try:
            if not hasattr(self, '_start_time'):
                return ModuleHealth.UNHEALTHY
            uptime = (datetime.now() - self._start_time).total_seconds()
            if uptime < 0:
                return ModuleHealth.UNHEALTHY
            error_count = getattr(self, '_error_count', 0)
            total_operations = getattr(self, '_command_count', 1)
            error_rate = error_count / total_operations if total_operations > 0 else 0
            if error_rate > 0.5:
                return ModuleHealth.UNHEALTHY
            elif error_rate > 0.1:
                return ModuleHealth.DEGRADED
            else:
                return ModuleHealth.HEALTHY
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return ModuleHealth.UNHEALTHY
    
    def get_configuration(self) -> ModuleConfiguration:
        """Get module configuration"""
        return ModuleConfiguration(
            validation_rules_count=len(self.validation_rules),
            strict_mode=self.strict_mode,
            project_id=self.project_id
        )
    
    def update_configuration(self, config: ModuleConfiguration) -> bool:
        """Update module configuration"""
        try:
            if hasattr(config, 'strict_mode'):
                self.strict_mode = config.strict_mode
            return True
        except Exception as e:
            logger.error(f"Configuration update failed: {e}")
            return False
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get module metrics"""
        try:
            uptime = (datetime.now() - self._start_time).total_seconds() if hasattr(self, '_start_time') else 0
            error_count = getattr(self, '_error_count', 0)
            total_operations = getattr(self, '_command_count', 0)
            success_count = total_operations - error_count
            success_rate = (success_count / total_operations) if total_operations > 0 else 1.0
            error_rate = (error_count / total_operations) if total_operations > 0 else 0.0
            health_status = self.check_health()
            
            return {
                'uptime_seconds': uptime,
                'total_operations': total_operations,
                'success_count': success_count,
                'error_count': error_count,
                'success_rate': success_rate,
                'error_rate': error_rate,
                'health_status': health_status.value,
                'module_id': getattr(self, 'module_id', 'unknown'),
                'version': getattr(self, 'version', 'unknown'),
                'last_updated': datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Metrics collection failed: {e}")
            return {
                'error': str(e),
                'health_status': 'UNHEALTHY',
                'last_updated': datetime.now().isoformat()
            }
    
    def reset_metrics(self) -> None:
        """Reset module metrics"""
        self._error_count = 0
        self._command_count = 0
        self._start_time = datetime.now()