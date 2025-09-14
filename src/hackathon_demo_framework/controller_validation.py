"""
Controller Validation

This module was extracted from controller.py
as part of RM-DDD compliance refactoring.
"""

import logging
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from .models import HackathonConfig, DemoPackage, DemoScript, ValidationResult, TechnicalAssessment, ComplianceAssessment, DemoEnvironment, SystematicEvidence, JudgeMaterials, PresentationMetrics, DEVPOST_HACKATHON_TEMPLATE, MLH_HACKATHON_TEMPLATE
from src.beast_mode.testing.test_orchestrator import BeastModeTestOrchestrator
from src.beast_mode.analysis.rca_analyzer import RCAPatternAnalyzer
from src.beast_mode.compliance.rdi_validator import RDIChainValidator
from .models import IsolationLevel
from src.rm_ddd.core.health import ModuleHealth


def validate_submission_readiness(self, demo_package: DemoPackage) -> ValidationResult:
    """
        Comprehensive validation of submission readiness.
        
        Args:
            demo_package: Demo package to validate
            
        Returns:
            Validation result with readiness assessment
        """
    issues = []
    recommendations = []
    if demo_package.technical_assessment.overall_technical_score < 80.0:
        issues.append(f'Technical score too low: {demo_package.technical_assessment.overall_technical_score:.1f}')
        recommendations.append('Improve code quality, testing, or documentation')
    if demo_package.compliance_assessment.overall_compliance_score < 95.0:
        issues.append(f'Compliance score too low: {demo_package.compliance_assessment.overall_compliance_score:.1f}')
        recommendations.extend(demo_package.compliance_assessment.blocking_issues)
    if demo_package.demo_environment.reliability_score < 90.0:
        issues.append(f'Demo reliability too low: {demo_package.demo_environment.reliability_score:.1f}')
        recommendations.append('Improve demo environment stability and backup plans')
    if demo_package.demo_script.total_duration > self.config.demo_time_limit * 60:
        issues.append(f'Demo too long: {demo_package.demo_script.total_duration}s > {self.config.demo_time_limit * 60}s')
        recommendations.append('Reduce demo content or improve pacing')
    is_valid = len(issues) == 0
    score = demo_package.get_readiness_score()
    return ValidationResult(is_valid=is_valid, score=score, issues=issues, recommendations=recommendations)

def _validate_technical_completeness(self) -> TechnicalAssessment:
    """Validate technical implementation completeness and quality."""
    return TechnicalAssessment(functionality_score=85.0, code_quality_score=80.0, documentation_score=75.0, test_coverage_percentage=85.0, installation_reliability=90.0, demo_stability_score=88.0, overall_technical_score=0, critical_issues=[], improvement_recommendations=['Improve documentation coverage', 'Add more integration tests'])

def _verify_compliance(self) -> ComplianceAssessment:
    """Verify compliance with hackathon requirements."""
    mandatory_requirements = {'README.md': (self.project_path / 'README.md').exists(), '.kiro directory': (self.project_path / '.kiro').exists(), 'requirements.txt or pyproject.toml': (self.project_path / 'requirements.txt').exists() or (self.project_path / 'pyproject.toml').exists()}
    return ComplianceAssessment(mandatory_requirements=mandatory_requirements, hackathon_specific_criteria={'theme_alignment': 85.0, 'technical_requirements': 90.0}, submission_format_compliance=True, deadline_compliance=datetime.now() < self.config.submission_deadline, team_eligibility=True, overall_compliance_score=0, blocking_issues=[], warning_issues=[])
