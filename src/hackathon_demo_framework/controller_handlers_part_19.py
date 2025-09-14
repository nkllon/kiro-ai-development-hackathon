from datetime import datetime
from typing import Dict, List, Any
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
