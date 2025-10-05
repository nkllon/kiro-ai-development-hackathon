#!/usr/bin/env python3
"""
Specification Bloat Detector
===========================

Detects when specifications have become theater instead of guidance.
Mathematically validates requirements-to-implementation ratios and identifies
the classic "we have met the enemy and he are us" syndrome.

Author: Spec Scrub Framework
Date: 2025-09-18
Purpose: Prevent specification theater through mathematical validation
"""

import re
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

try:
    from beast_mode.core import ReflectiveModule
except ImportError:
    # Fallback for when Beast Mode isn't available
    class ReflectiveModule:
        def get_module_status(self): return {}
        def is_healthy(self): return True
        def get_health_indicators(self): return {}
        def _get_primary_responsibility(self): return ""


class TheaterPatternType(Enum):
    """Types of specification theater patterns."""
    
    BLOATED_REQUIREMENTS = "bloated_requirements"
    OVER_ENGINEERING = "over_engineering" 
    IMPLEMENTATION_GAP = "implementation_gap"
    FORMAT_IMPEDANCE = "format_impedance"
    ACCEPTANCE_CRITERIA_EXPLOSION = "acceptance_criteria_explosion"


@dataclass
class TheaterPattern:
    """Detected theater pattern in specifications."""
    
    pattern_type: TheaterPatternType
    severity: str
    description: str
    suggested_remediation: str
    mathematical_evidence: Dict[str, float]


@dataclass
class SpecMetrics:
    """Mathematical metrics for specification analysis."""
    
    requirements_count: int
    acceptance_criteria_count: int
    design_elements_count: int
    implementation_tasks_count: int
    bloat_score: float
    coverage_ratio: float
    format_compatibility_score: float


class SpecBloatDetector(ReflectiveModule):
    """
    Detects specification bloat and theater patterns through mathematical analysis.
    
    The core insight: When bloat_score > 2.0, we've entered theater territory.
    When we can't parse our own formats, we've achieved peak self-sabotage.
    """
    
    def __init__(self):
        super().__init__()
        self._logger = logging.getLogger(__name__)
        
        # Empirically derived thresholds from perverse case analysis
        self.THEATER_THRESHOLD = 2.0
        self.OVER_ENGINEERING_THRESHOLD = 3.0
        self.MAX_ACCEPTANCE_CRITERIA = 3
        self.HEALTHY_COVERAGE_RATIO = 0.8
    
    def calculate_bloat_score(self, spec_path: str) -> float:
        """
        Calculate mathematical bloat score for a specification.
        
        Formula: (design_elements + acceptance_criteria) / implementation_tasks
        
        Args:
            spec_path: Path to specification directory
            
        Returns:
            Bloat score (>2.0 indicates theater territory)
        """
        metrics = self._extract_spec_metrics(spec_path)
        
        if metrics.implementation_tasks_count == 0:
            # No tasks = infinite bloat (mathematical proof of theater)
            return float('inf')
        
        bloat_score = (
            metrics.design_elements_count + metrics.acceptance_criteria_count
        ) / metrics.implementation_tasks_count
        
        self._logger.info(f"Bloat score for {spec_path}: {bloat_score:.2f}")
        return bloat_score
    
    def detect_theater_patterns(self, spec_path: str) -> List[TheaterPattern]:
        """
        Detect theater patterns in specification through systematic analysis.
        
        Args:
            spec_path: Path to specification directory
            
        Returns:
            List of detected theater patterns with mathematical evidence
        """
        patterns = []
        metrics = self._extract_spec_metrics(spec_path)
        
        # Pattern 1: Bloated Requirements (too many acceptance criteria)
        if metrics.acceptance_criteria_count > metrics.requirements_count * self.MAX_ACCEPTANCE_CRITERIA:
            patterns.append(TheaterPattern(
                pattern_type=TheaterPatternType.ACCEPTANCE_CRITERIA_EXPLOSION,
                severity="high",
                description=f"Requirements have {metrics.acceptance_criteria_count} acceptance criteria for {metrics.requirements_count} requirements",
                suggested_remediation="Decompose requirements to max 3 acceptance criteria each",
                mathematical_evidence={
                    "criteria_per_requirement": metrics.acceptance_criteria_count / max(metrics.requirements_count, 1),
                    "recommended_max": self.MAX_ACCEPTANCE_CRITERIA
                }
            ))
        
        # Pattern 2: Over-Engineering (design elements >> tasks)
        if metrics.design_elements_count > metrics.implementation_tasks_count * self.OVER_ENGINEERING_THRESHOLD:
            patterns.append(TheaterPattern(
                pattern_type=TheaterPatternType.OVER_ENGINEERING,
                severity="high", 
                description=f"Design has {metrics.design_elements_count} elements but only {metrics.implementation_tasks_count} tasks",
                suggested_remediation="Either add implementation tasks or simplify design",
                mathematical_evidence={
                    "design_to_task_ratio": metrics.design_elements_count / max(metrics.implementation_tasks_count, 1),
                    "threshold": self.OVER_ENGINEERING_THRESHOLD
                }
            ))
        
        # Pattern 3: Implementation Gap (requirements without tasks)
        if metrics.coverage_ratio < self.HEALTHY_COVERAGE_RATIO:
            patterns.append(TheaterPattern(
                pattern_type=TheaterPatternType.IMPLEMENTATION_GAP,
                severity="critical",
                description=f"Coverage ratio {metrics.coverage_ratio:.2f} indicates missing implementation",
                suggested_remediation="Add implementation tasks for all requirements",
                mathematical_evidence={
                    "coverage_ratio": metrics.coverage_ratio,
                    "healthy_threshold": self.HEALTHY_COVERAGE_RATIO
                }
            ))
        
        # Pattern 4: Format Impedance (parser can't handle format)
        if metrics.format_compatibility_score < 0.5:
            patterns.append(TheaterPattern(
                pattern_type=TheaterPatternType.FORMAT_IMPEDANCE,
                severity="critical",
                description="Specification format not compatible with existing parsers",
                suggested_remediation="Use format adapter or update parser to handle EARS format",
                mathematical_evidence={
                    "compatibility_score": metrics.format_compatibility_score,
                    "minimum_threshold": 0.5
                }
            ))
        
        # Pattern 5: Overall Bloat Score
        bloat_score = self.calculate_bloat_score(spec_path)
        if bloat_score > self.THEATER_THRESHOLD:
            patterns.append(TheaterPattern(
                pattern_type=TheaterPatternType.BLOATED_REQUIREMENTS,
                severity="high" if bloat_score < 5.0 else "critical",
                description=f"Bloat score {bloat_score:.2f} indicates specification theater",
                suggested_remediation="Focus on implementable requirements, eliminate planning theater",
                mathematical_evidence={
                    "bloat_score": bloat_score,
                    "theater_threshold": self.THEATER_THRESHOLD
                }
            ))
        
        return patterns
    
    def suggest_decomposition(self, spec_path: str) -> Dict[str, Any]:
        """
        Suggest decomposition strategy for bloated specifications.
        
        Args:
            spec_path: Path to specification directory
            
        Returns:
            Decomposition plan with specific recommendations
        """
        metrics = self._extract_spec_metrics(spec_path)
        patterns = self.detect_theater_patterns(spec_path)
        
        decomposition_plan = {
            "current_metrics": metrics,
            "detected_patterns": patterns,
            "recommendations": []
        }
        
        # Specific recommendations based on patterns
        for pattern in patterns:
            if pattern.pattern_type == TheaterPatternType.ACCEPTANCE_CRITERIA_EXPLOSION:
                decomposition_plan["recommendations"].append({
                    "action": "decompose_requirements",
                    "target": "Split requirements with >3 acceptance criteria",
                    "expected_improvement": "Reduce bloat score by 30-50%"
                })
            
            elif pattern.pattern_type == TheaterPatternType.OVER_ENGINEERING:
                decomposition_plan["recommendations"].append({
                    "action": "simplify_design",
                    "target": "Remove design elements without corresponding tasks",
                    "expected_improvement": "Improve design-to-task ratio to <2.0"
                })
            
            elif pattern.pattern_type == TheaterPatternType.IMPLEMENTATION_GAP:
                decomposition_plan["recommendations"].append({
                    "action": "add_implementation_tasks",
                    "target": "Create tasks for all requirements",
                    "expected_improvement": "Achieve >80% coverage ratio"
                })
        
        return decomposition_plan
    
    def _extract_spec_metrics(self, spec_path: str) -> SpecMetrics:
        """Extract mathematical metrics from specification files."""
        spec_dir = Path(spec_path)
        
        # Count requirements and acceptance criteria
        requirements_count = 0
        acceptance_criteria_count = 0
        format_compatibility_score = 0.0
        
        requirements_file = spec_dir / "requirements.md"
        if requirements_file.exists():
            req_content = requirements_file.read_text()
            
            # Count EARS format requirements
            ears_requirements = re.findall(r'### Requirement \d+:', req_content)
            requirements_count = len(ears_requirements)
            
            # Count acceptance criteria
            acceptance_criteria = re.findall(r'^\d+\.\s+WHEN.*THEN.*SHALL', req_content, re.MULTILINE)
            acceptance_criteria_count = len(acceptance_criteria)
            
            # Check format compatibility (can Beast Mode parser handle this?)
            beast_mode_format = re.findall(r'REQ-\d+:', req_content)
            if beast_mode_format:
                format_compatibility_score = 1.0
            elif ears_requirements:
                format_compatibility_score = 0.3  # EARS format needs adapter
            else:
                format_compatibility_score = 0.0  # Unknown format
        
        # Count design elements
        design_elements_count = 0
        design_file = spec_dir / "design.md"
        if design_file.exists():
            design_content = design_file.read_text()
            
            # Count headers as design elements
            design_headers = re.findall(r'^#+\s+', design_content, re.MULTILINE)
            design_elements_count = len(design_headers)
        
        # Count implementation tasks
        implementation_tasks_count = 0
        tasks_file = spec_dir / "tasks.md"
        if tasks_file.exists():
            tasks_content = tasks_file.read_text()
            
            # Count checkbox tasks
            task_items = re.findall(r'- \[ \]', tasks_content)
            implementation_tasks_count = len(task_items)
        
        # Calculate derived metrics
        bloat_score = (
            (design_elements_count + acceptance_criteria_count) / max(implementation_tasks_count, 1)
        )
        
        coverage_ratio = (
            implementation_tasks_count / max(requirements_count + design_elements_count, 1)
        )
        
        return SpecMetrics(
            requirements_count=requirements_count,
            acceptance_criteria_count=acceptance_criteria_count,
            design_elements_count=design_elements_count,
            implementation_tasks_count=implementation_tasks_count,
            bloat_score=bloat_score,
            coverage_ratio=coverage_ratio,
            format_compatibility_score=format_compatibility_score
        )
    
    # ReflectiveModule interface implementation
    def get_module_status(self) -> Dict[str, Any]:
        """Return current module status."""
        return {
            "module_name": "SpecBloatDetector",
            "status": "operational",
            "theater_threshold": self.THEATER_THRESHOLD,
            "patterns_detected": ["bloated_requirements", "over_engineering", "implementation_gap", "format_impedance"]
        }
    
    def is_healthy(self) -> bool:
        """Check if module is healthy."""
        return True
    
    def get_health_indicators(self) -> Dict[str, Any]:
        """Return health indicators."""
        return {
            "detector_operational": True,
            "thresholds_configured": True,
            "pattern_recognition_active": True,
            "mathematical_validation_enabled": True
        }
    
    def _get_primary_responsibility(self) -> str:
        """Return primary responsibility."""
        return "Detect specification theater through mathematical bloat analysis"