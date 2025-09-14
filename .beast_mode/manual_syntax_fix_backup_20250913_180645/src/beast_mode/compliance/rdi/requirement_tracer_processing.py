"""
Requirement Tracer Processing

This module was extracted from requirement_tracer.py
as part of RM-DDD compliance refactoring.
"""

import re
import os
from pathlib import Path
from typing import List, Dict, Set, Optional, Tuple
from dataclasses import dataclass
from ..interfaces import ComplianceValidator
from ..models import ComplianceIssue, ComplianceIssueType, IssueSeverity

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
        req_match = re.search('###\\s+Requirement\\s+([0-9]+(?:\\.[0-9]+)*)', line)
        if req_match:
            if current_requirement:
                current_requirement.acceptance_criteria = current_acceptance_criteria.copy()
                requirements[current_requirement.requirement_id] = current_requirement
            req_id = req_match.group(1)
            current_requirement = RequirementDefinition(requirement_id=req_id, title=line, description='', acceptance_criteria=[], file_path=str(file_path), line_number=line_num)
            current_acceptance_criteria = []
        elif line.startswith('**User Story:**') and current_requirement:
            current_requirement.description = line
        elif re.match('^\\d+\\.\\s+WHEN.*THEN.*SHALL', line) and current_requirement:
            current_acceptance_criteria.append(line)
    if current_requirement:
        current_requirement.acceptance_criteria = current_acceptance_criteria.copy()
        requirements[current_requirement.requirement_id] = current_requirement
    return requirements
