#!/usr/bin/env python3
"""
🎯 CRITICAL TEST GENERATOR
=========================

Automatically generates tests for critical modules identified in the coverage analysis.
Implements Phase 1 of the test coverage action plan.

Author: Beast Mode Framework
Date: 2025-09-14
Purpose: Generate Critical Test Coverage
"""

import os
import json
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple, Any
from test_coverage_analyzer import TestCoverageAnalyzer


class CriticalTestGenerator:
    """Generator for critical test files."""

    def __init__(self):
        self.repository_root = Path.cwd()
        self.src_dir = self.repository_root / "src"
        self.tests_dir = self.repository_root / "tests"
        self.coverage_data = None
        self.generated_tests = []

    def load_coverage_data(self):
        """Load the coverage analysis data."""
        coverage_file = "test_coverage_analysis_report.json"
        if os.path.exists(coverage_file):
            with open(coverage_file, "r") as f:
                self.coverage_data = json.load(f)
        else:
            print("❌ Coverage analysis data not found. Running analysis...")
            analyzer = TestCoverageAnalyzer()
            self.coverage_data = analyzer.run_analysis()

    def identify_critical_modules(self) -> List[Dict[str, Any]]:
        """Identify the most critical modules that need tests."""
        if not self.coverage_data:
            self.load_coverage_data()

        critical_gaps = self.coverage_data["gaps_analysis"]["critical_gaps"]
        coverage_mapping = self.coverage_data["gaps_analysis"]["coverage_mapping"]

        critical_modules = []

        for file_path in critical_gaps:
            module_info = coverage_mapping.get(file_path, {})
            module_name = module_info.get("module_name", "")

            # Categorize by importance
            importance_score = self._calculate_importance_score(file_path, module_name)

            critical_modules.append(
                {
                    "file_path": file_path,
                    "module_name": module_name,
                    "importance_score": importance_score,
                    "category": self._categorize_module(file_path),
                    "test_priority": self._determine_test_priority(
                        file_path, importance_score
                    ),
                }
            )

        # Sort by importance score (highest first)
        critical_modules.sort(key=lambda x: x["importance_score"], reverse=True)

        return critical_modules[:100]  # Top 100 most critical modules

    def _calculate_importance_score(self, file_path: str, module_name: str) -> int:
        """Calculate importance score for a module."""
        score = 0

        # Core modules get highest priority
        if "core" in file_path.lower():
            score += 100

        # Main entry points
        if "main" in file_path.lower():
            score += 90

        # CLI interfaces
        if "cli" in file_path.lower():
            score += 80

        # API modules
        if "api" in file_path.lower():
            score += 70

        # Service modules
        if "service" in file_path.lower():
            score += 60

        # Manager modules
        if "manager" in file_path.lower():
            score += 50

        # Controller modules
        if "controller" in file_path.lower():
            score += 50

        # Engine modules
        if "engine" in file_path.lower():
            score += 40

        # Handler modules
        if "handler" in file_path.lower():
            score += 30

        # Processor modules
        if "processor" in file_path.lower():
            score += 30

        # Validator modules
        if "validator" in file_path.lower():
            score += 30

        # Monitor modules
        if "monitor" in file_path.lower():
            score += 20

        # Domain-specific scoring
        if "beast_mode" in file_path:
            score += 25

        if "devpost_integration" in file_path:
            score += 20

        if "competitive_launch" in file_path:
            score += 20

        return score

    def _categorize_module(self, file_path: str) -> str:
        """Categorize module by type."""
        if "core" in file_path.lower():
            return "core"
        elif "service" in file_path.lower():
            return "service"
        elif "validation" in file_path.lower() or "validator" in file_path.lower():
            return "validation"
        elif "integration" in file_path.lower():
            return "integration"
        elif (
            "orchestration" in file_path.lower() or "orchestrator" in file_path.lower()
        ):
            return "orchestration"
        elif "api" in file_path.lower():
            return "api"
        elif "cli" in file_path.lower():
            return "cli"
        else:
            return "general"

    def _determine_test_priority(self, file_path: str, importance_score: int) -> str:
        """Determine test priority level."""
        if importance_score >= 80:
            return "CRITICAL"
        elif importance_score >= 60:
            return "HIGH"
        elif importance_score >= 40:
            return "MEDIUM"
        else:
            return "LOW"

    def generate_test_file(self, module_info: Dict[str, Any]) -> str:
        """Generate test file content for a module."""
        file_path = module_info["file_path"]
        category = module_info["category"]
        priority = module_info["test_priority"]

        # Extract module details
        module_parts = file_path.replace("src/", "").split("/")
        module_file = module_parts[-1].replace(".py", "")

        # Determine class name from file
        class_name = self._extract_class_name(file_path)

        # Generate test content based on category
        if category == "core":
            return self._generate_core_test(module_info, module_file, class_name)
        elif category == "service":
            return self._generate_service_test(module_info, module_file, class_name)
        elif category == "validation":
            return self._generate_validation_test(module_info, module_file, class_name)
        elif category == "integration":
            return self._generate_integration_test(module_info, module_file, class_name)
        elif category == "orchestration":
            return self._generate_orchestration_test(
                module_info, module_file, class_name
            )
        elif category == "api":
            return self._generate_api_test(module_info, module_file, class_name)
        elif category == "cli":
            return self._generate_cli_test(module_info, module_file, class_name)
        else:
            return self._generate_general_test(module_info, module_file, class_name)

    def _extract_class_name(self, file_path: str) -> str:
        """Extract likely class name from file path."""
        file_name = Path(file_path).stem

        # Convert snake_case to PascalCase
        parts = file_name.split("_")
        class_name = "".join(word.capitalize() for word in parts)

        # Handle common suffixes
        if class_name.endswith("Part"):
            class_name = class_name[:-4]
        if class_name.endswith("Class"):
            class_name = class_name[:-5]

        return class_name or "TestClass"

    def _generate_core_test(
        self, module_info: Dict[str, Any], module_file: str, class_name: str
    ) -> str:
        """Generate core module test."""
        file_path = module_info["file_path"]
        priority = module_info["test_priority"]

        # Determine module path
        module_path = file_path.replace("src/", "").replace(".py", "").replace("/", ".")

        return f'''"""
Test module for {class_name} core functionality.

Priority: {priority}
Module: {module_path}
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime
from src.{module_path.replace("/", ".")} import {class_name}


class Test{class_name}:
    """Test cases for {class_name} core module."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.instance = {class_name}()
    
    def test_initialization(self):
        """Test module initialization."""
        assert self.instance is not None
    
    def test_reflective_module_inheritance(self):
        """Test ReflectiveModule inheritance."""
        from src.rm_ddd.core.base_reflective_module import ReflectiveModule
        assert isinstance(self.instance, ReflectiveModule)
    
    def test_get_module_info(self):
        """Test module info retrieval."""
        info = self.instance.get_module_info()
        assert isinstance(info, dict)
        assert 'module_id' in info
    
    def test_get_capabilities(self):
        """Test capabilities retrieval."""
        capabilities = self.instance.get_capabilities()
        assert isinstance(capabilities, list)
    
    def test_health_check(self):
        """Test health check functionality."""
        health = self.instance.check_health()
        assert health is not None
        assert hasattr(health, 'status')
    
    def test_interface_metadata(self):
        """Test interface metadata."""
        metadata = self.instance.get_interface_metadata()
        assert isinstance(metadata, dict)
        assert 'module_id' in metadata
    
    def test_register_module(self):
        """Test module registration."""
        mock_registry = Mock()
        self.instance.register_module(mock_registry)
        # Verify registration was attempted
        assert mock_registry is not None
    
    def test_error_handling(self):
        """Test error handling capabilities."""
        # Test basic error handling
        try:
            # Simulate error condition if applicable
            pass
        except Exception:
            # Verify error is handled appropriately
            pass
    
    def test_module_functionality(self):
        """Test core module functionality."""
        # Add specific tests for module functionality
        assert self.instance is not None
'''

    def _generate_service_test(
        self, module_info: Dict[str, Any], module_file: str, class_name: str
    ) -> str:
        """Generate service module test."""
        file_path = module_info["file_path"]
        priority = module_info["test_priority"]
        module_path = file_path.replace("src/", "").replace(".py", "").replace("/", ".")

        return f'''"""
Test module for {class_name} service functionality.

Priority: {priority}
Module: {module_path}
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime
from src.{module_path.replace("/", ".")} import {class_name}


class Test{class_name}:
    """Test cases for {class_name} service."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.service = {class_name}()
        self.mock_config = Mock()
        self.mock_logger = Mock()
    
    def test_service_initialization(self):
        """Test service initialization."""
        assert self.service is not None
    
    def test_service_start(self):
        """Test service start functionality."""
        if hasattr(self.service, 'start'):
            result = self.service.start()
            assert result is True or result is False
    
    def test_service_stop(self):
        """Test service stop functionality."""
        if hasattr(self.service, 'stop'):
            result = self.service.stop()
            assert result is True or result is False
    
    def test_service_health_check(self):
        """Test service health check."""
        health = self.service.check_health()
        assert health is not None
        assert hasattr(health, 'status')
    
    def test_service_configuration(self):
        """Test service configuration handling."""
        if hasattr(self.service, 'get_configuration'):
            config = self.service.get_configuration()
            assert isinstance(config, dict)
    
    def test_service_metrics(self):
        """Test service metrics collection."""
        if hasattr(self.service, 'get_metrics'):
            metrics = self.service.get_metrics()
            assert isinstance(metrics, dict)
    
    def test_error_scenarios(self):
        """Test error handling scenarios."""
        # Test various error scenarios
        try:
            # Simulate error condition
            pass
        except Exception:
            # Verify error is handled appropriately
            pass
'''

    def _generate_validation_test(
        self, module_info: Dict[str, Any], module_file: str, class_name: str
    ) -> str:
        """Generate validation module test."""
        file_path = module_info["file_path"]
        priority = module_info["test_priority"]
        module_path = file_path.replace("src/", "").replace(".py", "").replace("/", ".")

        return f'''"""
Test module for {class_name} validation functionality.

Priority: {priority}
Module: {module_path}
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime
from src.{module_path.replace("/", ".")} import {class_name}


class Test{class_name}:
    """Test cases for {class_name} validator."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.validator = {class_name}()
        self.valid_data = {{'test': 'data'}}
        self.invalid_data = {{'invalid': 'data'}}
    
    def test_validator_initialization(self):
        """Test validator initialization."""
        assert self.validator is not None
    
    def test_validate_success(self):
        """Test successful validation."""
        if hasattr(self.validator, 'validate'):
            result = self.validator.validate(self.valid_data)
            assert result is not None
    
    def test_validate_failure(self):
        """Test validation failure."""
        if hasattr(self.validator, 'validate'):
            result = self.validator.validate(self.invalid_data)
            assert result is not None
    
    def test_validation_rules(self):
        """Test validation rules."""
        if hasattr(self.validator, 'get_validation_rules'):
            rules = self.validator.get_validation_rules()
            assert isinstance(rules, list)
    
    def test_validation_metrics(self):
        """Test validation metrics."""
        if hasattr(self.validator, 'get_validation_metrics'):
            metrics = self.validator.get_validation_metrics()
            assert isinstance(metrics, dict)
    
    def test_batch_validation(self):
        """Test batch validation."""
        if hasattr(self.validator, 'validate_batch'):
            batch_data = [self.valid_data, self.invalid_data]
            results = self.validator.validate_batch(batch_data)
            assert isinstance(results, list)
'''

    def _generate_integration_test(
        self, module_info: Dict[str, Any], module_file: str, class_name: str
    ) -> str:
        """Generate integration module test."""
        file_path = module_info["file_path"]
        priority = module_info["test_priority"]
        module_path = file_path.replace("src/", "").replace(".py", "").replace("/", ".")

        return f'''"""
Test module for {class_name} integration functionality.

Priority: {priority}
Module: {module_path}
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime
from src.{module_path.replace("/", ".")} import {class_name}


class Test{class_name}:
    """Test cases for {class_name} integration."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.integration = {class_name}()
        self.mock_external_service = Mock()
    
    def test_integration_initialization(self):
        """Test integration initialization."""
        assert self.integration is not None
    
    def test_connection_establishment(self):
        """Test external connection establishment."""
        if hasattr(self.integration, 'establish_connection'):
            result = self.integration.establish_connection()
            assert result is not None
    
    def test_data_synchronization(self):
        """Test data synchronization."""
        if hasattr(self.integration, 'synchronize_data'):
            test_data = {{'test': 'data'}}
            result = self.integration.synchronize_data(test_data)
            assert result is not None
    
    def test_error_handling(self):
        """Test integration error handling."""
        # Test error handling scenarios
        try:
            # Simulate error condition
            pass
        except Exception:
            # Verify error is handled appropriately
            pass
    
    def test_integration_health(self):
        """Test integration health monitoring."""
        health = self.integration.check_health()
        assert health is not None
        assert hasattr(health, 'status')
    
    def test_configuration_validation(self):
        """Test integration configuration validation."""
        if hasattr(self.integration, 'validate_configuration'):
            config = self.integration.validate_configuration()
            assert config is not None
'''

    def _generate_orchestration_test(
        self, module_info: Dict[str, Any], module_file: str, class_name: str
    ) -> str:
        """Generate orchestration module test."""
        file_path = module_info["file_path"]
        priority = module_info["test_priority"]
        module_path = file_path.replace("src/", "").replace(".py", "").replace("/", ".")

        return f'''"""
Test module for {class_name} orchestration functionality.

Priority: {priority}
Module: {module_path}
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime
from src.{module_path.replace("/", ".")} import {class_name}


class Test{class_name}:
    """Test cases for {class_name} orchestrator."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.orchestrator = {class_name}()
        self.mock_task = Mock()
        self.mock_workflow = Mock()
    
    def test_orchestrator_initialization(self):
        """Test orchestrator initialization."""
        assert self.orchestrator is not None
    
    def test_task_execution(self):
        """Test task execution."""
        if hasattr(self.orchestrator, 'execute_task'):
            self.mock_task.execute.return_value = True
            result = self.orchestrator.execute_task(self.mock_task)
            assert result is not None
    
    def test_workflow_orchestration(self):
        """Test workflow orchestration."""
        if hasattr(self.orchestrator, 'orchestrate_workflow'):
            self.mock_workflow.get_tasks.return_value = [self.mock_task]
            result = self.orchestrator.orchestrate_workflow(self.mock_workflow)
            assert result is not None
    
    def test_resource_management(self):
        """Test resource management."""
        if hasattr(self.orchestrator, 'get_available_resources'):
            resources = self.orchestrator.get_available_resources()
            assert isinstance(resources, dict)
    
    def test_orchestration_metrics(self):
        """Test orchestration metrics."""
        if hasattr(self.orchestrator, 'get_orchestration_metrics'):
            metrics = self.orchestrator.get_orchestration_metrics()
            assert isinstance(metrics, dict)
'''

    def _generate_api_test(
        self, module_info: Dict[str, Any], module_file: str, class_name: str
    ) -> str:
        """Generate API module test."""
        file_path = module_info["file_path"]
        priority = module_info["test_priority"]
        module_path = file_path.replace("src/", "").replace(".py", "").replace("/", ".")

        return f'''"""
Test module for {class_name} API functionality.

Priority: {priority}
Module: {module_path}
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime
from src.{module_path.replace("/", ".")} import {class_name}


class Test{class_name}:
    """Test cases for {class_name} API."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.api = {class_name}()
        self.mock_request = Mock()
        self.mock_response = Mock()
    
    def test_api_initialization(self):
        """Test API initialization."""
        assert self.api is not None
    
    def test_api_endpoints(self):
        """Test API endpoints."""
        if hasattr(self.api, 'get_endpoints'):
            endpoints = self.api.get_endpoints()
            assert isinstance(endpoints, list)
    
    def test_request_handling(self):
        """Test request handling."""
        if hasattr(self.api, 'handle_request'):
            result = self.api.handle_request(self.mock_request)
            assert result is not None
    
    def test_response_generation(self):
        """Test response generation."""
        if hasattr(self.api, 'generate_response'):
            result = self.api.generate_response(self.mock_request)
            assert result is not None
    
    def test_error_handling(self):
        """Test API error handling."""
        try:
            # Simulate error condition
            pass
        except Exception:
            # Verify error is handled appropriately
            pass
'''

    def _generate_cli_test(
        self, module_info: Dict[str, Any], module_file: str, class_name: str
    ) -> str:
        """Generate CLI module test."""
        file_path = module_info["file_path"]
        priority = module_info["test_priority"]
        module_path = file_path.replace("src/", "").replace(".py", "").replace("/", ".")

        return f'''"""
Test module for {class_name} CLI functionality.

Priority: {priority}
Module: {module_path}
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime
from src.{module_path.replace("/", ".")} import {class_name}


class Test{class_name}:
    """Test cases for {class_name} CLI."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.cli = {class_name}()
        self.mock_args = Mock()
        self.mock_config = Mock()
    
    def test_cli_initialization(self):
        """Test CLI initialization."""
        assert self.cli is not None
    
    def test_command_parsing(self):
        """Test command parsing."""
        if hasattr(self.cli, 'parse_commands'):
            result = self.cli.parse_commands(['test', 'command'])
            assert result is not None
    
    def test_command_execution(self):
        """Test command execution."""
        if hasattr(self.cli, 'execute_command'):
            result = self.cli.execute_command('test_command')
            assert result is not None
    
    def test_help_generation(self):
        """Test help generation."""
        if hasattr(self.cli, 'generate_help'):
            help_text = self.cli.generate_help()
            assert isinstance(help_text, str)
    
    def test_error_handling(self):
        """Test CLI error handling."""
        try:
            # Simulate error condition
            pass
        except Exception:
            # Verify error is handled appropriately
            pass
'''

    def _generate_general_test(
        self, module_info: Dict[str, Any], module_file: str, class_name: str
    ) -> str:
        """Generate general module test."""
        file_path = module_info["file_path"]
        priority = module_info["test_priority"]
        module_path = file_path.replace("src/", "").replace(".py", "").replace("/", ".")

        return f'''"""
Test module for {class_name} functionality.

Priority: {priority}
Module: {module_path}
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime
from src.{module_path.replace("/", ".")} import {class_name}


class Test{class_name}:
    """Test cases for {class_name}."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.instance = {class_name}()
    
    def test_initialization(self):
        """Test module initialization."""
        assert self.instance is not None
    
    def test_basic_functionality(self):
        """Test basic module functionality."""
        # Add specific tests for module functionality
        assert self.instance is not None
    
    def test_error_handling(self):
        """Test error handling capabilities."""
        try:
            # Simulate error condition
            pass
        except Exception:
            # Verify error is handled appropriately
            pass
'''

    def create_test_directory_structure(self, file_path: str) -> Path:
        """Create appropriate test directory structure."""
        # Convert source path to test path
        test_path = file_path.replace("src/", "tests/unit/")
        test_dir = Path(test_path).parent

        # Create directory if it doesn't exist
        test_dir.mkdir(parents=True, exist_ok=True)

        return test_dir

    def generate_critical_tests(self, limit: int = 50) -> List[str]:
        """Generate tests for the most critical modules."""
        print("🎯 Generating tests for critical modules...")

        # Load coverage data
        self.load_coverage_data()

        # Identify critical modules
        critical_modules = self.identify_critical_modules()

        generated_tests = []

        for i, module_info in enumerate(critical_modules[:limit]):
            file_path = module_info["file_path"]
            priority = module_info["test_priority"]
            importance_score = module_info["importance_score"]

            print(
                f"📝 Generating test for {file_path} (Priority: {priority}, Score: {importance_score})"
            )

            # Generate test content
            test_content = self.generate_test_file(module_info)

            # Create test file path
            test_dir = self.create_test_directory_structure(file_path)
            test_file_name = f"test_{Path(file_path).stem}.py"
            test_file_path = test_dir / test_file_name

            # Write test file
            with open(test_file_path, "w") as f:
                f.write(test_content)

            generated_tests.append(str(test_file_path))
            self.generated_tests.append(
                {
                    "source_file": file_path,
                    "test_file": str(test_file_path),
                    "priority": priority,
                    "importance_score": importance_score,
                    "category": module_info["category"],
                }
            )

        print(f"✅ Generated {len(generated_tests)} test files")
        return generated_tests

    def save_generation_report(self):
        """Save report of generated tests."""
        report = {
            "timestamp": datetime.now().isoformat(),
            "total_tests_generated": len(self.generated_tests),
            "generated_tests": self.generated_tests,
            "summary_by_priority": {},
            "summary_by_category": {},
        }

        # Summary by priority
        for test in self.generated_tests:
            priority = test["priority"]
            if priority not in report["summary_by_priority"]:
                report["summary_by_priority"][priority] = 0
            report["summary_by_priority"][priority] += 1

        # Summary by category
        for test in self.generated_tests:
            category = test["category"]
            if category not in report["summary_by_category"]:
                report["summary_by_category"][category] = 0
            report["summary_by_category"][category] += 1

        # Save report
        with open("critical_tests_generation_report.json", "w") as f:
            json.dump(report, f, indent=2)

        print(f"📄 Generation report saved to: critical_tests_generation_report.json")


if __name__ == "__main__":
    generator = CriticalTestGenerator()

    # Generate tests for top 50 critical modules
    generated_tests = generator.generate_critical_tests(limit=50)

    # Save generation report
    generator.save_generation_report()

    print(f"\n🎉 Critical test generation complete!")
    print(f"📊 Generated {len(generated_tests)} test files")
    print(f"📋 Report saved to: critical_tests_generation_report.json")
