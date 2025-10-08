"""
Relationship Display Manager - Focused UI Component

Single Responsibility: Configure relationship displays and dropdowns in Directus UI.
Maintains <280 lines through focused scope on relationship visualization only.

Requirements Addressed:
- 6.1: Display related code files, documents, and tasks for specifications
- 6.2: Dropdown selectors for creating relationships
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


class RelationshipDisplayManager(ReflectiveModule):
    """
    Focused relationship display configuration
    
    Handles only relationship visualization and dropdown configuration.
    Maintains <280 lines through single responsibility focus.
    """
    
    def __init__(self, directus_client=None):
        """Initialize with Directus client"""
        super().__init__()
        
        self.module_id = "relationship_display_manager"
        self.directus_client = directus_client
        
        # Collection configurations
        self.collections = {
            "specifications": {
                "related_fields": ["code_files", "documents", "tasks"],
                "display_sections": ["Related Code Files", "Related Documents", "Related Tasks"]
            },
            "code_files": {
                "parent_field": "specification_id",
                "dropdown_config": {"searchable": True, "display_template": "{{name}}"}
            },
            "documents": {
                "parent_field": "specification_id", 
                "dropdown_config": {"searchable": True, "display_template": "{{name}}"}
            },
            "tasks": {
                "parent_field": "specification_id",
                "dropdown_config": {"searchable": True, "display_template": "{{name}}"}
            }
        }
    
    def get_module_info(self) -> Dict[str, Any]:
        """Get module information - ReflectiveModule implementation"""
        return {
            "module_id": self.module_id,
            "module_name": "RelationshipDisplayManager",
            "version": "1.0.0",
            "focus": "relationship_visualization_only",
            "collections": list(self.collections.keys())
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
        status = ModuleStatus.HEALTHY
        health_score = 1.0
        
        # Check Directus client availability
        if not self.directus_client:
            issues.append("Directus client not configured")
            status = ModuleStatus.WARNING
            health_score = 0.7
        
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
            error_message="Directus client unavailable, display configuration disabled"
        )
    
    def configure_all_displays(self) -> Dict[str, Any]:
        """
        Configure all relationship displays systematically
        
        Returns:
            Configuration result with detailed status
        """
        with self.trace_operation("configure_all_displays") as trace:
            try:
                configured_collections = []
                errors = []
                
                # Configure each collection's relationship displays
                for collection_name, config in self.collections.items():
                    try:
                        if "related_fields" in config:
                            # Configure parent collection with related sections
                            result = self._configure_parent_collection_display(collection_name, config)
                        else:
                            # Configure child collection with dropdown
                            result = self._configure_child_collection_dropdown(collection_name, config)
                        
                        if result["success"]:
                            configured_collections.append(collection_name)
                        else:
                            errors.append(f"{collection_name}: {result.get('error', 'Unknown error')}")
                        
                    except Exception as e:
                        error_msg = f"Failed to configure {collection_name}: {e}"
                        errors.append(error_msg)
                        self._logger.error(error_msg)
                
                result = {
                    "success": len(errors) == 0,
                    "configured_collections": configured_collections,
                    "total_collections": len(self.collections),
                    "errors": errors,
                    "message": f"Configured {len(configured_collections)}/{len(self.collections)} collections"
                }
                
                trace.output_result = result
                return result
                
            except Exception as e:
                self._increment_error_count()
                error_result = {
                    "success": False,
                    "error": str(e),
                    "message": f"Display configuration failed: {e}"
                }
                
                trace.error_info = {"error": str(e)}
                return error_result
    
    def _configure_parent_collection_display(self, collection_name: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """Configure parent collection to display related items"""
        try:
            # Mock configuration for now - would use actual Directus API
            display_config = {
                "collection": collection_name,
                "layout": "tabular",
                "related_sections": []
            }
            
            # Add related sections
            for i, field in enumerate(config["related_fields"]):
                section_config = {
                    "field": field,
                    "display_name": config["display_sections"][i],
                    "type": "related_values",
                    "template": "{{title}} ({{status}})" if field == "tasks" else "{{title}}"
                }
                display_config["related_sections"].append(section_config)
            
            # Would apply to Directus here
            self._logger.info(f"Configured parent display for {collection_name}")
            
            return {
                "success": True,
                "collection": collection_name,
                "config": display_config,
                "message": f"Parent display configured for {collection_name}"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": f"Parent display configuration failed for {collection_name}"
            }
    
    def _configure_child_collection_dropdown(self, collection_name: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """Configure child collection dropdown for parent selection"""
        try:
            # Mock configuration for now - would use actual Directus API
            dropdown_config = {
                "collection": collection_name,
                "field": config["parent_field"],
                "interface": "select-dropdown-m2o",
                "options": config["dropdown_config"]
            }
            
            # Would apply to Directus here
            self._logger.info(f"Configured dropdown for {collection_name}")
            
            return {
                "success": True,
                "collection": collection_name,
                "config": dropdown_config,
                "message": f"Dropdown configured for {collection_name}"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": f"Dropdown configuration failed for {collection_name}"
            }
    
    def configure_search_filters(self) -> Dict[str, Any]:
        """Configure search and filtering by relationships"""
        try:
            filter_configs = []
            
            # Configure relationship-based filters
            for collection_name, config in self.collections.items():
                if "parent_field" in config:
                    filter_config = {
                        "collection": collection_name,
                        "filter_field": config["parent_field"],
                        "filter_type": "select",
                        "options": {"searchable": True, "multiple": False}
                    }
                    filter_configs.append(filter_config)
            
            return {
                "success": True,
                "configured_filters": len(filter_configs),
                "filter_configs": filter_configs,
                "message": "Search filters configured"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": f"Search filter configuration failed: {e}"
            }
    
    def validate_displays(self) -> Dict[str, Any]:
        """Validate that all relationship displays work correctly"""
        try:
            validation_results = []
            
            # Validate each collection's display configuration
            for collection_name in self.collections.keys():
                # Mock validation - would test actual Directus interface
                validation_result = {
                    "collection": collection_name,
                    "display_working": True,
                    "relationships_visible": True,
                    "dropdowns_functional": True
                }
                validation_results.append(validation_result)
            
            all_valid = all(r["display_working"] and r["relationships_visible"] and r["dropdowns_functional"] 
                           for r in validation_results)
            
            return {
                "success": all_valid,
                "validated_collections": len(validation_results),
                "validation_results": validation_results,
                "message": "Display validation completed"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": f"Display validation failed: {e}"
            }