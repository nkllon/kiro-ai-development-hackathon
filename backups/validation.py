"""
Consistency Validator - Ensures terminology, interface, and pattern consistency

This module implements real-time validation of spec consistency to prevent
fragmentation and maintain architectural integrity.
"""

import json
import logging
import re
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Dict, List, Set, Optional, Tuple
from difflib import SequenceMatcher

from src.beast_mode.core.reflective_module import ReflectiveModule


class ConsistencyLevel(Enum):
    """Consistency level indicators"""
    EXCELLENT = "excellent"  # >95%
    GOOD = "good"           # 85-95%
    FAIR = "fair"           # 70-85%
    POOR = "poor"           # 50-70%
    CRITICAL = "critical"   # <50%


@dataclass
class TerminologyReport:
    """Report on terminology consistency"""
    consistent_terms: Set[str]
    inconsistent_terms: Dict[str, List[str]]  # term -> variations
    new_terms: Set[str]
    deprecated_terms: Set[str]
    consistency_score: float
    recommendations: List[str]


@dataclass
class ComplianceReport:
    """Report on interface compliance"""
    compliant_interfaces: List[str]
    non_compliant_interfaces: List[str]
    missing_methods: Dict[str, List[str]]  # interface -> missing methods
    compliance_score: float
    remediation_steps: List[str]


@dataclass
class PatternReport:
    """Report on design pattern consistency"""
    consistent_patterns: List[str]
    inconsistent_patterns: List[str]
    pattern_violations: Dict[str, str]  # pattern -> violation description
    pattern_score: float
    improvement_suggestions: List[str]


@dataclass
class ConsistencyMetrics:
    """Overall consistency metrics"""
    terminology_score: float
    interface_score: float
    pattern_score: float
    overall_score: float
    consistency_level: ConsistencyLevel
    critical_issues: List[str]
    improvement_priority: List[str]


class ConsistencyValidator(ReflectiveModule):
    """
    Ensures terminology, interface, and pattern consistency across all specs
    
    This validator implements real-time checking to prevent inconsistencies
    from being introduced during spec creation and modification.
    """
    
    def __init__(self, specs_directory: str = ".kiro/specs"):
        super().__init__("ConsistencyValidator")
        self.specs_directory = Path(specs_directory)
        self.logger = logging.getLogger(__name__)
        
        # Load unified registries
        self.terminology_registry = self._load_terminology_registry()
        self.interface_patterns = self._load_interface_patterns()
        self.design_patterns = self._load_design_patterns()
        
        # Consistency thresholds
        self.terminology_threshold = 0.85
        self.interface_threshold = 0.90
        self.pattern_threshold = 0.80
    
    def validate_terminology(self, spec_content: str) -> TerminologyReport:
        """
        Validate terminology consistency against unified vocabulary
        
        Checks for consistent usage of technical terms and identifies
        variations that could cause confusion.
        """
        try:
            # Extract terminology from spec content
            extracted_terms = self._extract_terminology_from_content(spec_content)
            
            consistent_terms = set()
            inconsistent_terms = {}
            new_terms = set()
            
            for term in extracted_terms:
                if term in self.terminology_registry:
                    # Check for variations
                    variations = self._find_term_variations(term, extracted_terms)
                    if variations:
                        inconsistent_terms[term] = variations
                    else:
                        consistent_terms.add(term)
                else:
                    # Check if it's a variation of existing term
                    canonical_term = self._find_canonical_term(term)
                    if canonical_term:
                        if canonical_term not in inconsistent_terms:
                            inconsistent_terms[canonical_term] = []
                        inconsistent_terms[canonical_term].append(term)
                    else:
                        new_terms.add(term)
            
            # Calculate consistency score
            total_terms = len(extracted_terms)
            consistent_count = len(consistent_terms)
            consistency_score = consistent_count / total_terms if total_terms > 0 else 1.0
            
            # Generate recommendations
            recommendations = self._generate_terminology_recommendations(
                inconsistent_terms, new_terms
            )
            
            return TerminologyReport(
                consistent_terms=consistent_terms,
                inconsistent_terms=inconsistent_terms,
                new_terms=new_terms,
                deprecated_terms=set(),  # TODO: Implement deprecated term detection
                consistency_score=consistency_score,
                recommendations=recommendations
            )
            
        except Exception as e:
            self.logger.error(f"Error validating terminology: {e}")
            return TerminologyReport(
                consistent_terms=set(),
                inconsistent_terms={},
                new_terms=set(),
                deprecated_terms=set(),
                consistency_score=0.0,
                recommendations=[f"Error during validation: {e}"]
            )
    
    def check_interface_compliance(self, interface_def: str) -> ComplianceReport:
        """
        Check interface compliance with standard patterns
        
        Validates that interfaces follow ReflectiveModule patterns and
        other established interface standards.
        """
        try:
            # Extract interface definitions
            interfaces = self._extract_interfaces_from_definition(interface_def)
            
            compliant_interfaces = []
            non_compliant_interfaces = []
            missing_methods = {}
            
            for interface_name, methods in interfaces.items():
                compliance_result = self._check_single_interface_compliance(
                    interface_name, methods
                )
                
                if compliance_result['compliant']:
                    compliant_interfaces.append(interface_name)
                else:
                    non_compliant_interfaces.append(interface_name)
                    if compliance_result['missing_methods']:
                        missing_methods[interface_name] = compliance_result['missing_methods']
            
            # Calculate compliance score
            total_interfaces = len(interfaces)
            compliant_count = len(compliant_interfaces)
            compliance_score = compliant_count / total_interfaces if total_interfaces > 0 else 1.0
            
            # Generate remediation steps
            remediation_steps = self._generate_interface_remediation_steps(
                non_compliant_interfaces, missing_methods
            )
            
            return ComplianceReport(
                compliant_interfaces=compliant_interfaces,
                non_compliant_interfaces=non_compliant_interfaces,
                missing_methods=missing_methods,
                compliance_score=compliance_score,
                remediation_steps=remediation_steps
            )
            
        except Exception as e:
            self.logger.error(f"Error checking interface compliance: {e}")
            return ComplianceReport(
                compliant_interfaces=[],
                non_compliant_interfaces=[],
                missing_methods={},
                compliance_score=0.0,
                remediation_steps=[f"Error during compliance check: {e}"]
            )
    
    def validate_pattern_consistency(self, design_patterns: List[str]) -> PatternReport:
        """
        Validate design pattern consistency across specifications
        
        Ensures that design patterns are used consistently and follow
        established architectural guidelines.
        """
        try:
            consistent_patterns = []
            inconsistent_patterns = []
            pattern_violations = {}
            
            for pattern in design_patterns:
                consistency_check = self._check_pattern_consistency(pattern)
                
                if consistency_check['consistent']:
                    consistent_patterns.append(pattern)
                else:
                    inconsistent_patterns.append(pattern)
                    pattern_violations[pattern] = consistency_check['violation_description']
            
            # Calculate pattern score
            total_patterns = len(design_patterns)
            consistent_count = len(consistent_patterns)
            pattern_score = consistent_count / total_patterns if total_patterns > 0 else 1.0
            
            # Generate improvement suggestions
            improvement_suggestions = self._generate_pattern_improvement_suggestions(
                inconsistent_patterns, pattern_violations
            )
            
            return PatternReport(
                consistent_patterns=consistent_patterns,
                inconsistent_patterns=inconsistent_patterns,
                pattern_violations=pattern_violations,
                pattern_score=pattern_score,
                improvement_suggestions=improvement_suggestions
            )
            
        except Exception as e:
            self.logger.error(f"Error validating pattern consistency: {e}")
            return PatternReport(
                consistent_patterns=[],
                inconsistent_patterns=[],
                pattern_violations={},
                pattern_score=0.0,
                improvement_suggestions=[f"Error during pattern validation: {e}"]
            )
    
    def generate_consistency_score(self, spec_set: List[str]) -> ConsistencyMetrics:
        """
        Generate overall consistency score for a set of specifications
        
        Provides comprehensive consistency metrics and prioritized
        improvement recommendations.
        """
        try:
            terminology_scores = []
            interface_scores = []
            pattern_scores = []
            critical_issues = []
            
            for spec_path in spec_set:
                spec_content = self._load_spec_content(spec_path)
                
                # Validate terminology
                term_report = self.validate_terminology(spec_content)
                terminology_scores.append(term_report.consistency_score)
                
                # Check interface compliance
                interface_report = self.check_interface_compliance(spec_content)
                interface_scores.append(interface_report.compliance_score)
                
                # Validate patterns
                patterns = self._extract_patterns_from_content(spec_content)
                pattern_report = self.validate_pattern_consistency(patterns)
                pattern_scores.append(pattern_report.pattern_score)
                
                # Collect critical issues
                if term_report.consistency_score < 0.5:
                    critical_issues.append(f"Critical terminology issues in {spec_path}")
                if interface_report.compliance_score < 0.5:
                    critical_issues.append(f"Critical interface issues in {spec_path}")
                if pattern_report.pattern_score < 0.5:
                    critical_issues.append(f"Critical pattern issues in {spec_path}")
            
            # Calculate average scores
            terminology_score = sum(terminology_scores) / len(terminology_scores) if terminology_scores else 0.0
            interface_score = sum(interface_scores) / len(interface_scores) if interface_scores else 0.0
            pattern_score = sum(pattern_scores) / len(pattern_scores) if pattern_scores else 0.0
            
            # Calculate overall score (weighted average)
            overall_score = (
                terminology_score * 0.3 +
                interface_score * 0.4 +
                pattern_score * 0.3
            )
            
            # Determine consistency level
            consistency_level = self._determine_consistency_level(overall_score)
            
            # Generate improvement priorities
            improvement_priority = self._generate_improvement_priorities(
                terminology_score, interface_score, pattern_score
            )
            
            return ConsistencyMetrics(
                terminology_score=terminology_score,
                interface_score=interface_score,
                pattern_score=pattern_score,
                overall_score=overall_score,
                consistency_level=consistency_level,
                critical_issues=critical_issues,
                improvement_priority=improvement_priority
            )
            
        except Exception as e:
            self.logger.error(f"Error generating consistency score: {e}")
            return ConsistencyMetrics(
                terminology_score=0.0,
                interface_score=0.0,
                pattern_score=0.0,
                overall_score=0.0,
                consistency_level=ConsistencyLevel.CRITICAL,
                critical_issues=[f"Error during consistency analysis: {e}"],
                improvement_priority=["Fix validation system errors"]
            )
    
    def _load_terminology_registry(self) -> Dict[str, Dict]:
        """Load unified terminology registry"""
        registry = {}
        
        # Load from existing specs
        if self.specs_directory.exists():
            for spec_dir in self.specs_directory.iterdir():
                if spec_dir.is_dir():
                    spec_terms = self._extract_spec_terminology(spec_dir)
                    for term, definition in spec_terms.items():
                        if term not in registry:
                            registry[term] = {
                                'canonical_form': term,
                                'variations': set(),
                                'definitions': [],
                                'usage_count': 0
                            }
                        registry[term]['definitions'].append(definition)
                        registry[term]['usage_count'] += 1
        
        return registry
    
    def _load_interface_patterns(self) -> Dict[str, Dict]:
        """Load standard interface patterns"""
        return {
            'ReflectiveModule': {
                'required_methods': [
                    'get_module_status',
                    'is_healthy', 
                    'get_health_indicators'
                ],
                'optional_methods': [
                    'degrade_gracefully',
                    'maintain_single_responsibility'
                ]
            },
            'ServiceInterface': {
                'required_methods': [
                    'provide_service',
                    'validate_request',
                    'handle_error'
                ],
                'optional_methods': [
                    'authenticate_request',
                    'log_service_call'
                ]
            }
        }
    
    def _load_design_patterns(self) -> Dict[str, Dict]:
        """Load standard design patterns"""
        return {
            'PDCA': {
                'required_phases': ['Plan', 'Do', 'Check', 'Act'],
                'pattern_indicators': ['plan', 'execute', 'validate', 'learn']
            },
            'RCA': {
                'required_phases': ['Symptom Analysis', 'Root Cause', 'Fix', 'Validation'],
                'pattern_indicators': ['analyze', 'diagnose', 'fix', 'verify']
            }
        }
    
    def _extract_terminology_from_content(self, content: str) -> Set[str]:
        """Extract terminology from spec content"""
        # Technical terms patterns
        patterns = [
            r'\b[A-Z]{2,}\b',  # Acronyms
            r'\b[A-Z][a-z]+(?:[A-Z][a-z]+)+\b',  # CamelCase
            r'`([^`]+)`',  # Code terms
            r'\*\*([^*]+)\*\*',  # Bold terms (often definitions)
        ]
        
        terms = set()
        for pattern in patterns:
            matches = re.findall(pattern, content)
            terms.update(matches)
        
        return terms
    
    def _find_term_variations(self, term: str, all_terms: Set[str]) -> List[str]:
        """Find variations of a term in the term set"""
        variations = []
        term_lower = term.lower()
        
        for other_term in all_terms:
            if other_term != term:
                similarity = SequenceMatcher(None, term_lower, other_term.lower()).ratio()
                if similarity > 0.8:  # 80% similarity threshold
                    variations.append(other_term)
        
        return variations
    
    def _find_canonical_term(self, term: str) -> Optional[str]:
        """Find canonical form of a term"""
        term_lower = term.lower()
        
        for canonical_term in self.terminology_registry:
            similarity = SequenceMatcher(None, term_lower, canonical_term.lower()).ratio()
            if similarity > 0.8:
                return canonical_term
        
        return None
    
    def _generate_terminology_recommendations(self, inconsistent_terms: Dict, 
                                            new_terms: Set[str]) -> List[str]:
        """Generate recommendations for terminology consistency"""
        recommendations = []
        
        for term, variations in inconsistent_terms.items():
            recommendations.append(
                f"Standardize variations of '{term}': {', '.join(variations)}"
            )
        
        if new_terms:
            recommendations.append(
                f"Review new terms for consistency: {', '.join(list(new_terms)[:5])}"
            )
        
        return recommendations
    
    def _extract_interfaces_from_definition(self, interface_def: str) -> Dict[str, List[str]]:
        """Extract interface definitions from content"""
        interfaces = {}
        
        # Look for class definitions
        class_pattern = r'class\s+(\w+).*?:(.*?)(?=class|\Z)'
        class_matches = re.findall(class_pattern, interface_def, re.DOTALL)
        
        for class_name, class_body in class_matches:
            # Extract method definitions
            method_pattern = r'def\s+(\w+)\s*\('
            methods = re.findall(method_pattern, class_body)
            interfaces[class_name] = methods
        
        return interfaces
    
    def _check_single_interface_compliance(self, interface_name: str, 
                                         methods: List[str]) -> Dict:
        """Check compliance of a single interface"""
        # Check against ReflectiveModule pattern
        if 'ReflectiveModule' in interface_name or any('reflective' in m.lower() for m in methods):
            required_methods = self.interface_patterns['ReflectiveModule']['required_methods']
            missing_methods = [m for m in required_methods if m not in methods]
            
            return {
                'compliant': len(missing_methods) == 0,
                'missing_methods': missing_methods
            }
        
        # Default compliance check
        return {
            'compliant': True,
            'missing_methods': []
        }
    
    def _generate_interface_remediation_steps(self, non_compliant: List[str], 
                                            missing_methods: Dict) -> List[str]:
        """Generate remediation steps for interface compliance"""
        steps = []
        
        for interface in non_compliant:
            if interface in missing_methods:
                methods = missing_methods[interface]
                steps.append(f"Add missing methods to {interface}: {', '.join(methods)}")
        
        return steps
    
    def _check_pattern_consistency(self, pattern: str) -> Dict:
        """Check consistency of a design pattern"""
        # Simple pattern consistency check
        pattern_lower = pattern.lower()
        
        if 'pdca' in pattern_lower:
            required_phases = self.design_patterns['PDCA']['required_phases']
            has_all_phases = all(phase.lower() in pattern_lower for phase in required_phases)
            
            return {
                'consistent': has_all_phases,
                'violation_description': 'Missing PDCA phases' if not has_all_phases else ''
            }
        
        return {
            'consistent': True,
            'violation_description': ''
        }
    
    def _generate_pattern_improvement_suggestions(self, inconsistent_patterns: List[str], 
                                                violations: Dict) -> List[str]:
        """Generate pattern improvement suggestions"""
        suggestions = []
        
        for pattern in inconsistent_patterns:
            if pattern in violations:
                suggestions.append(f"Fix {pattern}: {violations[pattern]}")
        
        return suggestions
    
    def _load_spec_content(self, spec_path: str) -> str:
        """Load content from a spec file"""
        try:
            return Path(spec_path).read_text()
        except Exception as e:
            self.logger.error(f"Error loading spec content from {spec_path}: {e}")
            return ""
    
    def _extract_patterns_from_content(self, content: str) -> List[str]:
        """Extract design patterns from content"""
        patterns = []
        content_lower = content.lower()
        
        # Look for common patterns
        if 'pdca' in content_lower or 'plan-do-check-act' in content_lower:
            patterns.append('PDCA')
        if 'rca' in content_lower or 'root cause analysis' in content_lower:
            patterns.append('RCA')
        
        return patterns
    
    def _determine_consistency_level(self, score: float) -> ConsistencyLevel:
        """Determine consistency level from score"""
        if score >= 0.95:
            return ConsistencyLevel.EXCELLENT
        elif score >= 0.85:
            return ConsistencyLevel.GOOD
        elif score >= 0.70:
            return ConsistencyLevel.FAIR
        elif score >= 0.50:
            return ConsistencyLevel.POOR
        else:
            return ConsistencyLevel.CRITICAL
    
    def _generate_improvement_priorities(self, terminology_score: float, 
                                       interface_score: float, 
                                       pattern_score: float) -> List[str]:
        """Generate prioritized improvement recommendations"""
        priorities = []
        
        scores = [
            ('terminology', terminology_score),
            ('interface', interface_score),
            ('pattern', pattern_score)
        ]
        
        # Sort by lowest score first (highest priority)
        scores.sort(key=lambda x: x[1])
        
        for area, score in scores:
            if score < 0.8:
                priorities.append(f"Improve {area} consistency (current: {score:.2f})")
        
        return priorities
    
    def _extract_spec_terminology(self, spec_dir: Path) -> Dict[str, str]:
        """Extract terminology from a spec directory"""
        terminology = {}
        
        requirements_file = spec_dir / "requirements.md"
        if requirements_file.exists():
            content = requirements_file.read_text()
            terms = self._extract_terminology_from_content(content)
            
            for term in terms:
                terminology[term] = f"Used in {spec_dir.name}"
        
        return terminology
    
    # ReflectiveModule interface implementation
    def get_module_status(self) -> Dict[str, any]:
        """Get current module status"""
        return {
            'module_name': 'ConsistencyValidator',
            'status': 'operational',
            'terminology_registry_size': len(self.terminology_registry),
            'interface_patterns_loaded': len(self.interface_patterns),
            'design_patterns_loaded': len(self.design_patterns),
            'validation_thresholds': {
                'terminology': self.terminology_threshold,
                'interface': self.interface_threshold,
                'pattern': self.pattern_threshold
            }
        }
    
    def is_healthy(self) -> bool:
        """Check if module is healthy"""
        try:
            return (
                len(self.terminology_registry) > 0 and
                len(self.interface_patterns) > 0 and
                len(self.design_patterns) > 0
            )
        except Exception:
            return False
    
    def get_health_indicators(self) -> Dict[str, any]:
        """Get detailed health indicators"""
        return {
            'terminology_registry_loaded': len(self.terminology_registry) > 0,
            'interface_patterns_loaded': len(self.interface_patterns) > 0,
            'design_patterns_loaded': len(self.design_patterns) > 0,
            'validation_system_operational': True,
            'thresholds_configured': all([
                self.terminology_threshold > 0,
                self.interface_threshold > 0,
                self.pattern_threshold > 0
            ])
        }
    
    def _get_primary_responsibility(self) -> str:
        """Define the single primary responsibility of this module"""
        return "Ensure terminology, interface, and pattern consistency across all specs"