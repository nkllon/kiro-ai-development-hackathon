"""
Metrics Collector - Collect system health metrics
"""

import time
import psutil
import os
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path


@dataclass
class SystemMetrics:
    """System-level metrics"""
    timestamp: datetime
    cpu_percent: float
    memory_percent: float
    disk_usage_percent: float
    load_average: tuple
    process_count: int
    uptime_seconds: float


@dataclass
class MakefileMetrics:
    """Makefile-specific metrics"""
    timestamp: datetime
    makefile_path: str
    health_score: float
    node_count: int
    cycle_count: int
    orphaned_count: int
    dependency_depth: int


@dataclass
class PerformanceMetrics:
    """Performance-related metrics"""
    timestamp: datetime
    analysis_time_ms: float
    fix_time_ms: Optional[float]
    memory_usage_mb: float
    cpu_usage_percent: float


class MetricsCollector:
    """Collects comprehensive system and application metrics"""
    
    def __init__(self):
        self.metrics_history: List[Dict[str, Any]] = []
        self.start_time = time.time()
        
    def collect_system_metrics(self) -> SystemMetrics:
        """Collect current system metrics"""
        try:
            cpu_percent = psutil.cpu_percent(interval=0.1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            # Get load average (Unix-like systems)
            try:
                load_avg = os.getloadavg()
            except AttributeError:
                load_avg = (0.0, 0.0, 0.0)
            
            process_count = len(psutil.pids())
            uptime = time.time() - self.start_time
            
            return SystemMetrics(
                timestamp=datetime.now(),
                cpu_percent=cpu_percent,
                memory_percent=memory.percent,
                disk_usage_percent=disk.percent,
                load_average=load_avg,
                process_count=process_count,
                uptime_seconds=uptime
            )
        except Exception as e:
            print(f"Error collecting system metrics: {e}")
            return self._get_default_system_metrics()
    
    def collect_makefile_metrics(self, makefile_path: str, 
                               health_score: float, node_count: int,
                               cycle_count: int, orphaned_count: int,
                               dependency_depth: int) -> MakefileMetrics:
        """Collect Makefile-specific metrics"""
        return MakefileMetrics(
            timestamp=datetime.now(),
            makefile_path=makefile_path,
            health_score=health_score,
            node_count=node_count,
            cycle_count=cycle_count,
            orphaned_count=orphaned_count,
            dependency_depth=dependency_depth
        )
    
    def collect_performance_metrics(self, analysis_time_ms: float,
                                  fix_time_ms: Optional[float] = None) -> PerformanceMetrics:
        """Collect performance metrics for operations"""
        process = psutil.Process()
        
        return PerformanceMetrics(
            timestamp=datetime.now(),
            analysis_time_ms=analysis_time_ms,
            fix_time_ms=fix_time_ms,
            memory_usage_mb=process.memory_info().rss / 1024 / 1024,
            cpu_usage_percent=process.cpu_percent()
        )
    
    def store_metrics(self, metrics: Any) -> None:
        """Store metrics in history"""
        metrics_dict = asdict(metrics) if hasattr(metrics, '__dataclass_fields__') else metrics
        metrics_dict['timestamp'] = metrics_dict['timestamp'].isoformat() if isinstance(metrics_dict.get('timestamp'), datetime) else metrics_dict.get('timestamp')
        
        self.metrics_history.append(metrics_dict)
        
        # Keep only last 1000 entries to prevent memory issues
        if len(self.metrics_history) > 1000:
            self.metrics_history = self.metrics_history[-1000:]
    
    def get_metrics_summary(self, time_window_minutes: int = 60) -> Dict[str, Any]:
        """Get summary of metrics over time window"""
        if not self.metrics_history:
            return {"error": "No metrics available"}
        
        cutoff_time = time.time() - (time_window_minutes * 60)
        
        # Filter metrics within time window
        recent_metrics = []
        for metric in self.metrics_history:
            try:
                if isinstance(metric.get('timestamp'), str):
                    metric_time = datetime.fromisoformat(metric['timestamp']).timestamp()
                else:
                    metric_time = metric.get('timestamp', 0)
                    
                if metric_time >= cutoff_time:
                    recent_metrics.append(metric)
            except:
                continue
        
        if not recent_metrics:
            return {"error": f"No metrics in last {time_window_minutes} minutes"}
        
        # Calculate summary statistics
        summary = {
            "time_window_minutes": time_window_minutes,
            "total_metrics": len(recent_metrics),
            "metrics_types": {}
        }
        
        # Group by metric type
        metric_types = {}
        for metric in recent_metrics:
            metric_type = metric.get('__class__', 'unknown')
            if metric_type not in metric_types:
                metric_types[metric_type] = []
            metric_types[metric_type].append(metric)
        
        # Calculate statistics for each type
        for metric_type, metrics in metric_types.items():
            if metric_type == 'SystemMetrics':
                summary["metrics_types"]["system"] = self._summarize_system_metrics(metrics)
            elif metric_type == 'MakefileMetrics':
                summary["metrics_types"]["makefile"] = self._summarize_makefile_metrics(metrics)
            elif metric_type == 'PerformanceMetrics':
                summary["metrics_types"]["performance"] = self._summarize_performance_metrics(metrics)
        
        return summary
    
    def _summarize_system_metrics(self, metrics: List[Dict]) -> Dict[str, Any]:
        """Summarize system metrics"""
        if not metrics:
            return {}
        
        cpu_values = [m.get('cpu_percent', 0) for m in metrics]
        memory_values = [m.get('memory_percent', 0) for m in metrics]
        disk_values = [m.get('disk_usage_percent', 0) for m in metrics]
        
        return {
            "cpu_percent": {
                "avg": sum(cpu_values) / len(cpu_values),
                "max": max(cpu_values),
                "min": min(cpu_values)
            },
            "memory_percent": {
                "avg": sum(memory_values) / len(memory_values),
                "max": max(memory_values),
                "min": min(memory_values)
            },
            "disk_usage_percent": {
                "avg": sum(disk_values) / len(disk_values),
                "max": max(disk_values),
                "min": min(disk_values)
            },
            "sample_count": len(metrics)
        }
    
    def _summarize_makefile_metrics(self, metrics: List[Dict]) -> Dict[str, Any]:
        """Summarize Makefile metrics"""
        if not metrics:
            return {}
        
        health_scores = [m.get('health_score', 0) for m in metrics]
        node_counts = [m.get('node_count', 0) for m in metrics]
        cycle_counts = [m.get('cycle_count', 0) for m in metrics]
        
        return {
            "health_score": {
                "avg": sum(health_scores) / len(health_scores),
                "max": max(health_scores),
                "min": min(health_scores)
            },
            "node_count": {
                "avg": sum(node_counts) / len(node_counts),
                "max": max(node_counts),
                "min": min(node_counts)
            },
            "cycle_count": {
                "total": sum(cycle_counts),
                "max": max(cycle_counts),
                "files_with_cycles": sum(1 for c in cycle_counts if c > 0)
            },
            "sample_count": len(metrics)
        }
    
    def _summarize_performance_metrics(self, metrics: List[Dict]) -> Dict[str, Any]:
        """Summarize performance metrics"""
        if not metrics:
            return {}
        
        analysis_times = [m.get('analysis_time_ms', 0) for m in metrics]
        fix_times = [m.get('fix_time_ms', 0) for m in metrics if m.get('fix_time_ms')]
        memory_usage = [m.get('memory_usage_mb', 0) for m in metrics]
        
        summary = {
            "analysis_time_ms": {
                "avg": sum(analysis_times) / len(analysis_times),
                "max": max(analysis_times),
                "min": min(analysis_times)
            },
            "memory_usage_mb": {
                "avg": sum(memory_usage) / len(memory_usage),
                "max": max(memory_usage),
                "min": min(memory_usage)
            },
            "sample_count": len(metrics)
        }
        
        if fix_times:
            summary["fix_time_ms"] = {
                "avg": sum(fix_times) / len(fix_times),
                "max": max(fix_times),
                "min": min(fix_times)
            }
        
        return summary
    
    def export_metrics(self, output_path: str) -> bool:
        """Export all metrics to file"""
        try:
            import json
            
            export_data = {
                "export_timestamp": datetime.now().isoformat(),
                "total_metrics": len(self.metrics_history),
                "metrics": self.metrics_history
            }
            
            with open(output_path, 'w') as f:
                json.dump(export_data, f, indent=2)
            
            return True
            
        except Exception as e:
            print(f"Error exporting metrics: {e}")
            return False
    
    def _get_default_system_metrics(self) -> SystemMetrics:
        """Get default system metrics when collection fails"""
        return SystemMetrics(
            timestamp=datetime.now(),
            cpu_percent=0.0,
            memory_percent=0.0,
            disk_usage_percent=0.0,
            load_average=(0.0, 0.0, 0.0),
            process_count=0,
            uptime_seconds=time.time() - self.start_time
        )
