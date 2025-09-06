"""
Spec Consolidator - Systematically merges overlapping specs while preserving all functionality

This module implements the core consolidation mechanism that eliminates spec fragmentation
by intelligently merging overlapping specifications while maintaining traceability.
"""

import ast
import json
import logging
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple, Any
import hashlib
import re
from datetime import datetime

from src.beast_mode.core.reflective_module import ReflectiveModule
from .governance import GovernanceController, OverlapSeverity, OverlapReport


class ConsolidationStatus(Enum):
    """Consolidation status types"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    REQUIRES_MANUAL_REVIEW = "requires_manual_review"


class ConflictResolutionStrategy(Enum):
    """Conflict resolution strategies"""
    MERGE_COMPATIBLE = "merge_compatible"
    PRIORITIZE_NEWER = "prioritize_newer"
    PRIORITIZE_MORE_DETAILED = "prioritize_more_detailed"
    MANUAL_REVIEW = "manual_review"
    KEEP_SEPARATE = "keep_separate"


@dataclass
class RequirementAnalysis:
    """Analysis of a single requirement"""
    requirement_id: str
    content: str
    functionality_keywords: Set[str]
    acceptance_criteria: List[str]
    stakeholder_personas: List[str]
    complexity_score: float
    quality_score: float


@dataclass
class OverlapAnalysis:
    """Comprehensive analysis of overlaps between specs"""
    spec_pairs: List[Tuple[str, str]]
    functional_overlaps: Dict[str, List[str]]
    terminology_conflicts: Dict[str, List[str]]
    interface_conflicts: Dict[str, List[str]]
    dependency_relationships: Dict[str, List[str]]
    consolidation_opportunities: List['ConsolidationOpportunity']
    risk_assessment: Dict[str, float]
    effort_estimates: Dict[str, int]  # hours


@dataclass
class ConsolidationOpportunity:
    """Represents an opportunity for spec consolidation"""
    target_specs: List[str]
    overlap_percentage: float
    consolidation_type: str  # "merge", "absorb", "split"
    effort_estimate: int  # hours
    risk_level: str  # "low", "medium", "high"
    benefits: List[str]
    challenges: List[str]
    recommended_strategy: ConflictResolutionStrategy


@dataclass
class ConsolidationPlan:
    """Detailed plan for consolidating specs"""
    plan_id: str
    target_specs: List[str]
    unified_spec_name: str
    consolidation_strategy: ConflictResolutionStrategy
    requirement_mapping: Dict[str, str]  # original_req_id -> unified_req_id
    interface_standardization: List['InterfaceChange']
    terminology_unification: List['TerminologyChange']
    migration_steps: List['MigrationStep']
    validation_criteria: List['ValidationCriterion']
    estimated_effort: int  # hours
    risk_mitigation: List[str]
    success_metrics: Dict[str, Any]


@dataclass
class InterfaceChange:
    """Represents a change to standardize interfaces"""
    original_interface: str
    standardized_interface: str
    affected_specs: List[str]
    migration_guidance: str


@dataclass
class TerminologyChange:
    """Represents a terminology unification change"""
    original_terms: List[str]
    unified_term: str
    affected_specs: List[str]
    definition: str


@dataclass
class MigrationStep:
    """Single step in migration process"""
    step_id: str
    description: str
    prerequisites: List[str]
    actions: List[str]
    validation_checks: List[str]
    estimated_effort: int  # hours


@dataclass
class ValidationCriterion:
    """Criteria for validating successful consolidation"""
    criterion_id: str
    description: str
    validation_method: str
    success_threshold: Any
    measurement_approach: str


@dataclass
class TraceabilityLink:
    """Links original requirements to consolidated requirements"""
    original_spec: str
    original_requirement_id: str
    consolidated_spec: str
    consolidated_requirement_id: str
    transformation_type: str  # "merged", "split", "unchanged", "deprecated"
    rationale: str


@dataclass
class TraceabilityMap:
    """Complete traceability mapping for consolidation"""
    consolidation_id: str
    links: List[TraceabilityLink]
    impact_analysis: Dict[str, List[str]]
    change_log: List[Dict[str, Any]]
    validation_status: Dict[str, bool]


class SpecConsolidator(ReflectiveModule):
    """
    Systematically merges overlapping specs while preserving all functionality
    
    This module implements intelligent consolidation that eliminates fragmentation
    while maintaining complete traceability and functionality preservation.
    """
    
    def __init__(self, specs_directory: str = ".kiro/specs"):
        super().__init__("SpecConsolidator")
        self.specs_directory = Path(specs_directory)
        self.logger = logging.getLogger(__name__)
        self.governance_controller = GovernanceController(specs_directory)
        self.consolidation_history: List[ConsolidationPlan] = []
        self.traceability_maps: Dict[str, TraceabilityMap] = {}
        
    def analyze_overlap(self, spec_set: List[str]) -> OverlapAnalysis:
        """
        Build comprehensive spec parsing system to extract requirements, interfaces, and terminology
        Create semantic similarity analysis using existing functionality keywords approach
        Implement dependency graph analysis to identify component relationships
        Generate consolidation opportunity reports with effort estimates and risk assessments
        """
        try:
            self.logger.info(f"Starting overlap analysis for {len(spec_set)} specs")
            
            # Parse all specs to extract structured data
            parsed_specs = {}
            for spec_name in spec_set:
                parsed_data = self._parse_spec_comprehensively(spec_name)
                if parsed_data:
                    parsed_specs[spec_name] = parsed_data
            
            # Analyze functional overlaps using semantic similarity
            functional_overlaps = self._analyze_functional_overlaps(parsed_specs)
            
            # Detect terminology conflicts
            terminology_conflicts = self._detect_terminology_conflicts(parsed_specs)
            
            # Identify interface conflicts
            interface_conflicts = self._identify_interface_conflicts(parsed_specs)
            
            # Build dependency graph and analyze relationships
            dependency_relationships = self._analyze_dependency_relationships(parsed_specs)
            
            # Generate consolidation opportunities
            consolidation_opportunities = self._generate_consolidation_opportunities(
                parsed_specs, functional_overlaps, dependency_relationships
            )
            
            # Assess risks and estimate effort
            risk_assessment = self._assess_consolidation_risks(consolidation_opportunities)
            effort_estimates = self._estimate_consolidation_effort(consolidation_opportunities)
            
            # Find spec pairs with significant overlap
            spec_pairs = self._identify_overlapping_spec_pairs(functional_overlaps)
            
            return OverlapAnalysis(
                spec_pairs=spec_pairs,
                functional_overlaps=functional_overlaps,
                terminology_conflicts=terminology_conflicts,
                interface_conflicts=interface_conflicts,
                dependency_relationships=dependency_relationships,
                consolidation_opportunities=consolidation_opportunities,
                risk_assessment=risk_assessment,
                effort_estimates=effort_estimates
            )
            
        except Exception as e:
            self.logger.error(f"Error in overlap analysis: {e}")
            raise
    
    def _parse_spec_comprehensively(self, spec_name: str) -> Optional[Dict[str, Any]]:
        """Parse a single spec to extract all relevant information"""
        spec_dir = self.specs_directory / spec_name
        if not spec_dir.exists():
            self.logger.warning(f"Spec directory not found: {spec_name}")
            return None
            
        try:
            # Load spec files
            requirements_file = spec_dir / "requirements.md"
            design_file = spec_dir / "design.md"
            tasks_file = spec_dir / "tasks.md"
            
            requirements_content = requirements_file.read_text() if requirements_file.exists() else ""
            design_content = design_file.read_text() if design_file.exists() else ""
            tasks_content = tasks_file.read_text() if tasks_file.exists() else ""
            
            # Extract structured information
            requirements = self._extract_requirements(requirements_content)
            interfaces = self._extract_interfaces_detailed(design_content)
            terminology = self._extract_terminology_detailed(requirements_content + design_content)
            functionality_keywords = self._extract_functionality_keywords_enhanced(
                requirements_content + design_content + tasks_content
            )
            dependencies = self._extract_dependencies(design_content + tasks_content)
            
            return {
                'name': spec_name,
                'requirements_content': requirements_content,
                'design_content': design_content,
                'tasks_content': tasks_content,
                'requirements': requirements,
                'interfaces': interfaces,
                'terminology': terminology,
                'functionality_keywords': functionality_keywords,
                'dependencies': dependencies,
                'complexity_score': self._calculate_complexity_score(requirements_content, design_content),
                'quality_score': self._calculate_quality_score(requirements_content, design_content)
            }
            
        except Exception as e:
            self.logger.error(f"Error parsing spec {spec_name}: {e}")
            return None
    
    def _extract_requirements(self, content: str) -> List[RequirementAnalysis]:
        """Extract and analyze individual requirements"""
        requirements = []
        
        # Pattern to match requirement sections
        requirement_pattern = r'### Requirement \d+[:\s]*([^\n]+)\n\n\*\*User Story:\*\*([^#]+?)#### Acceptance Criteria\n\n(.*?)(?=###|$)'
        
        matches = re.findall(requirement_pattern, content, re.DOTALL)
        
        for i, (title, user_story, criteria_text) in enumerate(matches):
            # Extract acceptance criteria
            criteria_lines = [line.strip() for line in criteria_text.split('\n') if line.strip() and line.strip().startswith(('1.', '2.', '3.', '4.', '5.'))]
            
            # Extract functionality keywords from requirement
            req_text = title + user_story + criteria_text
            functionality_keywords = self._extract_functionality_keywords_enhanced(req_text)
            
            # Extract stakeholder personas
            stakeholder_personas = self._extract_stakeholder_personas(user_story)
            
            requirements.append(RequirementAnalysis(
                requirement_id=f"R{i+1}",
                content=req_text,
                functionality_keywords=functionality_keywords,
                acceptance_criteria=criteria_lines,
                stakeholder_personas=stakeholder_personas,
                complexity_score=self._calculate_requirement_complexity(req_text),
                quality_score=self._calculate_requirement_quality(criteria_lines)
            ))
        
        return requirements
    
    def _extract_interfaces_detailed(self, content: str) -> List[Dict[str, Any]]:
        """Extract detailed interface information"""
        interfaces = []
        
        # Pattern for class definitions with methods
        class_pattern = r'class\s+(\w+)\s*\([^)]*\):\s*\n(.*?)(?=\nclass|\n\n[A-Z]|$)'
        
        matches = re.findall(class_pattern, content, re.DOTALL)
        
        for class_name, class_body in matches:
            methods = re.findall(r'def\s+(\w+)\s*\([^)]*\)\s*->\s*([^:]+):', class_body)
            
            interfaces.append({
                'name': class_name,
                'type': 'class',
                'methods': [{'name': method, 'return_type': return_type.strip()} for method, return_type in methods],
                'follows_reflective_module': 'ReflectiveModule' in class_body
            })
        
        return interfaces
    
    def _extract_terminology_detailed(self, content: str) -> Dict[str, Dict[str, Any]]:
        """Extract detailed terminology with context"""
        terminology = {}
        
        # Extract acronyms and their definitions
        acronym_pattern = r'\b([A-Z]{2,})\s*\([^)]+\)'
        acronym_matches = re.findall(acronym_pattern, content)
        
        for acronym in acronym_matches:
            terminology[acronym] = {
                'type': 'acronym',
                'context': 'definition_provided',
                'usage_count': content.count(acronym)
            }
        
        # Extract technical terms (CamelCase)
        camelcase_pattern = r'\b[A-Z][a-z]+(?:[A-Z][a-z]+)+\b'
        camelcase_matches = re.findall(camelcase_pattern, content)
        
        for term in camelcase_matches:
            if term not in terminology:
                terminology[term] = {
                    'type': 'technical_term',
                    'context': 'camelcase',
                    'usage_count': content.count(term)
                }
        
        # Extract code terms
        code_pattern = r'`([^`]+)`'
        code_matches = re.findall(code_pattern, content)
        
        for term in code_matches:
            if term not in terminology:
                terminology[term] = {
                    'type': 'code_term',
                    'context': 'code_block',
                    'usage_count': content.count(f'`{term}`')
                }
        
        return terminology
    
    def _extract_functionality_keywords_enhanced(self, content: str) -> Set[str]:
        """Enhanced functionality keyword extraction with semantic analysis"""
        keywords = set()
        
        # Enhanced patterns for functionality extraction
        functionality_patterns = [
            r'WHEN\s+([^T]+)\s+THEN\s+[^S]*SHALL\s+([^.]+)',  # Acceptance criteria
            r'User Story.*?I want\s+([^,]+)',  # User stories
            r'implement\s+([^.]+)',  # Implementation tasks
            r'create\s+([^.]+)',  # Creation tasks
            r'build\s+([^.]+)',  # Building tasks
            r'validate\s+([^.]+)',  # Validation tasks
            r'analyze\s+([^.]+)',  # Analysis tasks
            r'monitor\s+([^.]+)',  # Monitoring tasks
            r'detect\s+([^.]+)',  # Detection tasks
            r'prevent\s+([^.]+)',  # Prevention tasks
        ]
        
        content_lower = content.lower()
        
        for pattern in functionality_patterns:
            matches = re.findall(pattern, content_lower, re.IGNORECASE)
            for match in matches:
                if isinstance(match, tuple):
                    for submatch in match:
                        words = self._extract_meaningful_words(submatch)
                        keywords.update(words)
                else:
                    words = self._extract_meaningful_words(match)
                    keywords.update(words)
        
        return keywords
    
    def _extract_meaningful_words(self, text: str) -> Set[str]:
        """Extract meaningful words from text, filtering out common words"""
        # Extract words that are 3+ characters and not common words
        words = re.findall(r'\b[a-z]{3,}\b', text.lower())
        
        # Common words to filter out
        common_words = {
            'the', 'and', 'for', 'with', 'that', 'this', 'will', 'can', 'are', 'have',
            'been', 'was', 'were', 'not', 'but', 'all', 'any', 'had', 'her', 'his',
            'how', 'its', 'may', 'new', 'now', 'old', 'see', 'two', 'way', 'who',
            'boy', 'did', 'has', 'let', 'put', 'say', 'she', 'too', 'use'
        }
        
        return set(words) - common_words
    
    def _extract_stakeholder_personas(self, user_story: str) -> List[str]:
        """Extract stakeholder personas from user stories"""
        persona_pattern = r'As\s+a\s+([^,]+),'
        matches = re.findall(persona_pattern, user_story, re.IGNORECASE)
        return [match.strip().replace('"', '') for match in matches]
    
    def _extract_dependencies(self, content: str) -> List[str]:
        """Extract dependencies between components"""
        dependencies = []
        
        # Look for explicit dependency mentions
        dependency_patterns = [
            r'depends\s+on\s+([^.]+)',
            r'requires\s+([^.]+)',
            r'uses\s+([A-Z][a-zA-Z]+)',
            r'integrates\s+with\s+([^.]+)',
        ]
        
        for pattern in dependency_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            dependencies.extend(matches)
        
        return dependencies
    
    def _calculate_complexity_score(self, requirements_content: str, design_content: str) -> float:
        """Calculate complexity score for a spec"""
        # Factors that increase complexity
        complexity_factors = {
            'requirements_count': len(re.findall(r'### Requirement \d+', requirements_content)) * 0.1,
            'acceptance_criteria_count': len(re.findall(r'\d+\.\s+WHEN', requirements_content)) * 0.05,
            'interface_count': len(re.findall(r'class\s+\w+', design_content)) * 0.15,
            'method_count': len(re.findall(r'def\s+\w+', design_content)) * 0.02,
            'content_length': (len(requirements_content) + len(design_content)) / 10000 * 0.1
        }
        
        return min(sum(complexity_factors.values()), 1.0)  # Cap at 1.0
    
    def _calculate_quality_score(self, requirements_content: str, design_content: str) -> float:
        """Calculate quality score for a spec"""
        quality_factors = {
            'has_user_stories': 0.2 if 'User Story:' in requirements_content else 0,
            'has_acceptance_criteria': 0.3 if 'Acceptance Criteria' in requirements_content else 0,
            'has_design_document': 0.2 if design_content else 0,
            'has_interfaces': 0.15 if 'class ' in design_content else 0,
            'has_error_handling': 0.15 if 'Error Handling' in design_content else 0
        }
        
        return sum(quality_factors.values())
    
    def _calculate_requirement_complexity(self, req_text: str) -> float:
        """Calculate complexity score for individual requirement"""
        complexity_indicators = {
            'criteria_count': len(re.findall(r'\d+\.\s+', req_text)) * 0.1,
            'conditional_logic': len(re.findall(r'\bIF\b|\bWHEN\b|\bAND\b', req_text, re.IGNORECASE)) * 0.05,
            'text_length': len(req_text) / 1000 * 0.1
        }
        
        return min(sum(complexity_indicators.values()), 1.0)
    
    def _calculate_requirement_quality(self, criteria_lines: List[str]) -> float:
        """Calculate quality score for individual requirement"""
        if not criteria_lines:
            return 0.0
        
        quality_indicators = {
            'has_criteria': 0.4 if criteria_lines else 0,
            'criteria_completeness': min(len(criteria_lines) / 5, 1.0) * 0.3,  # Up to 5 criteria
            'uses_ears_format': 0.3 if any('WHEN' in line and 'THEN' in line and 'SHALL' in line 
                                          for line in criteria_lines) else 0
        }
        
        return sum(quality_indicators.values())
    
    def _analyze_functional_overlaps(self, parsed_specs: Dict[str, Dict[str, Any]]) -> Dict[str, List[str]]:
        """Analyze functional overlaps between specs using semantic similarity"""
        functional_overlaps = {}
        
        spec_names = list(parsed_specs.keys())
        
        for i, spec1 in enumerate(spec_names):
            for spec2 in spec_names[i+1:]:
                spec1_keywords = parsed_specs[spec1]['functionality_keywords']
                spec2_keywords = parsed_specs[spec2]['functionality_keywords']
                
                # Calculate semantic overlap
                overlap_keywords = spec1_keywords.intersection(spec2_keywords)
                overlap_percentage = len(overlap_keywords) / len(spec1_keywords.union(spec2_keywords)) if spec1_keywords.union(spec2_keywords) else 0
                
                if overlap_percentage > 0.2:  # 20% threshold for significant overlap
                    pair_key = f"{spec1}+{spec2}"
                    functional_overlaps[pair_key] = list(overlap_keywords)
        
        return functional_overlaps
    
    def _detect_terminology_conflicts(self, parsed_specs: Dict[str, Dict[str, Any]]) -> Dict[str, List[str]]:
        """Detect terminology conflicts between specs"""
        terminology_conflicts = {}
        
        # Build term usage map
        term_usage = {}
        for spec_name, spec_data in parsed_specs.items():
            for term, term_data in spec_data['terminology'].items():
                if term not in term_usage:
                    term_usage[term] = []
                term_usage[term].append({
                    'spec': spec_name,
                    'type': term_data['type'],
                    'context': term_data['context'],
                    'usage_count': term_data['usage_count']
                })
        
        # Identify conflicts (same term used differently)
        for term, usages in term_usage.items():
            if len(usages) > 1:
                types = set(usage['type'] for usage in usages)
                contexts = set(usage['context'] for usage in usages)
                
                if len(types) > 1 or len(contexts) > 1:
                    terminology_conflicts[term] = [usage['spec'] for usage in usages]
        
        return terminology_conflicts
    
    def _identify_interface_conflicts(self, parsed_specs: Dict[str, Dict[str, Any]]) -> Dict[str, List[str]]:
        """Identify interface conflicts between specs"""
        interface_conflicts = {}
        
        # Build interface usage map
        interface_usage = {}
        for spec_name, spec_data in parsed_specs.items():
            for interface in spec_data['interfaces']:
                interface_name = interface['name']
                if interface_name not in interface_usage:
                    interface_usage[interface_name] = []
                interface_usage[interface_name].append({
                    'spec': spec_name,
                    'methods': interface['methods'],
                    'follows_reflective_module': interface['follows_reflective_module']
                })
        
        # Identify conflicts (same interface name, different signatures)
        for interface_name, usages in interface_usage.items():
            if len(usages) > 1:
                method_signatures = []
                for usage in usages:
                    signature = set((method['name'], method['return_type']) for method in usage['methods'])
                    method_signatures.append(signature)
                
                # Check if signatures are different
                if len(set(frozenset(sig) for sig in method_signatures)) > 1:
                    interface_conflicts[interface_name] = [usage['spec'] for usage in usages]
        
        return interface_conflicts
    
    def _analyze_dependency_relationships(self, parsed_specs: Dict[str, Dict[str, Any]]) -> Dict[str, List[str]]:
        """Analyze dependency relationships between specs"""
        dependency_relationships = {}
        
        for spec_name, spec_data in parsed_specs.items():
            dependencies = []
            
            # Check for explicit dependencies in content
            for dependency in spec_data['dependencies']:
                # Try to match dependency to existing spec names
                for other_spec in parsed_specs.keys():
                    if other_spec != spec_name and other_spec.lower() in dependency.lower():
                        dependencies.append(other_spec)
            
            # Check for implicit dependencies through shared terminology/interfaces
            for other_spec, other_data in parsed_specs.items():
                if other_spec != spec_name:
                    shared_terms = set(spec_data['terminology'].keys()).intersection(
                        set(other_data['terminology'].keys())
                    )
                    shared_interfaces = set(interface['name'] for interface in spec_data['interfaces']).intersection(
                        set(interface['name'] for interface in other_data['interfaces'])
                    )
                    
                    if len(shared_terms) > 3 or len(shared_interfaces) > 0:
                        dependencies.append(other_spec)
            
            if dependencies:
                dependency_relationships[spec_name] = list(set(dependencies))
        
        return dependency_relationships    

    def _generate_consolidation_opportunities(self, parsed_specs: Dict[str, Dict[str, Any]], 
                                            functional_overlaps: Dict[str, List[str]], 
                                            dependency_relationships: Dict[str, List[str]]) -> List[ConsolidationOpportunity]:
        """Generate consolidation opportunities with effort estimates and risk assessments"""
        opportunities = []
        
        # Analyze each functional overlap for consolidation potential
        for pair_key, overlapping_functions in functional_overlaps.items():
            spec1, spec2 = pair_key.split('+')
            
            spec1_data = parsed_specs[spec1]
            spec2_data = parsed_specs[spec2]
            
            # Calculate overlap percentage
            all_functions = spec1_data['functionality_keywords'].union(spec2_data['functionality_keywords'])
            overlap_percentage = len(overlapping_functions) / len(all_functions) if all_functions else 0
            
            # Determine consolidation type
            if overlap_percentage > 0.8:
                consolidation_type = "merge"  # High overlap - merge completely
            elif overlap_percentage > 0.5:
                consolidation_type = "absorb"  # Medium overlap - one absorbs the other
            else:
                consolidation_type = "split"  # Low overlap - split common functionality
            
            # Estimate effort based on complexity and size
            effort_estimate = self._estimate_consolidation_effort_for_pair(spec1_data, spec2_data, overlap_percentage)
            
            # Assess risk level
            risk_level = self._assess_consolidation_risk_for_pair(spec1_data, spec2_data, dependency_relationships)
            
            # Identify benefits and challenges
            benefits = self._identify_consolidation_benefits(spec1_data, spec2_data, overlap_percentage)
            challenges = self._identify_consolidation_challenges(spec1_data, spec2_data, dependency_relationships)
            
            # Recommend strategy
            recommended_strategy = self._recommend_consolidation_strategy(
                overlap_percentage, risk_level, spec1_data, spec2_data
            )
            
            opportunities.append(ConsolidationOpportunity(
                target_specs=[spec1, spec2],
                overlap_percentage=overlap_percentage,
                consolidation_type=consolidation_type,
                effort_estimate=effort_estimate,
                risk_level=risk_level,
                benefits=benefits,
                challenges=challenges,
                recommended_strategy=recommended_strategy
            ))
        
        # Sort by potential impact (overlap percentage * inverse risk)
        opportunities.sort(key=lambda x: x.overlap_percentage * (1.0 if x.risk_level == "low" else 0.5 if x.risk_level == "medium" else 0.2), reverse=True)
        
        return opportunities
    
    def _estimate_consolidation_effort_for_pair(self, spec1_data: Dict, spec2_data: Dict, overlap_percentage: float) -> int:
        """Estimate effort in hours for consolidating a pair of specs"""
        base_effort = 8  # Base 8 hours for any consolidation
        
        # Add effort based on complexity
        complexity_effort = (spec1_data['complexity_score'] + spec2_data['complexity_score']) * 20
        
        # Add effort based on number of requirements
        requirements_effort = (len(spec1_data['requirements']) + len(spec2_data['requirements'])) * 2
        
        # Add effort based on interfaces
        interface_effort = (len(spec1_data['interfaces']) + len(spec2_data['interfaces'])) * 4
        
        # Reduce effort if high overlap (easier to merge)
        overlap_reduction = overlap_percentage * 0.3
        
        total_effort = base_effort + complexity_effort + requirements_effort + interface_effort
        total_effort *= (1 - overlap_reduction)
        
        return int(total_effort)
    
    def _assess_consolidation_risk_for_pair(self, spec1_data: Dict, spec2_data: Dict, 
                                          dependency_relationships: Dict[str, List[str]]) -> str:
        """Assess risk level for consolidating a pair of specs"""
        risk_factors = []
        
        # High complexity increases risk
        if spec1_data['complexity_score'] > 0.7 or spec2_data['complexity_score'] > 0.7:
            risk_factors.append("high_complexity")
        
        # Many dependencies increase risk
        spec1_deps = len(dependency_relationships.get(spec1_data['name'], []))
        spec2_deps = len(dependency_relationships.get(spec2_data['name'], []))
        if spec1_deps > 3 or spec2_deps > 3:
            risk_factors.append("many_dependencies")
        
        # Low quality specs increase risk
        if spec1_data['quality_score'] < 0.5 or spec2_data['quality_score'] < 0.5:
            risk_factors.append("low_quality")
        
        # Determine overall risk level
        if len(risk_factors) >= 3:
            return "high"
        elif len(risk_factors) >= 1:
            return "medium"
        else:
            return "low"
    
    def _identify_consolidation_benefits(self, spec1_data: Dict, spec2_data: Dict, overlap_percentage: float) -> List[str]:
        """Identify benefits of consolidating two specs"""
        benefits = []
        
        if overlap_percentage > 0.5:
            benefits.append("Eliminates significant functional duplication")
        
        if len(spec1_data['requirements']) + len(spec2_data['requirements']) > 10:
            benefits.append("Reduces overall requirement complexity")
        
        if spec1_data['quality_score'] > 0.7 or spec2_data['quality_score'] > 0.7:
            benefits.append("Leverages high-quality specification patterns")
        
        benefits.extend([
            "Improves architectural consistency",
            "Reduces implementation effort",
            "Simplifies maintenance overhead"
        ])
        
        return benefits
    
    def _identify_consolidation_challenges(self, spec1_data: Dict, spec2_data: Dict, 
                                         dependency_relationships: Dict[str, List[str]]) -> List[str]:
        """Identify challenges in consolidating two specs"""
        challenges = []
        
        if spec1_data['complexity_score'] > 0.7 or spec2_data['complexity_score'] > 0.7:
            challenges.append("High complexity requires careful integration")
        
        spec1_deps = len(dependency_relationships.get(spec1_data['name'], []))
        spec2_deps = len(dependency_relationships.get(spec2_data['name'], []))
        if spec1_deps > 2 or spec2_deps > 2:
            challenges.append("Multiple dependencies require coordination")
        
        if len(spec1_data['interfaces']) > 3 or len(spec2_data['interfaces']) > 3:
            challenges.append("Interface standardization complexity")
        
        if spec1_data['quality_score'] < 0.5 or spec2_data['quality_score'] < 0.5:
            challenges.append("Quality improvement needed during consolidation")
        
        return challenges
    
    def _recommend_consolidation_strategy(self, overlap_percentage: float, risk_level: str, 
                                        spec1_data: Dict, spec2_data: Dict) -> ConflictResolutionStrategy:
        """Recommend consolidation strategy based on analysis"""
        if risk_level == "high":
            return ConflictResolutionStrategy.MANUAL_REVIEW
        
        if overlap_percentage > 0.8:
            return ConflictResolutionStrategy.MERGE_COMPATIBLE
        elif overlap_percentage > 0.5:
            if spec1_data['quality_score'] > spec2_data['quality_score']:
                return ConflictResolutionStrategy.PRIORITIZE_MORE_DETAILED
            else:
                return ConflictResolutionStrategy.PRIORITIZE_NEWER
        else:
            return ConflictResolutionStrategy.KEEP_SEPARATE
    
    def _assess_consolidation_risks(self, opportunities: List[ConsolidationOpportunity]) -> Dict[str, float]:
        """Assess overall consolidation risks"""
        risk_assessment = {}
        
        for opportunity in opportunities:
            risk_key = "+".join(opportunity.target_specs)
            
            # Calculate risk score based on multiple factors
            risk_score = 0.0
            
            if opportunity.risk_level == "high":
                risk_score += 0.7
            elif opportunity.risk_level == "medium":
                risk_score += 0.4
            else:
                risk_score += 0.1
            
            # Add risk based on effort estimate
            if opportunity.effort_estimate > 40:
                risk_score += 0.2
            elif opportunity.effort_estimate > 20:
                risk_score += 0.1
            
            # Reduce risk for high overlap (easier consolidation)
            if opportunity.overlap_percentage > 0.7:
                risk_score *= 0.8
            
            risk_assessment[risk_key] = min(risk_score, 1.0)
        
        return risk_assessment
    
    def _estimate_consolidation_effort(self, opportunities: List[ConsolidationOpportunity]) -> Dict[str, int]:
        """Estimate effort for consolidation opportunities"""
        effort_estimates = {}
        
        for opportunity in opportunities:
            effort_key = "+".join(opportunity.target_specs)
            effort_estimates[effort_key] = opportunity.effort_estimate
        
        return effort_estimates
    
    def _identify_overlapping_spec_pairs(self, functional_overlaps: Dict[str, List[str]]) -> List[Tuple[str, str]]:
        """Identify spec pairs with significant overlap"""
        spec_pairs = []
        
        for pair_key in functional_overlaps.keys():
            spec1, spec2 = pair_key.split('+')
            spec_pairs.append((spec1, spec2))
        
        return spec_pairs
    
    # ReflectiveModule interface implementation
    def get_module_status(self) -> Dict[str, any]:
        """Get current module status"""
        return {
            'module_name': 'SpecConsolidator',
            'status': 'operational',
            'consolidations_completed': len(self.consolidation_history),
            'traceability_maps': len(self.traceability_maps),
            'governance_controller_healthy': self.governance_controller.is_healthy(),
            'last_analysis': datetime.now().isoformat()
        }
    
    def is_healthy(self) -> bool:
        """Check if module is healthy"""
        try:
            return (
                self.specs_directory.exists() and
                self.governance_controller.is_healthy()
            )
        except Exception:
            return False
    
    def get_health_indicators(self) -> Dict[str, any]:
        """Get detailed health indicators"""
        return {
            'specs_directory_exists': self.specs_directory.exists(),
            'governance_controller_operational': self.governance_controller.is_healthy(),
            'consolidation_history_size': len(self.consolidation_history),
            'traceability_maps_size': len(self.traceability_maps),
            'analysis_system_operational': True
        }
    
    def _get_primary_responsibility(self) -> str:
        """Define the single primary responsibility of this module"""
        return "Systematically merge overlapping specs while preserving all functionality"
    
    def create_consolidation_plan(self, overlap_analysis: OverlapAnalysis) -> ConsolidationPlan:
        """
        Create detailed consolidation plan based on overlap analysis
        
        This method orchestrates the consolidation process by creating a comprehensive
        plan that addresses all aspects of merging overlapping specifications.
        """
        try:
            self.logger.info("Creating consolidation plan from overlap analysis")
            
            # Select the best consolidation opportunity
            if not overlap_analysis.consolidation_opportunities:
                raise ValueError("No consolidation opportunities found in analysis")
            
            primary_opportunity = overlap_analysis.consolidation_opportunities[0]  # Highest priority
            target_specs = primary_opportunity.target_specs
            
            # Generate unified spec name
            unified_spec_name = self._generate_unified_spec_name(target_specs)
            
            # Create requirement mapping through intelligent merging
            requirement_mapping = self._create_requirement_mapping(target_specs, overlap_analysis)
            
            # Plan interface standardization
            interface_standardization = self._plan_interface_standardization(target_specs, overlap_analysis)
            
            # Plan terminology unification
            terminology_unification = self._plan_terminology_unification(target_specs, overlap_analysis)
            
            # Create migration steps
            migration_steps = self._create_migration_steps(target_specs, primary_opportunity)
            
            # Define validation criteria
            validation_criteria = self._define_validation_criteria(target_specs, overlap_analysis)
            
            # Calculate effort and create risk mitigation
            estimated_effort = primary_opportunity.effort_estimate
            risk_mitigation = self._create_risk_mitigation_plan(primary_opportunity)
            
            # Define success metrics
            success_metrics = self._define_success_metrics(target_specs, overlap_analysis)
            
            plan = ConsolidationPlan(
                plan_id=self._generate_plan_id(),
                target_specs=target_specs,
                unified_spec_name=unified_spec_name,
                consolidation_strategy=primary_opportunity.recommended_strategy,
                requirement_mapping=requirement_mapping,
                interface_standardization=interface_standardization,
                terminology_unification=terminology_unification,
                migration_steps=migration_steps,
                validation_criteria=validation_criteria,
                estimated_effort=estimated_effort,
                risk_mitigation=risk_mitigation,
                success_metrics=success_metrics
            )
            
            self.consolidation_history.append(plan)
            return plan
            
        except Exception as e:
            self.logger.error(f"Error creating consolidation plan: {e}")
            raise
    
    def merge_requirements(self, overlapping_requirements: List[RequirementAnalysis]) -> 'UnifiedRequirement':
        """
        Implement semantic analysis to identify functionally equivalent requirements
        Create conflict resolution workflows with automated and manual resolution options
        Build requirement quality assessment to identify gaps and inconsistencies
        Implement validation system ensuring merged requirements maintain original intent
        """
        try:
            self.logger.info(f"Merging {len(overlapping_requirements)} overlapping requirements")
            
            if not overlapping_requirements:
                raise ValueError("No requirements provided for merging")
            
            # Group functionally equivalent requirements
            equivalent_groups = self._group_functionally_equivalent_requirements(overlapping_requirements)
            
            # Merge each group of equivalent requirements
            merged_requirements = []
            for group in equivalent_groups:
                if len(group) > 1:
                    # Multiple requirements need merging
                    merged_req = self._merge_requirement_group(group)
                    merged_requirements.append(merged_req)
                else:
                    # Single requirement, convert to unified format
                    unified_req = self._convert_to_unified_requirement(group[0])
                    merged_requirements.append(unified_req)
            
            # Validate merged requirements maintain original intent
            validation_result = self._validate_merged_requirements(overlapping_requirements, merged_requirements)
            
            if not validation_result['is_valid']:
                self.logger.warning(f"Validation issues found: {validation_result['issues']}")
            
            # Create final unified requirement
            unified_requirement = self._create_unified_requirement(merged_requirements, validation_result)
            
            return unified_requirement
            
        except Exception as e:
            self.logger.error(f"Error merging requirements: {e}")
            raise
    
    def _group_functionally_equivalent_requirements(self, requirements: List[RequirementAnalysis]) -> List[List[RequirementAnalysis]]:
        """Group requirements that are functionally equivalent using semantic analysis"""
        groups = []
        processed = set()
        
        for i, req1 in enumerate(requirements):
            if req1.requirement_id in processed:
                continue
                
            # Start new group with this requirement
            current_group = [req1]
            processed.add(req1.requirement_id)
            
            # Find all requirements equivalent to this one
            for j, req2 in enumerate(requirements[i+1:], i+1):
                if req2.requirement_id in processed:
                    continue
                    
                if self._are_functionally_equivalent(req1, req2):
                    current_group.append(req2)
                    processed.add(req2.requirement_id)
            
            groups.append(current_group)
        
        return groups
    
    def _are_functionally_equivalent(self, req1: RequirementAnalysis, req2: RequirementAnalysis) -> bool:
        """Determine if two requirements are functionally equivalent using semantic analysis"""
        # Calculate keyword overlap
        keyword_overlap = len(req1.functionality_keywords.intersection(req2.functionality_keywords))
        keyword_union = len(req1.functionality_keywords.union(req2.functionality_keywords))
        keyword_similarity = keyword_overlap / keyword_union if keyword_union > 0 else 0
        
        # Check stakeholder overlap
        stakeholder_overlap = len(set(req1.stakeholder_personas).intersection(set(req2.stakeholder_personas)))
        stakeholder_similarity = stakeholder_overlap > 0
        
        # Check acceptance criteria similarity
        criteria_similarity = self._calculate_criteria_similarity(req1.acceptance_criteria, req2.acceptance_criteria)
        
        # Requirements are equivalent if they have high similarity across multiple dimensions
        return (
            keyword_similarity > 0.6 and
            stakeholder_similarity and
            criteria_similarity > 0.5
        )
    
    def _calculate_criteria_similarity(self, criteria1: List[str], criteria2: List[str]) -> float:
        """Calculate similarity between acceptance criteria lists"""
        if not criteria1 or not criteria2:
            return 0.0
        
        # Extract keywords from criteria
        keywords1 = set()
        keywords2 = set()
        
        for criterion in criteria1:
            keywords1.update(self._extract_meaningful_words(criterion))
        
        for criterion in criteria2:
            keywords2.update(self._extract_meaningful_words(criterion))
        
        # Calculate keyword overlap
        if not keywords1 or not keywords2:
            return 0.0
        
        intersection = keywords1.intersection(keywords2)
        union = keywords1.union(keywords2)
        
        return len(intersection) / len(union)
    
    def _merge_requirement_group(self, requirement_group: List[RequirementAnalysis]) -> 'UnifiedRequirement':
        """Merge a group of functionally equivalent requirements"""
        # Select the highest quality requirement as base
        base_requirement = max(requirement_group, key=lambda r: r.quality_score)
        
        # Merge functionality keywords from all requirements
        merged_keywords = set()
        for req in requirement_group:
            merged_keywords.update(req.functionality_keywords)
        
        # Merge acceptance criteria, removing duplicates
        merged_criteria = []
        seen_criteria = set()
        
        for req in requirement_group:
            for criterion in req.acceptance_criteria:
                criterion_keywords = frozenset(self._extract_meaningful_words(criterion))
                if criterion_keywords not in seen_criteria:
                    merged_criteria.append(criterion)
                    seen_criteria.add(criterion_keywords)
        
        # Merge stakeholder personas
        merged_personas = list(set(persona for req in requirement_group for persona in req.stakeholder_personas))
        
        # Create conflict resolution record
        conflicts_resolved = self._identify_and_resolve_conflicts(requirement_group)
        
        # Calculate merged quality and complexity scores
        merged_quality_score = max(req.quality_score for req in requirement_group)
        merged_complexity_score = sum(req.complexity_score for req in requirement_group) / len(requirement_group)
        
        return UnifiedRequirement(
            unified_id=f"UR_{self._generate_requirement_id()}",
            original_requirements=[req.requirement_id for req in requirement_group],
            merged_content=self._create_merged_content(base_requirement, merged_criteria, merged_personas),
            functionality_keywords=merged_keywords,
            acceptance_criteria=merged_criteria,
            stakeholder_personas=merged_personas,
            quality_score=merged_quality_score,
            complexity_score=merged_complexity_score,
            conflicts_resolved=conflicts_resolved,
            merge_strategy=self._determine_merge_strategy(requirement_group),
            validation_status="pending"
        )
    
    def _convert_to_unified_requirement(self, requirement: RequirementAnalysis) -> 'UnifiedRequirement':
        """Convert a single requirement to unified format"""
        return UnifiedRequirement(
            unified_id=f"UR_{self._generate_requirement_id()}",
            original_requirements=[requirement.requirement_id],
            merged_content=requirement.content,
            functionality_keywords=requirement.functionality_keywords,
            acceptance_criteria=requirement.acceptance_criteria,
            stakeholder_personas=requirement.stakeholder_personas,
            quality_score=requirement.quality_score,
            complexity_score=requirement.complexity_score,
            conflicts_resolved=[],
            merge_strategy="no_merge_needed",
            validation_status="pending"
        )
    
    def _identify_and_resolve_conflicts(self, requirement_group: List[RequirementAnalysis]) -> List[Dict[str, Any]]:
        """Identify and resolve conflicts between requirements in a group"""
        conflicts_resolved = []
        
        # Check for conflicting acceptance criteria
        all_criteria = []
        for req in requirement_group:
            for criterion in req.acceptance_criteria:
                all_criteria.append((req.requirement_id, criterion))
        
        # Look for contradictory statements
        for i, (req_id1, criterion1) in enumerate(all_criteria):
            for req_id2, criterion2 in all_criteria[i+1:]:
                if self._are_contradictory_criteria(criterion1, criterion2):
                    # Resolve conflict by choosing more specific criterion
                    resolution = self._resolve_contradictory_criteria(criterion1, criterion2, req_id1, req_id2)
                    conflicts_resolved.append(resolution)
        
        return conflicts_resolved
    
    def _are_contradictory_criteria(self, criterion1: str, criterion2: str) -> bool:
        """Check if two criteria are contradictory"""
        # Look for explicit contradictions
        contradictory_patterns = [
            (r'SHALL\s+([^.]+)', r'SHALL\s+NOT\s+\1'),  # SHALL vs SHALL NOT
            (r'MUST\s+([^.]+)', r'MUST\s+NOT\s+\1'),    # MUST vs MUST NOT
            (r'WHEN\s+([^T]+)\s+THEN\s+([^.]+)', r'WHEN\s+\1\s+THEN\s+(?!.*\2)'),  # Different outcomes for same condition
        ]
        
        for positive_pattern, negative_pattern in contradictory_patterns:
            positive_match = re.search(positive_pattern, criterion1, re.IGNORECASE)
            negative_match = re.search(negative_pattern, criterion2, re.IGNORECASE)
            
            if positive_match and negative_match:
                return True
        
        return False
    
    def _resolve_contradictory_criteria(self, criterion1: str, criterion2: str, req_id1: str, req_id2: str) -> Dict[str, Any]:
        """Resolve contradictory criteria by selecting the more specific one"""
        # Choose the more specific criterion (longer, more detailed)
        if len(criterion1) > len(criterion2):
            chosen_criterion = criterion1
            chosen_req = req_id1
            rejected_criterion = criterion2
            rejected_req = req_id2
        else:
            chosen_criterion = criterion2
            chosen_req = req_id2
            rejected_criterion = criterion1
            rejected_req = req_id1
        
        return {
            'conflict_type': 'contradictory_criteria',
            'chosen_criterion': chosen_criterion,
            'chosen_from_requirement': chosen_req,
            'rejected_criterion': rejected_criterion,
            'rejected_from_requirement': rejected_req,
            'resolution_strategy': 'prioritize_more_detailed',
            'rationale': 'Selected more detailed and specific criterion'
        }
    
    def _determine_merge_strategy(self, requirement_group: List[RequirementAnalysis]) -> str:
        """Determine the strategy used to merge requirements"""
        if len(requirement_group) == 1:
            return "no_merge_needed"
        elif all(req.quality_score > 0.7 for req in requirement_group):
            return "high_quality_merge"
        elif any(req.complexity_score > 0.8 for req in requirement_group):
            return "complex_merge_with_review"
        else:
            return "standard_merge"
    
    def _create_merged_content(self, base_requirement: RequirementAnalysis, 
                             merged_criteria: List[str], merged_personas: List[str]) -> str:
        """Create merged content for unified requirement"""
        # Extract user story from base requirement
        user_story_match = re.search(r'\*\*User Story:\*\*([^#]+)', base_requirement.content)
        user_story = user_story_match.group(1).strip() if user_story_match else ""
        
        # Update user story to include all personas if multiple
        if len(merged_personas) > 1:
            persona_list = ", ".join(merged_personas)
            user_story = re.sub(r'As a [^,]+,', f'As a {persona_list},', user_story)
        
        # Create merged content
        merged_content = f"""**User Story:** {user_story}

#### Acceptance Criteria

"""
        
        for i, criterion in enumerate(merged_criteria, 1):
            merged_content += f"{i}. {criterion}\n"
        
        return merged_content
    
    def _validate_merged_requirements(self, original_requirements: List[RequirementAnalysis], 
                                    merged_requirements: List['UnifiedRequirement']) -> Dict[str, Any]:
        """Validate that merged requirements maintain original intent"""
        validation_result = {
            'is_valid': True,
            'issues': [],
            'coverage_analysis': {},
            'quality_assessment': {}
        }
        
        # Check coverage - all original functionality should be preserved
        original_keywords = set()
        for req in original_requirements:
            original_keywords.update(req.functionality_keywords)
        
        merged_keywords = set()
        for req in merged_requirements:
            merged_keywords.update(req.functionality_keywords)
        
        missing_keywords = original_keywords - merged_keywords
        if missing_keywords:
            validation_result['is_valid'] = False
            validation_result['issues'].append(f"Missing functionality keywords: {missing_keywords}")
        
        validation_result['coverage_analysis'] = {
            'original_keyword_count': len(original_keywords),
            'merged_keyword_count': len(merged_keywords),
            'coverage_percentage': len(merged_keywords.intersection(original_keywords)) / len(original_keywords) if original_keywords else 1.0,
            'missing_keywords': list(missing_keywords)
        }
        
        # Check quality - merged requirements should maintain or improve quality
        original_avg_quality = sum(req.quality_score for req in original_requirements) / len(original_requirements)
        merged_avg_quality = sum(req.quality_score for req in merged_requirements) / len(merged_requirements)
        
        if merged_avg_quality < original_avg_quality * 0.9:  # Allow 10% quality reduction
            validation_result['issues'].append("Significant quality reduction in merged requirements")
        
        validation_result['quality_assessment'] = {
            'original_average_quality': original_avg_quality,
            'merged_average_quality': merged_avg_quality,
            'quality_change': merged_avg_quality - original_avg_quality
        }
        
        return validation_result
    
    def _create_unified_requirement(self, merged_requirements: List['UnifiedRequirement'], 
                                  validation_result: Dict[str, Any]) -> 'UnifiedRequirement':
        """Create final unified requirement from merged requirements"""
        # If only one merged requirement, return it with validation status
        if len(merged_requirements) == 1:
            unified_req = merged_requirements[0]
            unified_req.validation_status = "validated" if validation_result['is_valid'] else "validation_failed"
            return unified_req
        
        # If multiple merged requirements, create a composite
        all_keywords = set()
        all_criteria = []
        all_personas = []
        all_original_reqs = []
        
        for req in merged_requirements:
            all_keywords.update(req.functionality_keywords)
            all_criteria.extend(req.acceptance_criteria)
            all_personas.extend(req.stakeholder_personas)
            all_original_reqs.extend(req.original_requirements)
        
        # Remove duplicate personas and criteria
        unique_personas = list(set(all_personas))
        unique_criteria = list(dict.fromkeys(all_criteria))  # Preserves order while removing duplicates
        
        return UnifiedRequirement(
            unified_id=f"UR_COMPOSITE_{self._generate_requirement_id()}",
            original_requirements=list(set(all_original_reqs)),
            merged_content=self._create_composite_content(unique_criteria, unique_personas),
            functionality_keywords=all_keywords,
            acceptance_criteria=unique_criteria,
            stakeholder_personas=unique_personas,
            quality_score=validation_result['quality_assessment']['merged_average_quality'],
            complexity_score=sum(req.complexity_score for req in merged_requirements) / len(merged_requirements),
            conflicts_resolved=[conflict for req in merged_requirements for conflict in req.conflicts_resolved],
            merge_strategy="composite_merge",
            validation_status="validated" if validation_result['is_valid'] else "validation_failed"
        )
    
    def _create_composite_content(self, criteria: List[str], personas: List[str]) -> str:
        """Create content for composite unified requirement"""
        persona_text = ", ".join(personas) if len(personas) > 1 else personas[0] if personas else "system user"
        
        content = f"""**User Story:** As a {persona_text}, I want the consolidated functionality from multiple overlapping requirements, so that all stakeholder needs are addressed in a unified manner.

#### Acceptance Criteria

"""
        
        for i, criterion in enumerate(criteria, 1):
            content += f"{i}. {criterion}\n"
        
        return content
    
    def _generate_requirement_id(self) -> str:
        """Generate unique requirement ID"""
        import time
        return f"{int(time.time())}"
    
    def _generate_plan_id(self) -> str:
        """Generate unique consolidation plan ID"""
        import time
        return f"PLAN_{int(time.time())}"


@dataclass
class UnifiedRequirement:
    """Represents a unified requirement created from merging multiple overlapping requirements"""
    unified_id: str
    original_requirements: List[str]
    merged_content: str
    functionality_keywords: Set[str]
    acceptance_criteria: List[str]
    stakeholder_personas: List[str]
    quality_score: float
    complexity_score: float
    conflicts_resolved: List[Dict[str, Any]]
    merge_strategy: str
    validation_status: str    
    
    def preserve_traceability(self, original_specs: List[str], unified_spec: str) -> TraceabilityMap:
        """
        Implement bidirectional traceability linking from original to consolidated requirements
        Create impact analysis system showing effects of consolidation on existing implementations
        Build change tracking system documenting all consolidation decisions and rationale
        Implement validation system ensuring traceability completeness and accuracy
        """
        try:
            self.logger.info(f"Creating traceability map for consolidation: {original_specs} -> {unified_spec}")
            
            consolidation_id = f"CONSOLIDATION_{self._generate_requirement_id()}"
            
            # Create traceability links for all requirements
            traceability_links = self._create_traceability_links(original_specs, unified_spec, consolidation_id)
            
            # Perform impact analysis
            impact_analysis = self._perform_impact_analysis(original_specs, unified_spec, traceability_links)
            
            # Create change tracking log
            change_log = self._create_change_tracking_log(original_specs, unified_spec, traceability_links)
            
            # Validate traceability completeness and accuracy
            validation_status = self._validate_traceability_completeness(original_specs, traceability_links)
            
            traceability_map = TraceabilityMap(
                consolidation_id=consolidation_id,
                links=traceability_links,
                impact_analysis=impact_analysis,
                change_log=change_log,
                validation_status=validation_status
            )
            
            # Store traceability map for future reference
            self.traceability_maps[consolidation_id] = traceability_map
            
            return traceability_map
            
        except Exception as e:
            self.logger.error(f"Error preserving traceability: {e}")
            raise
    
    def _create_traceability_links(self, original_specs: List[str], unified_spec: str, consolidation_id: str) -> List[TraceabilityLink]:
        """Create bidirectional traceability links between original and consolidated requirements"""
        traceability_links = []
        
        # Load original specs and extract requirements
        original_requirements = {}
        for spec_name in original_specs:
            spec_data = self._parse_spec_comprehensively(spec_name)
            if spec_data:
                original_requirements[spec_name] = spec_data['requirements']
        
        # Load unified spec requirements (if it exists)
        unified_requirements = []
        unified_spec_path = self.specs_directory / unified_spec
        if unified_spec_path.exists():
            unified_data = self._parse_spec_comprehensively(unified_spec)
            if unified_data:
                unified_requirements = unified_data['requirements']
        
        # Create links based on consolidation history
        consolidation_plan = self._find_consolidation_plan_for_specs(original_specs)
        
        if consolidation_plan and consolidation_plan.requirement_mapping:
            # Use explicit mapping from consolidation plan
            for original_req_id, unified_req_id in consolidation_plan.requirement_mapping.items():
                # Find the original spec that contains this requirement
                original_spec = self._find_spec_containing_requirement(original_req_id, original_requirements)
                
                if original_spec:
                    transformation_type = self._determine_transformation_type(
                        original_req_id, unified_req_id, consolidation_plan
                    )
                    
                    rationale = self._generate_transformation_rationale(
                        original_req_id, unified_req_id, transformation_type, consolidation_plan
                    )
                    
                    traceability_links.append(TraceabilityLink(
                        original_spec=original_spec,
                        original_requirement_id=original_req_id,
                        consolidated_spec=unified_spec,
                        consolidated_requirement_id=unified_req_id,
                        transformation_type=transformation_type,
                        rationale=rationale
                    ))
        else:
            # Create links based on semantic similarity
            traceability_links = self._create_semantic_traceability_links(
                original_requirements, unified_requirements, unified_spec, consolidation_id
            )
        
        return traceability_links
    
    def _create_semantic_traceability_links(self, original_requirements: Dict[str, List[RequirementAnalysis]], 
                                          unified_requirements: List[RequirementAnalysis], 
                                          unified_spec: str, consolidation_id: str) -> List[TraceabilityLink]:
        """Create traceability links based on semantic similarity when explicit mapping is not available"""
        traceability_links = []
        
        for spec_name, requirements in original_requirements.items():
            for original_req in requirements:
                # Find the most similar unified requirement
                best_match = None
                best_similarity = 0.0
                
                for unified_req in unified_requirements:
                    similarity = self._calculate_requirement_similarity(original_req, unified_req)
                    if similarity > best_similarity and similarity > 0.3:  # Minimum similarity threshold
                        best_similarity = similarity
                        best_match = unified_req
                
                if best_match:
                    transformation_type = self._infer_transformation_type(original_req, best_match, best_similarity)
                    rationale = f"Semantic similarity: {best_similarity:.2f}. {self._generate_similarity_rationale(original_req, best_match)}"
                    
                    traceability_links.append(TraceabilityLink(
                        original_spec=spec_name,
                        original_requirement_id=original_req.requirement_id,
                        consolidated_spec=unified_spec,
                        consolidated_requirement_id=best_match.requirement_id,
                        transformation_type=transformation_type,
                        rationale=rationale
                    ))
                else:
                    # No match found - requirement may have been deprecated
                    traceability_links.append(TraceabilityLink(
                        original_spec=spec_name,
                        original_requirement_id=original_req.requirement_id,
                        consolidated_spec=unified_spec,
                        consolidated_requirement_id="DEPRECATED",
                        transformation_type="deprecated",
                        rationale="No matching requirement found in consolidated spec - functionality may have been deprecated or absorbed into other requirements"
                    ))
        
        return traceability_links
    
    def _calculate_requirement_similarity(self, req1: RequirementAnalysis, req2: RequirementAnalysis) -> float:
        """Calculate similarity between two requirements"""
        # Keyword similarity
        keyword_intersection = req1.functionality_keywords.intersection(req2.functionality_keywords)
        keyword_union = req1.functionality_keywords.union(req2.functionality_keywords)
        keyword_similarity = len(keyword_intersection) / len(keyword_union) if keyword_union else 0
        
        # Stakeholder similarity
        stakeholder_intersection = set(req1.stakeholder_personas).intersection(set(req2.stakeholder_personas))
        stakeholder_union = set(req1.stakeholder_personas).union(set(req2.stakeholder_personas))
        stakeholder_similarity = len(stakeholder_intersection) / len(stakeholder_union) if stakeholder_union else 0
        
        # Content similarity (simple word overlap)
        content1_words = set(self._extract_meaningful_words(req1.content))
        content2_words = set(self._extract_meaningful_words(req2.content))
        content_intersection = content1_words.intersection(content2_words)
        content_union = content1_words.union(content2_words)
        content_similarity = len(content_intersection) / len(content_union) if content_union else 0
        
        # Weighted average
        return (keyword_similarity * 0.5 + stakeholder_similarity * 0.2 + content_similarity * 0.3)
    
    def _infer_transformation_type(self, original_req: RequirementAnalysis, unified_req: RequirementAnalysis, similarity: float) -> str:
        """Infer transformation type based on similarity and characteristics"""
        if similarity > 0.9:
            return "unchanged"
        elif similarity > 0.7:
            return "merged"
        elif similarity > 0.5:
            return "split"
        else:
            return "transformed"
    
    def _generate_similarity_rationale(self, original_req: RequirementAnalysis, unified_req: RequirementAnalysis) -> str:
        """Generate rationale for similarity-based traceability"""
        shared_keywords = original_req.functionality_keywords.intersection(unified_req.functionality_keywords)
        shared_personas = set(original_req.stakeholder_personas).intersection(set(unified_req.stakeholder_personas))
        
        rationale_parts = []
        
        if shared_keywords:
            rationale_parts.append(f"Shared functionality: {', '.join(list(shared_keywords)[:3])}")
        
        if shared_personas:
            rationale_parts.append(f"Common stakeholders: {', '.join(list(shared_personas))}")
        
        return ". ".join(rationale_parts) if rationale_parts else "General content similarity"
    
    def _perform_impact_analysis(self, original_specs: List[str], unified_spec: str, 
                               traceability_links: List[TraceabilityLink]) -> Dict[str, List[str]]:
        """Perform impact analysis showing effects of consolidation on existing implementations"""
        impact_analysis = {
            'affected_implementations': [],
            'deprecated_functionality': [],
            'new_requirements': [],
            'interface_changes': [],
            'migration_requirements': []
        }
        
        # Analyze affected implementations
        for spec_name in original_specs:
            # Look for existing implementations that reference this spec
            implementations = self._find_implementations_referencing_spec(spec_name)
            impact_analysis['affected_implementations'].extend(implementations)
        
        # Identify deprecated functionality
        deprecated_links = [link for link in traceability_links if link.transformation_type == "deprecated"]
        for link in deprecated_links:
            impact_analysis['deprecated_functionality'].append(
                f"{link.original_spec}:{link.original_requirement_id} - {link.rationale}"
            )
        
        # Identify new requirements (in unified spec but not in originals)
        unified_req_ids = set(link.consolidated_requirement_id for link in traceability_links)
        unified_data = self._parse_spec_comprehensively(unified_spec)
        if unified_data:
            all_unified_reqs = set(req.requirement_id for req in unified_data['requirements'])
            new_reqs = all_unified_reqs - unified_req_ids
            impact_analysis['new_requirements'] = list(new_reqs)
        
        # Analyze interface changes
        interface_changes = self._analyze_interface_changes(original_specs, unified_spec)
        impact_analysis['interface_changes'] = interface_changes
        
        # Determine migration requirements
        migration_reqs = self._determine_migration_requirements(traceability_links, interface_changes)
        impact_analysis['migration_requirements'] = migration_reqs
        
        return impact_analysis
    
    def _find_implementations_referencing_spec(self, spec_name: str) -> List[str]:
        """Find implementations that reference a specific spec"""
        implementations = []
        
        # Search for references in source code
        src_directory = Path("src")
        if src_directory.exists():
            for py_file in src_directory.rglob("*.py"):
                try:
                    content = py_file.read_text()
                    if spec_name.replace("-", "_") in content or spec_name in content:
                        implementations.append(str(py_file))
                except Exception:
                    continue
        
        # Search for references in tests
        tests_directory = Path("tests")
        if tests_directory.exists():
            for py_file in tests_directory.rglob("*.py"):
                try:
                    content = py_file.read_text()
                    if spec_name.replace("-", "_") in content or spec_name in content:
                        implementations.append(str(py_file))
                except Exception:
                    continue
        
        return implementations
    
    def _analyze_interface_changes(self, original_specs: List[str], unified_spec: str) -> List[str]:
        """Analyze interface changes between original and unified specs"""
        interface_changes = []
        
        # Collect interfaces from original specs
        original_interfaces = {}
        for spec_name in original_specs:
            spec_data = self._parse_spec_comprehensively(spec_name)
            if spec_data:
                for interface in spec_data['interfaces']:
                    original_interfaces[interface['name']] = interface
        
        # Collect interfaces from unified spec
        unified_interfaces = {}
        unified_data = self._parse_spec_comprehensively(unified_spec)
        if unified_data:
            for interface in unified_data['interfaces']:
                unified_interfaces[interface['name']] = interface
        
        # Compare interfaces
        for interface_name, original_interface in original_interfaces.items():
            if interface_name in unified_interfaces:
                unified_interface = unified_interfaces[interface_name]
                if original_interface != unified_interface:
                    interface_changes.append(f"Modified interface: {interface_name}")
            else:
                interface_changes.append(f"Removed interface: {interface_name}")
        
        # Check for new interfaces
        for interface_name in unified_interfaces:
            if interface_name not in original_interfaces:
                interface_changes.append(f"New interface: {interface_name}")
        
        return interface_changes
    
    def _determine_migration_requirements(self, traceability_links: List[TraceabilityLink], 
                                        interface_changes: List[str]) -> List[str]:
        """Determine migration requirements based on traceability and interface changes"""
        migration_requirements = []
        
        # Requirements based on transformation types
        transformation_counts = {}
        for link in traceability_links:
            transformation_counts[link.transformation_type] = transformation_counts.get(link.transformation_type, 0) + 1
        
        if transformation_counts.get('deprecated', 0) > 0:
            migration_requirements.append(f"Remove {transformation_counts['deprecated']} deprecated requirements from implementations")
        
        if transformation_counts.get('merged', 0) > 0:
            migration_requirements.append(f"Update {transformation_counts['merged']} merged requirements in implementations")
        
        if transformation_counts.get('split', 0) > 0:
            migration_requirements.append(f"Refactor {transformation_counts['split']} split requirements in implementations")
        
        # Requirements based on interface changes
        if interface_changes:
            migration_requirements.append(f"Update implementations for {len(interface_changes)} interface changes")
        
        return migration_requirements
    
    def _create_change_tracking_log(self, original_specs: List[str], unified_spec: str, 
                                  traceability_links: List[TraceabilityLink]) -> List[Dict[str, Any]]:
        """Create change tracking log documenting all consolidation decisions and rationale"""
        change_log = []
        
        # Log consolidation initiation
        change_log.append({
            'timestamp': datetime.now().isoformat(),
            'change_type': 'consolidation_initiated',
            'description': f"Started consolidation of specs: {', '.join(original_specs)} into {unified_spec}",
            'rationale': 'Eliminate spec fragmentation and improve architectural consistency',
            'affected_specs': original_specs + [unified_spec]
        })
        
        # Log each traceability transformation
        for link in traceability_links:
            change_log.append({
                'timestamp': datetime.now().isoformat(),
                'change_type': f'requirement_{link.transformation_type}',
                'description': f"Requirement {link.original_requirement_id} from {link.original_spec} {link.transformation_type} to {link.consolidated_requirement_id} in {link.consolidated_spec}",
                'rationale': link.rationale,
                'affected_specs': [link.original_spec, link.consolidated_spec],
                'original_requirement': link.original_requirement_id,
                'consolidated_requirement': link.consolidated_requirement_id
            })
        
        # Log consolidation completion
        change_log.append({
            'timestamp': datetime.now().isoformat(),
            'change_type': 'consolidation_completed',
            'description': f"Completed consolidation with {len(traceability_links)} traceability links established",
            'rationale': 'Consolidation process completed with full traceability preservation',
            'affected_specs': original_specs + [unified_spec],
            'metrics': {
                'traceability_links_created': len(traceability_links),
                'transformation_types': {t_type: len([l for l in traceability_links if l.transformation_type == t_type]) 
                                       for t_type in set(l.transformation_type for l in traceability_links)}
            }
        })
        
        return change_log
    
    def _validate_traceability_completeness(self, original_specs: List[str], 
                                          traceability_links: List[TraceabilityLink]) -> Dict[str, bool]:
        """Validate traceability completeness and accuracy"""
        validation_status = {}
        
        # Check that all original requirements have traceability links
        for spec_name in original_specs:
            spec_data = self._parse_spec_comprehensively(spec_name)
            if spec_data:
                original_req_ids = set(req.requirement_id for req in spec_data['requirements'])
                linked_req_ids = set(link.original_requirement_id for link in traceability_links 
                                   if link.original_spec == spec_name)
                
                missing_links = original_req_ids - linked_req_ids
                validation_status[f"{spec_name}_complete_traceability"] = len(missing_links) == 0
                
                if missing_links:
                    self.logger.warning(f"Missing traceability links for requirements in {spec_name}: {missing_links}")
        
        # Check bidirectional consistency
        validation_status['bidirectional_consistency'] = self._validate_bidirectional_consistency(traceability_links)
        
        # Check for duplicate links
        link_signatures = [(link.original_spec, link.original_requirement_id) for link in traceability_links]
        validation_status['no_duplicate_links'] = len(link_signatures) == len(set(link_signatures))
        
        # Overall validation
        validation_status['overall_valid'] = all(validation_status.values())
        
        return validation_status
    
    def _validate_bidirectional_consistency(self, traceability_links: List[TraceabilityLink]) -> bool:
        """Validate that traceability links are bidirectionally consistent"""
        # For now, this is a placeholder - in a full implementation, this would check
        # that consolidated requirements properly reference their original sources
        return True
    
    def _find_consolidation_plan_for_specs(self, spec_names: List[str]) -> Optional[ConsolidationPlan]:
        """Find consolidation plan that matches the given specs"""
        for plan in self.consolidation_history:
            if set(plan.target_specs) == set(spec_names):
                return plan
        return None
    
    def _find_spec_containing_requirement(self, requirement_id: str, 
                                        original_requirements: Dict[str, List[RequirementAnalysis]]) -> Optional[str]:
        """Find which spec contains a specific requirement"""
        for spec_name, requirements in original_requirements.items():
            for req in requirements:
                if req.requirement_id == requirement_id:
                    return spec_name
        return None
    
    def _determine_transformation_type(self, original_req_id: str, unified_req_id: str, 
                                     consolidation_plan: ConsolidationPlan) -> str:
        """Determine transformation type based on consolidation plan"""
        # This would be determined based on the consolidation strategy and mapping
        # For now, using simple heuristics
        if unified_req_id == "DEPRECATED":
            return "deprecated"
        elif original_req_id == unified_req_id:
            return "unchanged"
        else:
            return "merged"  # Default assumption
    
    def _generate_transformation_rationale(self, original_req_id: str, unified_req_id: str, 
                                         transformation_type: str, consolidation_plan: ConsolidationPlan) -> str:
        """Generate rationale for requirement transformation"""
        rationale_map = {
            "merged": f"Requirement merged as part of {consolidation_plan.consolidation_strategy.value} strategy",
            "split": f"Requirement split to improve clarity as part of {consolidation_plan.consolidation_strategy.value} strategy",
            "unchanged": "Requirement preserved without changes",
            "deprecated": "Requirement deprecated due to functional overlap or obsolescence"
        }
        
        return rationale_map.get(transformation_type, f"Requirement transformed using {consolidation_plan.consolidation_strategy.value} strategy") 
   
    # Helper methods for consolidation plan creation
    def _generate_unified_spec_name(self, target_specs: List[str]) -> str:
        """Generate a name for the unified specification"""
        # Extract common themes from spec names
        common_words = set()
        for spec in target_specs:
            words = spec.replace("-", " ").split()
            if not common_words:
                common_words = set(words)
            else:
                common_words = common_words.intersection(set(words))
        
        if common_words:
            base_name = "-".join(sorted(common_words))
        else:
            # Use first spec as base and add "unified"
            base_name = target_specs[0].split("-")[0] + "-unified"
        
        return f"{base_name}-consolidated"
    
    def _create_requirement_mapping(self, target_specs: List[str], overlap_analysis: OverlapAnalysis) -> Dict[str, str]:
        """Create mapping from original requirements to unified requirements"""
        requirement_mapping = {}
        
        # Load all requirements from target specs
        all_requirements = []
        for spec_name in target_specs:
            spec_data = self._parse_spec_comprehensively(spec_name)
            if spec_data:
                for req in spec_data['requirements']:
                    req.spec_source = spec_name  # Add source tracking
                    all_requirements.append(req)
        
        # Merge overlapping requirements
        unified_requirement = self.merge_requirements(all_requirements)
        
        # Create mapping based on merge results
        if hasattr(unified_requirement, 'original_requirements'):
            for original_req_id in unified_requirement.original_requirements:
                requirement_mapping[original_req_id] = unified_requirement.unified_id
        
        return requirement_mapping
    
    def _plan_interface_standardization(self, target_specs: List[str], overlap_analysis: OverlapAnalysis) -> List[InterfaceChange]:
        """Plan interface standardization changes"""
        interface_changes = []
        
        # Analyze interface conflicts from overlap analysis
        for interface_name, conflicting_specs in overlap_analysis.interface_conflicts.items():
            if len(conflicting_specs) > 1:
                # Choose the most complete interface as standard
                best_interface = self._select_best_interface(interface_name, conflicting_specs)
                
                interface_changes.append(InterfaceChange(
                    original_interface=interface_name,
                    standardized_interface=best_interface['definition'],
                    affected_specs=conflicting_specs,
                    migration_guidance=f"Standardize {interface_name} interface across all specs using ReflectiveModule pattern"
                ))
        
        return interface_changes
    
    def _select_best_interface(self, interface_name: str, conflicting_specs: List[str]) -> Dict[str, Any]:
        """Select the best interface definition from conflicting specs"""
        # For now, select the first one - in practice, this would use more sophisticated logic
        spec_data = self._parse_spec_comprehensively(conflicting_specs[0])
        if spec_data:
            for interface in spec_data['interfaces']:
                if interface['name'] == interface_name:
                    return {
                        'definition': f"class {interface_name}(ReflectiveModule): ...",
                        'source_spec': conflicting_specs[0]
                    }
        
        return {'definition': f"class {interface_name}(ReflectiveModule): ...", 'source_spec': 'default'}
    
    def _plan_terminology_unification(self, target_specs: List[str], overlap_analysis: OverlapAnalysis) -> List[TerminologyChange]:
        """Plan terminology unification changes"""
        terminology_changes = []
        
        # Analyze terminology conflicts from overlap analysis
        for term, conflicting_specs in overlap_analysis.terminology_conflicts.items():
            if len(conflicting_specs) > 1:
                # Choose the most commonly used definition
                unified_term = self._select_unified_terminology(term, conflicting_specs)
                
                terminology_changes.append(TerminologyChange(
                    original_terms=[term],  # Could be multiple variants
                    unified_term=unified_term['term'],
                    affected_specs=conflicting_specs,
                    definition=unified_term['definition']
                ))
        
        return terminology_changes
    
    def _select_unified_terminology(self, term: str, conflicting_specs: List[str]) -> Dict[str, str]:
        """Select unified terminology from conflicting definitions"""
        # For now, use the term as-is with a standard definition
        return {
            'term': term,
            'definition': f"Standardized definition of {term} across all consolidated specifications"
        }
    
    def _create_migration_steps(self, target_specs: List[str], opportunity: ConsolidationOpportunity) -> List[MigrationStep]:
        """Create detailed migration steps"""
        migration_steps = []
        
        # Step 1: Backup original specs
        migration_steps.append(MigrationStep(
            step_id="BACKUP_001",
            description="Create backup of original specifications",
            prerequisites=[],
            actions=[
                f"Create backup directory for specs: {', '.join(target_specs)}",
                "Copy all original spec files to backup location",
                "Verify backup integrity"
            ],
            validation_checks=[
                "Confirm all original files are backed up",
                "Verify backup file integrity"
            ],
            estimated_effort=2
        ))
        
        # Step 2: Create unified specification
        migration_steps.append(MigrationStep(
            step_id="CREATE_001",
            description="Create unified specification structure",
            prerequisites=["BACKUP_001"],
            actions=[
                "Create new unified spec directory",
                "Generate consolidated requirements document",
                "Generate consolidated design document",
                "Generate consolidated tasks document"
            ],
            validation_checks=[
                "Verify all requirements are included",
                "Confirm design consistency",
                "Validate task completeness"
            ],
            estimated_effort=opportunity.effort_estimate // 2
        ))
        
        # Step 3: Update implementations
        migration_steps.append(MigrationStep(
            step_id="MIGRATE_001",
            description="Update existing implementations",
            prerequisites=["CREATE_001"],
            actions=[
                "Update source code references",
                "Modify test cases",
                "Update documentation",
                "Update configuration files"
            ],
            validation_checks=[
                "All tests pass",
                "No broken references",
                "Documentation is consistent"
            ],
            estimated_effort=opportunity.effort_estimate // 2
        ))
        
        return migration_steps
    
    def _define_validation_criteria(self, target_specs: List[str], overlap_analysis: OverlapAnalysis) -> List[ValidationCriterion]:
        """Define validation criteria for successful consolidation"""
        validation_criteria = []
        
        # Functional completeness
        validation_criteria.append(ValidationCriterion(
            criterion_id="FUNC_001",
            description="All original functionality is preserved",
            validation_method="functional_coverage_analysis",
            success_threshold=1.0,  # 100% coverage
            measurement_approach="Compare functionality keywords before and after consolidation"
        ))
        
        # Quality improvement
        validation_criteria.append(ValidationCriterion(
            criterion_id="QUAL_001",
            description="Overall specification quality is maintained or improved",
            validation_method="quality_score_comparison",
            success_threshold=0.9,  # At least 90% of original quality
            measurement_approach="Calculate weighted average quality scores"
        ))
        
        # Traceability completeness
        validation_criteria.append(ValidationCriterion(
            criterion_id="TRACE_001",
            description="Complete traceability is maintained",
            validation_method="traceability_completeness_check",
            success_threshold=1.0,  # 100% traceability
            measurement_approach="Verify all original requirements have traceability links"
        ))
        
        return validation_criteria
    
    def _create_risk_mitigation_plan(self, opportunity: ConsolidationOpportunity) -> List[str]:
        """Create risk mitigation plan for consolidation"""
        risk_mitigation = []
        
        if opportunity.risk_level == "high":
            risk_mitigation.extend([
                "Conduct thorough architectural review before proceeding",
                "Create detailed rollback plan",
                "Implement phased consolidation approach",
                "Increase testing coverage during migration"
            ])
        elif opportunity.risk_level == "medium":
            risk_mitigation.extend([
                "Create rollback plan",
                "Conduct peer review of consolidation plan",
                "Test migration in isolated environment first"
            ])
        else:
            risk_mitigation.extend([
                "Monitor consolidation progress closely",
                "Validate each step before proceeding"
            ])
        
        # Add challenge-specific mitigations
        for challenge in opportunity.challenges:
            if "complexity" in challenge.lower():
                risk_mitigation.append("Break down complex consolidation into smaller steps")
            elif "dependencies" in challenge.lower():
                risk_mitigation.append("Coordinate with dependent system owners")
            elif "interface" in challenge.lower():
                risk_mitigation.append("Implement backward compatibility layers")
        
        return risk_mitigation
    
    def _define_success_metrics(self, target_specs: List[str], overlap_analysis: OverlapAnalysis) -> Dict[str, Any]:
        """Define success metrics for consolidation"""
        return {
            'spec_count_reduction': {
                'target': len(target_specs) - 1,  # Reduce by consolidating into 1
                'measurement': 'Count of active specifications'
            },
            'overlap_elimination': {
                'target': 0.95,  # 95% overlap elimination
                'measurement': 'Percentage of functional overlaps resolved'
            },
            'traceability_completeness': {
                'target': 1.0,  # 100% traceability
                'measurement': 'Percentage of original requirements with traceability links'
            },
            'implementation_compatibility': {
                'target': 1.0,  # 100% compatibility
                'measurement': 'Percentage of existing implementations that continue working'
            },
            'quality_preservation': {
                'target': 0.9,  # At least 90% quality preservation
                'measurement': 'Ratio of consolidated quality score to original average'
            }
        }