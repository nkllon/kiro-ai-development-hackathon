"""
Unit tests for PDCA data models

Tests core data structures, validation, and utility functions
for systematic PDCA orchestration.
"""

import pytest
from datetime import datetime, timedelta
from src.beast_mode.core.pdca_models import (
    PDCATask, PDCAResult, PlanResult, DoResult, CheckResult, ActResult,
    ModelIntelligence, Requirement, Constraint, Criterion, Pattern, Tool,
    PDCAPhase, TaskStatus, ValidationLevel, ReflectiveModule,
    create_basic_task, calculate_systematic_score, validate_pdca_result
)


class TestPDCATask:
    """Test PDCATask data model"""
    
    def test_create_valid_task(self):
        """Test creating a valid PDCA task"""
        task = PDCATask(
            task_id="test-001",
            description="Test systematic implementation",
            domain="testing",
            requirements=[],
            constraints=[],
            success_criteria=[],
            estimated_complexity=5
        )
        
        assert task.task_id == "test-001"
        assert task.description == "Test systematic implementation"
        assert task.domain == "testing"
        assert task.status == TaskStatus.PENDING
        assert isinstance(task.created_at, datetime)
    
    def test_task_validation_errors(self):
        """Test task validation for required fields"""
        with pytest.raises(ValueError, match="task_id is required"):
            PDCATask(
                task_id="",
                description="Test",
                domain="testing",
                requirements=[],
                constraints=[],
                success_criteria=[],
                estimated_complexity=5
            )
        
        with pytest.raises(ValueError, match="description is required"):
            PDCATask(
                task_id="test-001",
                description="",
                domain="testing",
                requirements=[],
                constraints=[],
                success_criteria=[],
                estimated_complexity=5
            )
    
    def test_create_basic_task_utility(self):
        """Test create_basic_task utility function"""
        task = create_basic_task("basic-001", "Basic test task", "testing")
        
        assert task.task_id == "basic-001"
        assert task.description == "Basic test task"
        assert task.domain == "testing"
        assert task.estimated_complexity == 5
        assert len(task.requirements) == 0
        assert len(task.constraints) == 0
        assert len(task.success_criteria) == 0


class TestPDCAResult:
    """Test PDCAResult and phase results"""
    
    def setup_method(self):
        """Set up test data"""
        self.plan_result = PlanResult(
            task_id="test-001",
            systematic_approach="Model-driven systematic approach",
            implementation_steps=["Step 1", "Step 2"],
            resource_requirements=["Python 3.9+", "pytest"],
            risk_assessment={"low": "Well-defined requirements"},
            model_intelligence_used=["domain_patterns", "tool_mappings"],
            confidence_score=0.85,
            estimated_duration=timedelta(hours=4)
        )
        
        self.do_result = DoResult(
            task_id="test-001",
            implementation_artifacts=["src/module.py", "tests/test_module.py"],
            systematic_compliance=0.90,
            execution_metrics={"lines_of_code": 150, "test_coverage": 95.0},
            tools_used=["pytest", "black", "mypy"],
            deviations_from_plan=[],
            actual_duration=timedelta(hours=3, minutes=45)
        )
        
        self.check_result = CheckResult(
            task_id="test-001",
            validation_results={"requirements_met": True, "tests_pass": True},
            systematic_score=0.88,
            rca_findings=[],
            quality_metrics={"code_quality": 9.2, "maintainability": 8.8},
            validation_level=ValidationLevel.HIGH
        )
        
        self.act_result = ActResult(
            task_id="test-001",
            learning_patterns=[],
            model_registry_updates=["Updated testing domain patterns"],
            improvement_recommendations=["Consider automated code generation"],
            success_rate_improvement=0.15,
            knowledge_artifacts=["testing_best_practices.md"]
        )
    
    def test_create_complete_pdca_result(self):
        """Test creating complete PDCA result"""
        result = PDCAResult(
            task_id="test-001",
            plan_result=self.plan_result,
            do_result=self.do_result,
            check_result=self.check_result,
            act_result=self.act_result,
            cycle_duration=timedelta(hours=4),
            systematic_score=0.88,
            success_rate=0.95,
            improvement_factor=1.25
        )
        
        assert result.task_id == "test-001"
        assert result.systematic_score == 0.88
        assert result.success_rate == 0.95
        assert result.improvement_factor == 1.25
        assert isinstance(result.created_at, datetime)
    
    def test_get_phase_result(self):
        """Test getting results by PDCA phase"""
        result = PDCAResult(
            task_id="test-001",
            plan_result=self.plan_result,
            do_result=self.do_result,
            check_result=self.check_result,
            act_result=self.act_result,
            cycle_duration=timedelta(hours=4),
            systematic_score=0.88,
            success_rate=0.95,
            improvement_factor=1.25
        )
        
        assert result.get_phase_result(PDCAPhase.PLAN) == self.plan_result
        assert result.get_phase_result(PDCAPhase.DO) == self.do_result
        assert result.get_phase_result(PDCAPhase.CHECK) == self.check_result
        assert result.get_phase_result(PDCAPhase.ACT) == self.act_result


class TestModelIntelligence:
    """Test ModelIntelligence data model"""
    
    def test_create_model_intelligence(self):
        """Test creating model intelligence"""
        tool = Tool(
            tool_id="pytest-001",
            name="pytest",
            domain="testing",
            purpose="unit testing framework",
            command_template="pytest {test_path}",
            validation_method="exit_code"
        )
        
        intelligence = ModelIntelligence(
            domain="testing",
            requirements=[],
            patterns=[],
            tools={"pytest": tool},
            success_metrics={"test_coverage": 95.0, "success_rate": 0.92},
            confidence_score=0.85
        )
        
        assert intelligence.domain == "testing"
        assert intelligence.confidence_score == 0.85
        assert "pytest" in intelligence.tools
        assert intelligence.success_metrics["test_coverage"] == 95.0
    
    def test_get_tool_by_purpose(self):
        """Test finding tool by purpose"""
        tool1 = Tool(
            tool_id="pytest-001",
            name="pytest",
            domain="testing",
            purpose="unit testing framework",
            command_template="pytest {test_path}",
            validation_method="exit_code"
        )
        
        tool2 = Tool(
            tool_id="black-001",
            name="black",
            domain="testing",
            purpose="code formatting tool",
            command_template="black {file_path}",
            validation_method="exit_code"
        )
        
        intelligence = ModelIntelligence(
            domain="testing",
            requirements=[],
            patterns=[],
            tools={"pytest": tool1, "black": tool2},
            success_metrics={},
            confidence_score=0.85
        )
        
        # Test exact match
        found_tool = intelligence.get_tool_by_purpose("unit testing framework")
        assert found_tool == tool1
        
        # Test partial match
        found_tool = intelligence.get_tool_by_purpose("testing")
        assert found_tool == tool1  # First match
        
        # Test no match
        found_tool = intelligence.get_tool_by_purpose("database")
        assert found_tool is None


class TestUtilityFunctions:
    """Test utility functions"""
    
    def test_calculate_systematic_score(self):
        """Test systematic score calculation"""
        score = calculate_systematic_score(0.9, 0.8, 0.85, 0.75)
        
        # Expected: 0.9*0.25 + 0.8*0.35 + 0.85*0.25 + 0.75*0.15 = 0.825
        expected = 0.9 * 0.25 + 0.8 * 0.35 + 0.85 * 0.25 + 0.75 * 0.15
        assert abs(score - expected) < 0.001
    
    def test_validate_pdca_result_valid(self):
        """Test validation of valid PDCA result"""
        result = PDCAResult(
            task_id="test-001",
            plan_result=PlanResult(
                task_id="test-001",
                systematic_approach="Test",
                implementation_steps=[],
                resource_requirements=[],
                risk_assessment={},
                model_intelligence_used=[],
                confidence_score=0.8,
                estimated_duration=timedelta(hours=1)
            ),
            do_result=DoResult(
                task_id="test-001",
                implementation_artifacts=[],
                systematic_compliance=0.9,
                execution_metrics={},
                tools_used=[],
                deviations_from_plan=[],
                actual_duration=timedelta(hours=1)
            ),
            check_result=CheckResult(
                task_id="test-001",
                validation_results={},
                systematic_score=0.85,
                rca_findings=[],
                quality_metrics={},
                validation_level=ValidationLevel.HIGH
            ),
            act_result=ActResult(
                task_id="test-001",
                learning_patterns=[],
                model_registry_updates=[],
                improvement_recommendations=[],
                success_rate_improvement=0.1,
                knowledge_artifacts=[]
            ),
            cycle_duration=timedelta(hours=1),
            systematic_score=0.85,
            success_rate=0.95,
            improvement_factor=1.2
        )
        
        issues = validate_pdca_result(result)
        assert len(issues) == 0
    
    def test_validate_pdca_result_invalid(self):
        """Test validation of invalid PDCA result"""
        result = PDCAResult(
            task_id="",  # Invalid: empty task_id
            plan_result=PlanResult(
                task_id="test-001",
                systematic_approach="Test",
                implementation_steps=[],
                resource_requirements=[],
                risk_assessment={},
                model_intelligence_used=[],
                confidence_score=0.8,
                estimated_duration=timedelta(hours=1)
            ),
            do_result=DoResult(
                task_id="test-001",
                implementation_artifacts=[],
                systematic_compliance=0.9,
                execution_metrics={},
                tools_used=[],
                deviations_from_plan=[],
                actual_duration=timedelta(hours=1)
            ),
            check_result=CheckResult(
                task_id="test-001",
                validation_results={},
                systematic_score=0.85,
                rca_findings=[],
                quality_metrics={},
                validation_level=ValidationLevel.HIGH
            ),
            act_result=ActResult(
                task_id="test-001",
                learning_patterns=[],
                model_registry_updates=[],
                improvement_recommendations=[],
                success_rate_improvement=0.1,
                knowledge_artifacts=[]
            ),
            cycle_duration=timedelta(seconds=-1),  # Invalid: negative duration
            systematic_score=1.5,  # Invalid: > 1.0
            success_rate=-0.1,     # Invalid: < 0.0
            improvement_factor=1.2
        )
        
        issues = validate_pdca_result(result)
        assert len(issues) == 4  # task_id, cycle_duration, systematic_score, success_rate


class MockReflectiveModule(ReflectiveModule):
    """Mock implementation for testing ReflectiveModule interface"""
    
    def get_health_status(self) -> dict:
        return {"status": "healthy", "uptime": "1h"}
    
    def get_performance_metrics(self) -> dict:
        return {"response_time": 0.1, "throughput": 100.0}
    
    def validate_systematic_compliance(self) -> ValidationLevel:
        return ValidationLevel.HIGH


class TestReflectiveModule:
    """Test ReflectiveModule interface"""
    
    def test_reflective_module_interface(self):
        """Test ReflectiveModule implementation"""
        module = MockReflectiveModule()
        
        health = module.get_health_status()
        assert health["status"] == "healthy"
        
        metrics = module.get_performance_metrics()
        assert metrics["response_time"] == 0.1
        
        compliance = module.validate_systematic_compliance()
        assert compliance == ValidationLevel.HIGH
        
        info = module.get_module_info()
        assert info["module_name"] == "MockReflectiveModule"
        assert info["module_type"] == "ReflectiveModule"
        assert info["systematic_approach"] == "PDCA-driven"