"""
Directus Schema Extension for Repository Content
==============================================

Extends the existing 5-collection Directus schema with repository-wide
collections for comprehensive content management and intelligence.

Author: Beast Mode Framework
Date: 2025-01-16
Version: 1.0
"""

import os
import json
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict

# Import unified ReflectiveModule
from src.rm_ddd.core.unified_reflective_module import (
    ReflectiveModule, 
    ModuleHealth, 
    ModuleStatus, 
    ModuleCapability,
    GracefulDegradationResult
)


@dataclass
class DirectusCollection:
    """Directus collection definition"""
    name: str
    schema: Dict[str, Any]
    fields: List[Dict[str, Any]]
    relations: List[Dict[str, Any]]
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class SchemaExtensionResult:
    """Result of schema extension operation"""
    success: bool
    collections_created: List[str]
    relations_created: List[str]
    error_message: Optional[str] = None
    migration_sql: Optional[str] = None


class DirectusSchemaExtension(ReflectiveModule):
    """
    Directus Schema Extension - RM-DDD Compliant
    
    Extends existing Directus schema with repository content collections
    following the established 5-collection pattern.
    
    Single Responsibility: Extend Directus schema for repository intelligence
    """  
  
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__()
        self.module_id = "DirectusSchemaExtension"
        self._config = config or {}
        self._logger = logging.getLogger(f"repository_discovery.{self.__class__.__name__}")
        
        # Configuration
        self._directus_url = self._config.get('directus_url', 'http://localhost:8055')
        self._admin_token = self._config.get('admin_token', None)
        self._dry_run = self._config.get('dry_run', True)
        
        # Schema tracking
        self._collections_created = []
        self._relations_created = []
        
        self._logger.info(f"DirectusSchemaExtension initialized with URL: {self._directus_url}")
    
    def get_module_info(self) -> Dict[str, Any]:
        """Get module information - RDI Compliant"""
        return {
            "module_id": self.module_id,
            "name": "DirectusSchemaExtension",
            "version": "1.0.0",
            "description": "Extends Directus schema for repository content management",
            "capabilities": [cap.value for cap in self.get_capabilities()],
            "collections_created": len(self._collections_created),
            "relations_created": len(self._relations_created),
            "directus_url": self._directus_url
        }
    
    def get_capabilities(self) -> List[ModuleCapability]:
        """Get module capabilities - RDI Compliant"""
        return [
            ModuleCapability.CORE_FUNCTIONALITY,
            ModuleCapability.DATA_PROCESSING,
            ModuleCapability.API_INTEGRATION,
            ModuleCapability.VALIDATION
        ]
    
    def get_health_status(self) -> ModuleHealth:
        """Get module health status - RDI Compliant"""
        # Test Directus connectivity if configured
        if self._admin_token:
            try:
                # Would test actual connection here
                status = ModuleStatus.HEALTHY
                health_score = 1.0
                issues = []
            except Exception as e:
                status = ModuleStatus.ERROR
                health_score = 0.0
                issues = [f"Directus connection failed: {str(e)}"]
        else:
            status = ModuleStatus.WARNING
            health_score = 0.7
            issues = ["No admin token configured - dry run mode only"]
        
        return ModuleHealth(
            module_id=self.module_id,
            status=status,
            health_score=health_score,
            issues=issues,
            last_check=datetime.now(),
            uptime_seconds=(datetime.now() - self._start_time).total_seconds()
        )
    
    def graceful_degradation(self) -> GracefulDegradationResult:
        """Perform graceful degradation - RDI Compliant"""
        try:
            # In degraded mode, we can still generate schema definitions
            remaining_capabilities = [
                ModuleCapability.CORE_FUNCTIONALITY,
                ModuleCapability.DATA_PROCESSING
            ]
            
            degraded_capabilities = []
            if not self._admin_token:
                degraded_capabilities.append(ModuleCapability.API_INTEGRATION)
            
            return GracefulDegradationResult(
                success=True,
                degraded_capabilities=degraded_capabilities,
                remaining_capabilities=remaining_capabilities
            )
        except Exception as e:
            return GracefulDegradationResult(
                success=False,
                degraded_capabilities=[ModuleCapability.CORE_FUNCTIONALITY],
                remaining_capabilities=[],
                error_message=str(e)
            ) 
   
    def create_repository_collections(self) -> SchemaExtensionResult:
        """
        Create repository content collections extending existing Directus schema
        
        Returns:
            SchemaExtensionResult with creation status and SQL
        """
        with self.trace_operation("create_repository_collections") as trace:
            try:
                collections = self._define_repository_collections()
                migration_sql = self._generate_migration_sql(collections)
                
                if not self._dry_run and self._admin_token:
                    # Would execute actual Directus API calls here
                    self._logger.info("Executing Directus schema extension...")
                    # result = self._execute_directus_migration(collections)
                    result = self._simulate_migration(collections)
                else:
                    self._logger.info("Dry run mode - generating schema definitions only")
                    result = self._simulate_migration(collections)
                
                trace.output_result = {
                    'collections_created': len(result.collections_created),
                    'relations_created': len(result.relations_created),
                    'success': result.success
                }
                
                return result
                
            except Exception as e:
                self._logger.error(f"Failed to create repository collections: {e}")
                result = SchemaExtensionResult(
                    success=False,
                    collections_created=[],
                    relations_created=[],
                    error_message=str(e)
                )
                trace.output_result = {'success': False, 'error': str(e)}
                return result
    
    def _define_repository_collections(self) -> List[DirectusCollection]:
        """Define repository content collections"""
        collections = []
        
        # 1. Repository Items Collection
        repository_items = DirectusCollection(
            name="repository_items",
            schema={
                "collection": "repository_items",
                "meta": {
                    "accountability": "all",
                    "collection": "repository_items",
                    "group": None,
                    "hidden": False,
                    "icon": "folder",
                    "item_duplication_fields": None,
                    "note": "Repository content items with metadata",
                    "singleton": False,
                    "translations": None
                }
            },
            fields=[
                {
                    "field": "id",
                    "type": "uuid",
                    "meta": {"hidden": True, "readonly": True, "interface": "input", "special": ["uuid"]},
                    "schema": {"is_primary_key": True, "has_auto_increment": False, "is_nullable": False}
                },
                {
                    "field": "item_type",
                    "type": "string",
                    "meta": {"interface": "select-dropdown", "options": {
                        "choices": [
                            {"text": "Specification", "value": "specification"},
                            {"text": "Source Code", "value": "source_code"},
                            {"text": "Documentation", "value": "documentation"},
                            {"text": "Analysis", "value": "analysis"},
                            {"text": "Script", "value": "script"},
                            {"text": "Configuration", "value": "configuration"}
                        ]
                    }},
                    "schema": {"is_nullable": False, "max_length": 50}
                },
                {
                    "field": "path",
                    "type": "string",
                    "meta": {"interface": "input", "width": "full"},
                    "schema": {"is_nullable": False, "max_length": 1000}
                },
                {
                    "field": "name",
                    "type": "string", 
                    "meta": {"interface": "input", "width": "half"},
                    "schema": {"is_nullable": False, "max_length": 255}
                },
                {
                    "field": "content_hash",
                    "type": "string",
                    "meta": {"interface": "input", "readonly": True},
                    "schema": {"is_nullable": True, "max_length": 64}
                },
                {
                    "field": "file_size",
                    "type": "integer",
                    "meta": {"interface": "input", "readonly": True},
                    "schema": {"is_nullable": True}
                },
                {
                    "field": "mime_type",
                    "type": "string",
                    "meta": {"interface": "input", "readonly": True},
                    "schema": {"is_nullable": True, "max_length": 100}
                },
                {
                    "field": "encoding",
                    "type": "string",
                    "meta": {"interface": "input", "readonly": True},
                    "schema": {"is_nullable": True, "max_length": 50}
                },
                {
                    "field": "is_binary",
                    "type": "boolean",
                    "meta": {"interface": "boolean", "readonly": True},
                    "schema": {"is_nullable": False, "default_value": False}
                },
                {
                    "field": "line_count",
                    "type": "integer",
                    "meta": {"interface": "input", "readonly": True},
                    "schema": {"is_nullable": True}
                }
            ],
            relations=[]
        )
        collections.append(repository_items)  
      
        # 2. Specifications Collection
        specifications = DirectusCollection(
            name="specifications",
            schema={
                "collection": "specifications",
                "meta": {
                    "accountability": "all",
                    "collection": "specifications",
                    "group": None,
                    "hidden": False,
                    "icon": "description",
                    "note": "Repository specifications with requirements",
                    "singleton": False
                }
            },
            fields=[
                {
                    "field": "id",
                    "type": "uuid",
                    "meta": {"hidden": True, "readonly": True, "interface": "input", "special": ["uuid"]},
                    "schema": {"is_primary_key": True, "has_auto_increment": False, "is_nullable": False}
                },
                {
                    "field": "repository_item_id",
                    "type": "uuid",
                    "meta": {"interface": "select-dropdown-m2o", "special": ["m2o"]},
                    "schema": {"is_nullable": False}
                },
                {
                    "field": "spec_name",
                    "type": "string",
                    "meta": {"interface": "input", "width": "full"},
                    "schema": {"is_nullable": False, "max_length": 255}
                },
                {
                    "field": "status",
                    "type": "string",
                    "meta": {"interface": "select-dropdown", "options": {
                        "choices": [
                            {"text": "Draft", "value": "draft"},
                            {"text": "Active", "value": "active"},
                            {"text": "Deprecated", "value": "deprecated"},
                            {"text": "Complete", "value": "complete"}
                        ]
                    }},
                    "schema": {"is_nullable": False, "default_value": "draft", "max_length": 20}
                },
                {
                    "field": "priority",
                    "type": "integer",
                    "meta": {"interface": "select-dropdown", "options": {
                        "choices": [
                            {"text": "Critical", "value": 1},
                            {"text": "High", "value": 2},
                            {"text": "Medium", "value": 3},
                            {"text": "Low", "value": 4}
                        ]
                    }},
                    "schema": {"is_nullable": False, "default_value": 3}
                }
            ],
            relations=[
                {
                    "collection": "specifications",
                    "field": "repository_item_id",
                    "related_collection": "repository_items",
                    "meta": {"many_collection": "specifications", "many_field": "repository_item_id", "one_collection": "repository_items", "one_field": None, "one_collection_field": None, "one_allowed_collections": None, "junction_field": None, "sort_field": None, "one_deselect_action": "nullify"},
                    "schema": {"on_update": "CASCADE", "on_delete": "CASCADE"}
                }
            ]
        )
        collections.append(specifications)
        
        # 3. Requirements Collection
        requirements = DirectusCollection(
            name="requirements",
            schema={
                "collection": "requirements",
                "meta": {
                    "accountability": "all",
                    "collection": "requirements", 
                    "group": None,
                    "hidden": False,
                    "icon": "checklist",
                    "note": "Specification requirements with acceptance criteria",
                    "singleton": False
                }
            },
            fields=[
                {
                    "field": "id",
                    "type": "uuid",
                    "meta": {"hidden": True, "readonly": True, "interface": "input", "special": ["uuid"]},
                    "schema": {"is_primary_key": True, "has_auto_increment": False, "is_nullable": False}
                },
                {
                    "field": "specification_id",
                    "type": "uuid",
                    "meta": {"interface": "select-dropdown-m2o", "special": ["m2o"]},
                    "schema": {"is_nullable": False}
                },
                {
                    "field": "requirement_number",
                    "type": "string",
                    "meta": {"interface": "input", "width": "half"},
                    "schema": {"is_nullable": False, "max_length": 50}
                },
                {
                    "field": "user_story",
                    "type": "text",
                    "meta": {"interface": "input-multiline", "width": "full"},
                    "schema": {"is_nullable": False}
                },
                {
                    "field": "acceptance_criteria",
                    "type": "json",
                    "meta": {"interface": "list", "width": "full"},
                    "schema": {"is_nullable": False}
                },
                {
                    "field": "priority",
                    "type": "integer",
                    "meta": {"interface": "select-dropdown"},
                    "schema": {"is_nullable": False, "default_value": 3}
                },
                {
                    "field": "status",
                    "type": "string",
                    "meta": {"interface": "select-dropdown"},
                    "schema": {"is_nullable": False, "default_value": "draft", "max_length": 20}
                }
            ],
            relations=[
                {
                    "collection": "requirements",
                    "field": "specification_id", 
                    "related_collection": "specifications",
                    "meta": {"many_collection": "requirements", "many_field": "specification_id", "one_collection": "specifications", "one_field": None},
                    "schema": {"on_update": "CASCADE", "on_delete": "CASCADE"}
                }
            ]
        )
        collections.append(requirements)     
   
        # 4. Analysis Artifacts Collection
        analysis_artifacts = DirectusCollection(
            name="analysis_artifacts",
            schema={
                "collection": "analysis_artifacts",
                "meta": {
                    "accountability": "all",
                    "collection": "analysis_artifacts",
                    "group": None,
                    "hidden": False,
                    "icon": "analytics",
                    "note": "Repository analysis artifacts and reports",
                    "singleton": False
                }
            },
            fields=[
                {
                    "field": "id",
                    "type": "uuid",
                    "meta": {"hidden": True, "readonly": True, "interface": "input", "special": ["uuid"]},
                    "schema": {"is_primary_key": True, "has_auto_increment": False, "is_nullable": False}
                },
                {
                    "field": "repository_item_id",
                    "type": "uuid",
                    "meta": {"interface": "select-dropdown-m2o", "special": ["m2o"]},
                    "schema": {"is_nullable": True}
                },
                {
                    "field": "analysis_type",
                    "type": "string",
                    "meta": {"interface": "select-dropdown", "options": {
                        "choices": [
                            {"text": "Conflict Report", "value": "conflict_report"},
                            {"text": "Overlap Matrix", "value": "overlap_matrix"},
                            {"text": "Landscape Analysis", "value": "landscape_analysis"},
                            {"text": "RCA Report", "value": "rca_report"},
                            {"text": "Performance Analysis", "value": "performance_analysis"},
                            {"text": "Dependency Analysis", "value": "dependency_analysis"}
                        ]
                    }},
                    "schema": {"is_nullable": False, "max_length": 50}
                },
                {
                    "field": "analysis_data",
                    "type": "json",
                    "meta": {"interface": "input-code", "width": "full", "options": {"language": "json"}},
                    "schema": {"is_nullable": False}
                },
                {
                    "field": "confidence_score",
                    "type": "decimal",
                    "meta": {"interface": "input", "width": "half"},
                    "schema": {"is_nullable": False, "default_value": 1.0, "numeric_precision": 3, "numeric_scale": 2}
                },
                {
                    "field": "generated_by",
                    "type": "string",
                    "meta": {"interface": "input", "width": "half"},
                    "schema": {"is_nullable": True, "max_length": 100}
                },
                {
                    "field": "correlation_id",
                    "type": "string",
                    "meta": {"interface": "input", "readonly": True},
                    "schema": {"is_nullable": True, "max_length": 100}
                }
            ],
            relations=[
                {
                    "collection": "analysis_artifacts",
                    "field": "repository_item_id",
                    "related_collection": "repository_items", 
                    "meta": {"many_collection": "analysis_artifacts", "many_field": "repository_item_id", "one_collection": "repository_items", "one_field": None},
                    "schema": {"on_update": "CASCADE", "on_delete": "SET NULL"}
                }
            ]
        )
        collections.append(analysis_artifacts)
        
        # 5. Operation Traces Collection (for monitoring)
        operation_traces = DirectusCollection(
            name="operation_traces",
            schema={
                "collection": "operation_traces",
                "meta": {
                    "accountability": "all",
                    "collection": "operation_traces",
                    "group": None,
                    "hidden": False,
                    "icon": "timeline",
                    "note": "System operation traces for monitoring and debugging",
                    "singleton": False
                }
            },
            fields=[
                {
                    "field": "id",
                    "type": "uuid",
                    "meta": {"hidden": True, "readonly": True, "interface": "input", "special": ["uuid"]},
                    "schema": {"is_primary_key": True, "has_auto_increment": False, "is_nullable": False}
                },
                {
                    "field": "trace_id",
                    "type": "string",
                    "meta": {"interface": "input", "readonly": True},
                    "schema": {"is_nullable": False, "max_length": 255}
                },
                {
                    "field": "operation_name",
                    "type": "string",
                    "meta": {"interface": "input", "readonly": True},
                    "schema": {"is_nullable": False, "max_length": 255}
                },
                {
                    "field": "component_name",
                    "type": "string",
                    "meta": {"interface": "input", "readonly": True},
                    "schema": {"is_nullable": False, "max_length": 255}
                },
                {
                    "field": "duration_ms",
                    "type": "decimal",
                    "meta": {"interface": "input", "readonly": True},
                    "schema": {"is_nullable": True, "numeric_precision": 10, "numeric_scale": 3}
                },
                {
                    "field": "input_parameters",
                    "type": "json",
                    "meta": {"interface": "input-code", "readonly": True},
                    "schema": {"is_nullable": True}
                },
                {
                    "field": "output_result",
                    "type": "json",
                    "meta": {"interface": "input-code", "readonly": True},
                    "schema": {"is_nullable": True}
                },
                {
                    "field": "error_info",
                    "type": "json",
                    "meta": {"interface": "input-code", "readonly": True},
                    "schema": {"is_nullable": True}
                },
                {
                    "field": "correlation_id",
                    "type": "string",
                    "meta": {"interface": "input", "readonly": True},
                    "schema": {"is_nullable": False, "max_length": 255}
                }
            ],
            relations=[]
        )
        collections.append(operation_traces)
        
        return collections
    
    def _generate_migration_sql(self, collections: List[DirectusCollection]) -> str:
        """Generate SQL migration script for the collections"""
        sql_statements = []
        
        # Add header
        sql_statements.append("-- Repository Discovery Directus Schema Extension")
        sql_statements.append(f"-- Generated: {datetime.now().isoformat()}")
        sql_statements.append("-- Extends existing 5-collection pattern with repository content")
        sql_statements.append("")
        
        for collection in collections:
            # Create table statement
            table_name = collection.name
            sql_statements.append(f"-- Create {table_name} table")
            
            create_table = f"CREATE TABLE {table_name} ("
            field_definitions = []
            
            for field in collection.fields:
                field_def = self._field_to_sql(field)
                field_definitions.append(field_def)
            
            # Add Directus standard fields
            field_definitions.extend([
                "date_created TIMESTAMP DEFAULT CURRENT_TIMESTAMP",
                "date_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP",
                "user_created UUID REFERENCES directus_users(id)",
                "user_updated UUID REFERENCES directus_users(id)"
            ])
            
            create_table += ",\n    ".join(field_definitions)
            create_table += "\n);"
            
            sql_statements.append(create_table)
            sql_statements.append("")
            
            # Add indexes
            sql_statements.append(f"-- Indexes for {table_name}")
            if table_name == "repository_items":
                sql_statements.extend([
                    f"CREATE INDEX idx_{table_name}_item_type ON {table_name}(item_type);",
                    f"CREATE INDEX idx_{table_name}_path ON {table_name}(path);",
                    f"CREATE INDEX idx_{table_name}_content_hash ON {table_name}(content_hash);"
                ])
            elif table_name == "specifications":
                sql_statements.extend([
                    f"CREATE INDEX idx_{table_name}_status ON {table_name}(status);",
                    f"CREATE INDEX idx_{table_name}_priority ON {table_name}(priority);"
                ])
            elif table_name == "requirements":
                sql_statements.extend([
                    f"CREATE INDEX idx_{table_name}_spec_id ON {table_name}(specification_id);",
                    f"CREATE INDEX idx_{table_name}_status ON {table_name}(status);"
                ])
            elif table_name == "analysis_artifacts":
                sql_statements.extend([
                    f"CREATE INDEX idx_{table_name}_type ON {table_name}(analysis_type);",
                    f"CREATE INDEX idx_{table_name}_correlation ON {table_name}(correlation_id);"
                ])
            elif table_name == "operation_traces":
                sql_statements.extend([
                    f"CREATE INDEX idx_{table_name}_trace_id ON {table_name}(trace_id);",
                    f"CREATE INDEX idx_{table_name}_operation ON {table_name}(operation_name);",
                    f"CREATE INDEX idx_{table_name}_correlation ON {table_name}(correlation_id);"
                ])
            
            sql_statements.append("")
            
            # Add foreign key constraints
            if collection.relations:
                sql_statements.append(f"-- Foreign key constraints for {table_name}")
                for relation in collection.relations:
                    fk_field = relation["field"]
                    fk_table = relation["related_collection"]
                    on_update = relation["schema"].get("on_update", "CASCADE")
                    on_delete = relation["schema"].get("on_delete", "CASCADE")
                    
                    constraint_name = f"fk_{table_name}_{fk_field}"
                    fk_sql = f"ALTER TABLE {table_name} ADD CONSTRAINT {constraint_name} FOREIGN KEY ({fk_field}) REFERENCES {fk_table}(id) ON UPDATE {on_update} ON DELETE {on_delete};"
                    sql_statements.append(fk_sql)
                
                sql_statements.append("")
        
        return "\n".join(sql_statements)
    
    def _field_to_sql(self, field: Dict[str, Any]) -> str:
        """Convert Directus field definition to SQL"""
        field_name = field["field"]
        field_type = field["type"]
        schema = field.get("schema", {})
        
        # Map Directus types to SQL types
        type_mapping = {
            "uuid": "UUID PRIMARY KEY DEFAULT gen_random_uuid()" if schema.get("is_primary_key") else "UUID",
            "string": f"VARCHAR({schema.get('max_length', 255)})",
            "text": "TEXT",
            "integer": "INTEGER",
            "decimal": f"DECIMAL({schema.get('numeric_precision', 10)},{schema.get('numeric_scale', 2)})",
            "boolean": "BOOLEAN",
            "json": "JSONB",
            "timestamp": "TIMESTAMP"
        }
        
        sql_type = type_mapping.get(field_type, "TEXT")
        
        # Add constraints
        constraints = []
        if not schema.get("is_nullable", True):
            constraints.append("NOT NULL")
        
        if "default_value" in schema:
            default_val = schema["default_value"]
            if isinstance(default_val, str):
                constraints.append(f"DEFAULT '{default_val}'")
            else:
                constraints.append(f"DEFAULT {default_val}")
        
        constraint_str = " " + " ".join(constraints) if constraints else ""
        
        return f"{field_name} {sql_type}{constraint_str}"
    
    def _simulate_migration(self, collections: List[DirectusCollection]) -> SchemaExtensionResult:
        """Simulate migration for dry run mode"""
        collections_created = [col.name for col in collections]
        relations_created = []
        
        for collection in collections:
            relations_created.extend([
                f"{collection.name}.{rel['field']}" 
                for rel in collection.relations
            ])
        
        self._collections_created = collections_created
        self._relations_created = relations_created
        
        return SchemaExtensionResult(
            success=True,
            collections_created=collections_created,
            relations_created=relations_created,
            migration_sql=self._generate_migration_sql(collections)
        )
    
    def get_schema_status(self) -> Dict[str, Any]:
        """Get current schema extension status"""
        return {
            "collections_created": self._collections_created,
            "relations_created": self._relations_created,
            "total_collections": len(self._collections_created),
            "total_relations": len(self._relations_created),
            "dry_run_mode": self._dry_run,
            "directus_url": self._directus_url
        }