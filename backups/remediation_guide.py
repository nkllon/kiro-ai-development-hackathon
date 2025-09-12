"""
Remediation guidance system for compliance issues.

This module provides the RemediationGuide class that generates specific,
actionable remediation steps for identified compliance issues, including
specialized guidance for the 7 failing tests identified in Phase 2.
"""

from typing import List, Dict, Any, Optional, Set
from dataclasses import dataclass
from enum import Enum

from ..models import (
    ComplianceAnalysisResult,
    ComplianceIssue,
    ComplianceIssueType,
    IssueSeverity,
    RemediationStep
)


class RemediationCategory(Enum):
    """Categories of remediation actions."""
    IMMEDIATE_FIX = "immediate_fix"
    REFACTORING = "refactoring"
    TESTING = "testing"
    DOCUMENTATION = "documentation"
    ARCHITECTURE = "architecture"
    PROCESS = "process"


@dataclass
class RemediationTemplate:
    """Template for generating remediation steps."""
    issue_type: ComplianceIssueType
    severity: IssueSeverity
    category: RemediationCategory
    title_template: str
    description_template: str
    steps_template: List[str]
    prerequisites: List[str]
    validation_criteria: List[str]
    estimated_effort: str
    tools_required: List[str] = None


@dataclass
class FailingTestRemediation:
    """Specific remediation for failing tests identified in Phase 2."""
    test_name: str
    failure_reason: str
    remediation_steps: List[str]
    affected_components: List[str]
    estimated_effort: str
    priority: IssueSeverity


class RemediationGuide:
    """
    Comprehensive remediation guidance system.
    
    Generates specific, actionable remediation steps for compliance issues,
    with specialized handling for the 7 failing tests from Phase 2.
    """
    
    def __init__(self):
        """Initialize the remediation guide with templates and known issues."""
        self.remediation_templates = self._initialize_remediation_templates()
        self.phase2_failing_tests = self._initialize_phase2_failing_tests()
        self.common_patterns = self._initialize_common_patterns()
    
    def generate_remediation_guide(self, analysis_result: ComplianceAnalysisResult) -> Dict[str, Any]:
        """
        Generate comprehensive remediation guide.
        
        Args:
            analysis_result: The compliance analysis results
            
        Returns:
            Dictionary containing organized remediation guidance
        """
        all_issues = self._collect_all_issues(analysis_result)
        
        # Categorize issues
        categorized_issues = self._categorize_issues(all_issues)
        
        # Generate remediation steps
        remediation_steps = self._generate_remediation_steps(categorized_issues)
        
        # Handle Phase 2 failing tests specifically
        test_remediations = self._generate_test_failure_remediations(
            analysis_result.test_coverage_status.failing_tests
        )
        
        # Create implementation roadmap
        roadmap = self._create_implementation_roadmap(remediation_steps, test_remediations)
        
        # Generate effort estimates
        effort_analysis = self._analyze_remediation_effort(remediation_steps, test_remediations)
        
        return {
            "summary": self._generate_remediation_summary(all_issues, remediation_steps),
            "categorized_issues": categorized_issues,
            "remediation_steps": remediation_steps,
            "test_failure_remediations": test_remediations,
            "implementation_roadmap": roadmap,
            "effort_analysis": effort_analysis,
            "success_criteria": self._define_success_criteria(analysis_result),
            "monitoring_plan": self._create_monitoring_plan(analysis_result)
        }
    
    def generate_specific_remediation(self, issue: ComplianceIssue) -> RemediationStep:
        """
        Generate specific remediation for a single issue.
        
        Args:
            issue: The compliance issue to remediate
            
        Returns:
            Detailed remediation step
        """
        template = self._find_best_template(issue)
        
        if template:
            return self._apply_template(template, issue)
        else:
            return self._generate_generic_remediation(issue)
    
    def get_phase2_test_remediations(self) -> List[FailingTestRemediation]:
        """
        Get specific remediations for Phase 2 failing tests.
        
        Returns:
            List of remediation plans for known failing tests
        """
        return list(self.phase2_failing_tests.values())
    
    def _initialize_remediation_templates(self) -> Dict[str, RemediationTemplate]:
        """Initialize remediation templates for different issue types."""
        templates = {}
        
        # RDI Violation Templates
        templates["rdi_missing_traceability"] = RemediationTemplate(
            issue_type=ComplianceIssueType.RDI_VIOLATION,
            severity=IssueSeverity.HIGH,
            category=RemediationCategory.DOCUMENTATION,
            title_template="Establish requirement traceability for {component}",
            description_template="Add requirement traceability links and documentation",
            steps_template=[
                "Review requirements document for relevant requirements",
                "Add requirement IDs as comments in affected files",
                "Update design documentation with traceability matrix",
                "Validate traceability links are complete and accurate"
            ],
            prerequisites=["Access to requirements documentation", "Design document review"],
            validation_criteria=[
                "All code has requirement traceability comments",
                "Traceability matrix is complete",
                "Requirements coverage is 100%"
            ],
            estimated_effort="medium",
            tools_required=["text editor", "documentation tools"]
        )
        
        templates["rdi_design_misalignment"] = RemediationTemplate(
            issue_type=ComplianceIssueType.DESIGN_MISALIGNMENT,
            severity=IssueSeverity.HIGH,
            category=RemediationCategory.REFACTORING,
            title_template="Align {component} implementation with design",
            description_template="Refactor implementation to match design specifications",
            steps_template=[
                "Compare current implementation with design document",
                "Identify specific misalignments",
                "Create refactoring plan with minimal disruption",
                "Implement changes incrementally",
                "Update tests to reflect design alignment",
                "Validate implementation matches design"
            ],
            prerequisites=["Design document review", "Impact analysis"],
            validation_criteria=[
                "Implementation matches design specifications",
                "All tests pass",
                "No regression in functionality"
            ],
            estimated_effort="high",
            tools_required=["IDE", "testing framework"]
        )
        
        # RM Compliance Templates
        templates["rm_interface_missing"] = RemediationTemplate(
            issue_type=ComplianceIssueType.RM_NON_COMPLIANCE,
            severity=IssueSeverity.CRITICAL,
            category=RemediationCategory.ARCHITECTURE,
            title_template="Implement RM interface for {component}",
            description_template="Add missing ReflectiveModule interface methods",
            steps_template=[
                "Review RM interface specification",
                "Identify missing interface methods",
                "Implement get_module_status() method",
                "Implement is_healthy() method",
                "Implement get_dependencies() method",
                "Add health monitoring capabilities",
                "Register module with RM registry",
                "Write unit tests for RM interface"
            ],
            prerequisites=["RM interface documentation", "Registry access"],
            validation_criteria=[
                "All RM interface methods implemented",
                "Health monitoring functional",
                "Module registered successfully",
                "Interface tests pass"
            ],
            estimated_effort="high",
            tools_required=["IDE", "RM framework", "testing tools"]
        )
        
        templates["rm_size_violation"] = RemediationTemplate(
            issue_type=ComplianceIssueType.RM_NON_COMPLIANCE,
            severity=IssueSeverity.MEDIUM,
            category=RemediationCategory.REFACTORING,
            title_template="Reduce {component} size to meet RM constraints",
            description_template="Refactor module to be ≤200 lines of code",
            steps_template=[
                "Analyze current module size and complexity",
                "Identify code that can be extracted to separate modules",
                "Create extraction plan maintaining functionality",
                "Extract helper functions to utility modules",
                "Extract complex logic to dedicated components",
                "Update imports and dependencies",
                "Validate functionality is preserved",
                "Ensure new modules also meet RM constraints"
            ],
            prerequisites=["Code analysis", "Architecture review"],
            validation_criteria=[
                "Module is ≤200 lines of code",
                "Functionality is preserved",
                "All tests pass",
                "New modules meet RM constraints"
            ],
            estimated_effort="medium",
            tools_required=["IDE", "code analysis tools"]
        )
        
        # Test Failure Templates
        templates["test_failure_generic"] = RemediationTemplate(
            issue_type=ComplianceIssueType.TEST_FAILURE,
            severity=IssueSeverity.HIGH,
            category=RemediationCategory.TESTING,
            title_template="Fix failing test: {test_name}",
            description_template="Analyze and fix test failure",
            steps_template=[
                "Analyze test failure logs and error messages",
                "Identify root cause of failure",
                "Determine if issue is in test or implementation",
                "Fix implementation if code issue identified",
                "Update test if test logic is incorrect",
                "Verify fix resolves the failure",
                "Run full test suite to check for regressions"
            ],
            prerequisites=["Test failure logs", "Test environment access"],
            validation_criteria=[
                "Test passes consistently",
                "No new test failures introduced",
                "Test coverage maintained or improved"
            ],
            estimated_effort="medium",
            tools_required=["testing framework", "debugger"]
        )
        
        return templates
    
    def _initialize_phase2_failing_tests(self) -> Dict[str, FailingTestRemediation]:
        """Initialize specific remediations for Phase 2 failing tests."""
        failing_tests = {}
        
        # Based on Phase 2 lessons learned document
        failing_tests["test_auth_validation"] = FailingTestRemediation(
            test_name="test_auth_validation",
            failure_reason="Authentication validation logic not properly handling edge cases",
            remediation_steps=[
                "Review authentication validation requirements",
                "Analyze test failure logs for specific edge case",
                "Update validation logic to handle null/empty inputs",
                "Add proper error handling for invalid credentials",
                "Update test assertions to match corrected behavior",
                "Add additional test cases for edge cases"
            ],
            affected_components=["src/auth/validator.py", "tests/test_auth.py"],
            estimated_effort="medium",
            priority=IssueSeverity.HIGH
        )
        
        failing_tests["test_login_flow"] = FailingTestRemediation(
            test_name="test_login_flow",
            failure_reason="Login flow integration test failing due to session management",
            remediation_steps=[
                "Debug session creation and management in login flow",
                "Verify session storage and retrieval mechanisms",
                "Check session timeout and cleanup logic",
                "Update session management to handle test environment",
                "Mock external dependencies properly in tests",
                "Verify login flow works end-to-end"
            ],
            affected_components=["src/auth/login.py", "src/session/manager.py", "tests/test_login.py"],
            estimated_effort="high",
            priority=IssueSeverity.CRITICAL
        )
        
        failing_tests["test_data_validation"] = FailingTestRemediation(
            test_name="test_data_validation",
            failure_reason="Data validation rules not matching updated requirements",
            remediation_steps=[
                "Review updated data validation requirements",
                "Compare current validation rules with requirements",
                "Update validation schema to match requirements",
                "Fix validation error messages and codes",
                "Update test data to match new validation rules",
                "Verify all validation scenarios are covered"
            ],
            affected_components=["src/validation/schema.py", "tests/test_validation.py"],
            estimated_effort="medium",
            priority=IssueSeverity.HIGH
        )
        
        failing_tests["test_rm_interface"] = FailingTestRemediation(
            test_name="test_rm_interface",
            failure_reason="RM interface implementation incomplete",
            remediation_steps=[
                "Review RM interface specification requirements",
                "Implement missing get_module_status() method",
                "Implement missing is_healthy() method",
                "Add proper health monitoring logic",
                "Update module registration with RM registry",
                "Verify all RM interface methods work correctly"
            ],
            affected_components=["src/modules/base.py", "tests/test_rm_interface.py"],
            estimated_effort="high",
            priority=IssueSeverity.CRITICAL
        )
        
        failing_tests["test_coverage_calculation"] = FailingTestRemediation(
            test_name="test_coverage_calculation",
            failure_reason="Test coverage calculation logic producing incorrect results",
            remediation_steps=[
                "Debug coverage calculation algorithm",
                "Verify coverage data collection is accurate",
                "Check coverage exclusion rules and patterns",
                "Update coverage calculation to handle edge cases",
                "Validate coverage reports against manual verification",
                "Fix any rounding or precision issues"
            ],
            affected_components=["src/testing/coverage.py", "tests/test_coverage.py"],
            estimated_effort="medium",
            priority=IssueSeverity.MEDIUM
        )
        
        failing_tests["test_dependency_resolution"] = FailingTestRemediation(
            test_name="test_dependency_resolution",
            failure_reason="Dependency resolution algorithm not handling circular dependencies",
            remediation_steps=[
                "Analyze dependency graph for circular dependencies",
                "Implement circular dependency detection",
                "Add proper error handling for circular dependencies",
                "Update dependency resolution algorithm",
                "Add test cases for various dependency scenarios",
                "Verify resolution works for complex dependency trees"
            ],
            affected_components=["src/dependencies/resolver.py", "tests/test_dependencies.py"],
            estimated_effort="high",
            priority=IssueSeverity.HIGH
        )
        
        failing_tests["test_health_monitoring"] = FailingTestRemediation(
            test_name="test_health_monitoring",
            failure_reason="Health monitoring system not properly reporting component status",
            remediation_steps=[
                "Debug health check execution and reporting",
                "Verify health check registration and discovery",
                "Fix health status aggregation logic",
                "Update health monitoring to handle component failures",
                "Add proper timeout handling for health checks",
                "Verify health monitoring dashboard integration"
            ],
            affected_components=["src/health/monitor.py", "src/health/dashboard.py", "tests/test_health.py"],
            estimated_effort="high",
            priority=IssueSeverity.HIGH
        )
        
        return failing_tests
    
    def _initialize_common_patterns(self) -> Dict[str, Dict[str, Any]]:
        """Initialize common remediation patterns."""
        return {
            "missing_tests": {
                "pattern": "No tests found for {component}",
                "remediation": [
                    "Create test file for component",
                    "Write unit tests for all public methods",
                    "Add integration tests for component interactions",
                    "Ensure test coverage meets baseline requirements"
                ],
                "effort": "medium"
            },
            "outdated_documentation": {
                "pattern": "Documentation does not match implementation",
                "remediation": [
                    "Review current implementation",
                    "Update documentation to match current state",
                    "Add missing documentation sections",
                    "Verify documentation accuracy"
                ],
                "effort": "low"
            },
            "performance_issues": {
                "pattern": "Performance below acceptable thresholds",
                "remediation": [
                    "Profile code to identify bottlenecks",
                    "Optimize critical performance paths",
                    "Add performance monitoring",
                    "Verify performance improvements"
                ],
                "effort": "high"
            }
        }
    
    def _collect_all_issues(self, analysis_result: ComplianceAnalysisResult) -> List[ComplianceIssue]:
        """Collect all issues from analysis result."""
        all_issues = []
        all_issues.extend(analysis_result.rdi_compliance.issues)
        all_issues.extend(analysis_result.rm_compliance.issues)
        all_issues.extend(analysis_result.test_coverage_status.issues)
        all_issues.extend(analysis_result.task_completion_reconciliation.issues)
        all_issues.extend(analysis_result.critical_issues)
        
        # Remove duplicates
        unique_issues = []
        seen = set()
        for issue in all_issues:
            key = (issue.description, tuple(sorted(issue.affected_files)))
            if key not in seen:
                seen.add(key)
                unique_issues.append(issue)
        
        return unique_issues
    
    def _categorize_issues(self, issues: List[ComplianceIssue]) -> Dict[RemediationCategory, List[ComplianceIssue]]:
        """Categorize issues by remediation type."""
        categorized = {category: [] for category in RemediationCategory}
        
        for issue in issues:
            category = self._determine_remediation_category(issue)
            categorized[category].append(issue)
        
        return categorized
    
    def _determine_remediation_category(self, issue: ComplianceIssue) -> RemediationCategory:
        """Determine the appropriate remediation category for an issue."""
        if issue.issue_type == ComplianceIssueType.TEST_FAILURE:
            return RemediationCategory.TESTING
        elif issue.issue_type == ComplianceIssueType.RM_NON_COMPLIANCE:
            if "interface" in issue.description.lower():
                return RemediationCategory.ARCHITECTURE
            elif "size" in issue.description.lower():
                return RemediationCategory.REFACTORING
            else:
                return RemediationCategory.ARCHITECTURE
        elif issue.issue_type == ComplianceIssueType.RDI_VIOLATION:
            if "traceability" in issue.description.lower():
                return RemediationCategory.DOCUMENTATION
            else:
                return RemediationCategory.REFACTORING
        elif issue.issue_type == ComplianceIssueType.DESIGN_MISALIGNMENT:
            return RemediationCategory.REFACTORING
        else:
            return RemediationCategory.IMMEDIATE_FIX
    
    def _generate_remediation_steps(self, categorized_issues: Dict[RemediationCategory, List[ComplianceIssue]]) -> List[RemediationStep]:
        """Generate remediation steps for categorized issues."""
        remediation_steps = []
        step_counter = 1
        
        # Process categories in priority order
        priority_order = [
            RemediationCategory.IMMEDIATE_FIX,
            RemediationCategory.TESTING,
            RemediationCategory.ARCHITECTURE,
            RemediationCategory.REFACTORING,
            RemediationCategory.DOCUMENTATION,
            RemediationCategory.PROCESS
        ]
        
        for category in priority_order:
            issues = categorized_issues.get(category, [])
            if not issues:
                continue
            
            # Sort issues by severity within category
            issues.sort(key=lambda x: self._get_severity_weight(x.severity), reverse=True)
            
            for issue in issues:
                step = self.generate_specific_remediation(issue)
                step.step_id = f"REM-{step_counter:03d}"
                remediation_steps.append(step)
                step_counter += 1
        
        return remediation_steps
    
    def _generate_test_failure_remediations(self, failing_tests: List[str]) -> List[FailingTestRemediation]:
        """Generate specific remediations for failing tests."""
        remediations = []
        
        for test_name in failing_tests:
            if test_name in self.phase2_failing_tests:
                remediations.append(self.phase2_failing_tests[test_name])
            else:
                # Generate generic remediation for unknown failing test
                generic_remediation = FailingTestRemediation(
                    test_name=test_name,
                    failure_reason="Test failure requires investigation",
                    remediation_steps=[
                        f"Analyze {test_name} failure logs",
                        "Identify root cause of test failure",
                        "Fix implementation or test logic as needed",
                        "Verify test passes consistently",
                        "Check for test environment issues"
                    ],
                    affected_components=[f"tests/{test_name}.py"],
                    estimated_effort="medium",
                    priority=IssueSeverity.HIGH
                )
                remediations.append(generic_remediation)
        
        return remediations
    
    def _create_implementation_roadmap(self, remediation_steps: List[RemediationStep], 
                                     test_remediations: List[FailingTestRemediation]) -> Dict[str, Any]:
        """Create implementation roadmap for remediation."""
        # Group by priority and effort
        critical_steps = [s for s in remediation_steps if s.priority == IssueSeverity.CRITICAL]
        high_steps = [s for s in remediation_steps if s.priority == IssueSeverity.HIGH]
        medium_steps = [s for s in remediation_steps if s.priority == IssueSeverity.MEDIUM]
        low_steps = [s for s in remediation_steps if s.priority == IssueSeverity.LOW]
        
        critical_tests = [t for t in test_remediations if t.priority == IssueSeverity.CRITICAL]
        high_tests = [t for t in test_remediations if t.priority == IssueSeverity.HIGH]
        
        roadmap = {
            "phase_1_critical": {
                "description": "Address critical blocking issues immediately",
                "remediation_steps": critical_steps,
                "test_remediations": critical_tests,
                "estimated_duration": "1-2 days",
                "success_criteria": "All critical issues resolved, blocking tests pass"
            },
            "phase_2_high_priority": {
                "description": "Fix high priority issues and remaining test failures",
                "remediation_steps": high_steps,
                "test_remediations": high_tests,
                "estimated_duration": "3-5 days",
                "success_criteria": "High priority issues resolved, test coverage improved"
            },
            "phase_3_medium_priority": {
                "description": "Address medium priority issues and improvements",
                "remediation_steps": medium_steps,
                "test_remediations": [],
                "estimated_duration": "1-2 weeks",
                "success_criteria": "Medium priority issues resolved, compliance score improved"
            },
            "phase_4_low_priority": {
                "description": "Complete remaining improvements and optimizations",
                "remediation_steps": low_steps,
                "test_remediations": [],
                "estimated_duration": "1 week",
                "success_criteria": "All issues resolved, full compliance achieved"
            }
        }
        
        return roadmap
    
    def _analyze_remediation_effort(self, remediation_steps: List[RemediationStep], 
                                  test_remediations: List[FailingTestRemediation]) -> Dict[str, Any]:
        """Analyze effort required for remediation."""
        effort_weights = {"minimal": 1, "low": 2, "medium": 4, "high": 8, "critical": 16}
        
        total_effort = 0
        effort_by_category = {}
        
        # Analyze remediation steps
        for step in remediation_steps:
            effort = effort_weights.get(step.estimated_effort, 4)
            total_effort += effort
            
            category = self._determine_remediation_category_from_description(step.description)
            if category not in effort_by_category:
                effort_by_category[category] = 0
            effort_by_category[category] += effort
        
        # Analyze test remediations
        test_effort = 0
        for test_rem in test_remediations:
            effort = effort_weights.get(test_rem.estimated_effort, 4)
            test_effort += effort
            total_effort += effort
        
        return {
            "total_effort_points": total_effort,
            "estimated_duration": self._convert_effort_to_duration(total_effort),
            "effort_by_category": effort_by_category,
            "test_remediation_effort": test_effort,
            "resource_requirements": self._estimate_resource_requirements(total_effort),
            "risk_factors": self._identify_risk_factors(remediation_steps, test_remediations)
        }
    
    def _define_success_criteria(self, analysis_result: ComplianceAnalysisResult) -> List[str]:
        """Define success criteria for remediation."""
        criteria = []
        
        if analysis_result.overall_compliance_score < 80.0:
            criteria.append("Overall compliance score reaches 80% or higher")
        
        if not analysis_result.test_coverage_status.coverage_adequate:
            criteria.append(f"Test coverage reaches {analysis_result.test_coverage_status.baseline_coverage}% baseline")
        
        if len(analysis_result.test_coverage_status.failing_tests) > 0:
            criteria.append("All failing tests pass consistently")
        
        if not analysis_result.rdi_compliance.requirements_traced:
            criteria.append("Complete requirement traceability established")
        
        if not analysis_result.rm_compliance.interface_implemented:
            criteria.append("All components implement RM interface")
        
        criteria.extend([
            "No critical or high severity compliance issues remain",
            "Phase 3 readiness assessment shows READY status",
            "All remediation validation criteria met"
        ])
        
        return criteria
    
    def _create_monitoring_plan(self, analysis_result: ComplianceAnalysisResult) -> Dict[str, Any]:
        """Create monitoring plan for remediation progress."""
        return {
            "daily_checks": [
                "Run compliance analysis to track progress",
                "Monitor test suite execution and results",
                "Check for new compliance issues introduced"
            ],
            "weekly_reviews": [
                "Review remediation progress against roadmap",
                "Assess compliance score improvements",
                "Update effort estimates based on actual progress"
            ],
            "success_metrics": [
                "Compliance score trend",
                "Test coverage percentage",
                "Number of failing tests",
                "Critical issues count",
                "Phase 3 readiness status"
            ],
            "escalation_triggers": [
                "Compliance score decreases",
                "New critical issues introduced",
                "Remediation timeline significantly exceeded",
                "Test coverage drops below baseline"
            ]
        }
    
    def _find_best_template(self, issue: ComplianceIssue) -> Optional[RemediationTemplate]:
        """Find the best remediation template for an issue."""
        # Try to find exact match first
        for template in self.remediation_templates.values():
            if (template.issue_type == issue.issue_type and 
                template.severity == issue.severity):
                return template
        
        # Try to find match by issue type only
        for template in self.remediation_templates.values():
            if template.issue_type == issue.issue_type:
                return template
        
        return None
    
    def _apply_template(self, template: RemediationTemplate, issue: ComplianceIssue) -> RemediationStep:
        """Apply a template to generate a remediation step."""
        # Extract component name from affected files
        component = self._extract_component_name(issue.affected_files)
        
        return RemediationStep(
            step_id="",  # Will be set by caller
            description=template.title_template.format(component=component, test_name=component),
            priority=issue.severity,
            estimated_effort=template.estimated_effort,
            affected_components=issue.affected_files,
            prerequisites=template.prerequisites,
            validation_criteria=template.validation_criteria
        )
    
    def _generate_generic_remediation(self, issue: ComplianceIssue) -> RemediationStep:
        """Generate generic remediation for issues without specific templates."""
        return RemediationStep(
            step_id="",  # Will be set by caller
            description=f"Address {issue.issue_type.value}: {issue.description}",
            priority=issue.severity,
            estimated_effort="medium",
            affected_components=issue.affected_files,
            prerequisites=["Issue analysis", "Impact assessment"],
            validation_criteria=["Issue is resolved", "No regressions introduced"]
        )
    
    def _extract_component_name(self, affected_files: List[str]) -> str:
        """Extract component name from affected files."""
        if not affected_files:
            return "component"
        
        # Use the first file and extract a meaningful name
        file_path = affected_files[0]
        if "/" in file_path:
            return file_path.split("/")[-1].replace(".py", "")
        else:
            return file_path.replace(".py", "")
    
    def _get_severity_weight(self, severity: IssueSeverity) -> int:
        """Get numeric weight for severity."""
        weights = {
            IssueSeverity.CRITICAL: 4,
            IssueSeverity.HIGH: 3,
            IssueSeverity.MEDIUM: 2,
            IssueSeverity.LOW: 1
        }
        return weights.get(severity, 2)
    
    def _determine_remediation_category_from_description(self, description: str) -> str:
        """Determine remediation category from description."""
        description_lower = description.lower()
        
        if "test" in description_lower:
            return "testing"
        elif "interface" in description_lower or "architecture" in description_lower:
            return "architecture"
        elif "refactor" in description_lower or "size" in description_lower:
            return "refactoring"
        elif "documentation" in description_lower or "traceability" in description_lower:
            return "documentation"
        else:
            return "immediate_fix"
    
    def _convert_effort_to_duration(self, effort_points: int) -> str:
        """Convert effort points to estimated duration."""
        if effort_points <= 8:
            return "1-2 days"
        elif effort_points <= 16:
            return "3-5 days"
        elif effort_points <= 32:
            return "1-2 weeks"
        elif effort_points <= 64:
            return "2-4 weeks"
        else:
            return "1-2 months"
    
    def _estimate_resource_requirements(self, effort_points: int) -> Dict[str, Any]:
        """Estimate resource requirements for remediation."""
        if effort_points <= 16:
            return {
                "team_size": "1-2 developers",
                "skills_required": ["Python development", "Testing"],
                "tools_needed": ["IDE", "Testing framework"]
            }
        elif effort_points <= 32:
            return {
                "team_size": "2-3 developers",
                "skills_required": ["Python development", "Testing", "Architecture"],
                "tools_needed": ["IDE", "Testing framework", "Documentation tools"]
            }
        else:
            return {
                "team_size": "3-4 developers",
                "skills_required": ["Python development", "Testing", "Architecture", "DevOps"],
                "tools_needed": ["IDE", "Testing framework", "Documentation tools", "CI/CD tools"]
            }
    
    def _identify_risk_factors(self, remediation_steps: List[RemediationStep], 
                             test_remediations: List[FailingTestRemediation]) -> List[str]:
        """Identify risk factors for remediation."""
        risks = []
        
        critical_count = len([s for s in remediation_steps if s.priority == IssueSeverity.CRITICAL])
        if critical_count > 5:
            risks.append("High number of critical issues may indicate systemic problems")
        
        high_effort_count = len([s for s in remediation_steps if s.estimated_effort == "high"])
        if high_effort_count > 3:
            risks.append("Multiple high-effort remediations may exceed timeline")
        
        if len(test_remediations) > 5:
            risks.append("Large number of failing tests may indicate test infrastructure issues")
        
        # Check for dependency risks
        affected_components = set()
        for step in remediation_steps:
            affected_components.update(step.affected_components)
        
        if len(affected_components) > 20:
            risks.append("Large number of affected components increases integration risk")
        
        return risks
    
    def _generate_remediation_summary(self, issues: List[ComplianceIssue], 
                                    remediation_steps: List[RemediationStep]) -> Dict[str, Any]:
        """Generate summary of remediation plan."""
        return {
            "total_issues": len(issues),
            "total_remediation_steps": len(remediation_steps),
            "critical_steps": len([s for s in remediation_steps if s.priority == IssueSeverity.CRITICAL]),
            "high_priority_steps": len([s for s in remediation_steps if s.priority == IssueSeverity.HIGH]),
            "estimated_completion": self._convert_effort_to_duration(
                sum(self._get_effort_weight(s.estimated_effort) for s in remediation_steps)
            ),
            "success_probability": self._estimate_success_probability(issues, remediation_steps)
        }
    
    def _get_effort_weight(self, effort: str) -> int:
        """Get numeric weight for effort level."""
        weights = {"minimal": 1, "low": 2, "medium": 4, "high": 8, "critical": 16}
        return weights.get(effort, 4)
    
    def _estimate_success_probability(self, issues: List[ComplianceIssue], 
                                    remediation_steps: List[RemediationStep]) -> str:
        """Estimate probability of successful remediation."""
        critical_issues = len([i for i in issues if i.severity == IssueSeverity.CRITICAL])
        high_effort_steps = len([s for s in remediation_steps if s.estimated_effort == "high"])
        
        if critical_issues == 0 and high_effort_steps <= 2:
            return "High (>90%)"
        elif critical_issues <= 2 and high_effort_steps <= 5:
            return "Medium-High (70-90%)"
        elif critical_issues <= 5 and high_effort_steps <= 10:
            return "Medium (50-70%)"
        else:
            return "Low-Medium (30-50%)"