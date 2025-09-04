"""
Requirement traceability validation for RDI compliance.

This module implements the RequirementTracer class that analyzes requirement-to-implementation
links to ensure all implementations trace back to valid requirements.
"""

import re
import os
from pathlib import Path
from typing import List, Dict, Set, Optional, Tuple
from dataclasses import dataclass

from ..interfaces import ComplianceValidator
from ..models import ComplianceIssue, ComplianceIssueType, IssueSeverity


@dataclass
class RequirementReference:
    """Represents a reference to a requirement in code or documentation."""
    requirement_id: str
    file_path: str
    line_number: int
    context: str
    reference_type: str  # 'implementation', 'test', 'comment', 'docstring'


@dataclass
class RequirementDefinition:
    """Represents a requirement definition from requirements documents."""
    requirement_id: str
    title: str
    description: str
    acceptance_criteria: List[str]
    file_path: str
    line_number: int


@dataclass
class TraceabilityResult:
    """Results of requirement traceability analysis."""
    total_requirements: int
    traced_requirements: int
    untraced_requirements: List[str]
    orphaned_implementations: List[RequirementReference]
    traceability_score: float
    issues: List[ComplianceIssue]


class RequirementTracer(ComplianceValidator):
    """
    Analyzes requirement-to-implementation traceability for RDI compliance.
    
    This class validates that:
    1. All requirements have corresponding implementations
    2. All implementations trace back to valid requirements
    3. Traceability links are properly maintained
    """
    
    def __init__(self, repository_path: str):
        """
        Initialize the RequirementTracer.
        
        Args:
            repository_path: Path to the repository root
        """
        self.repository_path = Path(repository_path)
        self.requirement_patterns = [
            r'_Requirements?:\s*([0-9]+(?:\.[0-9]+)*(?:,\s*[0-9]+(?:\.[0-9]+)*)*)',
            r'Requirements?:\s*([0-9]+(?:\.[0-9]+)*(?:,\s*[0-9]+(?:\.[0-9]+)*)*)',
            r'Requirement\s+([0-9]+(?:\.[0-9]+)*)',
            r'REQ-([0-9]+(?:\.[0-9]+)*)',
            r'#\s*([0-9]+(?:\.[0-9]+)*)',  # Simple numbered requirements
        ]
        self.requirements_cache: Optional[Dict[str, RequirementDefinition]] = None
    
    def validate(self, target: str) -> List[ComplianceIssue]:
        """
        Validate requirement traceability for the given target.
        
        Args:
            target: Path to analyze (file or directory)
            
        Returns:
            List of compliance issues found
        """
        target_path = Path(target) if isinstance(target, str) else target
        
        # Load requirements if not cached
        if self.requirements_cache is None:
            self.requirements_cache = self._load_requirements()
        
        # Analyze traceability
        traceability_result = self._analyze_traceability(target_path)
        
        return traceability_result.issues
    
    def get_validator_name(self) -> str:
        """Get the name of this validator."""
        return "RequirementTracer"
    
    def analyze_traceability(self, target_path: Optional[str] = None) -> TraceabilityResult:
        """
        Perform comprehensive traceability analysis.
        
        Args:
            target_path: Specific path to analyze, or None for full repository
            
        Returns:
            Detailed traceability analysis results
        """
        if self.requirements_cache is None:
            self.requirements_cache = self._load_requirements()
        
        analysis_path = Path(target_path) if target_path else self.repository_path
        return self._analyze_traceability(analysis_path)
    
    def _load_requirements(self) -> Dict[str, RequirementDefinition]:
        """
        Load all requirements from requirements documents.
        
        Returns:
            Dictionary mapping requirement IDs to definitions
        """
        requirements = {}
        
        # Look for requirements documents
        requirements_files = []
        for pattern in ['**/requirements.md', '**/requirements/*.md', '**/*requirements*.md']:
            requirements_files.extend(self.repository_path.glob(pattern))
        
        for req_file in requirements_files:
            try:
                file_requirements = self._parse_requirements_file(req_file)
                requirements.update(file_requirements)
            except Exception as e:
                # Log error but continue processing other files
                print(f"Warning: Failed to parse requirements file {req_file}: {e}")
        
        return requirements
    
    def _parse_requirements_file(self, file_path: Path) -> Dict[str, RequirementDefinition]:
        """
        Parse a requirements document to extract requirement definitions.
        
        Args:
            file_path: Path to the requirements file
            
        Returns:
            Dictionary of requirement definitions
        """
        requirements = {}
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                lines = content.split('\n')
        except Exception:
            return requirements
        
        current_requirement = None
        current_acceptance_criteria = []
        
        for line_num, line in enumerate(lines, 1):
            line = line.strip()
            
            # Look for requirement headers
            req_match = re.search(r'###\s+Requirement\s+([0-9]+(?:\.[0-9]+)*)', line)
            if req_match:
                # Save previous requirement if exists
                if current_requirement:
                    current_requirement.acceptance_criteria = current_acceptance_criteria.copy()
                    requirements[current_requirement.requirement_id] = current_requirement
                
                # Start new requirement
                req_id = req_match.group(1)
                current_requirement = RequirementDefinition(
                    requirement_id=req_id,
                    title=line,
                    description="",
                    acceptance_criteria=[],
                    file_path=str(file_path),
                    line_number=line_num
                )
                current_acceptance_criteria = []
            
            # Look for user stories (requirement descriptions)
            elif line.startswith('**User Story:**') and current_requirement:
                current_requirement.description = line
            
            # Look for acceptance criteria
            elif re.match(r'^\d+\.\s+WHEN.*THEN.*SHALL', line) and current_requirement:
                current_acceptance_criteria.append(line)
        
        # Save last requirement
        if current_requirement:
            current_requirement.acceptance_criteria = current_acceptance_criteria.copy()
            requirements[current_requirement.requirement_id] = current_requirement
        
        return requirements
    
    def _analyze_traceability(self, target_path: Path) -> TraceabilityResult:
        """
        Analyze requirement traceability for the given path.
        
        Args:
            target_path: Path to analyze
            
        Returns:
            Traceability analysis results
        """
        # Find all requirement references in code
        requirement_references = self._find_requirement_references(target_path)
        
        # Group references by requirement ID
        referenced_requirements = set()
        for ref in requirement_references:
            referenced_requirements.add(ref.requirement_id)
        
        # Identify untraced requirements
        all_requirements = set(self.requirements_cache.keys())
        untraced_requirements = all_requirements - referenced_requirements
        
        # Identify orphaned implementations (references to non-existent requirements)
        orphaned_implementations = [
            ref for ref in requirement_references
            if ref.requirement_id not in all_requirements
        ]
        
        # Calculate traceability score
        total_requirements = len(all_requirements)
        traced_requirements = len(referenced_requirements & all_requirements)
        traceability_score = (traced_requirements / total_requirements * 100) if total_requirements > 0 else 0
        
        # Generate compliance issues
        issues = self._generate_traceability_issues(
            untraced_requirements, orphaned_implementations, traceability_score
        )
        
        return TraceabilityResult(
            total_requirements=total_requirements,
            traced_requirements=traced_requirements,
            untraced_requirements=list(untraced_requirements),
            orphaned_implementations=orphaned_implementations,
            traceability_score=traceability_score,
            issues=issues
        )
    
    def _find_requirement_references(self, target_path: Path) -> List[RequirementReference]:
        """
        Find all requirement references in the target path.
        
        Args:
            target_path: Path to search for references
            
        Returns:
            List of requirement references found
        """
        references = []
        
        # Define file patterns to search
        search_patterns = ['**/*.py', '**/*.md', '**/*.rst', '**/*.txt']
        
        for pattern in search_patterns:
            if target_path.is_file():
                files_to_search = [target_path] if target_path.match(pattern.replace('**/', '')) else []
            else:
                files_to_search = list(target_path.glob(pattern))
            
            for file_path in files_to_search:
                try:
                    file_references = self._find_references_in_file(file_path)
                    references.extend(file_references)
                except Exception as e:
                    # Log error but continue processing
                    print(f"Warning: Failed to process file {file_path}: {e}")
        
        return references
    
    def _find_references_in_file(self, file_path: Path) -> List[RequirementReference]:
        """
        Find requirement references in a single file.
        
        Args:
            file_path: Path to the file to search
            
        Returns:
            List of requirement references found in the file
        """
        references = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
        except Exception:
            return references
        
        for line_num, line in enumerate(lines, 1):
            # Track requirement IDs found on this line to avoid duplicates
            found_on_line = set()
            
            for pattern in self.requirement_patterns:
                matches = re.finditer(pattern, line, re.IGNORECASE)
                for match in matches:
                    # Extract requirement IDs (handle comma-separated lists)
                    req_ids_str = match.group(1)
                    req_ids = [req_id.strip() for req_id in req_ids_str.split(',')]
                    
                    for req_id in req_ids:
                        if req_id and req_id not in found_on_line:  # Skip empty strings and duplicates
                            found_on_line.add(req_id)
                            
                            # Determine reference type
                            ref_type = self._determine_reference_type(line, file_path)
                            
                            references.append(RequirementReference(
                                requirement_id=req_id,
                                file_path=str(file_path),
                                line_number=line_num,
                                context=line.strip(),
                                reference_type=ref_type
                            ))
        
        return references
    
    def _determine_reference_type(self, line: str, file_path: Path) -> str:
        """
        Determine the type of requirement reference based on context.
        
        Args:
            line: The line containing the reference
            file_path: Path to the file containing the reference
            
        Returns:
            Reference type string
        """
        line_lower = line.lower().strip()
        
        # Check if it's in a test file
        if 'test' in file_path.name.lower():
            return 'test'
        
        # Check if it's in a comment
        if line_lower.startswith('#') or line_lower.startswith('//'):
            return 'comment'
        
        # Check if it's in a docstring
        if '"""' in line or "'''" in line:
            return 'docstring'
        
        # Default to implementation
        return 'implementation'
    
    def _generate_traceability_issues(
        self, 
        untraced_requirements: List[str], 
        orphaned_implementations: List[RequirementReference],
        traceability_score: float
    ) -> List[ComplianceIssue]:
        """
        Generate compliance issues based on traceability analysis.
        
        Args:
            untraced_requirements: Requirements without implementations
            orphaned_implementations: Implementations without valid requirements
            traceability_score: Overall traceability score
            
        Returns:
            List of compliance issues
        """
        issues = []
        
        # Issue for untraced requirements
        if untraced_requirements:
            issues.append(ComplianceIssue(
                issue_type=ComplianceIssueType.REQUIREMENT_TRACEABILITY,
                severity=IssueSeverity.HIGH,
                description=f"Found {len(untraced_requirements)} requirements without implementations",
                affected_files=[],
                remediation_steps=[
                    f"Implement missing requirements: {', '.join(untraced_requirements)}",
                    "Add requirement references to implementation files",
                    "Ensure all requirements have corresponding code implementations"
                ],
                estimated_effort="Medium",
                blocking_merge=len(untraced_requirements) > 5,
                metadata={
                    "untraced_requirements": untraced_requirements,
                    "count": len(untraced_requirements)
                }
            ))
        
        # Issue for orphaned implementations
        if orphaned_implementations:
            affected_files = list(set(ref.file_path for ref in orphaned_implementations))
            orphaned_req_ids = list(set(ref.requirement_id for ref in orphaned_implementations))
            
            issues.append(ComplianceIssue(
                issue_type=ComplianceIssueType.REQUIREMENT_TRACEABILITY,
                severity=IssueSeverity.MEDIUM,
                description=f"Found {len(orphaned_implementations)} references to non-existent requirements",
                affected_files=affected_files,
                remediation_steps=[
                    f"Remove or update invalid requirement references: {', '.join(orphaned_req_ids)}",
                    "Verify requirement IDs match those in requirements documents",
                    "Update requirement references to use correct IDs"
                ],
                estimated_effort="Low",
                blocking_merge=False,
                metadata={
                    "orphaned_requirements": orphaned_req_ids,
                    "count": len(orphaned_implementations)
                }
            ))
        
        # Issue for low traceability score
        if traceability_score < 80.0:
            issues.append(ComplianceIssue(
                issue_type=ComplianceIssueType.REQUIREMENT_TRACEABILITY,
                severity=IssueSeverity.HIGH if traceability_score < 60.0 else IssueSeverity.MEDIUM,
                description=f"Low requirement traceability score: {traceability_score:.1f}%",
                affected_files=[],
                remediation_steps=[
                    "Improve requirement traceability by adding requirement references to implementations",
                    "Ensure all requirements have corresponding implementations",
                    "Review and update requirement documentation",
                    f"Target: Achieve >80% traceability (currently {traceability_score:.1f}%)"
                ],
                estimated_effort="High",
                blocking_merge=traceability_score < 60.0,
                metadata={
                    "traceability_score": traceability_score,
                    "target_score": 80.0
                }
            ))
        
        return issues