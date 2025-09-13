"""
Complexity Core Core Core

This module was extracted from complexity_core_core.py
as part of RM-DDD compliance refactoring.
"""

"""
Complexity - Consolidated Interface Definition

This file was consolidated from the core_core_core refactoring mess.
All duplicate definitions have been removed and this is now the single
authoritative source for complexity.

Consolidated from: /Users/lou/kiro-2/kiro-ai-development-hackathon/src/rm_ddd/utilities/complexity_core_core_core.py
Consolidation date: 2025-09-13T10:15:07.515319
"""



import ast
import inspect
import logging
import math
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Set, Type, Union
from ..core.base import DomainReflectiveModule
from ..core.compliance import ValidationResult
from ..models import DomainException, ModuleStatus, ModuleCapability
from ..core.health import ModuleHealth
from ..models import DomainBoundaries
from ..models import DomainBoundaries
from ..core.health import ModuleHealth
from ..models import DomainBoundaries
from ..models import DomainBoundaries
from ..models import DomainBoundaries
from ..core.health import ModuleHealth
from ..models import DomainBoundaries

class ComplexityType(Enum):
    """Types of complexity measurements."""
    CYCLOMATIC = 'cyclomatic'
    COGNITIVE = 'cognitive'
    HALSTEAD = 'halstead'
    MAINTAINABILITY = 'maintainability'
    LINES_OF_CODE = 'lines_of_code'
    METHOD_COUNT = 'method_count'
    PARAMETER_COUNT = 'parameter_count'

@dataclass
class ComplexityMetric:
    """Represents a complexity measurement."""
    metric_type: ComplexityType
    value: float
    threshold: float
    description: str
    measured_at: datetime = field(default_factory=datetime.now)

    @property
    def exceeds_threshold(self) -> bool:
        """Check if metric exceeds its threshold."""
        return self.value > self.threshold

    @property
    def severity_level(self) -> str:
        """Get severity level based on threshold exceedance."""
        if self.value <= self.threshold:
            return 'acceptable'
        elif self.value <= self.threshold * 1.5:
            return 'warning'
        elif self.value <= self.threshold * 2.0:
            return 'high'
        else:
            return 'critical'

@dataclass
class ComplexityReport:
    """Comprehensive complexity report for a code element."""
    element_name: str
    element_type: str
    metrics: Dict[ComplexityType, ComplexityMetric] = field(default_factory=dict)
    suggestions: List[str] = field(default_factory=list)
    generated_at: datetime = field(default_factory=datetime.now)

    def add_metric(self, metric: ComplexityMetric):
        """Add a complexity metric to the report."""
        self.metrics[metric.metric_type] = metric

    def get_overall_score(self) -> float:
        """Calculate overall complexity score (0-100)."""
        if not self.metrics:
            return 0.0
        weights = {ComplexityType.CYCLOMATIC: 0.3, ComplexityType.COGNITIVE: 0.4, ComplexityType.MAINTAINABILITY: 0.2, ComplexityType.LINES_OF_CODE: 0.1}
        weighted_score = 0.0
        total_weight = 0.0
        for metric_type, metric in self.metrics.items():
            weight = weights.get(metric_type, 0.1)
            normalized_score = min(100.0, metric.value / metric.threshold * 50)
            weighted_score += normalized_score * weight
            total_weight += weight
        return weighted_score / max(total_weight, 1.0)

    def get_critical_issues(self) -> List[ComplexityMetric]:
        """Get metrics that are in critical state."""
        return [metric for metric in self.metrics.values() if metric.severity_level == 'critical']

    def to_dict(self) -> Dict[str, Any]:
        """Convert report to dictionary."""
        return {'element_name': self.element_name, 'element_type': self.element_type, 'overall_score': self.get_overall_score(), 'metrics': {metric_type.value: {'value': metric.value, 'threshold': metric.threshold, 'exceeds_threshold': metric.exceeds_threshold, 'severity': metric.severity_level} for metric_type, metric in self.metrics.items()}, 'suggestions': self.suggestions, 'generated_at': self.generated_at.isoformat()}

class ComplexityAnalyzer(ABC):
    """Abstract base class for complexity analyzers."""

    @abstractmethod
    def analyze(self, target: Any) -> ComplexityReport:
        """
        Analyze complexity of a target element.
        
        Args:
            target: Element to analyze (class, method, function, etc.)
            
        Returns:
            ComplexityReport: Complexity analysis report
        """
        pass

class CyclomaticComplexityAnalyzer(ComplexityAnalyzer):
    """
    Analyzer for cyclomatic complexity.
    
    Measures the number of linearly independent paths through
    a program's source code.
    """

    def __init__(self, threshold: float=10.0):
        self.threshold = threshold

    def analyze(self, target: Any) -> ComplexityReport:
        """Analyze cyclomatic complexity."""
        report = ComplexityReport(element_name=self._get_element_name(target), element_type=self._get_element_type(target))
        try:
            complexity = self._calculate_cyclomatic_complexity(target)
            metric = ComplexityMetric(metric_type=ComplexityType.CYCLOMATIC, value=complexity, threshold=self.threshold, description=f'Cyclomatic complexity: {complexity}')
            report.add_metric(metric)
            if complexity > self.threshold:
                report.suggestions.extend(self._get_cyclomatic_suggestions(complexity))
        except Exception as e:
            logger.error(f'Error calculating cyclomatic complexity: {e}')
        return report

    def _calculate_cyclomatic_complexity(self, target: Any) -> float:
        """Calculate cyclomatic complexity for a target."""
        if inspect.ismethod(target) or inspect.isfunction(target):
            return self._analyze_function_complexity(target)
        elif inspect.isclass(target):
            return self._analyze_class_complexity(target)
        else:
            return 1.0

    def _analyze_function_complexity(self, func: Any) -> float:
        """Analyze complexity of a function."""
        try:
            source = inspect.getsource(func)
            tree = ast.parse(source)
            complexity = 1
            for node in ast.walk(tree):
                if isinstance(node, (ast.If, ast.While, ast.For, ast.AsyncFor)):
                    complexity += 1
                elif isinstance(node, ast.ExceptHandler):
                    complexity += 1
                elif isinstance(node, ast.BoolOp):
                    complexity += len(node.values) - 1
            return float(complexity)
        except Exception as e:
            logger.warning(f'Could not analyze function complexity: {e}')
            return 1.0

    def _analyze_class_complexity(self, cls: Type) -> float:
        """Analyze complexity of a class."""
        total_complexity = 0.0
        method_count = 0
        for name, method in inspect.getmembers(cls, predicate=inspect.isfunction):
            if not name.startswith('_'):
                total_complexity += self._analyze_function_complexity(method)
                method_count += 1
        return total_complexity / max(method_count, 1)

    def _get_cyclomatic_suggestions(self, complexity: float) -> List[str]:
        """Get suggestions for reducing cyclomatic complexity."""
        suggestions = []
        if complexity > 15:
            suggestions.append('Consider breaking this method into smaller methods')
            suggestions.append('Extract complex conditional logic into separate methods')
        if complexity > 20:
            suggestions.append('This method is very complex - consider redesigning the algorithm')
            suggestions.append('Use strategy pattern to handle different cases')
        return suggestions

    def _get_element_name(self, target: Any) -> str:
        """Get name of the target element."""
        if hasattr(target, '__name__'):
            return target.__name__
        elif hasattr(target, '__class__'):
            return target.__class__.__name__
        else:
            return str(target)

    def _get_element_type(self, target: Any) -> str:
        """Get type of the target element."""
        if inspect.isclass(target):
            return 'class'
        elif inspect.ismethod(target) or inspect.isfunction(target):
            return 'method'
        else:
            return 'unknown'

class CognitiveComplexityAnalyzer(ComplexityAnalyzer):
    """
    Analyzer for cognitive complexity.
    
    Measures how difficult code is to understand by counting
    the mental overhead required to comprehend it.
    """

    def __init__(self, threshold: float=15.0):
        self.threshold = threshold

    def analyze(self, target: Any) -> ComplexityReport:
        """Analyze cognitive complexity."""
        report = ComplexityReport(element_name=self._get_element_name(target), element_type=self._get_element_type(target))
        try:
            complexity = self._calculate_cognitive_complexity(target)
            metric = ComplexityMetric(metric_type=ComplexityType.COGNITIVE, value=complexity, threshold=self.threshold, description=f'Cognitive complexity: {complexity}')
            report.add_metric(metric)
            if complexity > self.threshold:
                report.suggestions.extend(self._get_cognitive_suggestions(complexity))
        except Exception as e:
            logger.error(f'Error calculating cognitive complexity: {e}')
        return report

    def _calculate_cognitive_complexity(self, target: Any) -> float:
        """Calculate cognitive complexity for a target."""
        if inspect.ismethod(target) or inspect.isfunction(target):
            return self._analyze_function_cognitive_complexity(target)
        elif inspect.isclass(target):
            return self._analyze_class_cognitive_complexity(target)
        else:
            return 0.0

    def _analyze_function_cognitive_complexity(self, func: Any) -> float:
        """Analyze cognitive complexity of a function."""
        try:
            source = inspect.getsource(func)
            tree = ast.parse(source)
            complexity = 0
            nesting_level = 0

            class CognitiveVisitor(ast.NodeVisitor):

                def __init__(self):
                    self.complexity = 0
                    self.nesting_level = 0

                def visit_If(self, node):
                    self.complexity += 1 + self.nesting_level
                    self.nesting_level += 1
                    self.generic_visit(node)
                    self.nesting_level -= 1

                def visit_While(self, node):
                    self.complexity += 1 + self.nesting_level
                    self.nesting_level += 1
                    self.generic_visit(node)
                    self.nesting_level -= 1

                def visit_For(self, node):
                    self.complexity += 1 + self.nesting_level
                    self.nesting_level += 1
                    self.generic_visit(node)
                    self.nesting_level -= 1

                def visit_ExceptHandler(self, node):
                    self.complexity += 1 + self.nesting_level
                    self.nesting_level += 1
                    self.generic_visit(node)
                    self.nesting_level -= 1

                def visit_BoolOp(self, node):
                    self.complexity += len(node.values) - 1
                    self.generic_visit(node)
            visitor = CognitiveVisitor()
            visitor.visit(tree)
            return float(visitor.complexity)
        except Exception as e:
            logger.warning(f'Could not analyze cognitive complexity: {e}')
            return 0.0

    def _analyze_class_cognitive_complexity(self, cls: Type) -> float:
        """Analyze cognitive complexity of a class."""
        total_complexity = 0.0
        method_count = 0
        for name, method in inspect.getmembers(cls, predicate=inspect.isfunction):
            if not name.startswith('_'):
                total_complexity += self._analyze_function_cognitive_complexity(method)
                method_count += 1
        return total_complexity / max(method_count, 1)

    def _get_cognitive_suggestions(self, complexity: float) -> List[str]:
        """Get suggestions for reducing cognitive complexity."""
        suggestions = []
        if complexity > 20:
            suggestions.append('Reduce nesting levels by extracting methods')
            suggestions.append('Simplify boolean expressions')
            suggestions.append('Use early returns to reduce nesting')
        if complexity > 30:
            suggestions.append('This code is very difficult to understand')
            suggestions.append('Consider complete refactoring with simpler logic')
        return suggestions

    def _get_element_name(self, target: Any) -> str:
        """Get name of the target element."""
        if hasattr(target, '__name__'):
            return target.__name__
        elif hasattr(target, '__class__'):
            return target.__class__.__name__
        else:
            return str(target)

    def _get_element_type(self, target: Any) -> str:
        """Get type of the target element."""
        if inspect.isclass(target):
            return 'class'
        elif inspect.ismethod(target) or inspect.isfunction(target):
            return 'method'
        else:
            return 'unknown'

class ComplexityMonitor(DomainReflectiveModule):
    """
    Systematic complexity monitoring for domain models.
    
    Provides continuous monitoring of complexity metrics across
    domain models with alerting and trend analysis.
    """

    def __init__(self, domain_context: str='complexity_monitoring'):
        super().__init__(domain_context)
        self._analyzers: Dict[ComplexityType, ComplexityAnalyzer] = {}
        self._reports: Dict[str, ComplexityReport] = {}
        self._thresholds: Dict[ComplexityType, float] = {}
        self._initialize_default_analyzers()

    def _initialize_default_analyzers(self):
        """Initialize default complexity analyzers."""
        self._analyzers[ComplexityType.CYCLOMATIC] = CyclomaticComplexityAnalyzer()
        self._analyzers[ComplexityType.COGNITIVE] = CognitiveComplexityAnalyzer()
        self._thresholds = {ComplexityType.CYCLOMATIC: 10.0, ComplexityType.COGNITIVE: 15.0, ComplexityType.LINES_OF_CODE: 50.0, ComplexityType.METHOD_COUNT: 20.0, ComplexityType.PARAMETER_COUNT: 5.0}

    def add_analyzer(self, complexity_type: ComplexityType, analyzer: ComplexityAnalyzer):
        """Add a complexity analyzer."""
        self._analyzers[complexity_type] = analyzer
        logger.debug(f'Added complexity analyzer for {complexity_type.value}')

    def set_threshold(self, complexity_type: ComplexityType, threshold: float):
        """Set threshold for a complexity type."""
        self._thresholds[complexity_type] = threshold
        logger.debug(f'Set threshold for {complexity_type.value}: {threshold}')

    def analyze_element(self, target: Any, element_name: Optional[str]=None) -> ComplexityReport:
        """
        Analyze complexity of a single element.
        
        Args:
            target: Element to analyze
            element_name: Optional name for the element
            
        Returns:
            ComplexityReport: Comprehensive complexity report
        """
        if element_name is None:
            element_name = self._get_element_name(target)
        combined_report = ComplexityReport(element_name=element_name, element_type=self._get_element_type(target))
        for complexity_type, analyzer in self._analyzers.items():
            try:
                report = analyzer.analyze(target)
                for metric_type, metric in report.metrics.items():
                    combined_report.add_metric(metric)
                combined_report.suggestions.extend(report.suggestions)
            except Exception as e:
                logger.error(f'Error running {complexity_type.value} analyzer: {e}')
        self._add_basic_metrics(target, combined_report)
        self._reports[element_name] = combined_report
        return combined_report

    def _add_basic_metrics(self, target: Any, report: ComplexityReport):
        """Add basic complexity metrics."""
        try:
            if inspect.isclass(target) or inspect.isfunction(target):
                source = inspect.getsource(target)
                loc = len([line for line in source.split('\n') if line.strip()])
                metric = ComplexityMetric(metric_type=ComplexityType.LINES_OF_CODE, value=float(loc), threshold=self._thresholds.get(ComplexityType.LINES_OF_CODE, 50.0), description=f'Lines of code: {loc}')
                report.add_metric(metric)
            if inspect.isclass(target):
                method_count = len([m for m in inspect.getmembers(target, predicate=inspect.isfunction) if not m[0].startswith('_')])
                metric = ComplexityMetric(metric_type=ComplexityType.METHOD_COUNT, value=float(method_count), threshold=self._thresholds.get(ComplexityType.METHOD_COUNT, 20.0), description=f'Method count: {method_count}')
                report.add_metric(metric)
        except Exception as e:
            logger.warning(f'Could not add basic metrics: {e}')

    def get_complexity_summary(self) -> Dict[str, Any]:
        """Get summary of all complexity reports."""
        if not self._reports:
            return {'total_elements': 0, 'reports': []}
        critical_elements = []
        high_complexity_elements = []
        for element_name, report in self._reports.items():
            overall_score = report.get_overall_score()
            critical_issues = report.get_critical_issues()
            if critical_issues:
                critical_elements.append({'name': element_name, 'score': overall_score, 'critical_issues': len(critical_issues)})
            elif overall_score > 70:
                high_complexity_elements.append({'name': element_name, 'score': overall_score})
        return {'total_elements': len(self._reports), 'critical_elements': critical_elements, 'high_complexity_elements': high_complexity_elements, 'average_score': sum((r.get_overall_score() for r in self._reports.values())) / len(self._reports), 'thresholds': {t.value: threshold for t, threshold in self._thresholds.items()}}

    def _get_element_name(self, target: Any) -> str:
        """Get name of the target element."""
        if hasattr(target, '__name__'):
            return target.__name__
        elif hasattr(target, '__class__'):
            return target.__class__.__name__
        else:
            return str(target)

    def _get_element_type(self, target: Any) -> str:
        """Get type of the target element."""
        if inspect.isclass(target):
            return 'class'
        elif inspect.ismethod(target) or inspect.isfunction(target):
            return 'method'
        else:
            return 'unknown'

    async def get_module_status(self):
        """Get module status."""
        from ..core.health import ModuleHealth
        summary = self.get_complexity_summary()
        critical_count = len(summary.get('critical_elements', []))
        status = ModuleStatus.AVAILABLE if critical_count == 0 else ModuleStatus.DEGRADED
        return ModuleHealth(status=status, message=f"Complexity monitor tracking {summary['total_elements']} elements", capabilities=await self.get_module_capabilities(), health_indicators={'total_elements': summary['total_elements'], 'critical_elements': critical_count, 'average_score': summary.get('average_score', 0.0)})

    async def get_module_capabilities(self):
        """Get module capabilities."""
        return [ModuleCapability(name='complexity_monitoring', description='Monitors and analyzes code complexity', available=True, version='1.0.0')]

    async def is_healthy(self) -> bool:
        """Check if complexity monitor is healthy."""
        summary = self.get_complexity_summary()
        critical_count = len(summary.get('critical_elements', []))
        return critical_count == 0

    async def get_health_indicators(self):
        """Get health indicators."""
        return {'complexity_summary': self.get_complexity_summary(), 'domain_context': self.domain_context}

    def get_domain_boundaries(self):
        """Get domain boundaries."""
        from ..models import DomainBoundaries
        return DomainBoundaries(context=self.domain_context, invariants=['Complexity metrics must be within acceptable thresholds', 'Critical complexity issues must be addressed', 'Complexity trends should be monitored over time'])

    def validate_domain_invariants(self):
        """Validate domain invariants."""
        result = ValidationResult(is_valid=True)
        summary = self.get_complexity_summary()
        critical_count = len(summary.get('critical_elements', []))
        if critical_count > 0:
            result.add_error(f'Found {critical_count} elements with critical complexity issues')
        avg_score = summary.get('average_score', 0.0)
        if avg_score > 80:
            result.add_warning(f'High average complexity score: {avg_score:.1f}')
        return result

class CognitiveVisitor(ast.NodeVisitor):

    def __init__(self):
        self.complexity = 0
        self.nesting_level = 0

    def visit_If(self, node):
        self.complexity += 1 + self.nesting_level
        self.nesting_level += 1
        self.generic_visit(node)
        self.nesting_level -= 1

    def visit_While(self, node):
        self.complexity += 1 + self.nesting_level
        self.nesting_level += 1
        self.generic_visit(node)
        self.nesting_level -= 1

    def visit_For(self, node):
        self.complexity += 1 + self.nesting_level
        self.nesting_level += 1
        self.generic_visit(node)
        self.nesting_level -= 1

    def visit_ExceptHandler(self, node):
        self.complexity += 1 + self.nesting_level
        self.nesting_level += 1
        self.generic_visit(node)
        self.nesting_level -= 1

    def visit_BoolOp(self, node):
        self.complexity += len(node.values) - 1
        self.generic_visit(node)

class CognitiveVisitor(ast.NodeVisitor):

    def __init__(self):
        self.complexity = 0
        self.nesting_level = 0

    def visit_If(self, node):
        self.complexity += 1 + self.nesting_level
        self.nesting_level += 1
        self.generic_visit(node)
        self.nesting_level -= 1

    def visit_While(self, node):
        self.complexity += 1 + self.nesting_level
        self.nesting_level += 1
        self.generic_visit(node)
        self.nesting_level -= 1

    def visit_For(self, node):
        self.complexity += 1 + self.nesting_level
        self.nesting_level += 1
        self.generic_visit(node)
        self.nesting_level -= 1

    def visit_ExceptHandler(self, node):
        self.complexity += 1 + self.nesting_level
        self.nesting_level += 1
        self.generic_visit(node)
        self.nesting_level -= 1

    def visit_BoolOp(self, node):
        self.complexity += len(node.values) - 1
        self.generic_visit(node)

class CognitiveVisitor(ast.NodeVisitor):

    def __init__(self):
        self.complexity = 0
        self.nesting_level = 0

    def visit_If(self, node):
        self.complexity += 1 + self.nesting_level
        self.nesting_level += 1
        self.generic_visit(node)
        self.nesting_level -= 1

    def visit_While(self, node):
        self.complexity += 1 + self.nesting_level
        self.nesting_level += 1
        self.generic_visit(node)
        self.nesting_level -= 1

    def visit_For(self, node):
        self.complexity += 1 + self.nesting_level
        self.nesting_level += 1
        self.generic_visit(node)
        self.nesting_level -= 1

    def visit_ExceptHandler(self, node):
        self.complexity += 1 + self.nesting_level
        self.nesting_level += 1
        self.generic_visit(node)
        self.nesting_level -= 1

    def visit_BoolOp(self, node):
        self.complexity += len(node.values) - 1
        self.generic_visit(node)

class CognitiveVisitor(ast.NodeVisitor):

    def __init__(self):
        self.complexity = 0
        self.nesting_level = 0

    def visit_If(self, node):
        self.complexity += 1 + self.nesting_level
        self.nesting_level += 1
        self.generic_visit(node)
        self.nesting_level -= 1

    def visit_While(self, node):
        self.complexity += 1 + self.nesting_level
        self.nesting_level += 1
        self.generic_visit(node)
        self.nesting_level -= 1

    def visit_For(self, node):
        self.complexity += 1 + self.nesting_level
        self.nesting_level += 1
        self.generic_visit(node)
        self.nesting_level -= 1

    def visit_ExceptHandler(self, node):
        self.complexity += 1 + self.nesting_level
        self.nesting_level += 1
        self.generic_visit(node)
        self.nesting_level -= 1

    def visit_BoolOp(self, node):
        self.complexity += len(node.values) - 1
        self.generic_visit(node)

class CognitiveVisitor(ast.NodeVisitor):

    def __init__(self):
        self.complexity = 0
        self.nesting_level = 0

    def visit_If(self, node):
        self.complexity += 1 + self.nesting_level
        self.nesting_level += 1
        self.generic_visit(node)
        self.nesting_level -= 1

    def visit_While(self, node):
        self.complexity += 1 + self.nesting_level
        self.nesting_level += 1
        self.generic_visit(node)
        self.nesting_level -= 1

    def visit_For(self, node):
        self.complexity += 1 + self.nesting_level
        self.nesting_level += 1
        self.generic_visit(node)
        self.nesting_level -= 1

    def visit_ExceptHandler(self, node):
        self.complexity += 1 + self.nesting_level
        self.nesting_level += 1
        self.generic_visit(node)
        self.nesting_level -= 1

    def visit_BoolOp(self, node):
        self.complexity += len(node.values) - 1
        self.generic_visit(node)

class CognitiveVisitor(ast.NodeVisitor):

    def __init__(self):
        self.complexity = 0
        self.nesting_level = 0

    def visit_If(self, node):
        self.complexity += 1 + self.nesting_level
        self.nesting_level += 1
        self.generic_visit(node)
        self.nesting_level -= 1

    def visit_While(self, node):
        self.complexity += 1 + self.nesting_level
        self.nesting_level += 1
        self.generic_visit(node)
        self.nesting_level -= 1

    def visit_For(self, node):
        self.complexity += 1 + self.nesting_level
        self.nesting_level += 1
        self.generic_visit(node)
        self.nesting_level -= 1

    def visit_ExceptHandler(self, node):
        self.complexity += 1 + self.nesting_level
        self.nesting_level += 1
        self.generic_visit(node)
        self.nesting_level -= 1

    def visit_BoolOp(self, node):
        self.complexity += len(node.values) - 1
        self.generic_visit(node)

def analyze_class_complexity(cls: Type) -> ComplexityReport:
    """Analyze complexity of a class."""
    monitor = ComplexityMonitor()
    return monitor.analyze_element(cls)

def analyze_method_complexity(method: Any) -> ComplexityReport:
    """Analyze complexity of a method."""
    monitor = ComplexityMonitor()
    return monitor.analyze_element(method)

@property
def exceeds_threshold(self) -> bool:
    """Check if metric exceeds its threshold."""
    return self.value > self.threshold

@property
def severity_level(self) -> str:
    """Get severity level based on threshold exceedance."""
    if self.value <= self.threshold:
        return 'acceptable'
    elif self.value <= self.threshold * 1.5:
        return 'warning'
    elif self.value <= self.threshold * 2.0:
        return 'high'
    else:
        return 'critical'

def add_metric(self, metric: ComplexityMetric):
    """Add a complexity metric to the report."""
    self.metrics[metric.metric_type] = metric

def get_overall_score(self) -> float:
    """Calculate overall complexity score (0-100)."""
    if not self.metrics:
        return 0.0
    weights = {ComplexityType.CYCLOMATIC: 0.3, ComplexityType.COGNITIVE: 0.4, ComplexityType.MAINTAINABILITY: 0.2, ComplexityType.LINES_OF_CODE: 0.1}
    weighted_score = 0.0
    total_weight = 0.0
    for metric_type, metric in self.metrics.items():
        weight = weights.get(metric_type, 0.1)
        normalized_score = min(100.0, metric.value / metric.threshold * 50)
        weighted_score += normalized_score * weight
        total_weight += weight
    return weighted_score / max(total_weight, 1.0)

def get_critical_issues(self) -> List[ComplexityMetric]:
    """Get metrics that are in critical state."""
    return [metric for metric in self.metrics.values() if metric.severity_level == 'critical']

def to_dict(self) -> Dict[str, Any]:
    """Convert report to dictionary."""
    return {'element_name': self.element_name, 'element_type': self.element_type, 'overall_score': self.get_overall_score(), 'metrics': {metric_type.value: {'value': metric.value, 'threshold': metric.threshold, 'exceeds_threshold': metric.exceeds_threshold, 'severity': metric.severity_level} for metric_type, metric in self.metrics.items()}, 'suggestions': self.suggestions, 'generated_at': self.generated_at.isoformat()}

@abstractmethod
def analyze(self, target: Any) -> ComplexityReport:
    """
        Analyze complexity of a target element.
        
        Args:
            target: Element to analyze (class, method, function, etc.)
            
        Returns:
            ComplexityReport: Complexity analysis report
        """
    pass

def __init__(self, threshold: float=10.0):
    self.threshold = threshold

def analyze(self, target: Any) -> ComplexityReport:
    """Analyze cyclomatic complexity."""
    report = ComplexityReport(element_name=self._get_element_name(target), element_type=self._get_element_type(target))
    try:
        complexity = self._calculate_cyclomatic_complexity(target)
        metric = ComplexityMetric(metric_type=ComplexityType.CYCLOMATIC, value=complexity, threshold=self.threshold, description=f'Cyclomatic complexity: {complexity}')
        report.add_metric(metric)
        if complexity > self.threshold:
            report.suggestions.extend(self._get_cyclomatic_suggestions(complexity))
    except Exception as e:
        logger.error(f'Error calculating cyclomatic complexity: {e}')
    return report

def _calculate_cyclomatic_complexity(self, target: Any) -> float:
    """Calculate cyclomatic complexity for a target."""
    if inspect.ismethod(target) or inspect.isfunction(target):
        return self._analyze_function_complexity(target)
    elif inspect.isclass(target):
        return self._analyze_class_complexity(target)
    else:
        return 1.0

def _analyze_function_complexity(self, func: Any) -> float:
    """Analyze complexity of a function."""
    try:
        source = inspect.getsource(func)
        tree = ast.parse(source)
        complexity = 1
        for node in ast.walk(tree):
            if isinstance(node, (ast.If, ast.While, ast.For, ast.AsyncFor)):
                complexity += 1
            elif isinstance(node, ast.ExceptHandler):
                complexity += 1
            elif isinstance(node, ast.BoolOp):
                complexity += len(node.values) - 1
        return float(complexity)
    except Exception as e:
        logger.warning(f'Could not analyze function complexity: {e}')
        return 1.0

def _analyze_class_complexity(self, cls: Type) -> float:
    """Analyze complexity of a class."""
    total_complexity = 0.0
    method_count = 0
    for name, method in inspect.getmembers(cls, predicate=inspect.isfunction):
        if not name.startswith('_'):
            total_complexity += self._analyze_function_complexity(method)
            method_count += 1
    return total_complexity / max(method_count, 1)

def _get_cyclomatic_suggestions(self, complexity: float) -> List[str]:
    """Get suggestions for reducing cyclomatic complexity."""
    suggestions = []
    if complexity > 15:
        suggestions.append('Consider breaking this method into smaller methods')
        suggestions.append('Extract complex conditional logic into separate methods')
    if complexity > 20:
        suggestions.append('This method is very complex - consider redesigning the algorithm')
        suggestions.append('Use strategy pattern to handle different cases')
    return suggestions

def _get_element_name(self, target: Any) -> str:
    """Get name of the target element."""
    if hasattr(target, '__name__'):
        return target.__name__
    elif hasattr(target, '__class__'):
        return target.__class__.__name__
    else:
        return str(target)

def _get_element_type(self, target: Any) -> str:
    """Get type of the target element."""
    if inspect.isclass(target):
        return 'class'
    elif inspect.ismethod(target) or inspect.isfunction(target):
        return 'method'
    else:
        return 'unknown'

def __init__(self, threshold: float=15.0):
    self.threshold = threshold

def analyze(self, target: Any) -> ComplexityReport:
    """Analyze cognitive complexity."""
    report = ComplexityReport(element_name=self._get_element_name(target), element_type=self._get_element_type(target))
    try:
        complexity = self._calculate_cognitive_complexity(target)
        metric = ComplexityMetric(metric_type=ComplexityType.COGNITIVE, value=complexity, threshold=self.threshold, description=f'Cognitive complexity: {complexity}')
        report.add_metric(metric)
        if complexity > self.threshold:
            report.suggestions.extend(self._get_cognitive_suggestions(complexity))
    except Exception as e:
        logger.error(f'Error calculating cognitive complexity: {e}')
    return report

def _calculate_cognitive_complexity(self, target: Any) -> float:
    """Calculate cognitive complexity for a target."""
    if inspect.ismethod(target) or inspect.isfunction(target):
        return self._analyze_function_cognitive_complexity(target)
    elif inspect.isclass(target):
        return self._analyze_class_cognitive_complexity(target)
    else:
        return 0.0

def _analyze_function_cognitive_complexity(self, func: Any) -> float:
    """Analyze cognitive complexity of a function."""
    try:
        source = inspect.getsource(func)
        tree = ast.parse(source)
        complexity = 0
        nesting_level = 0

        class CognitiveVisitor(ast.NodeVisitor):

            def __init__(self):
                self.complexity = 0
                self.nesting_level = 0

            def visit_If(self, node):
                self.complexity += 1 + self.nesting_level
                self.nesting_level += 1
                self.generic_visit(node)
                self.nesting_level -= 1

            def visit_While(self, node):
                self.complexity += 1 + self.nesting_level
                self.nesting_level += 1
                self.generic_visit(node)
                self.nesting_level -= 1

            def visit_For(self, node):
                self.complexity += 1 + self.nesting_level
                self.nesting_level += 1
                self.generic_visit(node)
                self.nesting_level -= 1

            def visit_ExceptHandler(self, node):
                self.complexity += 1 + self.nesting_level
                self.nesting_level += 1
                self.generic_visit(node)
                self.nesting_level -= 1

            def visit_BoolOp(self, node):
                self.complexity += len(node.values) - 1
                self.generic_visit(node)
        visitor = CognitiveVisitor()
        visitor.visit(tree)
        return float(visitor.complexity)
    except Exception as e:
        logger.warning(f'Could not analyze cognitive complexity: {e}')
        return 0.0

def _analyze_class_cognitive_complexity(self, cls: Type) -> float:
    """Analyze cognitive complexity of a class."""
    total_complexity = 0.0
    method_count = 0
    for name, method in inspect.getmembers(cls, predicate=inspect.isfunction):
        if not name.startswith('_'):
            total_complexity += self._analyze_function_cognitive_complexity(method)
            method_count += 1
    return total_complexity / max(method_count, 1)

def _get_cognitive_suggestions(self, complexity: float) -> List[str]:
    """Get suggestions for reducing cognitive complexity."""
    suggestions = []
    if complexity > 20:
        suggestions.append('Reduce nesting levels by extracting methods')
        suggestions.append('Simplify boolean expressions')
        suggestions.append('Use early returns to reduce nesting')
    if complexity > 30:
        suggestions.append('This code is very difficult to understand')
        suggestions.append('Consider complete refactoring with simpler logic')
    return suggestions

def _get_element_name(self, target: Any) -> str:
    """Get name of the target element."""
    if hasattr(target, '__name__'):
        return target.__name__
    elif hasattr(target, '__class__'):
        return target.__class__.__name__
    else:
        return str(target)

def _get_element_type(self, target: Any) -> str:
    """Get type of the target element."""
    if inspect.isclass(target):
        return 'class'
    elif inspect.ismethod(target) or inspect.isfunction(target):
        return 'method'
    else:
        return 'unknown'

def __init__(self, domain_context: str='complexity_monitoring'):
    super().__init__(domain_context)
    self._analyzers: Dict[ComplexityType, ComplexityAnalyzer] = {}
    self._reports: Dict[str, ComplexityReport] = {}
    self._thresholds: Dict[ComplexityType, float] = {}
    self._initialize_default_analyzers()

def _initialize_default_analyzers(self):
    """Initialize default complexity analyzers."""
    self._analyzers[ComplexityType.CYCLOMATIC] = CyclomaticComplexityAnalyzer()
    self._analyzers[ComplexityType.COGNITIVE] = CognitiveComplexityAnalyzer()
    self._thresholds = {ComplexityType.CYCLOMATIC: 10.0, ComplexityType.COGNITIVE: 15.0, ComplexityType.LINES_OF_CODE: 50.0, ComplexityType.METHOD_COUNT: 20.0, ComplexityType.PARAMETER_COUNT: 5.0}

def add_analyzer(self, complexity_type: ComplexityType, analyzer: ComplexityAnalyzer):
    """Add a complexity analyzer."""
    self._analyzers[complexity_type] = analyzer
    logger.debug(f'Added complexity analyzer for {complexity_type.value}')

def set_threshold(self, complexity_type: ComplexityType, threshold: float):
    """Set threshold for a complexity type."""
    self._thresholds[complexity_type] = threshold
    logger.debug(f'Set threshold for {complexity_type.value}: {threshold}')

def analyze_element(self, target: Any, element_name: Optional[str]=None) -> ComplexityReport:
    """
        Analyze complexity of a single element.
        
        Args:
            target: Element to analyze
            element_name: Optional name for the element
            
        Returns:
            ComplexityReport: Comprehensive complexity report
        """
    if element_name is None:
        element_name = self._get_element_name(target)
    combined_report = ComplexityReport(element_name=element_name, element_type=self._get_element_type(target))
    for complexity_type, analyzer in self._analyzers.items():
        try:
            report = analyzer.analyze(target)
            for metric_type, metric in report.metrics.items():
                combined_report.add_metric(metric)
            combined_report.suggestions.extend(report.suggestions)
        except Exception as e:
            logger.error(f'Error running {complexity_type.value} analyzer: {e}')
    self._add_basic_metrics(target, combined_report)
    self._reports[element_name] = combined_report
    return combined_report

def _add_basic_metrics(self, target: Any, report: ComplexityReport):
    """Add basic complexity metrics."""
    try:
        if inspect.isclass(target) or inspect.isfunction(target):
            source = inspect.getsource(target)
            loc = len([line for line in source.split('\n') if line.strip()])
            metric = ComplexityMetric(metric_type=ComplexityType.LINES_OF_CODE, value=float(loc), threshold=self._thresholds.get(ComplexityType.LINES_OF_CODE, 50.0), description=f'Lines of code: {loc}')
            report.add_metric(metric)
        if inspect.isclass(target):
            method_count = len([m for m in inspect.getmembers(target, predicate=inspect.isfunction) if not m[0].startswith('_')])
            metric = ComplexityMetric(metric_type=ComplexityType.METHOD_COUNT, value=float(method_count), threshold=self._thresholds.get(ComplexityType.METHOD_COUNT, 20.0), description=f'Method count: {method_count}')
            report.add_metric(metric)
    except Exception as e:
        logger.warning(f'Could not add basic metrics: {e}')

def get_complexity_summary(self) -> Dict[str, Any]:
    """Get summary of all complexity reports."""
    if not self._reports:
        return {'total_elements': 0, 'reports': []}
    critical_elements = []
    high_complexity_elements = []
    for element_name, report in self._reports.items():
        overall_score = report.get_overall_score()
        critical_issues = report.get_critical_issues()
        if critical_issues:
            critical_elements.append({'name': element_name, 'score': overall_score, 'critical_issues': len(critical_issues)})
        elif overall_score > 70:
            high_complexity_elements.append({'name': element_name, 'score': overall_score})
    return {'total_elements': len(self._reports), 'critical_elements': critical_elements, 'high_complexity_elements': high_complexity_elements, 'average_score': sum((r.get_overall_score() for r in self._reports.values())) / len(self._reports), 'thresholds': {t.value: threshold for t, threshold in self._thresholds.items()}}

def _get_element_name(self, target: Any) -> str:
    """Get name of the target element."""
    if hasattr(target, '__name__'):
        return target.__name__
    elif hasattr(target, '__class__'):
        return target.__class__.__name__
    else:
        return str(target)

def _get_element_type(self, target: Any) -> str:
    """Get type of the target element."""
    if inspect.isclass(target):
        return 'class'
    elif inspect.ismethod(target) or inspect.isfunction(target):
        return 'method'
    else:
        return 'unknown'

def get_domain_boundaries(self):
    """Get domain boundaries."""
    from ..models import DomainBoundaries
    return DomainBoundaries(context=self.domain_context, invariants=['Complexity metrics must be within acceptable thresholds', 'Critical complexity issues must be addressed', 'Complexity trends should be monitored over time'])

def __init__(self):
    self.complexity = 0
    self.nesting_level = 0

def visit_If(self, node):
    self.complexity += 1 + self.nesting_level
    self.nesting_level += 1
    self.generic_visit(node)
    self.nesting_level -= 1

def visit_While(self, node):
    self.complexity += 1 + self.nesting_level
    self.nesting_level += 1
    self.generic_visit(node)
    self.nesting_level -= 1

def visit_For(self, node):
    self.complexity += 1 + self.nesting_level
    self.nesting_level += 1
    self.generic_visit(node)
    self.nesting_level -= 1

def visit_ExceptHandler(self, node):
    self.complexity += 1 + self.nesting_level
    self.nesting_level += 1
    self.generic_visit(node)
    self.nesting_level -= 1

def visit_BoolOp(self, node):
    self.complexity += len(node.values) - 1
    self.generic_visit(node)

@property
def exceeds_threshold(self) -> bool:
    """Check if metric exceeds its threshold."""
    return self.value > self.threshold

@property
def severity_level(self) -> str:
    """Get severity level based on threshold exceedance."""
    if self.value <= self.threshold:
        return 'acceptable'
    elif self.value <= self.threshold * 1.5:
        return 'warning'
    elif self.value <= self.threshold * 2.0:
        return 'high'
    else:
        return 'critical'

def add_metric(self, metric: ComplexityMetric):
    """Add a complexity metric to the report."""
    self.metrics[metric.metric_type] = metric

def get_overall_score(self) -> float:
    """Calculate overall complexity score (0-100)."""
    if not self.metrics:
        return 0.0
    weights = {ComplexityType.CYCLOMATIC: 0.3, ComplexityType.COGNITIVE: 0.4, ComplexityType.MAINTAINABILITY: 0.2, ComplexityType.LINES_OF_CODE: 0.1}
    weighted_score = 0.0
    total_weight = 0.0
    for metric_type, metric in self.metrics.items():
        weight = weights.get(metric_type, 0.1)
        normalized_score = min(100.0, metric.value / metric.threshold * 50)
        weighted_score += normalized_score * weight
        total_weight += weight
    return weighted_score / max(total_weight, 1.0)

def get_critical_issues(self) -> List[ComplexityMetric]:
    """Get metrics that are in critical state."""
    return [metric for metric in self.metrics.values() if metric.severity_level == 'critical']

def to_dict(self) -> Dict[str, Any]:
    """Convert report to dictionary."""
    return {'element_name': self.element_name, 'element_type': self.element_type, 'overall_score': self.get_overall_score(), 'metrics': {metric_type.value: {'value': metric.value, 'threshold': metric.threshold, 'exceeds_threshold': metric.exceeds_threshold, 'severity': metric.severity_level} for metric_type, metric in self.metrics.items()}, 'suggestions': self.suggestions, 'generated_at': self.generated_at.isoformat()}

@abstractmethod
def analyze(self, target: Any) -> ComplexityReport:
    """
        Analyze complexity of a target element.
        
        Args:
            target: Element to analyze (class, method, function, etc.)
            
        Returns:
            ComplexityReport: Complexity analysis report
        """
    pass

def __init__(self, threshold: float=10.0):
    self.threshold = threshold

def analyze(self, target: Any) -> ComplexityReport:
    """Analyze cyclomatic complexity."""
    report = ComplexityReport(element_name=self._get_element_name(target), element_type=self._get_element_type(target))
    try:
        complexity = self._calculate_cyclomatic_complexity(target)
        metric = ComplexityMetric(metric_type=ComplexityType.CYCLOMATIC, value=complexity, threshold=self.threshold, description=f'Cyclomatic complexity: {complexity}')
        report.add_metric(metric)
        if complexity > self.threshold:
            report.suggestions.extend(self._get_cyclomatic_suggestions(complexity))
    except Exception as e:
        logger.error(f'Error calculating cyclomatic complexity: {e}')
    return report

def _calculate_cyclomatic_complexity(self, target: Any) -> float:
    """Calculate cyclomatic complexity for a target."""
    if inspect.ismethod(target) or inspect.isfunction(target):
        return self._analyze_function_complexity(target)
    elif inspect.isclass(target):
        return self._analyze_class_complexity(target)
    else:
        return 1.0

def _analyze_function_complexity(self, func: Any) -> float:
    """Analyze complexity of a function."""
    try:
        source = inspect.getsource(func)
        tree = ast.parse(source)
        complexity = 1
        for node in ast.walk(tree):
            if isinstance(node, (ast.If, ast.While, ast.For, ast.AsyncFor)):
                complexity += 1
            elif isinstance(node, ast.ExceptHandler):
                complexity += 1
            elif isinstance(node, ast.BoolOp):
                complexity += len(node.values) - 1
        return float(complexity)
    except Exception as e:
        logger.warning(f'Could not analyze function complexity: {e}')
        return 1.0

def _analyze_class_complexity(self, cls: Type) -> float:
    """Analyze complexity of a class."""
    total_complexity = 0.0
    method_count = 0
    for name, method in inspect.getmembers(cls, predicate=inspect.isfunction):
        if not name.startswith('_'):
            total_complexity += self._analyze_function_complexity(method)
            method_count += 1
    return total_complexity / max(method_count, 1)

def _get_cyclomatic_suggestions(self, complexity: float) -> List[str]:
    """Get suggestions for reducing cyclomatic complexity."""
    suggestions = []
    if complexity > 15:
        suggestions.append('Consider breaking this method into smaller methods')
        suggestions.append('Extract complex conditional logic into separate methods')
    if complexity > 20:
        suggestions.append('This method is very complex - consider redesigning the algorithm')
        suggestions.append('Use strategy pattern to handle different cases')
    return suggestions

def _get_element_name(self, target: Any) -> str:
    """Get name of the target element."""
    if hasattr(target, '__name__'):
        return target.__name__
    elif hasattr(target, '__class__'):
        return target.__class__.__name__
    else:
        return str(target)

def _get_element_type(self, target: Any) -> str:
    """Get type of the target element."""
    if inspect.isclass(target):
        return 'class'
    elif inspect.ismethod(target) or inspect.isfunction(target):
        return 'method'
    else:
        return 'unknown'

def __init__(self, threshold: float=15.0):
    self.threshold = threshold

def analyze(self, target: Any) -> ComplexityReport:
    """Analyze cognitive complexity."""
    report = ComplexityReport(element_name=self._get_element_name(target), element_type=self._get_element_type(target))
    try:
        complexity = self._calculate_cognitive_complexity(target)
        metric = ComplexityMetric(metric_type=ComplexityType.COGNITIVE, value=complexity, threshold=self.threshold, description=f'Cognitive complexity: {complexity}')
        report.add_metric(metric)
        if complexity > self.threshold:
            report.suggestions.extend(self._get_cognitive_suggestions(complexity))
    except Exception as e:
        logger.error(f'Error calculating cognitive complexity: {e}')
    return report

def _calculate_cognitive_complexity(self, target: Any) -> float:
    """Calculate cognitive complexity for a target."""
    if inspect.ismethod(target) or inspect.isfunction(target):
        return self._analyze_function_cognitive_complexity(target)
    elif inspect.isclass(target):
        return self._analyze_class_cognitive_complexity(target)
    else:
        return 0.0

def _analyze_function_cognitive_complexity(self, func: Any) -> float:
    """Analyze cognitive complexity of a function."""
    try:
        source = inspect.getsource(func)
        tree = ast.parse(source)
        complexity = 0
        nesting_level = 0

        class CognitiveVisitor(ast.NodeVisitor):

            def __init__(self):
                self.complexity = 0
                self.nesting_level = 0

            def visit_If(self, node):
                self.complexity += 1 + self.nesting_level
                self.nesting_level += 1
                self.generic_visit(node)
                self.nesting_level -= 1

            def visit_While(self, node):
                self.complexity += 1 + self.nesting_level
                self.nesting_level += 1
                self.generic_visit(node)
                self.nesting_level -= 1

            def visit_For(self, node):
                self.complexity += 1 + self.nesting_level
                self.nesting_level += 1
                self.generic_visit(node)
                self.nesting_level -= 1

            def visit_ExceptHandler(self, node):
                self.complexity += 1 + self.nesting_level
                self.nesting_level += 1
                self.generic_visit(node)
                self.nesting_level -= 1

            def visit_BoolOp(self, node):
                self.complexity += len(node.values) - 1
                self.generic_visit(node)
        visitor = CognitiveVisitor()
        visitor.visit(tree)
        return float(visitor.complexity)
    except Exception as e:
        logger.warning(f'Could not analyze cognitive complexity: {e}')
        return 0.0

def _analyze_class_cognitive_complexity(self, cls: Type) -> float:
    """Analyze cognitive complexity of a class."""
    total_complexity = 0.0
    method_count = 0
    for name, method in inspect.getmembers(cls, predicate=inspect.isfunction):
        if not name.startswith('_'):
            total_complexity += self._analyze_function_cognitive_complexity(method)
            method_count += 1
    return total_complexity / max(method_count, 1)

def _get_cognitive_suggestions(self, complexity: float) -> List[str]:
    """Get suggestions for reducing cognitive complexity."""
    suggestions = []
    if complexity > 20:
        suggestions.append('Reduce nesting levels by extracting methods')
        suggestions.append('Simplify boolean expressions')
        suggestions.append('Use early returns to reduce nesting')
    if complexity > 30:
        suggestions.append('This code is very difficult to understand')
        suggestions.append('Consider complete refactoring with simpler logic')
    return suggestions

def _get_element_name(self, target: Any) -> str:
    """Get name of the target element."""
    if hasattr(target, '__name__'):
        return target.__name__
    elif hasattr(target, '__class__'):
        return target.__class__.__name__
    else:
        return str(target)

def _get_element_type(self, target: Any) -> str:
    """Get type of the target element."""
    if inspect.isclass(target):
        return 'class'
    elif inspect.ismethod(target) or inspect.isfunction(target):
        return 'method'
    else:
        return 'unknown'

def __init__(self, domain_context: str='complexity_monitoring'):
    super().__init__(domain_context)
    self._analyzers: Dict[ComplexityType, ComplexityAnalyzer] = {}
    self._reports: Dict[str, ComplexityReport] = {}
    self._thresholds: Dict[ComplexityType, float] = {}
    self._initialize_default_analyzers()

def _initialize_default_analyzers(self):
    """Initialize default complexity analyzers."""
    self._analyzers[ComplexityType.CYCLOMATIC] = CyclomaticComplexityAnalyzer()
    self._analyzers[ComplexityType.COGNITIVE] = CognitiveComplexityAnalyzer()
    self._thresholds = {ComplexityType.CYCLOMATIC: 10.0, ComplexityType.COGNITIVE: 15.0, ComplexityType.LINES_OF_CODE: 50.0, ComplexityType.METHOD_COUNT: 20.0, ComplexityType.PARAMETER_COUNT: 5.0}

def add_analyzer(self, complexity_type: ComplexityType, analyzer: ComplexityAnalyzer):
    """Add a complexity analyzer."""
    self._analyzers[complexity_type] = analyzer
    logger.debug(f'Added complexity analyzer for {complexity_type.value}')

def set_threshold(self, complexity_type: ComplexityType, threshold: float):
    """Set threshold for a complexity type."""
    self._thresholds[complexity_type] = threshold
    logger.debug(f'Set threshold for {complexity_type.value}: {threshold}')

def analyze_element(self, target: Any, element_name: Optional[str]=None) -> ComplexityReport:
    """
        Analyze complexity of a single element.
        
        Args:
            target: Element to analyze
            element_name: Optional name for the element
            
        Returns:
            ComplexityReport: Comprehensive complexity report
        """
    if element_name is None:
        element_name = self._get_element_name(target)
    combined_report = ComplexityReport(element_name=element_name, element_type=self._get_element_type(target))
    for complexity_type, analyzer in self._analyzers.items():
        try:
            report = analyzer.analyze(target)
            for metric_type, metric in report.metrics.items():
                combined_report.add_metric(metric)
            combined_report.suggestions.extend(report.suggestions)
        except Exception as e:
            logger.error(f'Error running {complexity_type.value} analyzer: {e}')
    self._add_basic_metrics(target, combined_report)
    self._reports[element_name] = combined_report
    return combined_report

def _add_basic_metrics(self, target: Any, report: ComplexityReport):
    """Add basic complexity metrics."""
    try:
        if inspect.isclass(target) or inspect.isfunction(target):
            source = inspect.getsource(target)
            loc = len([line for line in source.split('\n') if line.strip()])
            metric = ComplexityMetric(metric_type=ComplexityType.LINES_OF_CODE, value=float(loc), threshold=self._thresholds.get(ComplexityType.LINES_OF_CODE, 50.0), description=f'Lines of code: {loc}')
            report.add_metric(metric)
        if inspect.isclass(target):
            method_count = len([m for m in inspect.getmembers(target, predicate=inspect.isfunction) if not m[0].startswith('_')])
            metric = ComplexityMetric(metric_type=ComplexityType.METHOD_COUNT, value=float(method_count), threshold=self._thresholds.get(ComplexityType.METHOD_COUNT, 20.0), description=f'Method count: {method_count}')
            report.add_metric(metric)
    except Exception as e:
        logger.warning(f'Could not add basic metrics: {e}')

def get_complexity_summary(self) -> Dict[str, Any]:
    """Get summary of all complexity reports."""
    if not self._reports:
        return {'total_elements': 0, 'reports': []}
    critical_elements = []
    high_complexity_elements = []
    for element_name, report in self._reports.items():
        overall_score = report.get_overall_score()
        critical_issues = report.get_critical_issues()
        if critical_issues:
            critical_elements.append({'name': element_name, 'score': overall_score, 'critical_issues': len(critical_issues)})
        elif overall_score > 70:
            high_complexity_elements.append({'name': element_name, 'score': overall_score})
    return {'total_elements': len(self._reports), 'critical_elements': critical_elements, 'high_complexity_elements': high_complexity_elements, 'average_score': sum((r.get_overall_score() for r in self._reports.values())) / len(self._reports), 'thresholds': {t.value: threshold for t, threshold in self._thresholds.items()}}

def _get_element_name(self, target: Any) -> str:
    """Get name of the target element."""
    if hasattr(target, '__name__'):
        return target.__name__
    elif hasattr(target, '__class__'):
        return target.__class__.__name__
    else:
        return str(target)

def _get_element_type(self, target: Any) -> str:
    """Get type of the target element."""
    if inspect.isclass(target):
        return 'class'
    elif inspect.ismethod(target) or inspect.isfunction(target):
        return 'method'
    else:
        return 'unknown'

def get_domain_boundaries(self):
    """Get domain boundaries."""
    from ..models import DomainBoundaries
    return DomainBoundaries(context=self.domain_context, invariants=['Complexity metrics must be within acceptable thresholds', 'Critical complexity issues must be addressed', 'Complexity trends should be monitored over time'])

def __init__(self):
    self.complexity = 0
    self.nesting_level = 0

def visit_If(self, node):
    self.complexity += 1 + self.nesting_level
    self.nesting_level += 1
    self.generic_visit(node)
    self.nesting_level -= 1

def visit_While(self, node):
    self.complexity += 1 + self.nesting_level
    self.nesting_level += 1
    self.generic_visit(node)
    self.nesting_level -= 1

def visit_For(self, node):
    self.complexity += 1 + self.nesting_level
    self.nesting_level += 1
    self.generic_visit(node)
    self.nesting_level -= 1

def visit_ExceptHandler(self, node):
    self.complexity += 1 + self.nesting_level
    self.nesting_level += 1
    self.generic_visit(node)
    self.nesting_level -= 1

def visit_BoolOp(self, node):
    self.complexity += len(node.values) - 1
    self.generic_visit(node)

def __init__(self):
    self.complexity = 0
    self.nesting_level = 0

def visit_If(self, node):
    self.complexity += 1 + self.nesting_level
    self.nesting_level += 1
    self.generic_visit(node)
    self.nesting_level -= 1

def visit_While(self, node):
    self.complexity += 1 + self.nesting_level
    self.nesting_level += 1
    self.generic_visit(node)
    self.nesting_level -= 1

def visit_For(self, node):
    self.complexity += 1 + self.nesting_level
    self.nesting_level += 1
    self.generic_visit(node)
    self.nesting_level -= 1

def visit_ExceptHandler(self, node):
    self.complexity += 1 + self.nesting_level
    self.nesting_level += 1
    self.generic_visit(node)
    self.nesting_level -= 1

def visit_BoolOp(self, node):
    self.complexity += len(node.values) - 1
    self.generic_visit(node)

def __init__(self):
    self.complexity = 0
    self.nesting_level = 0

def visit_If(self, node):
    self.complexity += 1 + self.nesting_level
    self.nesting_level += 1
    self.generic_visit(node)
    self.nesting_level -= 1

def visit_While(self, node):
    self.complexity += 1 + self.nesting_level
    self.nesting_level += 1
    self.generic_visit(node)
    self.nesting_level -= 1

def visit_For(self, node):
    self.complexity += 1 + self.nesting_level
    self.nesting_level += 1
    self.generic_visit(node)
    self.nesting_level -= 1

def visit_ExceptHandler(self, node):
    self.complexity += 1 + self.nesting_level
    self.nesting_level += 1
    self.generic_visit(node)
    self.nesting_level -= 1

def visit_BoolOp(self, node):
    self.complexity += len(node.values) - 1
    self.generic_visit(node)

@property
def exceeds_threshold(self) -> bool:
    """Check if metric exceeds its threshold."""
    return self.value > self.threshold

@property
def severity_level(self) -> str:
    """Get severity level based on threshold exceedance."""
    if self.value <= self.threshold:
        return 'acceptable'
    elif self.value <= self.threshold * 1.5:
        return 'warning'
    elif self.value <= self.threshold * 2.0:
        return 'high'
    else:
        return 'critical'

def add_metric(self, metric: ComplexityMetric):
    """Add a complexity metric to the report."""
    self.metrics[metric.metric_type] = metric

def get_overall_score(self) -> float:
    """Calculate overall complexity score (0-100)."""
    if not self.metrics:
        return 0.0
    weights = {ComplexityType.CYCLOMATIC: 0.3, ComplexityType.COGNITIVE: 0.4, ComplexityType.MAINTAINABILITY: 0.2, ComplexityType.LINES_OF_CODE: 0.1}
    weighted_score = 0.0
    total_weight = 0.0
    for metric_type, metric in self.metrics.items():
        weight = weights.get(metric_type, 0.1)
        normalized_score = min(100.0, metric.value / metric.threshold * 50)
        weighted_score += normalized_score * weight
        total_weight += weight
    return weighted_score / max(total_weight, 1.0)

def get_critical_issues(self) -> List[ComplexityMetric]:
    """Get metrics that are in critical state."""
    return [metric for metric in self.metrics.values() if metric.severity_level == 'critical']

def to_dict(self) -> Dict[str, Any]:
    """Convert report to dictionary."""
    return {'element_name': self.element_name, 'element_type': self.element_type, 'overall_score': self.get_overall_score(), 'metrics': {metric_type.value: {'value': metric.value, 'threshold': metric.threshold, 'exceeds_threshold': metric.exceeds_threshold, 'severity': metric.severity_level} for metric_type, metric in self.metrics.items()}, 'suggestions': self.suggestions, 'generated_at': self.generated_at.isoformat()}

@abstractmethod
def analyze(self, target: Any) -> ComplexityReport:
    """
        Analyze complexity of a target element.
        
        Args:
            target: Element to analyze (class, method, function, etc.)
            
        Returns:
            ComplexityReport: Complexity analysis report
        """
    pass

def __init__(self, threshold: float=10.0):
    self.threshold = threshold

def analyze(self, target: Any) -> ComplexityReport:
    """Analyze cyclomatic complexity."""
    report = ComplexityReport(element_name=self._get_element_name(target), element_type=self._get_element_type(target))
    try:
        complexity = self._calculate_cyclomatic_complexity(target)
        metric = ComplexityMetric(metric_type=ComplexityType.CYCLOMATIC, value=complexity, threshold=self.threshold, description=f'Cyclomatic complexity: {complexity}')
        report.add_metric(metric)
        if complexity > self.threshold:
            report.suggestions.extend(self._get_cyclomatic_suggestions(complexity))
    except Exception as e:
        logger.error(f'Error calculating cyclomatic complexity: {e}')
    return report

def _calculate_cyclomatic_complexity(self, target: Any) -> float:
    """Calculate cyclomatic complexity for a target."""
    if inspect.ismethod(target) or inspect.isfunction(target):
        return self._analyze_function_complexity(target)
    elif inspect.isclass(target):
        return self._analyze_class_complexity(target)
    else:
        return 1.0

def _analyze_function_complexity(self, func: Any) -> float:
    """Analyze complexity of a function."""
    try:
        source = inspect.getsource(func)
        tree = ast.parse(source)
        complexity = 1
        for node in ast.walk(tree):
            if isinstance(node, (ast.If, ast.While, ast.For, ast.AsyncFor)):
                complexity += 1
            elif isinstance(node, ast.ExceptHandler):
                complexity += 1
            elif isinstance(node, ast.BoolOp):
                complexity += len(node.values) - 1
        return float(complexity)
    except Exception as e:
        logger.warning(f'Could not analyze function complexity: {e}')
        return 1.0

def _analyze_class_complexity(self, cls: Type) -> float:
    """Analyze complexity of a class."""
    total_complexity = 0.0
    method_count = 0
    for name, method in inspect.getmembers(cls, predicate=inspect.isfunction):
        if not name.startswith('_'):
            total_complexity += self._analyze_function_complexity(method)
            method_count += 1
    return total_complexity / max(method_count, 1)

def _get_cyclomatic_suggestions(self, complexity: float) -> List[str]:
    """Get suggestions for reducing cyclomatic complexity."""
    suggestions = []
    if complexity > 15:
        suggestions.append('Consider breaking this method into smaller methods')
        suggestions.append('Extract complex conditional logic into separate methods')
    if complexity > 20:
        suggestions.append('This method is very complex - consider redesigning the algorithm')
        suggestions.append('Use strategy pattern to handle different cases')
    return suggestions

def _get_element_name(self, target: Any) -> str:
    """Get name of the target element."""
    if hasattr(target, '__name__'):
        return target.__name__
    elif hasattr(target, '__class__'):
        return target.__class__.__name__
    else:
        return str(target)

def _get_element_type(self, target: Any) -> str:
    """Get type of the target element."""
    if inspect.isclass(target):
        return 'class'
    elif inspect.ismethod(target) or inspect.isfunction(target):
        return 'method'
    else:
        return 'unknown'

def __init__(self, threshold: float=15.0):
    self.threshold = threshold

def analyze(self, target: Any) -> ComplexityReport:
    """Analyze cognitive complexity."""
    report = ComplexityReport(element_name=self._get_element_name(target), element_type=self._get_element_type(target))
    try:
        complexity = self._calculate_cognitive_complexity(target)
        metric = ComplexityMetric(metric_type=ComplexityType.COGNITIVE, value=complexity, threshold=self.threshold, description=f'Cognitive complexity: {complexity}')
        report.add_metric(metric)
        if complexity > self.threshold:
            report.suggestions.extend(self._get_cognitive_suggestions(complexity))
    except Exception as e:
        logger.error(f'Error calculating cognitive complexity: {e}')
    return report

def _calculate_cognitive_complexity(self, target: Any) -> float:
    """Calculate cognitive complexity for a target."""
    if inspect.ismethod(target) or inspect.isfunction(target):
        return self._analyze_function_cognitive_complexity(target)
    elif inspect.isclass(target):
        return self._analyze_class_cognitive_complexity(target)
    else:
        return 0.0

def _analyze_function_cognitive_complexity(self, func: Any) -> float:
    """Analyze cognitive complexity of a function."""
    try:
        source = inspect.getsource(func)
        tree = ast.parse(source)
        complexity = 0
        nesting_level = 0

        class CognitiveVisitor(ast.NodeVisitor):

            def __init__(self):
                self.complexity = 0
                self.nesting_level = 0

            def visit_If(self, node):
                self.complexity += 1 + self.nesting_level
                self.nesting_level += 1
                self.generic_visit(node)
                self.nesting_level -= 1

            def visit_While(self, node):
                self.complexity += 1 + self.nesting_level
                self.nesting_level += 1
                self.generic_visit(node)
                self.nesting_level -= 1

            def visit_For(self, node):
                self.complexity += 1 + self.nesting_level
                self.nesting_level += 1
                self.generic_visit(node)
                self.nesting_level -= 1

            def visit_ExceptHandler(self, node):
                self.complexity += 1 + self.nesting_level
                self.nesting_level += 1
                self.generic_visit(node)
                self.nesting_level -= 1

            def visit_BoolOp(self, node):
                self.complexity += len(node.values) - 1
                self.generic_visit(node)
        visitor = CognitiveVisitor()
        visitor.visit(tree)
        return float(visitor.complexity)
    except Exception as e:
        logger.warning(f'Could not analyze cognitive complexity: {e}')
        return 0.0

def _analyze_class_cognitive_complexity(self, cls: Type) -> float:
    """Analyze cognitive complexity of a class."""
    total_complexity = 0.0
    method_count = 0
    for name, method in inspect.getmembers(cls, predicate=inspect.isfunction):
        if not name.startswith('_'):
            total_complexity += self._analyze_function_cognitive_complexity(method)
            method_count += 1
    return total_complexity / max(method_count, 1)

def _get_cognitive_suggestions(self, complexity: float) -> List[str]:
    """Get suggestions for reducing cognitive complexity."""
    suggestions = []
    if complexity > 20:
        suggestions.append('Reduce nesting levels by extracting methods')
        suggestions.append('Simplify boolean expressions')
        suggestions.append('Use early returns to reduce nesting')
    if complexity > 30:
        suggestions.append('This code is very difficult to understand')
        suggestions.append('Consider complete refactoring with simpler logic')
    return suggestions

def _get_element_name(self, target: Any) -> str:
    """Get name of the target element."""
    if hasattr(target, '__name__'):
        return target.__name__
    elif hasattr(target, '__class__'):
        return target.__class__.__name__
    else:
        return str(target)

def _get_element_type(self, target: Any) -> str:
    """Get type of the target element."""
    if inspect.isclass(target):
        return 'class'
    elif inspect.ismethod(target) or inspect.isfunction(target):
        return 'method'
    else:
        return 'unknown'

def __init__(self, domain_context: str='complexity_monitoring'):
    super().__init__(domain_context)
    self._analyzers: Dict[ComplexityType, ComplexityAnalyzer] = {}
    self._reports: Dict[str, ComplexityReport] = {}
    self._thresholds: Dict[ComplexityType, float] = {}
    self._initialize_default_analyzers()

def _initialize_default_analyzers(self):
    """Initialize default complexity analyzers."""
    self._analyzers[ComplexityType.CYCLOMATIC] = CyclomaticComplexityAnalyzer()
    self._analyzers[ComplexityType.COGNITIVE] = CognitiveComplexityAnalyzer()
    self._thresholds = {ComplexityType.CYCLOMATIC: 10.0, ComplexityType.COGNITIVE: 15.0, ComplexityType.LINES_OF_CODE: 50.0, ComplexityType.METHOD_COUNT: 20.0, ComplexityType.PARAMETER_COUNT: 5.0}

def add_analyzer(self, complexity_type: ComplexityType, analyzer: ComplexityAnalyzer):
    """Add a complexity analyzer."""
    self._analyzers[complexity_type] = analyzer
    logger.debug(f'Added complexity analyzer for {complexity_type.value}')

def set_threshold(self, complexity_type: ComplexityType, threshold: float):
    """Set threshold for a complexity type."""
    self._thresholds[complexity_type] = threshold
    logger.debug(f'Set threshold for {complexity_type.value}: {threshold}')

def analyze_element(self, target: Any, element_name: Optional[str]=None) -> ComplexityReport:
    """
        Analyze complexity of a single element.
        
        Args:
            target: Element to analyze
            element_name: Optional name for the element
            
        Returns:
            ComplexityReport: Comprehensive complexity report
        """
    if element_name is None:
        element_name = self._get_element_name(target)
    combined_report = ComplexityReport(element_name=element_name, element_type=self._get_element_type(target))
    for complexity_type, analyzer in self._analyzers.items():
        try:
            report = analyzer.analyze(target)
            for metric_type, metric in report.metrics.items():
                combined_report.add_metric(metric)
            combined_report.suggestions.extend(report.suggestions)
        except Exception as e:
            logger.error(f'Error running {complexity_type.value} analyzer: {e}')
    self._add_basic_metrics(target, combined_report)
    self._reports[element_name] = combined_report
    return combined_report

def _add_basic_metrics(self, target: Any, report: ComplexityReport):
    """Add basic complexity metrics."""
    try:
        if inspect.isclass(target) or inspect.isfunction(target):
            source = inspect.getsource(target)
            loc = len([line for line in source.split('\n') if line.strip()])
            metric = ComplexityMetric(metric_type=ComplexityType.LINES_OF_CODE, value=float(loc), threshold=self._thresholds.get(ComplexityType.LINES_OF_CODE, 50.0), description=f'Lines of code: {loc}')
            report.add_metric(metric)
        if inspect.isclass(target):
            method_count = len([m for m in inspect.getmembers(target, predicate=inspect.isfunction) if not m[0].startswith('_')])
            metric = ComplexityMetric(metric_type=ComplexityType.METHOD_COUNT, value=float(method_count), threshold=self._thresholds.get(ComplexityType.METHOD_COUNT, 20.0), description=f'Method count: {method_count}')
            report.add_metric(metric)
    except Exception as e:
        logger.warning(f'Could not add basic metrics: {e}')

def get_complexity_summary(self) -> Dict[str, Any]:
    """Get summary of all complexity reports."""
    if not self._reports:
        return {'total_elements': 0, 'reports': []}
    critical_elements = []
    high_complexity_elements = []
    for element_name, report in self._reports.items():
        overall_score = report.get_overall_score()
        critical_issues = report.get_critical_issues()
        if critical_issues:
            critical_elements.append({'name': element_name, 'score': overall_score, 'critical_issues': len(critical_issues)})
        elif overall_score > 70:
            high_complexity_elements.append({'name': element_name, 'score': overall_score})
    return {'total_elements': len(self._reports), 'critical_elements': critical_elements, 'high_complexity_elements': high_complexity_elements, 'average_score': sum((r.get_overall_score() for r in self._reports.values())) / len(self._reports), 'thresholds': {t.value: threshold for t, threshold in self._thresholds.items()}}

def _get_element_name(self, target: Any) -> str:
    """Get name of the target element."""
    if hasattr(target, '__name__'):
        return target.__name__
    elif hasattr(target, '__class__'):
        return target.__class__.__name__
    else:
        return str(target)

def _get_element_type(self, target: Any) -> str:
    """Get type of the target element."""
    if inspect.isclass(target):
        return 'class'
    elif inspect.ismethod(target) or inspect.isfunction(target):
        return 'method'
    else:
        return 'unknown'

def get_domain_boundaries(self):
    """Get domain boundaries."""
    from ..models import DomainBoundaries
    return DomainBoundaries(context=self.domain_context, invariants=['Complexity metrics must be within acceptable thresholds', 'Critical complexity issues must be addressed', 'Complexity trends should be monitored over time'])

def __init__(self):
    self.complexity = 0
    self.nesting_level = 0

def visit_If(self, node):
    self.complexity += 1 + self.nesting_level
    self.nesting_level += 1
    self.generic_visit(node)
    self.nesting_level -= 1

def visit_While(self, node):
    self.complexity += 1 + self.nesting_level
    self.nesting_level += 1
    self.generic_visit(node)
    self.nesting_level -= 1

def visit_For(self, node):
    self.complexity += 1 + self.nesting_level
    self.nesting_level += 1
    self.generic_visit(node)
    self.nesting_level -= 1

def visit_ExceptHandler(self, node):
    self.complexity += 1 + self.nesting_level
    self.nesting_level += 1
    self.generic_visit(node)
    self.nesting_level -= 1

def visit_BoolOp(self, node):
    self.complexity += len(node.values) - 1
    self.generic_visit(node)

def __init__(self):
    self.complexity = 0
    self.nesting_level = 0

def visit_If(self, node):
    self.complexity += 1 + self.nesting_level
    self.nesting_level += 1
    self.generic_visit(node)
    self.nesting_level -= 1

def visit_While(self, node):
    self.complexity += 1 + self.nesting_level
    self.nesting_level += 1
    self.generic_visit(node)
    self.nesting_level -= 1

def visit_For(self, node):
    self.complexity += 1 + self.nesting_level
    self.nesting_level += 1
    self.generic_visit(node)
    self.nesting_level -= 1

def visit_ExceptHandler(self, node):
    self.complexity += 1 + self.nesting_level
    self.nesting_level += 1
    self.generic_visit(node)
    self.nesting_level -= 1

def visit_BoolOp(self, node):
    self.complexity += len(node.values) - 1
    self.generic_visit(node)

def __init__(self):
    self.complexity = 0
    self.nesting_level = 0

def visit_If(self, node):
    self.complexity += 1 + self.nesting_level
    self.nesting_level += 1
    self.generic_visit(node)
    self.nesting_level -= 1

def visit_While(self, node):
    self.complexity += 1 + self.nesting_level
    self.nesting_level += 1
    self.generic_visit(node)
    self.nesting_level -= 1

def visit_For(self, node):
    self.complexity += 1 + self.nesting_level
    self.nesting_level += 1
    self.generic_visit(node)
    self.nesting_level -= 1

def visit_ExceptHandler(self, node):
    self.complexity += 1 + self.nesting_level
    self.nesting_level += 1
    self.generic_visit(node)
    self.nesting_level -= 1

def visit_BoolOp(self, node):
    self.complexity += len(node.values) - 1
    self.generic_visit(node)

def __init__(self):
    self.complexity = 0
    self.nesting_level = 0

def visit_If(self, node):
    self.complexity += 1 + self.nesting_level
    self.nesting_level += 1
    self.generic_visit(node)
    self.nesting_level -= 1

def visit_While(self, node):
    self.complexity += 1 + self.nesting_level
    self.nesting_level += 1
    self.generic_visit(node)
    self.nesting_level -= 1

def visit_For(self, node):
    self.complexity += 1 + self.nesting_level
    self.nesting_level += 1
    self.generic_visit(node)
    self.nesting_level -= 1

def visit_ExceptHandler(self, node):
    self.complexity += 1 + self.nesting_level
    self.nesting_level += 1
    self.generic_visit(node)
    self.nesting_level -= 1

def visit_BoolOp(self, node):
    self.complexity += len(node.values) - 1
    self.generic_visit(node)

def __init__(self):
    self.complexity = 0
    self.nesting_level = 0

def visit_If(self, node):
    self.complexity += 1 + self.nesting_level
    self.nesting_level += 1
    self.generic_visit(node)
    self.nesting_level -= 1

def visit_While(self, node):
    self.complexity += 1 + self.nesting_level
    self.nesting_level += 1
    self.generic_visit(node)
    self.nesting_level -= 1

def visit_For(self, node):
    self.complexity += 1 + self.nesting_level
    self.nesting_level += 1
    self.generic_visit(node)
    self.nesting_level -= 1

def visit_ExceptHandler(self, node):
    self.complexity += 1 + self.nesting_level
    self.nesting_level += 1
    self.generic_visit(node)
    self.nesting_level -= 1

def visit_BoolOp(self, node):
    self.complexity += len(node.values) - 1
    self.generic_visit(node)

def __init__(self):
    self.complexity = 0
    self.nesting_level = 0

def visit_If(self, node):
    self.complexity += 1 + self.nesting_level
    self.nesting_level += 1
    self.generic_visit(node)
    self.nesting_level -= 1

def visit_While(self, node):
    self.complexity += 1 + self.nesting_level
    self.nesting_level += 1
    self.generic_visit(node)
    self.nesting_level -= 1

def visit_For(self, node):
    self.complexity += 1 + self.nesting_level
    self.nesting_level += 1
    self.generic_visit(node)
    self.nesting_level -= 1

def visit_ExceptHandler(self, node):
    self.complexity += 1 + self.nesting_level
    self.nesting_level += 1
    self.generic_visit(node)
    self.nesting_level -= 1

def visit_BoolOp(self, node):
    self.complexity += len(node.values) - 1
    self.generic_visit(node)
