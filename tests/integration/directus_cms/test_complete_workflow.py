#!/usr/bin/env python3
"""
Integration tests for Directus CMS complete workflow

Tests the end-to-end functionality including:
- Schema creation and validation
- Data population and relationship linking
- UI configuration and navigation
- API access and functionality
- Error scenarios and recovery
"""

import unittest
import tempfile
import os
import shutil
import sqlite3
from pathlib import Path
from datetime import datetime

import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from src.beast_mode.directus_cms.schema_manager import SchemaManager
from src.beast_mode.directus_cms.data_populator import DataPopulator
from src.beast_mode.directus_cms.orchestrator import DirectusOrchestrator


class TestCompleteWorkflow(unittest.TestCase):
    """Integration tests for complete Directus CMS workflow"""
    
    def setUp(self):
        """Set up test environment"""
        # Create temporary directory structure
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.temp_dir, 'test_directus.db')
        
        # Create test repository structure
        self.setup_test_repository()
        
        # Initialize components
        self.schema_manager = SchemaManager()
        self.data_populator = DataPopulator()
        self.orchestrator = DirectusOrchestrator()
        
        # Configuration
        self.config = {
            'database_type': 'sqlite',
            'database_path': self.db_path,
            'repository_root': self.temp_dir,
            'target_specifications': [
                'integration-orchestrator-framework',
                'ai-driven-cursor-sharing',
                'gpt5-context-calibration-system'
            ]
        }
    
    def tearDown(self):
        """Clean up test environment"""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def setup_test_repository(self):
        """Set up test repository structure with specifications"""
        specs_dir = os.path.join(self.temp_dir, '.kiro', 'specs')
        os.makedirs(specs_dir, exist_ok=True)
        
        # Create test specifications
        test_specs = [
            'integration-orchestrator-framework',
            'ai-driven-cursor-sharing', 
            'gpt5-context-calibration-system'
        ]
        
        for spec_name in test_specs:
            spec_dir = os.path.join(specs_dir, spec_name)
            os.makedirs(spec_dir, exist_ok=True)
            
            # Create requirements.md
            requirements_content = f"""# Requirements for {spec_name}

## Introduction
This specification defines the requirements for {spec_name}.

## Requirements

### Requirement 1: Core Functionality
**User Story:** As a user, I want core functionality, so that the system works.

#### Acceptance Criteria
1. WHEN the system starts THEN it SHALL initialize properly
2. WHEN operations are performed THEN they SHALL complete successfully
"""
            
            with open(os.path.join(spec_dir, 'requirements.md'), 'w') as f:
                f.write(requirements_content)
            
            # Create design.md
            design_content = f"""# Design Document for {spec_name}

## Overview
This document describes the design for {spec_name}.

## Architecture
The system follows MVC architecture with proper separation of concerns.

## Components
- Model: Data management
- View: User interface
- Controller: Business logic
"""
            
            with open(os.path.join(spec_dir, 'design.md'), 'w') as f:
                f.write(design_content)
            
            # Create tasks.md
            tasks_content = f"""# Implementation Plan for {spec_name}

## Tasks

- [x] 1. Create core infrastructure
  - Implement base classes
  - Set up configuration
  - _Requirements: 1.1_

- [ ] 2. Implement business logic
  - Create service classes
  - Add validation
  - _Requirements: 1.2_

- [ ] 3. Create user interface
  - Design UI components
  - Implement interactions
  - _Requirements: 1.3_
"""
            
            with open(os.path.join(spec_dir, 'tasks.md'), 'w') as f:
                f.write(tasks_content)
        
        # Create source code structure
        src_dir = os.path.join(self.temp_dir, 'src', 'beast_mode')
        os.makedirs(src_dir, exist_ok=True)
        
        # Create integration orchestrator code
        orchestrator_dir = os.path.join(src_dir, 'integration_orchestrator')
        os.makedirs(orchestrator_dir, exist_ok=True)
        
        with open(os.path.join(orchestrator_dir, '__init__.py'), 'w') as f:
            f.write('"""Integration Orchestrator Framework"""')
        
        with open(os.path.join(orchestrator_dir, 'core.py'), 'w') as f:
            f.write('''"""Integration Orchestrator Core"""

class IntegrationOrchestrator:
    """Core orchestrator for integration management"""
    
    def __init__(self):
        self.active_integrations = []
    
    def start_integration(self, config):
        """Start a new integration"""
        return {"status": "started", "config": config}
''')
        
        # Create cursor sharing code
        cursor_dir = os.path.join(src_dir, 'cursor_sharing')
        os.makedirs(cursor_dir, exist_ok=True)
        
        with open(os.path.join(cursor_dir, '__init__.py'), 'w') as f:
            f.write('"""AI-Driven Cursor Sharing"""')
        
        with open(os.path.join(cursor_dir, 'manager.py'), 'w') as f:
            f.write('''"""Cursor Sharing Manager"""

class CursorSharingManager:
    """Manages AI-driven cursor sharing"""
    
    def __init__(self):
        self.active_sessions = {}
    
    def create_session(self, user_id):
        """Create a new sharing session"""
        return {"session_id": f"session_{user_id}", "status": "active"}
''')
    
    def test_complete_workflow_success(self):
        """Test complete successful workflow from schema to data"""
        # Phase 1: Schema Creation
        schema_result = self.schema_manager.create_schema(self.config)
        self.assertTrue(schema_result.success, f"Schema creation failed: {schema_result.message}")
        
        # Verify schema was created
        connection = sqlite3.connect(self.db_path)
        cursor = connection.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        
        expected_tables = ['specifications', 'code_files', 'documents', 'tasks']
        for table in expected_tables:
            self.assertIn(table, tables, f"Table {table} not found")
        
        connection.close()
        
        # Phase 2: Data Population
        population_result = self.data_populator.import_specifications(self.config)
        self.assertTrue(population_result.success, f"Data population failed: {population_result.message}")
        self.assertEqual(population_result.specifications_imported, 3)
        
        # Verify data was populated
        connection = sqlite3.connect(self.db_path)
        cursor = connection.cursor()
        
        # Check specifications
        cursor.execute("SELECT COUNT(*) FROM specifications")
        spec_count = cursor.fetchone()[0]
        self.assertEqual(spec_count, 3, "Expected 3 specifications")
        
        # Check documents
        cursor.execute("SELECT COUNT(*) FROM documents")
        doc_count = cursor.fetchone()[0]
        self.assertEqual(doc_count, 9, "Expected 9 documents (3 per spec)")
        
        # Check tasks
        cursor.execute("SELECT COUNT(*) FROM tasks")
        task_count = cursor.fetchone()[0]
        self.assertGreater(task_count, 0, "Expected tasks to be imported")
        
        connection.close()
        
        # Phase 3: Relationship Validation
        self.validate_relationships()
        
        # Phase 4: End-to-end validation
        self.validate_complete_system()
    
    def test_orchestrated_workflow(self):
        """Test workflow using the orchestrator"""
        # Use orchestrator for complete workflow
        result = self.orchestrator.execute_complete_setup(self.config)
        
        self.assertTrue(result.success, f"Orchestrated workflow failed: {result.message}")
        self.assertIn('schema_created', result.details)
        self.assertIn('data_populated', result.details)
        self.assertIn('relationships_validated', result.details)
    
    def test_error_recovery_workflow(self):
        """Test error recovery during workflow execution"""
        # Create invalid configuration to trigger error
        invalid_config = self.config.copy()
        invalid_config['repository_root'] = '/nonexistent/path'
        
        # Attempt workflow with invalid config
        result = self.orchestrator.execute_complete_setup(invalid_config)
        
        # Should fail gracefully
        self.assertFalse(result.success)
        self.assertIn('error', result.message.lower())
        
        # Verify no partial data was left behind
        if os.path.exists(self.db_path):
            connection = sqlite3.connect(self.db_path)
            cursor = connection.cursor()
            
            # Check that no partial data exists
            cursor.execute("SELECT COUNT(*) FROM specifications")
            spec_count = cursor.fetchone()[0]
            self.assertEqual(spec_count, 0, "No partial data should remain after error")
            
            connection.close()
    
    def test_concurrent_workflow_execution(self):
        """Test concurrent workflow execution safety"""
        import threading
        import time
        
        results = []
        errors = []
        
        def workflow_worker(worker_id):
            try:
                # Use separate database for each worker
                worker_config = self.config.copy()
                worker_config['database_path'] = os.path.join(
                    self.temp_dir, f'worker_{worker_id}.db'
                )
                
                result = self.orchestrator.execute_complete_setup(worker_config)
                results.append((worker_id, result))
            except Exception as e:
                errors.append((worker_id, e))
        
        # Create multiple worker threads
        threads = []
        for i in range(3):
            thread = threading.Thread(target=workflow_worker, args=(i,))
            threads.append(thread)
        
        # Start all threads
        for thread in threads:
            thread.start()
        
        # Wait for completion
        for thread in threads:
            thread.join(timeout=30)
        
        # Verify results
        self.assertEqual(len(results), 3, "All workers should complete")
        self.assertEqual(len(errors), 0, "No errors should occur")
        
        # Verify all workers succeeded
        for worker_id, result in results:
            self.assertTrue(result.success, f"Worker {worker_id} failed: {result.message}")
    
    def test_performance_under_load(self):
        """Test system performance under load"""
        import time
        
        start_time = time.time()
        
        # Execute workflow
        result = self.orchestrator.execute_complete_setup(self.config)
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        # Verify success
        self.assertTrue(result.success)
        
        # Verify reasonable performance (should complete within 30 seconds)
        self.assertLess(execution_time, 30, f"Workflow took too long: {execution_time}s")
        
        # Get performance metrics
        schema_metrics = self.schema_manager.get_performance_metrics()
        population_metrics = self.data_populator.get_performance_metrics()
        
        # Verify metrics are collected
        self.assertGreater(schema_metrics['operation_count'], 0)
        self.assertGreater(population_metrics['operation_count'], 0)
    
    def validate_relationships(self):
        """Validate database relationships"""
        connection = sqlite3.connect(self.db_path)
        cursor = connection.cursor()
        
        # Test foreign key relationships
        cursor.execute("""
            SELECT d.id, d.specification_id, s.id 
            FROM documents d 
            JOIN specifications s ON d.specification_id = s.id
        """)
        doc_relationships = cursor.fetchall()
        self.assertGreater(len(doc_relationships), 0, "Document relationships should exist")
        
        # Test task relationships
        cursor.execute("""
            SELECT t.id, t.specification_id, s.id 
            FROM tasks t 
            JOIN specifications s ON t.specification_id = s.id
        """)
        task_relationships = cursor.fetchall()
        self.assertGreater(len(task_relationships), 0, "Task relationships should exist")
        
        connection.close()
    
    def validate_complete_system(self):
        """Validate the complete system functionality"""
        connection = sqlite3.connect(self.db_path)
        cursor = connection.cursor()
        
        # Validate data integrity
        cursor.execute("""
            SELECT s.name, 
                   COUNT(DISTINCT d.id) as doc_count,
                   COUNT(DISTINCT t.id) as task_count
            FROM specifications s
            LEFT JOIN documents d ON s.id = d.specification_id
            LEFT JOIN tasks t ON s.id = t.specification_id
            GROUP BY s.id, s.name
        """)
        
        spec_summary = cursor.fetchall()
        
        # Each spec should have documents and tasks
        for spec_name, doc_count, task_count in spec_summary:
            self.assertGreater(doc_count, 0, f"Spec {spec_name} should have documents")
            self.assertGreater(task_count, 0, f"Spec {spec_name} should have tasks")
        
        # Validate content quality
        cursor.execute("SELECT content FROM documents WHERE content IS NULL OR content = ''")
        empty_content = cursor.fetchall()
        self.assertEqual(len(empty_content), 0, "No documents should have empty content")
        
        connection.close()
    
    def test_rollback_on_failure(self):
        """Test rollback capability when operations fail"""
        # Create schema successfully
        schema_result = self.schema_manager.create_schema(self.config)
        self.assertTrue(schema_result.success)
        
        # Corrupt the repository to cause population failure
        specs_dir = os.path.join(self.temp_dir, '.kiro', 'specs')
        shutil.rmtree(specs_dir)
        
        # Attempt population (should fail)
        population_result = self.data_populator.import_specifications(self.config)
        self.assertFalse(population_result.success)
        
        # Verify database is in clean state (schema exists but no data)
        connection = sqlite3.connect(self.db_path)
        cursor = connection.cursor()
        
        # Tables should exist (schema was successful)
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        self.assertGreater(len(tables), 0, "Schema tables should exist")
        
        # But no data should be present (population failed and rolled back)
        cursor.execute("SELECT COUNT(*) FROM specifications")
        spec_count = cursor.fetchone()[0]
        self.assertEqual(spec_count, 0, "No specifications should remain after rollback")
        
        connection.close()


class TestAPIIntegration(unittest.TestCase):
    """Integration tests for API functionality"""
    
    def setUp(self):
        """Set up test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.temp_dir, 'test_api.db')
        
        # Set up complete system
        self.setup_complete_system()
    
    def tearDown(self):
        """Clean up test environment"""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def setup_complete_system(self):
        """Set up complete system for API testing"""
        # This would set up the complete system including Directus
        # For now, we'll mock the API responses
        pass
    
    def test_rest_api_access(self):
        """Test REST API access to CMS data"""
        # This would test actual REST API endpoints
        # For now, we'll test the configuration
        from src.beast_mode.directus_cms.api.rest_config import RestAPIConfigurator
        
        configurator = RestAPIConfigurator()
        config = configurator.get_api_configuration()
        
        self.assertIsInstance(config, dict)
        self.assertIn('endpoints', config)
        self.assertIn('authentication', config)
    
    def test_graphql_api_access(self):
        """Test GraphQL API access to CMS data"""
        # This would test actual GraphQL queries
        # For now, we'll test the configuration
        from src.beast_mode.directus_cms.api.graphql_config import GraphQLConfigurator
        
        configurator = GraphQLConfigurator()
        schema = configurator.get_graphql_schema()
        
        self.assertIsInstance(schema, dict)
        self.assertIn('types', schema)
        self.assertIn('queries', schema)


if __name__ == '__main__':
    # Run tests with verbose output
    unittest.main(verbosity=2)