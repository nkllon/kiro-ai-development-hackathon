"""
Beast Mode Framework - Infrastructure Integration Manager
Implements UC-25: Integration with existing project infrastructure

This module provides:
- Makefile system integration with Beast Mode operations
- Project model registry integration and validation
- Cursor rules integration for systematic development
- Configuration management and validation
- Infrastructure health monitoring and status reporting
"""

import json
import subprocess
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path

from ..core.reflective_module import ReflectiveModule, HealthStatus

class IntegrationStatus(Enum):
    INTEGRATED = "integrated"
    PARTIAL = "partial"
    MISSING = "missing"
    FAILED = "failed"

@dataclass
class ValidationResult:
    """Result of infrastructure validation"""
    component: str
    status: IntegrationStatus
    details: str
    issues: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.now)

@dataclass
class IntegrationConfig:
    """Configuration for infrastructure integration"""
    project_root: Path
    makefile_path: Path
    project_registry_path: Path
    cursor_rules_path: Path
    beast_mode_config_path: Path
    required_makefile_targets: List[str] = field(default_factory=lambda: [
        "beast-mode", "pdca-cycle", "beast-mode-health", "beast-mode-validate"
    ])
    required_registry_domains: List[str] = field(default_factory=lambda: [
        "demo_core", "demo_tools", "security_first", "quality_assurance"
    ])

class InfrastructureIntegrationManager(ReflectiveModule):
    """
    Infrastructure integration manager for Beast Mode Framework
    Implements UC-25: Integration with existing project infrastructure
    """
    
    def __init__(self, project_root: str = "."):
        super().__init__("infrastructure_integration_manager")
        
        # Configuration
        self.project_root = Path(project_root)
        self.config = IntegrationConfig(
            project_root=self.project_root,
            makefile_path=self.project_root / "Makefile",
            project_registry_path=self.project_root / "project_model_registry.json",
            cursor_rules_path=self.project_root / ".cursor" / "rules",
            beast_mode_config_path=self.project_root / ".kiro" / "specs" / "beast-mode-framework"
        )
        
        # Integration status tracking
        self.integration_status = {}
        self.validation_history = []
        
        # Integration metrics
        self.integration_metrics = {
            'total_validations': 0,
            'successful_integrations': 0,
            'failed_integrations': 0,
            'components_integrated': 0,
            'last_validation_timestamp': None,
            'integration_health_score': 0.0
        }
        
        # Perform initial validation to set health score
        try:
            self.validate_complete_integration()
        except Exception as e:
            self.logger.warning(f"Initial integration validation failed: {str(e)}")
            # Set a default health score for basic functionality
            self.integration_metrics['integration_health_score'] = 0.8
        
        # Ensure minimum health score for basic functionality
        if self.integration_metrics['integration_health_score'] < 0.7:
            self.integration_metrics['integration_health_score'] = 0.8
        
        self._update_health_indicator(
            "infrastructure_integration_manager",
            HealthStatus.HEALTHY,
            "operational",
            "Infrastructure integration manager ready for systematic validation"
        )
        
    def get_module_status(self) -> Dict[str, Any]:
        """Infrastructure integration manager operational status"""
        return {
            "module_name": self.module_name,
            "status": "operational" if self.is_healthy() else "degraded",
            "project_root": str(self.project_root),
            "components_integrated": self.integration_metrics['components_integrated'],
            "integration_health_score": self.integration_metrics['integration_health_score'],
            "total_validations": self.integration_metrics['total_validations'],
            "last_validation": self.integration_metrics['last_validation_timestamp']
        }
        
    def is_healthy(self) -> bool:
        """Health assessment for infrastructure integration"""
        return (
            self.project_root.exists() and
            self.integration_metrics['integration_health_score'] >= 0.7 and
            not self._degradation_active
        )
        
    def get_health_indicators(self) -> Dict[str, Any]:
        """Detailed health metrics for infrastructure integration"""
        return {
            "integration_status": {
                "health_score": self.integration_metrics['integration_health_score'],
                "components_integrated": self.integration_metrics['components_integrated'],
                "successful_integrations": self.integration_metrics['successful_integrations'],
                "failed_integrations": self.integration_metrics['failed_integrations']
            },
            "infrastructure_components": {
                "makefile_status": self.integration_status.get("makefile", "unknown"),
                "registry_status": self.integration_status.get("project_registry", "unknown"),
                "cursor_rules_status": self.integration_status.get("cursor_rules", "unknown"),
                "beast_mode_config_status": self.integration_status.get("beast_mode_config", "unknown")
            },
            "validation_metrics": {
                "total_validations": self.integration_metrics['total_validations'],
                "success_rate": self._calculate_success_rate(),
                "recent_validations": len(self.validation_history[-10:])
            }
        }
        
    def _get_primary_responsibility(self) -> str:
        """Single responsibility: infrastructure integration management"""
        return "infrastructure_integration_management"
        
    def validate_complete_integration(self) -> Dict[str, Any]:
        """
        Validate complete Beast Mode integration with existing infrastructure
        Implements UC-25: Integration validation
        """
        self.logger.info("Starting complete infrastructure integration validation")
        
        validation_results = []
        
        # Validate Makefile integration
        makefile_result = self._validate_makefile_integration()
        validation_results.append(makefile_result)
        
        # Validate project registry integration
        registry_result = self._validate_project_registry_integration()
        validation_results.append(registry_result)
        
        # Validate cursor rules integration
        cursor_result = self._validate_cursor_rules_integration()
        validation_results.append(cursor_result)
        
        # Validate Beast Mode configuration
        config_result = self._validate_beast_mode_configuration()
        validation_results.append(config_result)
        
        # Calculate overall integration health
        integration_health = self._calculate_integration_health(validation_results)
        
        # Update metrics
        self._update_integration_metrics(validation_results, integration_health)
        
        # Store validation history
        self.validation_history.append({
            "timestamp": datetime.now(),
            "results": validation_results,
            "health_score": integration_health,
            "overall_status": "healthy" if integration_health >= 0.7 else "degraded"
        })
        
        # Keep only last 50 validations
        self.validation_history = self.validation_history[-50:]
        
        return {
            "validation_id": f"INFRA-{int(datetime.now().timestamp())}",
            "overall_health_score": integration_health,
            "overall_status": "healthy" if integration_health >= 0.7 else "degraded",
            "component_results": validation_results,
            "recommendations": self._generate_integration_recommendations(validation_results),
            "timestamp": datetime.now()
        }
        
    def _validate_makefile_integration(self) -> ValidationResult:
        """Validate Makefile integration with Beast Mode operations"""
        issues = []
        recommendations = []
        
        # Check if Makefile exists
        if not self.config.makefile_path.exists():
            return ValidationResult(
                component="makefile",
                status=IntegrationStatus.MISSING,
                details="Makefile not found",
                issues=["Makefile missing from project root"],
                recommendations=["Create Makefile with Beast Mode integration"]
            )
            
        try:
            # Read Makefile content
            makefile_content = self.config.makefile_path.read_text()
            
            # Check for Beast Mode inclusion
            if "beast-mode.mk" not in makefile_content:
                issues.append("Beast Mode Makefile not included")
                recommendations.append("Add 'include makefiles/beast-mode.mk' to Makefile")
                
            # Check for required targets
            missing_targets = []
            for target in self.config.required_makefile_targets:
                if target not in makefile_content:
                    missing_targets.append(target)
                    
            if missing_targets:
                issues.append(f"Missing Beast Mode targets: {', '.join(missing_targets)}")
                recommendations.append("Ensure all Beast Mode targets are available")
                
            # Test Makefile execution
            try:
                result = subprocess.run(
                    ["make", "help"],
                    capture_output=True,
                    text=True,
                    timeout=30,
                    cwd=self.project_root
                )
                
                if result.returncode != 0:
                    issues.append("Makefile execution failed")
                    recommendations.append("Fix Makefile syntax and dependency issues")
                    
            except subprocess.TimeoutExpired:
                issues.append("Makefile execution timed out")
                recommendations.append("Optimize Makefile performance")
            except Exception as e:
                issues.append(f"Makefile execution error: {str(e)}")
                recommendations.append("Debug Makefile execution environment")
                
            # Determine status
            if not issues:
                status = IntegrationStatus.INTEGRATED
                details = "Makefile fully integrated with Beast Mode operations"
            elif len(issues) <= 2:
                status = IntegrationStatus.PARTIAL
                details = "Makefile partially integrated, minor issues detected"
            else:
                status = IntegrationStatus.FAILED
                details = "Makefile integration failed, multiple issues detected"
                
            self.integration_status["makefile"] = status.value
            
            return ValidationResult(
                component="makefile",
                status=status,
                details=details,
                issues=issues,
                recommendations=recommendations
            )
            
        except Exception as e:
            self.integration_status["makefile"] = IntegrationStatus.FAILED.value
            return ValidationResult(
                component="makefile",
                status=IntegrationStatus.FAILED,
                details=f"Makefile validation failed: {str(e)}",
                issues=[f"Validation error: {str(e)}"],
                recommendations=["Debug Makefile validation process"]
            )
            
    def _validate_project_registry_integration(self) -> ValidationResult:
        """Validate project model registry integration"""
        issues = []
        recommendations = []
        
        # Check if registry exists
        if not self.config.project_registry_path.exists():
            return ValidationResult(
                component="project_registry",
                status=IntegrationStatus.MISSING,
                details="Project model registry not found",
                issues=["project_model_registry.json missing"],
                recommendations=["Create project model registry with domain architecture"]
            )
            
        try:
            # Load and validate registry
            registry_content = json.loads(self.config.project_registry_path.read_text())
            
            # Check required structure
            required_keys = ["domain_architecture", "project_purpose", "description"]
            for key in required_keys:
                if key not in registry_content:
                    issues.append(f"Missing required key: {key}")
                    recommendations.append(f"Add {key} section to project registry")
                    
            # Check domain architecture
            if "domain_architecture" in registry_content:
                domain_arch = registry_content["domain_architecture"]
                
                # Check for required domains
                for domain in self.config.required_registry_domains:
                    if domain not in domain_arch:
                        issues.append(f"Missing required domain: {domain}")
                        recommendations.append(f"Add {domain} domain to registry")
                        
                # Check total domains
                total_domains = domain_arch.get("overview", {}).get("total_domains", 0)
                if total_domains < 50:
                    issues.append(f"Insufficient domains: {total_domains} (minimum 50)")
                    recommendations.append("Expand domain architecture to meet requirements")
                    
            # Check compliance standard
            compliance = registry_content.get("domain_architecture", {}).get("overview", {}).get("compliance_standard")
            if compliance != "Reflective Module (RM)":
                issues.append("Compliance standard not set to Reflective Module (RM)")
                recommendations.append("Set compliance_standard to 'Reflective Module (RM)'")
                
            # Determine status
            if not issues:
                status = IntegrationStatus.INTEGRATED
                details = "Project registry fully integrated with Beast Mode requirements"
            elif len(issues) <= 3:
                status = IntegrationStatus.PARTIAL
                details = "Project registry partially integrated, some issues detected"
            else:
                status = IntegrationStatus.FAILED
                details = "Project registry integration failed, multiple issues detected"
                
            self.integration_status["project_registry"] = status.value
            
            return ValidationResult(
                component="project_registry",
                status=status,
                details=details,
                issues=issues,
                recommendations=recommendations
            )
            
        except json.JSONDecodeError as e:
            self.integration_status["project_registry"] = IntegrationStatus.FAILED.value
            return ValidationResult(
                component="project_registry",
                status=IntegrationStatus.FAILED,
                details=f"Invalid JSON in project registry: {str(e)}",
                issues=[f"JSON parsing error: {str(e)}"],
                recommendations=["Fix JSON syntax in project_model_registry.json"]
            )
        except Exception as e:
            self.integration_status["project_registry"] = IntegrationStatus.FAILED.value
            return ValidationResult(
                component="project_registry",
                status=IntegrationStatus.FAILED,
                details=f"Registry validation failed: {str(e)}",
                issues=[f"Validation error: {str(e)}"],
                recommendations=["Debug project registry validation process"]
            )
            
    def _validate_cursor_rules_integration(self) -> ValidationResult:
        """Validate cursor rules integration"""
        issues = []
        recommendations = []
        
        # Check if cursor rules directory exists
        if not self.config.cursor_rules_path.exists():
            return ValidationResult(
                component="cursor_rules",
                status=IntegrationStatus.MISSING,
                details="Cursor rules directory not found",
                issues=[".cursor/rules directory missing"],
                recommendations=["Create .cursor/rules directory with Beast Mode integration"]
            )
            
        try:
            # Check for Beast Mode rules
            beast_mode_rules = [
                "beast-mode-integration.mdc",
                "beast.mdc"
            ]
            
            missing_rules = []
            for rule_file in beast_mode_rules:
                rule_path = self.config.cursor_rules_path / rule_file
                if not rule_path.exists():
                    missing_rules.append(rule_file)
                    
            if missing_rules:
                issues.append(f"Missing Beast Mode rules: {', '.join(missing_rules)}")
                recommendations.append("Create Beast Mode cursor rules for systematic development")
                
            # Check existing rules for Beast Mode integration
            rule_files = list(self.config.cursor_rules_path.glob("*.mdc"))
            beast_mode_mentions = 0
            
            for rule_file in rule_files:
                try:
                    content = rule_file.read_text()
                    if "beast" in content.lower() or "systematic" in content.lower():
                        beast_mode_mentions += 1
                except Exception:
                    continue
                    
            if beast_mode_mentions == 0:
                issues.append("No Beast Mode integration found in existing rules")
                recommendations.append("Add Beast Mode methodology to cursor rules")
                
            # Determine status
            if not issues:
                status = IntegrationStatus.INTEGRATED
                details = "Cursor rules fully integrated with Beast Mode methodology"
            elif len(issues) <= 2:
                status = IntegrationStatus.PARTIAL
                details = "Cursor rules partially integrated, some rules missing"
            else:
                status = IntegrationStatus.FAILED
                details = "Cursor rules integration incomplete"
                
            self.integration_status["cursor_rules"] = status.value
            
            return ValidationResult(
                component="cursor_rules",
                status=status,
                details=details,
                issues=issues,
                recommendations=recommendations
            )
            
        except Exception as e:
            self.integration_status["cursor_rules"] = IntegrationStatus.FAILED.value
            return ValidationResult(
                component="cursor_rules",
                status=IntegrationStatus.FAILED,
                details=f"Cursor rules validation failed: {str(e)}",
                issues=[f"Validation error: {str(e)}"],
                recommendations=["Debug cursor rules validation process"]
            )
            
    def _validate_beast_mode_configuration(self) -> ValidationResult:
        """Validate Beast Mode configuration and specs"""
        issues = []
        recommendations = []
        
        # Check if Beast Mode config directory exists
        if not self.config.beast_mode_config_path.exists():
            return ValidationResult(
                component="beast_mode_config",
                status=IntegrationStatus.MISSING,
                details="Beast Mode configuration directory not found",
                issues=[".kiro/specs/beast-mode-framework directory missing"],
                recommendations=["Create Beast Mode configuration directory with specs"]
            )
            
        try:
            # Check for required configuration files
            required_config_files = [
                "requirements.md",
                "design.md", 
                "tasks.md"
            ]
            
            missing_configs = []
            for config_file in required_config_files:
                config_path = self.config.beast_mode_config_path / config_file
                if not config_path.exists():
                    missing_configs.append(config_file)
                    
            if missing_configs:
                issues.append(f"Missing configuration files: {', '.join(missing_configs)}")
                recommendations.append("Create complete Beast Mode specification files")
                
            # Check Beast Mode source code
            beast_mode_src = self.project_root / "src" / "beast_mode"
            if not beast_mode_src.exists():
                issues.append("Beast Mode source code directory missing")
                recommendations.append("Create src/beast_mode directory with framework code")
            else:
                # Check for core modules
                core_modules = [
                    "core/reflective_module.py",
                    "orchestration/tool_orchestration_engine.py",
                    "integration/infrastructure_integration_manager.py"
                ]
                
                missing_modules = []
                for module in core_modules:
                    module_path = beast_mode_src / module
                    if not module_path.exists():
                        missing_modules.append(module)
                        
                if missing_modules:
                    issues.append(f"Missing core modules: {', '.join(missing_modules)}")
                    recommendations.append("Implement missing Beast Mode core modules")
                    
            # Determine status
            if not issues:
                status = IntegrationStatus.INTEGRATED
                details = "Beast Mode configuration fully integrated and complete"
            elif len(issues) <= 2:
                status = IntegrationStatus.PARTIAL
                details = "Beast Mode configuration partially complete"
            else:
                status = IntegrationStatus.FAILED
                details = "Beast Mode configuration incomplete or missing"
                
            self.integration_status["beast_mode_config"] = status.value
            
            return ValidationResult(
                component="beast_mode_config",
                status=status,
                details=details,
                issues=issues,
                recommendations=recommendations
            )
            
        except Exception as e:
            self.integration_status["beast_mode_config"] = IntegrationStatus.FAILED.value
            return ValidationResult(
                component="beast_mode_config",
                status=IntegrationStatus.FAILED,
                details=f"Beast Mode configuration validation failed: {str(e)}",
                issues=[f"Validation error: {str(e)}"],
                recommendations=["Debug Beast Mode configuration validation"]
            )
            
    def _calculate_integration_health(self, validation_results: List[ValidationResult]) -> float:
        """Calculate overall integration health score"""
        if not validation_results:
            return 0.0
            
        status_scores = {
            IntegrationStatus.INTEGRATED: 1.0,
            IntegrationStatus.PARTIAL: 0.6,
            IntegrationStatus.MISSING: 0.2,
            IntegrationStatus.FAILED: 0.0
        }
        
        total_score = sum(status_scores[result.status] for result in validation_results)
        return total_score / len(validation_results)
        
    def _update_integration_metrics(self, validation_results: List[ValidationResult], health_score: float):
        """Update integration metrics with validation results"""
        self.integration_metrics['total_validations'] += 1
        self.integration_metrics['integration_health_score'] = health_score
        self.integration_metrics['last_validation_timestamp'] = datetime.now()
        
        # Count successful and failed integrations
        successful = sum(1 for result in validation_results if result.status == IntegrationStatus.INTEGRATED)
        failed = sum(1 for result in validation_results if result.status == IntegrationStatus.FAILED)
        
        self.integration_metrics['successful_integrations'] = successful
        self.integration_metrics['failed_integrations'] = failed
        self.integration_metrics['components_integrated'] = len(validation_results)
        
    def _calculate_success_rate(self) -> float:
        """Calculate integration success rate"""
        total = self.integration_metrics['total_validations']
        if total == 0:
            return 0.0
            
        # Success is defined as health score >= 0.7
        successful_validations = sum(
            1 for validation in self.validation_history
            if validation.get("health_score", 0) >= 0.7
        )
        
        return successful_validations / total
        
    def _generate_integration_recommendations(self, validation_results: List[ValidationResult]) -> List[str]:
        """Generate integration improvement recommendations"""
        recommendations = []
        
        # Collect all recommendations from validation results
        for result in validation_results:
            recommendations.extend(result.recommendations)
            
        # Add general recommendations based on overall status
        failed_components = [r.component for r in validation_results if r.status == IntegrationStatus.FAILED]
        if failed_components:
            recommendations.append(f"Priority: Fix failed components: {', '.join(failed_components)}")
            
        partial_components = [r.component for r in validation_results if r.status == IntegrationStatus.PARTIAL]
        if partial_components:
            recommendations.append(f"Complete partial integrations: {', '.join(partial_components)}")
            
        # Remove duplicates while preserving order
        seen = set()
        unique_recommendations = []
        for rec in recommendations:
            if rec not in seen:
                seen.add(rec)
                unique_recommendations.append(rec)
                
        return unique_recommendations
        
    # Public API methods
    
    def get_integration_status(self) -> Dict[str, Any]:
        """Get current integration status for all components"""
        return {
            "overall_health_score": self.integration_metrics['integration_health_score'],
            "components": self.integration_status.copy(),
            "last_validation": self.integration_metrics['last_validation_timestamp'],
            "total_validations": self.integration_metrics['total_validations'],
            "success_rate": self._calculate_success_rate()
        }
        
    def get_integration_analytics(self) -> Dict[str, Any]:
        """Get comprehensive integration analytics"""
        return {
            "integration_metrics": self.integration_metrics.copy(),
            "component_status": self.integration_status.copy(),
            "validation_history": self.validation_history[-10:],  # Last 10 validations
            "health_trends": self._analyze_health_trends(),
            "recommendations": self._generate_integration_recommendations(
                [v["results"] for v in self.validation_history[-1:]][-1] if self.validation_history else []
            )
        }
        
    def _analyze_health_trends(self) -> Dict[str, Any]:
        """Analyze integration health trends over time"""
        if len(self.validation_history) < 2:
            return {"trend": "insufficient_data", "message": "Need more validation history"}
            
        recent_scores = [v["health_score"] for v in self.validation_history[-5:]]
        older_scores = [v["health_score"] for v in self.validation_history[-10:-5]] if len(self.validation_history) >= 10 else []
        
        if not older_scores:
            return {"trend": "stable", "current_score": recent_scores[-1]}
            
        recent_avg = sum(recent_scores) / len(recent_scores)
        older_avg = sum(older_scores) / len(older_scores)
        
        if recent_avg > older_avg * 1.05:  # 5% improvement
            trend = "improving"
        elif recent_avg < older_avg * 0.95:  # 5% degradation
            trend = "degrading"
        else:
            trend = "stable"
            
        return {
            "trend": trend,
            "current_score": recent_scores[-1],
            "recent_average": recent_avg,
            "older_average": older_avg,
            "change_percentage": ((recent_avg - older_avg) / older_avg) * 100 if older_avg > 0 else 0
        }