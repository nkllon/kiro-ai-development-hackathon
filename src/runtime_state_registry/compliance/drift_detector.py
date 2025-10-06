#!/usr/bin/env python3
"""
Configuration Drift Detection System - Task 10 Implementation
=============================================================

Advanced drift detection system that provides:
- Drift severity classification (CRITICAL, HIGH, MEDIUM, LOW)
- Orphaned service detection (running but not in CMS)
- Missing service detection (in CMS but not running)
- Remediation guidance generation

This system is the intelligence layer that identifies when services
drift from their intended configuration state.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Set, Tuple
from dataclasses import dataclass, field
from enum import Enum
import json
import re

from src.rm_ddd.core.unified_reflective_module import ReflectiveModule
from ..core.models import (
    UnifiedServiceState, ServiceState, DriftSeverity, ComplianceStatus,
    StateLayer, ServiceHealth, ConfigurationDrift
)


class DriftCategory(Enum):
    """Categories of configuration drift."""
    ORPHANED_SERVICE = "orphaned_service"      # Running but not in CMS
    MISSING_SERVICE = "missing_service"        # In CMS but not running
    CONFIGURATION_MISMATCH = "config_mismatch" # Config values differ
    VERSION_DRIFT = "version_drift"            # Version mismatches
    HEALTH_DEGRADATION = "health_degradation"  # Health status issues
    RESOURCE_DRIFT = "resource_drift"          # Resource allocation drift
    DEPENDENCY_DRIFT = "dependency_drift"      # Dependency mismatches


@dataclass
class DriftPattern:
    """Pattern definition for detecting specific types of drift."""
    name: str
    category: DriftCategory
    severity: DriftSeverity
    detection_rules: List[str]  # Regex patterns or conditions
    remediation_template: str
    auto_remediable: bool = False
    
    def matches(self, context: Dict[str, Any]) -> bool:
        """Check if this pattern matches the given context."""
        for rule in self.detection_rules:
            if self._evaluate_rule(rule, context):
                return True
        return False
    
    def _evaluate_rule(self, rule: str, context: Dict[str, Any]) -> bool:
        """Evaluate a detection rule against context."""
        # Simple rule evaluation - can be extended
        if rule.startswith("regex:"):
            pattern = rule[6:]  # Remove "regex:" prefix
            text = str(context)
            return bool(re.search(pattern, text, re.IGNORECASE))
        elif rule.startswith("key_missing:"):
            key = rule[12:]  # Remove "key_missing:" prefix
            return key not in context
        elif rule.startswith("key_present:"):
            key = rule[12:]  # Remove "key_present:" prefix
            return key in context
        elif rule.startswith("value_equals:"):
            key_value = rule[13:].split("=", 1)
            if len(key_value) == 2:
                key, expected_value = key_value
                return context.get(key) == expected_value
        return False


@dataclass
class DriftDetectionResult:
    """Result of drift detection analysis."""
    service_name: str
    detection_timestamp: datetime
    detected_drifts: List[ConfigurationDrift]
    drift_severity: DriftSeverity
    drift_categories: List[DriftCategory]
    orphaned_services: List[str]
    missing_services: List[str]
    remediation_guidance: List[Dict[str, Any]]
    confidence_score: float  # 0.0 to 1.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "service_name": self.service_name,
            "detection_timestamp": self.detection_timestamp.isoformat(),
            "detected_drifts": [drift.to_dict() for drift in self.detected_drifts],
            "drift_severity": self.drift_severity.value,
            "drift_categories": [cat.value for cat in self.drift_categories],
            "orphaned_services": self.orphaned_services,
            "missing_services": self.missing_services,
            "remediation_guidance": self.remediation_guidance,
            "confidence_score": self.confidence_score
        }


class DriftDetector(ReflectiveModule):
    """
    Advanced configuration drift detection system.
    
    Provides intelligent detection of various types of configuration drift:
    - Service lifecycle drift (orphaned/missing services)
    - Configuration value drift
    - Version and dependency drift
    - Health and performance drift
    
    Features:
    - Pattern-based drift detection
    - Severity classification with confidence scoring
    - Automated remediation guidance
    - Historical drift trend analysis
    - Custom drift pattern definitions
    """
    
    def __init__(self, 
                 confidence_threshold: float = 0.7,
                 enable_auto_remediation_suggestions: bool = True):
        super().__init__()
        
        self.confidence_threshold = confidence_threshold
        self.enable_auto_remediation_suggestions = enable_auto_remediation_suggestions
        
        # Initialize drift patterns
        self.drift_patterns = self._initialize_drift_patterns()
        
        # Detection history
        self.detection_history: List[DriftDetectionResult] = []
        self.drift_trends: Dict[str, List[Tuple[datetime, DriftSeverity]]] = {}
        
        self.logger = logging.getLogger(__name__)
        self.logger.info("DriftDetector initialized with pattern-based detection")
    
    async def detect_service_drift(self, 
                                  service_name: str,
                                  spec_state: Optional[Dict[str, Any]] = None,
                                  cms_state: Optional[Dict[str, Any]] = None,
                                  runtime_state: Optional[Dict[str, Any]] = None) -> DriftDetectionResult:
        """
        Detect configuration drift for a specific service.
        
        Args:
            service_name: Name of the service to analyze
            spec_state: Desired state from specifications
            cms_state: Canonical state from CMS
            runtime_state: Actual runtime state
            
        Returns:
            DriftDetectionResult with detailed drift analysis
        """
        start_time = datetime.now()
        self.logger.info(f"Starting drift detection for service: {service_name}")
        
        try:
            # Prepare detection context
            context = {
                "service_name": service_name,
                "spec_state": spec_state or {},
                "cms_state": cms_state or {},
                "runtime_state": runtime_state or {},
                "detection_timestamp": start_time
            }
            
            # Detect various types of drift
            detected_drifts = []
            drift_categories = set()
            
            # 1. Orphaned service detection
            orphaned_services = self._detect_orphaned_services(context)
            if orphaned_services:
                drift_categories.add(DriftCategory.ORPHANED_SERVICE)
                for orphaned in orphaned_services:
                    detected_drifts.append(ConfigurationDrift(
                        service_name=orphaned,
                        drift_type="orphaned_service",
                        severity=DriftSeverity.HIGH,
                        description=f"Service '{orphaned}' is running but not defined in CMS",
                        expected_value=None,
                        actual_value="running",
                        remediation_suggestion=f"Add '{orphaned}' to CMS configuration or stop the service"
                    ))
            
            # 2. Missing service detection
            missing_services = self._detect_missing_services(context)
            if missing_services:
                drift_categories.add(DriftCategory.MISSING_SERVICE)
                for missing in missing_services:
                    detected_drifts.append(ConfigurationDrift(
                        service_name=missing,
                        drift_type="missing_service",
                        severity=DriftSeverity.CRITICAL,
                        description=f"Service '{missing}' is defined in CMS but not running",
                        expected_value="running",
                        actual_value=None,
                        remediation_suggestion=f"Start service '{missing}' or remove from CMS if no longer needed"
                    ))
            
            # 3. Configuration drift detection
            config_drifts = self._detect_configuration_drift(context)
            detected_drifts.extend(config_drifts)
            if config_drifts:
                drift_categories.add(DriftCategory.CONFIGURATION_MISMATCH)
            
            # 4. Version drift detection
            version_drifts = self._detect_version_drift(context)
            detected_drifts.extend(version_drifts)
            if version_drifts:
                drift_categories.add(DriftCategory.VERSION_DRIFT)
            
            # 5. Health degradation detection
            health_drifts = self._detect_health_degradation(context)
            detected_drifts.extend(health_drifts)
            if health_drifts:
                drift_categories.add(DriftCategory.HEALTH_DEGRADATION)
            
            # 6. Pattern-based detection
            pattern_drifts = self._detect_pattern_based_drift(context)
            detected_drifts.extend(pattern_drifts)
            for drift in pattern_drifts:
                # Add categories based on drift type
                if "resource" in drift.drift_type:
                    drift_categories.add(DriftCategory.RESOURCE_DRIFT)
                elif "dependency" in drift.drift_type:
                    drift_categories.add(DriftCategory.DEPENDENCY_DRIFT)
            
            # Calculate overall drift severity
            overall_severity = self._calculate_overall_severity(detected_drifts)
            
            # Generate remediation guidance
            remediation_guidance = self._generate_remediation_guidance(
                service_name, detected_drifts, list(drift_categories)
            )
            
            # Calculate confidence score
            confidence_score = self._calculate_confidence_score(context, detected_drifts)
            
            # Create result
            result = DriftDetectionResult(
                service_name=service_name,
                detection_timestamp=start_time,
                detected_drifts=detected_drifts,
                drift_severity=overall_severity,
                drift_categories=list(drift_categories),
                orphaned_services=orphaned_services,
                missing_services=missing_services,
                remediation_guidance=remediation_guidance,
                confidence_score=confidence_score
            )
            
            # Update tracking
            self._update_drift_trends(service_name, overall_severity, start_time)
            self.detection_history.append(result)
            
            duration = (datetime.now() - start_time).total_seconds()
            self.logger.info(
                f"Drift detection completed for {service_name} in {duration:.2f}s. "
                f"Severity: {overall_severity.value}, Drifts: {len(detected_drifts)}, "
                f"Confidence: {confidence_score:.3f}"
            )
            
            return result
            
        except Exception as e:
            self.logger.error(f"Drift detection failed for {service_name}: {e}")
            return DriftDetectionResult(
                service_name=service_name,
                detection_timestamp=start_time,
                detected_drifts=[],
                drift_severity=DriftSeverity.CRITICAL,
                drift_categories=[],
                orphaned_services=[],
                missing_services=[],
                remediation_guidance=[{
                    "action": "manual_investigation",
                    "priority": "critical",
                    "description": f"Drift detection failed: {e}"
                }],
                confidence_score=0.0
            )
    
    async def detect_system_wide_drift(self, 
                                      all_services_state: Dict[str, Dict[str, Any]]) -> Dict[str, DriftDetectionResult]:
        """
        Detect drift across all services in the system.
        
        Args:
            all_services_state: Dictionary mapping service names to their state data
            
        Returns:
            Dictionary mapping service names to drift detection results
        """
        self.logger.info("Starting system-wide drift detection")
        
        results = {}
        
        # Extract service lists from different layers
        spec_services = set()
        cms_services = set()
        runtime_services = set()
        
        for service_name, state_data in all_services_state.items():
            if state_data.get("spec_state"):
                spec_services.add(service_name)
            if state_data.get("cms_state"):
                cms_services.add(service_name)
            if state_data.get("runtime_state"):
                runtime_services.add(service_name)
        
        # Detect system-wide orphaned and missing services
        system_orphaned = runtime_services - cms_services
        system_missing = cms_services - runtime_services
        
        # Analyze each service
        all_services = spec_services | cms_services | runtime_services
        
        for service_name in all_services:
            state_data = all_services_state.get(service_name, {})
            
            try:
                result = await self.detect_service_drift(
                    service_name=service_name,
                    spec_state=state_data.get("spec_state"),
                    cms_state=state_data.get("cms_state"),
                    runtime_state=state_data.get("runtime_state")
                )
                
                # Add system-wide context
                if service_name in system_orphaned:
                    result.orphaned_services = [service_name]
                if service_name in system_missing:
                    result.missing_services = [service_name]
                
                results[service_name] = result
                
            except Exception as e:
                self.logger.error(f"Failed to detect drift for {service_name}: {e}")
                results[service_name] = DriftDetectionResult(
                    service_name=service_name,
                    detection_timestamp=datetime.now(),
                    detected_drifts=[],
                    drift_severity=DriftSeverity.CRITICAL,
                    drift_categories=[],
                    orphaned_services=[],
                    missing_services=[],
                    remediation_guidance=[{"action": "manual_investigation"}],
                    confidence_score=0.0
                )
        
        self.logger.info(f"System-wide drift detection completed. {len(results)} services analyzed.")
        return results
    
    def get_drift_summary(self) -> Dict[str, Any]:
        """
        Get summary of drift detection across all services.
        
        Returns:
            Dictionary with drift metrics and trends
        """
        if not self.detection_history:
            return {"status": "no_data", "message": "No drift detection data available"}
        
        # Calculate metrics from recent detections
        recent_results = [r for r in self.detection_history 
                         if r.detection_timestamp > datetime.now() - timedelta(hours=24)]
        
        if not recent_results:
            return {"status": "stale_data", "message": "No recent drift detection data"}
        
        # Overall metrics
        total_services = len(set(r.service_name for r in recent_results))
        total_drifts = sum(len(r.detected_drifts) for r in recent_results)
        avg_confidence = sum(r.confidence_score for r in recent_results) / len(recent_results)
        
        # Severity distribution
        severity_counts = {}
        for severity in DriftSeverity:
            severity_counts[severity.value] = len([r for r in recent_results 
                                                  if r.drift_severity == severity])
        
        # Category distribution
        category_counts = {}
        for category in DriftCategory:
            category_counts[category.value] = sum(
                1 for r in recent_results if category in r.drift_categories
            )
        
        # Orphaned and missing services
        all_orphaned = set()
        all_missing = set()
        for result in recent_results:
            all_orphaned.update(result.orphaned_services)
            all_missing.update(result.missing_services)
        
        # Drift trend
        trend = self._calculate_drift_trend()
        
        return {
            "status": "healthy" if total_drifts == 0 else "drift_detected",
            "total_services_analyzed": total_services,
            "total_drifts_detected": total_drifts,
            "average_confidence": round(avg_confidence, 3),
            "drift_severity_distribution": severity_counts,
            "drift_category_distribution": category_counts,
            "orphaned_services": list(all_orphaned),
            "missing_services": list(all_missing),
            "drift_trend": trend,
            "confidence_threshold": self.confidence_threshold,
            "auto_remediation_suggestions_enabled": self.enable_auto_remediation_suggestions
        }
    
    # Private detection methods
    
    def _detect_orphaned_services(self, context: Dict[str, Any]) -> List[str]:
        """Detect services running but not in CMS."""
        orphaned = []
        
        runtime_state = context.get("runtime_state", {})
        cms_state = context.get("cms_state", {})
        
        # If service has runtime state but no CMS state, it's potentially orphaned
        if runtime_state and not cms_state:
            service_name = context.get("service_name")
            if service_name:
                orphaned.append(service_name)
        
        return orphaned
    
    def _detect_missing_services(self, context: Dict[str, Any]) -> List[str]:
        """Detect services in CMS but not running."""
        missing = []
        
        runtime_state = context.get("runtime_state", {})
        cms_state = context.get("cms_state", {})
        
        # If service has CMS state but no runtime state, it's missing
        if cms_state and not runtime_state:
            service_name = context.get("service_name")
            if service_name:
                missing.append(service_name)
        
        return missing
    
    def _detect_configuration_drift(self, context: Dict[str, Any]) -> List[ConfigurationDrift]:
        """Detect configuration value mismatches."""
        drifts = []
        
        spec_state = context.get("spec_state", {})
        cms_state = context.get("cms_state", {})
        runtime_state = context.get("runtime_state", {})
        service_name = context.get("service_name", "unknown")
        
        # Compare spec vs CMS
        if spec_state and cms_state:
            drifts.extend(self._compare_configurations(
                service_name, "spec", "cms", spec_state, cms_state
            ))
        
        # Compare CMS vs runtime
        if cms_state and runtime_state:
            drifts.extend(self._compare_configurations(
                service_name, "cms", "runtime", cms_state, runtime_state
            ))
        
        return drifts
    
    def _detect_version_drift(self, context: Dict[str, Any]) -> List[ConfigurationDrift]:
        """Detect version mismatches between layers."""
        drifts = []
        
        spec_state = context.get("spec_state", {})
        cms_state = context.get("cms_state", {})
        runtime_state = context.get("runtime_state", {})
        service_name = context.get("service_name", "unknown")
        
        # Check for version fields
        version_fields = ["version", "image_tag", "app_version", "build_version"]
        
        for field in version_fields:
            spec_version = spec_state.get(field)
            cms_version = cms_state.get(field)
            runtime_version = runtime_state.get(field)
            
            if spec_version and cms_version and spec_version != cms_version:
                drifts.append(ConfigurationDrift(
                    service_name=service_name,
                    drift_type="version_drift",
                    severity=DriftSeverity.MEDIUM,
                    description=f"Version mismatch in {field}: spec={spec_version}, cms={cms_version}",
                    expected_value=spec_version,
                    actual_value=cms_version,
                    remediation_suggestion=f"Align {field} between specification and CMS"
                ))
            
            if cms_version and runtime_version and cms_version != runtime_version:
                drifts.append(ConfigurationDrift(
                    service_name=service_name,
                    drift_type="version_drift",
                    severity=DriftSeverity.HIGH,
                    description=f"Version mismatch in {field}: cms={cms_version}, runtime={runtime_version}",
                    expected_value=cms_version,
                    actual_value=runtime_version,
                    remediation_suggestion=f"Update runtime {field} to match CMS configuration"
                ))
        
        return drifts
    
    def _detect_health_degradation(self, context: Dict[str, Any]) -> List[ConfigurationDrift]:
        """Detect health status degradation."""
        drifts = []
        
        runtime_state = context.get("runtime_state", {})
        service_name = context.get("service_name", "unknown")
        
        # Check health indicators
        health_indicators = ["health_status", "status", "state", "up"]
        
        for indicator in health_indicators:
            if indicator in runtime_state:
                health_value = runtime_state[indicator]
                
                # Check for unhealthy states
                unhealthy_states = ["down", "unhealthy", "failed", "error", "critical"]
                if str(health_value).lower() in unhealthy_states:
                    drifts.append(ConfigurationDrift(
                        service_name=service_name,
                        drift_type="health_degradation",
                        severity=DriftSeverity.CRITICAL,
                        description=f"Service health degraded: {indicator}={health_value}",
                        expected_value="healthy",
                        actual_value=health_value,
                        remediation_suggestion=f"Investigate and fix health issues for {service_name}"
                    ))
        
        return drifts
    
    def _detect_pattern_based_drift(self, context: Dict[str, Any]) -> List[ConfigurationDrift]:
        """Detect drift using predefined patterns."""
        drifts = []
        
        for pattern in self.drift_patterns:
            if pattern.matches(context):
                service_name = context.get("service_name", "unknown")
                
                drifts.append(ConfigurationDrift(
                    service_name=service_name,
                    drift_type=pattern.category.value,
                    severity=pattern.severity,
                    description=f"Pattern '{pattern.name}' detected drift",
                    expected_value="compliant",
                    actual_value="non_compliant",
                    remediation_suggestion=pattern.remediation_template.format(
                        service_name=service_name
                    )
                ))
        
        return drifts
    
    def _compare_configurations(self, service_name: str, layer1: str, layer2: str,
                               config1: Dict[str, Any], config2: Dict[str, Any]) -> List[ConfigurationDrift]:
        """Compare two configuration dictionaries."""
        drifts = []
        
        all_keys = set(config1.keys()) | set(config2.keys())
        
        for key in all_keys:
            if key not in config1:
                drifts.append(ConfigurationDrift(
                    service_name=service_name,
                    drift_type="configuration_mismatch",
                    severity=DriftSeverity.MEDIUM,
                    description=f"Key '{key}' missing in {layer1}",
                    expected_value=config2.get(key),
                    actual_value=None,
                    remediation_suggestion=f"Add '{key}' to {layer1} configuration"
                ))
            elif key not in config2:
                drifts.append(ConfigurationDrift(
                    service_name=service_name,
                    drift_type="configuration_mismatch",
                    severity=DriftSeverity.MEDIUM,
                    description=f"Key '{key}' missing in {layer2}",
                    expected_value=config1.get(key),
                    actual_value=None,
                    remediation_suggestion=f"Add '{key}' to {layer2} configuration"
                ))
            elif config1[key] != config2[key]:
                drifts.append(ConfigurationDrift(
                    service_name=service_name,
                    drift_type="configuration_mismatch",
                    severity=DriftSeverity.HIGH,
                    description=f"Value mismatch for '{key}': {layer1}={config1[key]}, {layer2}={config2[key]}",
                    expected_value=config1[key],
                    actual_value=config2[key],
                    remediation_suggestion=f"Align '{key}' value between {layer1} and {layer2}"
                ))
        
        return drifts
    
    def _calculate_overall_severity(self, drifts: List[ConfigurationDrift]) -> DriftSeverity:
        """Calculate overall drift severity from individual drifts."""
        if not drifts:
            return DriftSeverity.LOW
        
        # Use highest severity found
        max_severity = DriftSeverity.LOW
        for drift in drifts:
            if drift.severity.value > max_severity.value:
                max_severity = drift.severity
        
        return max_severity
    
    def _generate_remediation_guidance(self, service_name: str, 
                                      drifts: List[ConfigurationDrift],
                                      categories: List[DriftCategory]) -> List[Dict[str, Any]]:
        """Generate specific remediation guidance."""
        guidance = []
        
        # Group drifts by type for better guidance
        drift_by_type = {}
        for drift in drifts:
            drift_type = drift.drift_type
            if drift_type not in drift_by_type:
                drift_by_type[drift_type] = []
            drift_by_type[drift_type].append(drift)
        
        # Generate guidance for each drift type
        for drift_type, type_drifts in drift_by_type.items():
            if drift_type == "orphaned_service":
                guidance.append({
                    "action": "review_orphaned_services",
                    "priority": "high",
                    "description": f"Review {len(type_drifts)} orphaned services and decide to register or terminate",
                    "automated": False,
                    "estimated_effort": "medium"
                })
            elif drift_type == "missing_service":
                guidance.append({
                    "action": "start_missing_services",
                    "priority": "critical",
                    "description": f"Start {len(type_drifts)} missing services or remove from CMS",
                    "automated": True,
                    "estimated_effort": "low"
                })
            elif drift_type == "configuration_mismatch":
                guidance.append({
                    "action": "align_configurations",
                    "priority": "medium",
                    "description": f"Align {len(type_drifts)} configuration mismatches",
                    "automated": True,
                    "estimated_effort": "low"
                })
            elif drift_type == "version_drift":
                guidance.append({
                    "action": "update_versions",
                    "priority": "medium",
                    "description": f"Update {len(type_drifts)} version mismatches",
                    "automated": False,
                    "estimated_effort": "medium"
                })
            elif drift_type == "health_degradation":
                guidance.append({
                    "action": "investigate_health_issues",
                    "priority": "critical",
                    "description": f"Investigate and fix {len(type_drifts)} health issues",
                    "automated": False,
                    "estimated_effort": "high"
                })
        
        # Add summary guidance if multiple categories
        if len(categories) > 1:
            guidance.append({
                "action": "comprehensive_review",
                "priority": "high",
                "description": f"Service {service_name} has multiple drift categories requiring comprehensive review",
                "automated": False,
                "estimated_effort": "high"
            })
        
        return guidance
    
    def _calculate_confidence_score(self, context: Dict[str, Any], 
                                   drifts: List[ConfigurationDrift]) -> float:
        """Calculate confidence score for drift detection."""
        # Base confidence on data availability
        base_confidence = 0.5
        
        # Increase confidence based on available data layers
        if context.get("spec_state"):
            base_confidence += 0.15
        if context.get("cms_state"):
            base_confidence += 0.15
        if context.get("runtime_state"):
            base_confidence += 0.15
        
        # Adjust based on drift consistency
        if drifts:
            # More consistent drift patterns increase confidence
            drift_types = set(drift.drift_type for drift in drifts)
            if len(drift_types) == 1:  # All same type
                base_confidence += 0.1
            elif len(drift_types) <= 3:  # Few types
                base_confidence += 0.05
        
        return min(1.0, base_confidence)
    
    def _initialize_drift_patterns(self) -> List[DriftPattern]:
        """Initialize predefined drift detection patterns."""
        patterns = [
            DriftPattern(
                name="high_memory_usage",
                category=DriftCategory.RESOURCE_DRIFT,
                severity=DriftSeverity.HIGH,
                detection_rules=["regex:memory.*usage.*[89][0-9]%"],
                remediation_template="Investigate high memory usage for {service_name}",
                auto_remediable=False
            ),
            DriftPattern(
                name="high_cpu_usage",
                category=DriftCategory.RESOURCE_DRIFT,
                severity=DriftSeverity.HIGH,
                detection_rules=["regex:cpu.*usage.*[89][0-9]%"],
                remediation_template="Investigate high CPU usage for {service_name}",
                auto_remediable=False
            ),
            DriftPattern(
                name="missing_dependency",
                category=DriftCategory.DEPENDENCY_DRIFT,
                severity=DriftSeverity.CRITICAL,
                detection_rules=["regex:dependency.*not.*found", "regex:import.*error"],
                remediation_template="Install missing dependencies for {service_name}",
                auto_remediable=True
            ),
            DriftPattern(
                name="port_conflict",
                category=DriftCategory.CONFIGURATION_MISMATCH,
                severity=DriftSeverity.HIGH,
                detection_rules=["regex:port.*already.*in.*use", "regex:address.*already.*in.*use"],
                remediation_template="Resolve port conflict for {service_name}",
                auto_remediable=True
            )
        ]
        
        return patterns
    
    def _update_drift_trends(self, service_name: str, severity: DriftSeverity, timestamp: datetime):
        """Update drift trend tracking."""
        if service_name not in self.drift_trends:
            self.drift_trends[service_name] = []
        
        self.drift_trends[service_name].append((timestamp, severity))
        
        # Keep only last 100 data points per service
        if len(self.drift_trends[service_name]) > 100:
            self.drift_trends[service_name] = self.drift_trends[service_name][-100:]
    
    def _calculate_drift_trend(self) -> str:
        """Calculate overall drift trend."""
        if not self.drift_trends:
            return "unknown"
        
        # Simple trend calculation
        recent_severities = []
        older_severities = []
        
        cutoff_time = datetime.now() - timedelta(hours=12)
        
        for service_trends in self.drift_trends.values():
            for timestamp, severity in service_trends:
                if timestamp > cutoff_time:
                    recent_severities.append(severity.value)
                else:
                    older_severities.append(severity.value)
        
        if not recent_severities or not older_severities:
            return "stable"
        
        recent_avg = sum(recent_severities) / len(recent_severities)
        older_avg = sum(older_severities) / len(older_severities)
        
        if recent_avg > older_avg + 0.5:
            return "degrading"
        elif recent_avg < older_avg - 0.5:
            return "improving"
        else:
            return "stable"
    
    # ReflectiveModule implementation
    
    def get_capabilities(self) -> Dict[str, Any]:
        """Return drift detector capabilities."""
        return {
            "module_type": "drift_detector",
            "detection_categories": [cat.value for cat in DriftCategory],
            "severity_levels": [sev.value for sev in DriftSeverity],
            "confidence_threshold": self.confidence_threshold,
            "auto_remediation_suggestions": self.enable_auto_remediation_suggestions,
            "pattern_count": len(self.drift_patterns),
            "features": [
                "orphaned_service_detection",
                "missing_service_detection",
                "configuration_drift_detection",
                "version_drift_detection",
                "health_degradation_detection",
                "pattern_based_detection",
                "trend_analysis"
            ]
        }
    
    def get_module_info(self) -> Dict[str, Any]:
        """Return module information and status."""
        return {
            "name": "DriftDetector",
            "version": "2.0.0",
            "status": "operational",
            "total_detections": len(self.detection_history),
            "tracked_services": len(self.drift_trends),
            "active_patterns": len(self.drift_patterns),
            "confidence_threshold": self.confidence_threshold
        }
    
    def graceful_degradation(self, error: Exception) -> Dict[str, Any]:
        """Handle graceful degradation during failures."""
        self.logger.error(f"DriftDetector degradation: {error}")
        
        return {
            "status": "degraded",
            "error": str(error),
            "available_functions": [
                "get_drift_summary",
                "get_module_info"
            ],
            "degraded_functions": [
                "detect_service_drift",
                "detect_system_wide_drift"
            ],
            "recovery_actions": [
                "Check data collector connectivity",
                "Verify pattern definitions",
                "Restart drift detector"
            ]
        }
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get health status for ReflectiveModule compliance."""
        return {
            "status": "healthy",
            "total_detections": len(self.detection_history),
            "tracked_services": len(self.drift_trends),
            "active_patterns": len(self.drift_patterns),
            "confidence_threshold": self.confidence_threshold
        }


# CLI interface for testing
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Runtime State Registry - Drift Detector")
    parser.add_argument("--service", help="Detect drift for specific service")
    parser.add_argument("--summary", action="store_true", help="Show drift summary")
    parser.add_argument("--confidence-threshold", type=float, default=0.7, 
                       help="Confidence threshold for drift detection")
    
    args = parser.parse_args()
    
    # Configure logging
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    async def main():
        detector = DriftDetector(confidence_threshold=args.confidence_threshold)
        
        if args.summary:
            summary = detector.get_drift_summary()
            print(json.dumps(summary, indent=2))
        elif args.service:
            # Mock data for testing
            result = await detector.detect_service_drift(
                service_name=args.service,
                spec_state={"version": "1.0.0", "port": 8080},
                cms_state={"version": "1.0.1", "port": 8080},
                runtime_state={"version": "1.0.0", "port": 8080, "status": "running"}
            )
            print(json.dumps(result.to_dict(), indent=2))
        else:
            print("Use --help for usage information")
    
    asyncio.run(main())