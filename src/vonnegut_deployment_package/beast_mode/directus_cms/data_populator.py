"""
Directus CMS Data Populator - Systematic Implementation

This module provides systematic data population for the Directus CMS with:
- Controlled specification import (exactly 3 specs)
- File system scanning and content extraction
- Relationship validation and linking
- Comprehensive error handling and rollback capability

Requirements Addressed:
- 5.1: Import exactly 3 specifications with validation
- 5.2: Link documents and code files to specifications
- 10.1: Preserve all functionality with comprehensive validation
- 4.5: Rollback capability for failed operations
"""

import os
import logging
import re
from datetime import datetime
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
from pathlib import Path

from src.rm_ddd.core.unified_reflective_module import (
    ReflectiveModule,
    ModuleHealth,
    ModuleStatus,
    ModuleCapability,
    GracefulDegradationResult,
)
from src.beast_mode.directus_cms.schema_manager import SchemaManager
from src.beast_mode.directus_cms.database_utils import DatabaseConnectionManager


class PopulationStatus(Enum):
    """Data population status enumeration"""
    SUCCESS = "success"
    PARTIAL = "partial"
    FAILED = "failed"
    ROLLBACK = "rollback"


@dataclass
class SpecificationInfo:
    """Information about a specification"""
    name: str
    path: str
    description: str
    status: str = "active"


@dataclass
class CodeFileInfo:
    """Information about a code file"""
    file_name: str
    file_path: str
    specification_name: str
    relative_path: str


@dataclass
class DocumentInfo:
    """Information about a document"""
    title: str
    content: str
    document_type: str  # 'requirements', 'design', 'tasks'
    specification_name: str
    file_path: str


@dataclass
class TaskInfo:
    """Information about a task"""
    title: str
    description: str
    status: str
    specification_name: str
    task_number: str = None


@dataclass
class PopulationResult:
    """Result of data population operations"""
    success: bool
    status: PopulationStatus
    message: str
    details: Dict[str, Any]
    imported_specs: List[str] = None
    imported_files: List[str] = None
    errors: List[str] = None


@dataclass
class ValidationResult:
    """Result of relationship validation"""
    is_valid: bool
    validated_relationships: int
    broken_relationships: List[str]
    recommendations: List[str]


class DataPopulator(ReflectiveModule):
    """
    Systematic data population engine for Directus CMS
    
    Implements controlled data import with:
    - Exactly 3 target specifications
    - File system scanning and content extraction
    - Relationship validation and linking
    - Comprehensive error handling and rollback
    """
    
    def __init__(self, schema_manager: SchemaManager, repository_root: str = "."):
        """
        Initialize DataPopulator
        
        Args:
            schema_manager: SchemaManager instance for database operations
            repository_root: Root directory of the repository to scan
        """
        super().__init__()
        
        self.module_id = "directus_data_populator"
        self.schema_manager = schema_manager
        self.repository_root = Path(repository_root).resolve()
        
        # Target specifications (exactly 3 as per requirements)
        self.target_specifications = [
            "integration-orchestrator-framework",
            "ai-driven-cursor-sharing", 
            "gpt5-context-calibration-system"
        ]
        
        # File patterns for code file discovery
        self.code_file_patterns = [
            "integration_orchestrator",
            "cursor_sharing",
            "gpt5"
        ]
        
        self._logger = logging.getLogger(f"data_populator.{self.module_id}")
        self._imported_data = {}  # Track imported data for rollback
    
    def get_module_info(self) -> Dict[str, Any]:
        """Get module information - ReflectiveModule implementation"""
        return {
            "module_id": self.module_id,
            "module_name": "DirectusDataPopulator",
            "version": "1.0.0",
            "repository_root": str(self.repository_root),
            "target_specifications": self.target_specifications,
            "code_file_patterns": self.code_file_patterns,
            "schema_manager_status": self.schema_manager.get_health_status().status.value
        }
    
    def get_capabilities(self) -> List[ModuleCapability]:
        """Get module capabilities - ReflectiveModule implementation"""
        return [
            ModuleCapability.CORE_FUNCTIONALITY,
            ModuleCapability.DATA_PROCESSING,
            ModuleCapability.VALIDATION
        ]
    
    def get_health_status(self) -> ModuleHealth:
        """Get module health status - ReflectiveModule implementation"""
        issues = []
        status = ModuleStatus.HEALTHY
        health_score = 1.0
        
        # Check schema manager health
        schema_health = self.schema_manager.get_health_status()
        if schema_health.status != ModuleStatus.HEALTHY:
            issues.append(f"Schema manager not healthy: {schema_health.status.value}")
            status = ModuleStatus.WARNING
            health_score = 0.7
        
        # Check repository root exists
        if not self.repository_root.exists():
            issues.append(f"Repository root does not exist: {self.repository_root}")
            status = ModuleStatus.ERROR
            health_score = 0.0
        
        # Check target specifications exist
        missing_specs = []
        for spec_name in self.target_specifications:
            spec_path = self.repository_root / ".kiro" / "specs" / spec_name
            if not spec_path.exists():
                missing_specs.append(spec_name)
        
        if missing_specs:
            issues.append(f"Missing target specifications: {missing_specs}")
            if len(missing_specs) == len(self.target_specifications):
                status = ModuleStatus.ERROR
                health_score = 0.0
            else:
                status = ModuleStatus.WARNING
                health_score = 0.5
        
        uptime = (datetime.now() - self._start_time).total_seconds()
        
        return ModuleHealth(
            module_id=self.module_id,
            status=status,
            health_score=health_score,
            issues=issues,
            last_check=datetime.now(),
            uptime_seconds=uptime,
            error_count=self._error_count,
            warning_count=self._warning_count
        )
    
    def graceful_degradation(self) -> GracefulDegradationResult:
        """Perform graceful degradation - ReflectiveModule implementation"""
        try:
            # Check if we can still validate existing data
            if self.schema_manager.get_health_status().status == ModuleStatus.HEALTHY:
                return GracefulDegradationResult(
                    success=True,
                    degraded_capabilities=[],
                    remaining_capabilities=self.get_capabilities()
                )
            
            # If schema manager is unhealthy, disable data processing
            return GracefulDegradationResult(
                success=True,
                degraded_capabilities=[ModuleCapability.DATA_PROCESSING],
                remaining_capabilities=[ModuleCapability.CORE_FUNCTIONALITY, ModuleCapability.VALIDATION],
                error_message="Schema manager unhealthy, data processing disabled"
            )
            
        except Exception as e:
            self._increment_error_count()
            return GracefulDegradationResult(
                success=False,
                degraded_capabilities=self.get_capabilities(),
                remaining_capabilities=[],
                error_message=f"Graceful degradation failed: {e}"
            )
    
    def populate_specifications(self, spec_names: List[str] = None) -> PopulationResult:
        """
        Populate specifications with controlled import
        
        Args:
            spec_names: List of specification names to import (defaults to target specs)
            
        Returns:
            PopulationResult with import status and details
        """
        with self.trace_operation("populate_specifications", spec_names=spec_names) as trace:
            try:
                # Use target specifications if none provided
                if spec_names is None:
                    spec_names = self.target_specifications
                
                # Validate exactly 3 specifications
                if len(spec_names) != 3:
                    raise ValueError(f"Must import exactly 3 specifications, got {len(spec_names)}")
                
                imported_specs = []
                errors = []
                
                # Scan for specifications
                spec_infos = self._scan_specifications(spec_names)
                
                if len(spec_infos) != 3:
                    raise ValueError(f"Found {len(spec_infos)} specifications, expected 3")
                
                # Import each specification
                connection = self.schema_manager.connection
                cursor = connection.cursor()
                
                for spec_info in spec_infos:
                    try:
                        # Insert specification
                        if self.schema_manager.database_type == "postgresql":
                            cursor.execute("""
                                INSERT INTO repository_content.specifications (name, description, status)
                                VALUES (%s, %s, %s)
                                ON CONFLICT (name) DO UPDATE SET
                                    description = EXCLUDED.description,
                                    updated_date = CURRENT_TIMESTAMP
                                RETURNING id
                            """, (spec_info.name, spec_info.description, spec_info.status))
                        else:  # SQLite
                            cursor.execute("""
                                INSERT OR REPLACE INTO specifications (name, description, status)
                                VALUES (?, ?, ?)
                            """, (spec_info.name, spec_info.description, spec_info.status))
                        
                        if self.schema_manager.database_type == "postgresql":
                            spec_id = cursor.fetchone()[0]
                        else:
                            spec_id = cursor.lastrowid
                        
                        imported_specs.append(spec_info.name)
                        
                        # Track for rollback
                        if "specifications" not in self._imported_data:
                            self._imported_data["specifications"] = []
                        self._imported_data["specifications"].append({
                            "id": spec_id,
                            "name": spec_info.name
                        })
                        
                        self._logger.info(f"Imported specification: {spec_info.name} (ID: {spec_id})")
                        
                    except Exception as e:
                        error_msg = f"Failed to import specification {spec_info.name}: {e}"
                        errors.append(error_msg)
                        self._logger.error(error_msg)
                
                connection.commit()
                cursor.close()
                
                # Determine result status
                if len(imported_specs) == 3 and len(errors) == 0:
                    status = PopulationStatus.SUCCESS
                    message = f"Successfully imported {len(imported_specs)} specifications"
                elif len(imported_specs) > 0:
                    status = PopulationStatus.PARTIAL
                    message = f"Partially imported {len(imported_specs)}/3 specifications"
                else:
                    status = PopulationStatus.FAILED
                    message = "Failed to import any specifications"
                
                result = PopulationResult(
                    success=len(imported_specs) == 3,
                    status=status,
                    message=message,
                    details={
                        "imported_count": len(imported_specs),
                        "expected_count": 3,
                        "error_count": len(errors)
                    },
                    imported_specs=imported_specs,
                    errors=errors
                )
                
                trace.output_result = result
                return result
                
            except Exception as e:
                self._increment_error_count()
                error_result = PopulationResult(
                    success=False,
                    status=PopulationStatus.FAILED,
                    message=f"Specification population failed: {e}",
                    details={"error": str(e)},
                    errors=[str(e)]
                )
                
                trace.error_info = {"error": str(e)}
                return error_result
    
    def _scan_specifications(self, spec_names: List[str]) -> List[SpecificationInfo]:
        """Scan repository for target specifications"""
        spec_infos = []
        specs_dir = self.repository_root / ".kiro" / "specs"
        
        if not specs_dir.exists():
            raise FileNotFoundError(f"Specifications directory not found: {specs_dir}")
        
        for spec_name in spec_names:
            spec_path = specs_dir / spec_name
            
            if not spec_path.exists():
                raise FileNotFoundError(f"Specification directory not found: {spec_path}")
            
            # Read requirements.md for description
            requirements_file = spec_path / "requirements.md"
            description = "No description available"
            
            if requirements_file.exists():
                try:
                    with open(requirements_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                        # Extract description from introduction section
                        intro_match = re.search(r'## Introduction\s*\n\n(.*?)\n\n', content, re.DOTALL)
                        if intro_match:
                            description = intro_match.group(1).strip()[:500]  # Limit length
                except Exception as e:
                    self._logger.warning(f"Could not read description from {requirements_file}: {e}")
            
            spec_info = SpecificationInfo(
                name=spec_name,
                path=str(spec_path),
                description=description,
                status="active"
            )
            
            spec_infos.append(spec_info)
        
        return spec_infos
    
    def import_documents(self, spec_names: List[str] = None) -> PopulationResult:
        """
        Import documents (requirements.md, design.md, tasks.md) for specifications
        
        Args:
            spec_names: List of specification names (defaults to target specs)
            
        Returns:
            PopulationResult with import status
        """
        with self.trace_operation("import_documents", spec_names=spec_names) as trace:
            try:
                if spec_names is None:
                    spec_names = self.target_specifications
                
                imported_files = []
                errors = []
                
                # Get specification IDs
                spec_ids = self._get_specification_ids(spec_names)
                
                connection = self.schema_manager.connection
                cursor = connection.cursor()
                
                for spec_name in spec_names:
                    if spec_name not in spec_ids:
                        errors.append(f"Specification {spec_name} not found in database")
                        continue
                    
                    spec_id = spec_ids[spec_name]
                    spec_path = self.repository_root / ".kiro" / "specs" / spec_name
                    
                    # Import each document type
                    document_types = [
                        ("requirements.md", "requirements"),
                        ("design.md", "design"),
                        ("tasks.md", "tasks")
                    ]
                    
                    for filename, doc_type in document_types:
                        doc_file = spec_path / filename
                        
                        if doc_file.exists():
                            try:
                                with open(doc_file, 'r', encoding='utf-8') as f:
                                    content = f.read()
                                
                                title = f"{spec_name} {doc_type.title()}"
                                
                                # Insert document
                                if self.schema_manager.database_type == "postgresql":
                                    cursor.execute("""
                                        INSERT INTO repository_content.documents 
                                        (title, content, document_type, specification_id)
                                        VALUES (%s, %s, %s, %s)
                                        ON CONFLICT (title) DO UPDATE SET
                                            content = EXCLUDED.content,
                                            updated_date = CURRENT_TIMESTAMP
                                        RETURNING id
                                    """, (title, content, doc_type, spec_id))
                                    doc_id = cursor.fetchone()[0]
                                else:  # SQLite
                                    cursor.execute("""
                                        INSERT OR REPLACE INTO documents 
                                        (title, content, document_type, specification_id)
                                        VALUES (?, ?, ?, ?)
                                    """, (title, content, doc_type, spec_id))
                                    doc_id = cursor.lastrowid
                                
                                imported_files.append(str(doc_file))
                                
                                # Track for rollback
                                if "documents" not in self._imported_data:
                                    self._imported_data["documents"] = []
                                self._imported_data["documents"].append({
                                    "id": doc_id,
                                    "title": title
                                })
                                
                                self._logger.info(f"Imported document: {title}")
                                
                            except Exception as e:
                                error_msg = f"Failed to import document {doc_file}: {e}"
                                errors.append(error_msg)
                                self._logger.error(error_msg)
                
                connection.commit()
                cursor.close()
                
                result = PopulationResult(
                    success=len(errors) == 0,
                    status=PopulationStatus.SUCCESS if len(errors) == 0 else PopulationStatus.PARTIAL,
                    message=f"Imported {len(imported_files)} documents",
                    details={
                        "imported_count": len(imported_files),
                        "error_count": len(errors)
                    },
                    imported_files=imported_files,
                    errors=errors
                )
                
                trace.output_result = result
                return result
                
            except Exception as e:
                self._increment_error_count()
                error_result = PopulationResult(
                    success=False,
                    status=PopulationStatus.FAILED,
                    message=f"Document import failed: {e}",
                    details={"error": str(e)},
                    errors=[str(e)]
                )
                
                trace.error_info = {"error": str(e)}
                return error_result
    
    def link_code_files(self, spec_names: List[str] = None) -> PopulationResult:
        """
        Link code files to specifications based on naming patterns
        
        Args:
            spec_names: List of specification names (defaults to target specs)
            
        Returns:
            PopulationResult with linking status
        """
        with self.trace_operation("link_code_files", spec_names=spec_names) as trace:
            try:
                if spec_names is None:
                    spec_names = self.target_specifications
                
                imported_files = []
                errors = []
                
                # Get specification IDs
                spec_ids = self._get_specification_ids(spec_names)
                
                # Scan for code files
                code_files = self._scan_code_files()
                
                connection = self.schema_manager.connection
                cursor = connection.cursor()
                
                for code_file in code_files:
                    try:
                        if code_file.specification_name not in spec_ids:
                            errors.append(f"Specification {code_file.specification_name} not found for file {code_file.file_path}")
                            continue
                        
                        spec_id = spec_ids[code_file.specification_name]
                        
                        # Insert code file
                        if self.schema_manager.database_type == "postgresql":
                            cursor.execute("""
                                INSERT INTO repository_content.code_files 
                                (file_name, file_path, specification_id)
                                VALUES (%s, %s, %s)
                                ON CONFLICT (file_path) DO UPDATE SET
                                    specification_id = EXCLUDED.specification_id
                                RETURNING id
                            """, (code_file.file_name, code_file.relative_path, spec_id))
                            file_id = cursor.fetchone()[0]
                        else:  # SQLite
                            cursor.execute("""
                                INSERT OR REPLACE INTO code_files 
                                (file_name, file_path, specification_id)
                                VALUES (?, ?, ?)
                            """, (code_file.file_name, code_file.relative_path, spec_id))
                            file_id = cursor.lastrowid
                        
                        imported_files.append(code_file.file_path)
                        
                        # Track for rollback
                        if "code_files" not in self._imported_data:
                            self._imported_data["code_files"] = []
                        self._imported_data["code_files"].append({
                            "id": file_id,
                            "file_path": code_file.relative_path
                        })
                        
                        self._logger.info(f"Linked code file: {code_file.file_name} -> {code_file.specification_name}")
                        
                    except Exception as e:
                        error_msg = f"Failed to link code file {code_file.file_path}: {e}"
                        errors.append(error_msg)
                        self._logger.error(error_msg)
                
                connection.commit()
                cursor.close()
                
                result = PopulationResult(
                    success=len(errors) == 0,
                    status=PopulationStatus.SUCCESS if len(errors) == 0 else PopulationStatus.PARTIAL,
                    message=f"Linked {len(imported_files)} code files",
                    details={
                        "imported_count": len(imported_files),
                        "error_count": len(errors)
                    },
                    imported_files=imported_files,
                    errors=errors
                )
                
                trace.output_result = result
                return result
                
            except Exception as e:
                self._increment_error_count()
                error_result = PopulationResult(
                    success=False,
                    status=PopulationStatus.FAILED,
                    message=f"Code file linking failed: {e}",
                    details={"error": str(e)},
                    errors=[str(e)]
                )
                
                trace.error_info = {"error": str(e)}
                return error_result
    
    def _scan_code_files(self) -> List[CodeFileInfo]:
        """Scan repository for code files matching patterns"""
        code_files = []
        src_dir = self.repository_root / "src"
        
        if not src_dir.exists():
            self._logger.warning(f"Source directory not found: {src_dir}")
            return code_files
        
        # Pattern mapping: file pattern -> specification name
        pattern_mapping = {
            "integration_orchestrator": "integration-orchestrator-framework",
            "cursor_sharing": "ai-driven-cursor-sharing",
            "gpt5": "gpt5-context-calibration-system"
        }
        
        # Scan for Python files
        for py_file in src_dir.rglob("*.py"):
            try:
                relative_path = py_file.relative_to(self.repository_root)
                file_content = py_file.read_text(encoding='utf-8')
                
                # Check if file matches any pattern
                for pattern, spec_name in pattern_mapping.items():
                    if (pattern in py_file.name.lower() or 
                        pattern in str(py_file.parent).lower() or
                        pattern in file_content.lower()):
                        
                        code_file = CodeFileInfo(
                            file_name=py_file.name,
                            file_path=str(py_file),
                            specification_name=spec_name,
                            relative_path=str(relative_path)
                        )
                        
                        code_files.append(code_file)
                        break  # Only match first pattern
                        
            except Exception as e:
                self._logger.warning(f"Error scanning file {py_file}: {e}")
        
        return code_files
    
    def _get_specification_ids(self, spec_names: List[str]) -> Dict[str, int]:
        """Get specification IDs from database"""
        spec_ids = {}
        
        connection = self.schema_manager.connection
        cursor = connection.cursor()
        
        for spec_name in spec_names:
            if self.schema_manager.database_type == "postgresql":
                cursor.execute(
                    "SELECT id FROM repository_content.specifications WHERE name = %s",
                    (spec_name,)
                )
            else:  # SQLite
                cursor.execute(
                    "SELECT id FROM specifications WHERE name = ?",
                    (spec_name,)
                )
            
            result = cursor.fetchone()
            if result:
                spec_ids[spec_name] = result[0]
        
        cursor.close()
        return spec_ids
    
    def validate_relationships(self) -> ValidationResult:
        """
        Validate all relationships in the database
        
        Returns:
            ValidationResult with validation status
        """
        with self.trace_operation("validate_relationships") as trace:
            try:
                validated_count = 0
                broken_relationships = []
                recommendations = []
                
                connection = self.schema_manager.connection
                cursor = connection.cursor()
                
                # Validate code file relationships
                if self.schema_manager.database_type == "postgresql":
                    cursor.execute("""
                        SELECT cf.file_path, cf.specification_id, s.name
                        FROM repository_content.code_files cf
                        LEFT JOIN repository_content.specifications s ON cf.specification_id = s.id
                        WHERE cf.specification_id IS NOT NULL
                    """)
                else:  # SQLite
                    cursor.execute("""
                        SELECT cf.file_path, cf.specification_id, s.name
                        FROM code_files cf
                        LEFT JOIN specifications s ON cf.specification_id = s.id
                        WHERE cf.specification_id IS NOT NULL
                    """)
                
                code_file_results = cursor.fetchall()
                
                for file_path, spec_id, spec_name in code_file_results:
                    if spec_name is None:
                        broken_relationships.append(f"Code file {file_path} references non-existent specification ID {spec_id}")
                    else:
                        validated_count += 1
                
                # Validate document relationships
                if self.schema_manager.database_type == "postgresql":
                    cursor.execute("""
                        SELECT d.title, d.specification_id, s.name
                        FROM repository_content.documents d
                        LEFT JOIN repository_content.specifications s ON d.specification_id = s.id
                        WHERE d.specification_id IS NOT NULL
                    """)
                else:  # SQLite
                    cursor.execute("""
                        SELECT d.title, d.specification_id, s.name
                        FROM documents d
                        LEFT JOIN specifications s ON d.specification_id = s.id
                        WHERE d.specification_id IS NOT NULL
                    """)
                
                document_results = cursor.fetchall()
                
                for title, spec_id, spec_name in document_results:
                    if spec_name is None:
                        broken_relationships.append(f"Document {title} references non-existent specification ID {spec_id}")
                    else:
                        validated_count += 1
                
                cursor.close()
                
                # Generate recommendations
                if broken_relationships:
                    recommendations.append("Fix broken relationships by updating foreign key references")
                    recommendations.append("Consider running data cleanup to remove orphaned records")
                
                if validated_count == 0:
                    recommendations.append("No relationships found - consider running data population")
                
                result = ValidationResult(
                    is_valid=len(broken_relationships) == 0,
                    validated_relationships=validated_count,
                    broken_relationships=broken_relationships,
                    recommendations=recommendations
                )
                
                trace.output_result = result
                return result
                
            except Exception as e:
                self._increment_error_count()
                error_result = ValidationResult(
                    is_valid=False,
                    validated_relationships=0,
                    broken_relationships=[f"Validation failed: {e}"],
                    recommendations=["Check database connection and schema"]
                )
                
                trace.error_info = {"error": str(e)}
                return error_result
    
    def cleanup_data(self) -> PopulationResult:
        """
        Clean up imported data (rollback capability)
        
        Returns:
            PopulationResult with cleanup status
        """
        with self.trace_operation("cleanup_data") as trace:
            try:
                cleaned_items = []
                errors = []
                
                connection = self.schema_manager.connection
                cursor = connection.cursor()
                
                # Clean up in reverse order (tasks, documents, code_files, specifications)
                cleanup_order = ["tasks", "documents", "code_files", "specifications"]
                
                for table_name in cleanup_order:
                    if table_name in self._imported_data:
                        for item in self._imported_data[table_name]:
                            try:
                                if self.schema_manager.database_type == "postgresql":
                                    cursor.execute(
                                        f"DELETE FROM repository_content.{table_name} WHERE id = %s",
                                        (item["id"],)
                                    )
                                else:  # SQLite
                                    cursor.execute(
                                        f"DELETE FROM {table_name} WHERE id = ?",
                                        (item["id"],)
                                    )
                                
                                cleaned_items.append(f"{table_name}:{item['id']}")
                                
                            except Exception as e:
                                error_msg = f"Failed to clean {table_name} item {item['id']}: {e}"
                                errors.append(error_msg)
                                self._logger.error(error_msg)
                
                connection.commit()
                cursor.close()
                
                # Clear tracking data
                self._imported_data.clear()
                
                result = PopulationResult(
                    success=len(errors) == 0,
                    status=PopulationStatus.SUCCESS if len(errors) == 0 else PopulationStatus.PARTIAL,
                    message=f"Cleaned up {len(cleaned_items)} items",
                    details={
                        "cleaned_count": len(cleaned_items),
                        "error_count": len(errors)
                    },
                    imported_files=cleaned_items,
                    errors=errors
                )
                
                trace.output_result = result
                return result
                
            except Exception as e:
                self._increment_error_count()
                error_result = PopulationResult(
                    success=False,
                    status=PopulationStatus.FAILED,
                    message=f"Cleanup failed: {e}",
                    details={"error": str(e)},
                    errors=[str(e)]
                )
                
                trace.error_info = {"error": str(e)}
                return error_result
    
    def get_population_status(self) -> Dict[str, Any]:
        """Get comprehensive population status"""
        with self.trace_operation("get_population_status") as trace:
            try:
                status = {
                    "target_specifications": self.target_specifications,
                    "repository_root": str(self.repository_root),
                    "imported_data_summary": {},
                    "validation_status": None,
                    "last_updated": datetime.now().isoformat()
                }
                
                # Count imported data
                for table_name, items in self._imported_data.items():
                    status["imported_data_summary"][table_name] = len(items)
                
                # Get validation status
                validation_result = self.validate_relationships()
                status["validation_status"] = {
                    "is_valid": validation_result.is_valid,
                    "validated_relationships": validation_result.validated_relationships,
                    "broken_count": len(validation_result.broken_relationships)
                }
                
                trace.output_result = status
                return status
                
            except Exception as e:
                self._increment_error_count()
                error_status = {
                    "error": str(e),
                    "target_specifications": self.target_specifications,
                    "repository_root": str(self.repository_root),
                    "last_updated": datetime.now().isoformat()
                }
                
                trace.error_info = {"error": str(e)}
                return error_status