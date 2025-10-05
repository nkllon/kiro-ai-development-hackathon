"""
Core Deployment Data Governance Auditor implementation.

This module provides the main DeploymentAuditor class that inherits from ReflectiveModule
to provide comprehensive observability, health monitoring, and Beast Mode compliance.
"""

import os
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
from pathlib import Path

from src.rm_ddd.core.unified_reflective_module import (
    ReflectiveModule,
    ModuleCapability,
    ModuleHealth,
    ModuleStatus,
    GracefulDegradationResult
)
from .models import (
    ConfigurationSchema, MonitoringStatus, ComplianceReport,
    ClassifiedViolation, RemediationResult, Severity
)


class DeploymentAuditor(ReflectiveModule):
    """
    Main Deployment Data Governance Auditor class.
    
    Provides real-time monitoring of deployment directories for governance violations,
    with automated remediation and comprehensive reporting capabilities.
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """Initialize the Deployment Auditor with Beast Mode observability."""
        super().__init__()
        
        # Core configuration
        self.config_path = config_path or "deployment-auditor-config.yml"
        self.config: ConfigurationSchema = ConfigurationSchema.default_config()
        
        # Monitoring state
        self.monitoring_status = MonitoringStatus(
            is_active=False,
            watched_paths=[],
            events_processed=0,
            violations_detected=0
        )
        
        # Component references (will be initialized by specific components)
        self.file_monitor = None
        self.violation_detector = None
        self.violation_classifier = None
        self.auto_remediator = None
        self.report_generator = None
        
        # Metrics tracking
        self.metrics = {
            "violations_detected_total": 0,
            "violations_by_severity": {s.value: 0 for s in Severity},
            "files_scanned_total": 0,
            "remediation_actions_total": 0,
            "scan_duration_seconds": 0.0
        }
        
        self._logger.info("DeploymentAuditor initialized", extra={
            "config_path": self.config_path,
            "component": "deployment_auditor"
        })
    
    def load_configuration(self, config_path: Optional[str] = None) -> bool:
        """
        Load configuration from YAML file.
        
        Args:
            config_path: Optional path to configuration file
            
        Returns:
            bool: True if configuration loaded successfully
        """
        if config_path:
            self.config_path = config_path
            
        try:
            if os.path.exists(self.config_path):
                import yaml
                with open(self.config_path, 'r') as f:
                    config_data = yaml.safe_load(f)
                
                # Update configuration with loaded data
                if config_data:
                    self.config.monitoring.update(config_data.get('monitoring', {}))
                    self.config.patterns.update(config_data.get('patterns', {}))
                    self.config.remediation.update(config_data.get('remediation', {}))
                    self.config.notifications.update(config_data.get('notifications', {}))
                    self.config.prometheus.update(config_data.get('prometheus', {}))
                
                self._logger.info("Configuration loaded successfully", extra={
                    "config_path": self.config_path,
                    "component": "deployment_auditor"
                })
                return True
            else:
                self._logger.warning("Configuration file not found, using defaults", extra={
                    "config_path": self.config_path,
                    "component": "deployment_auditor"
                })
                return True  # Using defaults is acceptable

        except Exception as e:
            self._logger.error("Failed to load configuration", extra={
                "config_path": self.config_path,
                "error": str(e),
                "component": "deployment_auditor"
            })
            return False
    
    def start_monitoring(self) -> bool:
        """
        Start the deployment data monitoring daemon.
        
        Returns:
            bool: True if monitoring started successfully
        """
        try:
            # Load configuration first
            if not self.load_configuration():
                return False
            
            # Initialize watch paths
            watch_paths = self.config.monitoring.get("watch_paths", ["deployment/"])
            self.monitoring_status.watched_paths = [
                os.path.abspath(path) for path in watch_paths
                if os.path.exists(path)
            ]
            
            if not self.monitoring_status.watched_paths:
                self._logger.warning("No valid watch paths found", extra={
                    "requested_paths": watch_paths,
                    "component": "deployment_auditor"
                })
                return False

            # Update monitoring status
            self.monitoring_status.is_active = True
            self.monitoring_status.last_scan = datetime.now()

            self._logger.info("Monitoring started successfully", extra={
                "watch_paths": self.monitoring_status.watched_paths,
                "component": "deployment_auditor"
            })

            return True

        except Exception as e:
            self._logger.error("Failed to start monitoring", extra={
                "error": str(e),
                "component": "deployment_auditor"
            })
            return False
    
    def stop_monitoring(self) -> bool:
        """
        Stop the deployment data monitoring daemon.
        
        Returns:
            bool: True if monitoring stopped successfully
        """
        try:
            self.monitoring_status.is_active = False

            self._logger.info("Monitoring stopped successfully", extra={
                "events_processed": self.monitoring_status.events_processed,
                "violations_detected": self.monitoring_status.violations_detected,
                "component": "deployment_auditor"
            })

            return True

        except Exception as e:
            self._logger.error("Failed to stop monitoring", extra={
                "error": str(e),
                "component": "deployment_auditor"
            })
            return False
    
    def scan_directory(self, directory_path: str) -> ComplianceReport:
        """
        Perform a baseline scan of a directory for violations.
        
        Args:
            directory_path: Path to directory to scan
            
        Returns:
            ComplianceReport: Comprehensive scan results
        """
        start_time = datetime.now()
        
        report = ComplianceReport(
            scan_timestamp=start_time,
            total_files_scanned=0,
            violations_found=0,
            violations_by_severity={},
            violations_by_type={},
            remediation_summary={},
            recommendations=[]
        )
        
        try:
            directory = Path(directory_path)
            if not directory.exists():
                self._logger.warning("Directory does not exist", extra={
                    "directory": directory_path,
                    "component": "deployment_auditor"
                })
                return report

            # Scan all files in directory recursively
            for file_path in directory.rglob("*"):
                if file_path.is_file():
                    report.total_files_scanned += 1

                    # This would normally use the violation detector
                    # For now, we'll implement basic pattern matching
                    if self._is_violation(str(file_path)):
                        report.violations_found += 1

            # Update metrics
            self.metrics["files_scanned_total"] += report.total_files_scanned
            self.metrics["violations_detected_total"] += report.violations_found

            scan_duration = (datetime.now() - start_time).total_seconds()
            self.metrics["scan_duration_seconds"] = scan_duration

            self._logger.info("Directory scan completed", extra={
                "directory": directory_path,
                "files_scanned": report.total_files_scanned,
                "violations_found": report.violations_found,
                "scan_duration": scan_duration,
                "component": "deployment_auditor"
            })

        except Exception as e:
            self._logger.error("Directory scan failed", extra={
                "directory": directory_path,
                "error": str(e),
                "component": "deployment_auditor"
            })
        
        return report
    
    def _is_violation(self, file_path: str) -> bool:
        """
        Basic violation detection (will be replaced by proper detector).
        
        Args:
            file_path: Path to file to check
            
        Returns:
            bool: True if file appears to be a violation
        """
        # Basic patterns from governance rules
        violation_patterns = [
            ".db", ".sqlite", ".log", 
            "prometheus-data", "grafana-data",
            "cache/", "tmp/", "temp/"
        ]
        
        file_path_lower = file_path.lower()
        return any(pattern in file_path_lower for pattern in violation_patterns)
    
    def get_health_status(self) -> ModuleHealth:
        """
        Get comprehensive health status for Beast Mode integration.

        Returns:
            ModuleHealth object containing health status information
        """
        # Calculate health score based on error rate and activity
        error_count = len(self.monitoring_status.errors)
        health_score = 1.0

        if error_count > 0:
            health_score -= min(0.5, error_count * 0.05)

        if not self.monitoring_status.is_active:
            health_score -= 0.2

        # Determine status
        if health_score >= 0.9:
            status = ModuleStatus.HEALTHY
        elif health_score >= 0.7:
            status = ModuleStatus.WARNING
        elif health_score >= 0.5:
            status = ModuleStatus.DEGRADED
        else:
            status = ModuleStatus.ERROR

        # Calculate uptime
        uptime_seconds = (datetime.now() - self._start_time).total_seconds()

        return ModuleHealth(
            module_id="deployment_auditor",
            status=status,
            health_score=health_score,
            issues=self.monitoring_status.errors[-10:],  # Last 10 errors
            last_check=datetime.now(),
            uptime_seconds=uptime_seconds,
            error_count=error_count,
            warning_count=self._warning_count
        )
    
    def get_metrics(self) -> Dict[str, Any]:
        """
        Get Prometheus-compatible metrics.
        
        Returns:
            Dict containing metrics for Prometheus export
        """
        prefix = self.config.prometheus.get("metrics_prefix", "deployment_auditor_")
        
        return {
            f"{prefix}violations_detected_total": self.metrics["violations_detected_total"],
            f"{prefix}files_scanned_total": self.metrics["files_scanned_total"],
            f"{prefix}remediation_actions_total": self.metrics["remediation_actions_total"],
            f"{prefix}scan_duration_seconds": self.metrics["scan_duration_seconds"],
            f"{prefix}monitoring_active": 1 if self.monitoring_status.is_active else 0,
            f"{prefix}watched_paths_count": len(self.monitoring_status.watched_paths),
            **{
                f"{prefix}violations_{severity}_total": count
                for severity, count in self.metrics["violations_by_severity"].items()
            }
        }
    
    def is_ready(self) -> bool:
        """
        Check if the auditor is ready to process requests.
        
        Returns:
            bool: True if ready
        """
        return (
            self.config is not None and
            len(self.monitoring_status.errors) < 10  # Not too many errors
        )
    
    def shutdown(self) -> bool:
        """
        Gracefully shutdown the auditor.
        
        Returns:
            bool: True if shutdown successful
        """
        try:
            if self.monitoring_status.is_active:
                self.stop_monitoring()

            self._logger.info("DeploymentAuditor shutdown completed", extra={
                "component": "deployment_auditor"
            })

            return True

        except Exception as e:
            self._logger.error("Shutdown failed", extra={
                "error": str(e),
                "component": "deployment_auditor"
            })
            return False
    
    def get_capabilities(self) -> List[ModuleCapability]:
        """
        Get module capabilities for Beast Mode integration.

        Returns:
            List of ModuleCapability enums
        """
        return [
            ModuleCapability.CORE_FUNCTIONALITY,
            ModuleCapability.DATA_PROCESSING,
            ModuleCapability.VALIDATION,
            ModuleCapability.MONITORING
        ]
    
    def get_module_info(self) -> Dict[str, Any]:
        """
        Get detailed module information.
        
        Returns:
            Dict containing module information
        """
        return {
            "module_name": "deployment_auditor",
            "module_type": "governance_auditor",
            "version": "1.0.0",
            "author": "Beast Mode Framework",
            "description": "Deployment Data Governance Auditor - prevents volatile data in version control",
            "configuration": {
                "config_file": self.config_path,
                "watch_paths": self.monitoring_status.watched_paths,
                "auto_remediation": self.config.remediation.get("auto_gitignore", False)
            },
            "status": {
                "monitoring_active": self.monitoring_status.is_active,
                "events_processed": self.monitoring_status.events_processed,
                "violations_detected": self.monitoring_status.violations_detected
            }
        }
    
    def graceful_degradation(self) -> GracefulDegradationResult:
        """
        Handle graceful degradation when errors occur.

        Returns:
            GracefulDegradationResult with degradation status
        """
        self._logger.warning("Graceful degradation triggered", extra={
            "component": "deployment_auditor"
        })

        # Determine which capabilities to degrade based on health
        health = self.get_health_status()
        degraded_capabilities = []
        remaining_capabilities = list(self.get_capabilities())

        if health.status == ModuleStatus.ERROR or health.error_count > 10:
            # Severe degradation - disable automated remediation
            degraded_capabilities.append(ModuleCapability.DATA_PROCESSING)
            if ModuleCapability.DATA_PROCESSING in remaining_capabilities:
                remaining_capabilities.remove(ModuleCapability.DATA_PROCESSING)

        if health.status == ModuleStatus.DEGRADED:
            # Moderate degradation - reduce validation strictness
            degraded_capabilities.append(ModuleCapability.VALIDATION)
            if ModuleCapability.VALIDATION in remaining_capabilities:
                remaining_capabilities.remove(ModuleCapability.VALIDATION)

        success = len(remaining_capabilities) > 0

        return GracefulDegradationResult(
            success=success,
            degraded_capabilities=degraded_capabilities,
            remaining_capabilities=remaining_capabilities,
            error_message=f"Degraded due to health status: {health.status.value}" if degraded_capabilities else None
        )