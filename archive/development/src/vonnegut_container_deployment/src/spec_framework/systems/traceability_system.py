"""
Traceability System - Maintain complete traceability from business needs to implementation.

Provides bidirectional traceability, impact analysis, and coverage reporting.
"""

from typing import Dict, List, Optional, Any, Set
from datetime import datetime
import logging

from ..core.base import ReflectiveModule
from ..core.models import (
    Specification,
    TraceabilityMatrix,
    RequirementId,
    DesignComponentId,
    TaskId
)


logger = logging.getLogger(__name__)


class TraceabilitySystem(ReflectiveModule):
    """
    Maintain complete traceability from business needs to implementation.
    
    Provides systematic traceability management with bidirectional tracking,
    impact analysis, and comprehensive coverage reporting.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize the traceability system."""
        super().__init__()
        self._config = config or {}
        self._traceability_cache: Dict[str, TraceabilityMatrix] = {}
        
        logger.info("TraceabilitySystem initialized with systematic tracking")
    
    def build_traceability_matrix(self, specification: Specification) -> TraceabilityMatrix:
        """
        Build complete traceability matrix for specification.
        
        Args:
            specification: Specification to build traceability for
            
        Returns:
            Complete traceability matrix
        """
        matrix = TraceabilityMatrix()
        
        # Build requirement to design traceability
        if specification.design and specification.design.components:
            for req in specification.requirements:
                # Find design components that reference this requirement
                for component_id, component_info in specification.design.components.items():
                    if isinstance(component_info, dict) and 'requirements' in component_info:
                        if req.id in component_info['requirements']:
                            matrix.add_requirement_design_link(req.id, component_id)
        
        # Build design to task traceability
        for task in specification.tasks:
            for req_id in task.requirements_references:
                # Find design components linked to this requirement
                if req_id in matrix.requirement_to_design:
                    for design_id in matrix.requirement_to_design[req_id]:
                        if design_id not in matrix.design_to_tasks:
                            matrix.design_to_tasks[design_id] = []
                        if task.id not in matrix.design_to_tasks[design_id]:
                            matrix.design_to_tasks[design_id].append(task.id)
        
        # Build compliance traceability
        for req in specification.requirements:
            for compliance_tag in req.compliance_tags:
                compliance_req = f"{compliance_tag.framework}:{compliance_tag.requirement_id}"
                if compliance_req not in matrix.compliance_traceability:
                    matrix.compliance_traceability[compliance_req] = []
                if req.id not in matrix.compliance_traceability[compliance_req]:
                    matrix.compliance_traceability[compliance_req].append(req.id)
        
        # Cache the matrix
        self._traceability_cache[specification.id] = matrix
        
        logger.info(f"Built traceability matrix for specification {specification.name}")
        return matrix
    
    def validate_traceability_completeness(
        self,
        specification: Specification
    ) -> Dict[str, Any]:
        """
        Validate completeness of traceability links.
        
        Args:
            specification: Specification to validate
            
        Returns:
            Validation results with coverage metrics
        """
        matrix = self.build_traceability_matrix(specification)
        
        validation_results = {
            'requirement_coverage': 0.0,
            'design_coverage': 0.0,
            'task_coverage': 0.0,
            'compliance_coverage': 0.0,
            'orphaned_requirements': [],
            'orphaned_tasks': [],
            'missing_compliance_links': []
        }
        
        # Calculate requirement coverage
        total_requirements = len(specification.requirements)
        covered_requirements = len([
            req_id for req_id in matrix.requirement_to_design.keys()
            if matrix.requirement_to_design[req_id]
        ])
        validation_results['requirement_coverage'] = (
            (covered_requirements / total_requirements) * 100.0 if total_requirements > 0 else 0.0
        )
        
        # Find orphaned requirements (no design links)
        for req in specification.requirements:
            if req.id not in matrix.requirement_to_design or not matrix.requirement_to_design[req.id]:
                validation_results['orphaned_requirements'].append(req.id)
        
        # Find orphaned tasks (no requirement links)
        for task in specification.tasks:
            if not task.requirements_references:
                validation_results['orphaned_tasks'].append(task.id)
        
        # Calculate task coverage
        total_tasks = len(specification.tasks)
        covered_tasks = len([
            task for task in specification.tasks
            if task.requirements_references
        ])
        validation_results['task_coverage'] = (
            (covered_tasks / total_tasks) * 100.0 if total_tasks > 0 else 0.0
        )
        
        # Calculate compliance coverage
        total_compliance_requirements = sum(
            len(req.compliance_tags) for req in specification.requirements
        )
        covered_compliance = len(matrix.compliance_traceability)
        validation_results['compliance_coverage'] = (
            (covered_compliance / total_compliance_requirements) * 100.0 
            if total_compliance_requirements > 0 else 100.0
        )
        
        return validation_results
    
    def analyze_change_impact(
        self,
        specification: Specification,
        changed_requirement_id: RequirementId
    ) -> Dict[str, List[str]]:
        """
        Analyze impact of requirement change across specification.
        
        Args:
            specification: Specification containing the changed requirement
            changed_requirement_id: ID of the changed requirement
            
        Returns:
            Impact analysis results
        """
        matrix = self.build_traceability_matrix(specification)
        
        impact_analysis = {
            'affected_design_components': [],
            'affected_tasks': [],
            'affected_compliance_requirements': [],
            'downstream_requirements': []
        }
        
        # Find directly affected design components
        if changed_requirement_id in matrix.requirement_to_design:
            impact_analysis['affected_design_components'] = matrix.requirement_to_design[changed_requirement_id]
        
        # Find affected tasks through design components
        for design_id in impact_analysis['affected_design_components']:
            if design_id in matrix.design_to_tasks:
                impact_analysis['affected_tasks'].extend(matrix.design_to_tasks[design_id])
        
        # Find affected compliance requirements
        for compliance_req, req_ids in matrix.compliance_traceability.items():
            if changed_requirement_id in req_ids:
                impact_analysis['affected_compliance_requirements'].append(compliance_req)
        
        # Remove duplicates
        impact_analysis['affected_tasks'] = list(set(impact_analysis['affected_tasks']))
        
        logger.info(f"Analyzed change impact for requirement {changed_requirement_id}")
        return impact_analysis
    
    def generate_traceability_report(
        self,
        specification: Specification
    ) -> Dict[str, Any]:
        """
        Generate comprehensive traceability report.
        
        Args:
            specification: Specification to generate report for
            
        Returns:
            Comprehensive traceability report
        """
        matrix = self.build_traceability_matrix(specification)
        validation = self.validate_traceability_completeness(specification)
        
        report = {
            'specification_id': specification.id,
            'specification_name': specification.name,
            'generated_at': datetime.now().isoformat(),
            'summary': {
                'total_requirements': len(specification.requirements),
                'total_design_components': len(specification.design.components) if specification.design else 0,
                'total_tasks': len(specification.tasks),
                'total_compliance_requirements': len(matrix.compliance_traceability)
            },
            'coverage_metrics': {
                'requirement_coverage': validation['requirement_coverage'],
                'task_coverage': validation['task_coverage'],
                'compliance_coverage': validation['compliance_coverage']
            },
            'traceability_matrix': {
                'requirement_to_design_links': len(matrix.requirement_to_design),
                'design_to_task_links': len(matrix.design_to_tasks),
                'compliance_links': len(matrix.compliance_traceability)
            },
            'quality_issues': {
                'orphaned_requirements': validation['orphaned_requirements'],
                'orphaned_tasks': validation['orphaned_tasks'],
                'missing_compliance_links': validation['missing_compliance_links']
            }
        }
        
        return report
    
    def find_requirements_without_implementation(
        self,
        specification: Specification
    ) -> List[RequirementId]:
        """
        Find requirements that have no implementation path.
        
        Args:
            specification: Specification to analyze
            
        Returns:
            List of requirement IDs without implementation
        """
        matrix = self.build_traceability_matrix(specification)
        unimplemented = []
        
        for req in specification.requirements:
            # Check if requirement has design links
            has_design = req.id in matrix.requirement_to_design and matrix.requirement_to_design[req.id]
            
            # Check if requirement has task links (through design)
            has_tasks = False
            if has_design:
                for design_id in matrix.requirement_to_design[req.id]:
                    if design_id in matrix.design_to_tasks and matrix.design_to_tasks[design_id]:
                        has_tasks = True
                        break
            
            if not has_design or not has_tasks:
                unimplemented.append(req.id)
        
        return unimplemented
    
    def get_requirement_implementation_path(
        self,
        specification: Specification,
        requirement_id: RequirementId
    ) -> Dict[str, List[str]]:
        """
        Get complete implementation path for a requirement.
        
        Args:
            specification: Specification containing the requirement
            requirement_id: ID of the requirement
            
        Returns:
            Complete implementation path
        """
        matrix = self.build_traceability_matrix(specification)
        
        path = {
            'requirement_id': requirement_id,
            'design_components': [],
            'tasks': [],
            'implementation_artifacts': [],
            'test_cases': []
        }
        
        # Get design components
        if requirement_id in matrix.requirement_to_design:
            path['design_components'] = matrix.requirement_to_design[requirement_id]
        
        # Get tasks through design components
        for design_id in path['design_components']:
            if design_id in matrix.design_to_tasks:
                path['tasks'].extend(matrix.design_to_tasks[design_id])
        
        # Get implementation artifacts through tasks
        for task_id in path['tasks']:
            if task_id in matrix.task_to_implementation:
                path['implementation_artifacts'].extend(matrix.task_to_implementation[task_id])
        
        # Get test cases through implementation artifacts
        for artifact in path['implementation_artifacts']:
            if artifact in matrix.implementation_to_tests:
                path['test_cases'].extend(matrix.implementation_to_tests[artifact])
        
        # Remove duplicates
        path['tasks'] = list(set(path['tasks']))
        path['implementation_artifacts'] = list(set(path['implementation_artifacts']))
        path['test_cases'] = list(set(path['test_cases']))
        
        return path
    
    # ReflectiveModule implementation
    def health(self) -> Dict[str, Any]:
        """Return health status of the traceability system."""
        return {
            "status": "healthy",
            "cached_matrices": len(self._traceability_cache),
            "last_check": datetime.now().isoformat()
        }
    
    def ready(self) -> bool:
        """Check if traceability system is ready for operation."""
        return True  # Always ready
    
    def metrics(self) -> Dict[str, float]:
        """Return operational metrics."""
        return {
            "cached_matrices_count": float(len(self._traceability_cache))
        }
    
    def status(self) -> str:
        """Return current operational status."""
        return "ready"