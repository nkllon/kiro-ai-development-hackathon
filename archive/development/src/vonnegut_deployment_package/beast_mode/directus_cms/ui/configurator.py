"""
UI Configurator - Systematic Directus Interface Configuration

Single Responsibility: Orchestrate UI configuration components for optimal UX.
Maintains <250 lines through delegation to focused components.

Requirements Addressed:
- 6.1: User Interface Excellence with Relationship Management
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

from .relationship_display import RelationshipDisplayManager
from .navigation import NavigationManager


class UIConfigurator(ReflectiveModule):
    """
    Systematic UI configuration orchestrator
    
    Delegates to specialized components for focused functionality.
    Maintains <250 lines through composition pattern.
    """
    
    def __init__(self, directus_client=None):
        """Initialize with component dependencies"""
        super().__init__()
        
        self.module_id = "ui_configurator"
        self.directus_client = directus_client
        
        # Initialize focused components
        self.relationship_display = RelationshipDisplayManager(directus_client)
        self.navigation = NavigationManager(directus_client)
        
        self._configuration_status = {}
    
    def get_module_info(self) -> Dict[str, Any]:
        """Get module information - ReflectiveModule implementation"""
        return {
            "module_id": self.module_id,
            "module_name": "UIConfigurator",
            "version": "1.0.0",
            "pattern": "orchestrator_delegation",
            "components": ["relationship_display", "navigation"],
            "focus": "ui_coordination_only"
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
        display_health = self.relationship_display.get_health_status()
        nav_health = self.navigation.get_health_status()
        
        # Simple aggregation logic
        overall_status = ModuleStatus.HEALTHY
        issues = []
        
        if display_health.status != ModuleStatus.HEALTHY:
            overall_status = display_health.status
            issues.extend(display_health.issues)
        
        if nav_health.status != ModuleStatus.HEALTHY:
            if overall_status == ModuleStatus.HEALTHY:
                overall_status = nav_health.status
            issues.extend(nav_health.issues)
        
        overall_score = min(display_health.health_score, nav_health.health_score)
        
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
        display_degradation = self.relationship_display.graceful_degradation()
        nav_degradation = self.navigation.graceful_degradation()
        
        if display_degradation.success and nav_degradation.success:
            # Combine degraded capabilities
            degraded = list(set(display_degradation.degraded_capabilities + nav_degradation.degraded_capabilities))
            remaining = list(set(display_degradation.remaining_capabilities) & set(nav_degradation.remaining_capabilities))
            
            return GracefulDegradationResult(
                success=True,
                degraded_capabilities=degraded,
                remaining_capabilities=remaining
            )
        
        return GracefulDegradationResult(
            success=False,
            degraded_capabilities=self.get_capabilities(),
            remaining_capabilities=[],
            error_message="Component degradation failed"
        )
    
    def configure_all_ui_components(self) -> Dict[str, Any]:
        """
        Configure complete UI using PDCA methodology
        
        Returns:
            Comprehensive configuration result
        """
        with self.trace_operation("configure_all_ui_components") as trace:
            try:
                results = {}
                
                # PLAN: Define configuration sequence
                config_steps = [
                    ("relationship_displays", self._configure_relationship_displays),
                    ("navigation", self._configure_navigation),
                    ("search_filtering", self._configure_search_filtering)
                ]
                
                # DO: Execute each configuration step
                for step_name, step_function in config_steps:
                    step_result = step_function()
                    results[step_name] = step_result
                    
                    # CHECK: Validate step success
                    if not step_result.get("success", False):
                        self._logger.error(f"UI config step {step_name} failed: {step_result}")
                        break
                
                # ACT: Determine overall success
                overall_success = all(r.get("success", False) for r in results.values())
                
                final_result = {
                    "success": overall_success,
                    "configured_components": len(results),
                    "configuration_results": results,
                    "message": "UI configuration completed" if overall_success else "UI configuration failed"
                }
                
                trace.output_result = final_result
                return final_result
                
            except Exception as e:
                self._increment_error_count()
                error_result = {
                    "success": False,
                    "error": str(e),
                    "message": f"UI configuration failed: {e}"
                }
                
                trace.error_info = {"error": str(e)}
                return error_result
    
    def _configure_relationship_displays(self) -> Dict[str, Any]:
        """Delegate relationship display configuration"""
        try:
            return self.relationship_display.configure_all_displays()
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": f"Relationship display configuration failed: {e}"
            }
    
    def _configure_navigation(self) -> Dict[str, Any]:
        """Delegate navigation configuration"""
        try:
            return self.navigation.configure_navigation_system()
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": f"Navigation configuration failed: {e}"
            }
    
    def _configure_search_filtering(self) -> Dict[str, Any]:
        """Configure search and filtering capabilities"""
        try:
            # Delegate to both components for comprehensive search
            display_search = self.relationship_display.configure_search_filters()
            nav_search = self.navigation.configure_search_navigation()
            
            return {
                "success": display_search.get("success", False) and nav_search.get("success", False),
                "display_search": display_search,
                "navigation_search": nav_search,
                "message": "Search and filtering configured"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": f"Search configuration failed: {e}"
            }
    
    def get_configuration_status(self) -> Dict[str, Any]:
        """Get comprehensive UI configuration status"""
        return {
            "configurator_status": self.get_health_status().status.value,
            "relationship_display_status": self.relationship_display.get_health_status().status.value,
            "navigation_status": self.navigation.get_health_status().status.value,
            "configuration_results": self._configuration_status,
            "last_updated": datetime.now().isoformat()
        }
    
    def validate_ui_functionality(self) -> Dict[str, Any]:
        """Validate all UI functionality works correctly"""
        try:
            validation_results = {}
            
            # Validate relationship displays
            display_validation = self.relationship_display.validate_displays()
            validation_results["relationship_displays"] = display_validation
            
            # Validate navigation
            nav_validation = self.navigation.validate_navigation()
            validation_results["navigation"] = nav_validation
            
            overall_success = all(r.get("success", False) for r in validation_results.values())
            
            return {
                "success": overall_success,
                "validation_results": validation_results,
                "message": "UI validation completed" if overall_success else "UI validation found issues"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": f"UI validation failed: {e}"
            }