#!/usr/bin/env python3
"""
Prometheus Integration Collector for Runtime State Registry

Collects service discovery data from Prometheus targets and metrics,
providing authoritative source for service health and relationships.
"""

import os
import sys
import json
import asyncio
import logging
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from src.rm_ddd.core.unified_reflective_module import (
    ReflectiveModule, ModuleCapability, ModuleHealth, ModuleStatus, 
    GracefulDegradationResult
)
from ..core.models import PrometheusServiceData, ServiceStatus


class PrometheusIntegrationCollector(ReflectiveModule):
    """
    Collects service discovery data from Prometheus.
    
    Provides authoritative source for:
    - Service discovery targets (what Prometheus knows about)
    - Service health status from 'up' metrics
    - Service relationships from metric dependencies
    - Performance metrics and trends
    """
    
    def __init__(self, prometheus_url: str = None):
        super().__init__()
        
        # Prometheus connection configuration
        self.prometheus_url = prometheus_url or os.getenv('PROMETHEUS_URL', 'http://localhost:9090')
        
        # Data storage
        self._service_data: Dict[str, PrometheusServiceData] = {}
        self._targets_data: List[Dict[str, Any]] = []
        self._metrics_data: Dict[str, Dict[str, float]] = {}
        self._last_collection: Optional[datetime] = None
        
        # Request session for connection pooling
        self.session = requests.Session()
        self.session.timeout = 10
    
    def get_module_info(self) -> Dict[str, Any]:
        """Get module information."""
        return {
            'module_id': 'prometheus_integration_collector',
            'version': '1.0.0',
            'description': 'Prometheus integration for Runtime State Registry',
            'prometheus_url': self.prometheus_url
        }
    
    def get_capabilities(self) -> List[ModuleCapability]:
        """Get module capabilities."""
        return [
            ModuleCapability.DATA_PROCESSING,
            ModuleCapability.API_INTEGRATION,
            ModuleCapability.MONITORING
        ]
    
    def get_health_status(self) -> ModuleHealth:
        """Get module health status."""
        issues = []
        health_score = 1.0
        
        # Check Prometheus connectivity
        if not self._test_prometheus_connection():
            issues.append("Prometheus connection failed")
            health_score -= 0.7
        
        # Check data freshness
        if self._last_collection and (datetime.now() - self._last_collection).seconds > 300:
            issues.append("Data collection stale (>5 minutes)")
            health_score -= 0.2
        
        # Check targets availability
        if not self._targets_data:
            issues.append("No Prometheus targets discovered")
            health_score -= 0.1
        
        # Determine overall status
        if health_score >= 0.8:
            status = ModuleStatus.HEALTHY
        elif health_score >= 0.5:
            status = ModuleStatus.WARNING
        else:
            status = ModuleStatus.ERROR
        
        uptime = (datetime.now() - self._start_time).total_seconds()
        
        return ModuleHealth(
            module_id='prometheus_integration_collector',
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
            # Close session
            if self.session:
                self.session.close()
            
            return GracefulDegradationResult(
                success=True,
                degraded_capabilities=[ModuleCapability.API_INTEGRATION],
                remaining_capabilities=[ModuleCapability.DATA_PROCESSING]
            )
        except Exception as e:
            return GracefulDegradationResult(
                success=False,
                degraded_capabilities=self.get_capabilities(),
                remaining_capabilities=[],
                error_message=str(e)
            )
    
    def _test_prometheus_connection(self) -> bool:
        """Test Prometheus connection."""
        try:
            response = self.session.get(f"{self.prometheus_url}/api/v1/status/buildinfo")
            return response.status_code == 200
        except Exception:
            return False
    
    async def collect_all_prometheus_data(self) -> Dict[str, PrometheusServiceData]:
        """Collect all Prometheus data."""
        try:
            self._service_data.clear()
            
            # Collect service discovery targets
            await self._collect_service_targets()
            
            # Collect service health metrics
            await self._collect_health_metrics()
            
            # Collect service relationships
            await self._collect_service_relationships()
            
            self._last_collection = datetime.now()
            self._logger.info(f"Collected Prometheus data for {len(self._service_data)} services")
            
            return self._service_data.copy()
            
        except Exception as e:
            self._logger.error(f"Prometheus data collection failed: {e}")
            self._increment_error_count()
            return {}
    
    async def _collect_service_targets(self):
        """Collect Prometheus service discovery targets."""
        try:
            response = self.session.get(f"{self.prometheus_url}/api/v1/targets")
            if response.status_code != 200:
                self._logger.error(f"Failed to get targets: HTTP {response.status_code}")
                return
            
            targets_data = response.json()
            self._targets_data = targets_data.get('data', {}).get('activeTargets', [])
            
            # Process each target
            for target in self._targets_data:
                labels = target.get('labels', {})
                job = labels.get('job', 'unknown')
                instance = labels.get('instance', 'unknown')
                
                # Create service name from job and instance
                service_name = self._generate_service_name(job, instance)
                
                # Parse health status
                health = target.get('health', 'unknown')
                if health == 'up':
                    health_status = ServiceStatus.HEALTHY
                elif health == 'down':
                    health_status = ServiceStatus.ERROR
                else:
                    health_status = ServiceStatus.UNKNOWN
                
                # Parse last scrape time
                last_scrape = None
                if 'lastScrape' in target:
                    try:
                        last_scrape = datetime.fromisoformat(
                            target['lastScrape'].replace('Z', '+00:00')
                        )
                    except (ValueError, AttributeError):
                        pass
                
                # Create or update service data
                if service_name not in self._service_data:
                    self._service_data[service_name] = PrometheusServiceData()
                
                service_data = self._service_data[service_name]
                service_data.target_info = target
                service_data.health_status = health_status
                service_data.labels = labels
                service_data.last_scrape = last_scrape
                
        except Exception as e:
            self._logger.error(f"Failed to collect service targets: {e}")
    
    def _generate_service_name(self, job: str, instance: str) -> str:
        """Generate consistent service name from Prometheus job and instance."""
        # Clean up job name
        if job in ['prometheus', 'grafana', 'jaeger', 'beast-mode']:
            return job
        
        # Extract service name from instance if it contains a hostname
        if ':' in instance:
            host_part = instance.split(':')[0]
            if '.' in host_part:
                # Extract service name from hostname like "grafana.kiro.local"
                service_part = host_part.split('.')[0]
                if service_part != 'localhost':
                    return service_part
        
        # Fallback to job name
        return job.replace('-', '_')
    
    async def _collect_health_metrics(self):
        """Collect service health metrics from Prometheus."""
        try:
            # Query 'up' metric for all services
            response = self.session.get(
                f"{self.prometheus_url}/api/v1/query",
                params={'query': 'up'}
            )
            
            if response.status_code != 200:
                self._logger.error(f"Failed to get health metrics: HTTP {response.status_code}")
                return
            
            metrics_data = response.json()
            results = metrics_data.get('data', {}).get('result', [])
            
            for result in results:
                metric = result.get('metric', {})
                value = result.get('value', [None, '0'])
                
                job = metric.get('job', 'unknown')
                instance = metric.get('instance', 'unknown')
                service_name = self._generate_service_name(job, instance)
                
                # Parse metric value
                try:
                    up_value = float(value[1])
                    health_status = ServiceStatus.HEALTHY if up_value == 1.0 else ServiceStatus.ERROR
                except (ValueError, IndexError):
                    health_status = ServiceStatus.UNKNOWN
                
                # Update service data
                if service_name not in self._service_data:
                    self._service_data[service_name] = PrometheusServiceData()
                
                service_data = self._service_data[service_name]
                service_data.health_status = health_status
                service_data.metrics['up'] = up_value
                service_data.labels.update(metric)
                
        except Exception as e:
            self._logger.error(f"Failed to collect health metrics: {e}")
    
    async def _collect_service_relationships(self):
        """Collect service relationships from metric dependencies."""
        try:
            # Query for common relationship metrics
            relationship_queries = [
                'http_requests_total',
                'http_request_duration_seconds',
                'redis_connected_clients',
                'database_connections'
            ]
            
            for query in relationship_queries:
                try:
                    response = self.session.get(
                        f"{self.prometheus_url}/api/v1/query",
                        params={'query': query}
                    )
                    
                    if response.status_code == 200:
                        metrics_data = response.json()
                        results = metrics_data.get('data', {}).get('result', [])
                        
                        for result in results:
                            metric = result.get('metric', {})
                            value = result.get('value', [None, '0'])
                            
                            job = metric.get('job', 'unknown')
                            instance = metric.get('instance', 'unknown')
                            service_name = self._generate_service_name(job, instance)
                            
                            # Update metrics for this service
                            if service_name in self._service_data:
                                try:
                                    metric_value = float(value[1])
                                    self._service_data[service_name].metrics[query] = metric_value
                                except (ValueError, IndexError):
                                    pass
                                    
                except Exception as e:
                    self._logger.debug(f"Query {query} failed: {e}")
                    continue
                    
        except Exception as e:
            self._logger.error(f"Failed to collect service relationships: {e}")
    
    def get_service_data(self, service_name: str) -> Optional[PrometheusServiceData]:
        """Get Prometheus data for a specific service."""
        return self._service_data.get(service_name)
    
    def get_all_service_data(self) -> Dict[str, PrometheusServiceData]:
        """Get all collected Prometheus service data."""
        return self._service_data.copy()
    
    def get_targets_data(self) -> List[Dict[str, Any]]:
        """Get raw Prometheus targets data."""
        return self._targets_data.copy()
    
    def generate_promql_query(self, service_name: str, metric_name: str) -> str:
        """Generate PromQL query for a specific service and metric."""
        service_data = self._service_data.get(service_name)
        if not service_data or not service_data.labels:
            return f'{metric_name}{{job="{service_name}"}}'
        
        # Build query with known labels
        label_filters = []
        for key, value in service_data.labels.items():
            if key in ['job', 'instance']:
                label_filters.append(f'{key}="{value}"')
        
        if label_filters:
            return f'{metric_name}{{{",".join(label_filters)}}}'
        else:
            return f'{metric_name}{{job="{service_name}"}}'
    
    def get_service_health_summary(self) -> Dict[str, Any]:
        """Get summary of service health from Prometheus perspective."""
        summary = {
            'total_services': len(self._service_data),
            'healthy_services': 0,
            'error_services': 0,
            'unknown_services': 0,
            'services': {}
        }
        
        for service_name, service_data in self._service_data.items():
            status = service_data.health_status
            summary['services'][service_name] = {
                'status': status.value,
                'up_metric': service_data.metrics.get('up', 'unknown'),
                'last_scrape': service_data.last_scrape.isoformat() if service_data.last_scrape else None
            }
            
            if status == ServiceStatus.HEALTHY:
                summary['healthy_services'] += 1
            elif status == ServiceStatus.ERROR:
                summary['error_services'] += 1
            else:
                summary['unknown_services'] += 1
        
        return summary


# CLI interface for testing
async def main():
    """Main CLI interface for testing."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Prometheus Integration Collector")
    parser.add_argument('action', choices=['collect', 'health', 'targets', 'query'],
                       help='Action to perform')
    parser.add_argument('--prometheus-url', help='Prometheus URL override')
    parser.add_argument('--service', help='Service name for query generation')
    parser.add_argument('--metric', help='Metric name for query generation')
    
    args = parser.parse_args()
    
    collector = PrometheusIntegrationCollector(prometheus_url=args.prometheus_url)
    
    try:
        if args.action == 'collect':
            data = await collector.collect_all_prometheus_data()
            print(f"Collected Prometheus data for {len(data)} services:")
            for service_name, prom_data in data.items():
                print(f"  - {service_name}: {prom_data.health_status.value}")
                print(f"    Metrics: {list(prom_data.metrics.keys())}")
        
        elif args.action == 'health':
            health = collector.get_health_status()
            print(f"Status: {health.status.value}")
            print(f"Health Score: {health.health_score}")
            if health.issues:
                print("Issues:")
                for issue in health.issues:
                    print(f"  - {issue}")
        
        elif args.action == 'targets':
            targets = collector.get_targets_data()
            print(f"Prometheus Targets ({len(targets)}):")
            for target in targets:
                labels = target.get('labels', {})
                health = target.get('health', 'unknown')
                job = labels.get('job', 'unknown')
                instance = labels.get('instance', 'unknown')
                print(f"  - {job} ({instance}): {health}")
        
        elif args.action == 'query':
            if not args.service or not args.metric:
                print("--service and --metric required for query generation")
                sys.exit(1)
            
            query = collector.generate_promql_query(args.service, args.metric)
            print(f"Generated PromQL query: {query}")
    
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())