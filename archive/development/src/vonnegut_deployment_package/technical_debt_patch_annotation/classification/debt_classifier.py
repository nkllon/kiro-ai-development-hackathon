"""
Technical Debt Classification and Impact Assessment System

This module implements comprehensive technical debt classification algorithms,
severity assessment, component-level debt aggregation, and automated alerting
for patch management and cleanup prioritization.

Requirements addressed: 2.1, 2.2, 2.3, 2.4, 2.5
"""

import logging
import os
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional, Set, Tuple, Any
from pathlib import Path

from src.rm_ddd.core.unified_reflective_module import (
    ReflectiveModule, 
    ModuleHealth, 
    ModuleStatus, 
    ModuleCapability,
    GracefulDegradationResult
)
from ..core.models import PatchAnnotation, DebtLevel, BypassType


class AlertSeverity(Enum):
    """Alert severity levels for debt threshold violations."""
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"
    EMERGENCY = "emergency"


class ComponentType(Enum):
    """Component types for impact assessment."""
    CORE_SYSTEM = "core_system"
    API_LAYER = "api_layer"
    DATA_LAYER = "data_layer"
    UI_COMPONENT = "ui_component"
    INTEGRATION = "integration"
    UTILITY = "utility"
    CONFIGURATION = "configuration"


@dataclass
class ComponentImpact:
    """Assessment of technical debt impact on a specific component."""
    component_name: str
    patch_count: int
    total_debt_score: float
    average_debt_level: float
    critical_patches: int
    high_patches: int
    medium_patches: int
    low_patches: int
    component_type: ComponentType
    maintenance_burden_score: float
    risk_factors: List[str] = field(default_factory=list)
    recommended_actions: List[str] = field(default_factory=list)
    last_assessment: datetime = field(default_factory=datetime.now)


@dataclass
class DebtHotspot:
    """Identification of high-debt areas requiring immediate attention."""
    component_name: str
    hotspot_type: str  # "high_concentration", "critical_patches", "aging_debt"
    severity_score: float
    patch_count: int
    description: str
    recommended_priority: str  # "immediate", "high", "medium", "low"
    estimated_cleanup_effort: str  # "hours", "days", "weeks"
    business_impact: str
    technical_risk: str


@dataclass
class MaintenanceBurden:
    """Assessment of ongoing maintenance cost for patches."""
    patch_id: str
    daily_maintenance_cost: float  # Relative cost units
    complexity_factor: float
    integration_dependencies: int
    testing_overhead: float
    documentation_debt: float
    total_burden_score: float
    burden_category: str  # "low", "moderate", "high", "severe"


@dataclass
class RiskAssessment:
    """Overall technical debt risk profile for the system."""
    total_patches: int
    total_debt_score: float
    risk_level: str  # "low", "moderate", "high", "critical"
    top_risk_factors: List[str]
    components_at_risk: List[str]
    recommended_actions: List[str]
    assessment_timestamp: datetime = field(default_factory=datetime.now)
    trend_direction: str = "stable"  # "improving", "stable", "degrading"
    projected_cleanup_timeline: str = ""


@dataclass
class DebtAlert:
    """Automated alert for debt threshold violations."""
    alert_id: str
    severity: AlertSeverity
    component: str
    threshold_type: str
    current_value: float
    threshold_value: float
    message: str
    recommended_actions: List[str]
    created_at: datetime = field(default_factory=datetime.now)
    acknowledged: bool = False


class ImpactAssessmentEngine(ReflectiveModule):
    """
    Engine for assessing technical debt impact and generating insights.
    
    This class provides comprehensive analysis of patch impact on system
    components, maintenance burden calculation, and risk assessment.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__()
        self.module_id = "impact_assessment_engine"
        self._config = config or {}
        self._logger = logging.getLogger(__name__)
        
        # Component type mapping patterns
        self._component_patterns = {
            ComponentType.CORE_SYSTEM: ["core", "engine", "kernel", "system"],
            ComponentType.API_LAYER: ["api", "endpoint", "controller", "handler"],
            ComponentType.DATA_LAYER: ["data", "database", "repository", "model"],
            ComponentType.UI_COMPONENT: ["ui", "view", "component", "frontend"],
            ComponentType.INTEGRATION: ["integration", "client", "adapter", "connector"],
            ComponentType.UTILITY: ["util", "helper", "tool", "common"],
            ComponentType.CONFIGURATION: ["config", "settings", "env", "properties"]
        }
        
        # Debt scoring weights
        self._debt_weights = {
            DebtLevel.CRITICAL: 10.0,
            DebtLevel.HIGH: 5.0,
            DebtLevel.MEDIUM: 2.0,
            DebtLevel.LOW: 1.0
        }
        
        # Bypass type risk multipliers
        self._bypass_risk_multipliers = {
            BypassType.SECURITY: 2.0,
            BypassType.ARCHITECTURE: 1.5,
            BypassType.COMPLIANCE: 1.8,
            BypassType.PERFORMANCE: 1.2,
            BypassType.INTEGRATION: 1.3
        }
    
    def get_module_info(self) -> Dict[str, Any]:
        """Get module information."""
        return {
            "module_id": self.module_id,
            "name": "Impact Assessment Engine",
            "version": "1.0.0",
            "description": "Technical debt impact assessment and classification",
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
        return ModuleHealth(
            module_id=self.module_id,
            status=ModuleStatus.HEALTHY,
            health_score=1.0,
            issues=[],
            last_check=datetime.now(),
            uptime_seconds=(datetime.now() - self._start_time).total_seconds(),
            error_count=self._error_count,
            warning_count=self._warning_count
        )
    
    def graceful_degradation(self) -> GracefulDegradationResult:
        """Perform graceful degradation."""
        return GracefulDegradationResult(
            success=True,
            degraded_capabilities=[],
            remaining_capabilities=self.get_capabilities()
        )
    
    def assess_component_impact(self, component: str, patches: List[PatchAnnotation]) -> ComponentImpact:
        """
        Assess cumulative impact on a specific component.
        
        Args:
            component: Component name to assess
            patches: List of patches affecting the component
            
        Returns:
            ComponentImpact with detailed assessment
        """
        if not patches:
            return ComponentImpact(
                component_name=component,
                patch_count=0,
                total_debt_score=0.0,
                average_debt_level=0.0,
                critical_patches=0,
                high_patches=0,
                medium_patches=0,
                low_patches=0,
                component_type=self._classify_component_type(component),
                maintenance_burden_score=0.0
            )
        
        # Count patches by severity
        debt_counts = {level: 0 for level in DebtLevel}
        for patch in patches:
            debt_counts[patch.debt_level] += 1
        
        # Calculate debt score
        total_debt_score = sum(
            debt_counts[level] * self._debt_weights[level] 
            for level in DebtLevel
        )
        
        # Apply bypass type risk multipliers
        bypass_multiplier = 1.0
        for patch in patches:
            bypass_multiplier = max(
                bypass_multiplier, 
                self._bypass_risk_multipliers.get(patch.bypass_type, 1.0)
            )
        
        total_debt_score *= bypass_multiplier
        
        # Calculate average debt level
        total_weighted_debt = sum(
            debt_counts[level] * self._debt_weights[level] 
            for level in DebtLevel
        )
        average_debt_level = total_weighted_debt / len(patches) if patches else 0.0
        
        # Calculate maintenance burden
        maintenance_burden = self._calculate_maintenance_burden_score(patches)
        
        # Generate risk factors and recommendations
        risk_factors = self._identify_risk_factors(component, patches, debt_counts)
        recommendations = self._generate_component_recommendations(
            component, patches, debt_counts, total_debt_score
        )
        
        return ComponentImpact(
            component_name=component,
            patch_count=len(patches),
            total_debt_score=total_debt_score,
            average_debt_level=average_debt_level,
            critical_patches=debt_counts[DebtLevel.CRITICAL],
            high_patches=debt_counts[DebtLevel.HIGH],
            medium_patches=debt_counts[DebtLevel.MEDIUM],
            low_patches=debt_counts[DebtLevel.LOW],
            component_type=self._classify_component_type(component),
            maintenance_burden_score=maintenance_burden,
            risk_factors=risk_factors,
            recommended_actions=recommendations
        )
    
    def calculate_maintenance_burden(self, patch: PatchAnnotation) -> MaintenanceBurden:
        """
        Calculate ongoing maintenance cost for a specific patch.
        
        Args:
            patch: Patch annotation to assess
            
        Returns:
            MaintenanceBurden with detailed cost analysis
        """
        # Base complexity from debt level
        complexity_factor = self._debt_weights[patch.debt_level] / 10.0
        
        # Adjust for bypass type
        bypass_multiplier = self._bypass_risk_multipliers.get(patch.bypass_type, 1.0)
        complexity_factor *= bypass_multiplier
        
        # Estimate integration dependencies (simplified heuristic)
        integration_deps = 1
        if patch.bypass_type == BypassType.INTEGRATION:
            integration_deps = 3
        elif patch.bypass_type == BypassType.ARCHITECTURE:
            integration_deps = 2
        
        # Testing overhead based on component type and debt level
        component_type = self._classify_component_type(patch.component)
        testing_overhead = 1.0
        if component_type == ComponentType.CORE_SYSTEM:
            testing_overhead = 2.0
        elif component_type == ComponentType.API_LAYER:
            testing_overhead = 1.5
        
        # Documentation debt (higher for critical patches)
        doc_debt = 0.5
        if patch.debt_level in [DebtLevel.CRITICAL, DebtLevel.HIGH]:
            doc_debt = 1.0
        
        # Daily maintenance cost (relative units)
        daily_cost = complexity_factor * 0.1  # Base daily cost
        
        # Total burden score
        total_burden = (
            daily_cost * 30 +  # Monthly cost
            complexity_factor +
            integration_deps * 0.5 +
            testing_overhead +
            doc_debt
        )
        
        # Categorize burden
        if total_burden < 5:
            burden_category = "low"
        elif total_burden < 15:
            burden_category = "moderate"
        elif total_burden < 30:
            burden_category = "high"
        else:
            burden_category = "severe"
        
        return MaintenanceBurden(
            patch_id=patch.patch_id,
            daily_maintenance_cost=daily_cost,
            complexity_factor=complexity_factor,
            integration_dependencies=integration_deps,
            testing_overhead=testing_overhead,
            documentation_debt=doc_debt,
            total_burden_score=total_burden,
            burden_category=burden_category
        )
    
    def detect_debt_hotspots(self, patches: List[PatchAnnotation]) -> List[DebtHotspot]:
        """
        Identify components with excessive technical debt.
        
        Args:
            patches: List of all patches to analyze
            
        Returns:
            List of DebtHotspot instances for high-risk areas
        """
        hotspots = []
        
        # Group patches by component
        component_patches = defaultdict(list)
        for patch in patches:
            component_patches[patch.component].append(patch)
        
        for component, comp_patches in component_patches.items():
            impact = self.assess_component_impact(component, comp_patches)
            
            # High concentration hotspot
            if impact.patch_count >= 5:
                hotspots.append(DebtHotspot(
                    component_name=component,
                    hotspot_type="high_concentration",
                    severity_score=impact.total_debt_score,
                    patch_count=impact.patch_count,
                    description=f"Component has {impact.patch_count} patches with total debt score {impact.total_debt_score:.1f}",
                    recommended_priority="high" if impact.total_debt_score > 20 else "medium",
                    estimated_cleanup_effort="weeks" if impact.patch_count > 10 else "days",
                    business_impact="High maintenance overhead, reduced development velocity",
                    technical_risk="Increased complexity, potential for cascading failures"
                ))
            
            # Critical patches hotspot
            if impact.critical_patches >= 2:
                hotspots.append(DebtHotspot(
                    component_name=component,
                    hotspot_type="critical_patches",
                    severity_score=impact.critical_patches * 10.0,
                    patch_count=impact.critical_patches,
                    description=f"Component has {impact.critical_patches} critical patches requiring immediate attention",
                    recommended_priority="immediate",
                    estimated_cleanup_effort="days",
                    business_impact="High risk of system failures, security vulnerabilities",
                    technical_risk="System instability, potential data loss or security breaches"
                ))
            
            # Aging debt hotspot
            aging_patches = [
                p for p in comp_patches 
                if p.expected_resolution and p.expected_resolution < datetime.now()
            ]
            if len(aging_patches) >= 3:
                hotspots.append(DebtHotspot(
                    component_name=component,
                    hotspot_type="aging_debt",
                    severity_score=len(aging_patches) * 2.0,
                    patch_count=len(aging_patches),
                    description=f"Component has {len(aging_patches)} overdue patches",
                    recommended_priority="high",
                    estimated_cleanup_effort="weeks",
                    business_impact="Accumulating technical debt, reduced maintainability",
                    technical_risk="Increasing complexity, harder to modify and extend"
                ))
        
        # Sort by severity score
        hotspots.sort(key=lambda h: h.severity_score, reverse=True)
        return hotspots
    
    def generate_risk_assessment(self, patches: List[PatchAnnotation]) -> RiskAssessment:
        """
        Generate overall technical debt risk profile.
        
        Args:
            patches: List of all patches to analyze
            
        Returns:
            RiskAssessment with comprehensive risk analysis
        """
        if not patches:
            return RiskAssessment(
                total_patches=0,
                total_debt_score=0.0,
                risk_level="low",
                top_risk_factors=[],
                components_at_risk=[],
                recommended_actions=["No patches found - system appears clean"]
            )
        
        # Calculate total debt score
        total_debt_score = sum(
            self._debt_weights[patch.debt_level] * 
            self._bypass_risk_multipliers.get(patch.bypass_type, 1.0)
            for patch in patches
        )
        
        # Determine risk level
        avg_debt_per_patch = total_debt_score / len(patches)
        if avg_debt_per_patch >= 8.0 or any(p.debt_level == DebtLevel.CRITICAL for p in patches):
            risk_level = "critical"
        elif avg_debt_per_patch >= 5.0 or len(patches) > 20:
            risk_level = "high"
        elif avg_debt_per_patch >= 2.0 or len(patches) > 10:
            risk_level = "moderate"
        else:
            risk_level = "low"
        
        # Identify top risk factors
        risk_factors = []
        
        critical_count = sum(1 for p in patches if p.debt_level == DebtLevel.CRITICAL)
        if critical_count > 0:
            risk_factors.append(f"{critical_count} critical patches requiring immediate attention")
        
        security_patches = sum(1 for p in patches if p.bypass_type == BypassType.SECURITY)
        if security_patches > 0:
            risk_factors.append(f"{security_patches} security-related patches present")
        
        overdue_patches = sum(
            1 for p in patches 
            if p.expected_resolution and p.expected_resolution < datetime.now()
        )
        if overdue_patches > 0:
            risk_factors.append(f"{overdue_patches} patches are overdue for cleanup")
        
        # Identify components at risk
        component_patches = defaultdict(list)
        for patch in patches:
            component_patches[patch.component].append(patch)
        
        components_at_risk = []
        for component, comp_patches in component_patches.items():
            impact = self.assess_component_impact(component, comp_patches)
            if impact.total_debt_score > 15 or impact.critical_patches > 0:
                components_at_risk.append(component)
        
        # Generate recommendations
        recommendations = []
        if critical_count > 0:
            recommendations.append("Address critical patches immediately")
        if security_patches > 0:
            recommendations.append("Prioritize security-related patches")
        if overdue_patches > 0:
            recommendations.append("Create cleanup plan for overdue patches")
        if len(components_at_risk) > 0:
            recommendations.append(f"Focus cleanup efforts on high-risk components: {', '.join(components_at_risk[:3])}")
        
        # Estimate cleanup timeline
        if risk_level == "critical":
            timeline = "1-2 weeks for critical issues, 1-3 months for complete cleanup"
        elif risk_level == "high":
            timeline = "2-4 weeks for high priority, 2-6 months for complete cleanup"
        elif risk_level == "moderate":
            timeline = "1-2 months for systematic cleanup"
        else:
            timeline = "3-6 months for gradual improvement"
        
        return RiskAssessment(
            total_patches=len(patches),
            total_debt_score=total_debt_score,
            risk_level=risk_level,
            top_risk_factors=risk_factors,
            components_at_risk=components_at_risk,
            recommended_actions=recommendations,
            projected_cleanup_timeline=timeline
        )
    
    def _classify_component_type(self, component_name: str) -> ComponentType:
        """Classify component type based on name patterns."""
        component_lower = component_name.lower()
        
        for comp_type, patterns in self._component_patterns.items():
            if any(pattern in component_lower for pattern in patterns):
                return comp_type
        
        return ComponentType.UTILITY  # Default fallback
    
    def _calculate_maintenance_burden_score(self, patches: List[PatchAnnotation]) -> float:
        """Calculate overall maintenance burden score for a set of patches."""
        if not patches:
            return 0.0
        
        total_burden = 0.0
        for patch in patches:
            burden = self.calculate_maintenance_burden(patch)
            total_burden += burden.total_burden_score
        
        return total_burden / len(patches)  # Average burden per patch
    
    def _identify_risk_factors(self, component: str, patches: List[PatchAnnotation], 
                             debt_counts: Dict[DebtLevel, int]) -> List[str]:
        """Identify specific risk factors for a component."""
        risk_factors = []
        
        if debt_counts[DebtLevel.CRITICAL] > 0:
            risk_factors.append(f"{debt_counts[DebtLevel.CRITICAL]} critical patches")
        
        if debt_counts[DebtLevel.HIGH] > 2:
            risk_factors.append(f"{debt_counts[DebtLevel.HIGH]} high-priority patches")
        
        security_patches = sum(1 for p in patches if p.bypass_type == BypassType.SECURITY)
        if security_patches > 0:
            risk_factors.append(f"{security_patches} security-related bypasses")
        
        overdue_count = sum(
            1 for p in patches 
            if p.expected_resolution and p.expected_resolution < datetime.now()
        )
        if overdue_count > 0:
            risk_factors.append(f"{overdue_count} overdue patches")
        
        if len(patches) > 5:
            risk_factors.append("High patch concentration")
        
        return risk_factors
    
    def _generate_component_recommendations(self, component: str, patches: List[PatchAnnotation],
                                          debt_counts: Dict[DebtLevel, int], 
                                          total_debt_score: float) -> List[str]:
        """Generate specific recommendations for a component."""
        recommendations = []
        
        if debt_counts[DebtLevel.CRITICAL] > 0:
            recommendations.append("Address critical patches immediately")
        
        if total_debt_score > 20:
            recommendations.append("Schedule dedicated cleanup sprint")
        elif total_debt_score > 10:
            recommendations.append("Allocate cleanup time in next iteration")
        
        if len(patches) > 5:
            recommendations.append("Consider architectural refactoring")
        
        security_patches = sum(1 for p in patches if p.bypass_type == BypassType.SECURITY)
        if security_patches > 0:
            recommendations.append("Prioritize security patch resolution")
        
        overdue_count = sum(
            1 for p in patches 
            if p.expected_resolution and p.expected_resolution < datetime.now()
        )
        if overdue_count > 0:
            recommendations.append("Update patch timelines and assign owners")
        
        return recommendations


class DebtClassifier(ReflectiveModule):
    """
    Main technical debt classification system with automated alerting.
    
    This class provides comprehensive debt classification, severity assessment,
    and automated threshold-based alerting for patch management.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__()
        self.module_id = "debt_classifier"
        self._config = config or {}
        self._logger = logging.getLogger(__name__)
        
        # Initialize impact assessment engine
        self._impact_engine = ImpactAssessmentEngine(config)
        
        # Alert thresholds (configurable)
        self._alert_thresholds = self._config.get('alert_thresholds', {
            'component_debt_score': 15.0,
            'critical_patch_count': 2,
            'total_patch_count': 20,
            'overdue_patch_count': 5,
            'maintenance_burden_score': 25.0
        })
        
        # Active alerts
        self._active_alerts: List[DebtAlert] = []
        
        # Alert notification settings
        self._notification_enabled = self._config.get('notifications_enabled', True)
        self._notification_channels = self._config.get('notification_channels', ['log'])
    
    def get_module_info(self) -> Dict[str, Any]:
        """Get module information."""
        return {
            "module_id": self.module_id,
            "name": "Technical Debt Classifier",
            "version": "1.0.0",
            "description": "Comprehensive technical debt classification and alerting system",
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
        
        # Check for critical alerts
        critical_alerts = [a for a in self._active_alerts if a.severity == AlertSeverity.CRITICAL]
        if critical_alerts:
            issues.append(f"{len(critical_alerts)} critical debt alerts active")
            status = ModuleStatus.WARNING
        
        emergency_alerts = [a for a in self._active_alerts if a.severity == AlertSeverity.EMERGENCY]
        if emergency_alerts:
            issues.append(f"{len(emergency_alerts)} emergency debt alerts active")
            status = ModuleStatus.ERROR
        
        return ModuleHealth(
            module_id=self.module_id,
            status=status,
            health_score=1.0 if status == ModuleStatus.HEALTHY else 0.7,
            issues=issues,
            last_check=datetime.now(),
            uptime_seconds=(datetime.now() - self._start_time).total_seconds(),
            error_count=self._error_count,
            warning_count=self._warning_count
        )
    
    def graceful_degradation(self) -> GracefulDegradationResult:
        """Perform graceful degradation."""
        # In degraded mode, disable notifications but keep core functionality
        degraded_capabilities = []
        if not self._notification_enabled:
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
    
    def classify_patches(self, patches: List[PatchAnnotation]) -> Dict[str, Any]:
        """
        Classify and assess a collection of patches.
        
        Args:
            patches: List of patches to classify
            
        Returns:
            Dictionary with comprehensive classification results
        """
        try:
            self._logger.info(f"Classifying {len(patches)} patches")
            
            # Generate component impact assessments
            component_patches = defaultdict(list)
            for patch in patches:
                component_patches[patch.component].append(patch)
            
            component_impacts = {}
            for component, comp_patches in component_patches.items():
                component_impacts[component] = self._impact_engine.assess_component_impact(
                    component, comp_patches
                )
            
            # Detect debt hotspots
            hotspots = self._impact_engine.detect_debt_hotspots(patches)
            
            # Generate overall risk assessment
            risk_assessment = self._impact_engine.generate_risk_assessment(patches)
            
            # Calculate maintenance burdens
            maintenance_burdens = [
                self._impact_engine.calculate_maintenance_burden(patch)
                for patch in patches
            ]
            
            # Check for threshold violations and generate alerts
            new_alerts = self._check_thresholds(
                patches, component_impacts, hotspots, risk_assessment
            )
            
            # Update active alerts
            self._active_alerts.extend(new_alerts)
            
            # Send notifications for new alerts
            if new_alerts and self._notification_enabled:
                self._send_alert_notifications(new_alerts)
            
            classification_result = {
                'summary': {
                    'total_patches': len(patches),
                    'total_debt_score': risk_assessment.total_debt_score,
                    'risk_level': risk_assessment.risk_level,
                    'components_analyzed': len(component_impacts),
                    'hotspots_detected': len(hotspots),
                    'new_alerts': len(new_alerts)
                },
                'component_impacts': {
                    comp: {
                        'patch_count': impact.patch_count,
                        'debt_score': impact.total_debt_score,
                        'risk_factors': impact.risk_factors,
                        'recommendations': impact.recommended_actions
                    }
                    for comp, impact in component_impacts.items()
                },
                'debt_hotspots': [
                    {
                        'component': hotspot.component_name,
                        'type': hotspot.hotspot_type,
                        'severity': hotspot.severity_score,
                        'priority': hotspot.recommended_priority,
                        'description': hotspot.description
                    }
                    for hotspot in hotspots
                ],
                'risk_assessment': {
                    'risk_level': risk_assessment.risk_level,
                    'top_risk_factors': risk_assessment.top_risk_factors,
                    'components_at_risk': risk_assessment.components_at_risk,
                    'recommended_actions': risk_assessment.recommended_actions,
                    'cleanup_timeline': risk_assessment.projected_cleanup_timeline
                },
                'maintenance_analysis': {
                    'total_burden_score': sum(mb.total_burden_score for mb in maintenance_burdens),
                    'high_burden_patches': [
                        mb.patch_id for mb in maintenance_burdens 
                        if mb.burden_category in ['high', 'severe']
                    ],
                    'average_daily_cost': sum(mb.daily_maintenance_cost for mb in maintenance_burdens) / len(maintenance_burdens) if maintenance_burdens else 0
                },
                'alerts': [
                    {
                        'severity': alert.severity.value,
                        'component': alert.component,
                        'message': alert.message,
                        'actions': alert.recommended_actions
                    }
                    for alert in new_alerts
                ],
                'classification_timestamp': datetime.now().isoformat()
            }
            
            self._logger.info(f"Classification complete: {risk_assessment.risk_level} risk level, {len(hotspots)} hotspots, {len(new_alerts)} new alerts")
            return classification_result
            
        except Exception as e:
            self._error_count += 1
            self._logger.error(f"Error during patch classification: {str(e)}")
            raise
    
    def get_active_alerts(self) -> List[DebtAlert]:
        """Get all active debt alerts."""
        return self._active_alerts.copy()
    
    def acknowledge_alert(self, alert_id: str) -> bool:
        """
        Acknowledge a specific alert.
        
        Args:
            alert_id: ID of alert to acknowledge
            
        Returns:
            True if alert was found and acknowledged
        """
        for alert in self._active_alerts:
            if alert.alert_id == alert_id:
                alert.acknowledged = True
                self._logger.info(f"Alert {alert_id} acknowledged")
                return True
        return False
    
    def clear_acknowledged_alerts(self) -> int:
        """
        Clear all acknowledged alerts.
        
        Returns:
            Number of alerts cleared
        """
        initial_count = len(self._active_alerts)
        self._active_alerts = [a for a in self._active_alerts if not a.acknowledged]
        cleared_count = initial_count - len(self._active_alerts)
        
        if cleared_count > 0:
            self._logger.info(f"Cleared {cleared_count} acknowledged alerts")
        
        return cleared_count
    
    def _check_thresholds(self, patches: List[PatchAnnotation], 
                         component_impacts: Dict[str, ComponentImpact],
                         hotspots: List[DebtHotspot],
                         risk_assessment: RiskAssessment) -> List[DebtAlert]:
        """Check for threshold violations and generate alerts."""
        alerts = []
        
        # Check component debt score thresholds
        for component, impact in component_impacts.items():
            if impact.total_debt_score > self._alert_thresholds['component_debt_score']:
                severity = AlertSeverity.CRITICAL if impact.total_debt_score > 30 else AlertSeverity.WARNING
                alerts.append(DebtAlert(
                    alert_id=f"DEBT-{component}-{datetime.now().strftime('%Y%m%d%H%M%S')}",
                    severity=severity,
                    component=component,
                    threshold_type="component_debt_score",
                    current_value=impact.total_debt_score,
                    threshold_value=self._alert_thresholds['component_debt_score'],
                    message=f"Component {component} debt score ({impact.total_debt_score:.1f}) exceeds threshold ({self._alert_thresholds['component_debt_score']})",
                    recommended_actions=impact.recommended_actions
                ))
        
        # Check critical patch count
        critical_patches = [p for p in patches if p.debt_level == DebtLevel.CRITICAL]
        if len(critical_patches) > self._alert_thresholds['critical_patch_count']:
            alerts.append(DebtAlert(
                alert_id=f"CRITICAL-{datetime.now().strftime('%Y%m%d%H%M%S')}",
                severity=AlertSeverity.EMERGENCY,
                component="SYSTEM",
                threshold_type="critical_patch_count",
                current_value=len(critical_patches),
                threshold_value=self._alert_thresholds['critical_patch_count'],
                message=f"System has {len(critical_patches)} critical patches (threshold: {self._alert_thresholds['critical_patch_count']})",
                recommended_actions=["Address critical patches immediately", "Halt non-essential development"]
            ))
        
        # Check total patch count
        if len(patches) > self._alert_thresholds['total_patch_count']:
            alerts.append(DebtAlert(
                alert_id=f"TOTAL-{datetime.now().strftime('%Y%m%d%H%M%S')}",
                severity=AlertSeverity.WARNING,
                component="SYSTEM",
                threshold_type="total_patch_count",
                current_value=len(patches),
                threshold_value=self._alert_thresholds['total_patch_count'],
                message=f"System has {len(patches)} total patches (threshold: {self._alert_thresholds['total_patch_count']})",
                recommended_actions=["Plan systematic cleanup", "Review patch creation process"]
            ))
        
        # Check overdue patches
        overdue_patches = [
            p for p in patches 
            if p.expected_resolution and p.expected_resolution < datetime.now()
        ]
        if len(overdue_patches) > self._alert_thresholds['overdue_patch_count']:
            alerts.append(DebtAlert(
                alert_id=f"OVERDUE-{datetime.now().strftime('%Y%m%d%H%M%S')}",
                severity=AlertSeverity.CRITICAL,
                component="SYSTEM",
                threshold_type="overdue_patch_count",
                current_value=len(overdue_patches),
                threshold_value=self._alert_thresholds['overdue_patch_count'],
                message=f"System has {len(overdue_patches)} overdue patches (threshold: {self._alert_thresholds['overdue_patch_count']})",
                recommended_actions=["Update patch timelines", "Assign cleanup owners", "Escalate overdue items"]
            ))
        
        return alerts
    
    def _send_alert_notifications(self, alerts: List[DebtAlert]) -> None:
        """Send notifications for new alerts."""
        for alert in alerts:
            if 'log' in self._notification_channels:
                log_level = logging.CRITICAL if alert.severity == AlertSeverity.EMERGENCY else logging.WARNING
                self._logger.log(log_level, f"DEBT ALERT: {alert.message}")
            
            # Additional notification channels could be implemented here
            # (email, Slack, webhook, etc.)