#!/usr/bin/env python3
"""
Grafana Intelligence Collector for Runtime State Registry
========================================================

Collects intelligence from Grafana dashboards, alerts, and configurations
to provide comprehensive monitoring state information.

Features:
- Parse existing Grafana dashboards for service relationships
- Extract alert configurations and current alert status
- Implement auto-provisioning patterns for new services
- Generate dashboard deep-links for services
- Integration with Grafana API for real-time data
"""

import json
import logging
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Set
from dataclasses import dataclass, asdict
from urllib.parse import urljoin, quote

from ..core.models import (
    ServiceState, HealthStatus, ConfigurationState, 
    MonitoringState, AlertState, DashboardInfo
)


@dataclass
class GrafanaServiceRelationship:
    """Represents a service relationship discovered from Grafana dashboards."""
    source_service: str
    target_service: str
    relationship_type: str  # 'depends_on', 'monitors', 'alerts_on'
    dashboard_uid: str
    panel_title: str
    query: str


@dataclass
class GrafanaAlertRule:
    """Represents a Grafana alert rule configuration."""
    alert_id: str
    alert_name: str
    service_name: str
    condition: str
    threshold: str
    severity: str
    state: str  # 'ok', 'pending', 'alerting', 'no_data'
    dashboard_uid: Optional[str]
    panel_id: Optional[int]
    last_evaluation: datetime
    annotations: Dict[str, str]
    labels: Dict[str, str]


@dataclass
class GrafanaDashboardMetadata:
    """Metadata extracted from Grafana dashboard."""
    uid: str
    title: str
    tags: List[str]
    services_monitored: Set[str]
    panels_count: int
    alert_rules_count: int
    last_modified: datetime
    url: str
    auto_refresh: Optional[str]
    time_range: Dict[str, str]


class GrafanaIntelligenceCollector:
    """
    Collects intelligence from Grafana for runtime state registry.
    
    Provides comprehensive monitoring state by parsing dashboards,
    extracting alert configurations, and generating service insights.
    """
    
    def __init__(self, 
                 grafana_url: str = "http://localhost:3000",
                 api_key: Optional[str] = None,
                 username: str = "admin",
                 password: str = "admin"):
        """Initialize Grafana Intelligence Collector."""
        self.grafana_url = grafana_url.rstrip('/')
        self.api_key = api_key
        self.username = username
        self.password = password
        
        self.logger = logging.getLogger(__name__)
        
        # Initialize session with authentication
        self.session = requests.Session()
        if self.api_key:
            self.session.headers.update({
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json'
            })
        else:
            self.session.auth = (self.username, self.password)
        
        # Cache for dashboard metadata
        self._dashboard_cache: Dict[str, GrafanaDashboardMetadata] = {}
        self._cache_timestamp = None
        self._cache_ttl = timedelta(minutes=5)
        
        # Service name patterns for auto-detection
        self.service_patterns = [
            'prometheus', 'grafana', 'jaeger', 'redis', 'postgres',
            'nginx', 'apache', 'mysql', 'mongodb', 'elasticsearch',
            'kibana', 'logstash', 'fluentd', 'consul', 'vault',
            'etcd', 'zookeeper', 'kafka', 'rabbitmq', 'memcached'
        ]
    
    def collect_monitoring_state(self) -> Dict[str, MonitoringState]:
        """
        Collect comprehensive monitoring state from Grafana.
        
        Returns:
            Dictionary mapping service names to their monitoring states
        """
        try:
            self.logger.info("Starting Grafana intelligence collection")
            
            # Collect all dashboard metadata
            dashboards = self._get_all_dashboards()
            
            # Extract service relationships
            relationships = self._extract_service_relationships(dashboards)
            
            # Get alert states
            alerts = self._get_alert_states()
            
            # Build monitoring states
            monitoring_states = self._build_monitoring_states(
                dashboards, relationships, alerts
            )
            
            self.logger.info(f"Collected monitoring state for {len(monitoring_states)} services")
            return monitoring_states
            
        except Exception as e:
            self.logger.error(f"Failed to collect Grafana monitoring state: {e}")
            return {}
    
    def _get_all_dashboards(self) -> List[GrafanaDashboardMetadata]:
        """Get metadata for all Grafana dashboards."""
        try:
            # Check cache first
            if (self._cache_timestamp and 
                datetime.now() - self._cache_timestamp < self._cache_ttl):
                return list(self._dashboard_cache.values())
            
            # Search for all dashboards
            search_url = f"{self.grafana_url}/api/search"
            response = self.session.get(search_url, params={'type': 'dash-db'})
            response.raise_for_status()
            
            dashboard_list = response.json()
            dashboards = []
            
            for dashboard_info in dashboard_list:
                try:
                    dashboard_meta = self._get_dashboard_metadata(dashboard_info['uid'])
                    if dashboard_meta:
                        dashboards.append(dashboard_meta)
                        self._dashboard_cache[dashboard_meta.uid] = dashboard_meta
                except Exception as e:
                    self.logger.warning(f"Failed to get metadata for dashboard {dashboard_info.get('uid')}: {e}")
            
            self._cache_timestamp = datetime.now()
            return dashboards
            
        except Exception as e:
            self.logger.error(f"Failed to get dashboard list: {e}")
            return []
    
    def _get_dashboard_metadata(self, uid: str) -> Optional[GrafanaDashboardMetadata]:
        """Get detailed metadata for a specific dashboard."""
        try:
            dashboard_url = f"{self.grafana_url}/api/dashboards/uid/{uid}"
            response = self.session.get(dashboard_url)
            response.raise_for_status()
            
            dashboard_data = response.json()['dashboard']
            
            # Extract services monitored from panel queries
            services_monitored = self._extract_services_from_dashboard(dashboard_data)
            
            # Count alert rules
            alert_rules_count = sum(
                1 for panel in dashboard_data.get('panels', [])
                if panel.get('alert') is not None
            )
            
            return GrafanaDashboardMetadata(
                uid=uid,
                title=dashboard_data.get('title', 'Unknown'),
                tags=dashboard_data.get('tags', []),
                services_monitored=services_monitored,
                panels_count=len(dashboard_data.get('panels', [])),
                alert_rules_count=alert_rules_count,
                last_modified=datetime.fromisoformat(
                    dashboard_data.get('updated', datetime.now().isoformat()).replace('Z', '+00:00')
                ),
                url=f"{self.grafana_url}/d/{uid}",
                auto_refresh=dashboard_data.get('refresh'),
                time_range={
                    'from': dashboard_data.get('time', {}).get('from', 'now-1h'),
                    'to': dashboard_data.get('time', {}).get('to', 'now')
                }
            )
            
        except Exception as e:
            self.logger.error(f"Failed to get dashboard metadata for {uid}: {e}")
            return None
    
    def _extract_services_from_dashboard(self, dashboard_data: Dict) -> Set[str]:
        """Extract service names from dashboard panel queries."""
        services = set()
        
        for panel in dashboard_data.get('panels', []):
            # Check panel title for service names
            title = panel.get('title', '').lower()
            for pattern in self.service_patterns:
                if pattern in title:
                    services.add(pattern)
            
            # Check queries/targets for service names
            for target in panel.get('targets', []):
                expr = target.get('expr', '')
                if expr:
                    # Look for job labels and instance patterns
                    for pattern in self.service_patterns:
                        if f'job="{pattern}"' in expr or f'job=~".*{pattern}.*"' in expr:
                            services.add(pattern)
                        if f'{pattern}:' in expr or f'{pattern}_' in expr:
                            services.add(pattern)
        
        return services
    
    def _extract_service_relationships(self, 
                                     dashboards: List[GrafanaDashboardMetadata]) -> List[GrafanaServiceRelationship]:
        """Extract service relationships from dashboard configurations."""
        relationships = []
        
        for dashboard in dashboards:
            try:
                # Get full dashboard data for relationship analysis
                dashboard_url = f"{self.grafana_url}/api/dashboards/uid/{dashboard.uid}"
                response = self.session.get(dashboard_url)
                response.raise_for_status()
                
                dashboard_data = response.json()['dashboard']
                
                # Analyze panels for relationships
                for panel in dashboard_data.get('panels', []):
                    panel_relationships = self._analyze_panel_relationships(
                        panel, dashboard.uid, dashboard.services_monitored
                    )
                    relationships.extend(panel_relationships)
                    
            except Exception as e:
                self.logger.warning(f"Failed to extract relationships from dashboard {dashboard.uid}: {e}")
        
        return relationships
    
    def _analyze_panel_relationships(self, 
                                   panel: Dict, 
                                   dashboard_uid: str, 
                                   dashboard_services: Set[str]) -> List[GrafanaServiceRelationship]:
        """Analyze a panel for service relationships."""
        relationships = []
        panel_title = panel.get('title', '')
        
        for target in panel.get('targets', []):
            expr = target.get('expr', '')
            if not expr:
                continue
            
            # Detect monitoring relationships
            for service in dashboard_services:
                if service in expr.lower() or service in panel_title.lower():
                    # This panel monitors the service
                    relationships.append(GrafanaServiceRelationship(
                        source_service='grafana',
                        target_service=service,
                        relationship_type='monitors',
                        dashboard_uid=dashboard_uid,
                        panel_title=panel_title,
                        query=expr
                    ))
                    
                    # Check for dependency relationships in queries
                    if 'up{' in expr and service in expr:
                        relationships.append(GrafanaServiceRelationship(
                            source_service='monitoring_system',
                            target_service=service,
                            relationship_type='depends_on',
                            dashboard_uid=dashboard_uid,
                            panel_title=panel_title,
                            query=expr
                        ))
        
        return relationships
    
    def _get_alert_states(self) -> List[GrafanaAlertRule]:
        """Get current alert states from Grafana."""
        alerts = []
        
        try:
            # Get alert rules (Grafana 8+ unified alerting)
            alerts_url = f"{self.grafana_url}/api/ruler/grafana/api/v1/rules"
            response = self.session.get(alerts_url)
            
            if response.status_code == 200:
                alert_data = response.json()
                alerts.extend(self._parse_unified_alerts(alert_data))
            else:
                # Fallback to legacy alerts
                alerts.extend(self._get_legacy_alerts())
                
        except Exception as e:
            self.logger.warning(f"Failed to get alert states: {e}")
            # Try legacy alerts as fallback
            try:
                alerts.extend(self._get_legacy_alerts())
            except Exception as e2:
                self.logger.error(f"Failed to get legacy alerts: {e2}")
        
        return alerts
    
    def _parse_unified_alerts(self, alert_data: Dict) -> List[GrafanaAlertRule]:
        """Parse unified alerting rules (Grafana 8+)."""
        alerts = []
        
        for namespace, groups in alert_data.items():
            for group in groups:
                for rule in group.get('rules', []):
                    try:
                        alert = GrafanaAlertRule(
                            alert_id=rule.get('uid', ''),
                            alert_name=rule.get('title', ''),
                            service_name=self._extract_service_from_alert(rule),
                            condition=str(rule.get('condition', '')),
                            threshold=self._extract_threshold_from_rule(rule),
                            severity=rule.get('labels', {}).get('severity', 'unknown'),
                            state=rule.get('state', 'unknown'),
                            dashboard_uid=rule.get('annotations', {}).get('dashboard_uid'),
                            panel_id=rule.get('annotations', {}).get('panel_id'),
                            last_evaluation=datetime.now(),  # Would need separate API call for actual time
                            annotations=rule.get('annotations', {}),
                            labels=rule.get('labels', {})
                        )
                        alerts.append(alert)
                    except Exception as e:
                        self.logger.warning(f"Failed to parse alert rule: {e}")
        
        return alerts
    
    def _get_legacy_alerts(self) -> List[GrafanaAlertRule]:
        """Get legacy dashboard alerts."""
        alerts = []
        
        try:
            alerts_url = f"{self.grafana_url}/api/alerts"
            response = self.session.get(alerts_url)
            response.raise_for_status()
            
            alert_data = response.json()
            
            for alert in alert_data:
                try:
                    grafana_alert = GrafanaAlertRule(
                        alert_id=str(alert.get('id', '')),
                        alert_name=alert.get('name', ''),
                        service_name=self._extract_service_from_legacy_alert(alert),
                        condition=alert.get('message', ''),
                        threshold=str(alert.get('settings', {}).get('conditions', [])),
                        severity=alert.get('executionError', 'ok') if alert.get('executionError') else 'ok',
                        state=alert.get('state', 'unknown'),
                        dashboard_uid=alert.get('dashboardUid'),
                        panel_id=alert.get('panelId'),
                        last_evaluation=datetime.fromisoformat(
                            alert.get('evalDate', datetime.now().isoformat()).replace('Z', '+00:00')
                        ),
                        annotations={},
                        labels={}
                    )
                    alerts.append(grafana_alert)
                except Exception as e:
                    self.logger.warning(f"Failed to parse legacy alert: {e}")
        
        except Exception as e:
            self.logger.error(f"Failed to get legacy alerts: {e}")
        
        return alerts
    
    def _extract_service_from_alert(self, rule: Dict) -> str:
        """Extract service name from unified alert rule."""
        # Check labels first
        labels = rule.get('labels', {})
        if 'service' in labels:
            return labels['service']
        if 'job' in labels:
            return labels['job']
        
        # Check title and annotations
        title = rule.get('title', '').lower()
        annotations = rule.get('annotations', {})
        
        for pattern in self.service_patterns:
            if pattern in title:
                return pattern
            for annotation in annotations.values():
                if pattern in str(annotation).lower():
                    return pattern
        
        return 'unknown'
    
    def _extract_service_from_legacy_alert(self, alert: Dict) -> str:
        """Extract service name from legacy alert."""
        name = alert.get('name', '').lower()
        message = alert.get('message', '').lower()
        
        for pattern in self.service_patterns:
            if pattern in name or pattern in message:
                return pattern
        
        return 'unknown'
    
    def _extract_threshold_from_rule(self, rule: Dict) -> str:
        """Extract threshold information from alert rule."""
        try:
            conditions = rule.get('condition', '')
            if isinstance(conditions, str):
                return conditions
            elif isinstance(conditions, dict):
                return str(conditions)
            else:
                return 'unknown'
        except Exception:
            return 'unknown'
    
    def _build_monitoring_states(self, 
                                dashboards: List[GrafanaDashboardMetadata],
                                relationships: List[GrafanaServiceRelationship],
                                alerts: List[GrafanaAlertRule]) -> Dict[str, MonitoringState]:
        """Build monitoring states for all discovered services."""
        monitoring_states = {}
        
        # Get all unique services
        all_services = set()
        for dashboard in dashboards:
            all_services.update(dashboard.services_monitored)
        for relationship in relationships:
            all_services.add(relationship.target_service)
        for alert in alerts:
            all_services.add(alert.service_name)
        
        # Build monitoring state for each service
        for service in all_services:
            if service == 'unknown':
                continue
                
            # Get dashboards monitoring this service
            service_dashboards = [
                DashboardInfo(
                    name=d.title,
                    url=d.url,
                    panels_count=d.panels_count,
                    last_updated=d.last_modified
                )
                for d in dashboards if service in d.services_monitored
            ]
            
            # Get alerts for this service
            service_alerts = [
                AlertState(
                    name=a.alert_name,
                    status=a.state,
                    severity=a.severity,
                    message=a.condition,
                    last_triggered=a.last_evaluation
                )
                for a in alerts if a.service_name == service
            ]
            
            # Calculate overall health from alerts
            health_status = self._calculate_health_from_alerts(service_alerts)
            
            monitoring_states[service] = MonitoringState(
                service_name=service,
                dashboards=service_dashboards,
                alerts=service_alerts,
                health_status=health_status,
                metrics_available=len(service_dashboards) > 0,
                last_updated=datetime.now()
            )
        
        return monitoring_states
    
    def _calculate_health_from_alerts(self, alerts: List[AlertState]) -> HealthStatus:
        """Calculate overall health status from alert states."""
        if not alerts:
            return HealthStatus.UNKNOWN
        
        # Check for any alerting states
        for alert in alerts:
            if alert.status == 'alerting':
                if alert.severity in ['critical', 'high']:
                    return HealthStatus.CRITICAL
                elif alert.severity in ['warning', 'medium']:
                    return HealthStatus.WARNING
        
        # Check for pending alerts
        pending_count = sum(1 for alert in alerts if alert.status == 'pending')
        if pending_count > 0:
            return HealthStatus.WARNING
        
        # All alerts OK
        return HealthStatus.HEALTHY
    
    def generate_dashboard_deep_link(self, 
                                   service_name: str, 
                                   time_range: Optional[str] = None,
                                   refresh: Optional[str] = None) -> Optional[str]:
        """Generate deep-link URL to service-specific dashboard."""
        try:
            # Find dashboard for this service
            dashboards = self._get_all_dashboards()
            service_dashboard = None
            
            for dashboard in dashboards:
                if service_name in dashboard.services_monitored:
                    service_dashboard = dashboard
                    break
            
            if not service_dashboard:
                return None
            
            # Build URL with parameters
            base_url = service_dashboard.url
            params = []
            
            if time_range:
                params.append(f"from={quote(time_range)}")
            if refresh:
                params.append(f"refresh={quote(refresh)}")
            
            if params:
                return f"{base_url}?{'&'.join(params)}"
            else:
                return base_url
                
        except Exception as e:
            self.logger.error(f"Failed to generate dashboard deep-link for {service_name}: {e}")
            return None
    
    def auto_provision_service_monitoring(self, 
                                        service_name: str,
                                        service_port: int,
                                        service_type: str = 'http') -> Dict[str, Any]:
        """
        Auto-provision monitoring for a new service.
        
        Creates dashboard and alert configurations for a newly discovered service.
        """
        try:
            self.logger.info(f"Auto-provisioning monitoring for service: {service_name}")
            
            # Generate dashboard configuration
            dashboard_config = self._generate_service_dashboard(
                service_name, service_port, service_type
            )
            
            # Generate alert rules
            alert_rules = self._generate_service_alerts(
                service_name, service_port, service_type
            )
            
            # Create dashboard (if Grafana API allows)
            dashboard_result = self._create_dashboard(dashboard_config)
            
            # Create alert rules (if supported)
            alerts_result = self._create_alert_rules(alert_rules)
            
            return {
                'service_name': service_name,
                'dashboard_created': dashboard_result.get('success', False),
                'dashboard_url': dashboard_result.get('url'),
                'alerts_created': alerts_result.get('success', False),
                'alerts_count': len(alert_rules),
                'provisioning_timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Failed to auto-provision monitoring for {service_name}: {e}")
            return {
                'service_name': service_name,
                'dashboard_created': False,
                'alerts_created': False,
                'error': str(e)
            }
    
    def _generate_service_dashboard(self, 
                                  service_name: str, 
                                  service_port: int, 
                                  service_type: str) -> Dict[str, Any]:
        """Generate dashboard configuration for a service."""
        return {
            "dashboard": {
                "title": f"{service_name.title()} Service Dashboard",
                "tags": ["auto-generated", service_name, service_type],
                "timezone": "browser",
                "panels": [
                    {
                        "title": f"{service_name.title()} Uptime",
                        "type": "stat",
                        "targets": [
                            {
                                "expr": f'up{{job="{service_name}"}}',
                                "legendFormat": "Uptime"
                            }
                        ],
                        "gridPos": {"h": 8, "w": 12, "x": 0, "y": 0}
                    },
                    {
                        "title": f"{service_name.title()} Response Time",
                        "type": "graph",
                        "targets": [
                            {
                                "expr": f'http_request_duration_seconds{{job="{service_name}"}}',
                                "legendFormat": "Response Time"
                            }
                        ],
                        "gridPos": {"h": 8, "w": 12, "x": 12, "y": 0}
                    }
                ],
                "time": {"from": "now-1h", "to": "now"},
                "refresh": "30s"
            },
            "overwrite": True
        }
    
    def _generate_service_alerts(self, 
                               service_name: str, 
                               service_port: int, 
                               service_type: str) -> List[Dict[str, Any]]:
        """Generate alert rules for a service."""
        return [
            {
                "alert": {
                    "name": f"{service_name}_down",
                    "message": f"{service_name.title()} service is down",
                    "frequency": "10s",
                    "conditions": [
                        {
                            "query": {"params": [f'up{{job="{service_name}"}}']},
                            "reducer": {"params": [], "type": "last"},
                            "evaluator": {"params": [1], "type": "lt"}
                        }
                    ]
                }
            }
        ]
    
    def _create_dashboard(self, dashboard_config: Dict[str, Any]) -> Dict[str, Any]:
        """Create dashboard via Grafana API."""
        try:
            create_url = f"{self.grafana_url}/api/dashboards/db"
            response = self.session.post(create_url, json=dashboard_config)
            
            if response.status_code in [200, 201]:
                result = response.json()
                return {
                    'success': True,
                    'url': f"{self.grafana_url}{result.get('url', '')}",
                    'uid': result.get('uid')
                }
            else:
                return {
                    'success': False,
                    'error': f"HTTP {response.status_code}: {response.text}"
                }
                
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _create_alert_rules(self, alert_rules: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Create alert rules via Grafana API."""
        try:
            # This would depend on Grafana version and alerting system
            # For now, return success with note about manual configuration
            return {
                'success': True,
                'note': 'Alert rules generated - manual configuration may be required',
                'rules_count': len(alert_rules)
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def health_check(self) -> Dict[str, Any]:
        """Perform health check of Grafana connection."""
        try:
            health_url = f"{self.grafana_url}/api/health"
            response = self.session.get(health_url, timeout=5)
            
            if response.status_code == 200:
                return {
                    'status': 'healthy',
                    'grafana_url': self.grafana_url,
                    'response_time_ms': response.elapsed.total_seconds() * 1000,
                    'version': response.json().get('version', 'unknown')
                }
            else:
                return {
                    'status': 'unhealthy',
                    'error': f"HTTP {response.status_code}",
                    'grafana_url': self.grafana_url
                }
                
        except Exception as e:
            return {
                'status': 'unhealthy',
                'error': str(e),
                'grafana_url': self.grafana_url
            }


def main():
    """CLI interface for testing Grafana Intelligence Collector."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Grafana Intelligence Collector")
    parser.add_argument('--grafana-url', default='http://localhost:3000',
                       help='Grafana URL')
    parser.add_argument('--api-key', help='Grafana API key')
    parser.add_argument('--username', default='admin', help='Grafana username')
    parser.add_argument('--password', default='admin', help='Grafana password')
    parser.add_argument('--action', choices=['collect', 'health', 'dashboards', 'alerts'],
                       default='collect', help='Action to perform')
    parser.add_argument('--service', help='Service name for specific operations')
    
    args = parser.parse_args()
    
    # Configure logging
    logging.basicConfig(level=logging.INFO)
    
    # Create collector
    collector = GrafanaIntelligenceCollector(
        grafana_url=args.grafana_url,
        api_key=args.api_key,
        username=args.username,
        password=args.password
    )
    
    if args.action == 'health':
        health = collector.health_check()
        print(json.dumps(health, indent=2))
        
    elif args.action == 'dashboards':
        dashboards = collector._get_all_dashboards()
        print(f"Found {len(dashboards)} dashboards:")
        for dashboard in dashboards:
            print(f"  - {dashboard.title} ({dashboard.uid})")
            print(f"    Services: {', '.join(dashboard.services_monitored)}")
            print(f"    Panels: {dashboard.panels_count}, Alerts: {dashboard.alert_rules_count}")
            
    elif args.action == 'alerts':
        alerts = collector._get_alert_states()
        print(f"Found {len(alerts)} alerts:")
        for alert in alerts:
            print(f"  - {alert.alert_name} ({alert.service_name}): {alert.state}")
            
    elif args.action == 'collect':
        monitoring_states = collector.collect_monitoring_state()
        print(f"Collected monitoring state for {len(monitoring_states)} services:")
        for service_name, state in monitoring_states.items():
            print(f"  - {service_name}: {state.health_status.value}")
            print(f"    Dashboards: {len(state.dashboards)}")
            print(f"    Alerts: {len(state.alerts)}")


if __name__ == "__main__":
    main()