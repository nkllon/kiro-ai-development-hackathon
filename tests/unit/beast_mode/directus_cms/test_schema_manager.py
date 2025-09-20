"""
Unit Tests for Directus CMS Schema Manager

Comprehensive test suite for the SchemaManager class ensuring:
- Proper ReflectiveModule implementation
- Schema creation and validation
- Error handling and rollback capability
- Beast Mode integration compliance

Requirements Tested:
- 1.1: Database schema management infrastructure
- 2.2: MVC architecture with proper separation of concerns
- 4.2: Prevent schema inconsistencies with consistent INTEGER IDs
- 9.1: Beast Mode framework integration
"""

import unittest
import tempfile
import os
import sqlite3
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

# Import the modules under test
from src.beast_mode.directus_cms.schema_manager import (
    SchemaManager,
    SchemaResult,
    ValidationResult,
    MigrationResult,
    RollbackResult,
    SchemaValidationStatus
)
from src.rm_ddd.core.unified_reflective_module import (
    ModuleHealth,
    ModuleStatus,
    ModuleCapability
)


class TestSchemaManager(unittest.TestCase):
    """Test suite for SchemaManager class"""
    
    def setUp(self):
        """Set up test environment"""
        # Create temporary SQLite database for testing
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.temp_db.close()
        
        self.test_db_url = f"sqlite://{self.temp_db.name}"
        
        # Initialize SchemaManager with test database
        self.schema_manager = SchemaManager(
            database_url=self.test_db_url,
            database_type="sqlite"
        )
    
    def tearDown(self):
        """Clean up test environment"""
        # Close database connection
        if hasattr(self.schema_manager, 'connection') and self.schema_manager.connection:
            self.schema_manager.connection.close()
        
        # Remove temporary database file
        try:
            os.unlink(self.temp_db.name)
        except FileNotFoundError:
            pass
    
    def test_reflective_module_implementation(self):
        """Test ReflectiveModule interface implementation"""
        # Test get_module_info
        module_info = self.schema_manager.get_module_info()
        self.assertIsInstance(module_info, dict)
        self.assertEqual(module_info["module_id"], "directus_schema_manager")
        self.assertEqual(module_info["module_name"], "DirectusSchemaManager")
        self.assertIn("version", module_info)
        self.assertIn("database_type", module_info)
        
        # Test get_capabilities
        capabilities = self.schema_manager.get_capabilities()
        self.assertIsInstance(capabilities, list)
        self.assertIn(ModuleCapability.CORE_FUNCTIONALITY, capabilities)
        self.assertIn(ModuleCapability.DATA_PROCESSING, capabilities)
        self.assertIn(ModuleCapability.VALIDATION, capabilities)
        
        # Test get_health_status
        health_status = self.schema_manager.get_health_status()
        self.assertIsInstance(health_status, ModuleHealth)
        self.assertEqual(health_status.module_id, "directus_schema_manager")
        self.assertIsInstance(health_status.status, ModuleStatus)
        self.assertIsInstance(health_status.health_score, float)
        self.assertIsInstance(health_status.issues, list)
        
        # Test graceful_degradation
        degradation_result = self.schema_manager.graceful_degradation()
        self.assertIsNotNone(degradation_result)
        self.assertIsInstance(degradation_result.success, bool)
    
    def test_schema_creation_success(self):
        """Test successful schema creation"""
        # Create schema
        result = self.schema_manager.create_schema()
        
        # Verify result
        self.assertIsInstance(result, SchemaResult)
        self.assertTrue(result.success)
        self.assertEqual(result.validation_status, SchemaValidationStatus.VALID)
        self.assertIsInstance(result.created_tables, list)
        self.assertEqual(len(result.created_tables), 4)  # specifications, code_files, documents, tasks
        
        # Verify tables were created
        expected_tables = ["specifications", "code_files", "documents", "tasks"]
        for table in expected_tables:
            self.assertIn(table, result.created_tables)
        
        # Verify database actually contains the tables
        cursor = self.schema_manager.connection.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        actual_tables = [row[0] for row in cursor.fetchall()]
        cursor.close()
        
        for table in expected_tables:
            self.assertIn(table, actual_tables)
    
    def test_schema_validation_valid(self):
        """Test schema validation with valid schema"""
        # Create schema first
        self.schema_manager.create_schema()
        
        # Validate schema
        result = self.schema_manager.validate_schema()
        
        # Verify validation result
        self.assertIsInstance(result, ValidationResult)
        self.assertTrue(result.is_valid)
        self.assertEqual(result.validation_status, SchemaValidationStatus.VALID)
        self.assertEqual(len(result.issues), 0)
        self.assertIsInstance(result.table_status, dict)
        
        # Verify all tables are marked as existing
        expected_tables = ["specifications", "code_files", "documents", "tasks"]
        for table in expected_tables:
            self.assertEqual(result.table_status[table], "exists")
    
    def test_schema_validation_missing_tables(self):
        """Test schema validation with missing tables"""
        # Don't create schema, just validate
        result = self.schema_manager.validate_schema()
        
        # Verify validation result
        self.assertIsInstance(result, ValidationResult)
        self.assertFalse(result.is_valid)
        self.assertEqual(result.validation_status, SchemaValidationStatus.MISSING)
        self.assertGreater(len(result.issues), 0)
        
        # Verify all tables are marked as missing
        expected_tables = ["specifications", "code_files", "documents", "tasks"]
        for table in expected_tables:
            self.assertEqual(result.table_status[table], "missing")
    
    def test_foreign_key_constraints(self):
        """Test that foreign key constraints are properly created"""
        # Create schema
        self.schema_manager.create_schema()
        
        # Test foreign key constraint by inserting data
        cursor = self.schema_manager.connection.cursor()
        
        # Insert a specification
        cursor.execute("""
            INSERT INTO specifications (name, description, status)
            VALUES (?, ?, ?)
        """, ("test-spec", "Test specification", "active"))
        
        spec_id = cursor.lastrowid
        
        # Insert related code file
        cursor.execute("""
            INSERT INTO code_files (file_name, file_path, specification_id)
            VALUES (?, ?, ?)
        """, ("test.py", "/path/to/test.py", spec_id))
        
        # Insert related document
        cursor.execute("""
            INSERT INTO documents (title, content, document_type, specification_id)
            VALUES (?, ?, ?, ?)
        """, ("Test Doc", "Test content", "requirements", spec_id))
        
        # Insert related task
        cursor.execute("""
            INSERT INTO tasks (title, description, status, specification_id)
            VALUES (?, ?, ?, ?)
        """, ("Test Task", "Test task description", "not_started", spec_id))
        
        self.schema_manager.connection.commit()
        
        # Verify relationships exist
        cursor.execute("""
            SELECT cf.file_name, d.title, t.title
            FROM specifications s
            LEFT JOIN code_files cf ON s.id = cf.specification_id
            LEFT JOIN documents d ON s.id = d.specification_id
            LEFT JOIN tasks t ON s.id = t.specification_id
            WHERE s.id = ?
        """, (spec_id,))
        
        results = cursor.fetchall()
        cursor.close()
        
        self.assertGreater(len(results), 0)
        self.assertEqual(results[0][0], "test.py")
        self.assertEqual(results[0][1], "Test Doc")
        self.assertEqual(results[0][2], "Test Task")
    
    def test_consistent_integer_ids(self):
        """Test that all ID fields use consistent INTEGER type"""
        # Create schema
        self.schema_manager.create_schema()
        
        # Check table schemas
        cursor = self.schema_manager.connection.cursor()
        
        tables_to_check = ["specifications", "code_files", "documents", "tasks"]
        
        for table_name in tables_to_check:
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns = cursor.fetchall()
            
            # Find ID column
            id_column = None
            for col in columns:
                if col[1] == "id":  # column name
                    id_column = col
                    break
            
            self.assertIsNotNone(id_column, f"ID column not found in {table_name}")
            
            # Verify ID column is INTEGER and PRIMARY KEY
            column_type = id_column[2].upper()  # column type
            is_primary_key = id_column[5] == 1  # pk flag
            
            self.assertIn("INTEGER", column_type, f"ID column in {table_name} is not INTEGER: {column_type}")
            self.assertTrue(is_primary_key, f"ID column in {table_name} is not PRIMARY KEY")
        
        cursor.close()
    
    def test_rollback_capability(self):
        """Test schema rollback functionality"""
        # Create schema first
        create_result = self.schema_manager.create_schema()
        self.assertTrue(create_result.success)
        
        # Verify tables exist
        validation_result = self.schema_manager.validate_schema()
        self.assertTrue(validation_result.is_valid)
        
        # Perform rollback
        rollback_result = self.schema_manager.rollback_schema("clean_slate")
        
        # Verify rollback result
        self.assertIsInstance(rollback_result, RollbackResult)
        self.assertTrue(rollback_result.success)
        self.assertEqual(rollback_result.checkpoint, "clean_slate")
        self.assertIsInstance(rollback_result.restored_tables, list)
        
        # Verify tables are gone
        cursor = self.schema_manager.connection.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        remaining_tables = [row[0] for row in cursor.fetchall()]
        cursor.close()
        
        expected_tables = ["specifications", "code_files", "documents", "tasks"]
        for table in expected_tables:
            self.assertNotIn(table, remaining_tables)
    
    def test_migration_functionality(self):
        """Test schema migration functionality"""
        # Test migration to current version
        result = self.schema_manager.migrate_schema("1.0.0")
        
        self.assertIsInstance(result, MigrationResult)
        self.assertTrue(result.success)
        self.assertEqual(result.to_version, "1.0.0")
        self.assertTrue(result.rollback_available)
        
        # Test migration to unsupported version
        result = self.schema_manager.migrate_schema("2.0.0")
        
        self.assertIsInstance(result, MigrationResult)
        self.assertFalse(result.success)
        self.assertIsInstance(result.errors, list)
        self.assertGreater(len(result.errors), 0)
    
    def test_error_handling_no_connection(self):
        """Test error handling when database connection is not available"""
        # Create SchemaManager with invalid database URL
        invalid_manager = SchemaManager(
            database_url="postgresql://invalid:invalid@nonexistent:5432/invalid",
            database_type="postgresql"
        )
        
        # Test health status with no connection
        health_status = invalid_manager.get_health_status()
        self.assertEqual(health_status.status, ModuleStatus.ERROR)
        self.assertGreater(len(health_status.issues), 0)
        
        # Test graceful degradation
        degradation_result = invalid_manager.graceful_degradation()
        self.assertTrue(degradation_result.success)
        self.assertIn(ModuleCapability.DATA_PROCESSING, degradation_result.degraded_capabilities)
    
    def test_operation_tracing(self):
        """Test operation tracing functionality"""
        # Create schema with tracing
        result = self.schema_manager.create_schema()
        self.assertTrue(result.success)
        
        # Get operation traces
        traces = self.schema_manager.get_operation_traces()
        self.assertIsInstance(traces, list)
        self.assertGreater(len(traces), 0)
        
        # Verify trace contains create_schema operation
        create_trace = None
        for trace in traces:
            if trace.operation_name == "create_schema":
                create_trace = trace
                break
        
        self.assertIsNotNone(create_trace)
        self.assertEqual(create_trace.component_name, "SchemaManager")
        self.assertIsNotNone(create_trace.start_time)
        self.assertIsNotNone(create_trace.end_time)
        self.assertIsNotNone(create_trace.duration_ms)
    
    def test_performance_metrics(self):
        """Test performance metrics collection"""
        # Perform some operations
        self.schema_manager.create_schema()
        self.schema_manager.validate_schema()
        
        # Get performance metrics
        metrics = self.schema_manager.get_performance_metrics()
        
        self.assertIsInstance(metrics, dict)
        self.assertIn("operation_count", metrics)
        self.assertIn("total_operation_time_ms", metrics)
        self.assertIn("average_operation_time_ms", metrics)
        self.assertIn("error_count", metrics)
        self.assertIn("uptime_seconds", metrics)
        
        self.assertGreater(metrics["operation_count"], 0)
        self.assertGreaterEqual(metrics["total_operation_time_ms"], 0)
    
    def test_schema_info_retrieval(self):
        """Test schema information retrieval"""
        # Create schema first
        self.schema_manager.create_schema()
        
        # Get schema info
        info = self.schema_manager.get_schema_info()
        
        self.assertIsInstance(info, dict)
        self.assertIn("schema_version", info)
        self.assertIn("database_type", info)
        self.assertIn("connection_status", info)
        self.assertIn("validation_status", info)
        self.assertIn("table_count", info)
        self.assertIn("tables", info)
        self.assertIn("table_status", info)
        
        self.assertEqual(info["schema_version"], "1.0.0")
        self.assertEqual(info["database_type"], "sqlite")
        self.assertEqual(info["connection_status"], "connected")
        self.assertEqual(info["table_count"], 4)
        self.assertEqual(len(info["tables"]), 4)
    
    @patch('src.beast_mode.directus_cms.schema_manager.psycopg2')
    def test_postgresql_connection_attempt(self, mock_psycopg2):
        """Test PostgreSQL connection attempt (mocked)"""
        # Mock PostgreSQL connection
        mock_connection = Mock()
        mock_cursor = Mock()
        mock_connection.cursor.return_value = mock_cursor
        mock_psycopg2.connect.return_value = mock_connection
        
        # Create SchemaManager with PostgreSQL
        pg_manager = SchemaManager(
            database_url="postgresql://test:test@localhost:5432/test",
            database_type="postgresql"
        )
        
        # Verify connection was attempted
        mock_psycopg2.connect.assert_called_once()
        
        # Test module info
        module_info = pg_manager.get_module_info()
        self.assertEqual(module_info["database_type"], "postgresql")
    
    def test_cli_interface_generation(self):
        """Test CLI interface generation from ReflectiveModule"""
        # Get CLI interface
        cli_interface = self.schema_manager.get_cli_interface()
        
        self.assertIsInstance(cli_interface, dict)
        self.assertIn("module_id", cli_interface)
        self.assertIn("module_name", cli_interface)
        self.assertIn("commands", cli_interface)
        
        # Verify key methods are exposed as CLI commands
        commands = cli_interface["commands"]
        expected_commands = [
            "create_schema",
            "validate_schema",
            "migrate_schema",
            "rollback_schema",
            "get_schema_info"
        ]
        
        for cmd in expected_commands:
            self.assertIn(cmd, commands)
            self.assertIn("description", commands[cmd])
            self.assertIn("parameters", commands[cmd])
    
    def test_cli_command_execution(self):
        """Test CLI command execution"""
        # Execute create_schema command via CLI
        result = self.schema_manager.execute_cli_command("create_schema")
        
        self.assertIsInstance(result, dict)
        self.assertTrue(result["success"])
        self.assertEqual(result["command"], "create_schema")
        self.assertIn("result", result)
        
        # Verify the actual schema was created
        schema_result = result["result"]
        self.assertIsInstance(schema_result, SchemaResult)
        self.assertTrue(schema_result.success)
    
    def test_cli_help_generation(self):
        """Test CLI help generation"""
        # Generate general help
        general_help = self.schema_manager.generate_cli_help()
        self.assertIsInstance(general_help, str)
        self.assertIn("DirectusSchemaManager", general_help)
        self.assertIn("create_schema", general_help)
        
        # Generate specific command help
        command_help = self.schema_manager.generate_cli_help("create_schema")
        self.assertIsInstance(command_help, str)
        self.assertIn("create_schema", command_help)
        self.assertIn("Description:", command_help)


class TestSchemaManagerIntegration(unittest.TestCase):
    """Integration tests for SchemaManager with real database operations"""
    
    def setUp(self):
        """Set up integration test environment"""
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.temp_db.close()
        
        self.test_db_url = f"sqlite://{self.temp_db.name}"
        self.schema_manager = SchemaManager(
            database_url=self.test_db_url,
            database_type="sqlite"
        )
    
    def tearDown(self):
        """Clean up integration test environment"""
        if hasattr(self.schema_manager, 'connection') and self.schema_manager.connection:
            self.schema_manager.connection.close()
        
        try:
            os.unlink(self.temp_db.name)
        except FileNotFoundError:
            pass
    
    def test_full_schema_lifecycle(self):
        """Test complete schema lifecycle: create -> validate -> populate -> rollback"""
        # 1. Create schema
        create_result = self.schema_manager.create_schema()
        self.assertTrue(create_result.success)
        self.assertEqual(len(create_result.created_tables), 4)
        
        # 2. Validate schema
        validation_result = self.schema_manager.validate_schema()
        self.assertTrue(validation_result.is_valid)
        self.assertEqual(validation_result.validation_status, SchemaValidationStatus.VALID)
        
        # 3. Populate with test data
        cursor = self.schema_manager.connection.cursor()
        
        # Insert test specification
        cursor.execute("""
            INSERT INTO specifications (name, description, status)
            VALUES (?, ?, ?)
        """, ("integration-test-spec", "Integration test specification", "active"))
        
        spec_id = cursor.lastrowid
        
        # Insert related items
        cursor.execute("""
            INSERT INTO code_files (file_name, file_path, specification_id)
            VALUES (?, ?, ?)
        """, ("integration_test.py", "/test/integration_test.py", spec_id))
        
        cursor.execute("""
            INSERT INTO documents (title, content, document_type, specification_id)
            VALUES (?, ?, ?, ?)
        """, ("Integration Test Requirements", "Test requirements content", "requirements", spec_id))
        
        cursor.execute("""
            INSERT INTO tasks (title, description, status, specification_id)
            VALUES (?, ?, ?, ?)
        """, ("Integration Test Task", "Test task description", "in_progress", spec_id))
        
        self.schema_manager.connection.commit()
        cursor.close()
        
        # 4. Verify data integrity
        cursor = self.schema_manager.connection.cursor()
        cursor.execute("""
            SELECT s.name, cf.file_name, d.title, t.title
            FROM specifications s
            JOIN code_files cf ON s.id = cf.specification_id
            JOIN documents d ON s.id = d.specification_id
            JOIN tasks t ON s.id = t.specification_id
            WHERE s.id = ?
        """, (spec_id,))
        
        result = cursor.fetchone()
        cursor.close()
        
        self.assertIsNotNone(result)
        self.assertEqual(result[0], "integration-test-spec")
        self.assertEqual(result[1], "integration_test.py")
        self.assertEqual(result[2], "Integration Test Requirements")
        self.assertEqual(result[3], "Integration Test Task")
        
        # 5. Test rollback
        rollback_result = self.schema_manager.rollback_schema("clean_slate")
        self.assertTrue(rollback_result.success)
        
        # 6. Verify rollback worked
        final_validation = self.schema_manager.validate_schema()
        self.assertFalse(final_validation.is_valid)
        self.assertEqual(final_validation.validation_status, SchemaValidationStatus.MISSING)


if __name__ == '__main__':
    # Configure logging for tests
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Run tests
    unittest.main(verbosity=2)