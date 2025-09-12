"""
Gcp Integration Core Core

This module was extracted from gcp_integration_core.py
as part of RM-DDD compliance refactoring.
"""

import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from pathlib import Path
from .interfaces import BillingProvider, BillingMetrics, BillingProviderType, HealthStatus, ReflectiveModule
from .asset_bridge.gcp_billing_client import GCPBillingClientBridge
from .asset_bridge.cost_analyzer import CostAnalyzerBridge
import random
import random
import random

class GCPBillingMonitor(BillingProvider, ReflectiveModule):
    """
    GCP Billing Monitor for Beast Mode
    
    Integrates GCP billing data using either:
    1. OpenFlow asset bridge (preferred)
    2. Direct GCP SDK integration (fallback)
    
    Follows Beast Mode's Reflective Module (RM) pattern
    """

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(__name__)
        if OPENFLOW_ASSETS_AVAILABLE:
            self.logger.info('Using OpenFlow asset bridge for GCP integration')
            self._init_openflow_bridge()
        else:
            self.logger.info('Using direct GCP SDK integration (fallback)')
            self._init_gcp_sdk_fallback()
        self.last_update = None
        self.cached_metrics = None
        self.cache_duration = timedelta(minutes=config.get('cache_duration_minutes', 15))
        self.health_status = HealthStatus(is_healthy=True, status_message='Initialized', last_check=datetime.now(), metrics={})

    def _init_openflow_bridge(self):
        """Initialize using OpenFlow asset bridge"""
        try:
            self.billing_client = GCPBillingClientBridge(self.config)
            self.cost_analyzer = CostAnalyzerBridge(self.config)
            self.integration_mode = 'openflow_bridge'
        except Exception as e:
            self.logger.error(f'Failed to initialize OpenFlow bridge: {e}')
            self._init_gcp_sdk_fallback()

    def _init_gcp_sdk_fallback(self):
        """Initialize using direct GCP SDK (fallback)"""
        self.integration_mode = 'gcp_sdk_direct'
        self.logger.warning('GCP SDK direct integration not yet implemented - using mock data')
        self.billing_client = None
        self.cost_analyzer = None

    async def collect_billing_metrics(self) -> BillingMetrics:
        """
        Collect GCP billing metrics
        
        Uses cached data if available and fresh, otherwise fetches new data
        """
        try:
            if self._is_cache_valid():
                self.logger.debug('Using cached GCP billing metrics')
                return self.cached_metrics
            if self.integration_mode == 'openflow_bridge':
                metrics = await self._collect_via_openflow_bridge()
            else:
                metrics = await self._collect_via_gcp_sdk()
            self.cached_metrics = metrics
            self.last_update = datetime.now()
            self.health_status = HealthStatus(is_healthy=True, status_message='Successfully collected GCP billing metrics', last_check=datetime.now(), metrics={'last_cost': metrics.total_cost_usd})
            return metrics
        except Exception as e:
            self.logger.error(f'Failed to collect GCP billing metrics: {e}')
            self.health_status = HealthStatus(is_healthy=False, status_message=f'Error collecting metrics: {str(e)}', last_check=datetime.now(), metrics={})
            if self.cached_metrics:
                return self.cached_metrics
            else:
                return self._get_mock_metrics()

    async def _collect_via_openflow_bridge(self) -> BillingMetrics:
        """Collect metrics using OpenFlow asset bridge"""
        billing_data = await self.billing_client.get_billing_data()
        analyzed_costs = self.cost_analyzer.analyze_costs(billing_data)
        return BillingMetrics(provider_type=BillingProviderType.GCP, provider_name='Google Cloud Platform', total_cost_usd=analyzed_costs['total_cost'], daily_cost_usd=analyzed_costs['daily_cost'], hourly_burn_rate=analyzed_costs['hourly_burn_rate'], cost_breakdown=analyzed_costs['cost_breakdown'], usage_metrics=analyzed_costs['usage_metrics'], timestamp=datetime.now())

    async def _collect_via_gcp_sdk(self) -> BillingMetrics:
        """Collect metrics using direct GCP SDK integration"""
        return self._get_mock_metrics()

    def _get_mock_metrics(self) -> BillingMetrics:
        """Get mock GCP metrics for multi-service model with proper correlation"""
        import random
        requests_today = random.randint(1200, 3500)
        avg_cpu_per_request = random.uniform(0.1, 0.8)
        avg_memory_mb = random.randint(128, 512)
        request_cost = requests_today * 2.4e-05
        cpu_seconds = requests_today * avg_cpu_per_request
        cpu_cost = cpu_seconds * 9e-06
        memory_gb_seconds = requests_today * (avg_memory_mb / 1024) * avg_cpu_per_request
        memory_cost = memory_gb_seconds * 2.5e-06
        db_operations = int(requests_today * 0.7)
        db_instance_hours = 24
        db_tier_rate = 0.0413
        db_instance_cost = db_instance_hours * db_tier_rate
        db_storage_gb = random.uniform(10, 50)
        db_storage_cost = db_storage_gb * 0.17
        file_operations = int(requests_today * 0.3)
        storage_gb = random.uniform(5, 25)
        storage_cost = storage_gb * 0.02
        class_a_ops = file_operations * 0.2
        class_b_ops = file_operations * 0.8
        operation_cost = class_a_ops * 0.005 / 1000 + class_b_ops * 0.0004 / 1000
        secret_versions = random.randint(5, 15)
        secret_access_ops = requests_today * 1.2
        secret_version_cost = secret_versions * 0.06
        secret_access_cost = secret_access_ops * 0.03 / 10000
        avg_response_kb = random.uniform(2, 15)
        data_transfer_gb = requests_today * avg_response_kb / (1024 * 1024)
        networking_cost = data_transfer_gb * 0.12
        container_registry_cost = random.uniform(0.01, 0.03)
        logging_cost = random.uniform(0.02, 0.08)
        daily_cost = request_cost + cpu_cost + memory_cost + db_instance_cost + db_storage_cost + storage_cost + operation_cost + secret_version_cost + secret_access_cost + networking_cost + container_registry_cost + logging_cost
        return BillingMetrics(provider_type=BillingProviderType.GCP, provider_name='Google Cloud Platform (Multi-Service)', total_cost_usd=daily_cost * 7, daily_cost_usd=daily_cost, hourly_burn_rate=daily_cost / 24, cost_breakdown={'Cloud Run Requests': request_cost, 'Cloud Run CPU': cpu_cost, 'Cloud Run Memory': memory_cost, 'Cloud SQL Instance': db_instance_cost, 'Cloud SQL Storage': db_storage_cost, 'Cloud Storage Data': storage_cost, 'Cloud Storage Operations': operation_cost, 'Secret Manager Versions': secret_version_cost, 'Secret Manager Access': secret_access_cost, 'Networking (Egress)': networking_cost, 'Container Registry': container_registry_cost, 'Cloud Logging': logging_cost}, usage_metrics={'cloud_run_requests': requests_today, 'cpu_seconds': round(cpu_seconds, 2), 'memory_gb_seconds': round(memory_gb_seconds, 2), 'avg_request_duration_ms': round(avg_cpu_per_request * 1000, 1), 'avg_memory_mb': avg_memory_mb, 'cloud_sql_operations': db_operations, 'cloud_sql_instance_hours': db_instance_hours, 'cloud_sql_storage_gb': round(db_storage_gb, 2), 'cloud_storage_gb': round(storage_gb, 2), 'storage_operations': file_operations, 'class_a_operations': int(class_a_ops), 'class_b_operations': int(class_b_ops), 'secret_versions': secret_versions, 'secret_access_operations': secret_access_ops, 'avg_response_kb': round(avg_response_kb, 1), 'data_transfer_gb': round(data_transfer_gb, 3), 'cold_starts': random.randint(50, 200), 'concurrent_requests': random.randint(1, 10), 'cost_per_request': round(daily_cost / requests_today, 6), 'cost_per_cpu_second': round(cpu_cost / cpu_seconds, 6) if cpu_seconds > 0 else 0, 'cost_per_db_operation': round((db_instance_cost + db_storage_cost) / db_operations, 6) if db_operations > 0 else 0, 'cost_per_storage_operation': round((storage_cost + operation_cost) / file_operations, 6) if file_operations > 0 else 0, 'cost_per_secret_access': round((secret_version_cost + secret_access_cost) / secret_access_ops, 6) if secret_access_ops > 0 else 0}, timestamp=datetime.now())

    def _is_cache_valid(self) -> bool:
        """Check if cached metrics are still valid"""
        if not self.cached_metrics or not self.last_update:
            return False
        return datetime.now() - self.last_update < self.cache_duration

    def get_health_status(self) -> HealthStatus:
        """Get health status for RM pattern compliance"""
        return self.health_status

    def get_metrics(self) -> Dict[str, Any]:
        """Get operational metrics for RM pattern"""
        return {'integration_mode': self.integration_mode, 'openflow_assets_available': OPENFLOW_ASSETS_AVAILABLE, 'cache_valid': self._is_cache_valid(), 'last_update': self.last_update.isoformat() if self.last_update else None, 'cache_duration_minutes': self.cache_duration.total_seconds() / 60}

    def get_configuration(self) -> Dict[str, Any]:
        """Get current configuration for RM pattern"""
        return {'integration_mode': self.integration_mode, 'cache_duration_minutes': self.cache_duration.total_seconds() / 60, 'config_keys': list(self.config.keys())}

    def get_configuration_schema(self) -> Dict[str, Any]:
        """Get configuration schema for the provider"""
        return {'type': 'object', 'properties': {'enabled': {'type': 'boolean', 'default': True}, 'billing_account_id': {'type': 'string', 'description': 'GCP Billing Account ID'}, 'project_ids': {'type': 'array', 'items': {'type': 'string'}}, 'credentials_path': {'type': 'string', 'description': 'Path to GCP service account credentials'}, 'cache_duration_minutes': {'type': 'integer', 'default': 15, 'minimum': 1}, 'cost_attribution': {'type': 'object', 'properties': {'development': {'type': 'array', 'items': {'type': 'string'}}, 'ai_ml': {'type': 'array', 'items': {'type': 'string'}}, 'networking': {'type': 'array', 'items': {'type': 'string'}}}}, 'budget_alerts': {'type': 'object', 'properties': {'daily_limit_usd': {'type': 'number', 'minimum': 0}, 'hourly_spike_threshold': {'type': 'number', 'minimum': 0}}}}, 'required': ['billing_account_id']}

    async def validate_credentials(self) -> bool:
        """Validate GCP credentials"""
        try:
            if self.integration_mode == 'openflow_bridge' and self.billing_client:
                return await self.billing_client.validate_credentials()
            elif self.integration_mode == 'gcp_sdk_direct':
                return True
            else:
                return False
        except Exception as e:
            self.logger.error(f'Credential validation failed: {e}')
            return False

    def get_cost_optimization_recommendations(self) -> List[Dict[str, Any]]:
        """Get multi-service cost optimization recommendations"""
        recommendations = []
        if self.cached_metrics:
            cost_breakdown = self.cached_metrics.cost_breakdown
            usage_metrics = self.cached_metrics.usage_metrics
            cloud_run_total = cost_breakdown.get('Cloud Run Requests', 0) + cost_breakdown.get('Cloud Run CPU', 0) + cost_breakdown.get('Cloud Run Memory', 0)
            if cloud_run_total > 5.0:
                recommendations.append({'type': 'cloud_run_optimization', 'priority': 'medium', 'title': 'Cloud Run cost optimization opportunity', 'description': f'Cloud Run costs are ${cloud_run_total:.2f}/day. Consider memory/CPU optimization and request batching.', 'potential_savings_usd': cloud_run_total * 0.25, 'action': 'Review memory allocation and implement request batching'})
            sql_instance_cost = cost_breakdown.get('Cloud SQL Instance', 0)
            if sql_instance_cost > 1.0:
                recommendations.append({'type': 'cloud_sql_optimization', 'priority': 'high', 'title': 'Cloud SQL instance optimization', 'description': f'Cloud SQL instance costs ${sql_instance_cost:.2f}/day. Consider smaller instance or connection pooling.', 'potential_savings_usd': sql_instance_cost * 0.4, 'action': 'Evaluate db-f1-micro vs shared-core instances and implement connection pooling'})
            storage_data_cost = cost_breakdown.get('Cloud Storage Data', 0)
            storage_ops_cost = cost_breakdown.get('Cloud Storage Operations', 0)
            if storage_ops_cost > 0.1:
                recommendations.append({'type': 'storage_operations_optimization', 'priority': 'medium', 'title': 'High Cloud Storage operation costs', 'description': f'Storage operations cost ${storage_ops_cost:.3f}/day. Consider caching and batch operations.', 'potential_savings_usd': storage_ops_cost * 0.6, 'action': 'Implement CDN caching and batch file operations'})
            secret_access_cost = cost_breakdown.get('Secret Manager Access', 0)
            if secret_access_cost > 0.05:
                recommendations.append({'type': 'secret_manager_optimization', 'priority': 'low', 'title': 'Secret Manager access optimization', 'description': f'Secret access costs ${secret_access_cost:.3f}/day. Consider local caching of secrets.', 'potential_savings_usd': secret_access_cost * 0.8, 'action': 'Implement secret caching with TTL to reduce API calls'})
            cost_per_request = usage_metrics.get('cost_per_request', 0)
            if cost_per_request > 0.001:
                recommendations.append({'type': 'request_efficiency_optimization', 'priority': 'high', 'title': 'High cost per request detected', 'description': f'Cost per request is ${cost_per_request:.6f}. Consider request optimization and caching.', 'potential_savings_usd': self.cached_metrics.daily_cost_usd * 0.3, 'action': 'Implement request caching, reduce database calls, and optimize response sizes'})
        return recommendations

def __init__(self, config: Dict[str, Any]):
    self.config = config
    self.logger = logging.getLogger(__name__)
    if OPENFLOW_ASSETS_AVAILABLE:
        self.logger.info('Using OpenFlow asset bridge for GCP integration')
        self._init_openflow_bridge()
    else:
        self.logger.info('Using direct GCP SDK integration (fallback)')
        self._init_gcp_sdk_fallback()
    self.last_update = None
    self.cached_metrics = None
    self.cache_duration = timedelta(minutes=config.get('cache_duration_minutes', 15))
    self.health_status = HealthStatus(is_healthy=True, status_message='Initialized', last_check=datetime.now(), metrics={})

def _init_openflow_bridge(self):
    """Initialize using OpenFlow asset bridge"""
    try:
        self.billing_client = GCPBillingClientBridge(self.config)
        self.cost_analyzer = CostAnalyzerBridge(self.config)
        self.integration_mode = 'openflow_bridge'
    except Exception as e:
        self.logger.error(f'Failed to initialize OpenFlow bridge: {e}')
        self._init_gcp_sdk_fallback()

def _init_gcp_sdk_fallback(self):
    """Initialize using direct GCP SDK (fallback)"""
    self.integration_mode = 'gcp_sdk_direct'
    self.logger.warning('GCP SDK direct integration not yet implemented - using mock data')
    self.billing_client = None
    self.cost_analyzer = None

def _get_mock_metrics(self) -> BillingMetrics:
    """Get mock GCP metrics for multi-service model with proper correlation"""
    import random
    requests_today = random.randint(1200, 3500)
    avg_cpu_per_request = random.uniform(0.1, 0.8)
    avg_memory_mb = random.randint(128, 512)
    request_cost = requests_today * 2.4e-05
    cpu_seconds = requests_today * avg_cpu_per_request
    cpu_cost = cpu_seconds * 9e-06
    memory_gb_seconds = requests_today * (avg_memory_mb / 1024) * avg_cpu_per_request
    memory_cost = memory_gb_seconds * 2.5e-06
    db_operations = int(requests_today * 0.7)
    db_instance_hours = 24
    db_tier_rate = 0.0413
    db_instance_cost = db_instance_hours * db_tier_rate
    db_storage_gb = random.uniform(10, 50)
    db_storage_cost = db_storage_gb * 0.17
    file_operations = int(requests_today * 0.3)
    storage_gb = random.uniform(5, 25)
    storage_cost = storage_gb * 0.02
    class_a_ops = file_operations * 0.2
    class_b_ops = file_operations * 0.8
    operation_cost = class_a_ops * 0.005 / 1000 + class_b_ops * 0.0004 / 1000
    secret_versions = random.randint(5, 15)
    secret_access_ops = requests_today * 1.2
    secret_version_cost = secret_versions * 0.06
    secret_access_cost = secret_access_ops * 0.03 / 10000
    avg_response_kb = random.uniform(2, 15)
    data_transfer_gb = requests_today * avg_response_kb / (1024 * 1024)
    networking_cost = data_transfer_gb * 0.12
    container_registry_cost = random.uniform(0.01, 0.03)
    logging_cost = random.uniform(0.02, 0.08)
    daily_cost = request_cost + cpu_cost + memory_cost + db_instance_cost + db_storage_cost + storage_cost + operation_cost + secret_version_cost + secret_access_cost + networking_cost + container_registry_cost + logging_cost
    return BillingMetrics(provider_type=BillingProviderType.GCP, provider_name='Google Cloud Platform (Multi-Service)', total_cost_usd=daily_cost * 7, daily_cost_usd=daily_cost, hourly_burn_rate=daily_cost / 24, cost_breakdown={'Cloud Run Requests': request_cost, 'Cloud Run CPU': cpu_cost, 'Cloud Run Memory': memory_cost, 'Cloud SQL Instance': db_instance_cost, 'Cloud SQL Storage': db_storage_cost, 'Cloud Storage Data': storage_cost, 'Cloud Storage Operations': operation_cost, 'Secret Manager Versions': secret_version_cost, 'Secret Manager Access': secret_access_cost, 'Networking (Egress)': networking_cost, 'Container Registry': container_registry_cost, 'Cloud Logging': logging_cost}, usage_metrics={'cloud_run_requests': requests_today, 'cpu_seconds': round(cpu_seconds, 2), 'memory_gb_seconds': round(memory_gb_seconds, 2), 'avg_request_duration_ms': round(avg_cpu_per_request * 1000, 1), 'avg_memory_mb': avg_memory_mb, 'cloud_sql_operations': db_operations, 'cloud_sql_instance_hours': db_instance_hours, 'cloud_sql_storage_gb': round(db_storage_gb, 2), 'cloud_storage_gb': round(storage_gb, 2), 'storage_operations': file_operations, 'class_a_operations': int(class_a_ops), 'class_b_operations': int(class_b_ops), 'secret_versions': secret_versions, 'secret_access_operations': secret_access_ops, 'avg_response_kb': round(avg_response_kb, 1), 'data_transfer_gb': round(data_transfer_gb, 3), 'cold_starts': random.randint(50, 200), 'concurrent_requests': random.randint(1, 10), 'cost_per_request': round(daily_cost / requests_today, 6), 'cost_per_cpu_second': round(cpu_cost / cpu_seconds, 6) if cpu_seconds > 0 else 0, 'cost_per_db_operation': round((db_instance_cost + db_storage_cost) / db_operations, 6) if db_operations > 0 else 0, 'cost_per_storage_operation': round((storage_cost + operation_cost) / file_operations, 6) if file_operations > 0 else 0, 'cost_per_secret_access': round((secret_version_cost + secret_access_cost) / secret_access_ops, 6) if secret_access_ops > 0 else 0}, timestamp=datetime.now())

def _is_cache_valid(self) -> bool:
    """Check if cached metrics are still valid"""
    if not self.cached_metrics or not self.last_update:
        return False
    return datetime.now() - self.last_update < self.cache_duration

def get_health_status(self) -> HealthStatus:
    """Get health status for RM pattern compliance"""
    return self.health_status

def get_metrics(self) -> Dict[str, Any]:
    """Get operational metrics for RM pattern"""
    return {'integration_mode': self.integration_mode, 'openflow_assets_available': OPENFLOW_ASSETS_AVAILABLE, 'cache_valid': self._is_cache_valid(), 'last_update': self.last_update.isoformat() if self.last_update else None, 'cache_duration_minutes': self.cache_duration.total_seconds() / 60}

def get_configuration(self) -> Dict[str, Any]:
    """Get current configuration for RM pattern"""
    return {'integration_mode': self.integration_mode, 'cache_duration_minutes': self.cache_duration.total_seconds() / 60, 'config_keys': list(self.config.keys())}

def get_configuration_schema(self) -> Dict[str, Any]:
    """Get configuration schema for the provider"""
    return {'type': 'object', 'properties': {'enabled': {'type': 'boolean', 'default': True}, 'billing_account_id': {'type': 'string', 'description': 'GCP Billing Account ID'}, 'project_ids': {'type': 'array', 'items': {'type': 'string'}}, 'credentials_path': {'type': 'string', 'description': 'Path to GCP service account credentials'}, 'cache_duration_minutes': {'type': 'integer', 'default': 15, 'minimum': 1}, 'cost_attribution': {'type': 'object', 'properties': {'development': {'type': 'array', 'items': {'type': 'string'}}, 'ai_ml': {'type': 'array', 'items': {'type': 'string'}}, 'networking': {'type': 'array', 'items': {'type': 'string'}}}}, 'budget_alerts': {'type': 'object', 'properties': {'daily_limit_usd': {'type': 'number', 'minimum': 0}, 'hourly_spike_threshold': {'type': 'number', 'minimum': 0}}}}, 'required': ['billing_account_id']}

def get_cost_optimization_recommendations(self) -> List[Dict[str, Any]]:
    """Get multi-service cost optimization recommendations"""
    recommendations = []
    if self.cached_metrics:
        cost_breakdown = self.cached_metrics.cost_breakdown
        usage_metrics = self.cached_metrics.usage_metrics
        cloud_run_total = cost_breakdown.get('Cloud Run Requests', 0) + cost_breakdown.get('Cloud Run CPU', 0) + cost_breakdown.get('Cloud Run Memory', 0)
        if cloud_run_total > 5.0:
            recommendations.append({'type': 'cloud_run_optimization', 'priority': 'medium', 'title': 'Cloud Run cost optimization opportunity', 'description': f'Cloud Run costs are ${cloud_run_total:.2f}/day. Consider memory/CPU optimization and request batching.', 'potential_savings_usd': cloud_run_total * 0.25, 'action': 'Review memory allocation and implement request batching'})
        sql_instance_cost = cost_breakdown.get('Cloud SQL Instance', 0)
        if sql_instance_cost > 1.0:
            recommendations.append({'type': 'cloud_sql_optimization', 'priority': 'high', 'title': 'Cloud SQL instance optimization', 'description': f'Cloud SQL instance costs ${sql_instance_cost:.2f}/day. Consider smaller instance or connection pooling.', 'potential_savings_usd': sql_instance_cost * 0.4, 'action': 'Evaluate db-f1-micro vs shared-core instances and implement connection pooling'})
        storage_data_cost = cost_breakdown.get('Cloud Storage Data', 0)
        storage_ops_cost = cost_breakdown.get('Cloud Storage Operations', 0)
        if storage_ops_cost > 0.1:
            recommendations.append({'type': 'storage_operations_optimization', 'priority': 'medium', 'title': 'High Cloud Storage operation costs', 'description': f'Storage operations cost ${storage_ops_cost:.3f}/day. Consider caching and batch operations.', 'potential_savings_usd': storage_ops_cost * 0.6, 'action': 'Implement CDN caching and batch file operations'})
        secret_access_cost = cost_breakdown.get('Secret Manager Access', 0)
        if secret_access_cost > 0.05:
            recommendations.append({'type': 'secret_manager_optimization', 'priority': 'low', 'title': 'Secret Manager access optimization', 'description': f'Secret access costs ${secret_access_cost:.3f}/day. Consider local caching of secrets.', 'potential_savings_usd': secret_access_cost * 0.8, 'action': 'Implement secret caching with TTL to reduce API calls'})
        cost_per_request = usage_metrics.get('cost_per_request', 0)
        if cost_per_request > 0.001:
            recommendations.append({'type': 'request_efficiency_optimization', 'priority': 'high', 'title': 'High cost per request detected', 'description': f'Cost per request is ${cost_per_request:.6f}. Consider request optimization and caching.', 'potential_savings_usd': self.cached_metrics.daily_cost_usd * 0.3, 'action': 'Implement request caching, reduce database calls, and optimize response sizes'})
    return recommendations

def __init__(self, config: Dict[str, Any]):
    self.config = config
    self.logger = logging.getLogger(__name__)
    if OPENFLOW_ASSETS_AVAILABLE:
        self.logger.info('Using OpenFlow asset bridge for GCP integration')
        self._init_openflow_bridge()
    else:
        self.logger.info('Using direct GCP SDK integration (fallback)')
        self._init_gcp_sdk_fallback()
    self.last_update = None
    self.cached_metrics = None
    self.cache_duration = timedelta(minutes=config.get('cache_duration_minutes', 15))
    self.health_status = HealthStatus(is_healthy=True, status_message='Initialized', last_check=datetime.now(), metrics={})

def _init_openflow_bridge(self):
    """Initialize using OpenFlow asset bridge"""
    try:
        self.billing_client = GCPBillingClientBridge(self.config)
        self.cost_analyzer = CostAnalyzerBridge(self.config)
        self.integration_mode = 'openflow_bridge'
    except Exception as e:
        self.logger.error(f'Failed to initialize OpenFlow bridge: {e}')
        self._init_gcp_sdk_fallback()

def _init_gcp_sdk_fallback(self):
    """Initialize using direct GCP SDK (fallback)"""
    self.integration_mode = 'gcp_sdk_direct'
    self.logger.warning('GCP SDK direct integration not yet implemented - using mock data')
    self.billing_client = None
    self.cost_analyzer = None

def _get_mock_metrics(self) -> BillingMetrics:
    """Get mock GCP metrics for multi-service model with proper correlation"""
    import random
    requests_today = random.randint(1200, 3500)
    avg_cpu_per_request = random.uniform(0.1, 0.8)
    avg_memory_mb = random.randint(128, 512)
    request_cost = requests_today * 2.4e-05
    cpu_seconds = requests_today * avg_cpu_per_request
    cpu_cost = cpu_seconds * 9e-06
    memory_gb_seconds = requests_today * (avg_memory_mb / 1024) * avg_cpu_per_request
    memory_cost = memory_gb_seconds * 2.5e-06
    db_operations = int(requests_today * 0.7)
    db_instance_hours = 24
    db_tier_rate = 0.0413
    db_instance_cost = db_instance_hours * db_tier_rate
    db_storage_gb = random.uniform(10, 50)
    db_storage_cost = db_storage_gb * 0.17
    file_operations = int(requests_today * 0.3)
    storage_gb = random.uniform(5, 25)
    storage_cost = storage_gb * 0.02
    class_a_ops = file_operations * 0.2
    class_b_ops = file_operations * 0.8
    operation_cost = class_a_ops * 0.005 / 1000 + class_b_ops * 0.0004 / 1000
    secret_versions = random.randint(5, 15)
    secret_access_ops = requests_today * 1.2
    secret_version_cost = secret_versions * 0.06
    secret_access_cost = secret_access_ops * 0.03 / 10000
    avg_response_kb = random.uniform(2, 15)
    data_transfer_gb = requests_today * avg_response_kb / (1024 * 1024)
    networking_cost = data_transfer_gb * 0.12
    container_registry_cost = random.uniform(0.01, 0.03)
    logging_cost = random.uniform(0.02, 0.08)
    daily_cost = request_cost + cpu_cost + memory_cost + db_instance_cost + db_storage_cost + storage_cost + operation_cost + secret_version_cost + secret_access_cost + networking_cost + container_registry_cost + logging_cost
    return BillingMetrics(provider_type=BillingProviderType.GCP, provider_name='Google Cloud Platform (Multi-Service)', total_cost_usd=daily_cost * 7, daily_cost_usd=daily_cost, hourly_burn_rate=daily_cost / 24, cost_breakdown={'Cloud Run Requests': request_cost, 'Cloud Run CPU': cpu_cost, 'Cloud Run Memory': memory_cost, 'Cloud SQL Instance': db_instance_cost, 'Cloud SQL Storage': db_storage_cost, 'Cloud Storage Data': storage_cost, 'Cloud Storage Operations': operation_cost, 'Secret Manager Versions': secret_version_cost, 'Secret Manager Access': secret_access_cost, 'Networking (Egress)': networking_cost, 'Container Registry': container_registry_cost, 'Cloud Logging': logging_cost}, usage_metrics={'cloud_run_requests': requests_today, 'cpu_seconds': round(cpu_seconds, 2), 'memory_gb_seconds': round(memory_gb_seconds, 2), 'avg_request_duration_ms': round(avg_cpu_per_request * 1000, 1), 'avg_memory_mb': avg_memory_mb, 'cloud_sql_operations': db_operations, 'cloud_sql_instance_hours': db_instance_hours, 'cloud_sql_storage_gb': round(db_storage_gb, 2), 'cloud_storage_gb': round(storage_gb, 2), 'storage_operations': file_operations, 'class_a_operations': int(class_a_ops), 'class_b_operations': int(class_b_ops), 'secret_versions': secret_versions, 'secret_access_operations': secret_access_ops, 'avg_response_kb': round(avg_response_kb, 1), 'data_transfer_gb': round(data_transfer_gb, 3), 'cold_starts': random.randint(50, 200), 'concurrent_requests': random.randint(1, 10), 'cost_per_request': round(daily_cost / requests_today, 6), 'cost_per_cpu_second': round(cpu_cost / cpu_seconds, 6) if cpu_seconds > 0 else 0, 'cost_per_db_operation': round((db_instance_cost + db_storage_cost) / db_operations, 6) if db_operations > 0 else 0, 'cost_per_storage_operation': round((storage_cost + operation_cost) / file_operations, 6) if file_operations > 0 else 0, 'cost_per_secret_access': round((secret_version_cost + secret_access_cost) / secret_access_ops, 6) if secret_access_ops > 0 else 0}, timestamp=datetime.now())

def _is_cache_valid(self) -> bool:
    """Check if cached metrics are still valid"""
    if not self.cached_metrics or not self.last_update:
        return False
    return datetime.now() - self.last_update < self.cache_duration

def get_health_status(self) -> HealthStatus:
    """Get health status for RM pattern compliance"""
    return self.health_status

def get_metrics(self) -> Dict[str, Any]:
    """Get operational metrics for RM pattern"""
    return {'integration_mode': self.integration_mode, 'openflow_assets_available': OPENFLOW_ASSETS_AVAILABLE, 'cache_valid': self._is_cache_valid(), 'last_update': self.last_update.isoformat() if self.last_update else None, 'cache_duration_minutes': self.cache_duration.total_seconds() / 60}

def get_configuration(self) -> Dict[str, Any]:
    """Get current configuration for RM pattern"""
    return {'integration_mode': self.integration_mode, 'cache_duration_minutes': self.cache_duration.total_seconds() / 60, 'config_keys': list(self.config.keys())}

def get_configuration_schema(self) -> Dict[str, Any]:
    """Get configuration schema for the provider"""
    return {'type': 'object', 'properties': {'enabled': {'type': 'boolean', 'default': True}, 'billing_account_id': {'type': 'string', 'description': 'GCP Billing Account ID'}, 'project_ids': {'type': 'array', 'items': {'type': 'string'}}, 'credentials_path': {'type': 'string', 'description': 'Path to GCP service account credentials'}, 'cache_duration_minutes': {'type': 'integer', 'default': 15, 'minimum': 1}, 'cost_attribution': {'type': 'object', 'properties': {'development': {'type': 'array', 'items': {'type': 'string'}}, 'ai_ml': {'type': 'array', 'items': {'type': 'string'}}, 'networking': {'type': 'array', 'items': {'type': 'string'}}}}, 'budget_alerts': {'type': 'object', 'properties': {'daily_limit_usd': {'type': 'number', 'minimum': 0}, 'hourly_spike_threshold': {'type': 'number', 'minimum': 0}}}}, 'required': ['billing_account_id']}

def get_cost_optimization_recommendations(self) -> List[Dict[str, Any]]:
    """Get multi-service cost optimization recommendations"""
    recommendations = []
    if self.cached_metrics:
        cost_breakdown = self.cached_metrics.cost_breakdown
        usage_metrics = self.cached_metrics.usage_metrics
        cloud_run_total = cost_breakdown.get('Cloud Run Requests', 0) + cost_breakdown.get('Cloud Run CPU', 0) + cost_breakdown.get('Cloud Run Memory', 0)
        if cloud_run_total > 5.0:
            recommendations.append({'type': 'cloud_run_optimization', 'priority': 'medium', 'title': 'Cloud Run cost optimization opportunity', 'description': f'Cloud Run costs are ${cloud_run_total:.2f}/day. Consider memory/CPU optimization and request batching.', 'potential_savings_usd': cloud_run_total * 0.25, 'action': 'Review memory allocation and implement request batching'})
        sql_instance_cost = cost_breakdown.get('Cloud SQL Instance', 0)
        if sql_instance_cost > 1.0:
            recommendations.append({'type': 'cloud_sql_optimization', 'priority': 'high', 'title': 'Cloud SQL instance optimization', 'description': f'Cloud SQL instance costs ${sql_instance_cost:.2f}/day. Consider smaller instance or connection pooling.', 'potential_savings_usd': sql_instance_cost * 0.4, 'action': 'Evaluate db-f1-micro vs shared-core instances and implement connection pooling'})
        storage_data_cost = cost_breakdown.get('Cloud Storage Data', 0)
        storage_ops_cost = cost_breakdown.get('Cloud Storage Operations', 0)
        if storage_ops_cost > 0.1:
            recommendations.append({'type': 'storage_operations_optimization', 'priority': 'medium', 'title': 'High Cloud Storage operation costs', 'description': f'Storage operations cost ${storage_ops_cost:.3f}/day. Consider caching and batch operations.', 'potential_savings_usd': storage_ops_cost * 0.6, 'action': 'Implement CDN caching and batch file operations'})
        secret_access_cost = cost_breakdown.get('Secret Manager Access', 0)
        if secret_access_cost > 0.05:
            recommendations.append({'type': 'secret_manager_optimization', 'priority': 'low', 'title': 'Secret Manager access optimization', 'description': f'Secret access costs ${secret_access_cost:.3f}/day. Consider local caching of secrets.', 'potential_savings_usd': secret_access_cost * 0.8, 'action': 'Implement secret caching with TTL to reduce API calls'})
        cost_per_request = usage_metrics.get('cost_per_request', 0)
        if cost_per_request > 0.001:
            recommendations.append({'type': 'request_efficiency_optimization', 'priority': 'high', 'title': 'High cost per request detected', 'description': f'Cost per request is ${cost_per_request:.6f}. Consider request optimization and caching.', 'potential_savings_usd': self.cached_metrics.daily_cost_usd * 0.3, 'action': 'Implement request caching, reduce database calls, and optimize response sizes'})
    return recommendations
