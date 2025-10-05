"""
Error Prevention Orchestrator - Systematic Error Management

Single Responsibility: Orchestrate focused error prevention components.
Maintains <200 lines through delegation to specialized validators.

Requirements Addressed:
- 4.1-4.5: Comprehensive error prevention and recovery
- 11.2: Single responsibility principle enforcement
"""

from datetime import datetime
from typing import Dict, Any, List, Optional

from src.rm_ddd.core.unified_reflective_module import (
    ReflectiveModule,
    ModuleHealth,
    ModuleStatus,
    ModuleCapability,
    GracefulDegradationResult,
)

from .auth_validator import AuthenticationValidator
from .schema_validator import SchemaConsistencyValidator
from .api_handler import APIErrorHandler


class ErrorPreventionOrchestrator(ReflectiveModule):
    """
    Systematic error prevention orchestrator
    
    Delegates to specialized validators for focused error prevention.
    Maintains <200 lines through composition pattern.
    """
    
    def __init__(self, schema_manager=None, directus_client=None):
        """Initialize with component dependencies"""
        super().__init__()
        
        self.module_id = "error_prevention_orchestrator"
        
        # Initialize focused components
        self.auth_validator = AuthenticationValidator(directus_client)
        self.schema_validator = SchemaConsistencyValidator(schema_manager)
        self.api_handler = APIErrorHandler(directus_client)
        
        self._prevention_results = {}
    
    def get_module_info(self) -> Dict[str, Any]:
        """Get module information - ReflectiveModule implementation"""
        return {
            "module_id": self.module_id,
            "module_name": "ErrorPreventionOrchestrator",
            "version": "1.0.0",
            "pattern": "orchestrator_delegation",
            "components": ["auth_validator", "schema_validator", "api_handler"],
            "focus": "error_prevention_coordination"
        }
    
    def get_capabilities(self) -> List[ModuleCapability]:
        """Get module capabilities - ReflectiveModule implementation"""
        return [
            ModuleCapability.CORE_FUNCTIONALITY,
            ModuleCapability.VALIDATION
        ]
    
    def get_health_status(self) -> ModuleHealth:
        """Get module health status - ReflectiveModule implementation"""
        # Aggregate health from components
        auth_health = self.auth_validator.get_health_status()
        schema_health = self.schema_validator.get_health_status()
        api_health = self.api_handler.get_health_status()
        
        # Simple aggregation logic
        healths = [auth_health, schema_health, api_health]
        overall_status = min(h.status for h in healths)
        overall_score = min(h.health_score for h in healths)
        
        issues = []
        for health in healths:
            issues.extend(health.issues)
        
        return ModuleHealth(
            module_id=self.module_id,
            status=overall_status,
            health_score=overall_score,
            issues=issues,
            last_check=datetime.now(),
            uptime_seconds=(datetime.now() - self._start_time).total_seconds(),
            error_count=self._error_count,
            warning_count=self._warning_count
        )
    
    def graceful_degradation(self) -> GracefulDegradationResult:
        """Perform graceful degradation - ReflectiveModule implementation"""
        # Delegate to components
        degradations = [
            self.auth_validator.graceful_degradation(),
            self.schema_validator.graceful_degradation(),
            self.api_handler.graceful_degradation()
        ]
        
        if all(d.success for d in degradations):
            # Combine degraded capabilities
            all_degraded = []
            all_remaining = []
            
            for d in degradations:
                all_degraded.extend(d.degraded_capabilities)
                all_remaining.extend(d.remaining_capabilities)
            
            return GracefulDegradationResult(
                success=True,
                degraded_capabilities=list(set(all_degraded)),
                remaining_capabilities=list(set(all_remaining))
            )
        
        return GracefulDegradationResult(
            success=False,
            degraded_capabilities=self.get_capabilities(),
            remaining_capabilities=[],
            error_message="Component degradation failed"
        )
    
    def prevent_all_errors(self) -> Dict[str, Any]:
        """
        Execute comprehensive error prevention using PDCA methodology
        
        Returns:
            Comprehensive prevention result
        """
        with self.trace_operation("prevent_all_errors") as trace:
            try:
                results = {}
                
                # PLAN: Define prevention sequence
                prevention_steps = [
                    ("authentication", self._prevent_auth_errors),
                    ("schema_consistency", self._prevent_schema_errors),
                    ("api_errors", self._prevent_api_errors)
                ]
                
                # DO: Execute each prevention step
                for step_name, step_function in prevention_steps:
                    step_result = step_function()
                    results[step_name] = step_result
                    
                    # CHECK: Validate prevention success
                    if not step_result.get("success", False):
                        self._logger.warning(f"Error prevention step {step_name} had issues: {step_result}")
                
                # ACT: Determine overall prevention status
                overall_success = all(r.get("success", False) for r in results.values())
                
                final_result = {
                    "success": overall_success,
                    "prevention_steps": len(results),
                    "prevention_results": results,
                    "message": "Error prevention completed" if overall_success else "Error prevention had issues"
                }
                
                trace.output_result = final_result
                return final_result
                
            except Exception as e:
                self._increment_error_count()
                error_result = {
                    "success": False,
                    "error": str(e),
                    "message": f"Error prevention failed: {e}"
                }
                
                trace.error_info = {"error": str(e)}
                return error_result
    
    def _prevent_auth_errors(self) -> Dict[str, Any]:
        """Delegate authentication error prevention"""
        try:
            return self.auth_validator.validate_authentication_system()
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": f"Authentication error prevention failed: {e}"
            }
    
    def _prevent_schema_errors(self) -> Dict[str, Any]:
        """Delegate schema consistency error prevention"""
        try:
            return self.schema_validator.validate_schema_consistency()
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": f"Schema error prevention failed: {e}"
            }
    
    def _prevent_api_errors(self) -> Dict[str, Any]:
        """Delegate API error prevention"""
        try:
            return self.api_handler.configure_error_handling()
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": f"API error prevention failed: {e}"
            }