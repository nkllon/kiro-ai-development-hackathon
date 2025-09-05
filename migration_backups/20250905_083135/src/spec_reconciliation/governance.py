"""
Governance Controller - Prevents spec fragmentation through mandatory governance controls

This module implements the core prevention mechanism that stops spec fragmentation
from occurring during the reconciliation process and in the future.
"""

import ast
import json
import logging
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple
import hashlib
import re

from src.beast_mode.core.reflective_module import ReflectiveModule


class ValidationResult(Enum):
    """Validation result types"""
    APPROVED = "approved"
    REJECTED = "rejected" 
    REQUIRES_REVIEW = "requires_review"
    REQUIRES_CONSOLIDATION = "requires_consolidation"


class OverlapSeverity(Enum):
    """Overlap severity levels"""
    NONE = "none"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class SpecProposal:
    """Represents a proposed new specification"""
    name: str
    content: str
    requirements: List[str]
    interfaces: List[str]
    terminology: Set[str]
    functionality_keywords: Set[str]


@dataclass
class ConflictReport:
    """Reports conflicts between specs"""
    conflicting_specs: List[str]
    conflict_type: str
    severity: OverlapSeverity
    description: str
    suggested_resolution: str


@dataclass
class OverlapReport:
    """Reports functional overlaps between specs"""
    spec_pairs: List[Tuple[str, str]]
    overlap_percentage: float
    overlapping_functionality: List[str]
    severity: OverlapSeverity
    consolidation_recommendation: str


@dataclass
class ApprovalStatus:
    """Status of approval workflow"""
    status: ValidationResult
    reviewer: str
    timestamp: str
    comments: str
    required_actions: List[str]


class GovernanceController(ReflectiveModule):
    """
    Prevents spec fragmentation through mandatory governance controls
    
    This is the core prevention mechanism that implements PCOR approach
    by validating all spec changes before they can be applied.
    """
    
    def __init__(self, specs_directory: str = ".kiro/specs"):
        super().__init__("GovernanceController")
        self.specs_directory = Path(specs_directory)
        self.logger = logging.getLogger(__name__)
        self.existing_specs = self._load_existing_specs()
        self.terminology_registry = self._build_terminology_registry()
        self.functionality_map = self._build_functionality_map()
        
    def validate_new_spec(self, spec_proposal: SpecProposal) -> ValidationResult:
        """
        Validates a new spec proposal against existing specs
        
        This is the primary prevention mechanism - no spec can be created
        without passing this validation.
        """
        try:
            # Check for overlapping functionality
            overlap_report = self.check_overlap_conflicts(spec_proposal)
            
            if overlap_report.severity == OverlapSeverity.CRITICAL:
                self.logger.warning(f"Critical overlap detected for spec {spec_proposal.name}")
                return ValidationResult.REQUIRES_CONSOLIDATION
                
            if overlap_report.severity in [OverlapSeverity.HIGH, OverlapSeverity.MEDIUM]:
                self.logger.info(f"Significant overlap detected for spec {spec_proposal.name}")
                return ValidationResult.REQUIRES_REVIEW
                
            # Check terminology consistency
            terminology_conflicts = self._check_terminology_conflicts(spec_proposal)
            if terminology_conflicts:
                self.logger.info(f"Terminology conflicts detected for spec {spec_proposal.name}")
                return ValidationResult.REQUIRES_REVIEW
                
            # Check interface compliance
            interface_issues = self._check_interface_compliance(spec_proposal)
            if interface_issues:
                self.logger.info(f"Interface compliance issues for spec {spec_proposal.name}")
                return ValidationResult.REQUIRES_REVIEW
                
            return ValidationResult.APPROVED
            
        except Exception as e:
            self.logger.error(f"Error validating spec proposal: {e}")
            return ValidationResult.REJECTED
    
    def check_overlap_conflicts(self, spec_proposal: SpecProposal) -> OverlapReport:
        """
        Detects overlapping functionality between proposed spec and existing specs
        
        Uses semantic analysis to identify functional overlaps that could
        lead to fragmentation.
        """
        overlapping_specs = []
        overlapping_functionality = []
        max_overlap_percentage = 0.0
        
        for existing_spec_name, existing_spec_data in self.existing_specs.items():
            overlap_percentage = self._calculate_functional_overlap(
                spec_proposal.functionality_keywords,
                existing_spec_data.get('functionality_keywords', set())
            )
            
            if overlap_percentage > 0.3:  # 30% overlap threshold
                overlapping_specs.append((spec_proposal.name, existing_spec_name))
                overlapping_functionality.extend(
                    self._identify_overlapping_functions(
                        spec_proposal.functionality_keywords,
                        existing_spec_data.get('functionality_keywords', set())
                    )
                )
                max_overlap_percentage = max(max_overlap_percentage, overlap_percentage)
        
        severity = self._determine_overlap_severity(max_overlap_percentage)
        
        return OverlapReport(
            spec_pairs=overlapping_specs,
            overlap_percentage=max_overlap_percentage,
            overlapping_functionality=overlapping_functionality,
            severity=severity,
            consolidation_recommendation=self._generate_consolidation_recommendation(
                overlapping_specs, severity
            )
        )
    
    def enforce_approval_workflow(self, change_request: Dict) -> ApprovalStatus:
        """
        Enforces mandatory approval workflow for spec changes
        
        Implements governance controls that require architectural review
        for any significant spec modifications.
        """
        try:
            change_type = change_request.get('type', 'unknown')
            impact_level = self._assess_change_impact(change_request)
            
            if impact_level == 'high':
                return ApprovalStatus(
                    status=ValidationResult.REQUIRES_REVIEW,
                    reviewer="architectural_review_board",
                    timestamp=self._get_timestamp(),
                    comments="High impact change requires architectural review",
                    required_actions=["Schedule architectural review", "Impact assessment"]
                )
            elif impact_level == 'medium':
                return ApprovalStatus(
                    status=ValidationResult.REQUIRES_REVIEW,
                    reviewer="tech_lead",
                    timestamp=self._get_timestamp(),
                    comments="Medium impact change requires tech lead review",
                    required_actions=["Tech lead approval required"]
                )
            else:
                return ApprovalStatus(
                    status=ValidationResult.APPROVED,
                    reviewer="automated_system",
                    timestamp=self._get_timestamp(),
                    comments="Low impact change approved automatically",
                    required_actions=[]
                )
                
        except Exception as e:
            self.logger.error(f"Error in approval workflow: {e}")
            return ApprovalStatus(
                status=ValidationResult.REJECTED,
                reviewer="system",
                timestamp=self._get_timestamp(),
                comments=f"Error processing approval: {e}",
                required_actions=["Manual review required"]
            )
    
    def trigger_consolidation(self, overlap_detection: OverlapReport) -> Dict:
        """
        Triggers automatic consolidation workflow when overlaps are detected
        
        This prevents fragmentation by forcing consolidation when
        overlapping functionality is detected.
        """
        if overlap_detection.severity in [OverlapSeverity.HIGH, OverlapSeverity.CRITICAL]:
            consolidation_workflow = {
                'workflow_id': self._generate_workflow_id(),
                'trigger_reason': f"Overlap severity: {overlap_detection.severity.value}",
                'affected_specs': [pair[1] for pair in overlap_detection.spec_pairs],
                'consolidation_plan': overlap_detection.consolidation_recommendation,
                'status': 'triggered',
                'next_steps': [
                    'Analyze overlapping functionality in detail',
                    'Create consolidation plan',
                    'Schedule stakeholder review',
                    'Execute consolidation'
                ]
            }
            
            self.logger.info(f"Consolidation workflow triggered: {consolidation_workflow['workflow_id']}")
            return consolidation_workflow
        
        return {'status': 'no_consolidation_needed'}
    
    def _load_existing_specs(self) -> Dict:
        """Load and analyze all existing specifications"""
        specs = {}
        
        if not self.specs_directory.exists():
            return specs
            
        for spec_dir in self.specs_directory.iterdir():
            if spec_dir.is_dir():
                spec_data = self._analyze_spec_directory(spec_dir)
                if spec_data:
                    specs[spec_dir.name] = spec_data
                    
        return specs
    
    def _analyze_spec_directory(self, spec_dir: Path) -> Optional[Dict]:
        """Analyze a single spec directory to extract metadata"""
        requirements_file = spec_dir / "requirements.md"
        design_file = spec_dir / "design.md"
        
        if not requirements_file.exists():
            return None
            
        try:
            requirements_content = requirements_file.read_text()
            design_content = design_file.read_text() if design_file.exists() else ""
            
            return {
                'requirements_content': requirements_content,
                'design_content': design_content,
                'functionality_keywords': self._extract_functionality_keywords(
                    requirements_content + design_content
                ),
                'terminology': self._extract_terminology(requirements_content + design_content),
                'interfaces': self._extract_interfaces(design_content)
            }
        except Exception as e:
            self.logger.error(f"Error analyzing spec directory {spec_dir}: {e}")
            return None
    
    def _extract_functionality_keywords(self, content: str) -> Set[str]:
        """Extract functionality keywords from spec content"""
        # Common functionality patterns
        functionality_patterns = [
            r'WHEN\s+([^T]+)\s+THEN',  # Acceptance criteria patterns
            r'User Story.*?I want\s+([^,]+)',  # User story patterns
            r'SHALL\s+([^.]+)',  # Requirement patterns
            r'implement\s+([^.]+)',  # Implementation patterns
        ]
        
        keywords = set()
        content_lower = content.lower()
        
        for pattern in functionality_patterns:
            matches = re.findall(pattern, content_lower, re.IGNORECASE)
            for match in matches:
                # Extract meaningful keywords from the match
                words = re.findall(r'\b[a-z]{3,}\b', match.lower())
                keywords.update(words)
        
        # Filter out common words
        common_words = {'the', 'and', 'for', 'with', 'that', 'this', 'will', 'can', 'are', 'have'}
        return keywords - common_words
    
    def _extract_terminology(self, content: str) -> Set[str]:
        """Extract technical terminology from spec content"""
        # Look for capitalized technical terms and acronyms
        terminology_patterns = [
            r'\b[A-Z]{2,}\b',  # Acronyms
            r'\b[A-Z][a-z]+(?:[A-Z][a-z]+)+\b',  # CamelCase terms
            r'`([^`]+)`',  # Code terms
        ]
        
        terms = set()
        for pattern in terminology_patterns:
            matches = re.findall(pattern, content)
            terms.update(matches)
            
        return terms
    
    def _extract_interfaces(self, content: str) -> List[str]:
        """Extract interface definitions from design content"""
        interface_patterns = [
            r'class\s+(\w+)\s*\(',  # Python class definitions
            r'interface\s+(\w+)',  # Interface definitions
            r'def\s+(\w+)\s*\(',  # Method definitions
        ]
        
        interfaces = []
        for pattern in interface_patterns:
            matches = re.findall(pattern, content)
            interfaces.extend(matches)
            
        return interfaces
    
    def _build_terminology_registry(self) -> Dict[str, Set[str]]:
        """Build unified terminology registry from existing specs"""
        registry = {}
        
        for spec_name, spec_data in self.existing_specs.items():
            terminology = spec_data.get('terminology', set())
            for term in terminology:
                if term not in registry:
                    registry[term] = set()
                registry[term].add(spec_name)
                
        return registry
    
    def _build_functionality_map(self) -> Dict[str, Set[str]]:
        """Build functionality map showing which specs provide which capabilities"""
        functionality_map = {}
        
        for spec_name, spec_data in self.existing_specs.items():
            keywords = spec_data.get('functionality_keywords', set())
            for keyword in keywords:
                if keyword not in functionality_map:
                    functionality_map[keyword] = set()
                functionality_map[keyword].add(spec_name)
                
        return functionality_map
    
    def _calculate_functional_overlap(self, keywords1: Set[str], keywords2: Set[str]) -> float:
        """Calculate percentage of functional overlap between two keyword sets"""
        if not keywords1 or not keywords2:
            return 0.0
            
        intersection = keywords1.intersection(keywords2)
        union = keywords1.union(keywords2)
        
        return len(intersection) / len(union) if union else 0.0
    
    def _identify_overlapping_functions(self, keywords1: Set[str], keywords2: Set[str]) -> List[str]:
        """Identify specific overlapping functions between two keyword sets"""
        return list(keywords1.intersection(keywords2))
    
    def _determine_overlap_severity(self, overlap_percentage: float) -> OverlapSeverity:
        """Determine severity level based on overlap percentage"""
        if overlap_percentage >= 0.8:
            return OverlapSeverity.CRITICAL
        elif overlap_percentage >= 0.6:
            return OverlapSeverity.HIGH
        elif overlap_percentage >= 0.4:
            return OverlapSeverity.MEDIUM
        elif overlap_percentage >= 0.2:
            return OverlapSeverity.LOW
        else:
            return OverlapSeverity.NONE
    
    def _generate_consolidation_recommendation(self, overlapping_specs: List[Tuple[str, str]], 
                                             severity: OverlapSeverity) -> str:
        """Generate consolidation recommendation based on overlap analysis"""
        if severity == OverlapSeverity.CRITICAL:
            return f"CRITICAL: Immediate consolidation required for specs: {overlapping_specs}"
        elif severity == OverlapSeverity.HIGH:
            return f"HIGH: Consolidation strongly recommended for specs: {overlapping_specs}"
        elif severity == OverlapSeverity.MEDIUM:
            return f"MEDIUM: Consider consolidation for specs: {overlapping_specs}"
        else:
            return "LOW: Monitor for future consolidation opportunities"
    
    def _check_terminology_conflicts(self, spec_proposal: SpecProposal) -> List[str]:
        """Check for terminology conflicts with existing specs"""
        conflicts = []
        
        for term in spec_proposal.terminology:
            if term in self.terminology_registry:
                existing_specs = self.terminology_registry[term]
                if len(existing_specs) > 1:
                    conflicts.append(f"Term '{term}' used inconsistently across specs: {existing_specs}")
                    
        return conflicts
    
    def _check_interface_compliance(self, spec_proposal: SpecProposal) -> List[str]:
        """Check interface compliance with existing patterns"""
        issues = []
        
        # Check if interfaces follow ReflectiveModule pattern
        for interface in spec_proposal.interfaces:
            if not self._follows_reflective_module_pattern(interface):
                issues.append(f"Interface '{interface}' does not follow ReflectiveModule pattern")
                
        return issues
    
    def _follows_reflective_module_pattern(self, interface: str) -> bool:
        """Check if interface follows ReflectiveModule pattern"""
        required_methods = ['get_module_status', 'is_healthy', 'get_health_indicators']
        return any(method in interface.lower() for method in required_methods)
    
    def _assess_change_impact(self, change_request: Dict) -> str:
        """Assess the impact level of a change request"""
        change_type = change_request.get('type', '')
        affected_specs = change_request.get('affected_specs', [])
        
        if len(affected_specs) > 3 or 'architecture' in change_type.lower():
            return 'high'
        elif len(affected_specs) > 1 or 'interface' in change_type.lower():
            return 'medium'
        else:
            return 'low'
    
    def _generate_workflow_id(self) -> str:
        """Generate unique workflow ID"""
        import time
        timestamp = str(int(time.time()))
        return f"consolidation_{timestamp}"
    
    def _get_timestamp(self) -> str:
        """Get current timestamp"""
        from datetime import datetime
        return datetime.now().isoformat()
    
    # ReflectiveModule interface implementation
    def get_module_status(self) -> Dict[str, any]:
        """Get current module status"""
        return {
            'module_name': 'GovernanceController',
            'status': 'operational',
            'specs_monitored': len(self.existing_specs),
            'terminology_terms': len(self.terminology_registry),
            'functionality_keywords': len(self.functionality_map),
            'last_validation': self._get_timestamp()
        }
    
    def is_healthy(self) -> bool:
        """Check if module is healthy"""
        try:
            return (
                self.specs_directory.exists() and
                len(self.existing_specs) > 0 and
                len(self.terminology_registry) > 0
            )
        except Exception:
            return False
    
    def get_health_indicators(self) -> Dict[str, any]:
        """Get detailed health indicators"""
        return {
            'specs_directory_exists': self.specs_directory.exists(),
            'specs_loaded': len(self.existing_specs),
            'terminology_registry_size': len(self.terminology_registry),
            'functionality_map_size': len(self.functionality_map),
            'validation_system_operational': True
        }
    
    def _get_primary_responsibility(self) -> str:
        """Define the single primary responsibility of this module"""
        return "Prevent spec fragmentation through mandatory governance controls"