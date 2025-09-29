#!/usr/bin/env python3
"""
Unit tests for Directus CMS DataPopulator

Tests the systematic data population functionality including:
- Specification import and validation
- File system scanning and content extraction
- Relationship linking and validation
- Error handling and rollback capability
"""

import unittest
import tempfile
import os
import shutil
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from src.beast_mode.directus_cms.data_populator import (
    DataPopulator,
    PopulationStatus,
    SpecificationInfo,
    PopulationResult
)
from src.rm_ddd.core.unified_reflective_module import ModuleStatus, ModuleCapability


class TestDataPopulator(unittest.TestCase):
    """Test cases for DataPopulator class"""
    
    def setUp(self):
        """Set up test fixtures"""
        # Create temporary directory structure
        self.temp_dir = tempfile.mkdtemp()
        self.specs_dir = os.path.join(self.temp_dir, '.kiro', 'specs')
        os.makedirs(self.specs_dir, exist_ok=True)
        
        # Create test specifications
        self.test_specs = [
            'integration-orchestrator-framework',
            'ai-driven-cursor-sharing',
            'gpt5-context-calibration-system'
        ]
        
        for spec_name in self.test_specs:
            spec_dir = os.path.join(self.specs_dir, spec_name)
            os.makedirs(spec_dir, exist_ok=True)
            
            # Create requirements.md
            with open(os.path.join(spec_dir, 'requirements.md'), 'w') as f:
                f.write(f"# Requirements for {spec_name}\n\nTest requirements content.")
            
            # Create design.md
            with open(os.path.join(spec_dir, 'design.md'), 'w') as f:
                f.write(f"# Design for {spec_name}\n\nTest design content.")
            
            # Create tasks.md
            with open(os.path.join(spec_dir, 'tasks.md'), 'w') as f:
                f.write(f"# Tasks for {spec_name}\n\n- [ ] Task 1\n- [x] Task 2")
        
        # Create DataPopulator instance
        self.schema_manager = SchemaManager()
        self.data_populator = DataPopulator(self.schema_manager)
        
        # Mock database configuration
        self.test_config = {
            'database_type': 'sqlite',
            'database_path': ':memory:',
            'repository_root': self.temp_dir
        }
    
    def tearDown(self):
        """Clean up test fixtures"""
        # Remove temporary directory
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_module_info(self):
        """Test that DataPopulator provides correct module information"""
        module_info = self.data_populator.get_module_info()
        
        self.assertIsInstance(module_info, dict)
        self.assertIn('module_id', module_info)
        self.assertIn('module_name', module_info)
        self.assertIn('version', module_info)
        self.assertEqual(module_info['module_id'], 'directus_data_populator')
    
    def test_capabilities(self):
        """Test that DataPopulator declares correct capabilities"""
        capabilities = self.data_populator.get_capabilities()
        
        self.assertIsInstance(capabilities, list)
        self.assertIn(ModuleCapability.DATA_PROCESSING, capabilities)
        self.assertIn(ModuleCapability.VALIDATION, capabilities)
    
    def test_health_status(self):
        """Test health status reporting"""
        health = self.data_populator.get_health_status()
        
        self.assertIsNotNone(health)
        self.assertEqual(health.module_id, 'directus_data_populator')
        self.assertIsInstance(health.status, ModuleStatus)
        self.assertIsInstance(health.health_score, float)
        self.assertGreaterEqual(health.health_score, 0.0)
        self.assertLessEqual(health.health_score, 1.0)
    
    def test_specification_discovery(self):
        """Test specification discovery from file system"""
        specs = self.data_populator._discover_specifications(self.specs_dir)
        
        self.assertIsInstance(specs, list)
        self.assertEqual(len(specs), 3)
        
        spec_names = [spec.name for spec in specs]
        for expected_name in self.test_specs:
            self.assertIn(expected_name, spec_names)
    
    def test_controlled_specification_import(self):
        """Test controlled import of exactly 3 specifications"""
        with patch.object(self.data_populator, '_get_database_connection') as mock_db:
            mock_connection = Mock()
            mock_db.return_value = mock_connection
            
            result = self.data_populator.import_specifications(self.test_config)
            
            self.assertIsInstance(result, PopulationResult)
            # Should succeed with exactly 3 specs
            self.assertTrue(result.success)
            self.assertEqual(result.specifications_imported, 3)
    
    def test_specification_validation(self):
        """Test specification validation before import"""
        spec_info = SpecificationInfo(
            name='test-spec',
            path=os.path.join(self.specs_dir, 'integration-orchestrator-framework'),
            description='Test specification'
        )
        
        is_valid = self.data_populator._validate_specification(spec_info)
        self.assertTrue(is_valid)
    
    def test_specification_validation_missing_files(self):
        """Test specification validation with missing files"""
        # Create spec without required files
        incomplete_spec_dir = os.path.join(self.specs_dir, 'incomplete-spec')
        os.makedirs(incomplete_spec_dir, exist_ok=True)
        
        spec_info = SpecificationInfo(
            name='incomplete-spec',
            path=incomplete_spec_dir,
            description='Incomplete specification'
        )
        
        is_valid = self.data_populator._validate_specification(spec_info)
        self.assertFalse(is_valid)
    
    def test_document_extraction(self):
        """Test document content extraction"""
        spec_path = os.path.join(self.specs_dir, 'integration-orchestrator-framework')
        
        documents = self.data_populator._extract_documents(spec_path)
        
        self.assertIsInstance(documents, list)
        self.assertEqual(len(documents), 3)  # requirements, design, tasks
        
        doc_types = [doc['document_type'] for doc in documents]
        expected_types = ['requirements', 'design', 'tasks']
        for doc_type in expected_types:
            self.assertIn(doc_type, doc_types)
    
    def test_task_parsing(self):
        """Test task parsing from tasks.md files"""
        spec_path = os.path.join(self.specs_dir, 'integration-orchestrator-framework')
        tasks_file = os.path.join(spec_path, 'tasks.md')
        
        tasks = self.data_populator._parse_tasks(tasks_file)
        
        self.assertIsInstance(tasks, list)
        self.assertEqual(len(tasks), 2)  # Task 1 and Task 2
        
        # Check task structure
        for task in tasks:
            self.assertIn('title', task)
            self.assertIn('status', task)
            self.assertIn('description', task)
    
    def test_code_file_discovery(self):
        """Test code file discovery and linking"""
        # Create mock code files
        src_dir = os.path.join(self.temp_dir, 'src', 'beast_mode')
        os.makedirs(src_dir, exist_ok=True)
        
        # Create integration orchestrator files
        orchestrator_dir = os.path.join(src_dir, 'integration_orchestrator')
        os.makedirs(orchestrator_dir, exist_ok=True)
        
        with open(os.path.join(orchestrator_dir, 'core.py'), 'w') as f:
            f.write("# Integration orchestrator core")
        
        with open(os.path.join(orchestrator_dir, 'models.py'), 'w') as f:
            f.write("# Integration orchestrator models")
        
        # Test code file discovery
        code_files = self.data_populator._discover_code_files(
            self.temp_dir, 
            'integration-orchestrator-framework'
        )
        
        self.assertIsInstance(code_files, list)
        self.assertGreater(len(code_files), 0)
        
        # Check code file structure
        for code_file in code_files:
            self.assertIn('file_path', code_file)
            self.assertIn('file_type', code_file)
            self.assertIn('content_preview', code_file)
    
    def test_relationship_validation(self):
        """Test relationship validation between entities"""
        with patch.object(self.data_populator, '_get_database_connection') as mock_db:
            mock_connection = Mock()
            mock_cursor = Mock()
            mock_connection.cursor.return_value = mock_cursor
            mock_db.return_value = mock_connection
            
            # Mock successful relationship validation
            mock_cursor.fetchone.return_value = (1,)  # Valid foreign key
            
            is_valid = self.data_populator._validate_relationships(mock_connection)
            
            self.assertTrue(is_valid)
    
    def test_rollback_capability(self):
        """Test rollback capability for failed operations"""
        with patch.object(self.data_populator, '_get_database_connection') as mock_db:
            mock_connection = Mock()
            mock_db.return_value = mock_connection
            
            # Simulate rollback
            self.data_populator._rollback_population(mock_connection, 'test_transaction')
            
            # Verify rollback was called
            mock_connection.rollback.assert_called_once()
    
    def test_error_handling(self):
        """Test error handling during population"""
        # Test with invalid configuration
        invalid_config = {
            'database_type': 'invalid',
            'repository_root': '/nonexistent/path'
        }
        
        result = self.data_populator.import_specifications(invalid_config)
        
        self.assertIsInstance(result, PopulationResult)
        self.assertFalse(result.success)
        self.assertIn('error', result.message.lower())
    
    def test_observation_emission(self):
        """Test that population operations emit observations"""
        with patch.object(self.data_populator, 'emit_observation') as mock_emit:
            with patch.object(self.data_populator, '_get_database_connection'):
                # Perform population operation
                self.data_populator.import_specifications(self.test_config)
                
                # Verify observations were emitted
                mock_emit.assert_called()
                
                # Check observation details
                call_args = mock_emit.call_args_list
                self.assertGreater(len(call_args), 0)
    
    def test_performance_metrics(self):
        """Test performance metrics collection"""
        with patch.object(self.data_populator, '_get_database_connection'):
            # Perform some operations
            self.data_populator.import_specifications(self.test_config)
            
            # Get performance metrics
            metrics = self.data_populator.get_performance_metrics()
            
            self.assertIsInstance(metrics, dict)
            self.assertIn('operation_count', metrics)
            self.assertIn('total_operation_time_ms', metrics)
    
    def test_metadata_extraction(self):
        """Test metadata extraction from specification files"""
        spec_path = os.path.join(self.specs_dir, 'integration-orchestrator-framework')
        
        metadata = self.data_populator._extract_metadata(spec_path)
        
        self.assertIsInstance(metadata, dict)
        self.assertIn('name', metadata)
        self.assertIn('description', metadata)
        self.assertIn('file_count', metadata)
        self.assertIn('last_modified', metadata)
    
    def test_content_validation(self):
        """Test content validation before database insertion"""
        test_content = {
            'title': 'Test Document',
            'content': 'Test content',
            'document_type': 'requirements'
        }
        
        is_valid = self.data_populator._validate_content(test_content)
        self.assertTrue(is_valid)
        
        # Test invalid content
        invalid_content = {
            'title': '',  # Empty title
            'content': None,  # Null content
            'document_type': 'invalid_type'
        }
        
        is_valid = self.data_populator._validate_content(invalid_content)
        self.assertFalse(is_valid)
    
    def test_batch_processing(self):
        """Test batch processing of multiple specifications"""
        with patch.object(self.data_populator, '_get_database_connection') as mock_db:
            mock_connection = Mock()
            mock_db.return_value = mock_connection
            
            # Test batch import
            result = self.data_populator._batch_import_specifications(
                self.test_specs, 
                self.specs_dir, 
                mock_connection
            )
            
            self.assertIsInstance(result, dict)
            self.assertIn('success_count', result)
            self.assertIn('error_count', result)
            self.assertEqual(result['success_count'], 3)
            self.assertEqual(result['error_count'], 0)


class TestPopulationValidation(unittest.TestCase):
    """Test cases for population validation functionality"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.data_populator = DataPopulator()
    
    def test_comprehensive_validation(self):
        """Test comprehensive population validation"""
        with patch.object(self.data_populator, '_get_database_connection') as mock_db:
            mock_connection = Mock()
            mock_cursor = Mock()
            mock_connection.cursor.return_value = mock_cursor
            mock_db.return_value = mock_connection
            
            # Mock validation queries
            mock_cursor.fetchone.side_effect = [
                (3,),  # 3 specifications
                (9,),  # 9 documents (3 per spec)
                (6,),  # 6 tasks
                (1,),  # Valid relationships
            ]
            
            validation_report = self.data_populator._generate_validation_report(mock_connection)
            
            self.assertIsInstance(validation_report, dict)
            self.assertIn('specifications', validation_report)
            self.assertIn('documents', validation_report)
            self.assertIn('tasks', validation_report)
            self.assertIn('relationships', validation_report)
    
    def test_data_integrity_validation(self):
        """Test data integrity validation"""
        with patch.object(self.data_populator, '_get_database_connection') as mock_db:
            mock_connection = Mock()
            mock_cursor = Mock()
            mock_connection.cursor.return_value = mock_cursor
            mock_db.return_value = mock_connection
            
            # Mock integrity check
            mock_cursor.fetchall.return_value = []  # No integrity violations
            
            integrity_valid = self.data_populator._validate_data_integrity(mock_connection)
            
            self.assertTrue(integrity_valid)


if __name__ == '__main__':
    # Run tests with verbose output
    unittest.main(verbosity=2)