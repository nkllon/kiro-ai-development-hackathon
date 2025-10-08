"""
Specification Importer - Focused Component

Single Responsibility: Import exactly 3 target specifications with validation.
Maintains <300 lines through focused functionality.

Requirements Addressed:
- 5.1: Import exactly 3 specifications with validation
- 10.1: Preserve all functionality with comprehensive validation
"""

import os
import re
from datetime import datetime
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from pathlib import Path

from src.rm_ddd.core.unified_reflective_module import (
    ReflectiveModule,
    ModuleHealth,
    ModuleStatus,
    ModuleCapability,
    GracefulDegradationResult,
)


@dataclass
class SpecificationInfo:
    """Information about a specification"""
    name: str
    path: str
    description: str
    status: str = "active"


@dataclass
class ImportResult:
    """Result of specification import operation"""
    success: bool
    imported_specs: List[str]
    spec_ids: Dict[str, int]
    errors: List[str]
    message: str


class SpecificationImporter(ReflectiveModule):
    """
    Focused specification importer with single responsibility
    
    Handles only specification discovery, validation, and database import.
    Maintains <300 lines through focused scope.
    """
    
    def __init__(self, schema_manager, repository_root: str = "."):
        """Initialize with minimal dependencies"""
        super().__init__()
        
        self.module_id = "specification_importer"
        self.schema_manager = schema_manager
        self.repository_root = Path(repository_root).resolve()
        
        # Target specifications (exactly 3 as per requirements)
        self.target_specifications = [
            "integration-orchestrator-framework",
            "ai-driven-cursor-sharing", 
            "gpt5-context-calibration-system"
        ]
        
        self._imported_specs = {}  # Track for rollback
    
    def get_module_info(self) -> Dict[str, Any]:
        """Get module information - ReflectiveModule implementation"""
        return {
            "module_id": self.module_id,
            "module_name": "SpecificationImporter",
            "version": "1.0.0",
            "repository_root": str(self.repository_root),
            "target_specifications": self.target_specifications,
            "focus": "specification_import_only"
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
        status = ModuleStatus.HEALTHY if self.repository_root.exists() else ModuleStatus.ERROR
        health_score = 1.0 if status == ModuleStatus.HEALTHY else 0.0
        
        if not self.repository_root.exists():
            issues.append(f"Repository root missing: {self.repository_root}")
        
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
        if self.repository_root.exists():
            return GracefulDegradationResult(
                success=True,
                degraded_capabilities=[],
                remaining_capabilities=self.get_capabilities()
            )
        
        return GracefulDegradationResult(
            success=True,
            degraded_capabilities=[ModuleCapability.DATA_PROCESSING],
            remaining_capabilities=[ModuleCapability.CORE_FUNCTIONALITY],
            error_message="Repository missing, data processing disabled"
        )
    
    def import_specifications(self, spec_names: List[str] = None) -> ImportResult:
        """
        Import specifications with controlled validation
        
        Args:
            spec_names: List of specification names (defaults to target specs)
            
        Returns:
            ImportResult with import status and spec IDs
        """
        with self.trace_operation("import_specifications", spec_names=spec_names) as trace:
            try:
                # Use target specifications if none provided
                if spec_names is None:
                    spec_names = self.target_specifications
                
                # Validate exactly 3 specifications
                if len(spec_names) != 3:
                    raise ValueError(f"Must import exactly 3 specifications, got {len(spec_names)}")
                
                # Scan for specifications
                spec_infos = self._scan_specifications(spec_names)
                
                if len(spec_infos) != 3:
                    raise ValueError(f"Found {len(spec_infos)} specifications, expected 3")
                
                # Import to database
                imported_specs, spec_ids, errors = self._import_to_database(spec_infos)
                
                # Create result
                result = ImportResult(
                    success=len(imported_specs) == 3 and len(errors) == 0,
                    imported_specs=imported_specs,
                    spec_ids=spec_ids,
                    errors=errors,
                    message=f"Imported {len(imported_specs)}/3 specifications"
                )
                
                trace.output_result = result
                return result
                
            except Exception as e:
                self._increment_error_count()
                error_result = ImportResult(
                    success=False,
                    imported_specs=[],
                    spec_ids={},
                    errors=[str(e)],
                    message=f"Import failed: {e}"
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
            
            # Extract description from requirements.md
            description = self._extract_description(spec_path)
            
            spec_info = SpecificationInfo(
                name=spec_name,
                path=str(spec_path),
                description=description,
                status="active"
            )
            
            spec_infos.append(spec_info)
        
        return spec_infos
    
    def _extract_description(self, spec_path: Path) -> str:
        """Extract description from requirements.md"""
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
        
        return description
    
    def _import_to_database(self, spec_infos: List[SpecificationInfo]) -> tuple:
        """Import specifications to database"""
        imported_specs = []
        spec_ids = {}
        errors = []
        
        connection = self.schema_manager.connection
        cursor = connection.cursor()
        
        try:
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
                        spec_id = cursor.fetchone()[0]
                    else:  # SQLite
                        cursor.execute("""
                            INSERT OR REPLACE INTO specifications (name, description, status)
                            VALUES (?, ?, ?)
                        """, (spec_info.name, spec_info.description, spec_info.status))
                        spec_id = cursor.lastrowid
                    
                    imported_specs.append(spec_info.name)
                    spec_ids[spec_info.name] = spec_id
                    
                    # Track for rollback
                    self._imported_specs[spec_info.name] = spec_id
                    
                    self._logger.info(f"Imported specification: {spec_info.name} (ID: {spec_id})")
                    
                except Exception as e:
                    error_msg = f"Failed to import specification {spec_info.name}: {e}"
                    errors.append(error_msg)
                    self._logger.error(error_msg)
            
            connection.commit()
            
        finally:
            cursor.close()
        
        return imported_specs, spec_ids, errors
    
    def get_imported_spec_ids(self) -> Dict[str, int]:
        """Get IDs of imported specifications"""
        return self._imported_specs.copy()
    
    def cleanup_imported_specs(self) -> bool:
        """Cleanup imported specifications (rollback capability)"""
        try:
            if not self._imported_specs:
                return True
            
            connection = self.schema_manager.connection
            cursor = connection.cursor()
            
            for spec_name, spec_id in self._imported_specs.items():
                try:
                    if self.schema_manager.database_type == "postgresql":
                        cursor.execute(
                            "DELETE FROM repository_content.specifications WHERE id = %s",
                            (spec_id,)
                        )
                    else:  # SQLite
                        cursor.execute(
                            "DELETE FROM specifications WHERE id = ?",
                            (spec_id,)
                        )
                    
                    self._logger.info(f"Cleaned up specification: {spec_name}")
                    
                except Exception as e:
                    self._logger.error(f"Failed to cleanup specification {spec_name}: {e}")
                    return False
            
            connection.commit()
            cursor.close()
            
            # Clear tracking
            self._imported_specs.clear()
            
            return True
            
        except Exception as e:
            self._logger.error(f"Cleanup failed: {e}")
            return False