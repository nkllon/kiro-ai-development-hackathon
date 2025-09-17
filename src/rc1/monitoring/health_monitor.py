"""
Health Monitor - Real-time system health tracking

TRACE: REQ-RC1-RDI-003, REQ-RC1-RMDDD-003
TEST: tests/rc1/test_rdi_simple.py
IMPLEMENTATION: Real-time system health monitoring system
"""

import time
import threading
from typing import Dict, List, Any, Optional, Callable
from datetime import datetime, timedelta

from .metrics_collector import MetricsCollector, SystemMetrics, MakefileMetrics, PerformanceMetrics
from .alert_system import AlertSystem, Alert, AlertLevel
from ..foundation.makefile_health_manager import MakefileHealthManager


class HealthMonitor:
    """
    Real-time system health monitoring with continuous analysis
    
    TRACE: REQ-RC1-RDI-003, REQ-RC1-RMDDD-003
    TEST: tests/rc1/test_rdi_simple.py
    IMPLEMENTATION: Real-time system health monitoring system
    """
    
    def __init__(self, monitoring_interval: int = 30):
        self.monitoring_interval = monitoring_interval
        self.metrics_collector = MetricsCollector()
        self.alert_system = AlertSystem()
        self.makefile_manager = MakefileHealthManager()
        
        self.monitoring_active = False
        self.monitoring_thread: Optional[threading.Thread] = None
        self.callbacks: List[Callable[[Alert], None]] = []
        
        # Monitoring configuration
        self.monitor_makefiles = True
        self.monitor_system_resources = True
        self.monitor_performance = True
        
    def start_monitoring(self) -> bool:
        """
        Start continuous health monitoring
        
        Returns:
            True if monitoring started successfully
        """
        if self.monitoring_active:
            print("⚠️ Monitoring is already active")
            return False
        
        self.monitoring_active = True
        self.monitoring_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
        self.monitoring_thread.start()
        
        print(f"🚀 Health monitoring started (interval: {self.monitoring_interval}s)")
        return True
    
    def stop_monitoring(self) -> bool:
        """
        Stop continuous health monitoring
        
        Returns:
            True if monitoring stopped successfully
        """
        if not self.monitoring_active:
            print("⚠️ Monitoring is not active")
            return False
        
        self.monitoring_active = False
        
        if self.monitoring_thread and self.monitoring_thread.is_alive():
            self.monitoring_thread.join(timeout=5)
        
        print("🛑 Health monitoring stopped")
        return True
    
    def add_alert_callback(self, callback: Callable[[Alert], None]) -> None:
        """Add callback function for alert notifications"""
        self.callbacks.append(callback)
    
    def remove_alert_callback(self, callback: Callable[[Alert], None]) -> bool:
        """Remove alert callback function"""
        try:
            self.callbacks.remove(callback)
            return True
        except ValueError:
            return False
    
    def get_current_health_status(self) -> Dict[str, Any]:
        """
        Get current system health status
        
        Returns:
            Dictionary with current health metrics and alerts
        """
        status = {
            "timestamp": datetime.now().isoformat(),
            "monitoring_active": self.monitoring_active,
            "metrics": {},
            "alerts": {},
            "makefiles": {}
        }
        
        # Collect current system metrics
        if self.monitor_system_resources:
            system_metrics = self.metrics_collector.collect_system_metrics()
            self.metrics_collector.store_metrics(system_metrics)
            status["metrics"]["system"] = {
                "cpu_percent": system_metrics.cpu_percent,
                "memory_percent": system_metrics.memory_percent,
                "disk_usage_percent": system_metrics.disk_usage_percent,
                "load_average": system_metrics.load_average,
                "process_count": system_metrics.process_count,
                "uptime_seconds": system_metrics.uptime_seconds
            }
        
        # Check makefile health
        if self.monitor_makefiles:
            makefiles = self.makefile_manager.discover_makefiles('.')
            makefile_status = []
            
            for makefile in makefiles[:5]:  # Limit to first 5 for performance
                start_time = time.time()
                result = self.makefile_manager.diagnose_makefile(makefile)
                analysis_time = (time.time() - start_time) * 1000
                
                makefile_info = {
                    "path": makefile,
                    "health_score": result.overall_health_score,
                    "status": result.status,
                    "analysis_time_ms": analysis_time
                }
                
                if result.dag_analysis:
                    makefile_info.update({
                        "node_count": len(result.dag_analysis.nodes),
                        "cycle_count": len(result.dag_analysis.cycles),
                        "orphaned_count": len(result.dag_analysis.orphaned_nodes)
                    })
                
                makefile_status.append(makefile_info)
                
                # Store metrics
                if result.dag_analysis:
                    makefile_metrics = self.metrics_collector.collect_makefile_metrics(
                        makefile, result.overall_health_score,
                        len(result.dag_analysis.nodes),
                        len(result.dag_analysis.cycles),
                        len(result.dag_analysis.orphaned_nodes),
                        0  # TODO: Calculate dependency depth
                    )
                    self.metrics_collector.store_metrics(makefile_metrics)
                
                performance_metrics = self.metrics_collector.collect_performance_metrics(analysis_time)
                self.metrics_collector.store_metrics(performance_metrics)
            
            status["makefiles"] = makefile_status
        
        # Check for alerts
        all_metrics = self._get_all_current_metrics()
        new_alerts = self.alert_system.check_alerts(all_metrics)
        
        # Notify callbacks of new alerts
        for alert in new_alerts:
            for callback in self.callbacks:
                try:
                    callback(alert)
                except Exception as e:
                    print(f"Error in alert callback: {e}")
        
        # Get alert summary
        alert_summary = self.alert_system.get_alert_summary()
        status["alerts"] = alert_summary
        
        return status
    
    def get_health_history(self, time_window_minutes: int = 60) -> Dict[str, Any]:
        """
        Get health history over time window
        
        Args:
            time_window_minutes: Time window in minutes
            
        Returns:
            Dictionary with historical health data
        """
        return {
            "time_window_minutes": time_window_minutes,
            "metrics_summary": self.metrics_collector.get_metrics_summary(time_window_minutes),
            "alert_statistics": self.alert_system.get_alert_statistics(time_window_minutes // 60)
        }
    
    def export_health_data(self, output_path: str) -> bool:
        """
        Export comprehensive health data
        
        Args:
            output_path: Path to save the data
            
        Returns:
            True if successful
        """
        try:
            import json
            
            health_data = {
                "export_timestamp": datetime.now().isoformat(),
                "current_status": self.get_current_health_status(),
                "history": self.get_health_history(60),
                "metrics_export": self.metrics_collector.metrics_history,
                "alerts_export": [alert.__dict__ for alert in self.alert_system.alert_history]
            }
            
            with open(output_path, 'w') as f:
                json.dump(health_data, f, indent=2, default=str)
            
            return True
            
        except Exception as e:
            print(f"Error exporting health data: {e}")
            return False
    
    def set_monitoring_interval(self, interval_seconds: int) -> None:
        """Set monitoring interval"""
        self.monitoring_interval = max(10, interval_seconds)  # Minimum 10 seconds
        print(f"📊 Monitoring interval set to {self.monitoring_interval} seconds")
    
    def configure_monitoring(self, monitor_makefiles: bool = True,
                           monitor_system_resources: bool = True,
                           monitor_performance: bool = True) -> None:
        """Configure what to monitor"""
        self.monitor_makefiles = monitor_makefiles
        self.monitor_system_resources = monitor_system_resources
        self.monitor_performance = monitor_performance
        
        print(f"⚙️ Monitoring configuration updated:")
        print(f"  - Makefiles: {'✅' if monitor_makefiles else '❌'}")
        print(f"  - System Resources: {'✅' if monitor_system_resources else '❌'}")
        print(f"  - Performance: {'✅' if monitor_performance else '❌'}")
    
    def _monitoring_loop(self) -> None:
        """Main monitoring loop"""
        print("🔄 Starting monitoring loop...")
        
        while self.monitoring_active:
            try:
                # Get current health status (this triggers metric collection and alert checking)
                self.get_current_health_status()
                
                # Sleep until next monitoring cycle
                time.sleep(self.monitoring_interval)
                
            except Exception as e:
                print(f"Error in monitoring loop: {e}")
                time.sleep(self.monitoring_interval)  # Continue monitoring despite errors
    
    def _get_all_current_metrics(self) -> Dict[str, Any]:
        """Get all current metrics for alert checking"""
        metrics = {}
        
        # Get latest system metrics
        if self.monitor_system_resources:
            system_metrics = self.metrics_collector.collect_system_metrics()
            metrics.update({
                'cpu_percent': system_metrics.cpu_percent,
                'memory_percent': system_metrics.memory_percent,
                'disk_usage_percent': system_metrics.disk_usage_percent,
                'process_count': system_metrics.process_count
            })
        
        # Get latest makefile metrics
        if self.monitor_makefiles:
            makefiles = self.makefile_manager.discover_makefiles('.')
            if makefiles:
                # Get health of first makefile as representative
                result = self.makefile_manager.diagnose_makefile(makefiles[0])
                metrics.update({
                    'health_score': result.overall_health_score,
                    'cycle_count': len(result.dag_analysis.cycles) if result.dag_analysis else 0
                })
        
        # Get latest performance metrics
        if self.monitor_performance:
            # Use a small analysis to get performance metrics
            start_time = time.time()
            self.makefile_manager.discover_makefiles('.')
            analysis_time = (time.time() - start_time) * 1000
            
            performance_metrics = self.metrics_collector.collect_performance_metrics(analysis_time)
            metrics.update({
                'analysis_time_ms': analysis_time,
                'memory_usage_mb': performance_metrics.memory_usage_mb,
                'cpu_usage_percent': performance_metrics.cpu_usage_percent
            })
        
        return metrics
