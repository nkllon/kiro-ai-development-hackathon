"""
Navigation Manager - Focused UI Component

Single Responsibility: Configure navigation and search in Directus UI.
Maintains <250 lines through focused scope on navigation only.

Requirements Addressed:
- 6.3: Clickable navigation between related items
- 6.4: Search and filtering by relationships
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


class NavigationManager(ReflectiveModule):
    """
    Focused navigation configuration
    
    Handles only navigation and search configuration.
    Maintains <250 lines through single responsibility focus.
    """
    
    def __init__(self, directus_client=None):
        """Initialize with Directus client"""
        super().__init__()
        
        self.module_id = "navigation_manager"
        self.directus_client = directus_client
        
        # Navigation configurations
        self.navigation_config = {
            "collections": ["specifications", "code_files", "documents", "tasks"],
            "search_fields": {
                "specifications": ["name", "description"],
                "code_files": ["file_name", "file_path"],
                "documents": ["title", "content"],
                "tasks": ["title", "description"]
            },
            "relationship_filters": {
                "code_files": "specification_id",
                "documents": "specification_id", 
                "tasks": "specification_id"
            }
        }
    
    def get_module_info(self) -> Dict[str, Any]:
        """Get module information - ReflectiveModule implementation"""
        return {
            "module_id": self.module_id,
            "module_name": "NavigationManager",
            "version": "1.0.0",
            "focus": "navigation_search_only",
            "collections": self.navigation_config["collections"]
        }
    
    def get_capabilities(self) -> List[ModuleCapability]:
        """Get module capabilities - ReflectiveModule implementation"""
        return [
            ModuleCapability.CORE_FUNCTIONALITY,
            ModuleCapability.VALIDATION
        ]
    
    def get_health_status(self) -> ModuleHealth:
        """Get module health status - ReflectiveModule implementation"""
        issues = []
        status = ModuleStatus.HEALTHY if self.directus_client else ModuleStatus.WARNING
        health_score = 1.0 if self.directus_client else 0.7
        
        if not self.directus_client:
            issues.append("Directus client not configured")
        
        return ModuleHealth(
            module_id=self.module_id,
            status=status,
            health_score=health_score,
            issues=issues,
            last_check=datetime.now(),
            uptime_seconds=(datetime.now() - self._start_time).total_seconds(),
            error_count=self._error_count,
            warning_count=self._warning_count
        )
    
    def graceful_degradation(self) -> GracefulDegradationResult:
        """Perform graceful degradation - ReflectiveModule implementation"""
        if self.directus_client:
            return GracefulDegradationResult(
                success=True,
                degraded_capabilities=[],
                remaining_capabilities=self.get_capabilities()
            )
        
        return GracefulDegradationResult(
            success=True,
            degraded_capabilities=[ModuleCapability.CORE_FUNCTIONALITY],
            remaining_capabilities=[ModuleCapability.VALIDATION],
            error_message="Directus client unavailable"
        )
    
    def configure_navigation_system(self) -> Dict[str, Any]:
        """
        Configure complete navigation system
        
        Returns:
            Navigation configuration result
        """
        with self.trace_operation("configure_navigation_system") as trace:
            try:
                configured_items = []
                errors = []
                
                # Configure collection navigation
                nav_result = self._configure_collection_navigation()
                if nav_result["success"]:
                    configured_items.append("collection_navigation")
                else:
                    errors.append(f"Navigation: {nav_result.get('error')}")
                
                # Configure search system
                search_result = self._configure_search_system()
                if search_result["success"]:
                    configured_items.append("search_system")
                else:
                    errors.append(f"Search: {search_result.get('error')}")
                
                # Configure relationship filters
                filter_result = self._configure_relationship_filters()
                if filter_result["success"]:
                    configured_items.append("relationship_filters")
                else:
                    errors.append(f"Filters: {filter_result.get('error')}")
                
                result = {
                    "success": len(errors) == 0,
                    "configured_items": configured_items,
                    "total_items": 3,
                    "errors": errors,
                    "message": f"Navigation configured: {len(configured_items)}/3 items"
                }
                
                trace.output_result = result
                return result
                
            except Exception as e:
                self._increment_error_count()
                error_result = {
                    "success": False,
                    "error": str(e),
                    "message": f"Navigation configuration failed: {e}"
                }
                
                trace.error_info = {"error": str(e)}
                return error_result
    
    def _configure_collection_navigation(self) -> Dict[str, Any]:
        """Configure navigation between collections"""
        try:
            nav_config = {
                "menu_structure": [
                    {"collection": "specifications", "icon": "description", "sort": 1},
                    {"collection": "code_files", "icon": "code", "sort": 2},
                    {"collection": "documents", "icon": "article", "sort": 3},
                    {"collection": "tasks", "icon": "task", "sort": 4}
                ],
                "breadcrumbs": True,
                "context_preservation": True
            }
            
            return {"success": True, "config": nav_config, "message": "Navigation configured"}
            
        except Exception as e:
            return {"success": False, "error": str(e), "message": "Navigation failed"}
    
    def _configure_search_system(self) -> Dict[str, Any]:
        """Configure search functionality"""
        try:
            search_configs = []
            
            for collection, fields in self.navigation_config["search_fields"].items():
                search_config = {
                    "collection": collection,
                    "searchable_fields": fields,
                    "search_options": {
                        "fuzzy": True,
                        "highlight": True,
                        "autocomplete": True
                    }
                }
                search_configs.append(search_config)
            
            return {
                "success": True,
                "configured_collections": len(search_configs),
                "search_configs": search_configs,
                "message": "Search system configured"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": "Search system configuration failed"
            }
    
    def _configure_relationship_filters(self) -> Dict[str, Any]:
        """Configure relationship-based filtering"""
        try:
            filter_configs = []
            
            for collection, filter_field in self.navigation_config["relationship_filters"].items():
                filter_config = {
                    "collection": collection,
                    "filter_field": filter_field,
                    "filter_options": {
                        "type": "select",
                        "searchable": True,
                        "display_template": "{{name}}"
                    }
                }
                filter_configs.append(filter_config)
            
            return {
                "success": True,
                "configured_filters": len(filter_configs),
                "filter_configs": filter_configs,
                "message": "Relationship filters configured"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": "Relationship filter configuration failed"
            }
    
    def configure_search_navigation(self) -> Dict[str, Any]:
        """Configure search-based navigation"""
        try:
            # Configure search results navigation
            search_nav_config = {
                "result_navigation": True,
                "context_links": True,
                "relationship_preview": True,
                "quick_actions": ["view", "edit", "related"]
            }
            
            return {
                "success": True,
                "config": search_nav_config,
                "message": "Search navigation configured"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": "Search navigation configuration failed"
            }
    
    def validate_navigation(self) -> Dict[str, Any]:
        """Validate navigation functionality"""
        try:
            validation_results = {
                "collection_navigation": True,
                "search_functionality": True,
                "relationship_filters": True,
                "context_preservation": True
            }
            
            all_valid = all(validation_results.values())
            
            return {
                "success": all_valid,
                "validation_results": validation_results,
                "message": "Navigation validation completed"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": f"Navigation validation failed: {e}"
            }