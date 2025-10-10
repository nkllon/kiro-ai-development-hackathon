#!/usr/bin/env python3
"""
CMS Configuration Collector for Runtime State Registry

Collects canonical configuration data from Directus CMS for service definitions,
compliance policies, and configuration templates.
"""

import os
import sys
import json
import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from src.rm_ddd.core.unified_reflective_module import (
    ReflectiveModule, ModuleCapability, ModuleHealth, ModuleStatus, 
    GracefulDegradationResult
)
from ..core.models import CMSServiceData, ServiceStatus


class CMSConfigurationCollector(ReflectiveModule):
    """
    Collects canonical configuration data from Directus CMS.
    
    Provides authoritative source for:
    - Service definitions and expected configurations
    - Compliance policies and validation rules
    - Configuration templates for new services
    - Canonical service metadata
    """
    
    def __init__(self, cms_url: str = None, cms_token: str = None):
        super().__init__()
        
        # CMS connection configuration
        self.cms_url = cms_url or os.getenv('DIRECTUS_URL', 'http://localhost:8055')
        self.cms_token = cms_token or os.getenv('DIRECTUS_TOKEN')
        self.cms_client = None
        
        # Data storage with TTL caching
        self._service_definitions: Dict[str, CMSServiceData] = {}
        self._compliance_policies: List[Dict[str, Any]] = []
        self._configuration_templates: Dict[str, Dict[str, Any]] = {}
        self._last_collection: Optional[datetime] = None
        self._cache_ttl_minutes = 15  # 15 minute cache TTL
        
        # Initialize CMS client
        self._initialize_cms_client()
    
    def get_module_info(self) -> Dict[str, Any]:
        """Get module information."""
        return {
            'module_id': 'cms_configuration_collector',
            'version': '1.0.0',
            'description': 'CMS configuration collection for Runtime State Registry',
            'cms_url': self.cms_url,
            'cache_ttl_minutes': self._cache_ttl_minutes,
            'has_token': bool(self.cms_token)
        }
    
    def get_capabilities(self) -> List[ModuleCapability]:
        """Get module capabilities."""
        return [
            ModuleCapability.DATA_PROCESSING,
            ModuleCapability.API_INTEGRATION
        ]
    
    def get_health_status(self) -> ModuleHealth:
        """Get module health status."""
        issues = []
        health_score = 1.0
        
        # Check CMS connectivity
        if not self._test_cms_connection():
            issues.append("CMS connection failed")
            health_score -= 0.6
        
        # Check authentication
        if not self.cms_token:
            issues.append("CMS token not configured")
            health_score -= 0.3
        
        # Check data freshness
        if self._last_collection and (datetime.now() - self._last_collection).seconds > (self._cache_ttl_minutes * 60):
            issues.append(f"Data cache stale (>{self._cache_ttl_minutes} minutes)")
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
            module_id='cms_configuration_collector',
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
            # Close CMS client if available
            if self.cms_client:
                # CMS client doesn't need explicit closing
                pass
            
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
    
    def _initialize_cms_client(self):
        """Initialize Directus CMS client."""
        try:
            # Try to import and initialize Directus client
            from src.beast_mode.directus_cms.directus_client import DirectusClient
            
            if self.cms_token:
                self.cms_client = DirectusClient(
                    base_url=self.cms_url,
                    token=self.cms_token
                )
                self._logger.info(f"CMS client initialized: {self.cms_url}")
            else:
                self._logger.warning("CMS token not provided - operating in degraded mode")
                
        except ImportError:
            self._logger.warning("DirectusClient not available - using mock implementation")
            self.cms_client = self._create_mock_cms_client()
        except Exception as e:
            self._logger.error(f"Failed to initialize CMS client: {e}")
            self.cms_client = None
    
    def _create_mock_cms_client(self):
        """Create mock CMS client for testing when Directus is not available."""
        class MockCMSClient:
            def health_check(self):
                return True
            
            def get_items(self, collection, params=None):
                # Return mock data based on collection
                if collection == 'service_definitions':
                    return [
                        {
                            'id': 1,
                            'service_name': 'prometheus',
                            'expected_status': 'healthy',
                            'canonical_config': {
                                'port': 9090,
                                'scrape_interval': '15s',
                                'retention': '15d'
                            },
                            'compliance_policies': ['monitoring_required', 'metrics_exposed']
                        },
                        {
                            'id': 2,
                            'service_name': 'grafana',
                            'expected_status': 'healthy',
                            'canonical_config': {
                                'port': 3000,
                                'anonymous_access': True,
                                'default_theme': 'dark'
                            },
                            'compliance_policies': ['dashboard_available', 'auth_configured']
                        }
                    ]
                elif collection == 'compliance_policies':
                    return [
                        {
                            'id': 1,
                            'policy_name': 'monitoring_required',
                            'description': 'All services must expose monitoring endpoints',
                            'validation_rules': {
                                'required_endpoints': ['/health', '/metrics'],
                                'response_codes': [200]
                            }
                        },
                        {
                            'id': 2,
                            'policy_name': 'metrics_exposed',
                            'description': 'Services must expose Prometheus metrics',
                            'validation_rules': {
                                'metrics_format': 'prometheus',
                                'required_metrics': ['up', 'http_requests_total']
                            }
                        }
                    ]
                elif collection == 'configuration_templates':
                    return [
                        {
                            'id': 1,
                            'template_name': 'web_service',
                            'description': 'Standard web service configuration',
                            'template_config': {
                                'health_endpoint': '/health',
                                'metrics_endpoint': '/metrics',
                                'log_level': 'INFO',
                                'timeout': 30
                            }
                        }
                    ]
                return []
        
        return MockCMSClient()
    
    def _test_cms_connection(self) -> bool:
        """Test CMS connection."""
        try:
            if self.cms_client and hasattr(self.cms_client, 'health_check'):
                return self.cms_client.health_check()
        except Exception:
            pass
        return False
    
    async def collect_all_configuration_data(self) -> Dict[str, CMSServiceData]:
        """Collect all configuration data from CMS."""
        if not self.cms_client:
            self._logger.error("CMS client not available")
            return {}
        
        try:
            # Check cache freshness
            if self._is_cache_valid():
                self._logger.debug("Using cached CMS data")
                return self._service_definitions.copy()
            
            self._service_definitions.clear()
            
            # Collect service definitions
            await self._collect_service_definitions()
            
            # Collect compliance policies
            await self._collect_compliance_policies()
            
            # Collect configuration templates
            await self._collect_configuration_templates()
            
            self._last_collection = datetime.now()
            self._logger.info(f"Collected CMS data for {len(self._service_definitions)} services")
            
            return self._service_definitions.copy()
            
        except Exception as e:
            self._logger.error(f"CMS data collection failed: {e}")
            self._increment_error_count()
            return {}
    
    def _is_cache_valid(self) -> bool:
        """Check if cached data is still valid."""
        if not self._last_collection:
            return False
        
        cache_age = datetime.now() - self._last_collection
        return cache_age.total_seconds() < (self._cache_ttl_minutes * 60)
    
    async def _collect_service_definitions(self):
        """Collect service definitions from CMS."""
        try:
            service_definitions = self.cms_client.get_items('service_definitions')
            
            for definition in service_definitions:
                service_name = definition.get('service_name')
                if not service_name:
                    continue
                
                # Parse expected status
                expected_status_str = definition.get('expected_status', 'healthy')
                try:
                    expected_status = ServiceStatus(expected_status_str)
                except ValueError:
                    expected_status = ServiceStatus.HEALTHY
                
                # Create CMS service data
                cms_data = CMSServiceData(
                    service_definition=definition,
                    canonical_config=definition.get('canonical_config', {}),
                    expected_status=expected_status
                )
                
                # Add compliance policies for this service
                service_policies = definition.get('compliance_policies', [])
                cms_data.compliance_policies = [
                    policy for policy in self._compliance_policies
                    if policy.get('policy_name') in service_policies
                ]
                
                self._service_definitions[service_name] = cms_data
                
        except Exception as e:
            self._logger.error(f"Failed to collect service definitions: {e}")
    
    async def _collect_compliance_policies(self):
        """Collect compliance policies from CMS."""
        try:
            self._compliance_policies = self.cms_client.get_items('compliance_policies')
            self._logger.debug(f"Collected {len(self._compliance_policies)} compliance policies")
            
        except Exception as e:
            self._logger.error(f"Failed to collect compliance policies: {e}")
            self._compliance_policies = []
    
    async def _collect_configuration_templates(self):
        """Collect configuration templates from CMS."""
        try:
            templates = self.cms_client.get_items('configuration_templates')
            
            self._configuration_templates.clear()
            for template in templates:
                template_name = template.get('template_name')
                if template_name:
                    self._configuration_templates[template_name] = template
            
            self._logger.debug(f"Collected {len(self._configuration_templates)} configuration templates")
            
        except Exception as e:
            self._logger.error(f"Failed to collect configuration templates: {e}")
            self._configuration_templates = {}
    
    def get_service_definition(self, service_name: str) -> Optional[CMSServiceData]:
        """Get CMS data for a specific service."""
        return self._service_definitions.get(service_name)
    
    def get_all_service_definitions(self) -> Dict[str, CMSServiceData]:
        """Get all service definitions."""
        return self._service_definitions.copy()
    
    def get_compliance_policies(self) -> List[Dict[str, Any]]:
        """Get all compliance policies."""
        return self._compliance_policies.copy()
    
    def get_configuration_templates(self) -> Dict[str, Dict[str, Any]]:
        """Get all configuration templates."""
        return self._configuration_templates.copy()
    
    def get_template_for_service(self, service_type: str) -> Optional[Dict[str, Any]]:
        """Get configuration template for a service type."""
        return self._configuration_templates.get(service_type)
    
    def validate_service_against_policies(self, service_name: str, service_config: Dict[str, Any]) -> Dict[str, Any]:
        """Validate a service configuration against CMS policies."""
        validation_result = {
            'valid': True,
            'violations': [],
            'warnings': []
        }
        
        service_data = self._service_definitions.get(service_name)
        if not service_data:
            validation_result['warnings'].append(f"Service {service_name} not defined in CMS")
            return validation_result
        
        # Validate against compliance policies
        for policy in service_data.compliance_policies:
            policy_name = policy.get('policy_name')
            validation_rules = policy.get('validation_rules', {})
            
            # Check required endpoints
            required_endpoints = validation_rules.get('required_endpoints', [])
            for endpoint in required_endpoints:
                if endpoint not in service_config.get('endpoints', []):
                    validation_result['valid'] = False
                    validation_result['violations'].append(
                        f"Policy {policy_name}: Missing required endpoint {endpoint}"
                    )
            
            # Check required metrics
            required_metrics = validation_rules.get('required_metrics', [])
            service_metrics = service_config.get('metrics', [])
            for metric in required_metrics:
                if metric not in service_metrics:
                    validation_result['warnings'].append(
                        f"Policy {policy_name}: Missing recommended metric {metric}"
                    )
        
        return validation_result
    
    async def refresh_cache(self):
        """Force refresh of cached data."""
        self._last_collection = None
        return await self.collect_all_configuration_data()
    
    def get_cache_status(self) -> Dict[str, Any]:
        """Get cache status information."""
        if not self._last_collection:
            return {
                'cached': False,
                'last_collection': None,
                'cache_age_seconds': None,
                'cache_valid': False
            }
        
        cache_age = datetime.now() - self._last_collection
        cache_age_seconds = cache_age.total_seconds()
        
        return {
            'cached': True,
            'last_collection': self._last_collection.isoformat(),
            'cache_age_seconds': cache_age_seconds,
            'cache_valid': self._is_cache_valid(),
            'cache_ttl_minutes': self._cache_ttl_minutes
        }


# CLI interface for testing
async def main():
    """Main CLI interface for testing."""
    import argparse
    
    parser = argparse.ArgumentParser(description="CMS Configuration Collector")
    parser.add_argument('action', choices=['collect', 'health', 'validate', 'cache-status'],
                       help='Action to perform')
    parser.add_argument('--cms-url', help='CMS URL override')
    parser.add_argument('--service', help='Service name for validation')
    
    args = parser.parse_args()
    
    collector = CMSConfigurationCollector(cms_url=args.cms_url)
    
    try:
        if args.action == 'collect':
            data = await collector.collect_all_configuration_data()
            print(f"Collected CMS data for {len(data)} services:")
            for service_name, cms_data in data.items():
                print(f"  - {service_name}: {cms_data.expected_status.value}")
                print(f"    Policies: {len(cms_data.compliance_policies)}")
        
        elif args.action == 'health':
            health = collector.get_health_status()
            print(f"Status: {health.status.value}")
            print(f"Health Score: {health.health_score}")
            if health.issues:
                print("Issues:")
                for issue in health.issues:
                    print(f"  - {issue}")
        
        elif args.action == 'validate':
            if not args.service:
                print("--service required for validation")
                sys.exit(1)
            
            # Mock service config for testing
            service_config = {
                'endpoints': ['/health', '/metrics'],
                'metrics': ['up', 'http_requests_total']
            }
            
            result = collector.validate_service_against_policies(args.service, service_config)
            print(f"Validation result for {args.service}:")
            print(f"  Valid: {result['valid']}")
            if result['violations']:
                print("  Violations:")
                for violation in result['violations']:
                    print(f"    - {violation}")
            if result['warnings']:
                print("  Warnings:")
                for warning in result['warnings']:
                    print(f"    - {warning}")
        
        elif args.action == 'cache-status':
            status = collector.get_cache_status()
            print("Cache Status:")
            for key, value in status.items():
                print(f"  {key}: {value}")
    
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())