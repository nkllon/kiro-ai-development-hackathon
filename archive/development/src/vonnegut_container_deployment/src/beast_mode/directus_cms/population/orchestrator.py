"""
Data Population Orchestrator - Coordination Component

Single Responsibility: Coordinate smaller, focused components for data population.
Maintains <200 lines through delegation pattern.

Requirements Addressed:
- 2.1: Orchestrate systematic data population
- 9.1: Beast Mode integration with PDCA methodology
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

from .spec_importer import SpecificationImporter, ImportResult


class DataPopulationOrchestrator(ReflectiveModule):
    """
    Lightweight orchestrator that coordinates focused components
    
    Delegates to specialized components instead of implementing everything.
    Maintains <200 lines through composition over inheritance.
    """
    
    def __init__(self, schema_manager, repository_root: str = "."):
        """Initialize with component dependencies"""
        super().__init__()
        
        self.module_id = "data_population_orchestrator"
        self.schema_manager = schema_manager
        
        # Initialize focused components
        self.spec_importer = SpecificationImporter(schema_manager, repository_root)
        # TODO: Add other components as they're created
        # self.document_importer = DocumentImporter(schema_manager, repository_root)
        # self.code_linker = CodeFileLinker(schema_manager, repository_root)
        # self.validator = RelationshipValidator(schema_manager)
        
        self._operation_results = {}
    
    def get_module_info(self) -> Dict[str, Any]:
        """Get module information - ReflectiveModule implementation"""
        return {
            "module_id": self.module_id,
            "module_name": "DataPopulationOrchestrator",
            "version": "1.0.0",
            "pattern": "orchestrator_delegation",
            "components": ["spec_importer"],  # TODO: Add others
            "focus": "coordination_only"
        }
    
    def get_capabilities(self) -> List[ModuleCapability]:
        """Get module capabilities - ReflectiveModule implementation"""
        return [
            ModuleCapability.CORE_FUNCTIONALITY,
            ModuleCapability.DATA_PROCESSING
        ]
    
    def get_health_status(self) -> ModuleHealth:
        """Get module health status - ReflectiveModule implementation"""
        # Aggregate health from components
        spec_health = self.spec_importer.get_health_status()
        
        # Simple aggregation logic
        overall_status = spec_health.status
        overall_score = spec_health.health_score
        issues = spec_health.issues.copy()
        
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
        spec_degradation = self.spec_importer.graceful_degradation()
        
        if spec_degradation.success:
            return GracefulDegradationResult(
                success=True,
                degraded_capabilities=spec_degradation.degraded_capabilities,
                remaining_capabilities=spec_degradation.remaining_capabilities
            )
        
        return GracefulDegradationResult(
            success=False,
            degraded_capabilities=self.get_capabilities(),
            remaining_capabilities=[],
            error_message="Component degradation failed"
        )
    
    def populate_all_data(self) -> Dict[str, Any]:
        """
        Orchestrate complete data population using PDCA methodology
        
        Returns:
            Comprehensive result from all components
        """
        with self.trace_operation("populate_all_data") as trace:
            try:
                results = {}
                
                # PLAN: Define execution sequence
                execution_plan = [
                    ("specifications", self._populate_specifications),
                    # TODO: Add other steps
                    # ("documents", self._populate_documents),
                    # ("code_files", self._link_code_files),
                    # ("validation", self._validate_relationships)
                ]
                
                # DO: Execute each step
                for step_name, step_function in execution_plan:
                    step_result = step_function()
                    results[step_name] = step_result
                    
                    # CHECK: Validate step success
                    if not step_result.get("success", False):
                        self._logger.error(f"Step {step_name} failed: {step_result}")
                        break
                
                # ACT: Determine overall success
                overall_success = all(r.get("success", False) for r in results.values())
                
                final_result = {
                    "success": overall_success,
                    "steps_completed": len(results),
                    "step_results": results,
                    "message": "Data population completed" if overall_success else "Data population failed"
                }
                
                trace.output_result = final_result
                return final_result
                
            except Exception as e:
                self._increment_error_count()
                error_result = {
                    "success": False,
                    "error": str(e),
                    "message": f"Population orchestration failed: {e}"
                }
                
                trace.error_info = {"error": str(e)}
                return error_result
    
    def _populate_specifications(self) -> Dict[str, Any]:
        """Delegate specification population to focused component"""
        try:
            import_result = self.spec_importer.import_specifications()
            
            return {
                "success": import_result.success,
                "imported_specs": import_result.imported_specs,
                "spec_ids": import_result.spec_ids,
                "errors": import_result.errors,
                "message": import_result.message
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": f"Specification import failed: {e}"
            }
    
    def get_population_status(self) -> Dict[str, Any]:
        """Get comprehensive population status from all components"""
        return {
            "orchestrator_status": self.get_health_status().status.value,
            "spec_importer_status": self.spec_importer.get_health_status().status.value,
            "imported_specs": self.spec_importer.get_imported_spec_ids(),
            "operation_results": self._operation_results,
            "last_updated": datetime.now().isoformat()
        }
    
    def cleanup_all_data(self) -> Dict[str, Any]:
        """Cleanup all imported data using component rollback capabilities"""
        try:
            cleanup_results = {}
            
            # Cleanup specifications
            spec_cleanup = self.spec_importer.cleanup_imported_specs()
            cleanup_results["specifications"] = spec_cleanup
            
            # TODO: Add cleanup for other components
            
            overall_success = all(cleanup_results.values())
            
            return {
                "success": overall_success,
                "cleanup_results": cleanup_results,
                "message": "Cleanup completed" if overall_success else "Cleanup had issues"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": f"Cleanup failed: {e}"
            }