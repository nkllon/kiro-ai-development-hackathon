#!/usr/bin/env python3
"""
Accuracy Monitor - Phase 5 Task 5.2 Component

Monitors documentation accuracy with systematic tracking,
alerting, and correlation ID tracking across all components.
"""

import asyncio
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, asdict
from collections import defaultdict
import statistics

from src.rm_ddd.core.unified_reflective_module import ReflectiveModule


@dataclass
class AccuracyMetric:
    """Represents an accuracy measurement."""
    metric_id: str
    component: str
    metric_type: str  # 'validation', 'generation', 'discovery', 'analysis'
    accuracy_score: float  # 0.0 to 1.0
    timestamp: datetime
    correlation_id: Optional[str] = None
    details: Dict[str, Any] = None
    confidence_level: float = 1.0  # How confident we are in this measurement


@dataclass
class AccuracyAlert:
    """Represents an accuracy alert."""
    alert_id: str
    alert_type: str  # 'threshold_breach', 'trend_decline', 'component_failure'
    severity: str  # 'critical', 'warning', 'info'
    component: str
    current_accuracy: float
    threshold: float
    timestamp: datetime
    correlation_id: Optional[str] = None
    message: str = ""
    resolved: bool = False
    resolution_timestamp: Optional[datetime] = None


@dataclass
class AccuracyThreshold:
    """Defines accuracy thresholds for monitoring."""
    component: str
    metric_type: str
    critical_threshold: float  # Below this triggers critical alert
    warning_threshold: float   # Below this triggers warning alert
    trend_window_minutes: int = 60  # Window for trend analysis
    min_samples: int = 5       # Minimum samples needed for trend analysis


class AccuracyMonitor(ReflectiveModule):
    """
    Systematic accuracy monitoring with correlation ID tracking.
    
    Monitors documentation accuracy across all components, tracks trends,
    and provides alerting when accuracy drops below thresholds.
    """
    
    def __init__(self, default_threshold: float = 0.95):
        super().__init__()
        self.default_threshold = default_threshold
        self.accuracy_metrics: List[AccuracyMetric] = []
        self.accuracy_alerts: List[AccuracyAlert] = []
        self.accuracy_thresholds: Dict[str, AccuracyThreshold] = {}
        self.alert_callbacks: List[Callable[[AccuracyAlert], None]] = []
        self.monitoring_active = False
        self.monitoring_task: Optional[asyncio.Task] = None
        self.max_metrics_history = 50000
        self.max_alerts_history = 1000
        
        # Component accuracy tracking
        self.component_accuracy: Dict[str, Dict[str, Any]] = defaultdict(lambda: {
            'current_accuracy': 1.0,
            'trend': [],
            'last_update': None,
            'sample_count': 0,
            'alert_count': 0
        })
        
        # Initialize default thresholds
        self._initialize_default_thresholds()
        
        # Register capabilities
        self.register_capability('accuracy_monitoring', {
            'description': 'Systematic accuracy monitoring with correlation tracking',
            'default_threshold': self.default_threshold,
            'components_monitored': len(self.accuracy_thresholds),
            'monitoring_active': self.monitoring_active
        })
    
    def _initialize_default_thresholds(self):
        """Initialize default accuracy thresholds for components."""
        default_thresholds = [
            # Discovery components
            AccuracyThreshold(
                component='InfrastructureDiscoverer',
                metric_type='discovery',
                critical_threshold=0.85,
                warning_threshold=0.90,
                trend_window_minutes=30
            ),
            AccuracyThreshold(
                component='ServiceDiscoveryScanner',
                metric_type='discovery',
                critical_threshold=0.90,
                warning_threshold=0.95,
                trend_window_minutes=30
            ),
            AccuracyThreshold(
                component='ObservatoryWebSocketClient',
                metric_type='discovery',
                critical_threshold=0.80,
                warning_threshold=0.85,
                trend_window_minutes=15
            ),
            
            # Analysis components
            AccuracyThreshold(
                component='RelationshipMapper',
                metric_type='analysis',
                critical_threshold=0.85,
                warning_threshold=0.90,
                trend_window_minutes=45
            ),
            AccuracyThreshold(
                component='DataFlowMapper',
                metric_type='analysis',
                critical_threshold=0.85,
                warning_threshold=0.90,
                trend_window_minutes=45
            ),
            AccuracyThreshold(
                component='AutomationChainAnalyzer',
                metric_type='analysis',
                critical_threshold=0.80,
                warning_threshold=0.85,
                trend_window_minutes=60
            ),
            
            # Generation components
            AccuracyThreshold(
                component='DiagramGenerator',
                metric_type='generation',
                critical_threshold=0.90,
                warning_threshold=0.95,
                trend_window_minutes=60
            ),
            AccuracyThreshold(
                component='SequenceDiagramGenerator',
                metric_type='generation',
                critical_threshold=0.85,
                warning_threshold=0.90,
                trend_window_minutes=60
            ),
            AccuracyThreshold(
                component='NetworkTopologyVisualizer',
                metric_type='generation',
                critical_threshold=0.85,
                warning_threshold=0.90,
                trend_window_minutes=60
            ),
            
            # Validation components
            AccuracyThreshold(
                component='RealTimeValidator',
                metric_type='validation',
                critical_threshold=0.90,
                warning_threshold=0.95,
                trend_window_minutes=30
            ),
            AccuracyThreshold(
                component='DocumentationOrchestrator',
                metric_type='orchestration',
                critical_threshold=0.85,
                warning_threshold=0.90,
                trend_window_minutes=45
            )
        ]
        
        for threshold in default_thresholds:
            key = f"{threshold.component}:{threshold.metric_type}"
            self.accuracy_thresholds[key] = threshold
    
    async def start_monitoring(self, check_interval_minutes: int = 5) -> Dict[str, Any]:
        """Start accuracy monitoring."""
        try:
            if self.monitoring_active:
                return {'status': 'already_running'}
            
            self.monitoring_active = True
            self.monitoring_task = asyncio.create_task(
                self._monitoring_loop(check_interval_minutes)
            )
            
            self.logger.info(f"Accuracy monitoring started with {check_interval_minutes} minute intervals")
            
            return {
                'status': 'started',
                'check_interval_minutes': check_interval_minutes,
                'thresholds_configured': len(self.accuracy_thresholds),
                'alert_callbacks': len(self.alert_callbacks)
            }
            
        except Exception as e:
            self.logger.error(f"Failed to start accuracy monitoring: {e}")
            return {'status': 'failed', 'error': str(e)}
    
    async def stop_monitoring(self) -> Dict[str, Any]:
        """Stop accuracy monitoring."""
        try:
            self.monitoring_active = False
            
            if self.monitoring_task:
                self.monitoring_task.cancel()
                try:
                    await self.monitoring_task
                except asyncio.CancelledError:
                    pass
                self.monitoring_task = None
            
            self.logger.info("Accuracy monitoring stopped")
            return {'status': 'stopped'}
            
        except Exception as e:
            self.logger.error(f"Error stopping accuracy monitoring: {e}")
            return {'status': 'error', 'error': str(e)}
    
    async def _monitoring_loop(self, check_interval_minutes: int):
        """Main monitoring loop."""
        while self.monitoring_active:
            try:
                # Analyze accuracy trends
                await self._analyze_accuracy_trends()
                
                # Check for threshold breaches
                await self._check_threshold_breaches()
                
                # Clean up old data
                await self._cleanup_old_data()
                
                # Wait for next check
                await asyncio.sleep(check_interval_minutes * 60)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Error in accuracy monitoring loop: {e}")
                await asyncio.sleep(60)  # Wait 1 minute before retrying
    
    async def record_accuracy_metric(self, component: str, metric_type: str, 
                                   accuracy_score: float, correlation_id: Optional[str] = None,
                                   details: Optional[Dict[str, Any]] = None,
                                   confidence_level: float = 1.0) -> str:
        """Record an accuracy metric."""
        try:
            metric_id = f"{component}_{metric_type}_{int(time.time())}"
            
            metric = AccuracyMetric(
                metric_id=metric_id,
                component=component,
                metric_type=metric_type,
                accuracy_score=max(0.0, min(1.0, accuracy_score)),  # Clamp to [0,1]
                timestamp=datetime.now(),
                correlation_id=correlation_id,
                details=details or {},
                confidence_level=max(0.0, min(1.0, confidence_level))
            )
            
            # Add to metrics history
            self.accuracy_metrics.append(metric)
            
            # Update component tracking
            self._update_component_accuracy(component, metric)
            
            # Check for immediate threshold breach
            await self._check_immediate_threshold_breach(metric)
            
            # Trim history if needed
            if len(self.accuracy_metrics) > self.max_metrics_history:
                self.accuracy_metrics = self.accuracy_metrics[-self.max_metrics_history:]
            
            self.logger.debug(f"Recorded accuracy metric: {component} = {accuracy_score:.3f}")
            
            return metric_id
            
        except Exception as e:
            self.logger.error(f"Error recording accuracy metric: {e}")
            return ""
    
    def _update_component_accuracy(self, component: str, metric: AccuracyMetric):
        """Update component accuracy tracking."""
        comp_data = self.component_accuracy[component]
        
        # Update current accuracy (weighted average with confidence)
        if comp_data['sample_count'] == 0:
            comp_data['current_accuracy'] = metric.accuracy_score
        else:
            # Weighted average based on confidence levels
            weight = metric.confidence_level
            current_weight = comp_data.get('total_confidence', 1.0)
            total_weight = current_weight + weight
            
            comp_data['current_accuracy'] = (
                (comp_data['current_accuracy'] * current_weight + 
                 metric.accuracy_score * weight) / total_weight
            )
            comp_data['total_confidence'] = total_weight
        
        # Add to trend
        comp_data['trend'].append({
            'timestamp': metric.timestamp.isoformat(),
            'accuracy': metric.accuracy_score,
            'confidence': metric.confidence_level
        })
        
        # Keep only recent trend data (last 24 hours)
        cutoff_time = datetime.now() - timedelta(hours=24)
        comp_data['trend'] = [
            t for t in comp_data['trend'] 
            if datetime.fromisoformat(t['timestamp']) > cutoff_time
        ]
        
        comp_data['last_update'] = metric.timestamp.isoformat()
        comp_data['sample_count'] += 1
    
    async def _check_immediate_threshold_breach(self, metric: AccuracyMetric):
        """Check for immediate threshold breach."""
        threshold_key = f"{metric.component}:{metric.metric_type}"
        
        if threshold_key in self.accuracy_thresholds:
            threshold = self.accuracy_thresholds[threshold_key]
            
            # Check critical threshold
            if metric.accuracy_score < threshold.critical_threshold:
                await self._create_alert(
                    alert_type='threshold_breach',
                    severity='critical',
                    component=metric.component,
                    current_accuracy=metric.accuracy_score,
                    threshold=threshold.critical_threshold,
                    correlation_id=metric.correlation_id,
                    message=f"Critical accuracy threshold breached: {metric.accuracy_score:.3f} < {threshold.critical_threshold:.3f}"
                )
            
            # Check warning threshold
            elif metric.accuracy_score < threshold.warning_threshold:
                await self._create_alert(
                    alert_type='threshold_breach',
                    severity='warning',
                    component=metric.component,
                    current_accuracy=metric.accuracy_score,
                    threshold=threshold.warning_threshold,
                    correlation_id=metric.correlation_id,
                    message=f"Warning accuracy threshold breached: {metric.accuracy_score:.3f} < {threshold.warning_threshold:.3f}"
                )
    
    async def _analyze_accuracy_trends(self):
        """Analyze accuracy trends for all components."""
        for component, comp_data in self.component_accuracy.items():
            try:
                await self._analyze_component_trend(component, comp_data)
            except Exception as e:
                self.logger.error(f"Error analyzing trend for {component}: {e}")
    
    async def _analyze_component_trend(self, component: str, comp_data: Dict[str, Any]):
        """Analyze accuracy trend for a specific component."""
        trend_data = comp_data['trend']
        
        if len(trend_data) < 3:  # Need at least 3 points for trend analysis
            return
        
        # Get threshold for this component
        threshold_key = None
        for key in self.accuracy_thresholds:
            if key.startswith(f"{component}:"):
                threshold_key = key
                break
        
        if not threshold_key:
            return
        
        threshold = self.accuracy_thresholds[threshold_key]
        
        # Analyze trend within the specified window
        cutoff_time = datetime.now() - timedelta(minutes=threshold.trend_window_minutes)
        recent_trend = [
            t for t in trend_data 
            if datetime.fromisoformat(t['timestamp']) > cutoff_time
        ]
        
        if len(recent_trend) < threshold.min_samples:
            return
        
        # Calculate trend slope
        accuracies = [t['accuracy'] for t in recent_trend]
        timestamps = [datetime.fromisoformat(t['timestamp']).timestamp() for t in recent_trend]
        
        if len(accuracies) >= 2:
            # Simple linear regression for trend
            n = len(accuracies)
            sum_x = sum(timestamps)
            sum_y = sum(accuracies)
            sum_xy = sum(x * y for x, y in zip(timestamps, accuracies))
            sum_x2 = sum(x * x for x in timestamps)
            
            # Calculate slope
            denominator = n * sum_x2 - sum_x * sum_x
            if denominator != 0:
                slope = (n * sum_xy - sum_x * sum_y) / denominator
                
                # Check for declining trend (negative slope)
                if slope < -0.001:  # Significant decline
                    current_accuracy = comp_data['current_accuracy']
                    
                    # Predict accuracy in next window
                    time_delta = threshold.trend_window_minutes * 60
                    predicted_accuracy = current_accuracy + (slope * time_delta)
                    
                    # Alert if predicted accuracy will breach threshold
                    if predicted_accuracy < threshold.warning_threshold:
                        severity = 'critical' if predicted_accuracy < threshold.critical_threshold else 'warning'
                        
                        await self._create_alert(
                            alert_type='trend_decline',
                            severity=severity,
                            component=component,
                            current_accuracy=current_accuracy,
                            threshold=threshold.warning_threshold,
                            message=f"Declining accuracy trend detected. Current: {current_accuracy:.3f}, Predicted: {predicted_accuracy:.3f}"
                        )
    
    async def _check_threshold_breaches(self):
        """Check for threshold breaches across all components."""
        for component, comp_data in self.component_accuracy.items():
            try:
                current_accuracy = comp_data['current_accuracy']
                
                # Find threshold for this component
                threshold_key = None
                for key in self.accuracy_thresholds:
                    if key.startswith(f"{component}:"):
                        threshold_key = key
                        break
                
                if threshold_key:
                    threshold = self.accuracy_thresholds[threshold_key]
                    
                    # Check if we need to alert (avoid duplicate alerts)
                    recent_alerts = [
                        a for a in self.accuracy_alerts[-10:] 
                        if a.component == component and 
                           a.timestamp > datetime.now() - timedelta(minutes=30) and
                           not a.resolved
                    ]
                    
                    if not recent_alerts:
                        if current_accuracy < threshold.critical_threshold:
                            await self._create_alert(
                                alert_type='threshold_breach',
                                severity='critical',
                                component=component,
                                current_accuracy=current_accuracy,
                                threshold=threshold.critical_threshold,
                                message=f"Component accuracy below critical threshold"
                            )
                        elif current_accuracy < threshold.warning_threshold:
                            await self._create_alert(
                                alert_type='threshold_breach',
                                severity='warning',
                                component=component,
                                current_accuracy=current_accuracy,
                                threshold=threshold.warning_threshold,
                                message=f"Component accuracy below warning threshold"
                            )
            
            except Exception as e:
                self.logger.error(f"Error checking thresholds for {component}: {e}")
    
    async def _create_alert(self, alert_type: str, severity: str, component: str,
                          current_accuracy: float, threshold: float,
                          correlation_id: Optional[str] = None, message: str = ""):
        """Create an accuracy alert."""
        try:
            alert_id = f"{component}_{alert_type}_{int(time.time())}"
            
            alert = AccuracyAlert(
                alert_id=alert_id,
                alert_type=alert_type,
                severity=severity,
                component=component,
                current_accuracy=current_accuracy,
                threshold=threshold,
                timestamp=datetime.now(),
                correlation_id=correlation_id,
                message=message
            )
            
            # Add to alerts history
            self.accuracy_alerts.append(alert)
            
            # Update component alert count
            self.component_accuracy[component]['alert_count'] += 1
            
            # Log the alert
            log_level = 'error' if severity == 'critical' else 'warning'
            getattr(self.logger, log_level)(
                f"Accuracy alert [{severity.upper()}]: {component} - {message}"
            )
            
            # Notify callbacks
            for callback in self.alert_callbacks:
                try:
                    if asyncio.iscoroutinefunction(callback):
                        await callback(alert)
                    else:
                        callback(alert)
                except Exception as e:
                    self.logger.error(f"Error in alert callback: {e}")
            
            # Trim alerts history if needed
            if len(self.accuracy_alerts) > self.max_alerts_history:
                self.accuracy_alerts = self.accuracy_alerts[-self.max_alerts_history:]
            
            return alert_id
            
        except Exception as e:
            self.logger.error(f"Error creating alert: {e}")
            return ""
    
    async def resolve_alert(self, alert_id: str, resolution_message: str = "") -> bool:
        """Resolve an accuracy alert."""
        try:
            for alert in self.accuracy_alerts:
                if alert.alert_id == alert_id and not alert.resolved:
                    alert.resolved = True
                    alert.resolution_timestamp = datetime.now()
                    if resolution_message:
                        alert.message += f" | Resolved: {resolution_message}"
                    
                    self.logger.info(f"Resolved accuracy alert: {alert_id}")
                    return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"Error resolving alert {alert_id}: {e}")
            return False
    
    async def _cleanup_old_data(self):
        """Clean up old metrics and alerts."""
        try:
            # Remove metrics older than 7 days
            cutoff_time = datetime.now() - timedelta(days=7)
            self.accuracy_metrics = [
                m for m in self.accuracy_metrics 
                if m.timestamp > cutoff_time
            ]
            
            # Remove resolved alerts older than 30 days
            alert_cutoff_time = datetime.now() - timedelta(days=30)
            self.accuracy_alerts = [
                a for a in self.accuracy_alerts 
                if not a.resolved or a.timestamp > alert_cutoff_time
            ]
            
        except Exception as e:
            self.logger.error(f"Error cleaning up old data: {e}")
    
    def add_alert_callback(self, callback: Callable[[AccuracyAlert], None]):
        """Add a callback function to be called when alerts are created."""
        self.alert_callbacks.append(callback)
    
    def remove_alert_callback(self, callback: Callable[[AccuracyAlert], None]):
        """Remove an alert callback."""
        if callback in self.alert_callbacks:
            self.alert_callbacks.remove(callback)
    
    def set_component_threshold(self, component: str, metric_type: str,
                              critical_threshold: float, warning_threshold: float,
                              trend_window_minutes: int = 60, min_samples: int = 5):
        """Set accuracy threshold for a component."""
        threshold = AccuracyThreshold(
            component=component,
            metric_type=metric_type,
            critical_threshold=critical_threshold,
            warning_threshold=warning_threshold,
            trend_window_minutes=trend_window_minutes,
            min_samples=min_samples
        )
        
        key = f"{component}:{metric_type}"
        self.accuracy_thresholds[key] = threshold
        
        self.logger.info(f"Set threshold for {key}: critical={critical_threshold}, warning={warning_threshold}")
    
    def get_component_accuracy(self, component: Optional[str] = None) -> Dict[str, Any]:
        """Get accuracy data for a component or all components."""
        if component:
            if component in self.component_accuracy:
                return dict(self.component_accuracy[component])
            else:
                return {}
        else:
            return {comp: dict(data) for comp, data in self.component_accuracy.items()}
    
    def get_accuracy_metrics(self, component: Optional[str] = None, 
                           metric_type: Optional[str] = None,
                           limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get accuracy metrics with optional filtering."""
        metrics = self.accuracy_metrics
        
        # Filter by component
        if component:
            metrics = [m for m in metrics if m.component == component]
        
        # Filter by metric type
        if metric_type:
            metrics = [m for m in metrics if m.metric_type == metric_type]
        
        # Apply limit
        if limit:
            metrics = metrics[-limit:]
        
        return [asdict(metric) for metric in metrics]
    
    def get_accuracy_alerts(self, component: Optional[str] = None,
                          severity: Optional[str] = None,
                          resolved: Optional[bool] = None,
                          limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get accuracy alerts with optional filtering."""
        alerts = self.accuracy_alerts
        
        # Filter by component
        if component:
            alerts = [a for a in alerts if a.component == component]
        
        # Filter by severity
        if severity:
            alerts = [a for a in alerts if a.severity == severity]
        
        # Filter by resolved status
        if resolved is not None:
            alerts = [a for a in alerts if a.resolved == resolved]
        
        # Apply limit
        if limit:
            alerts = alerts[-limit:]
        
        return [asdict(alert) for alert in alerts]
    
    def get_accuracy_summary(self) -> Dict[str, Any]:
        """Get overall accuracy summary."""
        if not self.component_accuracy:
            return {
                'overall_accuracy': 1.0,
                'components_monitored': 0,
                'total_metrics': 0,
                'active_alerts': 0
            }
        
        # Calculate overall accuracy (weighted by sample count)
        total_weighted_accuracy = 0.0
        total_samples = 0
        
        for comp_data in self.component_accuracy.values():
            sample_count = comp_data['sample_count']
            if sample_count > 0:
                total_weighted_accuracy += comp_data['current_accuracy'] * sample_count
                total_samples += sample_count
        
        overall_accuracy = total_weighted_accuracy / total_samples if total_samples > 0 else 1.0
        
        # Count active alerts
        active_alerts = len([a for a in self.accuracy_alerts if not a.resolved])
        
        # Get component breakdown
        component_breakdown = {}
        for component, comp_data in self.component_accuracy.items():
            component_breakdown[component] = {
                'accuracy': comp_data['current_accuracy'],
                'sample_count': comp_data['sample_count'],
                'alert_count': comp_data['alert_count'],
                'last_update': comp_data['last_update']
            }
        
        return {
            'overall_accuracy': overall_accuracy,
            'components_monitored': len(self.component_accuracy),
            'total_metrics': len(self.accuracy_metrics),
            'active_alerts': active_alerts,
            'monitoring_active': self.monitoring_active,
            'component_breakdown': component_breakdown
        }
    
    def get_accuracy_statistics(self) -> Dict[str, Any]:
        """Get detailed accuracy statistics."""
        if not self.accuracy_metrics:
            return {'no_data': True}
        
        # Overall statistics
        all_scores = [m.accuracy_score for m in self.accuracy_metrics]
        
        stats = {
            'total_metrics': len(all_scores),
            'mean_accuracy': statistics.mean(all_scores),
            'median_accuracy': statistics.median(all_scores),
            'min_accuracy': min(all_scores),
            'max_accuracy': max(all_scores),
            'std_deviation': statistics.stdev(all_scores) if len(all_scores) > 1 else 0.0
        }
        
        # Component-wise statistics
        component_stats = {}
        for component in set(m.component for m in self.accuracy_metrics):
            component_scores = [m.accuracy_score for m in self.accuracy_metrics if m.component == component]
            if component_scores:
                component_stats[component] = {
                    'count': len(component_scores),
                    'mean': statistics.mean(component_scores),
                    'median': statistics.median(component_scores),
                    'min': min(component_scores),
                    'max': max(component_scores),
                    'std_dev': statistics.stdev(component_scores) if len(component_scores) > 1 else 0.0
                }
        
        stats['component_statistics'] = component_stats
        
        # Metric type statistics
        type_stats = {}
        for metric_type in set(m.metric_type for m in self.accuracy_metrics):
            type_scores = [m.accuracy_score for m in self.accuracy_metrics if m.metric_type == metric_type]
            if type_scores:
                type_stats[metric_type] = {
                    'count': len(type_scores),
                    'mean': statistics.mean(type_scores),
                    'median': statistics.median(type_scores)
                }
        
        stats['metric_type_statistics'] = type_stats
        
        return stats
    
    # ReflectiveModule health endpoints
    async def health_check(self) -> Dict[str, Any]:
        """Health check endpoint."""
        summary = self.get_accuracy_summary()
        
        return {
            'status': 'healthy',
            'monitoring_active': self.monitoring_active,
            'overall_accuracy': summary['overall_accuracy'],
            'active_alerts': summary['active_alerts'],
            'components_monitored': summary['components_monitored']
        }
    
    async def ready_check(self) -> Dict[str, Any]:
        """Readiness check endpoint."""
        return {
            'ready': True,
            'thresholds_configured': len(self.accuracy_thresholds) > 0,
            'monitoring_active': self.monitoring_active
        }
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get accuracy monitoring metrics."""
        summary = self.get_accuracy_summary()
        
        return {
            'accuracy_monitor_overall_accuracy': summary['overall_accuracy'],
            'accuracy_monitor_components_monitored': summary['components_monitored'],
            'accuracy_monitor_total_metrics': summary['total_metrics'],
            'accuracy_monitor_active_alerts': summary['active_alerts'],
            'accuracy_monitor_monitoring_active': 1 if self.monitoring_active else 0,
            'accuracy_monitor_thresholds_configured': len(self.accuracy_thresholds)
        }


# Example usage and testing
if __name__ == "__main__":
    async def main():
        # Create accuracy monitor
        monitor = AccuracyMonitor(default_threshold=0.90)
        
        # Add alert callback
        async def handle_alert(alert: AccuracyAlert):
            print(f"ALERT [{alert.severity}]: {alert.component} - {alert.message}")
        
        monitor.add_alert_callback(handle_alert)
        
        # Start monitoring
        result = await monitor.start_monitoring(check_interval_minutes=1)
        print(f"Monitoring started: {result}")
        
        # Record some metrics
        await monitor.record_accuracy_metric('TestComponent', 'validation', 0.95, 'test-001')
        await monitor.record_accuracy_metric('TestComponent', 'validation', 0.88, 'test-002')  # Should trigger warning
        await monitor.record_accuracy_metric('TestComponent', 'validation', 0.75, 'test-003')  # Should trigger critical
        
        # Wait for monitoring cycle
        await asyncio.sleep(5)
        
        # Get summary
        summary = monitor.get_accuracy_summary()
        print(f"Summary: {summary}")
        
        # Get alerts
        alerts = monitor.get_accuracy_alerts(resolved=False)
        print(f"Active alerts: {len(alerts)}")
        
        # Stop monitoring
        await monitor.stop_monitoring()
    
    asyncio.run(main())