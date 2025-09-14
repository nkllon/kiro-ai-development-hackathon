"""
Validation Validation

This module was extracted from validation.py
as part of RM-DDD compliance refactoring.
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
from src.rm_ddd.core.health import ModuleHealth


def validate_terminology(self, spec_content: str) -> TerminologyReport:
    """
        Validate terminology consistency against unified vocabulary
        
        Checks for consistent usage of technical terms and identifies
        variations that could cause confusion.
        """
    try:
        extracted_terms = self._extract_terminology_from_content(spec_content)
        consistent_terms = set()
        inconsistent_terms = {}
        new_terms = set()
        for term in extracted_terms:
            if term in self.terminology_registry:
                variations = self._find_term_variations(term, extracted_terms)
                if variations:
                    inconsistent_terms[term] = variations
                else:
                    consistent_terms.add(term)
            else:
                canonical_term = self._find_canonical_term(term)
                if canonical_term:
                    if canonical_term not in inconsistent_terms:
                        inconsistent_terms[canonical_term] = []
                    inconsistent_terms[canonical_term].append(term)
                else:
                    new_terms.add(term)
        total_terms = len(extracted_terms)
        consistent_count = len(consistent_terms)
        consistency_score = consistent_count / total_terms if total_terms > 0 else 1.0
        recommendations = self._generate_terminology_recommendations(inconsistent_terms, new_terms)
        return TerminologyReport(consistent_terms=consistent_terms, inconsistent_terms=inconsistent_terms, new_terms=new_terms, deprecated_terms=set(), consistency_score=consistency_score, recommendations=recommendations)
    except Exception as e:
        self.logger.error(f'Error validating terminology: {e}')
        return TerminologyReport(consistent_terms=set(), inconsistent_terms={}, new_terms=set(), deprecated_terms=set(), consistency_score=0.0, recommendations=[f'Error during validation: {e}'])

def check_interface_compliance(self, interface_def: str) -> ComplianceReport:
    """
        Check interface compliance with standard patterns
        
        Validates that interfaces follow ReflectiveModule patterns and
        other established interface standards.
        """
    try:
        interfaces = self._extract_interfaces_from_definition(interface_def)
        compliant_interfaces = []
        non_compliant_interfaces = []
        missing_methods = {}
        for interface_name, methods in interfaces.items():
            compliance_result = self._check_single_interface_compliance(interface_name, methods)
            if compliance_result['compliant']:
                compliant_interfaces.append(interface_name)
            else:
                non_compliant_interfaces.append(interface_name)
                if compliance_result['missing_methods']:
                    missing_methods[interface_name] = compliance_result['missing_methods']
        total_interfaces = len(interfaces)
        compliant_count = len(compliant_interfaces)
        compliance_score = compliant_count / total_interfaces if total_interfaces > 0 else 1.0
        remediation_steps = self._generate_interface_remediation_steps(non_compliant_interfaces, missing_methods)
        return ComplianceReport(compliant_interfaces=compliant_interfaces, non_compliant_interfaces=non_compliant_interfaces, missing_methods=missing_methods, compliance_score=compliance_score, remediation_steps=remediation_steps)
    except Exception as e:
        self.logger.error(f'Error checking interface compliance: {e}')
        return ComplianceReport(compliant_interfaces=[], non_compliant_interfaces=[], missing_methods={}, compliance_score=0.0, remediation_steps=[f'Error during compliance check: {e}'])

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
        total_patterns = len(design_patterns)
        consistent_count = len(consistent_patterns)
        pattern_score = consistent_count / total_patterns if total_patterns > 0 else 1.0
        improvement_suggestions = self._generate_pattern_improvement_suggestions(inconsistent_patterns, pattern_violations)
        return PatternReport(consistent_patterns=consistent_patterns, inconsistent_patterns=inconsistent_patterns, pattern_violations=pattern_violations, pattern_score=pattern_score, improvement_suggestions=improvement_suggestions)
    except Exception as e:
        self.logger.error(f'Error validating pattern consistency: {e}')
        return PatternReport(consistent_patterns=[], inconsistent_patterns=[], pattern_violations={}, pattern_score=0.0, improvement_suggestions=[f'Error during pattern validation: {e}'])

def _check_single_interface_compliance(self, interface_name: str, methods: List[str]) -> Dict:
    """Check compliance of a single interface"""
    if 'ReflectiveModule' in interface_name or any(('reflective' in m.lower() for m in methods)):
        required_methods = self.interface_patterns['ReflectiveModule']['required_methods']
        missing_methods = [m for m in required_methods if m not in methods]
        return {'compliant': len(missing_methods) == 0, 'missing_methods': missing_methods}
    return {'compliant': True, 'missing_methods': []}

def _check_pattern_consistency(self, pattern: str) -> Dict:
    """Check consistency of a design pattern"""
    pattern_lower = pattern.lower()
    if 'pdca' in pattern_lower:
        required_phases = self.design_patterns['PDCA']['required_phases']
        has_all_phases = all((phase.lower() in pattern_lower for phase in required_phases))
        return {'consistent': has_all_phases, 'violation_description': 'Missing PDCA phases' if not has_all_phases else ''}
    return {'consistent': True, 'violation_description': ''}

    def register_module(self, registry):
        """Register module with registry."""
        metadata = self.get_interface_metadata()
        if hasattr(registry, 'register'):
            registry.register(metadata)
            
    def get_interface_metadata(self):
        """Get interface metadata for registry."""
        return {
            'module_id': getattr(self, 'module_id', self.__class__.__name__),
            'interface_type': self.__class__.__name__,
            'version': '1.0.0',
            'dependencies': [],
            'capabilities': []
        }

