"""
Requirement Traceability System - Systematic tracking of requirement relationships.

Implements bidirectional traceability between requirements and business needs,
requirement relationship management, impact analysis, and coverage reporting.
"""

from typing import Dict, List, Optional, Set, Tuple, Any
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
import logging
from collections import defaultdict, deque

from ..core.base import ReflectiveModule
from ..core.models import (
    Requirement, RequirementId, SpecificationId, TaskId, DesignComponentId,
    TraceabilityMatrix, DependencyRelationship, DependencyType
)


logger = logging.getLogger(__name__)


class TraceabilityLinkType(Enum):
    """Types of traceability links."""
    DERIVES_FROM = "derives_from"
    SATISFIES = "satisfies"
    DEPENDS_ON = "depends_on"
    CONFLICTS_WITH = "conflicts_with"
    REFINES = "refines"
    IMPLEMENTS = "implements"
    VALIDATES = "validates"


class ImpactSeverity(Enum):
    """Severity levels for impact analysis."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ChangeType(Enum):
    """Types of requirement changes."""
    ADDED = "added"
    MODIFIED = "modified"
    DELETED = "deleted"
    STATUS_CHANGED = "status_changed"


@dataclass
class TraceabilityLink:
    """Individual traceability link between requirements."""
    source_id: RequirementId
    target_id: RequirementId
    link_type: TraceabilityLinkType
    description: str = ""
    created_at: datetime = field(default_factory=datetime.now)
    created_by: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class BusinessNeed:
    """Business need that requirements trace to."""
    id: str
    title: str
    description: str
    business_value: str
    stakeholders: List[str] = field(default_factory=list)
    priority: str = "medium"
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class RequirementChange:
    """Record of requirement change for impact analysis."""
    requirement_id: RequirementId
    change_type: ChangeType
    old_value: Optional[str] = None
    new_value: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.now)
    changed_by: str = ""
    reason: str = ""


@dataclass
class ImpactAnalysisResult:
    """Result of impact analysis for requirement changes."""
    change: RequirementChange
    impacted_requirements: List[RequirementId] = field(default_factory=list)
    impacted_design_components: List[DesignComponentId] = field(default_factory=list)
    impacted_tasks: List[TaskId] = field(default_factory=list)
    severity: ImpactSeverity = ImpactSeverity.LOW
    recommendations: List[str] = field(default_factory=list)
    estimated_effort: Optional[int] = None  # hours


@dataclass
class CoverageReport:
    """Coverage report for requirements traceability."""
    total_requirements: int
    traced_requirements: int
    untraceable_requirements: List[RequirementId] = field(default_factory=list)
    orphaned_components: List[str] = field(default_factory=list)
    coverage_percentage: float = 0.0
    gaps: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)


class RequirementTraceabilitySystem(ReflectiveModule):
    """
    Requirement Traceability System.
    
    Provides systematic tracking of requirement relationships with bidirectional
    traceability, impact analysis, and comprehensive coverage reporting.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize the requirement traceability system."""
        super().__init__()
        self._config = config or {}
        self._traceability_links: Dict[RequirementId, List[TraceabilityLink]] = defaultdict(list)
        self._business_needs: Dict[str, BusinessNeed] = {}
        self._requirement_to_business: Dict[RequirementId, List[str]] = defaultdict(list)
        self._change_history: List[RequirementChange] = []
        self._traceability_matrix = TraceabilityMatrix()
        
        logger.info("RequirementTraceabilitySystem initialized")
    
    def add_business_need(
        self,
        need_id: str,
        title: str,
        description: str,
        business_value: str,
        stakeholders: Optional[List[str]] = None,
        priority: str = "medium"
    ) -> BusinessNeed:
        """
        Add a business need to the system.
        
        Args:
            need_id: Unique identifier for the business need
            title: Title of the business need
            description: Detailed description
            business_value: Business value statement
            stakeholders: List of stakeholders
            priority: Priority level
            
        Returns:
            Created business need
        """
        business_need = BusinessNeed(
            id=need_id,
            title=title,
            description=description,
            business_value=business_value,
            stakeholders=stakeholders or [],
            priority=priority
        )
        
        self._business_needs[need_id] = business_need
        logger.info(f"Added business need: {need_id}")
        
        return business_need
    
    def link_requirement_to_business_need(
        self,
        requirement_id: RequirementId,
        business_need_id: str,
        description: str = ""
    ) -> bool:
        """
        Link a requirement to a business need.
        
        Args:
            requirement_id: ID of the requirement
            business_need_id: ID of the business need
            description: Description of the link
            
        Returns:
            True if link was created successfully
        """
        if business_need_id not in self._business_needs:
            logger.error(f"Business need {business_need_id} not found")
            return False
        
        if business_need_id not in self._requirement_to_business[requirement_id]:
            self._requirement_to_business[requirement_id].append(business_need_id)
            logger.info(f"Linked requirement {requirement_id} to business need {business_need_id}")
            return True
        
        return False
    
    def add_traceability_link(
        self,
        source_id: RequirementId,
        target_id: RequirementId,
        link_type: TraceabilityLinkType,
        description: str = "",
        created_by: str = "",
        metadata: Optional[Dict[str, Any]] = None
    ) -> TraceabilityLink:
        """
        Add a unidirectional traceability link between requirements.
        
        Args:
            source_id: Source requirement ID
            target_id: Target requirement ID
            link_type: Type of traceability link
            description: Description of the relationship
            created_by: Who created the link
            metadata: Additional metadata
            
        Returns:
            Created traceability link
        """
        # Validate that this link won't create a cycle
        if self._would_create_cycle(source_id, target_id, link_type):
            suggestions = self.suggest_requirement_decomposition(source_id, target_id, link_type)
            error_msg = (
                f"Adding link from {source_id} to {target_id} would create a circular dependency. "
                f"This indicates the requirements need to be either merged or decomposed. "
                f"Suggestions: {suggestions['options'][0]['description']}"
            )
            raise ValueError(error_msg)
        
        link = TraceabilityLink(
            source_id=source_id,
            target_id=target_id,
            link_type=link_type,
            description=description,
            created_by=created_by,
            metadata=metadata or {}
        )
        
        self._traceability_links[source_id].append(link)
        
        logger.info(f"Added traceability link: {source_id} -> {target_id} ({link_type.value})")
        
        return link
    
    def _would_create_cycle(
        self,
        source_id: RequirementId,
        target_id: RequirementId,
        link_type: TraceabilityLinkType
    ) -> bool:
        """
        Check if adding a link would create a cycle in the dependency graph.
        
        Args:
            source_id: Source requirement ID
            target_id: Target requirement ID
            link_type: Type of link being added
            
        Returns:
            True if adding the link would create a cycle
        """
        # Only check for cycles on dependency-type links
        if link_type not in [
            TraceabilityLinkType.DEPENDS_ON,
            TraceabilityLinkType.DERIVES_FROM,
            TraceabilityLinkType.REFINES
        ]:
            return False
        
        # Check if target can reach source through existing links
        visited = set()
        
        def can_reach(current_id: RequirementId, goal_id: RequirementId) -> bool:
            if current_id == goal_id:
                return True
            
            if current_id in visited:
                return False
            
            visited.add(current_id)
            
            links = self._traceability_links.get(current_id, [])
            for link in links:
                if link.link_type in [
                    TraceabilityLinkType.DEPENDS_ON,
                    TraceabilityLinkType.DERIVES_FROM,
                    TraceabilityLinkType.REFINES
                ]:
                    if can_reach(link.target_id, goal_id):
                        return True
            
            return False
        
        return can_reach(target_id, source_id)
    
    def suggest_requirement_decomposition(
        self,
        source_id: RequirementId,
        target_id: RequirementId,
        attempted_link_type: TraceabilityLinkType
    ) -> Dict[str, Any]:
        """
        Suggest requirement decomposition when circular dependencies are detected.
        
        Args:
            source_id: Source requirement ID
            target_id: Target requirement ID  
            attempted_link_type: The link type that would create a cycle
            
        Returns:
            Decomposition suggestions
        """
        suggestions = {
            "issue": f"Circular dependency detected between {source_id} and {target_id}",
            "root_cause": "Requirements are either duplicates or need decomposition",
            "options": []
        }
        
        # Option 1: Merge requirements
        suggestions["options"].append({
            "type": "merge",
            "description": f"Merge {source_id} and {target_id} into a single requirement",
            "rationale": "If both requirements represent the same logical need, they should be combined",
            "action": f"Create new requirement that encompasses both {source_id} and {target_id}, then retire the originals"
        })
        
        # Option 2: Decompose into three requirements
        suggestions["options"].append({
            "type": "decompose",
            "description": f"Decompose into three separate requirements with clear hierarchy",
            "rationale": "Break the circular dependency by introducing an intermediate requirement",
            "action": f"Create: {source_id}-base (foundation), {source_id}-impl (implementation), {target_id}-impl (implementation)"
        })
        
        # Option 3: Identify shared dependency
        suggestions["options"].append({
            "type": "extract_shared",
            "description": "Extract shared functionality into a separate requirement",
            "rationale": "Both requirements may depend on a common underlying capability",
            "action": "Create shared requirement that both can depend on without circular reference"
        })
        
        return suggestions
    
    def get_requirement_links(
        self,
        requirement_id: RequirementId,
        link_type: Optional[TraceabilityLinkType] = None,
        direction: str = "outgoing"
    ) -> List[TraceabilityLink]:
        """
        Get traceability links for a requirement.
        
        Args:
            requirement_id: ID of the requirement
            link_type: Optional filter by link type
            direction: "outgoing" (from this req), "incoming" (to this req), or "both"
            
        Returns:
            List of traceability links
        """
        links = []
        
        if direction in ["outgoing", "both"]:
            outgoing_links = self._traceability_links.get(requirement_id, [])
            if link_type:
                outgoing_links = [link for link in outgoing_links if link.link_type == link_type]
            links.extend(outgoing_links)
        
        if direction in ["incoming", "both"]:
            # Find incoming links by searching all links
            for source_req_id, source_links in self._traceability_links.items():
                for link in source_links:
                    if link.target_id == requirement_id:
                        if not link_type or link.link_type == link_type:
                            links.append(link)
        
        return links
    
    def get_requirement_dependencies(
        self,
        requirement_id: RequirementId
    ) -> Dict[str, List[RequirementId]]:
        """
        Get all dependencies for a requirement.
        
        Args:
            requirement_id: ID of the requirement
            
        Returns:
            Dictionary of dependency types and related requirements
        """
        dependencies = defaultdict(list)
        
        links = self._traceability_links.get(requirement_id, [])
        
        for link in links:
            dependencies[link.link_type.value].append(link.target_id)
        
        return dict(dependencies)
    
    def find_requirement_conflicts(
        self,
        requirement_id: RequirementId
    ) -> List[Tuple[RequirementId, str]]:
        """
        Find conflicts for a requirement.
        
        Args:
            requirement_id: ID of the requirement
            
        Returns:
            List of conflicting requirements with descriptions
        """
        conflicts = []
        
        conflict_links = self.get_requirement_links(
            requirement_id,
            TraceabilityLinkType.CONFLICTS_WITH
        )
        
        for link in conflict_links:
            conflicts.append((link.target_id, link.description))
        
        return conflicts
    
    def record_requirement_change(
        self,
        requirement_id: RequirementId,
        change_type: ChangeType,
        old_value: Optional[str] = None,
        new_value: Optional[str] = None,
        changed_by: str = "",
        reason: str = ""
    ) -> RequirementChange:
        """
        Record a requirement change for impact analysis.
        
        Args:
            requirement_id: ID of the changed requirement
            change_type: Type of change
            old_value: Previous value (for modifications)
            new_value: New value (for modifications)
            changed_by: Who made the change
            reason: Reason for the change
            
        Returns:
            Created change record
        """
        change = RequirementChange(
            requirement_id=requirement_id,
            change_type=change_type,
            old_value=old_value,
            new_value=new_value,
            changed_by=changed_by,
            reason=reason
        )
        
        self._change_history.append(change)
        logger.info(f"Recorded change for requirement {requirement_id}: {change_type.value}")
        
        return change
    
    def analyze_change_impact(
        self,
        change: RequirementChange,
        traceability_matrix: Optional[TraceabilityMatrix] = None
    ) -> ImpactAnalysisResult:
        """
        Analyze the impact of a requirement change.
        
        Args:
            change: The requirement change to analyze
            traceability_matrix: Optional traceability matrix for broader impact
            
        Returns:
            Impact analysis result
        """
        result = ImpactAnalysisResult(change=change)
        
        # Find directly impacted requirements
        impacted_reqs = self._find_impacted_requirements(change.requirement_id)
        result.impacted_requirements = impacted_reqs
        
        # Find impacted design components and tasks if matrix provided
        if traceability_matrix:
            design_components = traceability_matrix.requirement_to_design.get(
                change.requirement_id, []
            )
            result.impacted_design_components = design_components
            
            # Find tasks through design components
            tasks = []
            for component_id in design_components:
                component_tasks = traceability_matrix.design_to_tasks.get(component_id, [])
                tasks.extend(component_tasks)
            result.impacted_tasks = tasks
        
        # Determine severity
        result.severity = self._calculate_impact_severity(result)
        
        # Generate recommendations
        result.recommendations = self._generate_impact_recommendations(result)
        
        # Estimate effort
        result.estimated_effort = self._estimate_change_effort(result)
        
        logger.info(f"Impact analysis complete for {change.requirement_id}: {result.severity.value} severity")
        
        return result
    
    def _find_impacted_requirements(self, requirement_id: RequirementId) -> List[RequirementId]:
        """Find requirements impacted by a change."""
        impacted = set()
        
        # Find requirements that depend on the changed requirement (incoming links)
        for source_req_id, source_links in self._traceability_links.items():
            for link in source_links:
                if link.target_id == requirement_id and link.link_type in [
                    TraceabilityLinkType.DEPENDS_ON,
                    TraceabilityLinkType.DERIVES_FROM,
                    TraceabilityLinkType.REFINES
                ]:
                    impacted.add(source_req_id)
        
        # Also find requirements that this requirement depends on (outgoing links)
        # These might be impacted if the changed requirement can no longer fulfill its dependencies
        outgoing_links = self._traceability_links.get(requirement_id, [])
        for link in outgoing_links:
            if link.link_type in [
                TraceabilityLinkType.DEPENDS_ON,
                TraceabilityLinkType.DERIVES_FROM,
                TraceabilityLinkType.REFINES
            ]:
                impacted.add(link.target_id)
        
        # Use BFS to find transitively impacted requirements
        queue = deque(list(impacted))
        visited = {requirement_id}
        visited.update(impacted)
        
        while queue:
            current_id = queue.popleft()
            
            # Find requirements that depend on this one
            for source_req_id, source_links in self._traceability_links.items():
                for link in source_links:
                    if (link.target_id == current_id and 
                        link.link_type in [TraceabilityLinkType.DEPENDS_ON, TraceabilityLinkType.DERIVES_FROM] and
                        source_req_id not in visited):
                        
                        impacted.add(source_req_id)
                        visited.add(source_req_id)
                        queue.append(source_req_id)
        
        return list(impacted)
    
    def _calculate_impact_severity(self, result: ImpactAnalysisResult) -> ImpactSeverity:
        """Calculate the severity of the impact."""
        impact_score = 0
        
        # Score based on number of impacted items
        impact_score += len(result.impacted_requirements) * 2
        impact_score += len(result.impacted_design_components) * 3
        impact_score += len(result.impacted_tasks) * 1
        
        # Score based on change type
        change_type_scores = {
            ChangeType.ADDED: 1,
            ChangeType.MODIFIED: 2,
            ChangeType.DELETED: 4,
            ChangeType.STATUS_CHANGED: 1
        }
        
        impact_score += change_type_scores.get(result.change.change_type, 1)
        
        # Determine severity
        if impact_score >= 20:
            return ImpactSeverity.CRITICAL
        elif impact_score >= 10:
            return ImpactSeverity.HIGH
        elif impact_score >= 5:
            return ImpactSeverity.MEDIUM
        else:
            return ImpactSeverity.LOW
    
    def _generate_impact_recommendations(self, result: ImpactAnalysisResult) -> List[str]:
        """Generate recommendations for handling the impact."""
        recommendations = []
        
        # Always provide basic recommendations
        recommendations.append("Review and validate all impacted components")
        recommendations.append("Update documentation to reflect changes")
        
        if result.severity == ImpactSeverity.CRITICAL:
            recommendations.append("Conduct thorough impact assessment before proceeding")
            recommendations.append("Consider phased implementation to reduce risk")
            recommendations.append("Ensure comprehensive testing of all impacted components")
        
        if len(result.impacted_requirements) > 5:
            recommendations.append("Review all impacted requirements for consistency")
            recommendations.append("Update requirement documentation and traceability")
        elif len(result.impacted_requirements) > 0:
            recommendations.append("Review impacted requirements for consistency")
        
        if len(result.impacted_design_components) > 0:
            recommendations.append("Review and update design documentation")
            recommendations.append("Validate architectural consistency")
        
        if len(result.impacted_tasks) > 0:
            recommendations.append("Update implementation tasks and estimates")
            recommendations.append("Reassess project timeline and resource allocation")
        
        if result.change.change_type == ChangeType.DELETED:
            recommendations.append("Verify no orphaned components remain")
            recommendations.append("Update all dependent specifications")
        elif result.change.change_type == ChangeType.MODIFIED:
            recommendations.append("Validate that changes maintain requirement integrity")
        elif result.change.change_type == ChangeType.ADDED:
            recommendations.append("Ensure new requirement integrates properly with existing requirements")
        
        return recommendations
    
    def _estimate_change_effort(self, result: ImpactAnalysisResult) -> int:
        """Estimate effort required for the change in hours."""
        base_effort = {
            ChangeType.ADDED: 2,
            ChangeType.MODIFIED: 4,
            ChangeType.DELETED: 6,
            ChangeType.STATUS_CHANGED: 1
        }
        
        effort = base_effort.get(result.change.change_type, 2)
        
        # Add effort for impacted items
        effort += len(result.impacted_requirements) * 1
        effort += len(result.impacted_design_components) * 2
        effort += len(result.impacted_tasks) * 0.5
        
        # Multiply by severity factor
        severity_multipliers = {
            ImpactSeverity.LOW: 1.0,
            ImpactSeverity.MEDIUM: 1.5,
            ImpactSeverity.HIGH: 2.0,
            ImpactSeverity.CRITICAL: 3.0
        }
        
        effort *= severity_multipliers.get(result.severity, 1.0)
        
        return int(effort)
    
    def generate_coverage_report(
        self,
        requirements: List[Requirement],
        traceability_matrix: Optional[TraceabilityMatrix] = None
    ) -> CoverageReport:
        """
        Generate a comprehensive coverage report.
        
        Args:
            requirements: List of requirements to analyze
            traceability_matrix: Optional traceability matrix for broader analysis
            
        Returns:
            Coverage report
        """
        report = CoverageReport(
            total_requirements=len(requirements),
            traced_requirements=0  # Will be calculated below
        )
        
        # Analyze business need traceability
        traced_to_business = 0
        untraceable = []
        
        for req in requirements:
            if req.id in self._requirement_to_business:
                traced_to_business += 1
            else:
                untraceable.append(req.id)
        
        report.traced_requirements = traced_to_business
        report.untraceable_requirements = untraceable
        report.coverage_percentage = (traced_to_business / len(requirements)) * 100 if requirements else 0
        
        # Analyze traceability matrix if provided
        if traceability_matrix:
            self._analyze_matrix_coverage(report, requirements, traceability_matrix)
        
        # Generate gaps and recommendations
        report.gaps = self._identify_coverage_gaps(report, requirements)
        report.recommendations = self._generate_coverage_recommendations(report)
        
        logger.info(f"Coverage report generated: {report.coverage_percentage:.1f}% coverage")
        
        return report
    
    def _analyze_matrix_coverage(
        self,
        report: CoverageReport,
        requirements: List[Requirement],
        matrix: TraceabilityMatrix
    ) -> None:
        """Analyze traceability matrix coverage."""
        # Find orphaned design components
        all_design_components = set()
        for components in matrix.requirement_to_design.values():
            all_design_components.update(components)
        
        referenced_components = set(matrix.design_to_tasks.keys())
        orphaned_design = all_design_components - referenced_components
        report.orphaned_components.extend(f"design:{comp}" for comp in orphaned_design)
        
        # Find orphaned tasks
        all_tasks = set()
        for tasks in matrix.design_to_tasks.values():
            all_tasks.update(tasks)
        
        referenced_tasks = set(matrix.task_to_implementation.keys())
        orphaned_tasks = all_tasks - referenced_tasks
        report.orphaned_components.extend(f"task:{task}" for task in orphaned_tasks)
    
    def _identify_coverage_gaps(
        self,
        report: CoverageReport,
        requirements: List[Requirement]
    ) -> List[str]:
        """Identify coverage gaps."""
        gaps = []
        
        if report.coverage_percentage < 80:
            gaps.append(f"Low business need traceability: {report.coverage_percentage:.1f}%")
        
        if len(report.untraceable_requirements) > 0:
            gaps.append(f"{len(report.untraceable_requirements)} requirements not traced to business needs")
        
        if len(report.orphaned_components) > 0:
            gaps.append(f"{len(report.orphaned_components)} orphaned components found")
        
        # Check for requirements without acceptance criteria
        no_criteria_count = sum(1 for req in requirements if len(req.acceptance_criteria) == 0)
        if no_criteria_count > 0:
            gaps.append(f"{no_criteria_count} requirements without acceptance criteria")
        
        return gaps
    
    def _generate_coverage_recommendations(self, report: CoverageReport) -> List[str]:
        """Generate recommendations for improving coverage."""
        recommendations = []
        
        if report.coverage_percentage < 100:
            recommendations.append("Link all requirements to business needs for complete traceability")
        
        if len(report.untraceable_requirements) > 0:
            recommendations.append("Review untraceable requirements - they may be unnecessary or need business justification")
        
        if len(report.orphaned_components) > 0:
            recommendations.append("Remove or properly link orphaned components")
        
        if report.coverage_percentage < 50:
            recommendations.append("Conduct comprehensive traceability review - coverage is critically low")
        
        recommendations.append("Regularly update traceability links as requirements evolve")
        recommendations.append("Use automated tools to maintain traceability consistency")
        
        return recommendations
    
    def get_requirement_trace_path(
        self,
        requirement_id: RequirementId,
        target_id: Optional[RequirementId] = None
    ) -> List[List[RequirementId]]:
        """
        Get trace paths from a requirement to target or all connected requirements.
        
        Args:
            requirement_id: Starting requirement ID
            target_id: Optional target requirement ID
            
        Returns:
            List of trace paths (each path is a list of requirement IDs)
        """
        paths = []
        
        def dfs_trace(current_id: RequirementId, path: List[RequirementId], visited: Set[RequirementId]):
            if current_id in visited:
                return
            
            visited.add(current_id)
            path.append(current_id)
            
            if target_id and current_id == target_id:
                paths.append(path.copy())
                path.pop()
                return
            elif not target_id and len(path) > 1:
                paths.append(path.copy())
            
            # Follow traceability links (all dependency types)
            links = self._traceability_links.get(current_id, [])
            for link in links:
                if link.link_type in [
                    TraceabilityLinkType.DEPENDS_ON,
                    TraceabilityLinkType.DERIVES_FROM, 
                    TraceabilityLinkType.REFINES
                ]:
                    dfs_trace(link.target_id, path, visited.copy())
            
            path.pop()
        
        dfs_trace(requirement_id, [], set())
        
        return paths
    
    def validate_traceability_consistency(self) -> List[str]:
        """
        Validate traceability consistency and return list of issues.
        
        Returns:
            List of consistency issues found
        """
        issues = []
        
        # Check for circular dependencies
        for req_id in self._traceability_links.keys():
            if self._has_circular_dependency(req_id):
                issues.append(
                    f"Circular dependency detected involving requirement {req_id}. "
                    f"Consider merging related requirements or decomposing into separate concerns."
                )
        
        # Check for conflicting relationships
        for req_id, links in self._traceability_links.items():
            conflicts = self._find_conflicting_links(links)
            for conflict in conflicts:
                issues.append(f"Conflicting relationships for requirement {req_id}: {conflict}")
        
        # Check for orphaned business needs
        used_business_needs = set()
        for business_needs in self._requirement_to_business.values():
            used_business_needs.update(business_needs)
        
        all_business_needs = set(self._business_needs.keys())
        orphaned_needs = all_business_needs - used_business_needs
        
        for orphaned in orphaned_needs:
            issues.append(f"Orphaned business need: {orphaned}")
        
        return issues
    
    def _has_circular_dependency(self, requirement_id: RequirementId) -> bool:
        """Check if a requirement has circular dependencies."""
        visited = set()
        rec_stack = set()
        
        def dfs(current_id: RequirementId) -> bool:
            visited.add(current_id)
            rec_stack.add(current_id)
            
            links = self._traceability_links.get(current_id, [])
            for link in links:
                if link.link_type in [
                    TraceabilityLinkType.DEPENDS_ON,
                    TraceabilityLinkType.DERIVES_FROM,
                    TraceabilityLinkType.REFINES
                ]:
                    target_id = link.target_id
                    
                    if target_id not in visited:
                        if dfs(target_id):
                            return True
                    elif target_id in rec_stack:
                        return True
            
            rec_stack.remove(current_id)
            return False
        
        return dfs(requirement_id)
    
    def _find_conflicting_links(self, links: List[TraceabilityLink]) -> List[str]:
        """Find conflicting relationships in a set of links."""
        conflicts = []
        
        # Group links by target
        target_links = defaultdict(list)
        for link in links:
            target_links[link.target_id].append(link)
        
        # Check for conflicting link types to same target
        for target_id, target_link_list in target_links.items():
            link_types = [link.link_type for link in target_link_list]
            
            # Check for specific conflicts
            if (TraceabilityLinkType.DEPENDS_ON in link_types and 
                TraceabilityLinkType.CONFLICTS_WITH in link_types):
                conflicts.append(f"Cannot both depend on and conflict with {target_id}")
        
        return conflicts
    
    # ReflectiveModule implementation
    def health(self) -> Dict[str, Any]:
        """Return health status of the traceability system."""
        return {
            "status": "healthy",
            "business_needs_count": len(self._business_needs),
            "traceability_links_count": sum(len(links) for links in self._traceability_links.values()),
            "change_history_count": len(self._change_history),
            "last_check": datetime.now().isoformat()
        }
    
    def ready(self) -> bool:
        """Check if traceability system is ready for operation."""
        return True  # Always ready once initialized
    
    def metrics(self) -> Dict[str, float]:
        """Return operational metrics."""
        total_links = sum(len(links) for links in self._traceability_links.values())
        
        return {
            "business_needs_count": float(len(self._business_needs)),
            "traceability_links_count": float(total_links),
            "change_history_count": float(len(self._change_history)),
            "requirements_with_links": float(len(self._traceability_links)),
            "requirements_with_business_links": float(len(self._requirement_to_business))
        }
    
    def status(self) -> str:
        """Return current operational status."""
        return "ready"