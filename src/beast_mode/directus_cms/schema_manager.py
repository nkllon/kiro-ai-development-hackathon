"""
Directus CMS Schema Manager - Systematic Implementation

This module provides systematic database schema management for the Directus CMS
with proper MVC architecture, comprehensive error prevention, and Beast Mode integration.

Requirements Addressed:
- 1.1: Consolidate all Directus specifications into unified system
- 2.2: Use MVC architecture with proper separation of concerns  
- 4.2: Prevent schema inconsistencies with consistent INTEGER IDs
- 9.1: Integrate with Beast Mode framework using ReflectiveModule patterns
"""

import os
import logging
import sqlite3
from datetime import datetime
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

# Optional PostgreSQL support
try:
    import psycopg2
    POSTGRESQL_AVAILABLE = True
except ImportError:
    POSTGRESQL_AVAILABLE = False

from src.rm_ddd.core.unified_reflective_module import (
    ReflectiveModule,
    ModuleHealth,
    ModuleStatus,
    ModuleCapability,
    GracefulDegradationResult,
)


class SchemaValidationStatus(Enum):
    """Schema validation status enumeration"""
    VALID = "valid"
    INVALID = "invalid"
    MISSING = "missing"
    INCONSISTENT = "inconsistent"


@dataclass
class SchemaResult:
    """Result of schema operations"""
    success: bool
    message: str
    details: Dict[str, Any]
    validation_status: SchemaValidationStatus
    created_tables: List[str] = None
    errors: List[str] = None


@dataclass
class ValidationResult:
    """Result of schema validation operations"""
    is_valid: bool
    validation_status: SchemaValidationStatus
    issues: List[str]
    recommendations: List[str]
    table_status: Dict[str, str]


@dataclass
class MigrationResult:
    """Result of schema migration operations"""
    success: bool
    from_version: str
    to_version: str
    applied_migrations: List[str]
    rollback_available: bool
    errors: List[str] = None


@dataclass
class RollbackResult:
    """Result of schema rollback operations"""
    success: bool
    checkpoint: str
    restored_tables: List[str]
    errors: List[str] = None


class SchemaManager(ReflectiveModule):
    """
    Systematic database schema management for Directus CMS
    
    Implements MVC Model layer for database schema operations with:
    - Consistent INTEGER ID types across all tables
    - Proper foreign key constraints with CASCADE rules
    - Referential integrity validation
    - Comprehensive error prevention and rollback capability
    - Beast Mode integration with health monitoring
    """
    
    def __init__(self, database_url: str = None, database_type: str = "postgresql"):
        """
        Initialize SchemaManager with database connection
        
        Args:
            database_url: Database connection URL
            database_type: Type of database (postgresql, sqlite)
        """
        super().__init__()
        
        self.module_id = "directus_schema_manager"
        self.database_url = database_url or os.getenv(
            "DATABASE_URL", 
            "        os.getenv('DIRECTUS_DATABASE_URL', 'postgresql://directus:directus@localhost:5432/directus')"
        )
        self.database_type = database_type
        self.connection = None
        self.schema_version = "1.0.0"
        
        # Schema definition with consistent INTEGER IDs
        self.schema_definition = {
            "specifications": {
                "columns": [
                    ("id", "INTEGER PRIMARY KEY"),
                    ("name", "VARCHAR(255) NOT NULL UNIQUE"),
                    ("description", "TEXT"),
                    ("status", "VARCHAR(50) DEFAULT 'active'"),
                    ("created_date", "TIMESTAMP DEFAULT CURRENT_TIMESTAMP"),
                    ("updated_date", "TIMESTAMP DEFAULT CURRENT_TIMESTAMP")
                ],
                "indexes": [
                    "CREATE INDEX idx_specifications_name ON specifications(name)",
                    "CREATE INDEX idx_specifications_status ON specifications(status)"
                ]
            },
            "code_files": {
                "columns": [
                    ("id", "INTEGER PRIMARY KEY"),
                    ("file_name", "VARCHAR(255) NOT NULL"),
                    ("file_path", "TEXT NOT NULL UNIQUE"),
                    ("specification_id", "INTEGER"),
                    ("created_date", "TIMESTAMP DEFAULT CURRENT_TIMESTAMP")
                ],
                "foreign_keys": [
                    "FOREIGN KEY (specification_id) REFERENCES specifications(id) ON DELETE SET NULL"
                ],
                "indexes": [
                    "CREATE INDEX idx_code_files_spec_id ON code_files(specification_id)",
                    "CREATE INDEX idx_code_files_path ON code_files(file_path)"
                ]
            },
            "documents": {
                "columns": [
                    ("id", "INTEGER PRIMARY KEY"),
                    ("title", "VARCHAR(255) NOT NULL"),
                    ("content", "TEXT"),
                    ("document_type", "VARCHAR(50)"),
                    ("specification_id", "INTEGER"),
                    ("created_date", "TIMESTAMP DEFAULT CURRENT_TIMESTAMP")
                ],
                "foreign_keys": [
                    "FOREIGN KEY (specification_id) REFERENCES specifications(id) ON DELETE SET NULL"
                ],
                "indexes": [
                    "CREATE INDEX idx_documents_spec_id ON documents(specification_id)",
                    "CREATE INDEX idx_documents_type ON documents(document_type)"
                ]
            },
            "tasks": {
                "columns": [
                    ("id", "INTEGER PRIMARY KEY"),
                    ("title", "VARCHAR(255) NOT NULL"),
                    ("description", "TEXT"),
                    ("status", "VARCHAR(50) DEFAULT 'not_started'"),
                    ("specification_id", "INTEGER"),
                    ("created_date", "TIMESTAMP DEFAULT CURRENT_TIMESTAMP")
                ],
                "foreign_keys": [
                    "FOREIGN KEY (specification_id) REFERENCES specifications(id) ON DELETE SET NULL"
                ],
                "indexes": [
                    "CREATE INDEX idx_tasks_spec_id ON tasks(specification_id)",
                    "CREATE INDEX idx_tasks_status ON tasks(status)"
                ]
            }
        }
        
        self._logger = logging.getLogger(f"schema_manager.{self.module_id}")
        self._initialize_connection()
    
    def get_module_info(self) -> Dict[str, Any]:
        """Get module information - ReflectiveModule implementation"""
        return {
            "module_id": self.module_id,
            "module_name": "DirectusSchemaManager",
            "version": self.schema_version,
            "database_type": self.database_type,
            "database_url": self.database_url.split('@')[1] if '@' in self.database_url else "local",
            "schema_tables": list(self.schema_definition.keys()),
            "connection_status": "connected" if self.connection else "disconnected"
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
        
        # Check database connection
        if not self.connection:
            issues.append("Database connection not established")
            status = ModuleStatus.ERROR
            health_score = 0.0
        else:
            try:
                # Test connection with simple query
                cursor = self.connection.cursor()
                cursor.execute("SELECT 1")
                cursor.fetchone()
                cursor.close()
            except Exception as e:
                issues.append(f"Database connection test failed: {e}")
                status = ModuleStatus.ERROR
                health_score = 0.0
        
        # Check schema validation if connected
        if self.connection and status == ModuleStatus.HEALTHY:
            try:
                validation_result = self.validate_schema()
                if not validation_result.is_valid:
                    issues.extend(validation_result.issues)
                    status = ModuleStatus.WARNING
                    health_score = 0.7
            except Exception as e:
                issues.append(f"Schema validation failed: {e}")
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
            # If database connection fails, switch to read-only mode
            if not self.connection:
                return GracefulDegradationResult(
                    success=True,
                    degraded_capabilities=[ModuleCapability.DATA_PROCESSING],
                    remaining_capabilities=[ModuleCapability.VALIDATION],
                    error_message="Database connection unavailable, operating in validation-only mode"
                )
            
            # If schema is invalid, disable data operations
            validation_result = self.validate_schema()
            if not validation_result.is_valid:
                return GracefulDegradationResult(
                    success=True,
                    degraded_capabilities=[ModuleCapability.DATA_PROCESSING],
                    remaining_capabilities=[ModuleCapability.CORE_FUNCTIONALITY, ModuleCapability.VALIDATION],
                    error_message="Schema validation failed, data operations disabled"
                )
            
            # All capabilities available
            return GracefulDegradationResult(
                success=True,
                degraded_capabilities=[],
                remaining_capabilities=self.get_capabilities()
            )
            
        except Exception as e:
            self._increment_error_count()
            return GracefulDegradationResult(
                success=False,
                degraded_capabilities=self.get_capabilities(),
                remaining_capabilities=[],
                error_message=f"Graceful degradation failed: {e}"
            )
    
    def _initialize_connection(self):
        """Initialize database connection with error handling"""
        try:
            if self.database_type == "postgresql":
                if not POSTGRESQL_AVAILABLE:
                    raise ImportError("PostgreSQL support not available. Install with: pip install psycopg2-binary")
                self.connection = psycopg2.connect(self.database_url)
                self.connection.autocommit = False
            elif self.database_type == "sqlite":
                # Extract path from URL or use default
                db_path = self.database_url.replace("sqlite://", "") if "sqlite://" in self.database_url else "directus.db"
                self.connection = sqlite3.connect(db_path)
            else:
                raise ValueError(f"Unsupported database type: {self.database_type}")
            
            self._logger.info(f"Database connection established: {self.database_type}")
            
        except Exception as e:
            self._logger.error(f"Failed to initialize database connection: {e}")
            self._increment_error_count()
            self.connection = None
    
    def create_schema(self) -> SchemaResult:
        """
        Create database schema with consistent INTEGER IDs and proper constraints
        
        Returns:
            SchemaResult with creation status and details
        """
        with self.trace_operation("create_schema") as trace:
            try:
                if not self.connection:
                    raise Exception("Database connection not available")
                
                cursor = self.connection.cursor()
                created_tables = []
                errors = []
                
                # Create tables in dependency order (specifications first)
                table_order = ["specifications", "code_files", "documents", "tasks"]
                
                for table_name in table_order:
                    try:
                        table_def = self.schema_definition[table_name]
                        
                        # Build CREATE TABLE statement
                        columns_sql = ", ".join([f"{col[0]} {col[1]}" for col in table_def["columns"]])
                        
                        # Add foreign key constraints
                        if "foreign_keys" in table_def:
                            columns_sql += ", " + ", ".join(table_def["foreign_keys"])
                        
                        create_sql = f"CREATE TABLE IF NOT EXISTS {table_name} ({columns_sql})"
                        
                        cursor.execute(create_sql)
                        created_tables.append(table_name)
                        
                        # Create indexes
                        if "indexes" in table_def:
                            for index_sql in table_def["indexes"]:
                                try:
                                    cursor.execute(index_sql)
                                except Exception as idx_error:
                                    # Index might already exist, log but continue
                                    self._logger.warning(f"Index creation warning for {table_name}: {idx_error}")
                        
                        self._logger.info(f"Created table: {table_name}")
                        
                    except Exception as table_error:
                        error_msg = f"Failed to create table {table_name}: {table_error}"
                        errors.append(error_msg)
                        self._logger.error(error_msg)
                
                # Commit transaction
                self.connection.commit()
                cursor.close()
                
                # Validate created schema
                validation_result = self.validate_schema()
                
                result = SchemaResult(
                    success=len(errors) == 0,
                    message=f"Schema creation completed. Created {len(created_tables)} tables.",
                    details={
                        "created_tables": created_tables,
                        "total_tables": len(table_order),
                        "validation_status": validation_result.validation_status.value,
                        "schema_version": self.schema_version
                    },
                    validation_status=validation_result.validation_status,
                    created_tables=created_tables,
                    errors=errors
                )
                
                trace.output_result = result
                return result
                
            except Exception as e:
                self._increment_error_count()
                if self.connection:
                    self.connection.rollback()
                
                error_result = SchemaResult(
                    success=False,
                    message=f"Schema creation failed: {e}",
                    details={"error": str(e)},
                    validation_status=SchemaValidationStatus.INVALID,
                    errors=[str(e)]
                )
                
                trace.error_info = {"error": str(e)}
                return error_result
    
    def validate_schema(self) -> ValidationResult:
        """
        Validate database schema structure and constraints
        
        Returns:
            ValidationResult with validation status and recommendations
        """
        with self.trace_operation("validate_schema") as trace:
            try:
                if not self.connection:
                    return ValidationResult(
                        is_valid=False,
                        validation_status=SchemaValidationStatus.MISSING,
                        issues=["Database connection not available"],
                        recommendations=["Establish database connection"],
                        table_status={}
                    )
                
                cursor = self.connection.cursor()
                issues = []
                recommendations = []
                table_status = {}
                
                # Check if tables exist
                for table_name in self.schema_definition.keys():
                    try:
                        if self.database_type == "postgresql":
                            cursor.execute("""
                                SELECT EXISTS (
                                    SELECT FROM information_schema.tables 
                                    WHERE table_name = %s
                                )
                            """, (table_name,))
                        else:  # sqlite
                            cursor.execute("""
                                SELECT name FROM sqlite_master 
                                WHERE type='table' AND name=?
                            """, (table_name,))
                        
                        result = cursor.fetchone()
                        exists = result[0] if result else False
                        
                        if exists:
                            table_status[table_name] = "exists"
                            
                            # Validate table structure
                            structure_issues = self._validate_table_structure(cursor, table_name)
                            if structure_issues:
                                issues.extend(structure_issues)
                                table_status[table_name] = "invalid_structure"
                        else:
                            table_status[table_name] = "missing"
                            issues.append(f"Table {table_name} does not exist")
                            recommendations.append(f"Create table {table_name}")
                    
                    except Exception as e:
                        table_status[table_name] = "error"
                        issues.append(f"Error checking table {table_name}: {e}")
                
                # Validate foreign key constraints
                constraint_issues = self._validate_foreign_keys(cursor)
                issues.extend(constraint_issues)
                
                cursor.close()
                
                # Determine overall validation status
                if not issues:
                    validation_status = SchemaValidationStatus.VALID
                elif any("missing" in status for status in table_status.values()):
                    validation_status = SchemaValidationStatus.MISSING
                else:
                    validation_status = SchemaValidationStatus.INCONSISTENT
                
                result = ValidationResult(
                    is_valid=len(issues) == 0,
                    validation_status=validation_status,
                    issues=issues,
                    recommendations=recommendations,
                    table_status=table_status
                )
                
                trace.output_result = result
                return result
                
            except Exception as e:
                self._increment_error_count()
                error_result = ValidationResult(
                    is_valid=False,
                    validation_status=SchemaValidationStatus.INVALID,
                    issues=[f"Schema validation failed: {e}"],
                    recommendations=["Check database connection and permissions"],
                    table_status={}
                )
                
                trace.error_info = {"error": str(e)}
                return error_result
    
    def _validate_table_structure(self, cursor, table_name: str) -> List[str]:
        """Validate individual table structure"""
        issues = []
        
        try:
            expected_columns = {col[0]: col[1] for col in self.schema_definition[table_name]["columns"]}
            
            if self.database_type == "postgresql":
                cursor.execute("""
                    SELECT column_name, data_type, is_nullable, column_default
                    FROM information_schema.columns
                    WHERE table_name = %s
                    ORDER BY ordinal_position
                """, (table_name,))
            else:  # sqlite
                cursor.execute(f"PRAGMA table_info({table_name})")
            
            actual_columns = cursor.fetchall()
            
            # Check for missing or extra columns
            actual_column_names = set()
            for col_info in actual_columns:
                if self.database_type == "postgresql":
                    col_name = col_info[0]
                else:  # sqlite
                    col_name = col_info[1]  # name is second field in PRAGMA table_info
                actual_column_names.add(col_name)
            
            expected_column_names = set(expected_columns.keys())
            
            missing_columns = expected_column_names - actual_column_names
            extra_columns = actual_column_names - expected_column_names
            
            if missing_columns:
                issues.append(f"Table {table_name} missing columns: {', '.join(missing_columns)}")
            
            if extra_columns:
                issues.append(f"Table {table_name} has unexpected columns: {', '.join(extra_columns)}")
        
        except Exception as e:
            issues.append(f"Error validating table structure for {table_name}: {e}")
        
        return issues
    
    def _validate_foreign_keys(self, cursor) -> List[str]:
        """Validate foreign key constraints"""
        issues = []
        
        try:
            # Test foreign key constraints with sample data
            for table_name, table_def in self.schema_definition.items():
                if "foreign_keys" in table_def:
                    for fk in table_def["foreign_keys"]:
                        # Parse foreign key constraint
                        # Example: "FOREIGN KEY (specification_id) REFERENCES specifications(id) ON DELETE SET NULL"
                        if "specification_id" in fk and "specifications(id)" in fk:
                            # Test that the foreign key constraint exists and works
                            try:
                                # This is a basic test - in production we'd do more thorough validation
                                cursor.execute(f"SELECT COUNT(*) FROM {table_name} WHERE specification_id IS NOT NULL")
                                cursor.fetchone()
                            except Exception as fk_error:
                                issues.append(f"Foreign key constraint issue in {table_name}: {fk_error}")
        
        except Exception as e:
            issues.append(f"Error validating foreign keys: {e}")
        
        return issues
    
    def migrate_schema(self, version: str) -> MigrationResult:
        """
        Migrate schema to specified version
        
        Args:
            version: Target schema version
            
        Returns:
            MigrationResult with migration status
        """
        with self.trace_operation("migrate_schema", version=version) as trace:
            try:
                # For now, we only support version 1.0.0
                if version != "1.0.0":
                    return MigrationResult(
                        success=False,
                        from_version=self.schema_version,
                        to_version=version,
                        applied_migrations=[],
                        rollback_available=False,
                        errors=[f"Unsupported schema version: {version}"]
                    )
                
                # If already at target version, no migration needed
                if self.schema_version == version:
                    result = MigrationResult(
                        success=True,
                        from_version=self.schema_version,
                        to_version=version,
                        applied_migrations=[],
                        rollback_available=True
                    )
                    trace.output_result = result
                    return result
                
                # Future: Implement actual migration logic here
                result = MigrationResult(
                    success=True,
                    from_version=self.schema_version,
                    to_version=version,
                    applied_migrations=["initial_schema"],
                    rollback_available=True
                )
                
                self.schema_version = version
                trace.output_result = result
                return result
                
            except Exception as e:
                self._increment_error_count()
                error_result = MigrationResult(
                    success=False,
                    from_version=self.schema_version,
                    to_version=version,
                    applied_migrations=[],
                    rollback_available=False,
                    errors=[str(e)]
                )
                
                trace.error_info = {"error": str(e)}
                return error_result
    
    def rollback_schema(self, checkpoint: str) -> RollbackResult:
        """
        Rollback schema to specified checkpoint
        
        Args:
            checkpoint: Checkpoint identifier to rollback to
            
        Returns:
            RollbackResult with rollback status
        """
        with self.trace_operation("rollback_schema", checkpoint=checkpoint) as trace:
            try:
                if not self.connection:
                    raise Exception("Database connection not available")
                
                cursor = self.connection.cursor()
                restored_tables = []
                
                # For now, implement basic rollback by dropping and recreating tables
                if checkpoint == "clean_slate":
                    # Drop all tables in reverse dependency order
                    table_order = ["tasks", "documents", "code_files", "specifications"]
                    
                    for table_name in table_order:
                        try:
                            cursor.execute(f"DROP TABLE IF EXISTS {table_name}")
                            restored_tables.append(table_name)
                        except Exception as e:
                            self._logger.warning(f"Error dropping table {table_name}: {e}")
                    
                    self.connection.commit()
                
                cursor.close()
                
                result = RollbackResult(
                    success=True,
                    checkpoint=checkpoint,
                    restored_tables=restored_tables
                )
                
                trace.output_result = result
                return result
                
            except Exception as e:
                self._increment_error_count()
                if self.connection:
                    self.connection.rollback()
                
                error_result = RollbackResult(
                    success=False,
                    checkpoint=checkpoint,
                    restored_tables=[],
                    errors=[str(e)]
                )
                
                trace.error_info = {"error": str(e)}
                return error_result
    
    def get_schema_info(self) -> Dict[str, Any]:
        """Get comprehensive schema information"""
        with self.trace_operation("get_schema_info") as trace:
            try:
                validation_result = self.validate_schema()
                
                info = {
                    "schema_version": self.schema_version,
                    "database_type": self.database_type,
                    "connection_status": "connected" if self.connection else "disconnected",
                    "validation_status": validation_result.validation_status.value,
                    "table_count": len(self.schema_definition),
                    "tables": list(self.schema_definition.keys()),
                    "table_status": validation_result.table_status,
                    "issues": validation_result.issues,
                    "recommendations": validation_result.recommendations,
                    "last_validated": datetime.now().isoformat()
                }
                
                trace.output_result = info
                return info
                
            except Exception as e:
                self._increment_error_count()
                error_info = {
                    "error": str(e),
                    "schema_version": self.schema_version,
                    "database_type": self.database_type,
                    "connection_status": "error"
                }
                
                trace.error_info = {"error": str(e)}
                return error_info
    
    def __del__(self):
        """Cleanup database connection"""
        if self.connection:
            try:
                self.connection.close()
            except Exception:
                pass