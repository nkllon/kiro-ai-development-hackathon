#!/usr/bin/env python3
"""
RM-DDD Compliance Assessment Tool

Systematic analysis of DevPost integration modules for:
- Module size compliance (≤300 lines) - UPDATED for self-documentation
- RM interface compliance (ReflectiveModule inheritance)
- Health monitoring implementation
- Registry integration status
- PDCA convergence monitoring

Follows Requirements → Design → Implementation approach.
"""

import ast
import json
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger('RM-DDD-Assessment')


@dataclass
class ModuleSizeViolation:
    """Module size violation details"""
    module_name: str
    file_path: str
    line_count: int
    violation_multiplier: float
    severity: str  # critical, major, minor
    refactoring_priority: int


@dataclass
class PDCAConvergenceMetrics:
    """PDCA convergence tracking metrics"""
    iteration: int
    timestamp: str
    overall_compliance: float
    size_compliance: float
    improvement_rate: float
    convergence_status: str  # converging, diverging, stable
    stopping_criteria_met: bool


@dataclass
class RMInterfaceGap:
    """RM interface implementation gap"""
    module_name: str
    file_path: str
    missing_inheritance: bool
    missing_methods: List[str]
    compliance_score: float


@dataclass
class HealthMonitoringGap:
    """Health monitoring implementation gap"""
    module_name: str
    file_path: str
    missing_health_indicators: bool
    missing_status_reporting: bool
    missing_graceful_degradation: bool
    health_coverage_score: float


@dataclass
class ModuleAssessment:
    """Complete assessment of a single module"""
    module_name: str
    file_path: str
    line_count: int
    size_compliant: bool
    rm_interface_compliant: bool
    health_monitoring_compliant: bool
    registry_integrated: bool
    overall_compliance_score: float
    size_violation: Optional[ModuleSizeViolation]
    rm_gaps: List[RMInterfaceGap]
    health_gaps: List[HealthMonitoringGap]
    refactoring_priority: int


@dataclass
class ComplianceReport:
    """Overall compliance assessment report"""
    assessment_timestamp: datetime
    total_modules: int
    size_compliant_modules: int
    rm_interface_compliant_modules: int
    health_monitoring_compliant_modules: int
    registry_integrated_modules: int
    overall_compliance_score: float
    critical_violations: int
    major_violations: int
    minor_violations: int
    module_assessments: List[ModuleAssessment]
    recommendations: List[str]


class ModuleSizeAnalyzer:
    """Analyzes module size compliance"""
    
    def __init__(self, size_limit: int = 300):
        self.size_limit = size_limit
    
    def analyze_module(self, file_path: Path) -> Optional[ModuleSizeViolation]:
        """Analyze single module for size compliance"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            line_count = len(lines)
            
            if line_count <= self.size_limit:
                return None
            
            violation_multiplier = line_count / self.size_limit
            
            if violation_multiplier >= 5.0:
                severity = "critical"
            elif violation_multiplier >= 3.0:
                severity = "major"
            else:
                severity = "minor"
            
            return ModuleSizeViolation(
                module_name=file_path.stem,
                file_path=str(file_path),
                line_count=line_count,
                violation_multiplier=violation_multiplier,
                severity=severity,
                refactoring_priority=self._calculate_priority(violation_multiplier)
            )
            
        except Exception as e:
            logger.error(f"Error analyzing {file_path}: {e}")
            return None
    
    def _calculate_priority(self, violation_multiplier: float) -> int:
        """Calculate refactoring priority (1=highest)"""
        if violation_multiplier >= 5.0:
            return 1
        elif violation_multiplier >= 3.0:
            return 2
        elif violation_multiplier >= 2.0:
            return 3
        else:
            return 4


class PDCAConvergenceMonitor:
    """Monitors PDCA convergence to prevent infinite loops"""
    
    def __init__(self, convergence_file: str = "pdca_convergence.json"):
        self.convergence_file = Path(convergence_file)
        self.history: List[PDCAConvergenceMetrics] = []
        self.load_history()
    
    def load_history(self):
        """Load convergence history from file"""
        try:
            if self.convergence_file.exists():
                with open(self.convergence_file, 'r') as f:
                    data = json.load(f)
                    self.history = [PDCAConvergenceMetrics(**item) for item in data]
        except Exception as e:
            logger.warning(f"Could not load convergence history: {e}")
            self.history = []
    
    def save_history(self):
        """Save convergence history to file"""
        try:
            with open(self.convergence_file, 'w') as f:
                json.dump([asdict(metric) for metric in self.history], f, indent=2)
        except Exception as e:
            logger.error(f"Could not save convergence history: {e}")
    
    def record_iteration(self, overall_compliance: float, size_compliance: float) -> PDCAConvergenceMetrics:
        """Record current iteration metrics"""
        iteration = len(self.history) + 1
        timestamp = datetime.now().isoformat()
        
        # Calculate improvement rate
        if len(self.history) > 0:
            prev_compliance = self.history[-1].overall_compliance
            improvement_rate = overall_compliance - prev_compliance
        else:
            improvement_rate = 0.0
        
        # Determine convergence status
        convergence_status = self._determine_convergence_status(improvement_rate)
        
        # Check stopping criteria
        stopping_criteria_met = self._check_stopping_criteria(overall_compliance, improvement_rate, iteration)
        
        metrics = PDCAConvergenceMetrics(
            iteration=iteration,
            timestamp=timestamp,
            overall_compliance=overall_compliance,
            size_compliance=size_compliance,
            improvement_rate=improvement_rate,
            convergence_status=convergence_status,
            stopping_criteria_met=stopping_criteria_met
        )
        
        self.history.append(metrics)
        self.save_history()
        
        return metrics
    
    def _determine_convergence_status(self, improvement_rate: float) -> str:
        """Determine convergence status based on improvement rate"""
        if improvement_rate > 0.05:  # >5% improvement
            return "converging"
        elif improvement_rate < -0.01:  # <1% degradation
            return "diverging"
        else:
            return "stable"
    
    def _check_stopping_criteria(self, overall_compliance: float, improvement_rate: float, iteration: int) -> bool:
        """Check if stopping criteria are met"""
        # Stop if we've reached high compliance
        if overall_compliance >= 0.95:  # 95% compliance
            return True
        
        # Stop if improvement rate is too low for too long
        if iteration >= 10 and improvement_rate < 0.01:  # <1% improvement for 10+ iterations
            return True
        
        # Stop if we're diverging consistently
        if iteration >= 5 and improvement_rate < -0.01:  # Degrading for 5+ iterations
            return True
        
        return False
    
    def get_convergence_summary(self) -> Dict[str, Any]:
        """Get convergence summary"""
        if not self.history:
            return {"status": "no_history", "message": "No convergence data available"}
        
        latest = self.history[-1]
        
        return {
            "iteration": latest.iteration,
            "overall_compliance": latest.overall_compliance,
            "size_compliance": latest.size_compliance,
            "improvement_rate": latest.improvement_rate,
            "convergence_status": latest.convergence_status,
            "stopping_criteria_met": latest.stopping_criteria_met,
            "total_iterations": len(self.history),
            "average_improvement": sum(m.improvement_rate for m in self.history) / len(self.history)
        }


class RMComplianceAnalyzer:
    """Analyzes RM interface compliance"""
    
    REQUIRED_METHODS = [
        'get_module_info',
        'get_capabilities',
        'get_dependencies',
        'check_health',
        'get_configuration',
        'update_configuration',
        'get_metrics',
        'reset_metrics'
    ]
    
    def analyze_module(self, file_path: Path) -> RMInterfaceGap:
        """Analyze single module for RM interface compliance"""
        try:
            # Check if there's a corresponding _methods.py file
            methods_file = file_path.parent / f"{file_path.stem}_methods.py"
            if methods_file.exists():
                # Use the _methods.py file instead
                file_path = methods_file
                logger.info(f"Using {methods_file} for RM interface analysis")
            
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            tree = ast.parse(content)
            
            # Check for ReflectiveModule inheritance
            missing_inheritance = not self._has_reflective_module_inheritance(tree)
            
            # Check for required methods
            missing_methods = self._find_missing_methods(tree)
            
            # Calculate compliance score
            compliance_score = self._calculate_compliance_score(missing_inheritance, missing_methods)
            
            return RMInterfaceGap(
                module_name=file_path.stem,
                file_path=str(file_path),
                missing_inheritance=missing_inheritance,
                missing_methods=missing_methods,
                compliance_score=compliance_score
            )
            
        except Exception as e:
            logger.error(f"Error analyzing RM compliance for {file_path}: {e}")
            return RMInterfaceGap(
                module_name=file_path.stem,
                file_path=str(file_path),
                missing_inheritance=True,
                missing_methods=self.REQUIRED_METHODS,
                compliance_score=0.0
            )
    
    def _has_reflective_module_inheritance(self, tree: ast.AST) -> bool:
        """Check if module inherits from ReflectiveModule"""
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                for base in node.bases:
                    if isinstance(base, ast.Name) and base.id == 'ReflectiveModule':
                        return True
                    elif isinstance(base, ast.Attribute):
                        if base.attr == 'ReflectiveModule':
                            return True
        return False
    
    def _find_missing_methods(self, tree: ast.AST) -> List[str]:
        """Find missing required methods"""
        implemented_methods = set()
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                implemented_methods.add(node.name)
        
        return [method for method in self.REQUIRED_METHODS if method not in implemented_methods]
    
    def _calculate_compliance_score(self, missing_inheritance: bool, missing_methods: List[str]) -> float:
        """Calculate RM interface compliance score"""
        if missing_inheritance:
            return 0.0
        
        method_score = (len(self.REQUIRED_METHODS) - len(missing_methods)) / len(self.REQUIRED_METHODS)
        return method_score * 100.0


class HealthMonitoringAnalyzer:
    """Analyzes health monitoring implementation"""
    
    def analyze_module(self, file_path: Path) -> HealthMonitoringGap:
        """Analyze single module for health monitoring capabilities"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check for health monitoring patterns
            missing_health_indicators = not self._has_health_indicators(content)
            missing_status_reporting = not self._has_status_reporting(content)
            missing_graceful_degradation = not self._has_graceful_degradation(content)
            
            # Calculate health coverage score
            health_coverage_score = self._calculate_health_coverage_score(
                missing_health_indicators, missing_status_reporting, missing_graceful_degradation
            )
            
            return HealthMonitoringGap(
                module_name=file_path.stem,
                file_path=str(file_path),
                missing_health_indicators=missing_health_indicators,
                missing_status_reporting=missing_status_reporting,
                missing_graceful_degradation=missing_graceful_degradation,
                health_coverage_score=health_coverage_score
            )
            
        except Exception as e:
            logger.error(f"Error analyzing health monitoring for {file_path}: {e}")
            return HealthMonitoringGap(
                module_name=file_path.stem,
                file_path=str(file_path),
                missing_health_indicators=True,
                missing_status_reporting=True,
                missing_graceful_degradation=True,
                health_coverage_score=0.0
            )
    
    def _has_health_indicators(self, content: str) -> bool:
        """Check if module has health indicators"""
        health_patterns = [
            'check_health',
            'ModuleHealth',
            'uptime_seconds',
            'success_rate',
            'error_rate',
            'health_status'
        ]
        return any(pattern in content for pattern in health_patterns)
    
    def _has_status_reporting(self, content: str) -> bool:
        """Check if module has status reporting"""
        status_patterns = [
            'get_metrics',
            'total_operations',
            'success_count',
            'error_count',
            'last_updated'
        ]
        return any(pattern in content for pattern in status_patterns)
    
    def _has_graceful_degradation(self, content: str) -> bool:
        """Check if module has graceful degradation"""
        degradation_patterns = [
            'try:',
            'except Exception',
            'error_handling',
            'logger.error',
            'return ModuleHealth.UNHEALTHY'
        ]
        return any(pattern in content for pattern in degradation_patterns)
    
    def _calculate_health_coverage_score(self, missing_indicators: bool, missing_status: bool, missing_degradation: bool) -> float:
        """Calculate health monitoring coverage score"""
        total_checks = 3
        passed_checks = sum([not missing_indicators, not missing_status, not missing_degradation])
        return (passed_checks / total_checks) * 100.0


class RMComplianceAssessmentTool:
    """Main assessment tool orchestrating all analyzers"""
    
    def __init__(self, devpost_path: str = "src/devpost_integration"):
        self.devpost_path = Path(devpost_path)
        self.size_analyzer = ModuleSizeAnalyzer()
        self.rm_analyzer = RMComplianceAnalyzer()
        self.health_analyzer = HealthMonitoringAnalyzer()
    
    def assess_all_modules(self) -> ComplianceReport:
        """Assess all DevPost integration modules"""
        logger.info("Starting RM-DDD compliance assessment...")
        
        # Find all Python modules
        python_files = list(self.devpost_path.glob("*.py"))
        logger.info(f"Found {len(python_files)} Python modules to assess")
        
        module_assessments = []
        
        for file_path in python_files:
            if file_path.name == "__init__.py":
                continue
                
            logger.info(f"Assessing {file_path.name}...")
            assessment = self._assess_single_module(file_path)
            module_assessments.append(assessment)
        
        # Generate overall report
        report = self._generate_compliance_report(module_assessments)
        
        logger.info(f"Assessment complete. Overall compliance: {report.overall_compliance_score:.1f}%")
        return report
    
    def _assess_single_module(self, file_path: Path) -> ModuleAssessment:
        """Assess a single module"""
        # Size analysis
        size_violation = self.size_analyzer.analyze_module(file_path)
        size_compliant = size_violation is None
        
        # RM interface analysis - skip for reflective_module.py (it's the base class)
        if file_path.name == "reflective_module.py":
            rm_compliant = True  # Base class doesn't need to inherit from itself
            rm_gap = None
        else:
            rm_gap = self.rm_analyzer.analyze_module(file_path)
            rm_compliant = rm_gap.compliance_score == 100.0
        
        # Health monitoring analysis - check _methods.py file if it exists
        health_file_path = file_path
        methods_file = file_path.parent / f"{file_path.stem}_methods.py"
        if methods_file.exists():
            health_file_path = methods_file
            logger.info(f"Using {health_file_path} for health monitoring analysis")
        
        health_gap = self.health_analyzer.analyze_module(health_file_path)
        health_compliant = health_gap.health_coverage_score == 100.0
        
        # Registry integration (simplified check)
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        registry_integrated = self._check_registry_integration(content)
        
        # Calculate overall compliance score
        compliance_scores = []
        if size_compliant:
            compliance_scores.append(100.0)
        else:
            compliance_scores.append(0.0)
        
        compliance_scores.append(rm_gap.compliance_score if rm_gap else 100.0)
        compliance_scores.append(health_gap.health_coverage_score)
        
        overall_compliance = sum(compliance_scores) / len(compliance_scores)
        
        # Calculate refactoring priority
        refactoring_priority = size_violation.refactoring_priority if size_violation else 999
        
        return ModuleAssessment(
            module_name=file_path.stem,
            file_path=str(file_path),
            line_count=size_violation.line_count if size_violation else 0,
            size_compliant=size_compliant,
            rm_interface_compliant=rm_compliant,
            health_monitoring_compliant=health_compliant,
            registry_integrated=registry_integrated,
            overall_compliance_score=overall_compliance,
            size_violation=size_violation,
            rm_gaps=[rm_gap] if rm_gap else [],
            health_gaps=[health_gap],
            refactoring_priority=refactoring_priority
        )
    
    def _check_registry_integration(self, content: str) -> bool:
        """Check if module has registry integration"""
        registry_patterns = [
            'register_module',
            'ReflectiveModuleRegistry',
            'from .reflective_module import.*register_module'
        ]
        return any(pattern in content for pattern in registry_patterns)
    
    def _generate_compliance_report(self, assessments: List[ModuleAssessment]) -> ComplianceReport:
        """Generate overall compliance report"""
        total_modules = len(assessments)
        size_compliant = sum(1 for a in assessments if a.size_compliant)
        rm_compliant = sum(1 for a in assessments if a.rm_interface_compliant)
        health_compliant = sum(1 for a in assessments if a.health_monitoring_compliant)
        registry_integrated = sum(1 for a in assessments if a.registry_integrated)
        
        # Count violations by severity
        critical_violations = sum(1 for a in assessments if a.size_violation and a.size_violation.severity == "critical")
        major_violations = sum(1 for a in assessments if a.size_violation and a.size_violation.severity == "major")
        minor_violations = sum(1 for a in assessments if a.size_violation and a.size_violation.severity == "minor")
        
        # Calculate overall compliance score
        overall_compliance = sum(a.overall_compliance_score for a in assessments) / len(assessments) if assessments else 0.0
        
        # Generate recommendations
        recommendations = self._generate_recommendations(assessments)
        
        return ComplianceReport(
            assessment_timestamp=datetime.now(),
            total_modules=total_modules,
            size_compliant_modules=size_compliant,
            rm_interface_compliant_modules=rm_compliant,
            health_monitoring_compliant_modules=health_compliant,
            registry_integrated_modules=registry_integrated,
            overall_compliance_score=overall_compliance,
            critical_violations=critical_violations,
            major_violations=major_violations,
            minor_violations=minor_violations,
            module_assessments=assessments,
            recommendations=recommendations
        )
    
    def _generate_recommendations(self, assessments: List[ModuleAssessment]) -> List[str]:
        """Generate recommendations based on assessment results"""
        recommendations = []
        
        # Size compliance recommendations
        oversized_modules = [a for a in assessments if not a.size_compliant]
        if oversized_modules:
            recommendations.append(f"Refactor {len(oversized_modules)} oversized modules to meet 200-line limit")
            critical_modules = [a for a in oversized_modules if a.size_violation and a.size_violation.severity == "critical"]
            if critical_modules:
                recommendations.append(f"Priority: Refactor {len(critical_modules)} critical size violations first")
        
        # RM interface recommendations
        non_rm_modules = [a for a in assessments if not a.rm_interface_compliant]
        if non_rm_modules:
            recommendations.append(f"Implement ReflectiveModule interface for {len(non_rm_modules)} modules")
        
        # Health monitoring recommendations
        non_health_modules = [a for a in assessments if not a.health_monitoring_compliant]
        if non_health_modules:
            recommendations.append(f"Implement health monitoring for {len(non_health_modules)} modules")
        
        # Registry integration recommendations
        non_registry_modules = [a for a in assessments if not a.registry_integrated]
        if non_registry_modules:
            recommendations.append(f"Integrate {len(non_registry_modules)} modules with RM registry")
        
        return recommendations
    
    def save_report(self, report: ComplianceReport, output_file: str = "rm_ddd_compliance_report.json"):
        """Save assessment report to file"""
        report_dict = asdict(report)
        # Convert datetime to string for JSON serialization
        report_dict['assessment_timestamp'] = report.assessment_timestamp.isoformat()
        
        with open(output_file, 'w') as f:
            json.dump(report_dict, f, indent=2)
        
        logger.info(f"Assessment report saved to {output_file}")
    
    def print_summary(self, report: ComplianceReport):
        """Print human-readable summary"""
        print("\n" + "="*80)
        print("RM-DDD COMPLIANCE ASSESSMENT SUMMARY")
        print("="*80)
        print(f"Assessment Time: {report.assessment_timestamp}")
        print(f"Total Modules: {report.total_modules}")
        print(f"Overall Compliance Score: {report.overall_compliance_score:.1f}%")
        print()
        
        print("COMPLIANCE BREAKDOWN:")
        print(f"  Size Compliant: {report.size_compliant_modules}/{report.total_modules} ({report.size_compliant_modules/report.total_modules*100:.1f}%)")
        print(f"  RM Interface Compliant: {report.rm_interface_compliant_modules}/{report.total_modules} ({report.rm_interface_compliant_modules/report.total_modules*100:.1f}%)")
        print(f"  Health Monitoring Compliant: {report.health_monitoring_compliant_modules}/{report.total_modules} ({report.health_monitoring_compliant_modules/report.total_modules*100:.1f}%)")
        print(f"  Registry Integrated: {report.registry_integrated_modules}/{report.total_modules} ({report.registry_integrated_modules/report.total_modules*100:.1f}%)")
        print()
        
        print("VIOLATION SUMMARY:")
        print(f"  Critical Violations: {report.critical_violations}")
        print(f"  Major Violations: {report.major_violations}")
        print(f"  Minor Violations: {report.minor_violations}")
        print()
        
        print("TOP PRIORITY MODULES FOR REFACTORING:")
        sorted_assessments = sorted(report.module_assessments, key=lambda x: x.refactoring_priority)
        for i, assessment in enumerate(sorted_assessments[:5], 1):
            if not assessment.size_compliant:
                print(f"  {i}. {assessment.module_name} ({assessment.line_count} lines, {assessment.size_violation.severity})")
        print()
        
        print("RECOMMENDATIONS:")
        for i, rec in enumerate(report.recommendations, 1):
            print(f"  {i}. {rec}")
        print("="*80)


def main():
    """Main function with PDCA convergence monitoring"""
    if len(sys.argv) > 1:
        devpost_path = sys.argv[1]
    else:
        devpost_path = "src/devpost_integration"
    
    # Create assessment tool
    tool = RMComplianceAssessmentTool(devpost_path)
    
    # Run assessment
    report = tool.assess_all_modules()
    
    # Initialize convergence monitor
    convergence_monitor = PDCAConvergenceMonitor()
    
    # Record iteration metrics
    convergence_metrics = convergence_monitor.record_iteration(
        overall_compliance=report.overall_compliance_score / 100.0,
        size_compliance=report.size_compliant_modules / report.total_modules
    )
    
    # Save report
    tool.save_report(report)
    
    # Print summary with convergence info
    tool.print_summary(report)
    
    # Print convergence status
    print("\n" + "="*80)
    print("PDCA CONVERGENCE MONITORING")
    print("="*80)
    print(f"Iteration: {convergence_metrics.iteration}")
    print(f"Overall Compliance: {convergence_metrics.overall_compliance:.1%}")
    print(f"Size Compliance: {convergence_metrics.size_compliance:.1%}")
    print(f"Improvement Rate: {convergence_metrics.improvement_rate:+.1%}")
    print(f"Convergence Status: {convergence_metrics.convergence_status}")
    print(f"Stopping Criteria Met: {convergence_metrics.stopping_criteria_met}")
    
    if convergence_metrics.stopping_criteria_met:
        print("\n🛑 STOPPING CRITERIA MET - PDCA LOOP SHOULD TERMINATE")
        print("Consider implementing RM interfaces and health monitoring instead.")
    
    # Exit with appropriate code
    if report.overall_compliance_score < 50.0:
        sys.exit(1)  # Critical compliance issues
    elif report.overall_compliance_score < 90.0:
        sys.exit(2)  # Compliance issues need attention
    else:
        sys.exit(0)  # Good compliance


if __name__ == "__main__":
    main()
