"""
Monitoring and observability system for GitHub synchronization.

This module provides comprehensive metrics collection, structured logging,
and performance monitoring for the GitHub sync system.
"""

import json
import logging
import time
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass, field, asdict
from collections import defaultdict, deque
from threading import Lock
import sqlite3
from pathlib import Path

logger = logging.getLogger(__name__)


@dataclass
class SyncMetrics:
    """Metrics for a synchronization operation."""
    repository: str
    operation: str  # sync_issues, sync_prs, sync_commits, etc.
    start_time: datetime
    end_time: Optional[datetime] = None
    duration_seconds: Optional[float] = None
    items_processed: int = 0
    items_created: int = 0
    items_updated: int = 0
    items_skipped: int = 0
    api_calls_made: int = 0
    rate_limit_hits: int = 0
    errors_encountered: int = 0
    success: bool = True
    error_message: Optional[str] = None
    
    def finish(self, success: bool = True, error_message: Optional[str] = None) -> None:
        """Mark the operation as finished."""
        self.end_time = datetime.utcnow()
        self.duration_seconds = (self.end_time - self.start_time).total_seconds()
        self.success = success
        self.error_message = error_message


@dataclass
class APIMetrics:
    """Metrics for GitHub API usage."""
    endpoint: str
    method: str
    status_code: int
    response_time_ms: float
    timestamp: datetime
    rate_limit_remaining: Optional[int] = None
    rate_limit_reset: Optional[datetime] = None
    error_message: Optional[str] = None


@dataclass
class SystemMetrics:
    """System-wide metrics."""
    timestamp: datetime
    active_syncs: int = 0
    total_repositories: int = 0
    total_issues: int = 0
    total_pull_requests: int = 0
    total_commits: int = 0
    cache_size_mb: float = 0.0
    memory_usage_mb: float = 0.0
    cpu_usage_percent: float = 0.0


class StructuredLogger:
    """
    Structured logger for GitHub synchronization operations.
    
    This logger provides JSON-formatted logging with correlation IDs
    and contextual information for better observability.
    """
    
    def __init__(self, name: str, log_file: Optional[Path] = None):
        """
        Initialize structured logger.
        
        Args:
            name: Logger name
            log_file: Optional log file path
        """
        self.logger = logging.getLogger(name)
        self.correlation_id = None
        self.context = {}
        
        # Set up JSON formatter
        if log_file:
            handler = logging.FileHandler(log_file)
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
    
    def set_correlation_id(self, correlation_id: str) -> None:
        """Set correlation ID for request tracing."""
        self.correlation_id = correlation_id
    
    def set_context(self, **kwargs) -> None:
        """Set context information for logging."""
        self.context.update(kwargs)
    
    def clear_context(self) -> None:
        """Clear context information."""
        self.context.clear()
        self.correlation_id = None
    
    def _format_message(self, message: str, extra: Optional[Dict[str, Any]] = None) -> str:
        """Format message with context and correlation ID."""
        log_data = {
            'message': message,
            'timestamp': datetime.utcnow().isoformat(),
        }
        
        if self.correlation_id:
            log_data['correlation_id'] = self.correlation_id
        
        if self.context:
            log_data['context'] = self.context
        
        if extra:
            log_data['extra'] = extra
        
        return json.dumps(log_data)
    
    def info(self, message: str, **kwargs) -> None:
        """Log info message."""
        self.logger.info(self._format_message(message, kwargs))
    
    def warning(self, message: str, **kwargs) -> None:
        """Log warning message."""
        self.logger.warning(self._format_message(message, kwargs))
    
    def error(self, message: str, **kwargs) -> None:
        """Log error message."""
        self.logger.error(self._format_message(message, kwargs))
    
    def debug(self, message: str, **kwargs) -> None:
        """Log debug message."""
        self.logger.debug(self._format_message(message, kwargs))


class MetricsCollector:
    """
    Comprehensive metrics collection system.
    
    This class collects and stores various metrics about GitHub synchronization
    operations, API usage, and system performance.
    """
    
    def __init__(self, db_path: Optional[Path] = None):
        """
        Initialize metrics collector.
        
        Args:
            db_path: Optional path to SQLite database for metrics storage
        """
        self.db_path = db_path or Path.home() / ".github_sync_metrics.db"
        self.sync_metrics: List[SyncMetrics] = []
        self.api_metrics: deque = deque(maxlen=10000)  # Keep last 10k API calls
        self.system_metrics: deque = deque(maxlen=1440)  # Keep 24 hours of minute-level data
        
        # In-memory counters for real-time metrics
        self.counters = defaultdict(int)
        self.gauges = defaultdict(float)
        self.timers = defaultdict(list)
        
        # Thread safety
        self.lock = Lock()
        
        # Initialize database
        self._init_database()
    
    def _init_database(self) -> None:
        """Initialize SQLite database for metrics storage."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute('''
                    CREATE TABLE IF NOT EXISTS sync_metrics (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        repository TEXT NOT NULL,
                        operation TEXT NOT NULL,
                        start_time TEXT NOT NULL,
                        end_time TEXT,
                        duration_seconds REAL,
                        items_processed INTEGER DEFAULT 0,
                        items_created INTEGER DEFAULT 0,
                        items_updated INTEGER DEFAULT 0,
                        items_skipped INTEGER DEFAULT 0,
                        api_calls_made INTEGER DEFAULT 0,
                        rate_limit_hits INTEGER DEFAULT 0,
                        errors_encountered INTEGER DEFAULT 0,
                        success BOOLEAN DEFAULT TRUE,
                        error_message TEXT
                    )
                ''')
                
                conn.execute('''
                    CREATE TABLE IF NOT EXISTS api_metrics (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        endpoint TEXT NOT NULL,
                        method TEXT NOT NULL,
                        status_code INTEGER NOT NULL,
                        response_time_ms REAL NOT NULL,
                        timestamp TEXT NOT NULL,
                        rate_limit_remaining INTEGER,
                        rate_limit_reset TEXT,
                        error_message TEXT
                    )
                ''')
                
                conn.execute('''
                    CREATE TABLE IF NOT EXISTS system_metrics (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        timestamp TEXT NOT NULL,
                        active_syncs INTEGER DEFAULT 0,
                        total_repositories INTEGER DEFAULT 0,
                        total_issues INTEGER DEFAULT 0,
                        total_pull_requests INTEGER DEFAULT 0,
                        total_commits INTEGER DEFAULT 0,
                        cache_size_mb REAL DEFAULT 0.0,
                        memory_usage_mb REAL DEFAULT 0.0,
                        cpu_usage_percent REAL DEFAULT 0.0
                    )
                ''')
                
                # Create indexes for better query performance
                conn.execute('CREATE INDEX IF NOT EXISTS idx_sync_metrics_repo ON sync_metrics(repository)')
                conn.execute('CREATE INDEX IF NOT EXISTS idx_sync_metrics_time ON sync_metrics(start_time)')
                conn.execute('CREATE INDEX IF NOT EXISTS idx_api_metrics_endpoint ON api_metrics(endpoint)')
                conn.execute('CREATE INDEX IF NOT EXISTS idx_api_metrics_time ON api_metrics(timestamp)')
                conn.execute('CREATE INDEX IF NOT EXISTS idx_system_metrics_time ON system_metrics(timestamp)')
                
                conn.commit()
        except Exception as e:
            logger.error(f"Failed to initialize metrics database: {e}")
    
    def start_sync_operation(self, repository: str, operation: str) -> SyncMetrics:
        """
        Start tracking a synchronization operation.
        
        Args:
            repository: Repository name
            operation: Operation type
            
        Returns:
            SyncMetrics object for tracking
        """
        metrics = SyncMetrics(
            repository=repository,
            operation=operation,
            start_time=datetime.utcnow()
        )
        
        with self.lock:
            self.sync_metrics.append(metrics)
            self.counters[f'sync_started_{operation}'] += 1
            self.gauges['active_syncs'] += 1
        
        return metrics
    
    def finish_sync_operation(self, metrics: SyncMetrics, success: bool = True, 
                            error_message: Optional[str] = None) -> None:
        """
        Finish tracking a synchronization operation.
        
        Args:
            metrics: SyncMetrics object to finish
            success: Whether operation was successful
            error_message: Optional error message
        """
        metrics.finish(success, error_message)
        
        with self.lock:
            self.counters[f'sync_completed_{metrics.operation}'] += 1
            if success:
                self.counters[f'sync_success_{metrics.operation}'] += 1
            else:
                self.counters[f'sync_failure_{metrics.operation}'] += 1
            
            self.gauges['active_syncs'] = max(0, self.gauges['active_syncs'] - 1)
            
            # Add to timers for performance tracking
            if metrics.duration_seconds:
                self.timers[f'sync_duration_{metrics.operation}'].append(metrics.duration_seconds)
        
        # Persist to database
        self._persist_sync_metrics(metrics)
    
    def record_api_call(self, endpoint: str, method: str, status_code: int, 
                       response_time_ms: float, rate_limit_remaining: Optional[int] = None,
                       rate_limit_reset: Optional[datetime] = None, 
                       error_message: Optional[str] = None) -> None:
        """
        Record GitHub API call metrics.
        
        Args:
            endpoint: API endpoint
            method: HTTP method
            status_code: Response status code
            response_time_ms: Response time in milliseconds
            rate_limit_remaining: Remaining rate limit
            rate_limit_reset: Rate limit reset time
            error_message: Optional error message
        """
        api_metrics = APIMetrics(
            endpoint=endpoint,
            method=method,
            status_code=status_code,
            response_time_ms=response_time_ms,
            timestamp=datetime.utcnow(),
            rate_limit_remaining=rate_limit_remaining,
            rate_limit_reset=rate_limit_reset,
            error_message=error_message
        )
        
        with self.lock:
            self.api_metrics.append(api_metrics)
            self.counters[f'api_calls_{method}'] += 1
            self.counters[f'api_status_{status_code}'] += 1
            
            if status_code >= 400:
                self.counters['api_errors'] += 1
            
            if status_code == 429:  # Rate limit
                self.counters['rate_limit_hits'] += 1
            
            # Track response times
            self.timers[f'api_response_time_{endpoint}'].append(response_time_ms)
        
        # Persist to database
        self._persist_api_metrics(api_metrics)
    
    def record_system_metrics(self, system_metrics: SystemMetrics) -> None:
        """
        Record system-wide metrics.
        
        Args:
            system_metrics: System metrics to record
        """
        with self.lock:
            self.system_metrics.append(system_metrics)
            
            # Update gauges
            self.gauges['total_repositories'] = system_metrics.total_repositories
            self.gauges['total_issues'] = system_metrics.total_issues
            self.gauges['total_pull_requests'] = system_metrics.total_pull_requests
            self.gauges['total_commits'] = system_metrics.total_commits
            self.gauges['cache_size_mb'] = system_metrics.cache_size_mb
            self.gauges['memory_usage_mb'] = system_metrics.memory_usage_mb
            self.gauges['cpu_usage_percent'] = system_metrics.cpu_usage_percent
        
        # Persist to database
        self._persist_system_metrics(system_metrics)
    
    def increment_counter(self, name: str, value: int = 1) -> None:
        """Increment a counter metric."""
        with self.lock:
            self.counters[name] += value
    
    def set_gauge(self, name: str, value: float) -> None:
        """Set a gauge metric."""
        with self.lock:
            self.gauges[name] = value
    
    def record_timer(self, name: str, value: float) -> None:
        """Record a timer metric."""
        with self.lock:
            self.timers[name].append(value)
            # Keep only last 1000 values
            if len(self.timers[name]) > 1000:
                self.timers[name] = self.timers[name][-1000:]
    
    def get_metrics_summary(self, hours: int = 24) -> Dict[str, Any]:
        """
        Get a summary of metrics for the specified time period.
        
        Args:
            hours: Number of hours to look back
            
        Returns:
            Metrics summary dictionary
        """
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        
        with self.lock:
            # Recent sync metrics
            recent_syncs = [m for m in self.sync_metrics if m.start_time >= cutoff_time]
            
            # API metrics
            recent_api_calls = [m for m in self.api_metrics if m.timestamp >= cutoff_time]
            
            # Calculate statistics
            total_syncs = len(recent_syncs)
            successful_syncs = sum(1 for m in recent_syncs if m.success)
            failed_syncs = total_syncs - successful_syncs
            
            avg_sync_duration = 0.0
            if recent_syncs:
                durations = [m.duration_seconds for m in recent_syncs if m.duration_seconds]
                if durations:
                    avg_sync_duration = sum(durations) / len(durations)
            
            total_api_calls = len(recent_api_calls)
            api_errors = sum(1 for m in recent_api_calls if m.status_code >= 400)
            rate_limit_hits = sum(1 for m in recent_api_calls if m.status_code == 429)
            
            avg_response_time = 0.0
            if recent_api_calls:
                response_times = [m.response_time_ms for m in recent_api_calls]
                avg_response_time = sum(response_times) / len(response_times)
            
            return {
                'time_period_hours': hours,
                'sync_operations': {
                    'total': total_syncs,
                    'successful': successful_syncs,
                    'failed': failed_syncs,
                    'success_rate': successful_syncs / total_syncs if total_syncs > 0 else 0.0,
                    'avg_duration_seconds': avg_sync_duration
                },
                'api_usage': {
                    'total_calls': total_api_calls,
                    'errors': api_errors,
                    'error_rate': api_errors / total_api_calls if total_api_calls > 0 else 0.0,
                    'rate_limit_hits': rate_limit_hits,
                    'avg_response_time_ms': avg_response_time
                },
                'current_state': {
                    'active_syncs': self.gauges.get('active_syncs', 0),
                    'total_repositories': self.gauges.get('total_repositories', 0),
                    'total_issues': self.gauges.get('total_issues', 0),
                    'total_pull_requests': self.gauges.get('total_pull_requests', 0),
                    'total_commits': self.gauges.get('total_commits', 0),
                    'cache_size_mb': self.gauges.get('cache_size_mb', 0.0),
                    'memory_usage_mb': self.gauges.get('memory_usage_mb', 0.0),
                    'cpu_usage_percent': self.gauges.get('cpu_usage_percent', 0.0)
                },
                'counters': dict(self.counters),
                'gauges': dict(self.gauges)
            }
    
    def get_repository_metrics(self, repository: str, hours: int = 24) -> Dict[str, Any]:
        """
        Get metrics for a specific repository.
        
        Args:
            repository: Repository name
            hours: Number of hours to look back
            
        Returns:
            Repository-specific metrics
        """
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        
        with self.lock:
            repo_syncs = [
                m for m in self.sync_metrics 
                if m.repository == repository and m.start_time >= cutoff_time
            ]
            
            if not repo_syncs:
                return {'repository': repository, 'no_data': True}
            
            total_syncs = len(repo_syncs)
            successful_syncs = sum(1 for m in repo_syncs if m.success)
            
            total_items_processed = sum(m.items_processed for m in repo_syncs)
            total_items_created = sum(m.items_created for m in repo_syncs)
            total_items_updated = sum(m.items_updated for m in repo_syncs)
            total_api_calls = sum(m.api_calls_made for m in repo_syncs)
            
            return {
                'repository': repository,
                'time_period_hours': hours,
                'sync_operations': total_syncs,
                'successful_syncs': successful_syncs,
                'success_rate': successful_syncs / total_syncs,
                'items_processed': total_items_processed,
                'items_created': total_items_created,
                'items_updated': total_items_updated,
                'api_calls_made': total_api_calls,
                'last_sync': max(m.start_time for m in repo_syncs).isoformat()
            }
    
    def _persist_sync_metrics(self, metrics: SyncMetrics) -> None:
        """Persist sync metrics to database."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute('''
                    INSERT INTO sync_metrics (
                        repository, operation, start_time, end_time, duration_seconds,
                        items_processed, items_created, items_updated, items_skipped,
                        api_calls_made, rate_limit_hits, errors_encountered,
                        success, error_message
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    metrics.repository, metrics.operation,
                    metrics.start_time.isoformat(),
                    metrics.end_time.isoformat() if metrics.end_time else None,
                    metrics.duration_seconds,
                    metrics.items_processed, metrics.items_created,
                    metrics.items_updated, metrics.items_skipped,
                    metrics.api_calls_made, metrics.rate_limit_hits,
                    metrics.errors_encountered, metrics.success,
                    metrics.error_message
                ))
                conn.commit()
        except Exception as e:
            logger.error(f"Failed to persist sync metrics: {e}")
    
    def _persist_api_metrics(self, metrics: APIMetrics) -> None:
        """Persist API metrics to database."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute('''
                    INSERT INTO api_metrics (
                        endpoint, method, status_code, response_time_ms, timestamp,
                        rate_limit_remaining, rate_limit_reset, error_message
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    metrics.endpoint, metrics.method, metrics.status_code,
                    metrics.response_time_ms, metrics.timestamp.isoformat(),
                    metrics.rate_limit_remaining,
                    metrics.rate_limit_reset.isoformat() if metrics.rate_limit_reset else None,
                    metrics.error_message
                ))
                conn.commit()
        except Exception as e:
            logger.error(f"Failed to persist API metrics: {e}")
    
    def _persist_system_metrics(self, metrics: SystemMetrics) -> None:
        """Persist system metrics to database."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute('''
                    INSERT INTO system_metrics (
                        timestamp, active_syncs, total_repositories, total_issues,
                        total_pull_requests, total_commits, cache_size_mb,
                        memory_usage_mb, cpu_usage_percent
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    metrics.timestamp.isoformat(), metrics.active_syncs,
                    metrics.total_repositories, metrics.total_issues,
                    metrics.total_pull_requests, metrics.total_commits,
                    metrics.cache_size_mb, metrics.memory_usage_mb,
                    metrics.cpu_usage_percent
                ))
                conn.commit()
        except Exception as e:
            logger.error(f"Failed to persist system metrics: {e}")


class PerformanceMonitor:
    """
    Performance monitoring and alerting system.
    
    This class monitors system performance and can trigger alerts
    when thresholds are exceeded.
    """
    
    def __init__(self, metrics_collector: MetricsCollector):
        """
        Initialize performance monitor.
        
        Args:
            metrics_collector: Metrics collector instance
        """
        self.metrics_collector = metrics_collector
        self.alert_callbacks: List[Callable[[str, Dict[str, Any]], None]] = []
        self.thresholds = {
            'sync_failure_rate': 0.1,  # 10% failure rate
            'api_error_rate': 0.05,    # 5% API error rate
            'avg_response_time_ms': 5000,  # 5 second response time
            'memory_usage_mb': 1000,   # 1GB memory usage
            'cpu_usage_percent': 80,   # 80% CPU usage
        }
    
    def add_alert_callback(self, callback: Callable[[str, Dict[str, Any]], None]) -> None:
        """Add an alert callback function."""
        self.alert_callbacks.append(callback)
    
    def set_threshold(self, metric_name: str, threshold_value: float) -> None:
        """Set a threshold for a metric."""
        self.thresholds[metric_name] = threshold_value
    
    def check_thresholds(self) -> List[Dict[str, Any]]:
        """
        Check all thresholds and return any violations.
        
        Returns:
            List of threshold violations
        """
        violations = []
        summary = self.metrics_collector.get_metrics_summary(hours=1)  # Check last hour
        
        # Check sync failure rate
        sync_ops = summary.get('sync_operations', {})
        if sync_ops.get('total', 0) > 0:
            failure_rate = 1.0 - sync_ops.get('success_rate', 1.0)
            if failure_rate > self.thresholds.get('sync_failure_rate', 1.0):
                violations.append({
                    'metric': 'sync_failure_rate',
                    'value': failure_rate,
                    'threshold': self.thresholds['sync_failure_rate'],
                    'message': f"Sync failure rate {failure_rate:.2%} exceeds threshold {self.thresholds['sync_failure_rate']:.2%}"
                })
        
        # Check API error rate
        api_usage = summary.get('api_usage', {})
        if api_usage.get('total_calls', 0) > 0:
            error_rate = api_usage.get('error_rate', 0.0)
            if error_rate > self.thresholds.get('api_error_rate', 1.0):
                violations.append({
                    'metric': 'api_error_rate',
                    'value': error_rate,
                    'threshold': self.thresholds['api_error_rate'],
                    'message': f"API error rate {error_rate:.2%} exceeds threshold {self.thresholds['api_error_rate']:.2%}"
                })
        
        # Check response time
        avg_response_time = api_usage.get('avg_response_time_ms', 0.0)
        if avg_response_time > self.thresholds.get('avg_response_time_ms', float('inf')):
            violations.append({
                'metric': 'avg_response_time_ms',
                'value': avg_response_time,
                'threshold': self.thresholds['avg_response_time_ms'],
                'message': f"Average response time {avg_response_time:.0f}ms exceeds threshold {self.thresholds['avg_response_time_ms']:.0f}ms"
            })
        
        # Check system metrics
        current_state = summary.get('current_state', {})
        
        memory_usage = current_state.get('memory_usage_mb', 0.0)
        if memory_usage > self.thresholds.get('memory_usage_mb', float('inf')):
            violations.append({
                'metric': 'memory_usage_mb',
                'value': memory_usage,
                'threshold': self.thresholds['memory_usage_mb'],
                'message': f"Memory usage {memory_usage:.0f}MB exceeds threshold {self.thresholds['memory_usage_mb']:.0f}MB"
            })
        
        cpu_usage = current_state.get('cpu_usage_percent', 0.0)
        if cpu_usage > self.thresholds.get('cpu_usage_percent', 100.0):
            violations.append({
                'metric': 'cpu_usage_percent',
                'value': cpu_usage,
                'threshold': self.thresholds['cpu_usage_percent'],
                'message': f"CPU usage {cpu_usage:.1f}% exceeds threshold {self.thresholds['cpu_usage_percent']:.1f}%"
            })
        
        # Trigger alerts for violations
        for violation in violations:
            self._trigger_alert(violation['metric'], violation)
        
        return violations
    
    def _trigger_alert(self, metric_name: str, violation_data: Dict[str, Any]) -> None:
        """Trigger alert callbacks for a threshold violation."""
        for callback in self.alert_callbacks:
            try:
                callback(metric_name, violation_data)
            except Exception as e:
                logger.error(f"Alert callback failed: {e}")


# Default alert callback that logs alerts
def log_alert_callback(metric_name: str, violation_data: Dict[str, Any]) -> None:
    """Default alert callback that logs threshold violations."""
    logger.warning(f"ALERT: {violation_data['message']}", extra={
        'metric': metric_name,
        'value': violation_data['value'],
        'threshold': violation_data['threshold']
    })