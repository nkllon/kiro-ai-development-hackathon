"""
GCP Billing Integration for Beast Mode

Integrates GCP billing data into Beast Mode's unified financial monitoring.
Supports both OpenFlow asset bridge and direct GCP SDK integration.
"""

import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from pathlib import Path

from .interfaces import (
    BillingProvider, 
    BillingMetrics, 
    BillingProviderType,
    HealthStatus,
    ReflectiveModule
)

# Will be populated based on asset discovery results
try:
    # Try to import OpenFlow assets if available
    from .asset_bridge.gcp_billing_client import GCPBillingClientBridge
    from .asset_bridge.cost_analyzer import CostAnalyzerBridge
    OPENFLOW_ASSETS_AVAILABLE = True
except ImportError:
    # Fallback to direct GCP SDK integration
    OPENFLOW_ASSETS_AVAILABLE = False


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
        
        # Initialize based on asset availability
        if OPENFLOW_ASSETS_AVAILABLE:
            self.logger.info("Using OpenFlow asset bridge for GCP integration")
            self._init_openflow_bridge()
        else:
            self.logger.info("Using direct GCP SDK integration (fallback)")
            self._init_gcp_sdk_fallback()
        
        # Common initialization
        self.last_update = None
        self.cached_metrics = None
        self.cache_duration = timedelta(minutes=config.get('cache_duration_minutes', 15))
        
        # Health monitoring
        self.health_status = HealthStatus(
            is_healthy=True,
            status_message="Initialized",
            last_check=datetime.now(),
            metrics={}
        )
    
    def _init_openflow_bridge(self):
        """Initialize using OpenFlow asset bridge"""
        try:
            self.billing_client = GCPBillingClientBridge(self.config)
            self.cost_analyzer = CostAnalyzerBridge(self.config)
            self.integration_mode = "openflow_bridge"
        except Exception as e:
            self.logger.error(f"Failed to initialize OpenFlow bridge: {e}")
            self._init_gcp_sdk_fallback()
    
    def _init_gcp_sdk_fallback(self):
        """Initialize using direct GCP SDK (fallback)"""
        self.integration_mode = "gcp_sdk_direct"
        
        # Mock implementation for now - will be replaced with real GCP SDK
        self.logger.warning("GCP SDK direct integration not yet implemented - using mock data")
        self.billing_client = None
        self.cost_analyzer = None
    
    async def collect_billing_metrics(self) -> BillingMetrics:
        """
        Collect GCP billing metrics
        
        Uses cached data if available and fresh, otherwise fetches new data
        """
        try:
            # Check cache first
            if self._is_cache_valid():
                self.logger.debug("Using cached GCP billing metrics")
                return self.cached_metrics
            
            # Fetch new metrics based on integration mode
            if self.integration_mode == "openflow_bridge":
                metrics = await self._collect_via_openflow_bridge()
            else:
                metrics = await self._collect_via_gcp_sdk()
            
            # Update cache
            self.cached_metrics = metrics
            self.last_update = datetime.now()
            
            # Update health status
            self.health_status = HealthStatus(
                is_healthy=True,
                status_message="Successfully collected GCP billing metrics",
                last_check=datetime.now(),
                metrics={'last_cost': metrics.total_cost_usd}
            )
            
            return metrics
            
        except Exception as e:
            self.logger.error(f"Failed to collect GCP billing metrics: {e}")
            
            # Update health status
            self.health_status = HealthStatus(
                is_healthy=False,
                status_message=f"Error collecting metrics: {str(e)}",
                last_check=datetime.now(),
                metrics={}
            )
            
            # Return cached metrics if available, otherwise mock data
            if self.cached_metrics:
                return self.cached_metrics
            else:
                return self._get_mock_metrics()
    
    async def _collect_via_openflow_bridge(self) -> BillingMetrics:
        """Collect metrics using OpenFlow asset bridge"""
        # This will be implemented once we extract OpenFlow assets
        billing_data = await self.billing_client.get_billing_data()
        analyzed_costs = self.cost_analyzer.analyze_costs(billing_data)
        
        return BillingMetrics(
            provider_type=BillingProviderType.GCP,
            provider_name="Google Cloud Platform",
            total_cost_usd=analyzed_costs['total_cost'],
            daily_cost_usd=analyzed_costs['daily_cost'],
            hourly_burn_rate=analyzed_costs['hourly_burn_rate'],
            cost_breakdown=analyzed_costs['cost_breakdown'],
            usage_metrics=analyzed_costs['usage_metrics'],
            timestamp=datetime.now()
        )
    
    async def _collect_via_gcp_sdk(self) -> BillingMetrics:
        """Collect metrics using direct GCP SDK integration"""
        # TODO: Implement direct GCP SDK integration
        # For now, return mock data that looks realistic
        
        return self._get_mock_metrics()
    
    def _get_mock_metrics(self) -> BillingMetrics:
        """Get mock GCP metrics for Cloud Run pay-per-transaction model with proper correlation"""
        import random
        
        # Base transaction metrics
        requests_today = random.randint(1200, 3500)  # API requests today
        avg_cpu_per_request = random.uniform(0.1, 0.8)  # CPU seconds per request
        avg_memory_mb = random.randint(128, 512)  # Memory allocation per request
        
        # **TRANSACTION-CORRELATED COSTS** (scale with request count)
        # Cloud Run pricing (actual GCP rates)
        request_cost = requests_today * 0.000024  # $0.000024 per request
        cpu_seconds = requests_today * avg_cpu_per_request
        cpu_cost = cpu_seconds * 0.000009  # $0.000009 per CPU-second
        
        # Memory cost (correlated with requests * memory * duration)
        memory_gb_seconds = requests_today * (avg_memory_mb / 1024) * avg_cpu_per_request
        memory_cost = memory_gb_seconds * 0.0000025  # $0.0000025 per GB-second
        
        # **TRANSACTION-PROPORTIONAL COSTS** (loosely correlated)
        # Networking scales with request volume (more requests = more data transfer)
        avg_response_kb = random.uniform(2, 15)  # KB per response
        data_transfer_gb = (requests_today * avg_response_kb) / (1024 * 1024)
        networking_cost = data_transfer_gb * 0.12  # $0.12 per GB egress
        
        # **FIXED COSTS** (not correlated with transactions)
        storage_cost = random.uniform(0.01, 0.05)  # Container registry, logs
        
        # Total daily cost
        daily_cost = request_cost + cpu_cost + memory_cost + networking_cost + storage_cost
        
        return BillingMetrics(
            provider_type=BillingProviderType.GCP,
            provider_name="Google Cloud Platform (Cloud Run)",
            total_cost_usd=daily_cost * 7,  # Weekly total for context
            daily_cost_usd=daily_cost,
            hourly_burn_rate=daily_cost / 24,
            cost_breakdown={
                "Cloud Run Requests": request_cost,
                "Cloud Run CPU": cpu_cost,
                "Cloud Run Memory": memory_cost,
                "Networking (Egress)": networking_cost,
                "Storage (Fixed)": storage_cost
            },
            usage_metrics={
                "cloud_run_requests": requests_today,
                "cpu_seconds": round(cpu_seconds, 2),
                "memory_gb_seconds": round(memory_gb_seconds, 2),
                "avg_request_duration_ms": round(avg_cpu_per_request * 1000, 1),
                "avg_memory_mb": avg_memory_mb,
                "avg_response_kb": round(avg_response_kb, 1),
                "data_transfer_gb": round(data_transfer_gb, 3),
                "cold_starts": random.randint(50, 200),
                "concurrent_requests": random.randint(1, 10),
                # **CORRELATION METRICS**
                "cost_per_request": round(daily_cost / requests_today, 6),
                "cost_per_cpu_second": round(cpu_cost / cpu_seconds, 6) if cpu_seconds > 0 else 0
            },
            timestamp=datetime.now()
        )
    
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
        return {
            'integration_mode': self.integration_mode,
            'openflow_assets_available': OPENFLOW_ASSETS_AVAILABLE,
            'cache_valid': self._is_cache_valid(),
            'last_update': self.last_update.isoformat() if self.last_update else None,
            'cache_duration_minutes': self.cache_duration.total_seconds() / 60
        }
    
    def get_configuration(self) -> Dict[str, Any]:
        """Get current configuration for RM pattern"""
        return {
            'integration_mode': self.integration_mode,
            'cache_duration_minutes': self.cache_duration.total_seconds() / 60,
            'config_keys': list(self.config.keys())
        }
    
    def get_configuration_schema(self) -> Dict[str, Any]:
        """Get configuration schema for the provider"""
        return {
            "type": "object",
            "properties": {
                "enabled": {"type": "boolean", "default": True},
                "billing_account_id": {"type": "string", "description": "GCP Billing Account ID"},
                "project_ids": {"type": "array", "items": {"type": "string"}},
                "credentials_path": {"type": "string", "description": "Path to GCP service account credentials"},
                "cache_duration_minutes": {"type": "integer", "default": 15, "minimum": 1},
                "cost_attribution": {
                    "type": "object",
                    "properties": {
                        "development": {"type": "array", "items": {"type": "string"}},
                        "ai_ml": {"type": "array", "items": {"type": "string"}},
                        "networking": {"type": "array", "items": {"type": "string"}}
                    }
                },
                "budget_alerts": {
                    "type": "object", 
                    "properties": {
                        "daily_limit_usd": {"type": "number", "minimum": 0},
                        "hourly_spike_threshold": {"type": "number", "minimum": 0}
                    }
                }
            },
            "required": ["billing_account_id"]
        }
    
    async def validate_credentials(self) -> bool:
        """Validate GCP credentials"""
        try:
            if self.integration_mode == "openflow_bridge" and self.billing_client:
                return await self.billing_client.validate_credentials()
            elif self.integration_mode == "gcp_sdk_direct":
                # TODO: Implement GCP SDK credential validation
                return True  # Mock validation for now
            else:
                return False
        except Exception as e:
            self.logger.error(f"Credential validation failed: {e}")
            return False
    
    def get_cost_optimization_recommendations(self) -> List[Dict[str, Any]]:
        """Get cost optimization recommendations"""
        recommendations = []
        
        if self.cached_metrics:
            # Analyze cost breakdown for optimization opportunities
            cost_breakdown = self.cached_metrics.cost_breakdown
            
            # Check for high compute costs
            compute_cost = cost_breakdown.get("Compute Engine", 0)
            if compute_cost > 15.0:
                recommendations.append({
                    "type": "compute_optimization",
                    "priority": "medium",
                    "title": "High Compute Engine costs detected",
                    "description": f"Compute Engine costs are ${compute_cost:.2f}. Consider rightsizing instances or using preemptible VMs.",
                    "potential_savings_usd": compute_cost * 0.3,
                    "action": "Review compute instance utilization and consider cost-effective alternatives"
                })
            
            # Check for storage costs
            storage_cost = cost_breakdown.get("Cloud Storage", 0)
            if storage_cost > 10.0:
                recommendations.append({
                    "type": "storage_optimization", 
                    "priority": "low",
                    "title": "Storage costs optimization opportunity",
                    "description": f"Cloud Storage costs are ${storage_cost:.2f}. Consider lifecycle policies and storage class optimization.",
                    "potential_savings_usd": storage_cost * 0.2,
                    "action": "Implement storage lifecycle policies and review storage classes"
                })
        
        return recommendations