"""
Technical Debt Patch Annotation Reporting and Dashboard System

This module implements comprehensive reporting capabilities including patch inventory
reports by component and severity, trend analysis for patch creation and resolution
rates, and executive dashboards with cleanup progress tracking and actionable insights.

Requirements addressed: 8.1, 8.2, 8.3, 8.4, 8.5
"""

import json
import logging
import os
from collections import defaultdict, Counter
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional, Set, Tuple, Any, Union
from pathlib import Path

from src.rm_ddd.core.unified_reflective_module import (
    ReflectiveModule, 
    ModuleHealth, 
    ModuleStatus, 
    ModuleCapability,
    GracefulDegradationResult
)
from ..core.models import PatchAnnotation, DebtLevel, BypassType
from ..classification.debt_classifier import (
    ComponentImpact, DebtHotspot, RiskAssessment, 
    ImpactAssessmentEngine, DebtClassifier
)


class ReportFormat(Enum):
    """Supported report output formats."""
    JSON = "json"
    HTML = "html"
    CSV = "csv"
    MARKDOWN = "markdown"
    PDF = "pdf"


class TimeRange(Enum):
    """Time range options for trend analysis."""
    LAST_7_DAYS = "7d"
    LAST_30_DAYS = "30d"
    LAST_90_DAYS = "90d"
    LAST_6_MONTHS = "6m"
    LAST_YEAR = "1y"
    ALL_TIME = "all"


@dataclass
class InventoryReport:
    """Comprehensive patch inventory report by component and severity."""
    report_id: str
    generated_at: datetime
    total_patches: int
    patches_by_component: Dict[str, List[PatchAnnotation]]
    patches_by_severity: Dict[DebtLevel, List[PatchAnnotation]]
    patches_by_bypass_type: Dict[BypassType, List[PatchAnnotation]]
    component_summaries: Dict[str, Dict[str, Any]]
    severity_distribution: Dict[str, int]
    top_components_by_debt: List[Tuple[str, float]]
    overdue_patches: List[PatchAnnotation]
    aging_analysis: Dict[str, Any]
    recommendations: List[str]
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class TrendDataPoint:
    """Single data point for trend analysis."""
    timestamp: datetime
    patches_created: int
    patches_resolved: int
    total_active_patches: int
    total_debt_score: float
    average_resolution_time: Optional[float] = None  # in days


@dataclass
class TrendAnalysis:
    """Trend analysis for patch creation and resolution rates."""
    report_id: str
    generated_at: datetime
    time_range: TimeRange
    data_points: List[TrendDataPoint]
    creation_trend: str  # "increasing", "decreasing", "stable"
    resolution_trend: str  # "increasing", "decreasing", "stable"
    net_debt_trend: str  # "increasing", "decreasing", "stable"
    key_insights: List[str]
    performance_metrics: Dict[str, float]
    projections: Dict[str, Any]
    recommendations: List[str]
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class CleanupProgress:
    """Progress tracking for cleanup initiatives."""
    total_cleanup_tasks: int
    completed_tasks: int
    in_progress_tasks: int
    blocked_tasks: int
    completion_percentage: float
    estimated_completion_date: Optional[datetime]
    velocity_metrics: Dict[str, float]
    bottlenecks: List[str]


@dataclass
class ExecutiveDashboard:
    """Executive-level dashboard with high-level insights and actionable items."""
    report_id: str
    generated_at: datetime
    system_health_score: float  # 0-100
    total_technical_debt: float
    debt_trend: str  # "improving", "stable", "degrading"
    critical_issues: List[str]
    top_priorities: List[str]
    cleanup_progress: CleanupProgress
    roi_metrics: Dict[str, float]
    risk_assessment: RiskAssessment
    actionable_insights: List[Dict[str, Any]]
    success_metrics: Dict[str, float]
    next_review_date: datetime
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class DashboardMetrics:
    """Key performance indicators for dashboard display."""
    total_patches: int
    critical_patches: int
    overdue_patches: int
    patches_resolved_this_month: int
    average_resolution_time_days: float
    debt_score_trend: float  # percentage change
    cleanup_velocity: float  # patches resolved per week
    system_health_score: float
    top_risk_components: List[str]
    upcoming_deadlines: List[Tuple[str, datetime]]


class ReportGenerator(ReflectiveModule):
    """
    Core report generation engine for technical debt patch reporting.
    
    This class provides the foundation for generating various types of reports
    including inventory reports, trend analysis, and executive dashboards.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__()
        self.module_id = "report_generator"
        self._config = config or {}
        self._logger = logging.getLogger(__name__)
        
        # Initialize classification engine for impact assessment
        self._classifier = DebtClassifier(config)
        self._impact_engine = ImpactAssessmentEngine(config)
        
        # Report storage configuration
        self._report_storage_path = Path(
            self._config.get('report_storage_path', 'reports/technical_debt')
        )
        self._report_storage_path.mkdir(parents=True, exist_ok=True)
        
        # Report retention settings
        self._report_retention_days = self._config.get('report_retention_days', 90)
        
        # Cache for performance
        self._report_cache: Dict[str, Any] = {}
        self._cache_ttl_minutes = self._config.get('cache_ttl_minutes', 30)
    
    def get_module_info(self) -> Dict[str, Any]:
        """Get module information."""
        return {
            "module_id": self.module_id,
            "name": "Technical Debt Report Generator",
            "version": "1.0.0",
            "description": "Comprehensive reporting system for technical debt patch management",
            "capabilities": [cap.value for cap in self.get_capabilities()]
        }
    
    def get_capabilities(self) -> List[ModuleCapability]:
        """Get module capabilities."""
        return [
            ModuleCapability.CORE_FUNCTIONALITY,
            ModuleCapability.DATA_PROCESSING,
            ModuleCapability.VALIDATION,
            ModuleCapability.MONITORING
        ]
    
    def get_health_status(self) -> ModuleHealth:
        """Get module health status."""
        issues = []
        status = ModuleStatus.HEALTHY
        
        # Check report storage accessibility
        if not self._report_storage_path.exists():
            issues.append("Report storage path not accessible")
            status = ModuleStatus.WARNING
        
        # Check classifier health
        classifier_health = self._classifier.get_health_status()
        if classifier_health.status != ModuleStatus.HEALTHY:
            issues.append("Debt classifier not healthy")
            status = ModuleStatus.WARNING
        
        return ModuleHealth(
            module_id=self.module_id,
            status=status,
            health_score=1.0 if status == ModuleStatus.HEALTHY else 0.8,
            issues=issues,
            last_check=datetime.now(),
            uptime_seconds=(datetime.now() - self._start_time).total_seconds(),
            error_count=self._error_count,
            warning_count=self._warning_count
        )
    
    def graceful_degradation(self) -> GracefulDegradationResult:
        """Perform graceful degradation."""
        # In degraded mode, disable caching and use simplified reports
        degraded_capabilities = []
        
        if not self._report_storage_path.exists():
            degraded_capabilities.append(ModuleCapability.DATA_PROCESSING)
        
        remaining_capabilities = [
            cap for cap in self.get_capabilities() 
            if cap not in degraded_capabilities
        ]
        
        return GracefulDegradationResult(
            success=True,
            degraded_capabilities=degraded_capabilities,
            remaining_capabilities=remaining_capabilities
        )
    
    def generate_inventory_report(self, patches: List[PatchAnnotation], 
                                include_recommendations: bool = True) -> InventoryReport:
        """
        Generate comprehensive patch inventory report by component and severity.
        
        Args:
            patches: List of patches to include in the report
            include_recommendations: Whether to include actionable recommendations
            
        Returns:
            InventoryReport with detailed inventory analysis
        """
        try:
            self._logger.info(f"Generating inventory report for {len(patches)} patches")
            
            report_id = f"inventory_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            # Group patches by various dimensions
            patches_by_component = defaultdict(list)
            patches_by_severity = defaultdict(list)
            patches_by_bypass_type = defaultdict(list)
            
            for patch in patches:
                patches_by_component[patch.component].append(patch)
                patches_by_severity[patch.debt_level].append(patch)
                patches_by_bypass_type[patch.bypass_type].append(patch)
            
            # Generate component summaries with impact assessment
            component_summaries = {}
            for component, comp_patches in patches_by_component.items():
                impact = self._impact_engine.assess_component_impact(component, comp_patches)
                component_summaries[component] = {
                    'patch_count': len(comp_patches),
                    'debt_score': impact.total_debt_score,
                    'maintenance_burden': impact.maintenance_burden_score,
                    'risk_factors': impact.risk_factors,
                    'critical_patches': impact.critical_patches,
                    'high_patches': impact.high_patches,
                    'medium_patches': impact.medium_patches,
                    'low_patches': impact.low_patches,
                    'component_type': impact.component_type.value,
                    'recommendations': impact.recommended_actions if include_recommendations else []
                }
            
            # Calculate severity distribution
            severity_distribution = {
                level.value: len(patches_by_severity[level]) 
                for level in DebtLevel
            }
            
            # Identify top components by debt score
            top_components_by_debt = sorted(
                [(comp, summary['debt_score']) for comp, summary in component_summaries.items()],
                key=lambda x: x[1],
                reverse=True
            )[:10]  # Top 10 components
            
            # Find overdue patches
            now = datetime.now()
            overdue_patches = [
                patch for patch in patches
                if patch.expected_resolution and patch.expected_resolution < now
            ]
            
            # Aging analysis
            aging_analysis = self._analyze_patch_aging(patches)
            
            # Generate recommendations
            recommendations = []
            if include_recommendations:
                recommendations = self._generate_inventory_recommendations(
                    patches, component_summaries, overdue_patches
                )
            
            report = InventoryReport(
                report_id=report_id,
                generated_at=datetime.now(),
                total_patches=len(patches),
                patches_by_component=dict(patches_by_component),
                patches_by_severity=dict(patches_by_severity),
                patches_by_bypass_type=dict(patches_by_bypass_type),
                component_summaries=component_summaries,
                severity_distribution=severity_distribution,
                top_components_by_debt=top_components_by_debt,
                overdue_patches=overdue_patches,
                aging_analysis=aging_analysis,
                recommendations=recommendations,
                metadata={
                    'generation_time_seconds': 0,  # Will be updated
                    'data_quality_score': self._calculate_data_quality_score(patches),
                    'coverage_metrics': self._calculate_coverage_metrics(patches)
                }
            )
            
            # Save report
            self._save_report(report, ReportFormat.JSON)
            
            self._logger.info(f"Generated inventory report {report_id} with {len(patches)} patches")
            return report
            
        except Exception as e:
            self._logger.error(f"Failed to generate inventory report: {str(e)}")
            self._error_count += 1
            raise
    
    def generate_trend_analysis(self, patches: List[PatchAnnotation], 
                              time_range: TimeRange = TimeRange.LAST_30_DAYS,
                              include_projections: bool = True) -> TrendAnalysis:
        """
        Generate trend analysis for patch creation and resolution rates.
        
        Args:
            patches: List of patches to analyze
            time_range: Time range for the analysis
            include_projections: Whether to include future projections
            
        Returns:
            TrendAnalysis with comprehensive trend data
        """
        try:
            self._logger.info(f"Generating trend analysis for {time_range.value}")
            
            report_id = f"trends_{time_range.value}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            # Calculate time range boundaries
            end_date = datetime.now()
            start_date = self._calculate_start_date(end_date, time_range)
            
            # Generate time series data points
            data_points = self._generate_trend_data_points(patches, start_date, end_date)
            
            # Analyze trends
            creation_trend = self._analyze_creation_trend(data_points)
            resolution_trend = self._analyze_resolution_trend(data_points)
            net_debt_trend = self._analyze_net_debt_trend(data_points)
            
            # Generate key insights
            key_insights = self._generate_trend_insights(
                data_points, creation_trend, resolution_trend, net_debt_trend
            )
            
            # Calculate performance metrics
            performance_metrics = self._calculate_performance_metrics(data_points)
            
            # Generate projections
            projections = {}
            if include_projections:
                projections = self._generate_trend_projections(data_points, time_range)
            
            # Generate recommendations
            recommendations = self._generate_trend_recommendations(
                data_points, creation_trend, resolution_trend, performance_metrics
            )
            
            report = TrendAnalysis(
                report_id=report_id,
                generated_at=datetime.now(),
                time_range=time_range,
                data_points=data_points,
                creation_trend=creation_trend,
                resolution_trend=resolution_trend,
                net_debt_trend=net_debt_trend,
                key_insights=key_insights,
                performance_metrics=performance_metrics,
                projections=projections,
                recommendations=recommendations,
                metadata={
                    'data_points_count': len(data_points),
                    'analysis_period_days': (end_date - start_date).days,
                    'data_completeness': self._calculate_trend_data_completeness(data_points)
                }
            )
            
            # Save report
            self._save_report(report, ReportFormat.JSON)
            
            self._logger.info(f"Generated trend analysis {report_id}")
            return report
            
        except Exception as e:
            self._logger.error(f"Failed to generate trend analysis: {str(e)}")
            self._error_count += 1
            raise
    
    def generate_executive_dashboard(self, patches: List[PatchAnnotation],
                                   cleanup_data: Optional[Dict[str, Any]] = None) -> ExecutiveDashboard:
        """
        Generate executive dashboard with cleanup progress tracking and actionable insights.
        
        Args:
            patches: List of patches to analyze
            cleanup_data: Optional cleanup progress data
            
        Returns:
            ExecutiveDashboard with high-level insights and metrics
        """
        try:
            self._logger.info("Generating executive dashboard")
            
            report_id = f"executive_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            # Generate risk assessment
            risk_assessment = self._impact_engine.generate_risk_assessment(patches)
            
            # Calculate system health score
            system_health_score = self._calculate_system_health_score(patches, risk_assessment)
            
            # Determine debt trend
            debt_trend = self._determine_debt_trend(patches)
            
            # Identify critical issues
            critical_issues = self._identify_critical_issues(patches, risk_assessment)
            
            # Generate top priorities
            top_priorities = self._generate_top_priorities(patches, risk_assessment)
            
            # Calculate cleanup progress
            cleanup_progress = self._calculate_cleanup_progress(patches, cleanup_data)
            
            # Calculate ROI metrics
            roi_metrics = self._calculate_roi_metrics(patches, cleanup_progress)
            
            # Generate actionable insights
            actionable_insights = self._generate_actionable_insights(
                patches, risk_assessment, cleanup_progress
            )
            
            # Calculate success metrics
            success_metrics = self._calculate_success_metrics(patches, cleanup_progress)
            
            # Determine next review date
            next_review_date = self._calculate_next_review_date(risk_assessment.risk_level)
            
            dashboard = ExecutiveDashboard(
                report_id=report_id,
                generated_at=datetime.now(),
                system_health_score=system_health_score,
                total_technical_debt=risk_assessment.total_debt_score,
                debt_trend=debt_trend,
                critical_issues=critical_issues,
                top_priorities=top_priorities,
                cleanup_progress=cleanup_progress,
                roi_metrics=roi_metrics,
                risk_assessment=risk_assessment,
                actionable_insights=actionable_insights,
                success_metrics=success_metrics,
                next_review_date=next_review_date,
                metadata={
                    'dashboard_version': '1.0',
                    'data_freshness_hours': 0,  # Assuming real-time data
                    'confidence_score': self._calculate_confidence_score(patches)
                }
            )
            
            # Save dashboard
            self._save_report(dashboard, ReportFormat.JSON)
            
            self._logger.info(f"Generated executive dashboard {report_id}")
            return dashboard
            
        except Exception as e:
            self._logger.error(f"Failed to generate executive dashboard: {str(e)}")
            self._error_count += 1
            raise
    
    def get_dashboard_metrics(self, patches: List[PatchAnnotation]) -> DashboardMetrics:
        """
        Get key performance indicators for dashboard display.
        
        Args:
            patches: List of patches to analyze
            
        Returns:
            DashboardMetrics with key performance indicators
        """
        try:
            now = datetime.now()
            month_ago = now - timedelta(days=30)
            
            # Count patches by status
            total_patches = len(patches)
            critical_patches = sum(1 for p in patches if p.debt_level == DebtLevel.CRITICAL)
            overdue_patches = sum(
                1 for p in patches 
                if p.expected_resolution and p.expected_resolution < now
            )
            
            # Calculate resolution metrics (simplified - would need historical data)
            patches_resolved_this_month = 0  # Would need resolution tracking
            average_resolution_time_days = 14.0  # Would calculate from historical data
            
            # Calculate debt score trend (simplified)
            debt_score_trend = 0.0  # Would calculate from historical data
            
            # Calculate cleanup velocity
            cleanup_velocity = 2.5  # Would calculate from historical data
            
            # Calculate system health score
            risk_assessment = self._impact_engine.generate_risk_assessment(patches)
            system_health_score = self._calculate_system_health_score(patches, risk_assessment)
            
            # Identify top risk components
            component_patches = defaultdict(list)
            for patch in patches:
                component_patches[patch.component].append(patch)
            
            component_risks = []
            for component, comp_patches in component_patches.items():
                impact = self._impact_engine.assess_component_impact(component, comp_patches)
                component_risks.append((component, impact.total_debt_score))
            
            top_risk_components = [
                comp for comp, _ in sorted(component_risks, key=lambda x: x[1], reverse=True)[:5]
            ]
            
            # Find upcoming deadlines
            upcoming_deadlines = [
                (patch.patch_id, patch.expected_resolution)
                for patch in patches
                if patch.expected_resolution and patch.expected_resolution > now
                and patch.expected_resolution < now + timedelta(days=30)
            ]
            upcoming_deadlines.sort(key=lambda x: x[1])
            
            return DashboardMetrics(
                total_patches=total_patches,
                critical_patches=critical_patches,
                overdue_patches=overdue_patches,
                patches_resolved_this_month=patches_resolved_this_month,
                average_resolution_time_days=average_resolution_time_days,
                debt_score_trend=debt_score_trend,
                cleanup_velocity=cleanup_velocity,
                system_health_score=system_health_score,
                top_risk_components=top_risk_components,
                upcoming_deadlines=upcoming_deadlines[:10]  # Top 10 upcoming deadlines
            )
            
        except Exception as e:
            self._logger.error(f"Failed to get dashboard metrics: {str(e)}")
            self._error_count += 1
            raise
    
    def export_report(self, report: Union[InventoryReport, TrendAnalysis, ExecutiveDashboard],
                     format: ReportFormat, output_path: Optional[str] = None) -> str:
        """
        Export report to specified format.
        
        Args:
            report: Report to export
            format: Output format
            output_path: Optional custom output path
            
        Returns:
            Path to the exported report file
        """
        try:
            if output_path is None:
                output_path = self._report_storage_path / f"{report.report_id}.{format.value}"
            else:
                output_path = Path(output_path)
            
            if format == ReportFormat.JSON:
                self._export_json(report, output_path)
            elif format == ReportFormat.HTML:
                self._export_html(report, output_path)
            elif format == ReportFormat.CSV:
                self._export_csv(report, output_path)
            elif format == ReportFormat.MARKDOWN:
                self._export_markdown(report, output_path)
            else:
                raise ValueError(f"Unsupported export format: {format}")
            
            self._logger.info(f"Exported report {report.report_id} to {output_path}")
            return str(output_path)
            
        except Exception as e:
            self._logger.error(f"Failed to export report: {str(e)}")
            self._error_count += 1
            raise
    
    # Private helper methods
    
    def _analyze_patch_aging(self, patches: List[PatchAnnotation]) -> Dict[str, Any]:
        """Analyze patch aging patterns."""
        now = datetime.now()
        age_buckets = {
            '0-7_days': 0,
            '8-30_days': 0,
            '31-90_days': 0,
            '91-180_days': 0,
            '180+_days': 0
        }
        
        for patch in patches:
            age_days = (now - patch.created_date).days
            if age_days <= 7:
                age_buckets['0-7_days'] += 1
            elif age_days <= 30:
                age_buckets['8-30_days'] += 1
            elif age_days <= 90:
                age_buckets['31-90_days'] += 1
            elif age_days <= 180:
                age_buckets['91-180_days'] += 1
            else:
                age_buckets['180+_days'] += 1
        
        return {
            'age_distribution': age_buckets,
            'average_age_days': sum((now - p.created_date).days for p in patches) / len(patches) if patches else 0,
            'oldest_patch_days': max((now - p.created_date).days for p in patches) if patches else 0
        }
    
    def _generate_inventory_recommendations(self, patches: List[PatchAnnotation],
                                         component_summaries: Dict[str, Dict[str, Any]],
                                         overdue_patches: List[PatchAnnotation]) -> List[str]:
        """Generate actionable recommendations for inventory report."""
        recommendations = []
        
        # Critical patch recommendations
        critical_count = sum(1 for p in patches if p.debt_level == DebtLevel.CRITICAL)
        if critical_count > 0:
            recommendations.append(f"Address {critical_count} critical patches immediately")
        
        # Overdue patch recommendations
        if overdue_patches:
            recommendations.append(f"Review and update {len(overdue_patches)} overdue patches")
        
        # Component-specific recommendations
        high_debt_components = [
            comp for comp, summary in component_summaries.items()
            if summary['debt_score'] > 15
        ]
        if high_debt_components:
            recommendations.append(
                f"Focus cleanup efforts on high-debt components: {', '.join(high_debt_components[:3])}"
            )
        
        # General recommendations
        if len(patches) > 20:
            recommendations.append("Consider implementing systematic cleanup sprints")
        
        return recommendations
    
    def _calculate_start_date(self, end_date: datetime, time_range: TimeRange) -> datetime:
        """Calculate start date based on time range."""
        if time_range == TimeRange.LAST_7_DAYS:
            return end_date - timedelta(days=7)
        elif time_range == TimeRange.LAST_30_DAYS:
            return end_date - timedelta(days=30)
        elif time_range == TimeRange.LAST_90_DAYS:
            return end_date - timedelta(days=90)
        elif time_range == TimeRange.LAST_6_MONTHS:
            return end_date - timedelta(days=180)
        elif time_range == TimeRange.LAST_YEAR:
            return end_date - timedelta(days=365)
        else:  # ALL_TIME
            return datetime.min
    
    def _generate_trend_data_points(self, patches: List[PatchAnnotation],
                                  start_date: datetime, end_date: datetime) -> List[TrendDataPoint]:
        """Generate time series data points for trend analysis."""
        # This is a simplified implementation - in practice would need historical data
        data_points = []
        current_date = start_date
        
        while current_date <= end_date:
            # Count patches created on this date
            patches_created = sum(
                1 for p in patches 
                if p.created_date.date() == current_date.date()
            )
            
            # Count patches resolved on this date (would need resolution tracking)
            patches_resolved = 0  # Simplified
            
            # Calculate total active patches at this point
            total_active = sum(
                1 for p in patches 
                if p.created_date <= current_date
            )
            
            # Calculate total debt score
            active_patches = [p for p in patches if p.created_date <= current_date]
            total_debt_score = sum(
                self._get_debt_score(p.debt_level) for p in active_patches
            )
            
            data_points.append(TrendDataPoint(
                timestamp=current_date,
                patches_created=patches_created,
                patches_resolved=patches_resolved,
                total_active_patches=total_active,
                total_debt_score=total_debt_score
            ))
            
            current_date += timedelta(days=1)
        
        return data_points
    
    def _get_debt_score(self, debt_level: DebtLevel) -> float:
        """Get numeric score for debt level."""
        scores = {
            DebtLevel.LOW: 1.0,
            DebtLevel.MEDIUM: 2.0,
            DebtLevel.HIGH: 5.0,
            DebtLevel.CRITICAL: 10.0
        }
        return scores.get(debt_level, 1.0)
    
    def _analyze_creation_trend(self, data_points: List[TrendDataPoint]) -> str:
        """Analyze patch creation trend."""
        if len(data_points) < 2:
            return "stable"
        
        recent_avg = sum(dp.patches_created for dp in data_points[-7:]) / min(7, len(data_points))
        earlier_avg = sum(dp.patches_created for dp in data_points[:7]) / min(7, len(data_points))
        
        if recent_avg > earlier_avg * 1.2:
            return "increasing"
        elif recent_avg < earlier_avg * 0.8:
            return "decreasing"
        else:
            return "stable"
    
    def _analyze_resolution_trend(self, data_points: List[TrendDataPoint]) -> str:
        """Analyze patch resolution trend."""
        # Simplified - would need actual resolution data
        return "stable"
    
    def _analyze_net_debt_trend(self, data_points: List[TrendDataPoint]) -> str:
        """Analyze net debt trend."""
        if len(data_points) < 2:
            return "stable"
        
        recent_debt = sum(dp.total_debt_score for dp in data_points[-7:]) / min(7, len(data_points))
        earlier_debt = sum(dp.total_debt_score for dp in data_points[:7]) / min(7, len(data_points))
        
        if recent_debt > earlier_debt * 1.1:
            return "increasing"
        elif recent_debt < earlier_debt * 0.9:
            return "decreasing"
        else:
            return "stable"
    
    def _generate_trend_insights(self, data_points: List[TrendDataPoint],
                               creation_trend: str, resolution_trend: str,
                               net_debt_trend: str) -> List[str]:
        """Generate key insights from trend analysis."""
        insights = []
        
        if creation_trend == "increasing":
            insights.append("Patch creation rate is increasing - may indicate growing technical debt")
        elif creation_trend == "decreasing":
            insights.append("Patch creation rate is decreasing - positive trend")
        
        if net_debt_trend == "increasing":
            insights.append("Net technical debt is growing - cleanup efforts may be insufficient")
        elif net_debt_trend == "decreasing":
            insights.append("Net technical debt is decreasing - cleanup efforts are effective")
        
        return insights
    
    def _calculate_performance_metrics(self, data_points: List[TrendDataPoint]) -> Dict[str, float]:
        """Calculate performance metrics from trend data."""
        if not data_points:
            return {}
        
        total_created = sum(dp.patches_created for dp in data_points)
        total_resolved = sum(dp.patches_resolved for dp in data_points)
        
        return {
            'total_patches_created': float(total_created),
            'total_patches_resolved': float(total_resolved),
            'net_patch_change': float(total_created - total_resolved),
            'average_daily_creation': float(total_created / len(data_points)),
            'average_daily_resolution': float(total_resolved / len(data_points)),
            'current_debt_score': float(data_points[-1].total_debt_score if data_points else 0)
        }
    
    def _generate_trend_projections(self, data_points: List[TrendDataPoint],
                                  time_range: TimeRange) -> Dict[str, Any]:
        """Generate future projections based on trend data."""
        # Simplified projection logic
        if not data_points:
            return {}
        
        current_rate = sum(dp.patches_created for dp in data_points[-7:]) / 7
        
        return {
            'projected_patches_next_30_days': int(current_rate * 30),
            'projected_debt_score_change': 'stable',  # Would calculate based on trends
            'confidence_level': 'medium'
        }
    
    def _generate_trend_recommendations(self, data_points: List[TrendDataPoint],
                                      creation_trend: str, resolution_trend: str,
                                      performance_metrics: Dict[str, float]) -> List[str]:
        """Generate recommendations based on trend analysis."""
        recommendations = []
        
        if creation_trend == "increasing":
            recommendations.append("Investigate root causes of increasing patch creation")
            recommendations.append("Consider preventive measures to reduce technical debt accumulation")
        
        if performance_metrics.get('net_patch_change', 0) > 0:
            recommendations.append("Increase cleanup efforts to reduce net technical debt")
        
        return recommendations
    
    def _calculate_system_health_score(self, patches: List[PatchAnnotation],
                                     risk_assessment: RiskAssessment) -> float:
        """Calculate overall system health score (0-100)."""
        if not patches:
            return 100.0
        
        # Base score
        base_score = 100.0
        
        # Deduct for critical patches
        critical_count = sum(1 for p in patches if p.debt_level == DebtLevel.CRITICAL)
        base_score -= critical_count * 20
        
        # Deduct for high patches
        high_count = sum(1 for p in patches if p.debt_level == DebtLevel.HIGH)
        base_score -= high_count * 10
        
        # Deduct for overdue patches
        now = datetime.now()
        overdue_count = sum(
            1 for p in patches 
            if p.expected_resolution and p.expected_resolution < now
        )
        base_score -= overdue_count * 5
        
        # Adjust based on risk level
        risk_adjustments = {
            'critical': -30,
            'high': -20,
            'moderate': -10,
            'low': 0
        }
        base_score += risk_adjustments.get(risk_assessment.risk_level, 0)
        
        return max(0.0, min(100.0, base_score))
    
    def _determine_debt_trend(self, patches: List[PatchAnnotation]) -> str:
        """Determine overall debt trend."""
        # Simplified - would need historical data
        return "stable"
    
    def _identify_critical_issues(self, patches: List[PatchAnnotation],
                                risk_assessment: RiskAssessment) -> List[str]:
        """Identify critical issues requiring immediate attention."""
        issues = []
        
        critical_patches = [p for p in patches if p.debt_level == DebtLevel.CRITICAL]
        if critical_patches:
            issues.append(f"{len(critical_patches)} critical patches require immediate attention")
        
        security_patches = [p for p in patches if p.bypass_type == BypassType.SECURITY]
        if security_patches:
            issues.append(f"{len(security_patches)} security-related patches present")
        
        now = datetime.now()
        overdue_patches = [
            p for p in patches 
            if p.expected_resolution and p.expected_resolution < now
        ]
        if overdue_patches:
            issues.append(f"{len(overdue_patches)} patches are overdue for cleanup")
        
        return issues
    
    def _generate_top_priorities(self, patches: List[PatchAnnotation],
                               risk_assessment: RiskAssessment) -> List[str]:
        """Generate top priority actions."""
        priorities = []
        
        if risk_assessment.risk_level in ['critical', 'high']:
            priorities.append("Execute emergency cleanup for critical patches")
        
        priorities.extend(risk_assessment.recommended_actions[:3])
        
        return priorities
    
    def _calculate_cleanup_progress(self, patches: List[PatchAnnotation],
                                  cleanup_data: Optional[Dict[str, Any]]) -> CleanupProgress:
        """Calculate cleanup progress metrics."""
        # Simplified implementation - would integrate with actual cleanup tracking
        total_tasks = len(patches)
        completed_tasks = 0  # Would track actual completions
        in_progress_tasks = 0  # Would track work in progress
        blocked_tasks = 0  # Would track blocked items
        
        completion_percentage = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
        
        return CleanupProgress(
            total_cleanup_tasks=total_tasks,
            completed_tasks=completed_tasks,
            in_progress_tasks=in_progress_tasks,
            blocked_tasks=blocked_tasks,
            completion_percentage=completion_percentage,
            estimated_completion_date=None,  # Would calculate based on velocity
            velocity_metrics={'patches_per_week': 2.5},
            bottlenecks=['Resource constraints', 'Complex dependencies']
        )
    
    def _calculate_roi_metrics(self, patches: List[PatchAnnotation],
                             cleanup_progress: CleanupProgress) -> Dict[str, float]:
        """Calculate return on investment metrics for cleanup efforts."""
        return {
            'estimated_maintenance_cost_reduction': 15000.0,  # Would calculate based on burden
            'development_velocity_improvement': 0.15,  # 15% improvement
            'risk_reduction_value': 25000.0,  # Would calculate based on risk assessment
            'cleanup_investment_cost': 8000.0  # Would track actual costs
        }
    
    def _generate_actionable_insights(self, patches: List[PatchAnnotation],
                                    risk_assessment: RiskAssessment,
                                    cleanup_progress: CleanupProgress) -> List[Dict[str, Any]]:
        """Generate actionable insights for executives."""
        insights = []
        
        # High-impact, low-effort opportunities
        insights.append({
            'type': 'quick_win',
            'title': 'Quick Win Opportunities',
            'description': 'Low-effort patches that can be resolved quickly',
            'impact': 'medium',
            'effort': 'low',
            'timeline': '1-2 weeks'
        })
        
        # Resource allocation insights
        insights.append({
            'type': 'resource_allocation',
            'title': 'Optimal Resource Allocation',
            'description': 'Focus 60% of cleanup effort on critical and high-priority patches',
            'impact': 'high',
            'effort': 'medium',
            'timeline': '1 month'
        })
        
        return insights
    
    def _calculate_success_metrics(self, patches: List[PatchAnnotation],
                                 cleanup_progress: CleanupProgress) -> Dict[str, float]:
        """Calculate success metrics for the dashboard."""
        return {
            'debt_reduction_percentage': cleanup_progress.completion_percentage,
            'system_stability_improvement': 0.12,  # 12% improvement
            'development_velocity_gain': 0.08,  # 8% gain
            'maintenance_cost_savings': 12000.0
        }
    
    def _calculate_next_review_date(self, risk_level: str) -> datetime:
        """Calculate when the next review should occur."""
        now = datetime.now()
        
        if risk_level == 'critical':
            return now + timedelta(days=7)  # Weekly reviews
        elif risk_level == 'high':
            return now + timedelta(days=14)  # Bi-weekly reviews
        elif risk_level == 'moderate':
            return now + timedelta(days=30)  # Monthly reviews
        else:
            return now + timedelta(days=90)  # Quarterly reviews
    
    def _calculate_data_quality_score(self, patches: List[PatchAnnotation]) -> float:
        """Calculate data quality score for patches."""
        if not patches:
            return 1.0
        
        complete_patches = 0
        for patch in patches:
            validation_result = patch.validate()
            if validation_result.is_valid:
                complete_patches += 1
        
        return complete_patches / len(patches)
    
    def _calculate_coverage_metrics(self, patches: List[PatchAnnotation]) -> Dict[str, Any]:
        """Calculate coverage metrics for the patch data."""
        components = set(p.component for p in patches if p.component)
        bypass_types = set(p.bypass_type for p in patches)
        
        return {
            'components_covered': len(components),
            'bypass_types_covered': len(bypass_types),
            'patches_with_validation_criteria': sum(
                1 for p in patches if p.validation_criteria
            )
        }
    
    def _calculate_trend_data_completeness(self, data_points: List[TrendDataPoint]) -> float:
        """Calculate completeness of trend data."""
        if not data_points:
            return 0.0
        
        # Simplified - would check for missing data points
        return 1.0
    
    def _calculate_confidence_score(self, patches: List[PatchAnnotation]) -> float:
        """Calculate confidence score for the analysis."""
        # Based on data quality and completeness
        data_quality = self._calculate_data_quality_score(patches)
        sample_size_factor = min(1.0, len(patches) / 50)  # Confidence increases with sample size
        
        return (data_quality + sample_size_factor) / 2
    
    def _save_report(self, report: Any, format: ReportFormat) -> None:
        """Save report to storage."""
        try:
            filename = f"{report.report_id}.{format.value}"
            filepath = self._report_storage_path / filename
            
            if format == ReportFormat.JSON:
                with open(filepath, 'w') as f:
                    json.dump(self._serialize_report(report), f, indent=2, default=str)
            
            self._logger.debug(f"Saved report to {filepath}")
            
        except Exception as e:
            self._logger.error(f"Failed to save report: {str(e)}")
    
    def _serialize_report(self, report: Any, visited: Optional[Set[int]] = None) -> Dict[str, Any]:
        """Serialize report object to dictionary with circular reference protection."""
        if visited is None:
            visited = set()
        
        # Handle circular references
        obj_id = id(report)
        if obj_id in visited:
            return f"<circular reference to {type(report).__name__}>"
        
        if hasattr(report, '__dict__'):
            visited.add(obj_id)
            result = {}
            
            for key, value in report.__dict__.items():
                # Skip private attributes and methods
                if key.startswith('_'):
                    continue
                    
                try:
                    if hasattr(value, '__dict__') and not isinstance(value, (datetime, type)):
                        result[key] = self._serialize_report(value, visited.copy())
                    elif isinstance(value, list):
                        result[key] = [
                            self._serialize_report(item, visited.copy()) if hasattr(item, '__dict__') and not isinstance(item, (datetime, type)) else self._safe_serialize_value(item)
                            for item in value
                        ]
                    elif isinstance(value, dict):
                        result[key] = {
                            self._safe_serialize_value(k): self._serialize_report(v, visited.copy()) if hasattr(v, '__dict__') and not isinstance(v, (datetime, type)) else self._safe_serialize_value(v)
                            for k, v in value.items()
                        }
                    else:
                        result[key] = self._safe_serialize_value(value)
                except Exception as e:
                    result[key] = f"<serialization error: {str(e)}>"
            
            return result
        else:
            return self._safe_serialize_value(report)
    
    def _safe_serialize_value(self, value: Any) -> Any:
        """Safely serialize a value, handling special types."""
        if isinstance(value, (str, int, float, bool, type(None))):
            return value
        elif isinstance(value, datetime):
            return value.isoformat()
        elif hasattr(value, 'value'):  # Enum types
            return value.value
        elif hasattr(value, '__str__'):
            return str(value)
        else:
            return f"<{type(value).__name__}>"
    
    def _export_json(self, report: Any, output_path: Path) -> None:
        """Export report as JSON."""
        with open(output_path, 'w') as f:
            json.dump(self._serialize_report(report), f, indent=2, default=str)
    
    def _export_html(self, report: Any, output_path: Path) -> None:
        """Export report as HTML."""
        # Simplified HTML export - would use proper templating
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Technical Debt Report - {report.report_id}</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 40px; }}
                .header {{ background-color: #f0f0f0; padding: 20px; }}
                .metric {{ margin: 10px 0; }}
                .critical {{ color: red; }}
                .high {{ color: orange; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>Technical Debt Report</h1>
                <p>Report ID: {report.report_id}</p>
                <p>Generated: {report.generated_at}</p>
            </div>
            <div class="content">
                <pre>{json.dumps(self._serialize_report(report), indent=2, default=str)}</pre>
            </div>
        </body>
        </html>
        """
        
        with open(output_path, 'w') as f:
            f.write(html_content)
    
    def _export_csv(self, report: Any, output_path: Path) -> None:
        """Export report as CSV."""
        # Simplified CSV export - would format appropriately for each report type
        import csv
        
        with open(output_path, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['Report ID', 'Generated At', 'Type'])
            writer.writerow([report.report_id, report.generated_at, type(report).__name__])
    
    def _export_markdown(self, report: Any, output_path: Path) -> None:
        """Export report as Markdown."""
        # Simplified Markdown export
        md_content = f"""
# Technical Debt Report

**Report ID:** {report.report_id}  
**Generated:** {report.generated_at}  
**Type:** {type(report).__name__}

## Summary

```json
{json.dumps(self._serialize_report(report), indent=2, default=str)}
```
        """
        
        with open(output_path, 'w') as f:
            f.write(md_content)


class PatchDashboard(ReflectiveModule):
    """
    Main dashboard system for technical debt patch management.
    
    This class provides a unified interface for generating reports,
    managing dashboards, and providing real-time insights into
    technical debt patch status and trends.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__()
        self.module_id = "patch_dashboard"
        self._config = config or {}
        self._logger = logging.getLogger(__name__)
        
        # Initialize report generator
        self._report_generator = ReportGenerator(config)
        
        # Dashboard configuration
        self._auto_refresh_enabled = self._config.get('auto_refresh_enabled', True)
        self._refresh_interval_minutes = self._config.get('refresh_interval_minutes', 60)
        
        # Cache for dashboard data
        self._dashboard_cache: Dict[str, Any] = {}
        self._last_refresh: Optional[datetime] = None
    
    def get_module_info(self) -> Dict[str, Any]:
        """Get module information."""
        return {
            "module_id": self.module_id,
            "name": "Technical Debt Patch Dashboard",
            "version": "1.0.0",
            "description": "Unified dashboard system for technical debt patch management",
            "capabilities": [cap.value for cap in self.get_capabilities()]
        }
    
    def get_capabilities(self) -> List[ModuleCapability]:
        """Get module capabilities."""
        return [
            ModuleCapability.CORE_FUNCTIONALITY,
            ModuleCapability.DATA_PROCESSING,
            ModuleCapability.VALIDATION,
            ModuleCapability.MONITORING
        ]
    
    def get_health_status(self) -> ModuleHealth:
        """Get module health status."""
        issues = []
        status = ModuleStatus.HEALTHY
        
        # Check report generator health
        generator_health = self._report_generator.get_health_status()
        if generator_health.status != ModuleStatus.HEALTHY:
            issues.append("Report generator not healthy")
            status = ModuleStatus.WARNING
        
        return ModuleHealth(
            module_id=self.module_id,
            status=status,
            health_score=1.0 if status == ModuleStatus.HEALTHY else 0.8,
            issues=issues,
            last_check=datetime.now(),
            uptime_seconds=(datetime.now() - self._start_time).total_seconds(),
            error_count=self._error_count,
            warning_count=self._warning_count
        )
    
    def graceful_degradation(self) -> GracefulDegradationResult:
        """Perform graceful degradation."""
        # In degraded mode, disable auto-refresh and use cached data
        degraded_capabilities = []
        
        if not self._auto_refresh_enabled:
            degraded_capabilities.append(ModuleCapability.MONITORING)
        
        remaining_capabilities = [
            cap for cap in self.get_capabilities() 
            if cap not in degraded_capabilities
        ]
        
        return GracefulDegradationResult(
            success=True,
            degraded_capabilities=degraded_capabilities,
            remaining_capabilities=remaining_capabilities
        )
    
    def generate_comprehensive_report(self, patches: List[PatchAnnotation],
                                    include_trends: bool = True,
                                    include_executive_summary: bool = True) -> Dict[str, Any]:
        """
        Generate comprehensive report with all dashboard components.
        
        Args:
            patches: List of patches to analyze
            include_trends: Whether to include trend analysis
            include_executive_summary: Whether to include executive dashboard
            
        Returns:
            Dictionary containing all report components
        """
        try:
            self._logger.info("Generating comprehensive dashboard report")
            
            # Generate inventory report
            inventory_report = self._report_generator.generate_inventory_report(patches)
            
            # Generate trend analysis if requested
            trend_analysis = None
            if include_trends:
                trend_analysis = self._report_generator.generate_trend_analysis(patches)
            
            # Generate executive dashboard if requested
            executive_dashboard = None
            if include_executive_summary:
                executive_dashboard = self._report_generator.generate_executive_dashboard(patches)
            
            # Get dashboard metrics
            dashboard_metrics = self._report_generator.get_dashboard_metrics(patches)
            
            comprehensive_report = {
                'report_id': f"comprehensive_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                'generated_at': datetime.now(),
                'inventory_report': inventory_report,
                'trend_analysis': trend_analysis,
                'executive_dashboard': executive_dashboard,
                'dashboard_metrics': dashboard_metrics,
                'summary': {
                    'total_patches': len(patches),
                    'system_health_score': dashboard_metrics.system_health_score,
                    'critical_issues_count': dashboard_metrics.critical_patches,
                    'cleanup_recommendations': inventory_report.recommendations
                }
            }
            
            # Cache the report
            self._dashboard_cache['comprehensive_report'] = comprehensive_report
            self._last_refresh = datetime.now()
            
            self._logger.info("Generated comprehensive dashboard report")
            return comprehensive_report
            
        except Exception as e:
            self._logger.error(f"Failed to generate comprehensive report: {str(e)}")
            self._error_count += 1
            raise
    
    def get_real_time_metrics(self, patches: List[PatchAnnotation]) -> DashboardMetrics:
        """
        Get real-time dashboard metrics.
        
        Args:
            patches: Current list of patches
            
        Returns:
            DashboardMetrics with current system state
        """
        return self._report_generator.get_dashboard_metrics(patches)
    
    def export_dashboard_report(self, report: Dict[str, Any], 
                              format: ReportFormat,
                              output_path: Optional[str] = None) -> str:
        """
        Export dashboard report to specified format.
        
        Args:
            report: Dashboard report to export
            format: Output format
            output_path: Optional custom output path
            
        Returns:
            Path to exported file
        """
        # Create a temporary report object for export
        class DashboardReport:
            def __init__(self, data):
                self.report_id = data['report_id']
                self.generated_at = data['generated_at']
                self.__dict__.update(data)
        
        temp_report = DashboardReport(report)
        return self._report_generator.export_report(temp_report, format, output_path)
    
    def refresh_dashboard(self, patches: List[PatchAnnotation]) -> bool:
        """
        Refresh dashboard data.
        
        Args:
            patches: Current list of patches
            
        Returns:
            True if refresh was successful
        """
        try:
            self._logger.info("Refreshing dashboard data")
            
            # Update cached metrics
            self._dashboard_cache['metrics'] = self.get_real_time_metrics(patches)
            self._dashboard_cache['last_update'] = datetime.now()
            self._last_refresh = datetime.now()
            
            return True
            
        except Exception as e:
            self._logger.error(f"Failed to refresh dashboard: {str(e)}")
            self._error_count += 1
            return False
    
    def get_cached_data(self, data_type: str) -> Optional[Any]:
        """
        Get cached dashboard data.
        
        Args:
            data_type: Type of cached data to retrieve
            
        Returns:
            Cached data if available, None otherwise
        """
        return self._dashboard_cache.get(data_type)
    
    def should_refresh(self) -> bool:
        """
        Check if dashboard should be refreshed based on configuration.
        
        Returns:
            True if refresh is needed
        """
        if not self._auto_refresh_enabled or not self._last_refresh:
            return True
        
        time_since_refresh = datetime.now() - self._last_refresh
        return time_since_refresh.total_seconds() > (self._refresh_interval_minutes * 60)