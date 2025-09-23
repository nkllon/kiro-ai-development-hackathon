"""
Unit Tests for Directus CMS Data Populator

Comprehensive test suite for the DataPopulator class ensuring:
- Controlled specification import (exactly 3 specs)
- File system scanning and content extraction
- Relationship validation and linking
- Error handling and rollback capability

Requirements Tested:
- 5.1: Import exactly 3 specifications with validation
- 5.2: Link documents and code files to specifications
- 10.1: Preserve all functionality with comprehensive validation
- 4.5: Rollback capability for failed operations
"""

import unittest
import tempfile
import os
import shutil
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

# Import the modules under test
from src.beast_mode.directus_cms.data_populator import (
    DataPopulator,
    PopulationResult,
    ValidationResult,
    PopulationStatus,
    SpecificationInfo,
    CodeFileInfo,
    DocumentInfo
)
from src.beast_mode.directus_cms.schema_manager import SchemaManager
from src.rm_ddd.core.unified_reflective_module import (
    ModuleHealth,
    ModuleStatus,
    ModuleCapability
)


class TestDataPopulator(unittest.TestCase):
    """Test suite for DataPopulator class"""
    
    def setUp(self):
        """Set up test environment"""
        # Create temporary repository structure
        self.temp_repo = tempfile.mkdtemp()
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.temp_db.close()
        
        # Create mock repository structure
        self._create_mock_repository()
        
        # Initialize SchemaManager with test database
        self.schema_manager = SchemaManager(
            database_url=f"sqlite://{self.temp_db.name}",
            database_type="sqlite"
        )
        
        # Create schema
        self.schema_manager.create_schema()
        
        # Initialize DataPopulator
        self.data_populator = DataPopulator(
            schema_manager=self.schema_manager,
            repository_root=self.temp_repo
        )
    
    def tearDown(self):
        """Clean up test environment"""
        # Close database connections
        if hasattr(self.schema_manager, 'connection') and self.schema_manager.connection:
            self.schema_manager.connection.close()
        
        # Remove temporary files
        try:
            shutil.rmtree(self.temp_repo)
            os.unlink(self.temp_db.name)
        except (FileNotFoundError, PermissionError):
            pass
    
    def _create_mock_repository(self):
        """Create mock repository structure for testing"""
        repo_path = Path(self.temp_repo)
        
        # Create .kiro/specs directory structure
        specs_dir = repo_path / ".kiro" / "specs"
        specs_dir.mkdir(parents=True, exist_ok=True)
        
        # Create target specifications
        target_specs = [
            "integration-orchestrator-framework",
            "ai-driven-cursor-sharing",
            "gpt5-context-calibration-system"
        ]
        
        for spec_name in target_specs:
            spec_dir = specs_dir / spec_name
            spec_dir.mkdir(exist_ok=True)
            
            # Create requirements.md
            requirements_content = f"""# Requirements Document

## Introduction

This is the {spec_name} specification for testing purposes. It provides systematic functionality for the test environment.

## Requirements

### Requirement 1

**User Story:** As a test user, I want {spec_name} functionality, so that I can validate the system.

#### Acceptance Criteria

1. WHEN testing THEN the system SHALL work correctly
2. WHEN validating THEN all requirements SHALL be met
"""
            (spec_dir / "requirements.md").write_text(requirements_content)
            
            # Create design.md
            design_content = f"""# Design Document

## Overview

The {spec_name} design provides systematic architecture for testing.

## Architecture

This is a test architecture for {spec_name}.
"""
            (spec_dir / "design.md").write_text(design_content)
            
            # Create tasks.md
            tasks_content = f"""# Implementation Plan

## Tasks

- [ ] 1. Implement {spec_name} core functionality
- [ ] 2. Add {spec_name} validation
- [ ] 3. Test {spec_name} integration
"""
            (spec_dir / "tasks.md").write_text(tasks_content)
        
        # Create src directory with code files
        src_dir = repo_path / "src" / "beast_mode"
        src_dir.mkdir(parents=True, exist_ok=True)
        
        # Create integration_orchestrator files
        orchestrator_dir = src_dir / "integration_orchestrator"
        orchestrator_dir.mkdir(exist_ok=True)
        (orchestrator_dir / "__init__.py").write_text("# Integration Orchestrator package")
        (orchestrator_dir / "orchestrator.py").write_text("""
# Integration Orchestrator implementation
class IntegrationOrchestrator:
    def __init__(self):
        self.integration_orchestrator_active = True
""")
        
        # Create cursor_sharing files
        cursor_dir = src_dir / "cursor_sharing"
        cursor_dir.mkdir(exist_ok=True)
        (cursor_dir / "__init__.py").write_text("# Cursor Sharing package")
        (cursor_dir / "cursor_manager.py").write_text("""
# Cursor Sharing implementation
class CursorManager:
    def __init__(self):
        self.cursor_sharing_enabled = True
""")
        
        # Create gpt5 files
        gpt5_dir = src_dir / "gpt5_calibration"
        gpt5_dir.mkdir(exist_ok=True)
        (gpt5_dir / "__init__.py").write_text("# GPT5 Calibration package")
        (gpt5_dir / "calibrator.py").write_text("""
# GPT5 Context Calibration implementation
class GPT5Calibrator:
    def __init__(self):
        self.gpt5_calibration_active = True
""")
    
    def test_reflective_module_implementation(self):
        """Test ReflectiveModule interface implementation"""
        # Test get_module_info
        module_info = self.data_populator.get_module_info()
        self.assertIsInstance(module_info, dict)
        self.assertEqual(module_info["module_id"], "directus_data_populator")
        self.assertEqual(module_info["module_name"], "DirectusDataPopulator")
        self.assertIn("target_specifications", module_info)
        self.assertEqual(len(module_info["target_specifications"]), 3)
        
        # Test get_capabilities
        capabilities = self.data_populator.get_capabilities()
        self.assertIsInstance(capabilities, list)
        self.assertIn(ModuleCapability.CORE_FUNCTIONALITY, capabilities)
        self.assertIn(ModuleCapability.DATA_PROCESSING, capabilities)
        self.assertIn(ModuleCapability.VALIDATION, capabilities)
        
        # Test get_health_status
        health_status = self.data_populator.get_health_status()
        self.assertIsInstance(health_status, ModuleHealth)
        self.assertEqual(health_status.module_id, "directus_data_populator")
        self.assertIsInstance(health_status.status, ModuleStatus)
        
        # Test graceful_degradation
        degradation_result = self.data_populator.graceful_degradation()
        self.assertIsNotNone(degradation_result)
        self.assertIsInstance(degradation_result.success, bool)
    
    def test_specification_scanning(self):
        """Test specification scanning functionality"""
        # Test scanning target specifications
        spec_infos = self.data_populator._scan_specifications(
            self.data_populator.target_specifications
        )
        
        self.assertEqual(len(spec_infos), 3)
        
        # Verify each specification
        spec_names = [spec.name for spec in spec_infos]
        for target_spec in self.data_populator.target_specifications:
            self.assertIn(target_spec, spec_names)
        
        # Verify specification info structure
        for spec_info in spec_infos:
            self.assertIsInstance(spec_info, SpecificationInfo)
            self.assertIsNotNone(spec_info.name)
            self.assertIsNotNone(spec_info.path)
            self.assertIsNotNone(spec_info.description)
            self.assertEqual(spec_info.status, "active")
    
    def test_specification_population_success(self):
        """Test successful specification population"""
        # Populate specifications
        result = self.data_populator.populate_specifications()
        
        # Verify result
        self.assertIsInstance(result, PopulationResult)
        self.assertTrue(result.success)
        self.assertEqual(result.status, PopulationStatus.SUCCESS)
        self.assertEqual(len(result.imported_specs), 3)
        
        # Verify specifications were inserted into database
        cursor = self.schema_manager.connection.cursor()
        cursor.execute("SELECT name FROM specifications ORDER BY name")
        db_specs = [row[0] for row in cursor.fetchall()]
        cursor.close()
        
        for target_spec in self.data_populator.target_specifications:
            self.assertIn(target_spec, db_specs)
    
    def test_specification_population_validation(self):
        """Test specification population validation (exactly 3 specs)"""
        # Test with wrong number of specifications
        with self.assertRaises(ValueError):
            self.data_populator.populate_specifications(["spec1", "spec2"])  # Only 2 specs
        
        with self.assertRaises(ValueError):
            self.data_populator.populate_specifications(["spec1", "spec2", "spec3", "spec4"])  # 4 specs
    
    def test_code_file_scanning(self):
        """Test code file scanning functionality"""
        # Scan for code files
        code_files = self.data_populator._scan_code_files()
        
        self.assertGreater(len(code_files), 0)
        
        # Verify code file structure
        for code_file in code_files:
            self.assertIsInstance(code_file, CodeFileInfo)
            self.assertIsNotNone(code_file.file_name)
            self.assertIsNotNone(code_file.file_path)
            self.assertIsNotNone(code_file.specification_name)
            self.assertIn(code_file.specification_name, self.data_populator.target_specifications)
        
        # Verify pattern matching works
        spec_names = [cf.specification_name for cf in code_files]
        self.assertIn("integration-orchestrator-framework", spec_names)
        self.assertIn("ai-driven-cursor-sharing", spec_names)
        self.assertIn("gpt5-context-calibration-system", spec_names)
    
    def test_document_import(self):
        """Test document import functionality"""
        # First populate specifications
        self.data_populator.populate_specifications()
        
        # Import documents
        result = self.data_populator.import_documents()
        
        # Verify result
        self.assertIsInstance(result, PopulationResult)
        self.assertTrue(result.success)
        self.assertEqual(result.status, PopulationStatus.SUCCESS)
        self.assertGreater(len(result.imported_files), 0)
        
        # Verify documents were inserted into database
        cursor = self.schema_manager.connection.cursor()
        cursor.execute("""
            SELECT d.title, d.document_type, s.name
            FROM documents d
            JOIN specifications s ON d.specification_id = s.id
            ORDER BY d.title
        """)
        documents = cursor.fetchall()
        cursor.close()
        
        self.assertGreater(len(documents), 0)
        
        # Verify document types
        doc_types = [doc[1] for doc in documents]
        self.assertIn("requirements", doc_types)
        self.assertIn("design", doc_types)
        self.assertIn("tasks", doc_types)
    
    def test_code_file_linking(self):
        """Test code file linking functionality"""
        # First populate specifications
        self.data_populator.populate_specifications()
        
        # Link code files
        result = self.data_populator.link_code_files()
        
        # Verify result
        self.assertIsInstance(result, PopulationResult)
        self.assertTrue(result.success)
        self.assertEqual(result.status, PopulationStatus.SUCCESS)
        self.assertGreater(len(result.imported_files), 0)
        
        # Verify code files were linked in database
        cursor = self.schema_manager.connection.cursor()
        cursor.execute("""
            SELECT cf.file_name, cf.file_path, s.name
            FROM code_files cf
            JOIN specifications s ON cf.specification_id = s.id
            ORDER BY cf.file_name
        """)
        code_files = cursor.fetchall()
        cursor.close()
        
        self.assertGreater(len(code_files), 0)
        
        # Verify relationships
        for file_name, file_path, spec_name in code_files:
            self.assertIn(spec_name, self.data_populator.target_specifications)
    
    def test_relationship_validation(self):
        """Test relationship validation functionality"""
        # Populate all data
        self.data_populator.populate_specifications()
        self.data_populator.import_documents()
        self.data_populator.link_code_files()
        
        # Validate relationships
        result = self.data_populator.validate_relationships()
        
        # Verify result
        self.assertIsInstance(result, ValidationResult)
        self.assertTrue(result.is_valid)
        self.assertGreater(result.validated_relationships, 0)
        self.assertEqual(len(result.broken_relationships), 0)
    
    def test_relationship_validation_with_broken_relationships(self):
        """Test relationship validation with broken relationships"""
        # Populate specifications
        self.data_populator.populate_specifications()
        
        # Manually insert broken relationship
        cursor = self.schema_manager.connection.cursor()
        cursor.execute("""
            INSERT INTO code_files (file_name, file_path, specification_id)
            VALUES (?, ?, ?)
        """, ("broken_file.py", "/broken/path.py", 999))  # Non-existent spec ID
        self.schema_manager.connection.commit()
        cursor.close()
        
        # Validate relationships
        result = self.data_populator.validate_relationships()
        
        # Verify broken relationship is detected
        self.assertIsInstance(result, ValidationResult)
        self.assertFalse(result.is_valid)
        self.assertGreater(len(result.broken_relationships), 0)
        self.assertGreater(len(result.recommendations), 0)
    
    def test_data_cleanup_rollback(self):
        """Test data cleanup and rollback functionality"""
        # Populate all data
        self.data_populator.populate_specifications()
        self.data_populator.import_documents()
        self.data_populator.link_code_files()
        
        # Verify data exists
        cursor = self.schema_manager.connection.cursor()
        cursor.execute("SELECT COUNT(*) FROM specifications")
        spec_count_before = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM documents")
        doc_count_before = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM code_files")
        file_count_before = cursor.fetchone()[0]
        cursor.close()
        
        self.assertGreater(spec_count_before, 0)
        self.assertGreater(doc_count_before, 0)
        self.assertGreater(file_count_before, 0)
        
        # Cleanup data
        cleanup_result = self.data_populator.cleanup_data()
        
        # Verify cleanup result
        self.assertIsInstance(cleanup_result, PopulationResult)
        self.assertTrue(cleanup_result.success)
        
        # Verify data was removed
        cursor = self.schema_manager.connection.cursor()
        cursor.execute("SELECT COUNT(*) FROM specifications")
        spec_count_after = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM documents")
        doc_count_after = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM code_files")
        file_count_after = cursor.fetchone()[0]
        cursor.close()
        
        # Data should be cleaned up
        self.assertLess(spec_count_after, spec_count_before)
        self.assertLess(doc_count_after, doc_count_before)
        self.assertLess(file_count_after, file_count_before)
    
    def test_population_status_reporting(self):
        """Test population status reporting"""
        # Get initial status
        initial_status = self.data_populator.get_population_status()
        self.assertIsInstance(initial_status, dict)
        self.assertIn("target_specifications", initial_status)
        self.assertIn("repository_root", initial_status)
        
        # Populate some data
        self.data_populator.populate_specifications()
        self.data_populator.import_documents()
        
        # Get updated status
        updated_status = self.data_populator.get_population_status()
        self.assertIsInstance(updated_status, dict)
        self.assertIn("imported_data_summary", updated_status)
        self.assertIn("validation_status", updated_status)
        
        # Verify data summary
        summary = updated_status["imported_data_summary"]
        self.assertGreater(summary.get("specifications", 0), 0)
        self.assertGreater(summary.get("documents", 0), 0)
    
    def test_error_handling_missing_repository(self):
        """Test error handling with missing repository structure"""
        # Create DataPopulator with non-existent repository
        invalid_populator = DataPopulator(
            schema_manager=self.schema_manager,
            repository_root="/non/existent/path"
        )
        
        # Test health status with missing repository
        health_status = invalid_populator.get_health_status()
        self.assertEqual(health_status.status, ModuleStatus.ERROR)
        self.assertGreater(len(health_status.issues), 0)
    
    def test_error_handling_missing_specifications(self):
        """Test error handling with missing specifications"""
        # Remove one specification directory
        spec_dir = Path(self.temp_repo) / ".kiro" / "specs" / "integration-orchestrator-framework"
        shutil.rmtree(spec_dir)
        
        # Test health status
        health_status = self.data_populator.get_health_status()
        self.assertIn(health_status.status, [ModuleStatus.WARNING, ModuleStatus.ERROR])
        self.assertGreater(len(health_status.issues), 0)
        
        # Test population with missing spec
        with self.assertRaises(FileNotFoundError):
            self.data_populator.populate_specifications()
    
    def test_operation_tracing(self):
        """Test operation tracing functionality"""
        # Perform operations with tracing
        self.data_populator.populate_specifications()
        
        # Get operation traces
        traces = self.data_populator.get_operation_traces()
        self.assertIsInstance(traces, list)
        self.assertGreater(len(traces), 0)
        
        # Verify trace contains populate_specifications operation
        populate_trace = None
        for trace in traces:
            if trace.operation_name == "populate_specifications":
                populate_trace = trace
                break
        
        self.assertIsNotNone(populate_trace)
        self.assertEqual(populate_trace.component_name, "DataPopulator")
        self.assertIsNotNone(populate_trace.start_time)
        self.assertIsNotNone(populate_trace.end_time)
        self.assertIsNotNone(populate_trace.duration_ms)
    
    def test_performance_metrics(self):
        """Test performance metrics collection"""
        # Perform some operations
        self.data_populator.populate_specifications()
        self.data_populator.validate_relationships()
        
        # Get performance metrics
        metrics = self.data_populator.get_performance_metrics()
        
        self.assertIsInstance(metrics, dict)
        self.assertIn("operation_count", metrics)
        self.assertIn("total_operation_time_ms", metrics)
        self.assertIn("average_operation_time_ms", metrics)
        self.assertIn("error_count", metrics)
        self.assertIn("uptime_seconds", metrics)
        
        self.assertGreater(metrics["operation_count"], 0)
        self.assertGreaterEqual(metrics["total_operation_time_ms"], 0)
    
    def test_cli_interface_generation(self):
        """Test CLI interface generation from ReflectiveModule"""
        # Get CLI interface
        cli_interface = self.data_populator.get_cli_interface()
        
        self.assertIsInstance(cli_interface, dict)
        self.assertIn("module_id", cli_interface)
        self.assertIn("module_name", cli_interface)
        self.assertIn("commands", cli_interface)
        
        # Verify key methods are exposed as CLI commands
        commands = cli_interface["commands"]
        expected_commands = [
            "populate_specifications",
            "import_documents",
            "link_code_files",
            "validate_relationships",
            "cleanup_data",
            "get_population_status"
        ]
        
        for cmd in expected_commands:
            self.assertIn(cmd, commands)
            self.assertIn("description", commands[cmd])
            self.assertIn("parameters", commands[cmd])
    
    def test_cli_command_execution(self):
        """Test CLI command execution"""
        # Execute populate_specifications command via CLI
        result = self.data_populator.execute_cli_command("populate_specifications")
        
        self.assertIsInstance(result, dict)
        self.assertTrue(result["success"])
        self.assertEqual(result["command"], "populate_specifications")
        self.assertIn("result", result)
        
        # Verify the actual population occurred
        population_result = result["result"]
        self.assertIsInstance(population_result, PopulationResult)
        self.assertTrue(population_result.success)


class TestDataPopulatorIntegration(unittest.TestCase):
    """Integration tests for DataPopulator with complete workflow"""
    
    def setUp(self):
        """Set up integration test environment"""
        self.temp_repo = tempfile.mkdtemp()
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.temp_db.close()
        
        # Create realistic repository structure
        self._create_realistic_repository()
        
        # Initialize components
        self.schema_manager = SchemaManager(
            database_url=f"sqlite://{self.temp_db.name}",
            database_type="sqlite"
        )
        self.schema_manager.create_schema()
        
        self.data_populator = DataPopulator(
            schema_manager=self.schema_manager,
            repository_root=self.temp_repo
        )
    
    def tearDown(self):
        """Clean up integration test environment"""
        if hasattr(self.schema_manager, 'connection') and self.schema_manager.connection:
            self.schema_manager.connection.close()
        
        try:
            shutil.rmtree(self.temp_repo)
            os.unlink(self.temp_db.name)
        except (FileNotFoundError, PermissionError):
            pass
    
    def _create_realistic_repository(self):
        """Create realistic repository structure with actual content"""
        repo_path = Path(self.temp_repo)
        
        # Create comprehensive spec structure
        specs_dir = repo_path / ".kiro" / "specs"
        
        # Integration Orchestrator Framework
        io_spec = specs_dir / "integration-orchestrator-framework"
        io_spec.mkdir(parents=True, exist_ok=True)
        
        (io_spec / "requirements.md").write_text("""# Requirements Document

## Introduction

The Integration Orchestrator Framework implements the "Don't Reinvent Shit" principle for systematic integration over reimplementation.

## Requirements

### Requirement 1: Integration Discovery

**User Story:** As a developer, I want automatic discovery of existing integrations, so that I don't reinvent existing functionality.

#### Acceptance Criteria

1. WHEN scanning for integrations THEN the system SHALL discover existing patterns
2. WHEN patterns are found THEN the system SHALL provide reuse recommendations
""")
        
        (io_spec / "design.md").write_text("""# Design Document

## Overview

The Integration Orchestrator provides systematic integration capabilities.

## Architecture

- Discovery Engine: Scans for existing integrations
- Pattern Registry: Maintains integration patterns
- Composition Framework: Enables systematic composition
""")
        
        (io_spec / "tasks.md").write_text("""# Implementation Plan

- [ ] 1. Implement discovery engine
- [ ] 2. Create pattern registry
- [ ] 3. Build composition framework
""")
        
        # AI-Driven Cursor Sharing
        cursor_spec = specs_dir / "ai-driven-cursor-sharing"
        cursor_spec.mkdir(parents=True, exist_ok=True)
        
        (cursor_spec / "requirements.md").write_text("""# Requirements Document

## Introduction

AI-enhanced cursor sharing system with real-time coordination and behavioral learning.

## Requirements

### Requirement 1: Cursor Event Capture

**User Story:** As a user, I want my cursor movements captured and shared, so that AI can learn from my behavior.

#### Acceptance Criteria

1. WHEN cursor moves THEN events SHALL be captured with sub-50ms latency
2. WHEN events are captured THEN they SHALL be transmitted to AI engine
""")
        
        # GPT-5 Context Calibration
        gpt5_spec = specs_dir / "gpt5-context-calibration-system"
        gpt5_spec.mkdir(parents=True, exist_ok=True)
        
        (gpt5_spec / "requirements.md").write_text("""# Requirements Document

## Introduction

AI capability assessment and context injection framework for GPT-5 integration.

## Requirements

### Requirement 1: Capability Assessment

**User Story:** As an AI system, I want to assess GPT-5 capabilities, so that I can optimize context injection.

#### Acceptance Criteria

1. WHEN assessing capabilities THEN the system SHALL measure response quality
2. WHEN capabilities are measured THEN context injection SHALL be optimized
""")
        
        # Create comprehensive source code structure
        src_dir = repo_path / "src" / "beast_mode"
        
        # Integration Orchestrator implementation
        io_impl = src_dir / "integration_orchestrator"
        io_impl.mkdir(parents=True, exist_ok=True)
        
        (io_impl / "__init__.py").write_text("# Integration Orchestrator Framework")
        (io_impl / "discovery_engine.py").write_text("""
class DiscoveryEngine:
    '''Integration discovery engine for systematic pattern detection'''
    
    def __init__(self):
        self.integration_orchestrator_patterns = []
    
    def discover_integrations(self):
        '''Discover existing integration patterns'''
        return self.integration_orchestrator_patterns
""")
        
        (io_impl / "pattern_registry.py").write_text("""
class PatternRegistry:
    '''Registry for integration_orchestrator patterns'''
    
    def __init__(self):
        self.patterns = {}
    
    def register_pattern(self, pattern):
        '''Register integration orchestrator pattern'''
        self.patterns[pattern.name] = pattern
""")
        
        # Cursor Sharing implementation
        cursor_impl = src_dir / "cursor_sharing"
        cursor_impl.mkdir(parents=True, exist_ok=True)
        
        (cursor_impl / "__init__.py").write_text("# AI-Driven Cursor Sharing")
        (cursor_impl / "cursor_manager.py").write_text("""
class CursorManager:
    '''AI-enhanced cursor sharing manager'''
    
    def __init__(self):
        self.cursor_sharing_active = True
        self.ai_engine = None
    
    def capture_cursor_events(self):
        '''Capture cursor events for AI processing'''
        pass
""")
        
        (cursor_impl / "ai_behavioral_engine.py").write_text("""
class AIBehavioralEngine:
    '''AI engine for cursor_sharing behavioral analysis'''
    
    def __init__(self):
        self.learning_enabled = True
    
    def analyze_behavior(self, cursor_data):
        '''Analyze cursor sharing behavior patterns'''
        return {"pattern": "learned", "confidence": 0.95}
""")
        
        # GPT-5 Calibration implementation
        gpt5_impl = src_dir / "gpt5_calibration"
        gpt5_impl.mkdir(parents=True, exist_ok=True)
        
        (gpt5_impl / "__init__.py").write_text("# GPT-5 Context Calibration")
        (gpt5_impl / "calibrator.py").write_text("""
class GPT5Calibrator:
    '''GPT5 context calibration system'''
    
    def __init__(self):
        self.gpt5_integration_active = True
    
    def assess_capabilities(self):
        '''Assess GPT5 capabilities for context optimization'''
        return {"capability_score": 0.92, "context_size": 128000}
""")
        
        (gpt5_impl / "context_injector.py").write_text("""
class ContextInjector:
    '''Context injection system for gpt5 optimization'''
    
    def __init__(self):
        self.injection_strategies = []
    
    def inject_context(self, context_data):
        '''Inject optimized context for GPT5'''
        return {"injected": True, "optimization": "gpt5_enhanced"}
""")
    
    def test_complete_data_population_workflow(self):
        """Test complete data population workflow with realistic data"""
        # 1. Populate specifications
        spec_result = self.data_populator.populate_specifications()
        self.assertTrue(spec_result.success)
        self.assertEqual(len(spec_result.imported_specs), 3)
        
        # 2. Import documents
        doc_result = self.data_populator.import_documents()
        self.assertTrue(doc_result.success)
        self.assertGreater(len(doc_result.imported_files), 0)
        
        # 3. Link code files
        code_result = self.data_populator.link_code_files()
        self.assertTrue(code_result.success)
        self.assertGreater(len(code_result.imported_files), 0)
        
        # 4. Validate relationships
        validation_result = self.data_populator.validate_relationships()
        self.assertTrue(validation_result.is_valid)
        self.assertGreater(validation_result.validated_relationships, 0)
        
        # 5. Verify data integrity in database
        cursor = self.schema_manager.connection.cursor()
        
        # Check specifications
        cursor.execute("SELECT COUNT(*) FROM specifications")
        spec_count = cursor.fetchone()[0]
        self.assertEqual(spec_count, 3)
        
        # Check documents (3 specs × 3 doc types = 9 documents)
        cursor.execute("SELECT COUNT(*) FROM documents")
        doc_count = cursor.fetchone()[0]
        self.assertEqual(doc_count, 9)
        
        # Check code files (should have multiple files)
        cursor.execute("SELECT COUNT(*) FROM code_files")
        file_count = cursor.fetchone()[0]
        self.assertGreater(file_count, 0)
        
        # Check relationships
        cursor.execute("""
            SELECT s.name, COUNT(cf.id) as code_files, COUNT(d.id) as documents
            FROM specifications s
            LEFT JOIN code_files cf ON s.id = cf.specification_id
            LEFT JOIN documents d ON s.id = d.specification_id
            GROUP BY s.id, s.name
        """)
        
        relationships = cursor.fetchall()
        cursor.close()
        
        # Each specification should have related items
        for spec_name, code_file_count, doc_count in relationships:
            self.assertIn(spec_name, self.data_populator.target_specifications)
            self.assertGreater(doc_count, 0)  # Should have documents
        
        # 6. Test cleanup and rollback
        cleanup_result = self.data_populator.cleanup_data()
        self.assertTrue(cleanup_result.success)
        
        # Verify cleanup worked
        cursor = self.schema_manager.connection.cursor()
        cursor.execute("SELECT COUNT(*) FROM specifications")
        final_spec_count = cursor.fetchone()[0]
        cursor.close()
        
        self.assertLess(final_spec_count, spec_count)


if __name__ == '__main__':
    # Configure logging for tests
    import logging
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Run tests
    unittest.main(verbosity=2)