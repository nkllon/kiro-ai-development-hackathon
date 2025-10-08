"""
Prometheus metrics integration for MSP SSL Chaos Tamer

Provides comprehensive metrics collection for certificate operations,
MSP-specific monitoring, and system performance tracking.
"""

import logging
import time
from typing import Dict, List, Optional, Any, Callable
from datetime import datetime, timedelta
from functools import wraps
from contextlib import contextmanager

try:
    from prometheus_client import (
        Counter, Gauge, Histogram, Summary, Info, Enum,
        CollectorRegistry, generate_latest, CONTENT_TYPE_LATEST,
        start_http_server, push_to_gateway
    )
    PROMETHEUS_AVAILABLE = True
except ImportError:
    PROMETHEUS_AVAILABLE = False

from ..core.interfaces import ReflectiveModule


class PrometheusMetrics(ReflectiveModule):
    """
    Prometheus metrics collector for MSP SSL Chaos Tamer
    
    Provides comprehensive metrics collection for certificate operations,
    CA plugin performance, and MSP-specific business metrics.
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__()
        
        if not PROMETHEUS_AVAILABLE:
            raise ImportError(
                "Prometheus client not available. Install with: "
                "pip install prometheus-client"
            )
        
        self.config = config or {}
        self.logger = logging.getLogger("msp_ssl.metrics")
        
        # Create custom registry
        self.registry = CollectorRegistry()
        
        # Initialize metrics
        self._init_certificate_metrics()
        self._init_ca_plugin_metrics()
        self._init_msp_business_metrics()
        self._init_system_metrics()
        
        # Metrics server configuration
        self.metrics_port = self.config.get("metrics_port", 9090)
        self.metrics_path = self.config.get("metrics_path", "/metrics")
        self.push_gateway_url = self.config.get("push_gateway_url")
        
        # Start metrics server if configured
        if self.config.get("start_server", True):
            self._start_metrics_server()
        
        self.logger.info("Prometheus metrics initialized")
    
    def _init_certificate_metrics(self) -> None:
        """Initialize certificate-related metrics"""
        
        # Certificate inventory metrics
        self.certificates_total = Gauge(
            'msp_ssl_certificates_total',
            'Total number of certificates managed',
            ['status', 'ca_provider', 'client_id'],
            registry=self.registry
        )
        
        self.certificates_expiring = Gauge(
            'msp_ssl_certificates_expiring',
            'Number of certificates expiring within threshold',
            ['days_threshold', 'client_id'],
            registry=self.registry
        )
        
        self.certificates_expired = Gauge(
            'msp_ssl_certificates_expired',
            'Number of expired certificates',
            ['client_id'],
            registry=self.registry
        )
        
        # Certificate operations metrics
        self.certificate_requests_total = Counter(
            'msp_ssl_certificate_requests_total',
            'Total number of certificate requests',
            ['ca_provider', 'status', 'client_id'],
            registry=self.registry
        )
        
        self.certificate_renewals_total = Counter(
            'msp_ssl_certificate_renewals_total',
            'Total number of certificate renewals',
            ['ca_provider', 'status', 'client_id'],
            registry=self.registry
        )
        
        self.certificate_revocations_total = Counter(
            'msp_ssl_certificate_revocations_total',
            'Total number of certificate revocations',
            ['ca_provider', 'reason', 'client_id'],
            registry=self.registry
        )
        
        # Certificate operation timing
        self.certificate_request_duration = Histogram(
            'msp_ssl_certificate_request_duration_seconds',
            'Time spent requesting certificates',
            ['ca_provider'],
            registry=self.registry,
            buckets=[0.1, 0.5, 1.0, 2.5, 5.0, 10.0, 30.0, 60.0, 120.0]
        )
        
        self.certificate_renewal_duration = Histogram(
            'msp_ssl_certificate_renewal_duration_seconds',
            'Time spent renewing certificates',
            ['ca_provider'],
            registry=self.registry,
            buckets=[0.1, 0.5, 1.0, 2.5, 5.0, 10.0, 30.0, 60.0, 120.0]
        )
    
    def _init_ca_plugin_metrics(self) -> None:
        """Initialize CA plugin metrics"""
        
        # CA plugin health
        self.ca_plugin_health = Gauge(
            'msp_ssl_ca_plugin_health',
            'CA plugin health status (1=healthy, 0=unhealthy)',
            ['ca_provider'],
            registry=self.registry
        )
        
        self.ca_plugin_authenticated = Gauge(
            'msp_ssl_ca_plugin_authenticated',
            'CA plugin authentication status (1=authenticated, 0=not authenticated)',
            ['ca_provider'],
            registry=self.registry
        )
        
        # Rate limiting metrics
        self.ca_plugin_rate_limit_usage = Gauge(
            'msp_ssl_ca_plugin_rate_limit_usage',
            'Current rate limit usage for CA plugin',
            ['ca_provider'],
            registry=self.registry
        )
        
        self.ca_plugin_rate_limit_capacity = Gauge(
            'msp_ssl_ca_plugin_rate_limit_capacity',
            'Rate limit capacity for CA plugin',
            ['ca_provider'],
            registry=self.registry
        )
        
        # CA plugin errors
        self.ca_plugin_errors_total = Counter(
            'msp_ssl_ca_plugin_errors_total',
            'Total number of CA plugin errors',
            ['ca_provider', 'error_type'],
            registry=self.registry
        )
        
        # API response times
        self.ca_plugin_api_duration = Histogram(
            'msp_ssl_ca_plugin_api_duration_seconds',
            'CA plugin API response time',
            ['ca_provider', 'operation'],
            registry=self.registry,
            buckets=[0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0, 30.0]
        )
    
    def _init_msp_business_metrics(self) -> None:
        """Initialize MSP business metrics"""
        
        # Client metrics
        self.msp_clients_total = Gauge(
            'msp_ssl_msp_clients_total',
            'Total number of MSP clients',
            registry=self.registry
        )
        
        self.msp_domains_total = Gauge(
            'msp_ssl_msp_domains_total',
            'Total number of domains managed',
            ['client_id'],
            registry=self.registry
        )
        
        # Certificate health score
        self.msp_client_certificate_health_score = Gauge(
            'msp_ssl_client_certificate_health_score',
            'Certificate health score for client (0-100)',
            ['client_id'],
            registry=self.registry
        )
        
        # Emergency operations
        self.emergency_provisions_total = Counter(
            'msp_ssl_emergency_provisions_total',
            'Total number of emergency certificate provisions',
            ['client_id', 'emergency_type'],
            registry=self.registry
        )
        
        # Cost tracking
        self.certificate_costs_total = Gauge(
            'msp_ssl_certificate_costs_total',
            'Total certificate costs',
            ['client_id', 'ca_provider', 'currency'],
            registry=self.registry
        )
    
    def _init_system_metrics(self) -> None:
        """Initialize system performance metrics"""
        
        # Database metrics
        self.database_connections = Gauge(
            'msp_ssl_database_connections',
            'Number of active database connections',
            registry=self.registry
        )
        
        self.database_query_duration = Histogram(
            'msp_ssl_database_query_duration_seconds',
            'Database query execution time',
            ['operation'],
            registry=self.registry,
            buckets=[0.001, 0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0]
        )
        
        # Credential store metrics
        self.credential_operations_total = Counter(
            'msp_ssl_credential_operations_total',
            'Total credential store operations',
            ['operation', 'status'],
            registry=self.registry
        )
        
        # System health
        self.system_health = Gauge(
            'msp_ssl_system_health',
            'Overall system health (1=healthy, 0=unhealthy)',
            registry=self.registry
        )
        
        # Component status
        self.component_status = Gauge(
            'msp_ssl_component_status',
            'Component status (1=healthy, 0=unhealthy)',
            ['component'],
            registry=self.registry
        )
    
    def _start_metrics_server(self) -> None:
        """Start Prometheus metrics HTTP server"""
        try:
            start_http_server(self.metrics_port, registry=self.registry)
            self.logger.info(f"Prometheus metrics server started on port {self.metrics_port}")
        except Exception as e:
            self.logger.error(f"Failed to start metrics server: {e}")
    
    # Certificate metrics methods
    def record_certificate_request(self, ca_provider: str, client_id: str, 
                                 status: str, duration: float) -> None:
        """Record certificate request metrics"""
        self.certificate_requests_total.labels(
            ca_provider=ca_provider,
            status=status,
            client_id=client_id
        ).inc()
        
        self.certificate_request_duration.labels(
            ca_provider=ca_provider
        ).observe(duration)
    
    def record_certificate_renewal(self, ca_provider: str, client_id: str,
                                 status: str, duration: float) -> None:
        """Record certificate renewal metrics"""
        self.certificate_renewals_total.labels(
            ca_provider=ca_provider,
            status=status,
            client_id=client_id
        ).inc()
        
        self.certificate_renewal_duration.labels(
            ca_provider=ca_provider
        ).observe(duration)
    
    def record_certificate_revocation(self, ca_provider: str, client_id: str, reason: str) -> None:
        """Record certificate revocation metrics"""
        self.certificate_revocations_total.labels(
            ca_provider=ca_provider,
            reason=reason,
            client_id=client_id
        ).inc()
    
    def update_certificate_inventory(self, certificates: List[Dict[str, Any]]) -> None:
        """Update certificate inventory metrics"""
        # Clear existing metrics
        self.certificates_total.clear()
        self.certificates_expiring.clear()
        self.certificates_expired.clear()
        
        # Count certificates by status, CA, and client
        status_counts = {}
        expiring_counts = {}
        expired_counts = {}
        
        for cert in certificates:
            status = cert.get('status', 'unknown')
            ca_provider = cert.get('ca_provider', 'unknown')
            client_id = cert.get('client_id', 'unknown')
            
            # Total certificates
            key = (status, ca_provider, client_id)
            status_counts[key] = status_counts.get(key, 0) + 1
            
            # Expiring certificates
            if cert.get('days_until_expiration'):
                days_left = cert['days_until_expiration']
                for threshold in [7, 14, 30, 60]:
                    if days_left <= threshold:
                        exp_key = (threshold, client_id)
                        expiring_counts[exp_key] = expiring_counts.get(exp_key, 0) + 1
            
            # Expired certificates
            if status == 'expired':
                expired_counts[client_id] = expired_counts.get(client_id, 0) + 1
        
        # Update metrics
        for (status, ca_provider, client_id), count in status_counts.items():
            self.certificates_total.labels(
                status=status,
                ca_provider=ca_provider,
                client_id=client_id
            ).set(count)
        
        for (threshold, client_id), count in expiring_counts.items():
            self.certificates_expiring.labels(
                days_threshold=str(threshold),
                client_id=client_id
            ).set(count)
        
        for client_id, count in expired_counts.items():
            self.certificates_expired.labels(client_id=client_id).set(count)
    
    # CA plugin metrics methods
    def update_ca_plugin_health(self, ca_provider: str, is_healthy: bool, 
                               is_authenticated: bool) -> None:
        """Update CA plugin health metrics"""
        self.ca_plugin_health.labels(ca_provider=ca_provider).set(1 if is_healthy else 0)
        self.ca_plugin_authenticated.labels(ca_provider=ca_provider).set(1 if is_authenticated else 0)
    
    def update_ca_plugin_rate_limits(self, ca_provider: str, usage: int, capacity: int) -> None:
        """Update CA plugin rate limit metrics"""
        self.ca_plugin_rate_limit_usage.labels(ca_provider=ca_provider).set(usage)
        self.ca_plugin_rate_limit_capacity.labels(ca_provider=ca_provider).set(capacity)
    
    def record_ca_plugin_error(self, ca_provider: str, error_type: str) -> None:
        """Record CA plugin error"""
        self.ca_plugin_errors_total.labels(
            ca_provider=ca_provider,
            error_type=error_type
        ).inc()
    
    @contextmanager
    def time_ca_plugin_operation(self, ca_provider: str, operation: str):
        """Context manager to time CA plugin operations"""
        start_time = time.time()
        try:
            yield
        finally:
            duration = time.time() - start_time
            self.ca_plugin_api_duration.labels(
                ca_provider=ca_provider,
                operation=operation
            ).observe(duration)
    
    # MSP business metrics methods
    def update_msp_client_metrics(self, clients: List[Dict[str, Any]]) -> None:
        """Update MSP client metrics"""
        self.msp_clients_total.set(len(clients))
        
        # Clear domain metrics
        self.msp_domains_total.clear()
        
        for client in clients:
            client_id = client.get('id', 'unknown')
            domains = client.get('domains', [])
            
            self.msp_domains_total.labels(client_id=client_id).set(len(domains))
    
    def update_client_health_score(self, client_id: str, health_score: float) -> None:
        """Update client certificate health score"""
        self.msp_client_certificate_health_score.labels(client_id=client_id).set(health_score)
    
    def record_emergency_provision(self, client_id: str, emergency_type: str) -> None:
        """Record emergency certificate provision"""
        self.emergency_provisions_total.labels(
            client_id=client_id,
            emergency_type=emergency_type
        ).inc()
    
    # System metrics methods
    def update_system_health(self, is_healthy: bool) -> None:
        """Update overall system health"""
        self.system_health.set(1 if is_healthy else 0)
    
    def update_component_status(self, component: str, is_healthy: bool) -> None:
        """Update component health status"""
        self.component_status.labels(component=component).set(1 if is_healthy else 0)
    
    @contextmanager
    def time_database_operation(self, operation: str):
        """Context manager to time database operations"""
        start_time = time.time()
        try:
            yield
        finally:
            duration = time.time() - start_time
            self.database_query_duration.labels(operation=operation).observe(duration)
    
    def record_credential_operation(self, operation: str, status: str) -> None:
        """Record credential store operation"""
        self.credential_operations_total.labels(
            operation=operation,
            status=status
        ).inc()
    
    # Utility methods
    def get_metrics_data(self) -> str:
        """Get Prometheus metrics data"""
        return generate_latest(self.registry).decode('utf-8')
    
    def push_metrics(self, job_name: str = "msp-ssl-chaos-tamer") -> bool:
        """Push metrics to Prometheus push gateway"""
        if not self.push_gateway_url:
            self.logger.warning("Push gateway URL not configured")
            return False
        
        try:
            push_to_gateway(
                self.push_gateway_url,
                job=job_name,
                registry=self.registry
            )
            return True
        except Exception as e:
            self.logger.error(f"Failed to push metrics: {e}")
            return False
    
    # ReflectiveModule implementation
    def get_module_info(self) -> Dict[str, Any]:
        """Get metrics module information"""
        return {
            "module_name": "prometheus_metrics",
            "module_type": "monitoring",
            "version": "1.0.0",
            "description": "Prometheus metrics collection for MSP SSL operations"
        }
    
    def get_capabilities(self) -> List[Any]:
        """Get metrics capabilities"""
        return [
            {"name": "certificate_metrics", "enabled": True},
            {"name": "ca_plugin_metrics", "enabled": True},
            {"name": "msp_business_metrics", "enabled": True},
            {"name": "system_metrics", "enabled": True},
            {"name": "metrics_server", "enabled": True},
            {"name": "push_gateway", "enabled": bool(self.push_gateway_url)}
        ]
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get metrics system health status"""
        return {
            "status": "healthy",
            "metrics_port": self.metrics_port,
            "push_gateway_configured": bool(self.push_gateway_url),
            "prometheus_available": PROMETHEUS_AVAILABLE,
            "last_check": datetime.utcnow().isoformat()
        }
    
    def graceful_degradation(self) -> Dict[str, Any]:
        """Perform graceful degradation for metrics system"""
        return {
            "degradation_applied": False,
            "fallback_mode": None,
            "message": "Metrics system operating normally"
        }


class MetricsCollector:
    """
    High-level metrics collector that integrates with MSP SSL components
    
    Provides decorators and utilities for automatic metrics collection.
    """
    
    def __init__(self, prometheus_metrics: PrometheusMetrics):
        self.metrics = prometheus_metrics
        self.logger = logging.getLogger("msp_ssl.metrics_collector")
    
    def time_operation(self, operation_type: str, ca_provider: str = None):
        """Decorator to time operations and record metrics"""
        def decorator(func: Callable) -> Callable:
            @wraps(func)
            def wrapper(*args, **kwargs):
                start_time = time.time()
                status = "success"
                
                try:
                    result = func(*args, **kwargs)
                    return result
                except Exception as e:
                    status = "error"
                    if ca_provider:
                        self.metrics.record_ca_plugin_error(ca_provider, type(e).__name__)
                    raise
                finally:
                    duration = time.time() - start_time
                    
                    # Record appropriate metrics based on operation type
                    if operation_type == "certificate_request" and ca_provider:
                        client_id = kwargs.get("client_id", "unknown")
                        self.metrics.record_certificate_request(
                            ca_provider, client_id, status, duration
                        )
                    elif operation_type == "certificate_renewal" and ca_provider:
                        client_id = kwargs.get("client_id", "unknown")
                        self.metrics.record_certificate_renewal(
                            ca_provider, client_id, status, duration
                        )
            
            return wrapper
        return decorator
    
    def monitor_ca_plugin(self, plugin):
        """Monitor CA plugin health and update metrics"""
        try:
            health_status = plugin.get_health_status()
            rate_limits = plugin.get_rate_limits()
            
            self.metrics.update_ca_plugin_health(
                plugin.ca_name,
                health_status.get("is_healthy", False),
                health_status.get("authenticated", False)
            )
            
            self.metrics.update_ca_plugin_rate_limits(
                plugin.ca_name,
                rate_limits.get("current_usage", 0),
                rate_limits.get("requests_per_window", 0)
            )
            
        except Exception as e:
            self.logger.error(f"Failed to monitor CA plugin {plugin.ca_name}: {e}")
    
    def update_certificate_inventory(self, database):
        """Update certificate inventory metrics from database"""
        try:
            # This would integrate with the actual database
            # For now, we'll use a placeholder
            certificates = []  # database.get_all_certificates()
            self.metrics.update_certificate_inventory(certificates)
            
        except Exception as e:
            self.logger.error(f"Failed to update certificate inventory metrics: {e}")
    
    def update_msp_metrics(self, database):
        """Update MSP business metrics from database"""
        try:
            # This would integrate with the actual database
            clients = []  # database.get_all_clients()
            self.metrics.update_msp_client_metrics(clients)
            
        except Exception as e:
            self.logger.error(f"Failed to update MSP metrics: {e}")


# Utility function to create metrics instance
def create_metrics(config: Dict[str, Any] = None) -> PrometheusMetrics:
    """Factory function to create Prometheus metrics instance"""
    return PrometheusMetrics(config)