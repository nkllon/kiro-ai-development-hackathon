"""
Tests for Beast Mode Integration Components
Tests UC-25: Self-Consistency Validation and Infrastructure Integration
"""

import pytest
import json
import tempfile
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path
from datetime import datetime

from src.beast_mode.integration.infrastructure_integration_manager import (
    InfrastructureIntegrationManager,
    IntegrationStatus,
    ValidationResult,
    IntegrationConfig
)

from src.beast_mode.integration.self_consistency_validator import (
    SelfConsistencyValidator,
    ConsistencyCheck,
    ConsistencyResult,
    SelfConsistencyReport
)

class TestInfrastructureIntegrationManager:
    """Test infrastructure integration functionality"""
    
    @pytest.fixture
    def temp_project_root(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            project_root = Path(temp_dir)
            
            # Create basic project structure
            (project_root / "src" / "beast_mode" / "core").mkdir(parents=True)
            (project_root / ".cursor" / "rules").mkdir(parents=True)
            (project_root / ".kiro" / "specs" / "beast-mode-framework").mkdir(parents=True)
            (project_root / "makefiles").mkdir(parents=True)
            
            yield project_root
            
    @pytest.fixture
    def integration_manager(self, temp_project_root):
        return InfrastructureIntegrationManager(str(temp_project_root))
        
    @pytest.fixture
    def sample_makefile_content(self):
        return """
# Sample Makefile with Beast Mode integration
include makefiles/beast-mode.mk

help: ## Show help
	@echo "Help message"

beast-mode: ## Beast Mode operations
	@echo "Beast Mode active"

pdca-cycle: ## PDCA cycle
	@echo "PDCA cycle"

beast-mode-health: ## Health check
	@echo "Health check"

beast-mode-validate: ## Validation
	@echo "Validation"
"""
        
    @pytest.fixture
    def sample_registry_content(self):
        return {
            "description": "Test project registry",
            "project_purpose": {
                "primary_goal": "Test Beast Mode integration"
            },
            "domain_architecture": {
                "overview": {
                    "total_domains": 100,
                    "compliance_standard": "Reflective Module (RM)"
                },
                "demo_core": {
                    "description": "Core demo functionality"
                },
                "demo_tools": {
                    "description": "Demo tools"
                },
                "security_first": {
                    "description": "Security-first development"
                },
                "quality_assurance": {
                    "description": "Quality assurance"
                }
            }
        }
        
    def test_integration_manager_initialization(self, integration_manager):
        """Test integration manager initialization"""
        assert integration_manager.module_name == "infrastructure_integration_manager"
        assert integration_manager.is_healthy()
        
        status = integration_manager.get_module_status()
        assert "module_name" in status
        assert "status" in status
        assert "project_root" in status
        
    def test_makefile_integration_validation(self, integration_manager, temp_project_root, sample_makefile_content):
        """Test Makefile integration validation"""
        # Create Makefile with Beast Mode integration
        makefile_path = temp_project_root / "Makefile"
        makefile_path.write_text(sample_makefile_content)
        
        # Create beast-mode.mk
        beast_mode_mk = temp_project_root / "makefiles" / "beast-mode.mk"
        beast_mode_mk.write_text("# Beast Mode Makefile")
        
        result = integration_manager._validate_makefile_integration()
        
        assert isinstance(result, ValidationResult)
        assert result.component == "makefile"
        assert result.status in [IntegrationStatus.INTEGRATED, IntegrationStatus.PARTIAL]
        
    def test_project_registry_validation(self, integration_manager, temp_project_root, sample_registry_content):
        """Test project registry integration validation"""
        # Create project registry
        registry_path = temp_project_root / "project_model_registry.json"
        registry_path.write_text(json.dumps(sample_registry_content, indent=2))
        
        result = integration_manager._validate_project_registry_integration()
        
        assert isinstance(result, ValidationResult)
        assert result.component == "project_registry"
        assert result.status in [IntegrationStatus.INTEGRATED, IntegrationStatus.PARTIAL]
        
    def test_cursor_rules_validation(self, integration_manager, temp_project_root):
        """Test cursor rules integration validation"""
        # Create Beast Mode cursor rules
        rules_dir = temp_project_root / ".cursor" / "rules"
        (rules_dir / "beast-mode-integration.mdc").write_text("# Beast Mode Integration Rules")
        (rules_dir / "beast.mdc").write_text("# Beast Mode Rules")
        
        result = integration_manager._validate_cursor_rules_integration()
        
        assert isinstance(result, ValidationResult)
        assert result.component == "cursor_rules"
        assert result.status in [IntegrationStatus.INTEGRATED, IntegrationStatus.PARTIAL]
        
    def test_beast_mode_configuration_validation(self, integration_manager, temp_project_root):
        """Test Beast Mode configuration validation"""
        # Create Beast Mode configuration files
        config_dir = temp_project_root / ".kiro" / "specs" / "beast-mode-framework"
        (config_dir / "requirements.md").write_text("# Requirements")
        (config_dir / "design.md").write_text("# Design")
        (config_dir / "tasks.md").write_text("# Tasks")
        
        # Create Beast Mode source structure
        src_dir = temp_project_root / "src" / "beast_mode"
        (src_dir / "core" / "reflective_module.py").write_text("# Reflective Module")
        (src_dir / "orchestration" / "tool_orchestration_engine.py").write_text("# Tool Orchestration")
        (src_dir / "integration" / "infrastructure_integration_manager.py").write_text("# Integration Manager")
        
        result = integration_manager._validate_beast_mode_configuration()
        
        assert isinstance(result, ValidationResult)
        assert result.component == "beast_mode_config"
        assert result.status in [IntegrationStatus.INTEGRATED, IntegrationStatus.PARTIAL]
        
    def test_complete_integration_validation(self, integration_manager, temp_project_root, sample_makefile_content, sample_registry_content):
        """Test complete integration validation"""
        # Set up complete project structure
        makefile_path = temp_project_root / "Makefile"
        makefile_path.write_text(sample_makefile_content)
        
        registry_path = temp_project_root / "project_model_registry.json"
        registry_path.write_text(json.dumps(sample_registry_content, indent=2))
        
        rules_dir = temp_project_root / ".cursor" / "rules"
        (rules_dir / "beast-mode-integration.mdc").write_text("# Beast Mode Integration")
        
        config_dir = temp_project_root / ".kiro" / "specs" / "beast-mode-framework"
        (config_dir / "requirements.md").write_text("# Requirements")
        
        # Mock subprocess for Makefile execution
        with patch('subprocess.run') as mock_subprocess:
            mock_subprocess.return_value = Mock(returncode=0, stdout="Help", stderr="")
            
            validation_result = integration_manager.validate_complete_integration()
            
            assert "validation_id" in validation_result
            assert "overall_health_score" in validation_result
            assert "component_results" in validation_result
            assert len(validation_result["component_results"]) == 4  # All 4 components
            
    def test_integration_health_calculation(self, integration_manager):
        """Test integration health score calculation"""
        validation_results = [
            ValidationResult("component1", IntegrationStatus.INTEGRATED, "Good", []),
            ValidationResult("component2", IntegrationStatus.PARTIAL, "Partial", []),
            ValidationResult("component3", IntegrationStatus.FAILED, "Failed", [])
        ]
        
        health_score = integration_manager._calculate_integration_health(validation_results)
        
        # Should be average of 1.0, 0.6, 0.0 = 0.533...
        assert 0.5 <= health_score <= 0.6
        
    def test_integration_analytics(self, integration_manager):
        """Test integration analytics functionality"""
        analytics = integration_manager.get_integration_analytics()
        
        assert "integration_metrics" in analytics
        assert "component_status" in analytics
        assert "validation_history" in analytics
        assert "health_trends" in analytics

class TestSelfConsistencyValidator:
    """Test self-consistency validation functionality"""
    
    @pytest.fixture
    def temp_project_root(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            project_root = Path(temp_dir)
            
            # Create Beast Mode project structure
            (project_root / "src" / "beast_mode" / "core").mkdir(parents=True)
            (project_root / "src" / "beast_mode" / "orchestration").mkdir(parents=True)
            (project_root / "src" / "beast_mode" / "integration").mkdir(parents=True)
            (project_root / "src" / "beast_mode" / "quality").mkdir(parents=True)
            (project_root / "src" / "beast_mode" / "observability").mkdir(parents=True)
            (project_root / "tests").mkdir(parents=True)
            (project_root / ".kiro" / "specs").mkdir(parents=True)
            
            yield project_root
            
    @pytest.fixture
    def consistency_validator(self, temp_project_root):
        return SelfConsistencyValidator(str(temp_project_root))
        
    @pytest.fixture
    def sample_project_registry(self, temp_project_root):
        registry_content = {
            "domain_architecture": {
                "overview": {
                    "total_domains": 100,
                    "compliance_standard": "Reflective Module (RM)"
                }
            }
        }
        
        registry_path = temp_project_root / "project_model_registry.json"
        registry_path.write_text(json.dumps(registry_content))
        return registry_path
        
    def test_consistency_validator_initialization(self, consistency_validator):
        """Test consistency validator initialization"""
        assert consistency_validator.module_name == "self_consistency_validator"
        assert consistency_validator.is_healthy()
        
        status = consistency_validator.get_module_status()
        assert "module_name" in status
        assert "total_validations" in status
        assert "credibility_success_rate" in status
        
    def test_model_driven_decisions_validation(self, consistency_validator, sample_project_registry):
        """Test model-driven decisions consistency check"""
        # Create intelligence engine
        intelligence_path = consistency_validator.project_root / "src" / "beast_mode" / "intelligence"
        intelligence_path.mkdir(parents=True)
        (intelligence_path / "__init__.py").write_text("")
        
        result = consistency_validator._validate_model_driven_decisions()
        
        assert isinstance(result, ConsistencyResult)
        assert result.check_type == ConsistencyCheck.MODEL_DRIVEN_DECISIONS
        assert result.score > 0.0
        assert len(result.evidence) > 0
        
    def test_systematic_tool_repair_validation(self, consistency_validator):
        """Test systematic tool repair consistency check"""
        # Create tool orchestration engine
        orchestration_path = consistency_validator.project_root / "src" / "beast_mode" / "orchestration"
        (orchestration_path / "tool_orchestration_engine.py").write_text("# Tool Orchestration")
        
        # Create RCA engine
        analysis_path = consistency_validator.project_root / "src" / "beast_mode" / "analysis"
        analysis_path.mkdir(parents=True)
        (analysis_path / "rca_engine.py").write_text("# RCA Engine")
        
        # Mock successful Makefile execution
        with patch('subprocess.run') as mock_subprocess:
            mock_subprocess.return_value = Mock(returncode=0, stdout="Help", stderr="")
            
            result = consistency_validator._validate_systematic_tool_repair()
            
            assert isinstance(result, ConsistencyResult)
            assert result.check_type == ConsistencyCheck.SYSTEMATIC_TOOL_REPAIR
            assert result.score > 0.0
            
    def test_pdca_methodology_validation(self, consistency_validator):
        """Test PDCA methodology consistency check"""
        # Create Makefile with PDCA targets
        makefile_content = """
pdca-cycle: ## PDCA cycle
	@echo "PDCA cycle"

pdca-plan: ## PDCA plan
	@echo "Plan"

pdca-do: ## PDCA do
	@echo "Do"

pdca-check: ## PDCA check
	@echo "Check"

pdca-act: ## PDCA act
	@echo "Act"
"""
        
        makefile_path = consistency_validator.project_root / "Makefile"
        makefile_path.write_text(makefile_content)
        
        result = consistency_validator._validate_pdca_methodology()
        
        assert isinstance(result, ConsistencyResult)
        assert result.check_type == ConsistencyCheck.PDCA_METHODOLOGY
        assert result.score > 0.0
        
    def test_rm_compliance_validation(self, consistency_validator):
        """Test RM compliance consistency check"""
        # Create ReflectiveModule base class
        rm_path = consistency_validator.project_root / "src" / "beast_mode" / "core" / "reflective_module.py"
        rm_content = """
class ReflectiveModule:
    def get_module_status(self):
        pass
    
    def is_healthy(self):
        pass
"""
        rm_path.write_text(rm_content)
        
        # Create RM compliant component
        component_path = consistency_validator.project_root / "src" / "beast_mode" / "test_component.py"
        component_content = """
from .core.reflective_module import ReflectiveModule

class TestComponent(ReflectiveModule):
    def get_module_status(self):
        return {"status": "healthy"}
"""
        component_path.write_text(component_content)
        
        result = consistency_validator._validate_rm_compliance()
        
        assert isinstance(result, ConsistencyResult)
        assert result.check_type == ConsistencyCheck.RM_COMPLIANCE
        assert result.score > 0.0
        
    def test_quality_gates_validation(self, consistency_validator):
        """Test quality gates consistency check"""
        # Create quality gates module
        quality_path = consistency_validator.project_root / "src" / "beast_mode" / "quality"
        (quality_path / "code_quality_gates.py").write_text("# Quality Gates")
        
        # Create test files
        tests_path = consistency_validator.project_root / "tests"
        (tests_path / "test_example.py").write_text("# Test file")
        
        # Create quality configuration
        (consistency_validator.project_root / "pyproject.toml").write_text("[tool.pytest]")
        
        result = consistency_validator._validate_quality_gates()
        
        assert isinstance(result, ConsistencyResult)
        assert result.check_type == ConsistencyCheck.QUALITY_GATES
        assert result.score > 0.0
        
    def test_health_monitoring_validation(self, consistency_validator):
        """Test health monitoring consistency check"""
        # Create observability module
        observability_path = consistency_validator.project_root / "src" / "beast_mode" / "observability"
        (observability_path / "enhanced_observability_manager.py").write_text("# Observability")
        
        # Create Makefile with health targets
        makefile_content = """
beast-mode-health: ## Health check
	@echo "Health check"

beast-mode-status: ## Status check
	@echo "Status"
"""
        
        makefile_path = consistency_validator.project_root / "Makefile"
        makefile_path.write_text(makefile_content)
        
        result = consistency_validator._validate_health_monitoring()
        
        assert isinstance(result, ConsistencyResult)
        assert result.check_type == ConsistencyCheck.HEALTH_MONITORING
        assert result.score > 0.0
        
    def test_superiority_evidence_validation(self, consistency_validator):
        """Test superiority evidence consistency check"""
        # Create metrics module
        metrics_path = consistency_validator.project_root / "src" / "beast_mode" / "metrics"
        metrics_path.mkdir(parents=True)
        (metrics_path / "baseline_metrics_engine.py").write_text("# Metrics")
        
        # Create Makefile with superiority metrics target
        makefile_content = """
beast-mode-superiority-metrics: ## Superiority metrics
	@echo "Superiority metrics"
"""
        
        makefile_path = consistency_validator.project_root / "Makefile"
        makefile_path.write_text(makefile_content)
        
        result = consistency_validator._validate_superiority_evidence()
        
        assert isinstance(result, ConsistencyResult)
        assert result.check_type == ConsistencyCheck.SUPERIORITY_EVIDENCE
        assert result.score > 0.0
        
    def test_complete_self_consistency_validation(self, consistency_validator, sample_project_registry):
        """Test complete self-consistency validation"""
        # Set up minimal project structure for validation
        self._setup_minimal_beast_mode_structure(consistency_validator.project_root)
        
        # Mock subprocess for Makefile execution
        with patch('subprocess.run') as mock_subprocess:
            mock_subprocess.return_value = Mock(returncode=0, stdout="Help", stderr="")
            
            report = consistency_validator.validate_complete_self_consistency()
            
            assert isinstance(report, SelfConsistencyReport)
            assert report.overall_consistency_score >= 0.0
            assert len(report.check_results) == 7  # All consistency checks
            assert "superiority_evidence" in report.__dict__
            assert "self_application_proof" in report.__dict__
            
    def test_superiority_evidence_generation(self, consistency_validator):
        """Test superiority evidence generation"""
        # Create sample check results
        check_results = [
            ConsistencyResult(
                ConsistencyCheck.MODEL_DRIVEN_DECISIONS,
                True, 0.9, ["Model registry available"], [], []
            ),
            ConsistencyResult(
                ConsistencyCheck.SYSTEMATIC_TOOL_REPAIR,
                True, 0.8, ["Makefile works correctly"], [], []
            )
        ]
        
        evidence = consistency_validator._generate_superiority_evidence(check_results)
        
        assert "systematic_vs_adhoc_comparison" in evidence
        assert "measurable_improvements" in evidence
        assert "concrete_metrics" in evidence
        assert "credibility_proof" in evidence
        
    def test_self_application_proof_generation(self, consistency_validator):
        """Test self-application proof generation"""
        # Create sample check results
        check_results = [
            ConsistencyResult(
                ConsistencyCheck.MODEL_DRIVEN_DECISIONS,
                True, 0.9, ["Evidence"], [], []
            ),
            ConsistencyResult(
                ConsistencyCheck.PDCA_METHODOLOGY,
                True, 0.8, ["Evidence"], [], []
            )
        ]
        
        proof = consistency_validator._generate_self_application_proof(check_results)
        
        assert "methodology_application" in proof
        assert "self_consistency_validation" in proof
        assert "credibility_establishment" in proof
        assert "systematic_superiority" in proof
        
    def test_credibility_report_generation(self, consistency_validator, sample_project_registry):
        """Test credibility report generation"""
        # Set up minimal structure
        self._setup_minimal_beast_mode_structure(consistency_validator.project_root)
        
        # Mock subprocess
        with patch('subprocess.run') as mock_subprocess:
            mock_subprocess.return_value = Mock(returncode=0, stdout="Help", stderr="")
            
            credibility_report = consistency_validator.generate_credibility_report()
            
            assert "credibility_assessment" in credibility_report
            assert "consistency_report" in credibility_report
            assert "validation_analytics" in credibility_report
            assert "recommendations" in credibility_report
            
            assessment = credibility_report["credibility_assessment"]
            assert "credibility_established" in assessment
            assert "overall_consistency_score" in assessment
            assert "evidence_strength" in assessment
            
    def test_validation_analytics(self, consistency_validator):
        """Test validation analytics functionality"""
        analytics = consistency_validator.get_validation_analytics()
        
        assert "validation_metrics" in analytics
        assert "consistency_thresholds" in analytics
        assert "validation_history" in analytics
        assert "credibility_trends" in analytics
        assert "consistency_patterns" in analytics
        
    def _setup_minimal_beast_mode_structure(self, project_root):
        """Set up minimal Beast Mode structure for testing"""
        # Create core components
        (project_root / "src" / "beast_mode" / "core" / "reflective_module.py").write_text(
            "class ReflectiveModule: pass"
        )
        
        # Create orchestration
        (project_root / "src" / "beast_mode" / "orchestration" / "tool_orchestration_engine.py").write_text(
            "# Tool Orchestration"
        )
        
        # Create quality gates
        (project_root / "src" / "beast_mode" / "quality" / "code_quality_gates.py").write_text(
            "# Quality Gates"
        )
        
        # Create observability
        (project_root / "src" / "beast_mode" / "observability" / "enhanced_observability_manager.py").write_text(
            "# Observability"
        )
        
        # Create metrics
        metrics_path = project_root / "src" / "beast_mode" / "metrics"
        metrics_path.mkdir(parents=True)
        (metrics_path / "baseline_metrics_engine.py").write_text("# Metrics")
        
        # Create tests
        (project_root / "tests" / "test_example.py").write_text("# Test")
        
        # Create Makefile with all targets
        makefile_content = """
help: ## Help
	@echo "Help"

beast-mode: ## Beast Mode
	@echo "Beast Mode"

pdca-cycle: ## PDCA cycle
	@echo "PDCA"

pdca-plan: ## Plan
	@echo "Plan"

pdca-do: ## Do
	@echo "Do"

pdca-check: ## Check
	@echo "Check"

pdca-act: ## Act
	@echo "Act"

beast-mode-health: ## Health
	@echo "Health"

beast-mode-status: ## Status
	@echo "Status"

beast-mode-superiority-metrics: ## Metrics
	@echo "Metrics"
"""
        (project_root / "Makefile").write_text(makefile_content)

class TestIntegrationComponentsIntegration:
    """Test integration between infrastructure and consistency validation"""
    
    @pytest.fixture
    def temp_project_root(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            project_root = Path(temp_dir)
            
            # Create complete project structure
            (project_root / "src" / "beast_mode" / "core").mkdir(parents=True)
            (project_root / "src" / "beast_mode" / "integration").mkdir(parents=True)
            (project_root / ".cursor" / "rules").mkdir(parents=True)
            (project_root / ".kiro" / "specs" / "beast-mode-framework").mkdir(parents=True)
            
            yield project_root
            
    def test_integration_components_health(self, temp_project_root):
        """Test that both integration components report healthy status"""
        integration_manager = InfrastructureIntegrationManager(str(temp_project_root))
        consistency_validator = SelfConsistencyValidator(str(temp_project_root))
        
        # Both should be healthy initially
        assert integration_manager.is_healthy()
        assert consistency_validator.is_healthy()
        
    def test_integration_components_status_reporting(self, temp_project_root):
        """Test that both components provide proper status reporting"""
        components = [
            InfrastructureIntegrationManager(str(temp_project_root)),
            SelfConsistencyValidator(str(temp_project_root))
        ]
        
        for component in components:
            status = component.get_module_status()
            assert "module_name" in status
            assert "status" in status
            
            health_indicators = component.get_health_indicators()
            assert isinstance(health_indicators, dict)
            assert len(health_indicators) > 0
            
    def test_integration_workflow(self, temp_project_root):
        """Test complete integration workflow"""
        integration_manager = InfrastructureIntegrationManager(str(temp_project_root))
        consistency_validator = SelfConsistencyValidator(str(temp_project_root))
        
        # Set up basic project structure
        (temp_project_root / "Makefile").write_text("help:\n\t@echo 'Help'")
        (temp_project_root / "project_model_registry.json").write_text('{"domain_architecture": {"overview": {"total_domains": 50}}}')
        
        # Mock subprocess calls
        with patch('subprocess.run') as mock_subprocess:
            mock_subprocess.return_value = Mock(returncode=0, stdout="Help", stderr="")
            
            # Run infrastructure validation
            infra_result = integration_manager.validate_complete_integration()
            assert "validation_id" in infra_result
            
            # Run consistency validation
            consistency_result = consistency_validator.validate_complete_self_consistency()
            assert isinstance(consistency_result, SelfConsistencyReport)
            
            # Both should provide meaningful results
            assert infra_result["overall_health_score"] >= 0.0
            assert consistency_result.overall_consistency_score >= 0.0

if __name__ == "__main__":
    pytest.main([__file__])