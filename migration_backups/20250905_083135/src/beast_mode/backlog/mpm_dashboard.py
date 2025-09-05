"""
MPMDashboard - Strategic backlog management interface for Marketing Product Managers

This module provides executive-level dashboard capabilities for MPMs to manage
strategic backlog across all four tracks with portfolio visibility, impact analysis,
and scenario planning tools.
"""

from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import logging
import time

from .models import BacklogItem, MPMValidation, DependencySpec
from .enums import StrategicTrack, BeastReadinessStatus, ApprovalStatus, StakeholderType, RiskLevel
from .dependency_manager import BacklogDependencyManager


class ScenarioType(Enum):
    """Types of resource allocation scenarios"""
    OPTIMISTIC = "optimistic"
    REALISTIC = "realistic"
    PESSIMISTIC = "pessimistic"
    CUSTOM = "custom"


@dataclass(frozen=True)
class PortfolioStatus:
    """Portfolio-level status across all strategic tracks"""
    total_items: int
    beast_ready_items: int
    in_progress_items: int
    blocked_items: int
    completion_percentage: float
    track_breakdown: Dict[StrategicTrack, Dict[str, int]]
    critical_path_items: List[str]
    delivery_confidence: float
    risk_assessment: Dict[RiskLevel, int]
    last_updated: datetime


@dataclass(frozen=True)
class ImpactAnalysis:
    """Impact analysis for strategic changes"""
    change_description: str
    affected_items: List[str]
    affected_tracks: List[StrategicTrack]
    timeline_impact_days: int
    resource_impact: Dict[str, float]
    risk_changes: Dict[RiskLevel, int]
    mitigation_recommendations: List[str]
    confidence_score: float
    analysis_timestamp: datetime


@dataclass(frozen=True)
class ResourceConstraints:
    """Resource constraints for scenario planning"""
    available_developers: int
    available_hours_per_week: int
    budget_constraints: Optional[float]
    timeline_constraints: Optional[datetime]
    skill_constraints: Dict[str, int]
    priority_constraints: List[str]


@dataclass(frozen=True)
class ScenarioResult:
    """Result of scenario planning analysis"""
    scenario_type: ScenarioType
    scenario_name: str
    estimated_completion: datetime
    resource_utilization: Dict[str, float]
    deliverable_timeline: Dict[StrategicTrack, datetime]
    risk_profile: Dict[RiskLevel, float]
    success_probability: float
    key_assumptions: List[str]
    critical_dependencies: List[str]
    generated_at: datetime


@dataclass(frozen=True)
class PriorityChange:
    """Specification for priority changes"""
    item_id: str
    old_priority: int
    new_priority: int
    justification: str
    impact_assessment_required: bool = True


@dataclass(frozen=True)
class StakeholderReport:
    """Report tailored for specific stakeholder audience"""
    report_id: str
    audience: StakeholderType
    title: str
    executive_summary: str
    key_metrics: Dict[str, Any]
    detailed_sections: Dict[str, Any]
    recommendations: List[str]
    next_steps: List[str]
    generated_at: datetime
    valid_until: datetime


class MPMDashboard:
    """
    Strategic backlog management dashboard for Marketing Product Managers
    
    Provides executive-level interface for:
    - Portfolio status monitoring across all strategic tracks
    - Strategic reprioritization with automatic impact analysis
    - Scenario planning for resource allocation decisions
    - Multi-audience stakeholder reporting
    """
    
    def __init__(self, dependency_manager: BacklogDependencyManager):
        self.dependency_manager = dependency_manager
        self.logger = logging.getLogger(__name__)
        self._backlog_items: Dict[str, BacklogItem] = {}
        self._cached_portfolio_status: Optional[PortfolioStatus] = None
        self._cache_timestamp: Optional[datetime] = None
        self._cache_ttl_seconds = 300  # 5 minutes cache TTL
        
        # Performance tracking
        self._performance_metrics = {
            "portfolio_queries": 0,
            "impact_analyses": 0,
            "scenario_plans": 0,
            "avg_response_time_ms": 0.0,
            "cache_hit_rate": 0.0
        }
        
    def get_portfolio_status(self) -> PortfolioStatus:
        """
        Get comprehensive portfolio status across all strategic tracks
        
        Returns:
            PortfolioStatus with current state of all backlog items
        """
        start_time = time.time()
        
        try:
            # Check cache first
            if self._is_cache_valid():
                self._performance_metrics["cache_hit_rate"] = (
                    self._performance_metrics["cache_hit_rate"] * 0.9 + 0.1
                )
                return self._cached_portfolio_status
            
            # Calculate portfolio metrics
            total_items = len(self._backlog_items)
            beast_ready_items = sum(
                1 for item in self._backlog_items.values()
                if item.beast_readiness_status == BeastReadinessStatus.BEAST_READY
            )
            in_progress_items = sum(
                1 for item in self._backlog_items.values()
                if item.beast_readiness_status == BeastReadinessStatus.IN_EXECUTION
            )
            blocked_items = sum(
                1 for item in self._backlog_items.values()
                if item.beast_readiness_status == BeastReadinessStatus.BLOCKED
            )
            
            # Calculate completion percentage
            completed_items = sum(
                1 for item in self._backlog_items.values()
                if item.beast_readiness_status == BeastReadinessStatus.COMPLETED
            )
            completion_percentage = (completed_items / total_items * 100) if total_items > 0 else 0.0
            
            # Track breakdown by strategic track
            track_breakdown = {}
            for track in StrategicTrack:
                track_items = [item for item in self._backlog_items.values() if item.track == track]
                track_breakdown[track] = {
                    "total": len(track_items),
                    "beast_ready": sum(1 for item in track_items if item.beast_readiness_status == BeastReadinessStatus.BEAST_READY),
                    "in_progress": sum(1 for item in track_items if item.beast_readiness_status == BeastReadinessStatus.IN_EXECUTION),
                    "completed": sum(1 for item in track_items if item.beast_readiness_status == BeastReadinessStatus.COMPLETED),
                    "blocked": sum(1 for item in track_items if item.beast_readiness_status == BeastReadinessStatus.BLOCKED)
                }
            
            # Get critical path items from dependency manager
            critical_path_items = self._get_critical_path_items()
            
            # Calculate delivery confidence based on beast-readiness and dependencies
            delivery_confidence = self._calculate_delivery_confidence()
            
            # Assess risk distribution
            risk_assessment = self._assess_portfolio_risks()
            
            # Create portfolio status
            portfolio_status = PortfolioStatus(
                total_items=total_items,
                beast_ready_items=beast_ready_items,
                in_progress_items=in_progress_items,
                blocked_items=blocked_items,
                completion_percentage=completion_percentage,
                track_breakdown=track_breakdown,
                critical_path_items=critical_path_items,
                delivery_confidence=delivery_confidence,
                risk_assessment=risk_assessment,
                last_updated=datetime.now()
            )
            
            # Cache the result
            self._cached_portfolio_status = portfolio_status
            self._cache_timestamp = datetime.now()
            self._performance_metrics["cache_hit_rate"] = (
                self._performance_metrics["cache_hit_rate"] * 0.9
            )
            
            # Update performance metrics
            self._update_performance_metrics("portfolio_queries", start_time)
            
            return portfolio_status
            
        except Exception as e:
            self.logger.error(f"Portfolio status calculation failed: {str(e)}")
            raise
    
    def generate_stakeholder_report(self, audience: StakeholderType, 
                                  custom_sections: Optional[Dict[str, Any]] = None) -> StakeholderReport:
        """
        Generate tailored report for specific stakeholder audience
        
        Args:
            audience: Target stakeholder type
            custom_sections: Optional custom sections to include
            
        Returns:
            StakeholderReport tailored for the audience
        """
        start_time = time.time()
        
        try:
            portfolio_status = self.get_portfolio_status()
            report_id = f"report_{audience.value}_{int(time.time())}"
            
            # Generate audience-specific content
            if audience == StakeholderType.MPM:
                report = self._generate_mpm_report(report_id, portfolio_status)
            elif audience == StakeholderType.STAKEHOLDER:
                report = self._generate_executive_report(report_id, portfolio_status)
            elif audience == StakeholderType.DEVELOPER:
                report = self._generate_developer_report(report_id, portfolio_status)
            elif audience == StakeholderType.OPERATIONS:
                report = self._generate_operations_report(report_id, portfolio_status)
            else:
                report = self._generate_generic_report(report_id, portfolio_status, audience)
            
            # Add custom sections if provided
            if custom_sections:
                detailed_sections = dict(report.detailed_sections)
                detailed_sections.update(custom_sections)
                report = StakeholderReport(
                    report_id=report.report_id,
                    audience=report.audience,
                    title=report.title,
                    executive_summary=report.executive_summary,
                    key_metrics=report.key_metrics,
                    detailed_sections=detailed_sections,
                    recommendations=report.recommendations,
                    next_steps=report.next_steps,
                    generated_at=report.generated_at,
                    valid_until=report.valid_until
                )
            
            self._update_performance_metrics("report_generation", start_time)
            return report
            
        except Exception as e:
            self.logger.error(f"Stakeholder report generation failed: {str(e)}")
            raise
    
    def perform_strategic_reprioritization(self, changes: List[PriorityChange]) -> ImpactAnalysis:
        """
        Perform strategic reprioritization with automatic impact analysis
        
        Args:
            changes: List of priority changes to analyze
            
        Returns:
            ImpactAnalysis showing impact of the proposed changes
        """
        start_time = time.time()
        
        try:
            # Validate changes
            for change in changes:
                if change.item_id not in self._backlog_items:
                    raise ValueError(f"Item {change.item_id} not found")
            
            # Analyze impact of changes
            affected_items = []
            affected_tracks = set()
            timeline_impact_days = 0
            resource_impact = {}
            risk_changes = {risk: 0 for risk in RiskLevel}
            mitigation_recommendations = []
            
            for change in changes:
                item = self._backlog_items[change.item_id]
                affected_items.append(change.item_id)
                affected_tracks.add(item.track)
                
                # Analyze dependency impact
                dependency_impact = self._analyze_dependency_impact(change)
                timeline_impact_days += dependency_impact["timeline_days"]
                
                # Analyze resource impact
                resource_impact[change.item_id] = self._calculate_resource_impact(change)
                
                # Analyze risk changes
                risk_change = self._assess_priority_risk_change(change)
                for risk_level, count in risk_change.items():
                    risk_changes[risk_level] += count
                
                # Generate mitigation recommendations
                item_recommendations = self._generate_mitigation_recommendations(change, dependency_impact)
                mitigation_recommendations.extend(item_recommendations)
            
            # Calculate overall confidence score
            confidence_score = self._calculate_reprioritization_confidence(changes, affected_items)
            
            impact_analysis = ImpactAnalysis(
                change_description=f"Strategic reprioritization of {len(changes)} items",
                affected_items=affected_items,
                affected_tracks=list(affected_tracks),
                timeline_impact_days=timeline_impact_days,
                resource_impact=resource_impact,
                risk_changes=risk_changes,
                mitigation_recommendations=mitigation_recommendations,
                confidence_score=confidence_score,
                analysis_timestamp=datetime.now()
            )
            
            self._update_performance_metrics("impact_analyses", start_time)
            return impact_analysis
            
        except Exception as e:
            self.logger.error(f"Strategic reprioritization analysis failed: {str(e)}")
            raise
    
    def run_scenario_planning(self, constraints: ResourceConstraints, 
                            scenario_type: ScenarioType = ScenarioType.REALISTIC) -> ScenarioResult:
        """
        Run scenario planning for resource allocation decisions
        
        Args:
            constraints: Resource constraints for the scenario
            scenario_type: Type of scenario to run
            
        Returns:
            ScenarioResult with projected outcomes
        """
        start_time = time.time()
        
        try:
            # Generate scenario parameters based on type
            scenario_params = self._generate_scenario_parameters(scenario_type, constraints)
            
            # Calculate estimated completion timeline
            estimated_completion = self._calculate_scenario_timeline(scenario_params, constraints)
            
            # Calculate resource utilization
            resource_utilization = self._calculate_resource_utilization(scenario_params, constraints)
            
            # Calculate deliverable timeline by track
            deliverable_timeline = self._calculate_track_timelines(scenario_params, constraints)
            
            # Assess risk profile for scenario
            risk_profile = self._assess_scenario_risks(scenario_params, constraints)
            
            # Calculate success probability
            success_probability = self._calculate_success_probability(scenario_params, risk_profile)
            
            # Generate key assumptions
            key_assumptions = self._generate_scenario_assumptions(scenario_type, constraints)
            
            # Identify critical dependencies
            critical_dependencies = self._identify_critical_dependencies(scenario_params)
            
            scenario_result = ScenarioResult(
                scenario_type=scenario_type,
                scenario_name=f"{scenario_type.value.title()} Resource Allocation",
                estimated_completion=estimated_completion,
                resource_utilization=resource_utilization,
                deliverable_timeline=deliverable_timeline,
                risk_profile=risk_profile,
                success_probability=success_probability,
                key_assumptions=key_assumptions,
                critical_dependencies=critical_dependencies,
                generated_at=datetime.now()
            )
            
            self._update_performance_metrics("scenario_plans", start_time)
            return scenario_result
            
        except Exception as e:
            self.logger.error(f"Scenario planning failed: {str(e)}")
            raise
    
    def update_backlog_items(self, items: Dict[str, BacklogItem]) -> None:
        """Update the backlog items for dashboard calculations"""
        self._backlog_items = items.copy()
        self._invalidate_cache()
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get dashboard performance metrics"""
        return self._performance_metrics.copy()
    
    # Private helper methods
    
    def _is_cache_valid(self) -> bool:
        """Check if cached portfolio status is still valid"""
        if self._cached_portfolio_status is None or self._cache_timestamp is None:
            return False
        
        age_seconds = (datetime.now() - self._cache_timestamp).total_seconds()
        return age_seconds < self._cache_ttl_seconds
    
    def _invalidate_cache(self) -> None:
        """Invalidate cached portfolio status"""
        self._cached_portfolio_status = None
        self._cache_timestamp = None
    
    def _get_critical_path_items(self) -> List[str]:
        """Get items on the critical path from dependency manager"""
        try:
            # This would integrate with the dependency manager's critical path calculation
            # For now, return items that are blocking others and not beast-ready
            critical_items = []
            
            for item_id, item in self._backlog_items.items():
                if item.beast_readiness_status in [BeastReadinessStatus.BLOCKED, BeastReadinessStatus.DRAFT]:
                    # Check if this item has dependents
                    has_dependents = any(
                        dep.target_item_id == item_id 
                        for other_item in self._backlog_items.values()
                        for dep in other_item.dependencies
                    )
                    if has_dependents:
                        critical_items.append(item_id)
            
            return critical_items
            
        except Exception as e:
            self.logger.warning(f"Critical path calculation failed: {str(e)}")
            return []
    
    def _calculate_delivery_confidence(self) -> float:
        """Calculate overall delivery confidence based on beast-readiness and dependencies"""
        if not self._backlog_items:
            return 0.0
        
        # Base confidence on beast-readiness distribution
        total_items = len(self._backlog_items)
        beast_ready_count = sum(
            1 for item in self._backlog_items.values()
            if item.beast_readiness_status == BeastReadinessStatus.BEAST_READY
        )
        completed_count = sum(
            1 for item in self._backlog_items.values()
            if item.beast_readiness_status == BeastReadinessStatus.COMPLETED
        )
        blocked_count = sum(
            1 for item in self._backlog_items.values()
            if item.beast_readiness_status == BeastReadinessStatus.BLOCKED
        )
        
        # Calculate base confidence
        readiness_score = (beast_ready_count + completed_count) / total_items
        
        # Adjust for blocked items (reduce confidence)
        blocked_penalty = (blocked_count / total_items) * 0.3
        
        # Adjust for MPM validation quality
        validation_bonus = self._calculate_validation_quality_bonus()
        
        confidence = max(0.0, min(1.0, readiness_score - blocked_penalty + validation_bonus))
        return confidence
    
    def _assess_portfolio_risks(self) -> Dict[RiskLevel, int]:
        """Assess risk distribution across portfolio"""
        risk_counts = {risk: 0 for risk in RiskLevel}
        
        for item in self._backlog_items.values():
            # Assess risk based on status and dependencies
            if item.beast_readiness_status == BeastReadinessStatus.BLOCKED:
                risk_counts[RiskLevel.HIGH] += 1
            elif item.beast_readiness_status == BeastReadinessStatus.DRAFT:
                risk_counts[RiskLevel.MEDIUM] += 1
            elif item.beast_readiness_status == BeastReadinessStatus.BEAST_READY:
                risk_counts[RiskLevel.LOW] += 1
            else:
                risk_counts[RiskLevel.LOW] += 1
        
        return risk_counts
    
    def _calculate_validation_quality_bonus(self) -> float:
        """Calculate bonus confidence from MPM validation quality"""
        validated_items = [
            item for item in self._backlog_items.values()
            if item.mpm_validation is not None
        ]
        
        if not validated_items:
            return 0.0
        
        avg_completeness = sum(
            item.mpm_validation.completeness_score for item in validated_items
        ) / len(validated_items)
        
        avg_confidence = sum(
            item.mpm_validation.dependency_confidence for item in validated_items
        ) / len(validated_items)
        
        return (avg_completeness + avg_confidence) / 2 * 0.2  # Max 20% bonus
    
    def _update_performance_metrics(self, operation: str, start_time: float) -> None:
        """Update performance metrics for operations"""
        duration_ms = (time.time() - start_time) * 1000
        
        if operation in self._performance_metrics:
            self._performance_metrics[operation] += 1
        
        # Update average response time
        current_avg = self._performance_metrics["avg_response_time_ms"]
        total_ops = sum(
            self._performance_metrics[key] for key in 
            ["portfolio_queries", "impact_analyses", "scenario_plans"]
            if key in self._performance_metrics
        )
        
        if total_ops > 0:
            new_avg = ((current_avg * (total_ops - 1)) + duration_ms) / total_ops
            self._performance_metrics["avg_response_time_ms"] = new_avg    

    # Report generation methods
    
    def _generate_mpm_report(self, report_id: str, portfolio_status: PortfolioStatus) -> StakeholderReport:
        """Generate detailed report for MPM audience"""
        return StakeholderReport(
            report_id=report_id,
            audience=StakeholderType.MPM,
            title="Strategic Portfolio Management Dashboard",
            executive_summary=f"Portfolio contains {portfolio_status.total_items} items across 4 strategic tracks. "
                            f"{portfolio_status.beast_ready_items} items are beast-ready ({portfolio_status.beast_ready_items/portfolio_status.total_items*100:.1f}%). "
                            f"Delivery confidence: {portfolio_status.delivery_confidence:.1%}.",
            key_metrics={
                "beast_readiness_rate": portfolio_status.beast_ready_items / portfolio_status.total_items if portfolio_status.total_items > 0 else 0,
                "completion_percentage": portfolio_status.completion_percentage,
                "delivery_confidence": portfolio_status.delivery_confidence,
                "critical_path_items": len(portfolio_status.critical_path_items),
                "blocked_items": portfolio_status.blocked_items
            },
            detailed_sections={
                "track_breakdown": portfolio_status.track_breakdown,
                "risk_assessment": portfolio_status.risk_assessment,
                "critical_path": portfolio_status.critical_path_items,
                "performance_metrics": self._performance_metrics
            },
            recommendations=self._generate_mpm_recommendations(portfolio_status),
            next_steps=self._generate_mpm_next_steps(portfolio_status),
            generated_at=datetime.now(),
            valid_until=datetime.now() + timedelta(hours=24)
        )
    
    def _generate_executive_report(self, report_id: str, portfolio_status: PortfolioStatus) -> StakeholderReport:
        """Generate high-level report for executive stakeholders"""
        return StakeholderReport(
            report_id=report_id,
            audience=StakeholderType.STAKEHOLDER,
            title="OpenFlow Strategic Progress Report",
            executive_summary=f"Strategic development is {portfolio_status.completion_percentage:.1f}% complete. "
                            f"Delivery confidence is {portfolio_status.delivery_confidence:.1%} with "
                            f"{portfolio_status.blocked_items} items requiring attention.",
            key_metrics={
                "overall_progress": portfolio_status.completion_percentage,
                "delivery_confidence": portfolio_status.delivery_confidence,
                "items_at_risk": portfolio_status.blocked_items,
                "tracks_on_schedule": sum(1 for track_data in portfolio_status.track_breakdown.values() 
                                        if track_data["blocked"] == 0)
            },
            detailed_sections={
                "strategic_tracks": {
                    track.value: {
                        "progress": f"{track_data['completed']}/{track_data['total']} items completed",
                        "status": "on_track" if track_data["blocked"] == 0 else "at_risk"
                    }
                    for track, track_data in portfolio_status.track_breakdown.items()
                },
                "delivery_timeline": "Q2 2025 (subject to dependency resolution)"
            },
            recommendations=self._generate_executive_recommendations(portfolio_status),
            next_steps=self._generate_executive_next_steps(portfolio_status),
            generated_at=datetime.now(),
            valid_until=datetime.now() + timedelta(days=7)
        )
    
    def _generate_developer_report(self, report_id: str, portfolio_status: PortfolioStatus) -> StakeholderReport:
        """Generate technical report for developer audience"""
        return StakeholderReport(
            report_id=report_id,
            audience=StakeholderType.DEVELOPER,
            title="Development Team Backlog Status",
            executive_summary=f"{portfolio_status.beast_ready_items} items are ready for pickup. "
                            f"{portfolio_status.in_progress_items} items currently in development. "
                            f"Focus on critical path items to unblock dependencies.",
            key_metrics={
                "available_work": portfolio_status.beast_ready_items,
                "work_in_progress": portfolio_status.in_progress_items,
                "critical_path_items": len(portfolio_status.critical_path_items),
                "avg_response_time": self._performance_metrics["avg_response_time_ms"]
            },
            detailed_sections={
                "ready_items_by_track": {
                    track.value: track_data["beast_ready"]
                    for track, track_data in portfolio_status.track_breakdown.items()
                },
                "critical_path_items": portfolio_status.critical_path_items,
                "technical_debt": "Dependency resolution required for blocked items"
            },
            recommendations=self._generate_developer_recommendations(portfolio_status),
            next_steps=self._generate_developer_next_steps(portfolio_status),
            generated_at=datetime.now(),
            valid_until=datetime.now() + timedelta(hours=12)
        )
    
    def _generate_operations_report(self, report_id: str, portfolio_status: PortfolioStatus) -> StakeholderReport:
        """Generate operational report for operations team"""
        return StakeholderReport(
            report_id=report_id,
            audience=StakeholderType.OPERATIONS,
            title="Backlog Operations Health Report",
            executive_summary=f"System processing {portfolio_status.total_items} items with "
                            f"{self._performance_metrics['avg_response_time_ms']:.1f}ms avg response time. "
                            f"Cache hit rate: {self._performance_metrics['cache_hit_rate']:.1%}.",
            key_metrics={
                "system_performance": self._performance_metrics["avg_response_time_ms"],
                "cache_efficiency": self._performance_metrics["cache_hit_rate"],
                "data_consistency": "healthy",
                "error_rate": 0.0  # Would be calculated from actual error tracking
            },
            detailed_sections={
                "performance_metrics": self._performance_metrics,
                "system_health": "All systems operational",
                "capacity_planning": f"Current load: {portfolio_status.total_items} items"
            },
            recommendations=self._generate_operations_recommendations(portfolio_status),
            next_steps=self._generate_operations_next_steps(portfolio_status),
            generated_at=datetime.now(),
            valid_until=datetime.now() + timedelta(hours=6)
        )
    
    def _generate_generic_report(self, report_id: str, portfolio_status: PortfolioStatus, 
                               audience: StakeholderType) -> StakeholderReport:
        """Generate generic report for other audiences"""
        return StakeholderReport(
            report_id=report_id,
            audience=audience,
            title=f"Backlog Status Report - {audience.value.title()}",
            executive_summary=f"Portfolio status: {portfolio_status.completion_percentage:.1f}% complete, "
                            f"{portfolio_status.beast_ready_items} items ready for execution.",
            key_metrics={
                "completion_rate": portfolio_status.completion_percentage,
                "ready_items": portfolio_status.beast_ready_items,
                "total_items": portfolio_status.total_items
            },
            detailed_sections={
                "status_breakdown": {
                    "beast_ready": portfolio_status.beast_ready_items,
                    "in_progress": portfolio_status.in_progress_items,
                    "blocked": portfolio_status.blocked_items
                }
            },
            recommendations=["Review portfolio status regularly", "Focus on unblocking critical items"],
            next_steps=["Contact MPM for detailed planning", "Review specific track progress"],
            generated_at=datetime.now(),
            valid_until=datetime.now() + timedelta(days=1)
        )
    
    # Recommendation generation methods
    
    def _generate_mpm_recommendations(self, portfolio_status: PortfolioStatus) -> List[str]:
        """Generate recommendations for MPM audience"""
        recommendations = []
        
        if portfolio_status.blocked_items > 0:
            recommendations.append(f"Address {portfolio_status.blocked_items} blocked items to improve delivery confidence")
        
        if portfolio_status.delivery_confidence < 0.7:
            recommendations.append("Improve beast-readiness validation to increase delivery confidence")
        
        if len(portfolio_status.critical_path_items) > 5:
            recommendations.append("Focus on critical path items to reduce delivery risk")
        
        # Track-specific recommendations
        for track, track_data in portfolio_status.track_breakdown.items():
            if track_data["blocked"] > track_data["total"] * 0.2:  # More than 20% blocked
                recommendations.append(f"Prioritize unblocking {track.value} track items")
        
        return recommendations
    
    def _generate_mpm_next_steps(self, portfolio_status: PortfolioStatus) -> List[str]:
        """Generate next steps for MPM audience"""
        next_steps = []
        
        if portfolio_status.critical_path_items:
            next_steps.append("Review critical path items and resolve blocking dependencies")
        
        next_steps.append("Conduct Ghostbusters validation for items in MPM_REVIEW status")
        next_steps.append("Update stakeholder reports and communicate delivery timeline changes")
        
        if portfolio_status.delivery_confidence < 0.8:
            next_steps.append("Run scenario planning to identify resource allocation improvements")
        
        return next_steps
    
    def _generate_executive_recommendations(self, portfolio_status: PortfolioStatus) -> List[str]:
        """Generate recommendations for executive audience"""
        recommendations = []
        
        if portfolio_status.delivery_confidence < 0.8:
            recommendations.append("Consider additional resources to improve delivery confidence")
        
        if portfolio_status.blocked_items > portfolio_status.total_items * 0.1:
            recommendations.append("Escalate dependency resolution to unblock strategic progress")
        
        return recommendations
    
    def _generate_executive_next_steps(self, portfolio_status: PortfolioStatus) -> List[str]:
        """Generate next steps for executive audience"""
        return [
            "Review monthly strategic progress in upcoming board meeting",
            "Approve additional resources if delivery confidence remains low",
            "Monitor critical path resolution progress weekly"
        ]
    
    def _generate_developer_recommendations(self, portfolio_status: PortfolioStatus) -> List[str]:
        """Generate recommendations for developer audience"""
        recommendations = []
        
        if portfolio_status.beast_ready_items > 0:
            recommendations.append(f"Pick up any of {portfolio_status.beast_ready_items} beast-ready items")
        
        if portfolio_status.critical_path_items:
            recommendations.append("Prioritize critical path items to unblock dependent work")
        
        return recommendations
    
    def _generate_developer_next_steps(self, portfolio_status: PortfolioStatus) -> List[str]:
        """Generate next steps for developer audience"""
        return [
            "Check beast execution pool for available work",
            "Coordinate with MPM on dependency resolution",
            "Update item status when work is completed"
        ]
    
    def _generate_operations_recommendations(self, portfolio_status: PortfolioStatus) -> List[str]:
        """Generate recommendations for operations audience"""
        recommendations = []
        
        if self._performance_metrics["avg_response_time_ms"] > 400:
            recommendations.append("Monitor system performance - approaching response time limits")
        
        if self._performance_metrics["cache_hit_rate"] < 0.8:
            recommendations.append("Review cache configuration to improve performance")
        
        return recommendations
    
    def _generate_operations_next_steps(self, portfolio_status: PortfolioStatus) -> List[str]:
        """Generate next steps for operations audience"""
        return [
            "Monitor system health metrics continuously",
            "Review capacity planning for portfolio growth",
            "Ensure backup and recovery procedures are tested"
        ]
    
    # Impact analysis helper methods
    
    def _analyze_dependency_impact(self, change: PriorityChange) -> Dict[str, Any]:
        """Analyze impact of priority change on dependencies"""
        # Simplified implementation - would integrate with dependency manager
        return {
            "timeline_days": abs(change.new_priority - change.old_priority) * 2,  # Rough estimate
            "affected_dependencies": [],
            "cascade_effects": []
        }
    
    def _calculate_resource_impact(self, change: PriorityChange) -> float:
        """Calculate resource impact of priority change"""
        # Simplified calculation based on priority delta
        priority_delta = abs(change.new_priority - change.old_priority)
        return priority_delta * 0.1  # 10% resource impact per priority level
    
    def _assess_priority_risk_change(self, change: PriorityChange) -> Dict[RiskLevel, int]:
        """Assess how priority change affects risk levels"""
        risk_changes = {risk: 0 for risk in RiskLevel}
        
        if change.new_priority > change.old_priority:
            # Increasing priority may reduce risk
            risk_changes[RiskLevel.MEDIUM] = -1
            risk_changes[RiskLevel.LOW] = 1
        else:
            # Decreasing priority may increase risk
            risk_changes[RiskLevel.LOW] = -1
            risk_changes[RiskLevel.MEDIUM] = 1
        
        return risk_changes
    
    def _generate_mitigation_recommendations(self, change: PriorityChange, 
                                          dependency_impact: Dict[str, Any]) -> List[str]:
        """Generate mitigation recommendations for priority change"""
        recommendations = []
        
        if dependency_impact["timeline_days"] > 7:
            recommendations.append(f"Consider parallel work streams to mitigate {dependency_impact['timeline_days']} day delay")
        
        if change.new_priority < change.old_priority:
            recommendations.append("Communicate priority reduction to affected stakeholders")
        
        return recommendations
    
    def _calculate_reprioritization_confidence(self, changes: List[PriorityChange], 
                                            affected_items: List[str]) -> float:
        """Calculate confidence score for reprioritization"""
        # Base confidence on number of changes and their magnitude
        total_priority_delta = sum(abs(change.new_priority - change.old_priority) for change in changes)
        
        # Lower confidence for larger changes
        if total_priority_delta > 20:
            return 0.6
        elif total_priority_delta > 10:
            return 0.8
        else:
            return 0.9
    
    # Scenario planning helper methods
    
    def _generate_scenario_parameters(self, scenario_type: ScenarioType, 
                                    constraints: ResourceConstraints) -> Dict[str, Any]:
        """Generate parameters for scenario planning"""
        base_velocity = constraints.available_developers * constraints.available_hours_per_week / 40  # Items per week
        
        if scenario_type == ScenarioType.OPTIMISTIC:
            velocity_multiplier = 1.3
            risk_factor = 0.1
        elif scenario_type == ScenarioType.PESSIMISTIC:
            velocity_multiplier = 0.7
            risk_factor = 0.3
        else:  # REALISTIC
            velocity_multiplier = 1.0
            risk_factor = 0.2
        
        return {
            "velocity": base_velocity * velocity_multiplier,
            "risk_factor": risk_factor,
            "efficiency": velocity_multiplier
        }
    
    def _calculate_scenario_timeline(self, scenario_params: Dict[str, Any], 
                                   constraints: ResourceConstraints) -> datetime:
        """Calculate estimated completion timeline for scenario"""
        remaining_items = sum(
            1 for item in self._backlog_items.values()
            if item.beast_readiness_status not in [BeastReadinessStatus.COMPLETED]
        )
        
        weeks_needed = remaining_items / scenario_params["velocity"]
        weeks_needed *= (1 + scenario_params["risk_factor"])  # Add risk buffer
        
        return datetime.now() + timedelta(weeks=weeks_needed)
    
    def _calculate_resource_utilization(self, scenario_params: Dict[str, Any], 
                                      constraints: ResourceConstraints) -> Dict[str, float]:
        """Calculate resource utilization for scenario"""
        return {
            "developers": min(1.0, scenario_params["efficiency"]),
            "time": scenario_params["efficiency"],
            "budget": 0.8 if constraints.budget_constraints else 1.0
        }
    
    def _calculate_track_timelines(self, scenario_params: Dict[str, Any], 
                                 constraints: ResourceConstraints) -> Dict[StrategicTrack, datetime]:
        """Calculate completion timeline by track"""
        timelines = {}
        
        for track in StrategicTrack:
            track_items = [item for item in self._backlog_items.values() if item.track == track]
            remaining_items = sum(
                1 for item in track_items
                if item.beast_readiness_status not in [BeastReadinessStatus.COMPLETED]
            )
            
            weeks_needed = remaining_items / (scenario_params["velocity"] / 4)  # Divide velocity across tracks
            timelines[track] = datetime.now() + timedelta(weeks=weeks_needed)
        
        return timelines
    
    def _assess_scenario_risks(self, scenario_params: Dict[str, Any], 
                             constraints: ResourceConstraints) -> Dict[RiskLevel, float]:
        """Assess risk profile for scenario"""
        base_risk = scenario_params["risk_factor"]
        
        return {
            RiskLevel.LOW: max(0.0, 1.0 - base_risk * 2),
            RiskLevel.MEDIUM: base_risk,
            RiskLevel.HIGH: base_risk * 0.5,
            RiskLevel.CRITICAL: max(0.0, base_risk - 0.2)
        }
    
    def _calculate_success_probability(self, scenario_params: Dict[str, Any], 
                                     risk_profile: Dict[RiskLevel, float]) -> float:
        """Calculate success probability for scenario"""
        # Higher efficiency and lower risk = higher success probability
        efficiency_factor = scenario_params["efficiency"]
        risk_factor = risk_profile[RiskLevel.HIGH] + risk_profile[RiskLevel.CRITICAL]
        
        return max(0.1, min(0.95, efficiency_factor - risk_factor))
    
    def _generate_scenario_assumptions(self, scenario_type: ScenarioType, 
                                     constraints: ResourceConstraints) -> List[str]:
        """Generate key assumptions for scenario"""
        assumptions = [
            f"Team velocity based on {constraints.available_developers} developers",
            f"Available capacity: {constraints.available_hours_per_week} hours/week",
            "No major scope changes during execution"
        ]
        
        if scenario_type == ScenarioType.OPTIMISTIC:
            assumptions.append("Minimal blockers and high team efficiency")
        elif scenario_type == ScenarioType.PESSIMISTIC:
            assumptions.append("Significant blockers and integration challenges")
        else:
            assumptions.append("Normal development challenges and dependencies")
        
        return assumptions
    
    def _identify_critical_dependencies(self, scenario_params: Dict[str, Any]) -> List[str]:
        """Identify critical dependencies for scenario"""
        # Return items that are blocking others and not yet beast-ready
        return [
            item_id for item_id in self._get_critical_path_items()
            if self._backlog_items[item_id].beast_readiness_status != BeastReadinessStatus.BEAST_READY
        ]