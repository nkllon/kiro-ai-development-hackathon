"""
Rca Analyzer Core

This module was extracted from rca_analyzer.py
as part of RM-DDD compliance refactoring.
"""

import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime
from enum import Enum

class RCASeverity(Enum):
    """RCA severity levels"""
    LOW = 'low'
    MEDIUM = 'medium'
    HIGH = 'high'
    CRITICAL = 'critical'

class RCACategory(Enum):
    """RCA category types"""
    TECHNICAL = 'technical'
    PROCESS = 'process'
    INFRASTRUCTURE = 'infrastructure'
    HUMAN = 'human'
    SYSTEMATIC = 'systematic'

@dataclass
class RCAResult:
    """Root cause analysis result"""
    issue_id: str
    description: str
    severity: RCASeverity
    category: RCACategory
    root_causes: List[str]
    contributing_factors: List[str]
    recommended_actions: List[str]
    prevention_measures: List[str]
    confidence_score: float
    analysis_timestamp: datetime
    analyst: str

class RCAAnalyzer:
    """
    Root Cause Analysis Analyzer
    
    Systematic analysis engine for identifying root causes of issues
    and generating actionable recommendations for prevention.
    """

    def __init__(self):
        """Initialize RCA analyzer"""
        self.analysis_history: List[RCAResult] = []
        self.pattern_database: Dict[str, List[str]] = {}
        self.prevention_rules: List[str] = []
        logger.info('RCA Analyzer initialized')

    def analyze_issue(self, issue_description: str, context: Dict[str, Any], severity: RCASeverity=RCASeverity.MEDIUM, category: RCACategory=RCACategory.TECHNICAL) -> RCAResult:
        """
        Analyze an issue to identify root causes
        
        Args:
            issue_description: Description of the issue
            context: Additional context information
            severity: Severity level of the issue
            category: Category of the issue
            
        Returns:
            RCAResult with analysis findings
        """
        logger.info(f'Analyzing issue: {issue_description}')
        issue_id = f'rca_{int(datetime.now().timestamp())}'
        root_causes = self._identify_root_causes(issue_description, context, category)
        contributing_factors = self._identify_contributing_factors(issue_description, context)
        recommended_actions = self._generate_recommendations(root_causes, severity)
        prevention_measures = self._generate_prevention_measures(root_causes, category)
        confidence_score = self._calculate_confidence_score(root_causes, context)
        result = RCAResult(issue_id=issue_id, description=issue_description, severity=severity, category=category, root_causes=root_causes, contributing_factors=contributing_factors, recommended_actions=recommended_actions, prevention_measures=prevention_measures, confidence_score=confidence_score, analysis_timestamp=datetime.now(), analyst='RCA Analyzer')
        self.analysis_history.append(result)
        self._update_pattern_database(result)
        logger.info(f'RCA analysis completed for issue {issue_id}')
        return result

    def _identify_root_causes(self, description: str, context: Dict[str, Any], category: RCACategory) -> List[str]:
        """Identify root causes based on issue description and context"""
        root_causes = []
        if category == RCACategory.TECHNICAL:
            if 'missing' in description.lower():
                root_causes.append('Incomplete implementation or missing components')
            if 'import' in description.lower() or 'module' in description.lower():
                root_causes.append('Module dependency or import issues')
            if 'error' in description.lower() or 'exception' in description.lower():
                root_causes.append('Error handling or exception management issues')
            if 'syntax' in description.lower():
                root_causes.append('Code syntax or structure issues')
        elif category == RCACategory.PROCESS:
            if 'validation' in description.lower():
                root_causes.append('Insufficient validation processes')
            if 'checklist' in description.lower():
                root_causes.append('Missing or incomplete process checklists')
            if 'workflow' in description.lower():
                root_causes.append('Workflow or process gaps')
        elif category == RCACategory.INFRASTRUCTURE:
            if 'deployment' in description.lower():
                root_causes.append('Deployment or infrastructure configuration issues')
            if 'service' in description.lower():
                root_causes.append('Service or infrastructure availability issues')
        elif category == RCACategory.SYSTEMATIC:
            if 'prevention' in description.lower():
                root_causes.append('Insufficient systematic prevention measures')
            if 'validation' in description.lower():
                root_causes.append('Missing systematic validation processes')
            if 'quality' in description.lower():
                root_causes.append('Quality assurance gaps')
        if not root_causes:
            root_causes.append('Insufficient analysis or unclear issue description')
        return root_causes

    def _identify_contributing_factors(self, description: str, context: Dict[str, Any]) -> List[str]:
        """Identify contributing factors to the issue"""
        factors = []
        if 'assumption' in description.lower():
            factors.append('Assumption-based development without validation')
        if 'time' in description.lower() or 'rush' in description.lower():
            factors.append('Time pressure or rushed development')
        if 'complex' in description.lower():
            factors.append('System complexity making issues harder to detect')
        if 'manual' in description.lower():
            factors.append('Manual processes prone to human error')
        if context.get('missing_validation', False):
            factors.append('Missing automated validation systems')
        if context.get('incomplete_checklist', False):
            factors.append('Incomplete development checklist')
        if context.get('no_prevention', False):
            factors.append('Lack of systematic prevention measures')
        return factors

    def _generate_recommendations(self, root_causes: List[str], severity: RCASeverity) -> List[str]:
        """Generate recommended actions based on root causes"""
        recommendations = []
        for cause in root_causes:
            if 'missing' in cause.lower() or 'incomplete' in cause.lower():
                recommendations.append('Implement comprehensive validation systems')
                recommendations.append('Create systematic development checklists')
                recommendations.append('Add automated quality gates')
            if 'import' in cause.lower() or 'module' in cause.lower():
                recommendations.append('Implement module completeness validation')
                recommendations.append('Add import testing to CI/CD pipeline')
                recommendations.append('Create dependency management system')
            if 'validation' in cause.lower():
                recommendations.append('Implement pre-commit validation hooks')
                recommendations.append('Add comprehensive testing suites')
                recommendations.append('Create systematic quality gates')
            if 'prevention' in cause.lower():
                recommendations.append('Implement systematic prevention architecture')
                recommendations.append('Add automated issue detection')
                recommendations.append('Create learning and improvement systems')
        if severity in [RCASeverity.HIGH, RCASeverity.CRITICAL]:
            recommendations.append('Implement immediate fixes and monitoring')
            recommendations.append('Conduct comprehensive system review')
            recommendations.append('Update prevention systems to prevent recurrence')
        return list(set(recommendations))

    def _generate_prevention_measures(self, root_causes: List[str], category: RCACategory) -> List[str]:
        """Generate prevention measures to avoid similar issues"""
        measures = []
        measures.append('Implement systematic development process')
        measures.append('Add comprehensive validation and testing')
        measures.append('Create automated quality gates')
        measures.append('Implement continuous monitoring and alerting')
        if category == RCACategory.TECHNICAL:
            measures.append('Implement module completeness validation')
            measures.append('Add automated import testing')
            measures.append('Create systematic code review process')
        elif category == RCACategory.PROCESS:
            measures.append('Implement development checklists')
            measures.append('Add process validation steps')
            measures.append('Create systematic workflow enforcement')
        elif category == RCACategory.SYSTEMATIC:
            measures.append('Implement prevention architecture')
            measures.append('Add systematic learning systems')
            measures.append('Create continuous improvement processes')
        return measures

    def _calculate_confidence_score(self, root_causes: List[str], context: Dict[str, Any]) -> float:
        """Calculate confidence score for the analysis"""
        base_score = 0.5
        if len(root_causes) > 0:
            base_score += 0.2
        if context.get('detailed_context', False):
            base_score += 0.1
        if context.get('historical_data', False):
            base_score += 0.1
        if context.get('systematic_analysis', False):
            base_score += 0.1
        return min(base_score, 1.0)

    def _update_pattern_database(self, result: RCAResult):
        """Update pattern database with analysis results"""
        pattern_key = f'{result.category.value}_{result.severity.value}'
        if pattern_key not in self.pattern_database:
            self.pattern_database[pattern_key] = []
        for cause in result.root_causes:
            if cause not in self.pattern_database[pattern_key]:
                self.pattern_database[pattern_key].append(cause)

    def get_analysis_history(self) -> List[RCAResult]:
        """Get analysis history"""
        return self.analysis_history

    def get_pattern_analysis(self) -> Dict[str, List[str]]:
        """Get pattern analysis from historical data"""
        return self.pattern_database

    def generate_prevention_rules(self) -> List[str]:
        """Generate prevention rules based on historical analysis"""
        rules = []
        for pattern, causes in self.pattern_database.items():
            if len(causes) > 1:
                rules.append(f"Prevent {pattern} issues by addressing: {', '.join(causes[:3])}")
        return rules

def __init__(self):
    """Initialize RCA analyzer"""
    self.analysis_history: List[RCAResult] = []
    self.pattern_database: Dict[str, List[str]] = {}
    self.prevention_rules: List[str] = []
    logger.info('RCA Analyzer initialized')

def analyze_issue(self, issue_description: str, context: Dict[str, Any], severity: RCASeverity=RCASeverity.MEDIUM, category: RCACategory=RCACategory.TECHNICAL) -> RCAResult:
    """
        Analyze an issue to identify root causes
        
        Args:
            issue_description: Description of the issue
            context: Additional context information
            severity: Severity level of the issue
            category: Category of the issue
            
        Returns:
            RCAResult with analysis findings
        """
    logger.info(f'Analyzing issue: {issue_description}')
    issue_id = f'rca_{int(datetime.now().timestamp())}'
    root_causes = self._identify_root_causes(issue_description, context, category)
    contributing_factors = self._identify_contributing_factors(issue_description, context)
    recommended_actions = self._generate_recommendations(root_causes, severity)
    prevention_measures = self._generate_prevention_measures(root_causes, category)
    confidence_score = self._calculate_confidence_score(root_causes, context)
    result = RCAResult(issue_id=issue_id, description=issue_description, severity=severity, category=category, root_causes=root_causes, contributing_factors=contributing_factors, recommended_actions=recommended_actions, prevention_measures=prevention_measures, confidence_score=confidence_score, analysis_timestamp=datetime.now(), analyst='RCA Analyzer')
    self.analysis_history.append(result)
    self._update_pattern_database(result)
    logger.info(f'RCA analysis completed for issue {issue_id}')
    return result

def _identify_root_causes(self, description: str, context: Dict[str, Any], category: RCACategory) -> List[str]:
    """Identify root causes based on issue description and context"""
    root_causes = []
    if category == RCACategory.TECHNICAL:
        if 'missing' in description.lower():
            root_causes.append('Incomplete implementation or missing components')
        if 'import' in description.lower() or 'module' in description.lower():
            root_causes.append('Module dependency or import issues')
        if 'error' in description.lower() or 'exception' in description.lower():
            root_causes.append('Error handling or exception management issues')
        if 'syntax' in description.lower():
            root_causes.append('Code syntax or structure issues')
    elif category == RCACategory.PROCESS:
        if 'validation' in description.lower():
            root_causes.append('Insufficient validation processes')
        if 'checklist' in description.lower():
            root_causes.append('Missing or incomplete process checklists')
        if 'workflow' in description.lower():
            root_causes.append('Workflow or process gaps')
    elif category == RCACategory.INFRASTRUCTURE:
        if 'deployment' in description.lower():
            root_causes.append('Deployment or infrastructure configuration issues')
        if 'service' in description.lower():
            root_causes.append('Service or infrastructure availability issues')
    elif category == RCACategory.SYSTEMATIC:
        if 'prevention' in description.lower():
            root_causes.append('Insufficient systematic prevention measures')
        if 'validation' in description.lower():
            root_causes.append('Missing systematic validation processes')
        if 'quality' in description.lower():
            root_causes.append('Quality assurance gaps')
    if not root_causes:
        root_causes.append('Insufficient analysis or unclear issue description')
    return root_causes

def _identify_contributing_factors(self, description: str, context: Dict[str, Any]) -> List[str]:
    """Identify contributing factors to the issue"""
    factors = []
    if 'assumption' in description.lower():
        factors.append('Assumption-based development without validation')
    if 'time' in description.lower() or 'rush' in description.lower():
        factors.append('Time pressure or rushed development')
    if 'complex' in description.lower():
        factors.append('System complexity making issues harder to detect')
    if 'manual' in description.lower():
        factors.append('Manual processes prone to human error')
    if context.get('missing_validation', False):
        factors.append('Missing automated validation systems')
    if context.get('incomplete_checklist', False):
        factors.append('Incomplete development checklist')
    if context.get('no_prevention', False):
        factors.append('Lack of systematic prevention measures')
    return factors

def _generate_recommendations(self, root_causes: List[str], severity: RCASeverity) -> List[str]:
    """Generate recommended actions based on root causes"""
    recommendations = []
    for cause in root_causes:
        if 'missing' in cause.lower() or 'incomplete' in cause.lower():
            recommendations.append('Implement comprehensive validation systems')
            recommendations.append('Create systematic development checklists')
            recommendations.append('Add automated quality gates')
        if 'import' in cause.lower() or 'module' in cause.lower():
            recommendations.append('Implement module completeness validation')
            recommendations.append('Add import testing to CI/CD pipeline')
            recommendations.append('Create dependency management system')
        if 'validation' in cause.lower():
            recommendations.append('Implement pre-commit validation hooks')
            recommendations.append('Add comprehensive testing suites')
            recommendations.append('Create systematic quality gates')
        if 'prevention' in cause.lower():
            recommendations.append('Implement systematic prevention architecture')
            recommendations.append('Add automated issue detection')
            recommendations.append('Create learning and improvement systems')
    if severity in [RCASeverity.HIGH, RCASeverity.CRITICAL]:
        recommendations.append('Implement immediate fixes and monitoring')
        recommendations.append('Conduct comprehensive system review')
        recommendations.append('Update prevention systems to prevent recurrence')
    return list(set(recommendations))

def _generate_prevention_measures(self, root_causes: List[str], category: RCACategory) -> List[str]:
    """Generate prevention measures to avoid similar issues"""
    measures = []
    measures.append('Implement systematic development process')
    measures.append('Add comprehensive validation and testing')
    measures.append('Create automated quality gates')
    measures.append('Implement continuous monitoring and alerting')
    if category == RCACategory.TECHNICAL:
        measures.append('Implement module completeness validation')
        measures.append('Add automated import testing')
        measures.append('Create systematic code review process')
    elif category == RCACategory.PROCESS:
        measures.append('Implement development checklists')
        measures.append('Add process validation steps')
        measures.append('Create systematic workflow enforcement')
    elif category == RCACategory.SYSTEMATIC:
        measures.append('Implement prevention architecture')
        measures.append('Add systematic learning systems')
        measures.append('Create continuous improvement processes')
    return measures

def _calculate_confidence_score(self, root_causes: List[str], context: Dict[str, Any]) -> float:
    """Calculate confidence score for the analysis"""
    base_score = 0.5
    if len(root_causes) > 0:
        base_score += 0.2
    if context.get('detailed_context', False):
        base_score += 0.1
    if context.get('historical_data', False):
        base_score += 0.1
    if context.get('systematic_analysis', False):
        base_score += 0.1
    return min(base_score, 1.0)

def _update_pattern_database(self, result: RCAResult):
    """Update pattern database with analysis results"""
    pattern_key = f'{result.category.value}_{result.severity.value}'
    if pattern_key not in self.pattern_database:
        self.pattern_database[pattern_key] = []
    for cause in result.root_causes:
        if cause not in self.pattern_database[pattern_key]:
            self.pattern_database[pattern_key].append(cause)

def get_analysis_history(self) -> List[RCAResult]:
    """Get analysis history"""
    return self.analysis_history

def get_pattern_analysis(self) -> Dict[str, List[str]]:
    """Get pattern analysis from historical data"""
    return self.pattern_database

def generate_prevention_rules(self) -> List[str]:
    """Generate prevention rules based on historical analysis"""
    rules = []
    for pattern, causes in self.pattern_database.items():
        if len(causes) > 1:
            rules.append(f"Prevent {pattern} issues by addressing: {', '.join(causes[:3])}")
    return rules
