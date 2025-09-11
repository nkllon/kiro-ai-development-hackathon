"""
Unit tests for Ghostbusters Framework core data models.

Tests validate data model behavior, validation logic, and
proper error handling for all core data structures.
"""

import pytest
from datetime import datetime, timedelta
from src.ghostbusters.core.models import (
    Finding, Recommendation, AnalysisContext, AnalysisResult,
    Delusion, RecoveryPlan, RecoveryAction, ValidationResult,
    ConsensusResult, MultiDimensionalResult, ValidationCertificate,
    CodeLocation, FindingType, Severity, DelusionCategory, RecoveryComplexity
)


class TestCodeLocation:
    """Test CodeLocation data model"""
    
    def test_code_location_creation(self):
        """Test basic code location creation"""
        location = CodeLocation(
            file_path="src/test.py",
            line_number=42,
            column_number=10
        )
        assert location.file_path == "src/test.py"
        assert location.line_number == 42
        assert location.column_number == 10
        assert str(location) == "src/test.py:42:10"
    
    def test_code_location_without_column(self):
        """Test code location without column number"""
        location = CodeLocation(
            file_path="src/test.py",
            line_number=42
        )
        assert str(location) == "src/test.py:42"
    
    def test_code_location_with_range(self):
        """Test code location with end line/column"""
        location = CodeLocation(
            file_path="src/test.py",
            line_number=42,
            column_number=10,
            end_line=45,
            end_column=20
        )
        assert location.end_line == 45
        assert location.end_column == 20


class TestFinding:
    """Test Finding data model"""
    
    def test_finding_creation(self):
        """Test basic finding creation"""
        location = CodeLocation("src/test.py", 42)
        finding = Finding(
            type=FindingType.SYNTAX_ERROR,
            severity=Severity.HIGH,
            location=location,
            description="Missing semicolon",
            confidence=0.95
        )
        
        assert finding.type == FindingType.SYNTAX_ERROR
        assert finding.severity == Severity.HIGH
        assert finding.location == location
        assert finding.description == "Missing semicolon"
        assert finding.confidence == 0.95
        assert finding.id is not None
        assert isinstance(finding.created_at, datetime)
    
    def test_finding_confidence_validation(self):
        """Test finding confidence validation"""
        with pytest.raises(ValueError, match="Confidence must be between 0.0 and 1.0"):
            Finding(confidence=1.5, description="Test")
        
        with pytest.raises(ValueError, match="Confidence must be between 0.0 and 1.0"):
            Finding(confidence=-0.1, description="Test")
    
    def test_finding_description_validation(self):
        """Test finding description validation"""
        with pytest.raises(ValueError, match="Finding description cannot be empty"):
            Finding(description="", confidence=0.8)
        
        with pytest.raises(ValueError, match="Finding description cannot be empty"):
            Finding(description="   ", confidence=0.8)


class TestRecommendation:
    """Test Recommendation data model"""
    
    def test_recommendation_creation(self):
        """Test basic recommendation creation"""
        rec = Recommendation(
            title="Fix syntax error",
            description="Add missing semicolon at end of line",
            priority=Severity.HIGH,
            effort_estimate="2 minutes",
            automated_fix_available=True,
            fix_command="add_semicolon"
        )
        
        assert rec.title == "Fix syntax error"
        assert rec.description == "Add missing semicolon at end of line"
        assert rec.priority == Severity.HIGH
        assert rec.effort_estimate == "2 minutes"
        assert rec.automated_fix_available is True
        assert rec.fix_command == "add_semicolon"
        assert rec.id is not None
    
    def test_recommendation_validation(self):
        """Test recommendation validation"""
        with pytest.raises(ValueError, match="Recommendation title cannot be empty"):
            Recommendation(title="", description="Test description")
        
        with pytest.raises(ValueError, match="Recommendation description cannot be empty"):
            Recommendation(title="Test title", description="")


class TestAnalysisContext:
    """Test AnalysisContext data model"""
    
    def test_analysis_context_creation(self):
        """Test basic analysis context creation"""
        context = AnalysisContext(
            target_path="src/test.py",
            analysis_type="syntax_check",
            configuration={"strict": True},
            metadata={"version": "1.0"}
        )
        
        assert context.target_path == "src/test.py"
        assert context.analysis_type == "syntax_check"
        assert context.configuration == {"strict": True}
        assert context.metadata == {"version": "1.0"}
        assert context.correlation_id is not None
        assert isinstance(context.timestamp, datetime)
    
    def test_analysis_context_validation(self):
        """Test analysis context validation"""
        with pytest.raises(ValueError, match="Target path cannot be empty"):
            AnalysisContext(target_path="", analysis_type="test")
        
        with pytest.raises(ValueError, match="Analysis type cannot be empty"):
            AnalysisContext(target_path="src/test.py", analysis_type="")


class TestAnalysisResult:
    """Test AnalysisResult data model"""
    
    def test_analysis_result_creation(self):
        """Test basic analysis result creation"""
        finding = Finding(
            type=FindingType.SYNTAX_ERROR,
            description="Test finding",
            confidence=0.9
        )
        
        result = AnalysisResult(
            agent_name="TestAgent",
            confidence=0.85,
            findings=[finding],
            analysis_duration=1.5
        )
        
        assert result.agent_name == "TestAgent"
        assert result.confidence == 0.85
        assert len(result.findings) == 1
        assert result.findings[0] == finding
        assert result.analysis_duration == 1.5
        assert result.id is not None
        assert isinstance(result.created_at, datetime)
    
    def test_analysis_result_validation(self):
        """Test analysis result validation"""
        with pytest.raises(ValueError, match="Confidence must be between 0.0 and 1.0"):
            AnalysisResult(agent_name="Test", confidence=1.5)
        
        with pytest.raises(ValueError, match="Agent name cannot be empty"):
            AnalysisResult(agent_name="", confidence=0.8)
        
        with pytest.raises(ValueError, match="Analysis duration cannot be negative"):
            AnalysisResult(agent_name="Test", confidence=0.8, analysis_duration=-1.0)
    
    def test_get_critical_findings(self):
        """Test getting critical findings"""
        critical_finding = Finding(
            severity=Severity.CRITICAL,
            description="Critical issue",
            confidence=0.9
        )
        normal_finding = Finding(
            severity=Severity.MEDIUM,
            description="Normal issue",
            confidence=0.8
        )
        
        result = AnalysisResult(
            agent_name="Test",
            confidence=0.8,
            findings=[critical_finding, normal_finding]
        )
        
        critical_findings = result.get_critical_findings()
        assert len(critical_findings) == 1
        assert critical_findings[0] == critical_finding
    
    def test_get_high_confidence_findings(self):
        """Test getting high confidence findings"""
        high_conf_finding = Finding(
            description="High confidence issue",
            confidence=0.95
        )
        low_conf_finding = Finding(
            description="Low confidence issue",
            confidence=0.6
        )
        
        result = AnalysisResult(
            agent_name="Test",
            confidence=0.8,
            findings=[high_conf_finding, low_conf_finding]
        )
        
        high_conf_findings = result.get_high_confidence_findings(threshold=0.8)
        assert len(high_conf_findings) == 1
        assert high_conf_findings[0] == high_conf_finding


class TestDelusion:
    """Test Delusion data model"""
    
    def test_delusion_creation(self):
        """Test basic delusion creation"""
        location = CodeLocation("src/test.py", 42)
        delusion = Delusion(
            category=DelusionCategory.SYNTAX,
            pattern="missing_semicolon",
            severity=Severity.HIGH,
            recovery_complexity=RecoveryComplexity.SIMPLE,
            location=location,
            description="Missing semicolon at end of statement",
            confidence=0.9
        )
        
        assert delusion.category == DelusionCategory.SYNTAX
        assert delusion.pattern == "missing_semicolon"
        assert delusion.severity == Severity.HIGH
        assert delusion.recovery_complexity == RecoveryComplexity.SIMPLE
        assert delusion.location == location
        assert delusion.description == "Missing semicolon at end of statement"
        assert delusion.confidence == 0.9
        assert delusion.id is not None
        assert isinstance(delusion.detected_at, datetime)
    
    def test_delusion_validation(self):
        """Test delusion validation"""
        with pytest.raises(ValueError, match="Confidence must be between 0.0 and 1.0"):
            Delusion(pattern="test", description="test", confidence=1.5)
        
        with pytest.raises(ValueError, match="Delusion pattern cannot be empty"):
            Delusion(pattern="", description="test", confidence=0.8)
        
        with pytest.raises(ValueError, match="Delusion description cannot be empty"):
            Delusion(pattern="test", description="", confidence=0.8)


class TestRecoveryPlan:
    """Test RecoveryPlan data model"""
    
    def test_recovery_plan_creation(self):
        """Test basic recovery plan creation"""
        action = RecoveryAction(
            action_type="replace",
            target="line:42",
            content="fixed_line;"
        )
        
        plan = RecoveryPlan(
            delusion_id="delusion-123",
            actions=[action],
            estimated_duration=2.0,
            risk_level=Severity.LOW
        )
        
        assert plan.delusion_id == "delusion-123"
        assert len(plan.actions) == 1
        assert plan.actions[0] == action
        assert plan.estimated_duration == 2.0
        assert plan.risk_level == Severity.LOW
        assert plan.id is not None
        assert isinstance(plan.created_at, datetime)
    
    def test_recovery_plan_validation(self):
        """Test recovery plan validation"""
        with pytest.raises(ValueError, match="Delusion ID cannot be empty"):
            RecoveryPlan(delusion_id="", actions=[RecoveryAction()])
        
        with pytest.raises(ValueError, match="Recovery plan must have at least one action"):
            RecoveryPlan(delusion_id="test", actions=[])
        
        with pytest.raises(ValueError, match="Estimated duration cannot be negative"):
            RecoveryPlan(
                delusion_id="test", 
                actions=[RecoveryAction()], 
                estimated_duration=-1.0
            )


class TestValidationResult:
    """Test ValidationResult data model"""
    
    def test_validation_result_creation(self):
        """Test basic validation result creation"""
        result = ValidationResult(
            validation_type="syntax_check",
            success=True,
            confidence=0.95,
            details={"lines_checked": 100},
            validation_duration=0.5
        )
        
        assert result.validation_type == "syntax_check"
        assert result.success is True
        assert result.confidence == 0.95
        assert result.details == {"lines_checked": 100}
        assert result.validation_duration == 0.5
        assert result.id is not None
        assert isinstance(result.created_at, datetime)
    
    def test_validation_result_validation(self):
        """Test validation result validation"""
        with pytest.raises(ValueError, match="Confidence must be between 0.0 and 1.0"):
            ValidationResult(validation_type="test", confidence=1.5)
        
        with pytest.raises(ValueError, match="Validation type cannot be empty"):
            ValidationResult(validation_type="", confidence=0.8)
        
        with pytest.raises(ValueError, match="Validation duration cannot be negative"):
            ValidationResult(
                validation_type="test", 
                confidence=0.8, 
                validation_duration=-1.0
            )


class TestConsensusResult:
    """Test ConsensusResult data model"""
    
    def test_consensus_result_creation(self):
        """Test basic consensus result creation"""
        unified_result = AnalysisResult(
            agent_name="Consensus",
            confidence=0.9
        )
        
        result = ConsensusResult(
            consensus_reached=True,
            confidence=0.9,
            unified_result=unified_result,
            participating_agents=["Agent1", "Agent2"],
            resolution_method="majority_vote",
            consensus_duration=1.0
        )
        
        assert result.consensus_reached is True
        assert result.confidence == 0.9
        assert result.unified_result == unified_result
        assert result.participating_agents == ["Agent1", "Agent2"]
        assert result.resolution_method == "majority_vote"
        assert result.consensus_duration == 1.0
        assert result.id is not None
        assert isinstance(result.created_at, datetime)
    
    def test_consensus_result_validation(self):
        """Test consensus result validation"""
        with pytest.raises(ValueError, match="Confidence must be between 0.0 and 1.0"):
            ConsensusResult(
                participating_agents=["Agent1"],
                confidence=1.5
            )
        
        unified_result = AnalysisResult(agent_name="Test", confidence=0.8)
        with pytest.raises(ValueError, match="Unified result required when consensus is reached"):
            ConsensusResult(
                consensus_reached=True,
                participating_agents=["Agent1"],
                unified_result=None,
                confidence=0.8
            )
        
        with pytest.raises(ValueError, match="At least one participating agent required"):
            ConsensusResult(
                participating_agents=[],
                confidence=0.8
            )
        
        with pytest.raises(ValueError, match="Consensus duration cannot be negative"):
            ConsensusResult(
                participating_agents=["Agent1"],
                confidence=0.8,
                consensus_duration=-1.0
            )


class TestMultiDimensionalResult:
    """Test MultiDimensionalResult data model"""
    
    def test_multi_dimensional_result_creation(self):
        """Test basic multi-dimensional result creation"""
        result = MultiDimensionalResult(
            functional_score=0.9,
            performance_score=0.8,
            security_score=0.95,
            integration_score=0.85,
            overall_confidence=0.87,
            test_duration=5.0
        )
        
        assert result.functional_score == 0.9
        assert result.performance_score == 0.8
        assert result.security_score == 0.95
        assert result.integration_score == 0.85
        assert result.overall_confidence == 0.87
        assert result.test_duration == 5.0
        assert result.id is not None
        assert isinstance(result.created_at, datetime)
    
    def test_multi_dimensional_result_validation(self):
        """Test multi-dimensional result validation"""
        with pytest.raises(ValueError, match="All scores must be between 0.0 and 1.0"):
            MultiDimensionalResult(functional_score=1.5)
        
        with pytest.raises(ValueError, match="Test duration cannot be negative"):
            MultiDimensionalResult(test_duration=-1.0)
    
    def test_get_failing_dimensions(self):
        """Test getting failing dimensions"""
        result = MultiDimensionalResult(
            functional_score=0.9,  # Pass
            performance_score=0.6,  # Fail
            security_score=0.5,     # Fail
            integration_score=0.8   # Pass
        )
        
        failing = result.get_failing_dimensions(threshold=0.7)
        assert set(failing) == {"performance", "security"}
    
    def test_is_production_ready(self):
        """Test production readiness check"""
        # Production ready
        result1 = MultiDimensionalResult(
            functional_score=0.9,
            performance_score=0.85,
            security_score=0.9,
            integration_score=0.8
        )
        assert result1.is_production_ready(threshold=0.8) is True
        
        # Not production ready
        result2 = MultiDimensionalResult(
            functional_score=0.9,
            performance_score=0.7,  # Below threshold
            security_score=0.9,
            integration_score=0.8
        )
        assert result2.is_production_ready(threshold=0.8) is False


class TestValidationCertificate:
    """Test ValidationCertificate data model"""
    
    def test_validation_certificate_creation(self):
        """Test basic validation certificate creation"""
        validation_result = ValidationResult(
            validation_type="comprehensive",
            success=True,
            confidence=0.9
        )
        
        cert = ValidationCertificate(
            target="src/project",
            validation_results=[validation_result],
            overall_confidence=0.9,
            certificate_level="production_ready",
            valid_until=datetime.utcnow() + timedelta(days=30)
        )
        
        assert cert.target == "src/project"
        assert len(cert.validation_results) == 1
        assert cert.validation_results[0] == validation_result
        assert cert.overall_confidence == 0.9
        assert cert.certificate_level == "production_ready"
        assert cert.valid_until is not None
        assert cert.issuer == "Ghostbusters Framework"
        assert cert.id is not None
        assert isinstance(cert.issued_at, datetime)
    
    def test_validation_certificate_validation(self):
        """Test validation certificate validation"""
        with pytest.raises(ValueError, match="Overall confidence must be between 0.0 and 1.0"):
            ValidationCertificate(
                target="test",
                validation_results=[ValidationResult(validation_type="test", confidence=0.8)],
                overall_confidence=1.5
            )
        
        with pytest.raises(ValueError, match="Certificate target cannot be empty"):
            ValidationCertificate(
                target="",
                validation_results=[ValidationResult(validation_type="test", confidence=0.8)],
                overall_confidence=0.8
            )
        
        with pytest.raises(ValueError, match="Certificate must have at least one validation result"):
            ValidationCertificate(
                target="test",
                validation_results=[],
                overall_confidence=0.8
            )