"""
Unit tests for MakefileGovernanceEngine.

Tests governance rule enforcement, quality metrics calculation,
and compliance validation functionality.
"""

import pytest
import tempfile
import shutil
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

from src.makefile_governance.core.governance_engine import (
    MakefileGovernanceEngine,
    GovernanceRule,
    GovernanceRuleType,
    ViolationSeverity,
    GovernanceViolation,
    GovernanceResult
)
from src.rm_ddd.core.unified_reflective_module import ModuleStatus, ModuleCapability


class TestMakefileGovernanceEngine:
    """Test suite for MakefileGovernanceEngine."""
    
    @pytest.fixture
    def engine(self):
        """Create a MakefileGovernanceEngine instance."""
        return MakefileGovernanceEngine()
    
    @pytest.fixture
    def temp_dir(self):
        """Create a temporary directory for test files."""
        temp_dir = Path(tempfile.mkdtemp())
        yield temp_dir
        shutil.rmtree(temp_dir)
    
    def test_module_initialization(self, engine):
        """Test that the governance engine initializes correctly."""
        assert engine.module_id == "makefile_governance_engine"
        assert isinstance(engine.get_capabilities(), list)
        assert ModuleCapability.VALIDATION in engine.get_capabilities()
        assert ModuleCapability.DATA_PROCESSING in engine.get_capabilities()
        assert ModuleCapability.CORE_FUNCTIONALITY in engine.get_capabilities()
        
        # Check that default rules are loaded
        rules = engine.get_governance_rules()
        assert len(rules) > 0
        
        # Check for expected rule types
        rule_types = [rule.rule_type for rule in rules]
        assert GovernanceRuleType.NAMING_CONVENTION in rule_types
        assert GovernanceRuleType.PHONY_DECLARATION in rule_types
        assert GovernanceRuleType.COMPLEXITY_LIMIT in rule_types
    
    def test_get_module_info(self, engine):
        """Test module info retrieval."""
        info = engine.get_module_info()
        
        assert info["module_id"] == "makefile_governance_engine"
        assert info["name"] == "Makefile Governance Engine"
        assert info["version"] == "1.0.0"
        assert "capabilities" in info
        assert "statistics" in info
        assert "rules" in info
        
        # Check statistics structure
        stats = info["statistics"]
        assert "validations_performed" in stats
        assert "violations_detected" in stats
        assert "compliance_rate" in stats
        
        # Check rules info
        rules_info = info["rules"]
        assert "total_rules" in rules_info
        assert "enabled_rules" in rules_info
    
    def test_get_health_status_healthy(self, engine):
        """Test health status when engine is healthy."""
        # Set high compliance rate
        engine._compliance_rate = 0.95
        
        health = engine.get_health_status()
        
        assert health.module_id == "makefile_governance_engine"
        assert health.status == ModuleStatus.HEALTHY
        assert health.health_score == 1.0
    
    def test_get_health_status_with_violations(self, engine):
        """Test health status when engine has detected violations."""
        # Simulate validation activity with violations
        engine._validation_count = 10
        engine._violation_count = 3
        engine._compliance_rate = 0.7  # 70% compliance
        
        health = engine.get_health_status()
        
        assert health.status == ModuleStatus.WARNING
        assert health.health_score == 0.7
        assert len(health.issues) > 0
        assert "Compliance rate below threshold" in health.issues[0]
    
    def test_graceful_degradation(self, engine):
        """Test graceful degradation functionality."""
        result = engine.graceful_degradation()
        
        assert result.success is True
        assert ModuleCapability.DATA_PROCESSING in result.degraded_capabilities
        assert ModuleCapability.VALIDATION in result.remaining_capabilities
        assert ModuleCapability.CORE_FUNCTIONALITY in result.remaining_capabilities
        assert result.error_message is None
    
    def test_validate_nonexistent_file(self, engine, temp_dir):
        """Test governance validation of non-existent makefile."""
        nonexistent_file = temp_dir / "nonexistent.mk"
        
        result = engine.validate_governance(nonexistent_file)
        
        assert result.is_compliant is False
        assert len(result.violations) == 1
        assert "Makefile not found" in result.violations[0].message
    
    def test_validate_compliant_makefile(self, engine, temp_dir):
        """Test validation of a governance-compliant makefile."""
        makefile_content = """# Compliant Makefile
.PHONY: help clean test

PROJECT_NAME := test-project
VERSION := 1.0.0

help: ## Show help message
\t@echo "Available targets:"
\t@echo "  help  - Show this help"

clean: ## Clean build artifacts
\t@echo "Cleaning..."
\trm -rf build/

test: ## Run tests
\t@echo "Running tests..."
\tpython -m pytest
"""
        
        makefile_path = temp_dir / "Makefile"
        makefile_path.write_text(makefile_content)
        
        result = engine.validate_governance(makefile_path)
        
        assert result.is_compliant is True
        assert len([v for v in result.violations if v.rule.severity in [ViolationSeverity.ERROR, ViolationSeverity.CRITICAL]]) == 0
        assert result.quality_score > 0.8
        assert result.complexity_score < 0.5
    
    def test_naming_convention_violations(self, engine, temp_dir):
        """Test detection of naming convention violations."""
        makefile_content = """# Makefile with naming violations
.PHONY: help

help: ## Show help
\t@echo "Help"

build_project: ## Build project (underscore violation)
\t@echo "Building..."

TestTarget: ## Test target (CamelCase violation)
\t@echo "Testing..."

CLEAN_ALL: ## Clean all (uppercase violation)
\t@echo "Cleaning..."
"""
        
        makefile_path = temp_dir / "Makefile"
        makefile_path.write_text(makefile_content)
        
        result = engine.validate_governance(makefile_path)
        
        # Should have naming convention violations
        naming_violations = [v for v in result.violations 
                           if v.rule.rule_type == GovernanceRuleType.NAMING_CONVENTION]
        assert len(naming_violations) >= 3
        
        # Check specific violations
        violation_targets = [v.target_name for v in naming_violations]
        assert "build_project" in violation_targets
        assert "TestTarget" in violation_targets
        assert "CLEAN_ALL" in violation_targets
        
        # Check suggested fixes
        for violation in naming_violations:
            assert violation.suggested_fix is not None
            assert violation.suggested_fix.islower()
            assert '_' not in violation.suggested_fix or '-' in violation.suggested_fix
    
    def test_phony_declaration_violations(self, engine, temp_dir):
        """Test detection of missing PHONY declarations."""
        makefile_content = """# Makefile missing PHONY declarations
help: ## Show help
\t@echo "Help"

clean: ## Clean up
\t@echo "Cleaning..."

test: ## Run tests
\t@echo "Testing..."

build: ## Build project
\t@echo "Building..."

# Only help is declared as PHONY
.PHONY: help
"""
        
        makefile_path = temp_dir / "Makefile"
        makefile_path.write_text(makefile_content)
        
        result = engine.validate_governance(makefile_path)
        
        # Should have PHONY declaration violations
        phony_violations = [v for v in result.violations 
                          if v.rule.rule_type == GovernanceRuleType.PHONY_DECLARATION]
        assert len(phony_violations) >= 3  # clean, test, build
        
        # Check specific violations
        violation_targets = [v.target_name for v in phony_violations]
        assert "clean" in violation_targets
        assert "test" in violation_targets
        assert "build" in violation_targets
        
        # Check suggested fixes
        for violation in phony_violations:
            assert violation.suggested_fix is not None
            assert ".PHONY:" in violation.suggested_fix
            assert violation.target_name in violation.suggested_fix
    
    def test_complexity_limit_violations(self, engine, temp_dir):
        """Test detection of overly complex recipes."""
        makefile_content = """# Makefile with complex recipes
.PHONY: simple complex

simple: ## Simple target
\t@echo "Simple"

complex: ## Complex target with many lines
\t@echo "Starting complex operation..."
\t@mkdir -p build/
\t@cp src/* build/
\t@cd build && make all
\t@echo "Running tests..."
\t@python -m pytest
\t@echo "Generating docs..."
\t@sphinx-build docs/ build/docs/
\t@echo "Complex operation complete"
"""
        
        makefile_path = temp_dir / "Makefile"
        makefile_path.write_text(makefile_content)
        
        result = engine.validate_governance(makefile_path)
        
        # Should have complexity violations
        complexity_violations = [v for v in result.violations 
                               if v.rule.rule_type == GovernanceRuleType.COMPLEXITY_LIMIT]
        assert len(complexity_violations) >= 1
        
        # Check the complex target violation
        complex_violation = next((v for v in complexity_violations if v.target_name == "complex"), None)
        assert complex_violation is not None
        assert "consider using external script" in complex_violation.message.lower()
        assert "scripts/" in complex_violation.suggested_fix
    
    def test_environment_variable_violations(self, engine, temp_dir):
        """Test detection of environment variable naming violations."""
        makefile_content = """# Makefile with env var violations
.PHONY: test

VALID_VAR := value
invalid-var := value

test: ## Test target
\t@echo "Using $(VALID_VAR)"
\t@echo "Using $(invalid-var)"
\t@echo "Using $(lowercase_var)"
\t@echo "Using $(MixedCase_Var)"
"""
        
        makefile_path = temp_dir / "Makefile"
        makefile_path.write_text(makefile_content)
        
        result = engine.validate_governance(makefile_path)
        
        # Should have environment variable violations
        env_violations = [v for v in result.violations 
                         if v.rule.rule_type == GovernanceRuleType.ENVIRONMENT_VARIABLE]
        assert len(env_violations) >= 2  # invalid-var, lowercase_var, MixedCase_Var
        
        # Check that valid variables don't generate violations
        violation_messages = [v.message for v in env_violations]
        assert not any("VALID_VAR" in msg for msg in violation_messages)
    
    def test_target_description_violations(self, engine, temp_dir):
        """Test detection of missing target descriptions."""
        makefile_content = """# Makefile with missing descriptions
.PHONY: help clean test build

help: ## Show help (has description)
\t@echo "Help"

clean:
\t@echo "Cleaning..."

test:
\t@echo "Testing..."

build: ## Build project (has description)
\t@echo "Building..."
"""
        
        makefile_path = temp_dir / "Makefile"
        makefile_path.write_text(makefile_content)
        
        result = engine.validate_governance(makefile_path)
        
        # Should have target description violations
        desc_violations = [v for v in result.violations 
                          if v.rule.rule_type == GovernanceRuleType.TARGET_DESCRIPTION]
        assert len(desc_violations) >= 2  # clean and test
        
        # Check specific violations
        violation_targets = [v.target_name for v in desc_violations]
        assert "clean" in violation_targets
        assert "test" in violation_targets
        
        # Should not have violations for targets with descriptions
        assert "help" not in violation_targets
        assert "build" not in violation_targets
    
    def test_complexity_score_calculation(self, engine):
        """Test complexity score calculation."""
        # Simple makefile
        simple_content = """help:
\t@echo "help"
"""
        simple_score = engine._calculate_complexity_score(simple_content)
        assert 0.0 <= simple_score <= 1.0
        
        # Complex makefile
        complex_content = """# Complex makefile with many targets
""" + "\n".join([f"target{i}:\n\t@echo 'target{i}'" for i in range(25)])
        
        complex_score = engine._calculate_complexity_score(complex_content)
        assert complex_score > simple_score
        assert 0.0 <= complex_score <= 1.0
    
    def test_quality_score_calculation(self, engine):
        """Test quality score calculation."""
        content = "help:\n\t@echo 'help'"
        
        # No violations should give high quality score
        no_violations_score = engine._calculate_quality_score(content, [])
        assert no_violations_score == 1.0
        
        # Create mock violations
        mock_rule = GovernanceRule(
            rule_type=GovernanceRuleType.NAMING_CONVENTION,
            name="test_rule",
            description="Test rule",
            severity=ViolationSeverity.WARNING
        )
        
        violations = [
            GovernanceViolation(
                rule=mock_rule,
                line_number=1,
                line_content="help:",
                message="Test violation"
            )
        ]
        
        with_violations_score = engine._calculate_quality_score(content, violations)
        assert with_violations_score < no_violations_score
        assert 0.0 <= with_violations_score <= 1.0
    
    def test_recommendations_generation(self, engine):
        """Test generation of recommendations."""
        # Create mock violations of different types
        naming_rule = GovernanceRule(
            rule_type=GovernanceRuleType.NAMING_CONVENTION,
            name="naming",
            description="Naming rule",
            severity=ViolationSeverity.WARNING
        )
        
        phony_rule = GovernanceRule(
            rule_type=GovernanceRuleType.PHONY_DECLARATION,
            name="phony",
            description="PHONY rule",
            severity=ViolationSeverity.WARNING
        )
        
        violations = [
            GovernanceViolation(naming_rule, 1, "test_target:", "Naming violation"),
            GovernanceViolation(naming_rule, 2, "another_target:", "Another naming violation"),
            GovernanceViolation(phony_rule, 3, "clean:", "PHONY violation")
        ]
        
        recommendations = engine._generate_recommendations(violations, 0.3)
        
        assert len(recommendations) > 0
        assert any("kebab-case" in rec for rec in recommendations)
        assert any("PHONY" in rec for rec in recommendations)
    
    def test_kebab_case_suggestion(self, engine):
        """Test kebab-case name suggestions."""
        assert engine._suggest_kebab_case("test_target") == "test-target"
        assert engine._suggest_kebab_case("TestTarget") == "testtarget"
        assert engine._suggest_kebab_case("BUILD_ALL") == "build-all"
        assert engine._suggest_kebab_case("clean__up") == "clean-up"
        assert engine._suggest_kebab_case("test target") == "test-target"
        assert engine._suggest_kebab_case("valid-name") == "valid-name"
    
    def test_should_be_phony_detection(self, engine):
        """Test detection of targets that should be PHONY."""
        assert engine._should_be_phony("help") is True
        assert engine._should_be_phony("clean") is True
        assert engine._should_be_phony("test") is True
        assert engine._should_be_phony("install") is True
        assert engine._should_be_phony("build-docker") is True
        assert engine._should_be_phony("run-tests") is True
        
        # These should not be PHONY
        assert engine._should_be_phony("main.o") is False
        assert engine._should_be_phony("program") is False
        assert engine._should_be_phony("lib.a") is False
    
    def test_rule_management(self, engine):
        """Test governance rule management."""
        initial_rules = engine.get_governance_rules()
        initial_count = len(initial_rules)
        
        # Test enabling/disabling rules
        rule_name = initial_rules[0].name
        assert engine.disable_rule(rule_name) is True
        assert not engine.get_governance_rules()[0].enabled
        
        assert engine.enable_rule(rule_name) is True
        assert engine.get_governance_rules()[0].enabled
        
        # Test non-existent rule
        assert engine.disable_rule("nonexistent_rule") is False
        assert engine.enable_rule("nonexistent_rule") is False
        
        # Test adding custom rule
        custom_rule = GovernanceRule(
            rule_type=GovernanceRuleType.NAMING_CONVENTION,
            name="custom_rule",
            description="Custom test rule",
            severity=ViolationSeverity.INFO
        )
        
        engine.add_custom_rule(custom_rule)
        updated_rules = engine.get_governance_rules()
        assert len(updated_rules) == initial_count + 1
        assert any(rule.name == "custom_rule" for rule in updated_rules)
    
    def test_statistics_tracking(self, engine, temp_dir):
        """Test that governance statistics are properly tracked."""
        makefile_content = """# Test makefile
help:
\t@echo "help"
"""
        makefile_path = temp_dir / "Makefile"
        makefile_path.write_text(makefile_content)
        
        initial_validation_count = engine._validation_count
        initial_violation_count = engine._violation_count
        
        # Perform validation
        result = engine.validate_governance(makefile_path)
        
        # Check statistics were updated
        assert engine._validation_count == initial_validation_count + 1
        assert engine._violation_count >= initial_violation_count
        
        # Check compliance rate calculation
        if engine._validation_count > 0:
            expected_rate = 1.0 - (engine._violation_count / engine._validation_count)
            assert abs(engine._compliance_rate - expected_rate) < 0.01
    
    def test_trace_operation_integration(self, engine, temp_dir):
        """Test that operations are properly traced."""
        makefile_content = "help:\n\t@echo 'help'"
        makefile_path = temp_dir / "Makefile"
        makefile_path.write_text(makefile_content)
        
        # Mock the trace_operation context manager
        with patch.object(engine, 'trace_operation') as mock_trace:
            mock_context = MagicMock()
            mock_trace.return_value.__enter__ = Mock(return_value=mock_context)
            mock_trace.return_value.__exit__ = Mock(return_value=None)
            
            result = engine.validate_governance(makefile_path)
            
            # Verify trace_operation was called
            mock_trace.assert_called_once_with("validate_governance", file_path=str(makefile_path))
            
            # Verify output_result was set
            assert mock_context.output_result is not None
    
    def test_comprehensive_governance_validation(self, engine, temp_dir):
        """Test comprehensive governance validation with multiple violation types."""
        makefile_content = """# Comprehensive test makefile
INVALID_var := value
VALID_VAR := value

help: ## Show help (compliant)
\t@echo "Available targets:"

build_project:
\t@echo "Building project..."
\t@mkdir -p build/
\t@cp src/* build/
\t@cd build && make all
\t@echo "Build complete"

TestTarget:
\t@echo "Testing..."

clean:
\t@echo "Cleaning..."

# Missing PHONY declarations for build_project, TestTarget, clean
.PHONY: help
"""
        
        makefile_path = temp_dir / "Makefile"
        makefile_path.write_text(makefile_content)
        
        result = engine.validate_governance(makefile_path)
        
        # Should have multiple types of violations
        violation_types = set(v.rule.rule_type for v in result.violations)
        assert GovernanceRuleType.NAMING_CONVENTION in violation_types
        assert GovernanceRuleType.PHONY_DECLARATION in violation_types
        assert GovernanceRuleType.COMPLEXITY_LIMIT in violation_types
        assert GovernanceRuleType.TARGET_DESCRIPTION in violation_types
        
        # Should not be compliant due to multiple violations
        assert result.is_compliant is False
        
        # Should have recommendations
        assert len(result.recommendations) > 0
        
        # Quality score should be lower due to violations
        assert result.quality_score < 1.0
    
    @pytest.mark.parametrize("target_name,expected_kebab", [
        ("test_target", "test-target"),
        ("TestTarget", "testtarget"),
        ("BUILD_ALL", "build-all"),
        ("clean__up", "clean-up"),
        ("test target", "test-target"),
        ("valid-name", "valid-name"),
        ("UPPER_CASE_NAME", "upper-case-name"),
        ("mixed_Case-Name", "mixed-case-name"),
    ])
    def test_kebab_case_suggestions_parametrized(self, engine, target_name, expected_kebab):
        """Parametrized test for kebab-case suggestions."""
        assert engine._suggest_kebab_case(target_name) == expected_kebab
    
    @pytest.mark.parametrize("target_name,should_be_phony", [
        ("help", True),
        ("clean", True),
        ("test", True),
        ("install", True),
        ("deploy", True),
        ("build", True),
        ("run", True),
        ("start", True),
        ("stop", True),
        ("check", True),
        ("lint", True),
        ("format", True),
        ("validate", True),
        ("setup", True),
        ("init", True),
        ("main.o", False),
        ("program", False),
        ("lib.a", False),
        ("config.json", False),
        ("data.txt", False),
    ])
    def test_phony_detection_parametrized(self, engine, target_name, should_be_phony):
        """Parametrized test for PHONY target detection."""
        assert engine._should_be_phony(target_name) == should_be_phony