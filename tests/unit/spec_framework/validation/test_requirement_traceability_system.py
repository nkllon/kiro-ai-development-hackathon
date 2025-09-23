"""
Tests for Requirement Traceability System.

Validates systematic requirement traceability, impact analysis, and coverage reporting.
"""

import pytest
from datetime import datetime

from src.spec_framework.validation.requirement_traceability_system import (
    RequirementTraceabilitySystem,
    TraceabilityLink,
    TraceabilityLinkType,
    BusinessNeed,
    RequirementChange,
    ImpactAnalysisResult,
    CoverageReport,
    ImpactSeverity,
    ChangeType
)
from src.spec_framework.core.models import (
    Requirement, UserStory, AcceptanceCriterion, EARSStatement,
    TraceabilityMatrix, RequirementStatus, Priority
)


class TestRequirementTraceabilitySystem:
    """Test suite for Requirement Traceability System."""
    
    @pytest.fixture
    def traceability_system(self):
        """Create requirement traceability system instance."""
        return RequirementTraceabilitySystem()
    
    @pytest.fixture
    def sample_requirements(self):
        """Create sample requirements for testing."""
        req1 = Requirement(
            id="REQ-001",
            user_story=UserStory(
                role="developer",
                feature="run automated tests",
                benefit="ensure code quality"
            ),
            business_value="Improve software quality",
            priority=Priority.HIGH,
            status=RequirementStatus.DEFINED
        )
        
        req2 = Requirement(
            id="REQ-002",
            user_story=UserStory(
                role="developer",
                feature="view test results",
                benefit="understand test outcomes"
            ),
            business_value="Improve development efficiency",
            priority=Priority.MEDIUM,
            status=RequirementStatus.DEFINED
        )
        
        req3 = Requirement(
            id="REQ-003",
            user_story=UserStory(
                role="project manager",
                feature="view test reports",
                benefit="track project quality"
            ),
            business_value="Improve project visibility",
            priority=Priority.LOW,
            status=RequirementStatus.DRAFT
        )
        
        return [req1, req2, req3]
    
    def test_system_initialization(self, traceability_system):
        """Test traceability system initializes correctly."""
        assert traceability_system.ready()
        assert traceability_system.status() == "ready"
        
        health = traceability_system.health()
        assert health["status"] == "healthy"
        assert health["business_needs_count"] == 0
        assert health["traceability_links_count"] == 0
        
        metrics = traceability_system.metrics()
        assert metrics["business_needs_count"] == 0.0
        assert metrics["traceability_links_count"] == 0.0
    
    def test_add_business_need(self, traceability_system):
        """Test adding business needs."""
        business_need = traceability_system.add_business_need(
            need_id="BN-001",
            title="Improve Software Quality",
            description="Ensure high-quality software delivery",
            business_value="Reduce defects and improve customer satisfaction",
            stakeholders=["development team", "quality team"],
            priority="high"
        )
        
        assert business_need.id == "BN-001"
        assert business_need.title == "Improve Software Quality"
        assert business_need.priority == "high"
        assert len(business_need.stakeholders) == 2
        
        # Check system state
        health = traceability_system.health()
        assert health["business_needs_count"] == 1
    
    def test_link_requirement_to_business_need(self, traceability_system, sample_requirements):
        """Test linking requirements to business needs."""
        # Add business need first
        traceability_system.add_business_need(
            need_id="BN-001",
            title="Quality Improvement",
            description="Improve software quality",
            business_value="Better customer satisfaction"
        )
        
        # Link requirement to business need
        success = traceability_system.link_requirement_to_business_need(
            requirement_id="REQ-001",
            business_need_id="BN-001",
            description="Supports quality improvement through testing"
        )
        
        assert success
        
        # Try linking to non-existent business need
        failure = traceability_system.link_requirement_to_business_need(
            requirement_id="REQ-001",
            business_need_id="BN-999",
            description="Invalid link"
        )
        
        assert not failure
        
        # Check metrics
        metrics = traceability_system.metrics()
        assert metrics["requirements_with_business_links"] == 1.0
    
    def test_add_traceability_link(self, traceability_system):
        """Test adding traceability links between requirements."""
        link = traceability_system.add_traceability_link(
            source_id="REQ-001",
            target_id="REQ-002",
            link_type=TraceabilityLinkType.DEPENDS_ON,
            description="REQ-001 depends on REQ-002 for test result viewing",
            created_by="test_user"
        )
        
        assert link.source_id == "REQ-001"
        assert link.target_id == "REQ-002"
        assert link.link_type == TraceabilityLinkType.DEPENDS_ON
        assert link.created_by == "test_user"
        
        # Check incoming links can be found
        incoming_links = traceability_system.get_requirement_links("REQ-002", direction="incoming")
        assert len(incoming_links) > 0
        
        incoming_link = incoming_links[0]
        assert incoming_link.source_id == "REQ-001"
        assert incoming_link.target_id == "REQ-002"
        
        # Check metrics
        metrics = traceability_system.metrics()
        assert metrics["traceability_links_count"] == 1.0  # Only forward link
        assert metrics["requirements_with_links"] == 1.0
    
    def test_get_requirement_links(self, traceability_system):
        """Test getting requirement links."""
        # Add multiple links
        traceability_system.add_traceability_link(
            "REQ-001", "REQ-002", TraceabilityLinkType.DEPENDS_ON
        )
        traceability_system.add_traceability_link(
            "REQ-001", "REQ-003", TraceabilityLinkType.REFINES
        )
        
        # Get all links
        all_links = traceability_system.get_requirement_links("REQ-001")
        assert len(all_links) == 2
        
        # Get filtered links
        depends_links = traceability_system.get_requirement_links(
            "REQ-001", TraceabilityLinkType.DEPENDS_ON
        )
        assert len(depends_links) == 1
        assert depends_links[0].link_type == TraceabilityLinkType.DEPENDS_ON
    
    def test_get_requirement_dependencies(self, traceability_system):
        """Test getting requirement dependencies."""
        # Add various types of links
        traceability_system.add_traceability_link(
            "REQ-001", "REQ-002", TraceabilityLinkType.DEPENDS_ON
        )
        traceability_system.add_traceability_link(
            "REQ-001", "REQ-003", TraceabilityLinkType.REFINES
        )
        
        dependencies = traceability_system.get_requirement_dependencies("REQ-001")
        
        assert "depends_on" in dependencies
        assert "refines" in dependencies
        assert "REQ-002" in dependencies["depends_on"]
        assert "REQ-003" in dependencies["refines"]
    
    def test_find_requirement_conflicts(self, traceability_system):
        """Test finding requirement conflicts."""
        # Add conflict link
        traceability_system.add_traceability_link(
            "REQ-001", "REQ-002", TraceabilityLinkType.CONFLICTS_WITH,
            description="These requirements have conflicting objectives"
        )
        
        conflicts = traceability_system.find_requirement_conflicts("REQ-001")
        
        assert len(conflicts) == 1
        assert conflicts[0][0] == "REQ-002"
        assert "conflicting objectives" in conflicts[0][1]
    
    def test_record_requirement_change(self, traceability_system):
        """Test recording requirement changes."""
        change = traceability_system.record_requirement_change(
            requirement_id="REQ-001",
            change_type=ChangeType.MODIFIED,
            old_value="Old requirement text",
            new_value="New requirement text",
            changed_by="test_user",
            reason="Clarification needed"
        )
        
        assert change.requirement_id == "REQ-001"
        assert change.change_type == ChangeType.MODIFIED
        assert change.old_value == "Old requirement text"
        assert change.new_value == "New requirement text"
        assert change.changed_by == "test_user"
        assert change.reason == "Clarification needed"
        
        # Check system state
        health = traceability_system.health()
        assert health["change_history_count"] == 1
    
    def test_analyze_change_impact_basic(self, traceability_system):
        """Test basic change impact analysis."""
        # Set up dependencies
        traceability_system.add_traceability_link(
            "REQ-001", "REQ-002", TraceabilityLinkType.DEPENDS_ON
        )
        traceability_system.add_traceability_link(
            "REQ-002", "REQ-003", TraceabilityLinkType.REFINES
        )
        
        # Record a change
        change = traceability_system.record_requirement_change(
            requirement_id="REQ-001",
            change_type=ChangeType.MODIFIED,
            changed_by="test_user"
        )
        
        # Analyze impact
        impact = traceability_system.analyze_change_impact(change)
        
        assert impact.change == change
        assert len(impact.impacted_requirements) > 0
        assert impact.severity in [ImpactSeverity.LOW, ImpactSeverity.MEDIUM, ImpactSeverity.HIGH, ImpactSeverity.CRITICAL]
        assert len(impact.recommendations) > 0
        assert impact.estimated_effort > 0
    
    def test_analyze_change_impact_with_matrix(self, traceability_system):
        """Test change impact analysis with traceability matrix."""
        # Create traceability matrix
        matrix = TraceabilityMatrix()
        matrix.requirement_to_design["REQ-001"] = ["DESIGN-001", "DESIGN-002"]
        matrix.design_to_tasks["DESIGN-001"] = ["TASK-001", "TASK-002"]
        matrix.design_to_tasks["DESIGN-002"] = ["TASK-003"]
        
        # Record a change
        change = traceability_system.record_requirement_change(
            requirement_id="REQ-001",
            change_type=ChangeType.DELETED,
            changed_by="test_user"
        )
        
        # Analyze impact with matrix
        impact = traceability_system.analyze_change_impact(change, matrix)
        
        assert len(impact.impacted_design_components) == 2
        assert len(impact.impacted_tasks) == 3
        assert impact.severity in [ImpactSeverity.HIGH, ImpactSeverity.CRITICAL]  # Deletion should be high impact
    
    def test_generate_coverage_report_basic(self, traceability_system, sample_requirements):
        """Test basic coverage report generation."""
        # Add business need and link one requirement
        traceability_system.add_business_need(
            need_id="BN-001",
            title="Quality Improvement",
            description="Improve software quality",
            business_value="Better customer satisfaction"
        )
        
        traceability_system.link_requirement_to_business_need("REQ-001", "BN-001")
        
        # Generate report
        report = traceability_system.generate_coverage_report(sample_requirements)
        
        assert report.total_requirements == 3
        assert report.traced_requirements == 1
        assert len(report.untraceable_requirements) == 2
        assert report.coverage_percentage == pytest.approx(33.33, rel=1e-2)
        assert len(report.gaps) > 0
        assert len(report.recommendations) > 0
    
    def test_generate_coverage_report_with_matrix(self, traceability_system, sample_requirements):
        """Test coverage report with traceability matrix."""
        # Set up traceability matrix with orphaned components
        matrix = TraceabilityMatrix()
        matrix.requirement_to_design["REQ-001"] = ["DESIGN-001"]
        matrix.requirement_to_design["REQ-002"] = ["DESIGN-002"]
        matrix.design_to_tasks["DESIGN-001"] = ["TASK-001"]
        # DESIGN-002 has no tasks (orphaned)
        matrix.task_to_implementation["TASK-001"] = ["impl1.py"]
        # No implementation for other tasks (orphaned)
        
        # Generate report with matrix
        report = traceability_system.generate_coverage_report(sample_requirements, matrix)
        
        assert len(report.orphaned_components) > 0
        
        # Should identify orphaned design components and tasks
        orphaned_design = [comp for comp in report.orphaned_components if comp.startswith("design:")]
        assert len(orphaned_design) > 0
    
    def test_get_requirement_trace_path(self, traceability_system):
        """Test getting requirement trace paths."""
        # Set up a chain of dependencies
        traceability_system.add_traceability_link(
            "REQ-001", "REQ-002", TraceabilityLinkType.DERIVES_FROM
        )
        traceability_system.add_traceability_link(
            "REQ-002", "REQ-003", TraceabilityLinkType.REFINES
        )
        
        # Get trace paths
        paths = traceability_system.get_requirement_trace_path("REQ-001")
        
        assert len(paths) > 0
        
        # Should find path from REQ-001 through the chain
        found_path = False
        for path in paths:
            if len(path) > 1 and path[0] == "REQ-001":
                found_path = True
                break
        
        assert found_path
        
        # Test specific target
        target_paths = traceability_system.get_requirement_trace_path("REQ-001", "REQ-003")
        
        # Should find path to specific target if it exists
        if target_paths:
            assert any("REQ-003" in path for path in target_paths)
    
    def test_validate_traceability_consistency(self, traceability_system):
        """Test traceability consistency validation."""
        # Add some valid links
        traceability_system.add_traceability_link(
            "REQ-001", "REQ-002", TraceabilityLinkType.DEPENDS_ON
        )
        
        # Add orphaned business need
        traceability_system.add_business_need(
            need_id="BN-ORPHANED",
            title="Orphaned Need",
            description="This need has no requirements",
            business_value="None"
        )
        
        issues = traceability_system.validate_traceability_consistency()
        
        # Should find orphaned business need
        orphaned_issues = [issue for issue in issues if "orphaned" in issue.lower()]
        assert len(orphaned_issues) > 0
    
    def test_circular_dependency_detection(self, traceability_system):
        """Test circular dependency detection in validation."""
        # Since we prevent cycles at creation time, we need to test the detection logic
        # by directly manipulating the internal state (for testing purposes only)
        
        # Manually create a cycle in the internal structure to test detection
        from src.spec_framework.validation.requirement_traceability_system import TraceabilityLink, TraceabilityLinkType
        
        # Create links that form a cycle
        link1 = TraceabilityLink("REQ-001", "REQ-002", TraceabilityLinkType.DEPENDS_ON)
        link2 = TraceabilityLink("REQ-002", "REQ-003", TraceabilityLinkType.DEPENDS_ON)
        link3 = TraceabilityLink("REQ-003", "REQ-001", TraceabilityLinkType.DEPENDS_ON)
        
        traceability_system._traceability_links["REQ-001"].append(link1)
        traceability_system._traceability_links["REQ-002"].append(link2)
        traceability_system._traceability_links["REQ-003"].append(link3)
        
        issues = traceability_system.validate_traceability_consistency()
        
        # Should detect circular dependency
        circular_issues = [issue for issue in issues if "circular" in issue.lower()]
        assert len(circular_issues) > 0
    
    def test_conflicting_relationships_detection(self, traceability_system):
        """Test detection of conflicting relationships."""
        # Add conflicting relationships
        traceability_system.add_traceability_link(
            "REQ-001", "REQ-002", TraceabilityLinkType.DEPENDS_ON
        )
        traceability_system.add_traceability_link(
            "REQ-001", "REQ-002", TraceabilityLinkType.CONFLICTS_WITH
        )
        
        issues = traceability_system.validate_traceability_consistency()
        
        # Should detect conflicting relationships
        conflict_issues = [issue for issue in issues if "conflict" in issue.lower()]
        assert len(conflict_issues) > 0
    
    def test_impact_severity_calculation(self, traceability_system):
        """Test impact severity calculation."""
        # Set up extensive dependencies for high impact
        for i in range(2, 10):
            traceability_system.add_traceability_link(
                "REQ-001", f"REQ-{i:03d}", TraceabilityLinkType.DEPENDS_ON
            )
        
        # Create matrix with many impacted components
        matrix = TraceabilityMatrix()
        matrix.requirement_to_design["REQ-001"] = [f"DESIGN-{i:03d}" for i in range(1, 6)]
        for i in range(1, 6):
            matrix.design_to_tasks[f"DESIGN-{i:03d}"] = [f"TASK-{i:03d}-{j}" for j in range(1, 4)]
        
        # Test different change types
        deletion_change = traceability_system.record_requirement_change(
            requirement_id="REQ-001",
            change_type=ChangeType.DELETED
        )
        
        deletion_impact = traceability_system.analyze_change_impact(deletion_change, matrix)
        
        # Deletion with many dependencies should be high/critical impact
        assert deletion_impact.severity in [ImpactSeverity.HIGH, ImpactSeverity.CRITICAL]
        
        # Test low impact change
        addition_change = traceability_system.record_requirement_change(
            requirement_id="REQ-999",  # No dependencies
            change_type=ChangeType.ADDED
        )
        
        addition_impact = traceability_system.analyze_change_impact(addition_change)
        
        # Addition with no dependencies should be low impact
        assert addition_impact.severity == ImpactSeverity.LOW
    
    def test_coverage_gap_identification(self, traceability_system, sample_requirements):
        """Test identification of coverage gaps."""
        # Create requirements with various issues
        incomplete_req = Requirement(
            id="REQ-INCOMPLETE",
            user_story=UserStory("user", "do something", "get value"),
            business_value="Some value"
        )
        # This requirement has no acceptance criteria
        
        sample_requirements.append(incomplete_req)
        
        # Generate report
        report = traceability_system.generate_coverage_report(sample_requirements)
        
        # Should identify gap for requirements without acceptance criteria
        criteria_gaps = [gap for gap in report.gaps if "acceptance criteria" in gap.lower()]
        assert len(criteria_gaps) > 0
    
    def test_cycle_prevention(self, traceability_system):
        """Test that circular dependencies are prevented."""
        # Add initial link
        traceability_system.add_traceability_link(
            "REQ-001", "REQ-002", TraceabilityLinkType.DEPENDS_ON
        )
        
        traceability_system.add_traceability_link(
            "REQ-002", "REQ-003", TraceabilityLinkType.DEPENDS_ON
        )
        
        # Try to create a cycle - this should raise an error
        with pytest.raises(ValueError, match="circular dependency"):
            traceability_system.add_traceability_link(
                "REQ-003", "REQ-001", TraceabilityLinkType.DEPENDS_ON
            )
        
        # Non-dependency links should not be restricted
        traceability_system.add_traceability_link(
            "REQ-003", "REQ-001", TraceabilityLinkType.CONFLICTS_WITH
        )


class TestRequirementTraceabilityIntegration:
    """Integration tests for requirement traceability system."""
    
    @pytest.fixture
    def traceability_system(self):
        """Create requirement traceability system instance."""
        return RequirementTraceabilitySystem()
    
    def test_end_to_end_traceability_workflow(self, traceability_system):
        """Test complete traceability workflow."""
        # 1. Add business needs
        business_need = traceability_system.add_business_need(
            need_id="BN-001",
            title="Improve Development Efficiency",
            description="Reduce time spent on manual testing",
            business_value="Faster delivery and higher quality"
        )
        
        # 2. Create requirements
        requirements = [
            Requirement(
                id="REQ-001",
                user_story=UserStory("developer", "run automated tests", "save time"),
                business_value="Efficiency improvement"
            ),
            Requirement(
                id="REQ-002", 
                user_story=UserStory("developer", "view test results", "understand outcomes"),
                business_value="Better visibility"
            )
        ]
        
        # 3. Link requirements to business needs
        for req in requirements:
            traceability_system.link_requirement_to_business_need(req.id, business_need.id)
        
        # 4. Add traceability links
        traceability_system.add_traceability_link(
            "REQ-001", "REQ-002", TraceabilityLinkType.DEPENDS_ON,
            description="Test execution depends on result viewing capability"
        )
        
        # 5. Record changes and analyze impact
        change = traceability_system.record_requirement_change(
            "REQ-002", ChangeType.MODIFIED, reason="UI improvements"
        )
        
        impact = traceability_system.analyze_change_impact(change)
        
        # 6. Generate coverage report
        report = traceability_system.generate_coverage_report(requirements)
        
        # 7. Validate consistency
        issues = traceability_system.validate_traceability_consistency()
        
        # Verify end-to-end workflow
        assert report.coverage_percentage == 100.0  # All requirements linked
        assert len(impact.impacted_requirements) > 0  # Change has impact
        assert len(issues) == 0  # No consistency issues
        
        # Verify traceability paths exist
        paths = traceability_system.get_requirement_trace_path("REQ-001")
        assert len(paths) > 0
    
    def test_systematic_quality_validation(self, traceability_system):
        """Test that system enforces systematic quality standards."""
        # Create high-quality traceability structure
        traceability_system.add_business_need(
            "BN-HIGH", "High Quality Need", "Well-defined business need",
            "Clear business value with measurable outcomes"
        )
        
        # Create low-quality structure (orphaned business need)
        traceability_system.add_business_need(
            "BN-LOW", "Orphaned Need", "No requirements link to this",
            "Unclear value"
        )
        
        requirements = [
            Requirement(id="REQ-HIGH", user_story=UserStory("dev", "feature", "benefit"))
        ]
        
        # Link only to high-quality need
        traceability_system.link_requirement_to_business_need("REQ-HIGH", "BN-HIGH")
        
        # Validate quality
        issues = traceability_system.validate_traceability_consistency()
        report = traceability_system.generate_coverage_report(requirements)
        
        # Should identify quality issues
        assert len(issues) > 0  # Should find orphaned business need
        assert len(report.recommendations) > 0  # Should provide improvement suggestions
    
    def test_comprehensive_impact_analysis(self, traceability_system):
        """Test comprehensive impact analysis across complex dependencies."""
        # Create complex dependency network
        requirements = [f"REQ-{i:03d}" for i in range(1, 11)]
        
        # Create hierarchical dependencies
        for i in range(1, 6):
            traceability_system.add_traceability_link(
                f"REQ-{i:03d}", f"REQ-{i+5:03d}", TraceabilityLinkType.REFINES
            )
        
        # Create cross-dependencies
        traceability_system.add_traceability_link(
            "REQ-001", "REQ-003", TraceabilityLinkType.DEPENDS_ON
        )
        traceability_system.add_traceability_link(
            "REQ-002", "REQ-004", TraceabilityLinkType.DEPENDS_ON
        )
        
        # Create comprehensive traceability matrix
        matrix = TraceabilityMatrix()
        for req_id in requirements[:5]:
            matrix.requirement_to_design[req_id] = [f"DESIGN-{req_id}"]
            matrix.design_to_tasks[f"DESIGN-{req_id}"] = [f"TASK-{req_id}-1", f"TASK-{req_id}-2"]
        
        # Analyze impact of critical change
        change = traceability_system.record_requirement_change(
            "REQ-001", ChangeType.DELETED, reason="No longer needed"
        )
        
        impact = traceability_system.analyze_change_impact(change, matrix)
        
        # Should have comprehensive impact analysis
        assert len(impact.impacted_requirements) > 0
        assert len(impact.impacted_design_components) > 0
        assert len(impact.impacted_tasks) > 0
        assert impact.severity in [ImpactSeverity.HIGH, ImpactSeverity.CRITICAL]
        assert len(impact.recommendations) > 3  # Should have multiple recommendations
        assert impact.estimated_effort > 10  # Should estimate significant effort