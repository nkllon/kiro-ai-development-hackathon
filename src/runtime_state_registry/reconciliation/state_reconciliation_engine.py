#!/usr/bin/env python3
"""
State Reconciliation Engine - Phase 2 Implementation
====================================================

Three-layer state reconciliation engine that provides:
- Spec → CMS → Runtime reconciliation
- Drift detection with severity classification
- Quantitative compliance scoring (0.0-1.0)
- Conflict resolution using hierarchical authority

This is the core of the Runtime State Registry's intelligence system.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple, Set
from dataclasses import dataclass, field
from enum import Enum
import json

from src.rm_ddd.core.unified_reflective_module import ReflectiveModule
from ..core.models import (
    UnifiedServiceState, ServiceState, DriftSeverity, ComplianceStatus,
    StateLayer, ServiceHealth, ConfigurationDrift
)
from ..collectors.redis_data_collector import RedisDataCollector
from ..collectors.cms_configuration_collector import CMSConfigurationCollector
from ..collectors.prometheus_integration_collector import PrometheusIntegrationCollector
from ..collectors.grafana_intelligence_collector import GrafanaIntelligenceCollector


class ReconciliationStrategy(Enum):
    """Strategy for resolving conflicts between state layers."""
    SPEC_AUTHORITY = "spec_authority"  # Specification is always correct
    CMS_AUTHORITY = "cms_authority"    # CMS configuration is authoritative
    RUNTIME_REALITY = "runtime_reality"  # Runtime state is the truth
    HIERARCHICAL = "hierarchical"      # Spec > CMS > Runtime priority


@dataclass
class ReconciliationResult:
    """Result of a state reconciliation operation."""
    service_name: str
    reconciliation_timestamp: datetime
    compliance_score: float  # 0.0 to 1.0
    drift_severity: DriftSeverity
    conflicts_detected: List[Dict[str, Any]]
    conflicts_resolved: List[Dict[str, Any]]
    remediation_actions: List[Dict[str, Any]]
    authority_chain: List[str]  # Which layer had authority for each decision
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "service_name": self.service_name,
            "reconciliation_timestamp": self.reconciliation_timestamp.isoformat(),
            "compliance_score": self.compliance_score,
            "drift_severity": self.drift_severity.value,
            "conflicts_detected": self.conflicts_detected,
            "conflicts_resolved": self.conflicts_resolved,
            "remediation_actions": self.remediation_actions,
            "authority_chain": self.authority_chain
        }


class StateReconciliationEngine(ReflectiveModule):
    """
    Three-layer state reconciliation engine for Runtime State Registry.
    
    Provides intelligent reconciliation between:
    - Specification layer (desired state from architectural specs)
    - CMS layer (canonical configuration from Directus)
    - Runtime layer (actual running state from Prometheus/Redis/Grafana)
    
    Features:
    - Drift detection with severity classification
    - Quantitative compliance scoring
    - Conflict resolution using configurable authority hierarchies
    - Auto-remediation recommendations
    - Comprehensive audit trails
    """
    
    def __init__(self, 
                 reconciliation_strategy: ReconciliationStrategy = ReconciliationStrategy.HIERARCHICAL,
                 compliance_threshold: float = 0.8,
                 auto_remediation_enabled: bool = False):
        super().__init__()
        
        self.reconciliation_strategy = reconciliation_strategy
        self.compliance_threshold = compliance_threshold
        self.auto_remediation_enabled = auto_remediation_enabled
        
        # Initialize collectors
        self.redis_collector = RedisDataCollector()
        self.cms_collector = CMSConfigurationCollector()
        self.prometheus_collector = PrometheusIntegrationCollector()
        self.grafana_collector = GrafanaIntelligenceCollector()
        
        # State tracking
        self.last_reconciliation: Optional[datetime] = None
        self.reconciliation_history: List[ReconciliationResult] = []
        self.compliance_trends: Dict[str, List[Tuple[datetime, float]]] = {}
        
        self.logger = logging.getLogger(__name__)
        self.logger.info(f"StateReconciliationEngine initialized with strategy: {reconciliation_strategy.value}")
    
    async def reconcile_service_state(self, service_name: str) -> ReconciliationResult:
        """
        Reconcile state for a specific service across all three layers.
        
        Args:
            service_name: Name of the service to reconcile
            
        Returns:
            ReconciliationResult with detailed reconciliation information
        """
        start_time = datetime.now()
        self.logger.info(f"Starting reconciliation for service: {service_name}")
        
        try:
            # Collect state from all layers
            spec_state = await self._collect_spec_state(service_name)
            cms_state = await self._collect_cms_state(service_name)
            runtime_state = await self._collect_runtime_state(service_name)
            
            # Detect conflicts between layers
            conflicts = self._detect_conflicts(service_name, spec_state, cms_state, runtime_state)
            
            # Resolve conflicts using configured strategy
            resolved_conflicts, authority_chain = self._resolve_conflicts(conflicts)
            
            # Calculate compliance score
            compliance_score = self._calculate_compliance_score(
                service_name, spec_state, cms_state, runtime_state, resolved_conflicts
            )
            
            # Determine drift severity
            drift_severity = self._classify_drift_severity(conflicts, compliance_score)
            
            # Generate remediation actions
            remediation_actions = self._generate_remediation_actions(
                service_name, conflicts, resolved_conflicts, drift_severity
            )
            
            # Create reconciliation result
            result = ReconciliationResult(
                service_name=service_name,
                reconciliation_timestamp=start_time,
                compliance_score=compliance_score,
                drift_severity=drift_severity,
                conflicts_detected=[c.to_dict() for c in conflicts],
                conflicts_resolved=[c.to_dict() for c in resolved_conflicts],
                remediation_actions=remediation_actions,
                authority_chain=authority_chain
            )
            
            # Update tracking
            self._update_compliance_trends(service_name, compliance_score, start_time)
            self.reconciliation_history.append(result)
            
            # Execute auto-remediation if enabled and safe
            if self.auto_remediation_enabled and self._is_safe_for_auto_remediation(result):
                await self._execute_auto_remediation(result)
            
            duration = (datetime.now() - start_time).total_seconds()
            self.logger.info(
                f"Reconciliation completed for {service_name} in {duration:.2f}s. "
                f"Compliance: {compliance_score:.3f}, Drift: {drift_severity.value}"
            )
            
            return result
            
        except Exception as e:
            self.logger.error(f"Reconciliation failed for {service_name}: {e}")
            # Return error result
            return ReconciliationResult(
                service_name=service_name,
                reconciliation_timestamp=start_time,
                compliance_score=0.0,
                drift_severity=DriftSeverity.CRITICAL,
                conflicts_detected=[{"error": str(e)}],
                conflicts_resolved=[],
                remediation_actions=[{"action": "manual_investigation", "reason": str(e)}],
                authority_chain=["error"]
            )
    
    async def reconcile_all_services(self) -> Dict[str, ReconciliationResult]:
        """
        Reconcile state for all discovered services.
        
        Returns:
            Dictionary mapping service names to reconciliation results
        """
        self.logger.info("Starting full system reconciliation")
        
        # Discover all services across all layers
        all_services = await self._discover_all_services()
        
        # Reconcile each service
        results = {}
        for service_name in all_services:
            try:
                result = await self.reconcile_service_state(service_name)
                results[service_name] = result
            except Exception as e:
                self.logger.error(f"Failed to reconcile {service_name}: {e}")
                results[service_name] = ReconciliationResult(
                    service_name=service_name,
                    reconciliation_timestamp=datetime.now(),
                    compliance_score=0.0,
                    drift_severity=DriftSeverity.CRITICAL,
                    conflicts_detected=[{"error": str(e)}],
                    conflicts_resolved=[],
                    remediation_actions=[{"action": "manual_investigation"}],
                    authority_chain=["error"]
                )
        
        self.last_reconciliation = datetime.now()
        self.logger.info(f"Full system reconciliation completed. {len(results)} services processed.")
        
        return results
    
    def get_compliance_summary(self) -> Dict[str, Any]:
        """
        Get overall compliance summary across all services.
        
        Returns:
            Dictionary with compliance metrics and trends
        """
        if not self.reconciliation_history:
            return {"status": "no_data", "message": "No reconciliation data available"}
        
        # Calculate overall metrics
        recent_results = [r for r in self.reconciliation_history 
                         if r.reconciliation_timestamp > datetime.now() - timedelta(hours=24)]
        
        if not recent_results:
            return {"status": "stale_data", "message": "No recent reconciliation data"}
        
        total_services = len(set(r.service_name for r in recent_results))
        avg_compliance = sum(r.compliance_score for r in recent_results) / len(recent_results)
        
        # Count by severity
        severity_counts = {}
        for severity in DriftSeverity:
            severity_counts[severity.value] = len([r for r in recent_results 
                                                  if r.drift_severity == severity])
        
        # Compliance trend
        trend = self._calculate_compliance_trend()
        
        return {
            "status": "healthy" if avg_compliance >= self.compliance_threshold else "degraded",
            "total_services": total_services,
            "average_compliance": round(avg_compliance, 3),
            "compliance_threshold": self.compliance_threshold,
            "drift_severity_distribution": severity_counts,
            "compliance_trend": trend,
            "last_reconciliation": self.last_reconciliation.isoformat() if self.last_reconciliation else None,
            "reconciliation_strategy": self.reconciliation_strategy.value,
            "auto_remediation_enabled": self.auto_remediation_enabled
        }
    
    # Private methods for implementation details
    
    async def _collect_spec_state(self, service_name: str) -> Optional[Dict[str, Any]]:
        """Collect desired state from specifications."""
        # TODO: Implement specification state collection
        # This would parse DAG dependencies and architectural specifications
        return None
    
    async def _collect_cms_state(self, service_name: str) -> Optional[Dict[str, Any]]:
        """Collect canonical state from CMS."""
        try:
            return await self.cms_collector.get_service_configuration(service_name)
        except Exception as e:
            self.logger.warning(f"Failed to collect CMS state for {service_name}: {e}")
            return None
    
    async def _collect_runtime_state(self, service_name: str) -> Optional[Dict[str, Any]]:
        """Collect actual runtime state from monitoring systems."""
        runtime_state = {}
        
        # Collect from Redis
        try:
            redis_data = await self.redis_collector.get_service_data(service_name)
            if redis_data:
                runtime_state["redis"] = redis_data
        except Exception as e:
            self.logger.warning(f"Failed to collect Redis state for {service_name}: {e}")
        
        # Collect from Prometheus
        try:
            prometheus_data = await self.prometheus_collector.get_service_metrics(service_name)
            if prometheus_data:
                runtime_state["prometheus"] = prometheus_data
        except Exception as e:
            self.logger.warning(f"Failed to collect Prometheus state for {service_name}: {e}")
        
        # Collect from Grafana
        try:
            grafana_data = await self.grafana_collector.get_service_dashboards(service_name)
            if grafana_data:
                runtime_state["grafana"] = grafana_data
        except Exception as e:
            self.logger.warning(f"Failed to collect Grafana state for {service_name}: {e}")
        
        return runtime_state if runtime_state else None
    
    def _detect_conflicts(self, service_name: str, spec_state: Optional[Dict], 
                         cms_state: Optional[Dict], runtime_state: Optional[Dict]) -> List[ConfigurationDrift]:
        """Detect conflicts between state layers."""
        conflicts = []
        
        # Compare spec vs CMS
        if spec_state and cms_state:
            spec_cms_conflicts = self._compare_states("spec", "cms", spec_state, cms_state)
            conflicts.extend(spec_cms_conflicts)
        
        # Compare CMS vs Runtime
        if cms_state and runtime_state:
            cms_runtime_conflicts = self._compare_states("cms", "runtime", cms_state, runtime_state)
            conflicts.extend(cms_runtime_conflicts)
        
        # Compare Spec vs Runtime (if CMS is missing)
        if spec_state and runtime_state and not cms_state:
            spec_runtime_conflicts = self._compare_states("spec", "runtime", spec_state, runtime_state)
            conflicts.extend(spec_runtime_conflicts)
        
        return conflicts
    
    def _compare_states(self, layer1: str, layer2: str, state1: Dict, state2: Dict) -> List[ConfigurationDrift]:
        """Compare two state dictionaries and identify conflicts."""
        conflicts = []
        
        # Simple implementation - compare keys and values
        all_keys = set(state1.keys()) | set(state2.keys())
        
        for key in all_keys:
            if key not in state1:
                conflicts.append(ConfigurationDrift(
                    service_name="",  # Will be set by caller
                    drift_type=f"missing_in_{layer1}",
                    severity=DriftSeverity.MEDIUM,
                    description=f"Key '{key}' present in {layer2} but missing in {layer1}",
                    expected_value=None,
                    actual_value=state2.get(key),
                    remediation_suggestion=f"Add '{key}' to {layer1} configuration"
                ))
            elif key not in state2:
                conflicts.append(ConfigurationDrift(
                    service_name="",  # Will be set by caller
                    drift_type=f"missing_in_{layer2}",
                    severity=DriftSeverity.MEDIUM,
                    description=f"Key '{key}' present in {layer1} but missing in {layer2}",
                    expected_value=state1.get(key),
                    actual_value=None,
                    remediation_suggestion=f"Add '{key}' to {layer2} configuration"
                ))
            elif state1[key] != state2[key]:
                conflicts.append(ConfigurationDrift(
                    service_name="",  # Will be set by caller
                    drift_type="value_mismatch",
                    severity=DriftSeverity.HIGH,
                    description=f"Value mismatch for '{key}': {layer1}={state1[key]}, {layer2}={state2[key]}",
                    expected_value=state1[key],
                    actual_value=state2[key],
                    remediation_suggestion=f"Align '{key}' value between {layer1} and {layer2}"
                ))
        
        return conflicts
    
    def _resolve_conflicts(self, conflicts: List[ConfigurationDrift]) -> Tuple[List[ConfigurationDrift], List[str]]:
        """Resolve conflicts using the configured reconciliation strategy."""
        resolved_conflicts = []
        authority_chain = []
        
        for conflict in conflicts:
            if self.reconciliation_strategy == ReconciliationStrategy.HIERARCHICAL:
                # Spec > CMS > Runtime priority
                if "spec" in conflict.drift_type:
                    authority_chain.append("spec")
                elif "cms" in conflict.drift_type:
                    authority_chain.append("cms")
                else:
                    authority_chain.append("runtime")
            elif self.reconciliation_strategy == ReconciliationStrategy.SPEC_AUTHORITY:
                authority_chain.append("spec")
            elif self.reconciliation_strategy == ReconciliationStrategy.CMS_AUTHORITY:
                authority_chain.append("cms")
            elif self.reconciliation_strategy == ReconciliationStrategy.RUNTIME_REALITY:
                authority_chain.append("runtime")
            
            # Mark conflict as resolved (actual resolution would depend on implementation)
            resolved_conflicts.append(conflict)
        
        return resolved_conflicts, authority_chain
    
    def _calculate_compliance_score(self, service_name: str, spec_state: Optional[Dict],
                                   cms_state: Optional[Dict], runtime_state: Optional[Dict],
                                   resolved_conflicts: List[ConfigurationDrift]) -> float:
        """Calculate quantitative compliance score (0.0 to 1.0)."""
        if not any([spec_state, cms_state, runtime_state]):
            return 0.0
        
        # Simple scoring based on conflicts
        total_possible_conflicts = 100  # Baseline assumption
        actual_conflicts = len(resolved_conflicts)
        
        # Weight conflicts by severity
        weighted_conflicts = 0
        for conflict in resolved_conflicts:
            if conflict.severity == DriftSeverity.CRITICAL:
                weighted_conflicts += 10
            elif conflict.severity == DriftSeverity.HIGH:
                weighted_conflicts += 5
            elif conflict.severity == DriftSeverity.MEDIUM:
                weighted_conflicts += 2
            else:  # LOW
                weighted_conflicts += 1
        
        # Calculate score (higher is better)
        score = max(0.0, 1.0 - (weighted_conflicts / total_possible_conflicts))
        return min(1.0, score)
    
    def _classify_drift_severity(self, conflicts: List[ConfigurationDrift], compliance_score: float) -> DriftSeverity:
        """Classify overall drift severity based on conflicts and compliance score."""
        if compliance_score < 0.3:
            return DriftSeverity.CRITICAL
        elif compliance_score < 0.6:
            return DriftSeverity.HIGH
        elif compliance_score < 0.8:
            return DriftSeverity.MEDIUM
        else:
            return DriftSeverity.LOW
    
    def _generate_remediation_actions(self, service_name: str, conflicts: List[ConfigurationDrift],
                                     resolved_conflicts: List[ConfigurationDrift],
                                     drift_severity: DriftSeverity) -> List[Dict[str, Any]]:
        """Generate specific remediation actions for detected drift."""
        actions = []
        
        for conflict in conflicts:
            actions.append({
                "action_type": "configuration_update",
                "priority": conflict.severity.value,
                "description": conflict.remediation_suggestion,
                "automated": drift_severity in [DriftSeverity.LOW, DriftSeverity.MEDIUM],
                "estimated_impact": "low" if conflict.severity == DriftSeverity.LOW else "medium"
            })
        
        # Add summary action
        if drift_severity == DriftSeverity.CRITICAL:
            actions.append({
                "action_type": "manual_intervention",
                "priority": "critical",
                "description": f"Service {service_name} requires immediate manual attention",
                "automated": False,
                "estimated_impact": "high"
            })
        
        return actions
    
    async def _discover_all_services(self) -> Set[str]:
        """Discover all services across all layers."""
        services = set()
        
        # Discover from Redis
        try:
            redis_services = await self.redis_collector.discover_services()
            services.update(redis_services)
        except Exception as e:
            self.logger.warning(f"Failed to discover Redis services: {e}")
        
        # Discover from CMS
        try:
            cms_services = await self.cms_collector.discover_services()
            services.update(cms_services)
        except Exception as e:
            self.logger.warning(f"Failed to discover CMS services: {e}")
        
        # Discover from Prometheus
        try:
            prometheus_services = await self.prometheus_collector.discover_services()
            services.update(prometheus_services)
        except Exception as e:
            self.logger.warning(f"Failed to discover Prometheus services: {e}")
        
        # Discover from Grafana
        try:
            grafana_services = await self.grafana_collector.discover_services()
            services.update(grafana_services)
        except Exception as e:
            self.logger.warning(f"Failed to discover Grafana services: {e}")
        
        return services
    
    def _update_compliance_trends(self, service_name: str, compliance_score: float, timestamp: datetime):
        """Update compliance trend tracking for a service."""
        if service_name not in self.compliance_trends:
            self.compliance_trends[service_name] = []
        
        self.compliance_trends[service_name].append((timestamp, compliance_score))
        
        # Keep only last 100 data points per service
        if len(self.compliance_trends[service_name]) > 100:
            self.compliance_trends[service_name] = self.compliance_trends[service_name][-100:]
    
    def _calculate_compliance_trend(self) -> str:
        """Calculate overall compliance trend across all services."""
        if not self.compliance_trends:
            return "unknown"
        
        # Simple trend calculation based on recent vs older averages
        recent_scores = []
        older_scores = []
        
        cutoff_time = datetime.now() - timedelta(hours=12)
        
        for service_trends in self.compliance_trends.values():
            for timestamp, score in service_trends:
                if timestamp > cutoff_time:
                    recent_scores.append(score)
                else:
                    older_scores.append(score)
        
        if not recent_scores or not older_scores:
            return "stable"
        
        recent_avg = sum(recent_scores) / len(recent_scores)
        older_avg = sum(older_scores) / len(older_scores)
        
        if recent_avg > older_avg + 0.05:
            return "improving"
        elif recent_avg < older_avg - 0.05:
            return "degrading"
        else:
            return "stable"
    
    def _is_safe_for_auto_remediation(self, result: ReconciliationResult) -> bool:
        """Determine if auto-remediation is safe for this result."""
        # Only auto-remediate low and medium severity drift
        if result.drift_severity in [DriftSeverity.CRITICAL, DriftSeverity.HIGH]:
            return False
        
        # Only auto-remediate if compliance score is reasonable
        if result.compliance_score < 0.5:
            return False
        
        # Check if all remediation actions are marked as automated
        for action in result.remediation_actions:
            if not action.get("automated", False):
                return False
        
        return True
    
    async def _execute_auto_remediation(self, result: ReconciliationResult):
        """Execute automatic remediation actions."""
        self.logger.info(f"Executing auto-remediation for {result.service_name}")
        
        for action in result.remediation_actions:
            if action.get("automated", False):
                try:
                    # TODO: Implement actual remediation execution
                    self.logger.info(f"Would execute: {action['description']}")
                except Exception as e:
                    self.logger.error(f"Auto-remediation failed for {result.service_name}: {e}")
    
    # ReflectiveModule implementation
    
    def get_capabilities(self) -> Dict[str, Any]:
        """Return state reconciliation engine capabilities."""
        return {
            "module_type": "state_reconciliation_engine",
            "reconciliation_strategies": [s.value for s in ReconciliationStrategy],
            "current_strategy": self.reconciliation_strategy.value,
            "compliance_threshold": self.compliance_threshold,
            "auto_remediation_enabled": self.auto_remediation_enabled,
            "supported_layers": ["specification", "cms", "runtime"],
            "collectors": ["redis", "cms", "prometheus", "grafana"],
            "features": [
                "drift_detection",
                "compliance_scoring",
                "conflict_resolution",
                "auto_remediation",
                "trend_analysis"
            ]
        }
    
    def get_module_info(self) -> Dict[str, Any]:
        """Return module information and current status."""
        return {
            "name": "StateReconciliationEngine",
            "version": "2.0.0",
            "status": "operational",
            "last_reconciliation": self.last_reconciliation.isoformat() if self.last_reconciliation else None,
            "total_reconciliations": len(self.reconciliation_history),
            "tracked_services": len(self.compliance_trends),
            "average_compliance": self._get_average_compliance(),
            "reconciliation_strategy": self.reconciliation_strategy.value
        }
    
    def graceful_degradation(self, error: Exception) -> Dict[str, Any]:
        """Handle graceful degradation during failures."""
        self.logger.error(f"StateReconciliationEngine degradation: {error}")
        
        return {
            "status": "degraded",
            "error": str(error),
            "available_functions": [
                "get_compliance_summary",
                "get_module_info"
            ],
            "degraded_functions": [
                "reconcile_service_state",
                "reconcile_all_services"
            ],
            "recovery_actions": [
                "Check collector connectivity",
                "Verify Redis/CMS/Prometheus availability",
                "Restart reconciliation engine"
            ]
        }
    
    def _get_average_compliance(self) -> float:
        """Get average compliance score across all recent reconciliations."""
        if not self.reconciliation_history:
            return 0.0
        
        recent_results = [r for r in self.reconciliation_history 
                         if r.reconciliation_timestamp > datetime.now() - timedelta(hours=24)]
        
        if not recent_results:
            return 0.0
        
        return sum(r.compliance_score for r in recent_results) / len(recent_results)
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get health status for ReflectiveModule compliance."""
        return {
            "status": "healthy",
            "last_reconciliation": self.last_reconciliation.isoformat() if self.last_reconciliation else None,
            "total_reconciliations": len(self.reconciliation_history),
            "average_compliance": self._get_average_compliance(),
            "tracked_services": len(self.compliance_trends)
        }


# CLI interface for testing
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Runtime State Registry - State Reconciliation Engine")
    parser.add_argument("--service", help="Reconcile specific service")
    parser.add_argument("--all", action="store_true", help="Reconcile all services")
    parser.add_argument("--summary", action="store_true", help="Show compliance summary")
    parser.add_argument("--strategy", choices=[s.value for s in ReconciliationStrategy], 
                       default="hierarchical", help="Reconciliation strategy")
    
    args = parser.parse_args()
    
    # Configure logging
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    async def main():
        engine = StateReconciliationEngine(
            reconciliation_strategy=ReconciliationStrategy(args.strategy)
        )
        
        if args.summary:
            summary = engine.get_compliance_summary()
            print(json.dumps(summary, indent=2))
        elif args.service:
            result = await engine.reconcile_service_state(args.service)
            print(json.dumps(result.to_dict(), indent=2))
        elif args.all:
            results = await engine.reconcile_all_services()
            for service_name, result in results.items():
                print(f"\n=== {service_name} ===")
                print(json.dumps(result.to_dict(), indent=2))
        else:
            print("Use --help for usage information")
    
    asyncio.run(main())