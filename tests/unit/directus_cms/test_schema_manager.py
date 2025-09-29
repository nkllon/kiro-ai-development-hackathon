#!/usr/bin/env python3
"""
Unit tests for Directus CMS SchemaManager

Tests the systematic database schema management functionality including:
- Schema creation and validation
- Database connection management
- Error handling and recovery
- Beast Mode integration
"""

import unittest
import tempfile
import os
import sqlite3
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from src.beast_mode.directus_cms.schema_manager import (
    SchemaManager,
    SchemaValidationStatus,
    SchemaResult
)
from src.rm_ddd.core.unified_reflective_module import ModuleStatus, ModuleCapability


class TestSchemaManager(unittest.TestCase):
    """Test cases for SchemaManager class"""
    
    def setUp(self):
        """Set up test fixtures"""
        # Create temporary database for testing
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.temp_db.close()
        self.db_path = self.temp_db.name
        
        # Create SchemaManager instance
        self.schema_manager = SchemaManager()
        
        # Mock database configuration
        self.test_config = {
            'database_type': 'sqlite',
            'database_path': self.db_path,
            'host': 'localhost',
            'port': 5432,
            'database': 'test_directus',
            'username': 'test_user',
            'password': 'test_pass'
        }
    
    def tearDown(self):
        """Clean up test fixtures"""
        # Remove temporary database
        if os.path.exists(self.db_path):
            os.unlink(self.db_path)
    
    def test_module_info(self):
        """Test that SchemaManager provides correct module information"""
        module_info = self.schema_manager.get_module_info()
        
        self.assertIsInstance(module_info, dict)
        self.assertIn('module_id', module_info)
        self.assertIn('module_name', module_info)
        self.assertIn('version', module_info)
        self.assertEqual(module_info['module_id'], 'directus_schema_manager')
    
    def test_capabilities(self):
        """Test that SchemaManager declares correct capabilities"""
        capabilities = self.schema_manager.get_capabilities()
        
        self.assertIsInstance(capabilities, list)
        self.assertIn(ModuleCapability.DATA_PROCESSING, capabilities)
        self.assertIn(ModuleCapability.VALIDATION, capabilities)
    
    def test_health_status(self):
        """Test health status reporting"""
        health = self.schema_manager.get_health_status()
        
        self.assertIsNotNone(health)
        self.assertEqual(health.module_id, 'directus_schema_manager')
        self.assertIsInstance(health.status, ModuleStatus)
        self.assertIsInstance(health.health_score, float)
        self.assertGreaterEqual(health.health_score, 0.0)
        self.assertLessEqual(health.health_score, 1.0)
    
    def test_graceful_degradation(self):
        """Test graceful degradation functionality"""
        result = self.schema_manager.graceful_degradation()
        
        self.assertIsNotNone(result)
        self.assertIsInstance(result.success, bool)
        self.assertIsInstance(result.degraded_capabilities, list)
        self.assertIsInstance(result.remaining_capabilities, list)
    
    def test_sqlite_connection_creation(self):
        """Test SQLite database connection creation"""
        with patch.object(self.schema_manager, '_create_sqlite_connection') as mock_create:
            mock_connection = Mock()
            mock_create.return_value = mock_connection
            
            connection = self.schema_manager._create_sqlite_connection(self.db_path)
            
            mock_create.assert_called_once_with(self.db_path)
            self.assertEqual(connection, mock_connection)
    
    @patch('src.beast_mode.directus_cms.schema_manager.psycopg2')
    def test_postgresql_connection_creation(self, mock_psycopg2):
        """Test PostgreSQL database connection creation"""
        mock_connection = Mock()
        mock_psycopg2.connect.return_value = mock_connection
        
        config = {
            'host': 'localhost',
            'port': 5432,
            'database': 'test_db',
            'username': 'test_user',
            'password': 'test_pass'
        }
        
        connection = self.schema_manager._create_postgresql_connection(config)
        
        mock_psycopg2.connect.assert_called_once_with(
            host='localhost',
            port=5432,
            database='test_db',
            user='test_user',
            password='test_pass'
        )
        self.assertEqual(connection, mock_connection)
    
    def test_schema_creation_sqlite(self):
        """Test schema creation with SQLite database"""
        # Create actual SQLite connection for testing
        connection = sqlite3.connect(self.db_path)
        
        # Test schema creation
        result = self.schema_manager._create_core_schema(connection, 'sqlite')
        
        self.assertIsInstance(result, SchemaResult)
        self.assertTrue(result.success)
        
        # Verify tables were created
        cursor = connection.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        
        expected_tables = ['specifications', 'code_files', 'documents', 'tasks']
        for table in expected_tables:
            self.assertIn(table, tables)
        
        connection.close()
    
    def test_schema_validation(self):
        """Test schema validation functionality"""
        # Create schema first
        connection = sqlite3.connect(self.db_path)
        self.schema_manager._create_core_schema(connection, 'sqlite')
        
        # Test validation
        status = self.schema_manager._validate_schema(connection, 'sqlite')
        
        self.assertEqual(status, SchemaValidationStatus.VALID)
        connection.close()
    
    def test_schema_validation_missing_tables(self):
        """Test schema validation with missing tables"""
        # Create empty database
        connection = sqlite3.connect(self.db_path)
        
        # Test validation should detect missing tables
        status = self.schema_manager._validate_schema(connection, 'sqlite')
        
        self.assertEqual(status, SchemaValidationStatus.MISSING)
        connection.close()
    
    def test_foreign_key_constraints(self):
        """Test foreign key constraint creation and validation"""
        connection = sqlite3.connect(self.db_path)
        
        # Enable foreign key constraints
        connection.execute("PRAGMA foreign_keys = ON")
        
        # Create schema
        self.schema_manager._create_core_schema(connection, 'sqlite')
        
        # Insert test data
        cursor = connection.cursor()
        
        # Insert specification
        cursor.execute("""
            INSERT INTO specifications (id, name, description, status, created_at)
            VALUES (1, 'test-spec', 'Test specification', 'active', ?)
        """, (datetime.now(),))
        
        # Insert document with valid foreign key
        cursor.execute("""
            INSERT INTO documents (id, specification_id, document_type, title, content, created_at)
            VALUES (1, 1, 'requirements', 'Test Requirements', 'Test content', ?)
        """, (datetime.now(),))
        
        # Try to insert document with invalid foreign key (should fail)
        with self.assertRaises(sqlite3.IntegrityError):
            cursor.execute("""
                INSERT INTO documents (id, specification_id, document_type, title, content, created_at)
                VALUES (2, 999, 'requirements', 'Invalid', 'Invalid content', ?)
            """, (datetime.now(),))
        
        connection.close()
    
    def test_rollback_capability(self):
        """Test rollback capability for failed operations"""
        connection = sqlite3.connect(self.db_path)
        
        try:
            # Start transaction
            connection.execute("BEGIN TRANSACTION")
            
            # Create partial schema
            connection.execute("""
                CREATE TABLE specifications (
                    id INTEGER PRIMARY KEY,
                    name TEXT NOT NULL
                )
            """)
            
            # Simulate error and rollback
            connection.execute("ROLLBACK")
            
            # Verify table was not created
            cursor = connection.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='specifications'")
            result = cursor.fetchone()
            
            self.assertIsNone(result)
            
        finally:
            connection.close()
    
    def test_error_handling(self):
        """Test error handling for database operations"""
        # Test with invalid database path
        invalid_path = "/invalid/path/database.db"
        
        with patch.object(self.schema_manager, '_create_sqlite_connection') as mock_create:
            mock_create.side_effect = Exception("Database connection failed")
            
            result = self.schema_manager.create_schema({
                'database_type': 'sqlite',
                'database_path': invalid_path
            })
            
            self.assertIsInstance(result, SchemaResult)
            self.assertFalse(result.success)
            self.assertIn("error", result.message.lower())
    
    def test_observation_emission(self):
        """Test that schema operations emit observations"""
        with patch.object(self.schema_manager, 'emit_observation') as mock_emit:
            # Perform schema operation
            self.schema_manager.create_schema(self.test_config)
            
            # Verify observation was emitted
            mock_emit.assert_called()
            
            # Check observation details
            call_args = mock_emit.call_args
            self.assertIn('message', call_args[1] if call_args[1] else call_args[0])
    
    def test_performance_metrics(self):
        """Test performance metrics collection"""
        # Perform some operations
        self.schema_manager.create_schema(self.test_config)
        
        # Get performance metrics
        metrics = self.schema_manager.get_performance_metrics()
        
        self.assertIsInstance(metrics, dict)
        self.assertIn('operation_count', metrics)
        self.assertIn('total_operation_time_ms', metrics)
        self.assertGreater(metrics['operation_count'], 0)
    
    def test_concurrent_access_safety(self):
        """Test thread safety for concurrent database access"""
        import threading
        import time
        
        results = []
        errors = []
        
        def create_schema_worker():
            try:
                result = self.schema_manager.create_schema(self.test_config)
                results.append(result)
            except Exception as e:
                errors.append(e)
        
        # Create multiple threads
        threads = []
        for i in range(3):
            thread = threading.Thread(target=create_schema_worker)
            threads.append(thread)
        
        # Start all threads
        for thread in threads:
            thread.start()
        
        # Wait for completion
        for thread in threads:
            thread.join(timeout=10)
        
        # Verify results
        self.assertEqual(len(results), 3)
        self.assertEqual(len(errors), 0)
        
        # At least one should succeed
        successful_results = [r for r in results if r.success]
        self.assertGreater(len(successful_results), 0)


class TestSchemaValidation(unittest.TestCase):
    """Test cases for schema validation functionality"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.temp_db.close()
        self.db_path = self.temp_db.name
        self.schema_manager = SchemaManager()
    
    def tearDown(self):
        """Clean up test fixtures"""
        if os.path.exists(self.db_path):
            os.unlink(self.db_path)
    
    def test_comprehensive_validation(self):
        """Test comprehensive schema validation"""
        connection = sqlite3.connect(self.db_path)
        
        # Create complete schema
        self.schema_manager._create_core_schema(connection, 'sqlite')
        
        # Run comprehensive validation
        validation_report = self.schema_manager._generate_validation_report(connection, 'sqlite')
        
        self.assertIsInstance(validation_report, dict)
        self.assertIn('status', validation_report)
        self.assertIn('tables', validation_report)
        self.assertIn('constraints', validation_report)
        
        connection.close()
    
    def test_constraint_validation(self):
        """Test foreign key constraint validation"""
        connection = sqlite3.connect(self.db_path)
        connection.execute("PRAGMA foreign_keys = ON")
        
        # Create schema
        self.schema_manager._create_core_schema(connection, 'sqlite')
        
        # Test constraint validation
        constraints_valid = self.schema_manager._validate_constraints(connection, 'sqlite')
        
        self.assertTrue(constraints_valid)
        connection.close()


if __name__ == '__main__':
    # Run tests with verbose output
    unittest.main(verbosity=2)