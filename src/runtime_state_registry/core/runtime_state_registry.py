#!/usr/bin/env python3
"""
Runtime State Registry - Core Implementation

Main registry that coordinates multi-source runtime state operations with
AI Memory Palace integration for O(1) context-aware queries.
"""

import os
import sys
import json
import redis
import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Set
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from src.rm_ddd.core.unified_reflective_module import (
    ReflectiveModule, ModuleCapability, ModuleHealth, ModuleStatus, 
    GracefulDegradationResult
)
from .models import (
    UnifiedServiceState, ThreeLayerState, DriftDetection, ComplianceScore,
    ServiceStatus, CMSStatus, SpecStatus, DriftType, DriftSeverity,
    QueryResult, ValidationResult, HistoricalStateEvent, EventType,
    MonitoringState, HealthStatus
)
from ..collectors.redis_data_collector import RedisDataCollector
from ..collectors.cms_configuration_collector import CMSConfigurationCollector
from ..collectors.prometheus_integration_collector import PrometheusIntegrationCollector
from ..collectors.grafana_intelligence_collector import GrafanaIntelligenceCollector


class RuntimeStateRegistry(ReflectiveModule):
    """
    Main registry that coordinates multi-source runtime state operations.
    
    Provides unified visibility into system state by reconciling data from:
    - Redis (ReflectiveModule auto-registration, DAG execution, Celery tasks)
    - CMS (canonical configurations and compliance policies)
    - Prometheus (service discovery targets and metrics)
    - Grafana (dashboard intelligence and alerts)
    - Specifications (DAG dependencies and architectural requirements)
    """
    
    def __init__(self, redis_host: str = None, redis_port: int = 6379):
        super().__init__()
        
        # Initialize Redis connection with smart environment detection
        self.redis_host = redis_host or self._resolve_redis_host()
        self.redis_port = redis_port
        self.redis_client = None
        
        # State storage
        self._unified_services: Dict[str, UnifiedServiceState] = {}
        self._three_layer_state: Optional[ThreeLayerState] = None
        self._last_reconciliation: Optional[datetime] = None
        
        # Monitoring
        self._monitoring_active = False
        self._monitoring_task: Optional[asyncio.Task] = None
        
        # Initialize collectors
        self._initialize_collectors()
        
        # Initialize connections
        self._initialize_connections()
    
    def get_module_info(self) -> Dict[str, Any]:
        """Get module information."""
        return {
            'module_id': 'runtime_state_registry',
            'version': '1.0.0',
            'description': 'Unified multi-source system state management',
            'redis_host': self.redis_host,
            'redis_port': self.redis_port
        }
    
    def get_capabilities(self) -> List[ModuleCapability]:
        """Get module capabilities."""
        return [
            ModuleCapability.CORE_FUNCTIONALITY,
            ModuleCapability.MONITORING,
            ModuleCapability.API_INTEGRATION
        ]
    
    def get_health_status(self) -> ModuleHealth:
        """Get module health status."""
        issues = []
        health_score = 1.0
        
        # Check Redis connectivity
        if not self._test_redis_connection():
            issues.append("Redis connection failed")
            health_score -= 0.5
        
        # Check monitoring status
        if not self._monitoring_active:
            issues.append("Real-time monitoring not active")
            health_score -= 0.2
        
        # Determine overall status
        if health_score >= 0.8:
            status = ModuleStatus.HEALTHY
        elif health_score >= 0.5:
            status = ModuleStatus.WARNING
        else:
            status = ModuleStatus.ERROR
        
        uptime = (datetime.now() - self._start_time).total_seconds()
        
        return ModuleHealth(
            module_id='runtime_state_registry',
            status=status,
            health_score=health_score,
            issues=issues,
            last_check=datetime.now(),
            uptime_seconds=uptime,
            error_count=self._error_count,
            warning_count=self._warning_count
        )
    
    def graceful_degradation(self) -> GracefulDegradationResult:
        """Perform graceful degradation."""
        try:
            # Stop monitoring if active
            if self._monitoring_active:
                self._stop_monitoring()
            
            # Close connections
            if self.redis_client:
                self.redis_client.close()
            
            return GracefulDegradationResult(
                success=True,
                degraded_capabilities=[],
                remaining_capabilities=[ModuleCapability.CORE_FUNCTIONALITY]
            )
        except Exception as e:
            return GracefulDegradationResult(
                success=False,
                degraded_capabilities=self.get_capabilities(),
                remaining_capabilities=[],
                error_message=str(e)
            )
    
    def _resolve_redis_host(self) -> str:
        """Smart Redis host resolution with container detection."""
        # Check for explicit Redis host
        explicit_host = os.getenv('REDIS_HOST')
        if explicit_host:
            return explicit_host
        
        # Detect container environment
        if os.path.exists('/.dockerenv'):
            return "host.docker.internal"
        elif os.getenv('KUBERNETES_SERVICE_HOST'):
            return "redis-service"
        else:
            return "localhost"
    
    def _initialize_collectors(self):
        """Initialize all data collectors."""
        try:
            # Initialize Redis Data Collector
            self.redis_collector = RedisDataCollector(
                redis_host=self.redis_host,
                redis_port=self.redis_port
            )
            
            # Initialize CMS Configuration Collector
            self.cms_collector = CMSConfigurationCollector()
            
            # Initialize Prometheus Integration Collector
            self.prometheus_collector = PrometheusIntegrationCollector()
            
            # Initialize Grafana Intelligence Collector
            self.grafana_collector = GrafanaIntelligenceCollector()
            
            self._logger.info("All collectors initialized successfully")
            
        except Exception as e:
            self._logger.error(f"Failed to initialize collectors: {e}")
            # Set fallback None values
            self.redis_collector = None
            self.cms_collector = None
            self.prometheus_collector = None
            self.grafana_collector = None
    
    def _initialize_connections(self):
        """Initialize all external connections."""
        try:
            # Initialize Redis
            self.redis_client = redis.Redis(
                host=self.redis_host,
                port=self.redis_port,
                password=os.getenv('REDIS_PASSWORD', ''),
                decode_responses=True,
                socket_connect_timeout=5,
                socket_timeout=5
            )
            
            # Test Redis connection
            if self._test_redis_connection():
                self._logger.info(f"Redis connected: {self.redis_host}:{self.redis_port}")
            else:
                self._logger.warning("Redis connection failed - operating in degraded mode")
                
        except Exception as e:
            self._logger.error(f"Failed to initialize connections: {e}")
            self.redis_client = None
    
    def _test_redis_connection(self) -> bool:
        """Test Redis connection."""
        try:
            if self.redis_client:
                self.redis_client.ping()
                return True
        except Exception:
            pass
        return False
    
    async def start_monitoring(self) -> None:
        """Start real-time monitoring of all sources."""
        if self._monitoring_active:
            self._logger.warning("Monitoring already active")
            return
        
        self._monitoring_active = True
        self._monitoring_task = asyncio.create_task(self._monitoring_loop())
        self._logger.info("Started real-time monitoring")
    
    async def stop_monitoring(self) -> None:
        """Stop real-time monitoring."""
        self._monitoring_active = False
        if self._monitoring_task:
            self._monitoring_task.cancel()
            try:
                await self._monitoring_task
            except asyncio.CancelledError:
                pass
        self._logger.info("Stopped real-time monitoring")
    
    async def _monitoring_loop(self):
        """Main monitoring loop for real-time updates."""
        while self._monitoring_active:
            try:
                # Perform reconciliation cycle
                await self.reconcile_state()
                
                # Wait before next cycle
                await asyncio.sleep(30)  # 30 second reconciliation cycle
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                self._logger.error(f"Monitoring loop error: {e}")
                await asyncio.sleep(60)  # Longer wait on error
    
    async def query_state(self, query: str, use_context: bool = True) -> QueryResult:
        """Execute context-aware state query."""
        start_time = datetime.now()
        
        try:
            # For now, implement basic query processing
            # TODO: Integrate with AI Memory Palace for O(1) context queries
            result_data = await self._execute_basic_query(query)
            
            execution_time = (datetime.now() - start_time).total_seconds() * 1000
            
            return QueryResult(
                query=query,
                result_type="basic_query",
                data=result_data,
                execution_time_ms=execution_time,
                from_context=False  # TODO: Implement context integration
            )
            
        except Exception as e:
            self._logger.error(f"Query failed: {e}")
            execution_time = (datetime.now() - start_time).total_seconds() * 1000
            
            return QueryResult(
                query=query,
                result_type="error",
                data={"error": str(e)},
                execution_time_ms=execution_time,
                from_context=False
            )
    
    async def _execute_basic_query(self, query: str) -> Dict[str, Any]:
        """Execute basic query without context integration."""
        query_lower = query.lower()
        
        if "what's running" in query_lower or "list services" in query_lower:
            return await self._get_running_services()
        elif "system health" in query_lower or "health" in query_lower:
            return await self._get_system_health()
        elif "port" in query_lower:
            return await self._get_port_information()
        else:
            return {"message": f"Query '{query}' not yet implemented"}
    
    async def _get_running_services(self) -> Dict[str, Any]:
        """Get list of running services from Redis."""
        services = {}
        
        if not self.redis_client:
            return {"error": "Redis not available"}
        
        try:
            # Get ReflectiveModule active modules
            active_modules = self.redis_client.hgetall("beast_mode:active_modules")
            
            for module_id, module_data_str in active_modules.items():
                try:
                    module_data = json.loads(module_data_str)
                    services[module_id] = {
                        "status": module_data.get("status", "unknown"),
                        "host": module_data.get("host", "unknown"),
                        "module_type": module_data.get("module_type", "unknown"),
                        "registered_at": module_data.get("registered_at"),
                        "source": "redis_reflective_module"
                    }
                except json.JSONDecodeError:
                    continue
            
            # Get health keys
            health_keys = self.redis_client.keys("health:*")
            for health_key in health_keys:
                service_name = health_key.replace("health:", "")
                health_data = self.redis_client.hgetall(health_key)
                
                if service_name not in services:
                    services[service_name] = {}
                
                services[service_name].update({
                    "health_status": health_data.get("status", "unknown"),
                    "health_score": health_data.get("health_score", "unknown"),
                    "last_check": health_data.get("last_check"),
                    "uptime_seconds": health_data.get("uptime_seconds"),
                    "source": "redis_health_key"
                })
            
            return {
                "total_services": len(services),
                "services": services,
                "query_timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            self._logger.error(f"Failed to get running services: {e}")
            return {"error": str(e)}
    
    async def _get_system_health(self) -> Dict[str, Any]:
        """Get system-wide health status."""
        if not self.redis_client:
            return {"error": "Redis not available"}
        
        try:
            health_summary = {
                "overall_status": "unknown",
                "healthy_services": 0,
                "warning_services": 0,
                "error_services": 0,
                "total_services": 0,
                "services": {}
            }
            
            # Get all health keys
            health_keys = self.redis_client.keys("health:*")
            
            for health_key in health_keys:
                service_name = health_key.replace("health:", "")
                health_data = self.redis_client.hgetall(health_key)
                
                status = health_data.get("status", "unknown")
                health_score = float(health_data.get("health_score", 0.0))
                
                health_summary["services"][service_name] = {
                    "status": status,
                    "health_score": health_score,
                    "last_check": health_data.get("last_check"),
                    "uptime_seconds": health_data.get("uptime_seconds")
                }
                
                # Count by status
                if status == "healthy":
                    health_summary["healthy_services"] += 1
                elif status == "warning":
                    health_summary["warning_services"] += 1
                elif status == "error":
                    health_summary["error_services"] += 1
                
                health_summary["total_services"] += 1
            
            # Determine overall status
            if health_summary["error_services"] > 0:
                health_summary["overall_status"] = "error"
            elif health_summary["warning_services"] > 0:
                health_summary["overall_status"] = "warning"
            elif health_summary["healthy_services"] > 0:
                health_summary["overall_status"] = "healthy"
            
            return health_summary
            
        except Exception as e:
            self._logger.error(f"Failed to get system health: {e}")
            return {"error": str(e)}
    
    async def _get_port_information(self) -> Dict[str, Any]:
        """Get port binding information."""
        # TODO: Integrate with Port Conflict Detector
        return {"message": "Port information query not yet implemented"}
    
    async def get_compliance_status(self) -> Dict[str, Any]:
        """Get comprehensive compliance status."""
        # TODO: Implement three-layer compliance checking
        return {
            "overall_compliance": 0.0,
            "message": "Compliance status not yet implemented"
        }
    
    async def get_monitoring_state(self) -> Dict[str, MonitoringState]:
        """Get comprehensive monitoring state from Grafana."""
        try:
            if not self.grafana_collector:
                return {}
            
            # Collect monitoring state from Grafana
            monitoring_states = self.grafana_collector.collect_monitoring_state()
            
            self._logger.info(f"Collected monitoring state for {len(monitoring_states)} services")
            return monitoring_states
            
        except Exception as e:
            self._logger.error(f"Failed to get monitoring state: {e}")
            return {}
    
    def generate_dashboard_link(self, service_name: str, time_range: str = "1h") -> Optional[str]:
        """Generate deep-link to service dashboard."""
        try:
            if not self.grafana_collector:
                return None
            
            return self.grafana_collector.generate_dashboard_deep_link(
                service_name=service_name,
                time_range=f"now-{time_range}",
                refresh="30s"
            )
            
        except Exception as e:
            self._logger.error(f"Failed to generate dashboard link for {service_name}: {e}")
            return None
    
    async def auto_provision_monitoring(self, service_name: str, service_port: int) -> Dict[str, Any]:
        """Auto-provision monitoring for a newly discovered service."""
        try:
            if not self.grafana_collector:
                return {"error": "Grafana collector not available"}
            
            result = self.grafana_collector.auto_provision_service_monitoring(
                service_name=service_name,
                service_port=service_port,
                service_type="http"
            )
            
            self._logger.info(f"Auto-provisioned monitoring for {service_name}: {result}")
            return result
            
        except Exception as e:
            self._logger.error(f"Failed to auto-provision monitoring for {service_name}: {e}")
            return {"error": str(e)}
    
    async def reconcile_state(self) -> Dict[str, Any]:
        """Perform three-layer state reconciliation."""
        try:
            reconciliation_start = datetime.now()
            
            # Basic reconciliation - collect Redis data
            services = await self._get_running_services()
            
            # Update last reconciliation time
            self._last_reconciliation = reconciliation_start
            
            # TODO: Implement full three-layer reconciliation
            return {
                "status": "partial",
                "services_found": services.get("total_services", 0),
                "reconciliation_time": reconciliation_start.isoformat(),
                "message": "Basic reconciliation complete - full implementation pending"
            }
            
        except Exception as e:
            self._logger.error(f"State reconciliation failed: {e}")
            return {"error": str(e)}
    
    def _stop_monitoring(self):
        """Stop monitoring (synchronous version for graceful degradation)."""
        self._monitoring_active = False
        if self._monitoring_task:
            self._monitoring_task.cancel()


# CLI Interface for immediate testing
async def main():
    """Main CLI interface for testing."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Runtime State Registry")
    parser.add_argument('action', choices=['query', 'health', 'reconcile', 'monitor'],
                       help='Action to perform')
    parser.add_argument('--query', help='Query string for query action')
    parser.add_argument('--redis-host', help='Redis host override')
    
    args = parser.parse_args()
    
    # Create registry
    registry = RuntimeStateRegistry(redis_host=args.redis_host)
    
    try:
        if args.action == 'query':
            query = args.query or "what's running"
            result = await registry.query_state(query)
            print(json.dumps(result.data, indent=2))
        
        elif args.action == 'health':
            health = registry.get_health_status()
            print(f"Status: {health.status.value}")
            print(f"Health Score: {health.health_score}")
            if health.issues:
                print("Issues:")
                for issue in health.issues:
                    print(f"  - {issue}")
        
        elif args.action == 'reconcile':
            result = await registry.reconcile_state()
            print(json.dumps(result, indent=2))
        
        elif args.action == 'monitor':
            print("Starting monitoring... Press Ctrl+C to stop")
            await registry.start_monitoring()
            try:
                while True:
                    await asyncio.sleep(1)
            except KeyboardInterrupt:
                await registry.stop_monitoring()
                print("Monitoring stopped")
    
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())