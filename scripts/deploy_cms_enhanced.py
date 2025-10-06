#!/usr/bin/env python3
"""
CMS Enhanced Deployment Script
==============================

Deploys the enhanced CMS architecture with all required services.
Includes validation, health checks, and systematic deployment procedures.

Author: Beast Mode Framework
Date: 2025-10-05
Purpose: Systematic CMS deployment with infrastructure validation
"""

import os
import sys
import time
import subprocess
import json
from pathlib import Path
from typing import Dict, Any, List
import requests

from src.rm_ddd.core.unified_reflective_module import ReflectiveModule


class CMSDeploymentOrchestrator(ReflectiveModule):
    """CMS deployment orchestrator with Beast Mode compliance."""
    
    def __init__(self):
        super().__init__()
        self.services = [
            'postgres',
            'redis', 
            'elasticsearch',
            'directus',
            'kibana',
            'cms-search',
            'cms-repo-sync'
        ]
        self.health_endpoints = {
            'postgres': None,  # No HTTP endpoint
            'redis': None,     # No HTTP endpoint
            'elasticsearch': 'http://localhost:9200/_cluster/health',
            'directus': 'http://localhost:8055/server/health',
            'kibana': 'http://localhost:5601/api/status',
            'cms-search': 'http://localhost:8056/health',
            'cms-repo-sync': 'http://localhost:8057/health'
        }
    
    def deploy(self) -> Dict[str, Any]:
        """Deploy the enhanced CMS architecture."""
        print("🚀 Starting CMS Enhanced Deployment")
        print("=" * 50)
        
        deployment_result = {
            'success': False,
            'services_deployed': [],
            'services_failed': [],
            'health_checks': {},
            'deployment_time': 0
        }
        
        start_time = time.time()
        
        try:
            # Step 1: Pre-deployment validation
            print("\n📋 Step 1: Pre-deployment validation")
            self._validate_prerequisites()
            
            # Step 2: Stop existing services
            print("\n🛑 Step 2: Stopping existing services")
            self._stop_existing_services()
            
            # Step 3: Deploy infrastructure services first
            print("\n🏗️  Step 3: Deploying infrastructure services")
            infrastructure_services = ['postgres', 'redis', 'elasticsearch']
            for service in infrastructure_services:
                if self._deploy_service(service):
                    deployment_result['services_deployed'].append(service)
                else:
                    deployment_result['services_failed'].append(service)
            
            # Step 4: Wait for infrastructure to be ready
            print("\n⏳ Step 4: Waiting for infrastructure services")
            self._wait_for_infrastructure()
            
            # Step 5: Deploy application services
            print("\n🎯 Step 5: Deploying application services")
            app_services = ['directus', 'kibana', 'cms-search', 'cms-repo-sync']
            for service in app_services:
                if self._deploy_service(service):
                    deployment_result['services_deployed'].append(service)
                else:
                    deployment_result['services_failed'].append(service)
            
            # Step 6: Health checks
            print("\n🏥 Step 6: Running health checks")
            deployment_result['health_checks'] = self._run_health_checks()
            
            # Step 7: Post-deployment setup
            print("\n⚙️  Step 7: Post-deployment setup")
            self._post_deployment_setup()
            
            # Step 8: Validation
            print("\n✅ Step 8: Final validation")
            deployment_result['success'] = self._validate_deployment()
            
            deployment_result['deployment_time'] = time.time() - start_time
            
            if deployment_result['success']:
                print("\n🎉 CMS Enhanced Deployment completed successfully!")
                self._print_deployment_summary(deployment_result)
            else:
                print("\n❌ CMS Enhanced Deployment failed!")
                self._print_failure_summary(deployment_result)
            
            return deployment_result
            
        except Exception as e:
            print(f"\n💥 Deployment failed with error: {str(e)}")
            deployment_result['deployment_time'] = time.time() - start_time
            return deployment_result
    
    def _validate_prerequisites(self):
        """Validate deployment prerequisites."""
        print("  Checking Docker...")
        result = subprocess.run(['docker', '--version'], capture_output=True, text=True)
        if result.returncode != 0:
            raise Exception("Docker is not installed or not running")
        print("  ✅ Docker is available")
        
        print("  Checking Docker Compose...")
        result = subprocess.run(['docker', 'compose', 'version'], capture_output=True, text=True)
        if result.returncode != 0:
            raise Exception("Docker Compose is not available")
        print("  ✅ Docker Compose is available")
        
        print("  Checking required files...")
        required_files = [
            'docker-compose.cms-enhanced.yml',
            'Dockerfile.cms-search',
            'Dockerfile.cms-repo-sync',
            'requirements-cms-search.txt',
            'requirements-cms-repo-sync.txt'
        ]
        
        for file_path in required_files:
            if not Path(file_path).exists():
                raise Exception(f"Required file not found: {file_path}")
        print("  ✅ All required files present")
    
    def _stop_existing_services(self):
        """Stop existing services to avoid conflicts."""
        print("  Stopping existing CMS services...")
        
        # Stop enhanced services
        subprocess.run([
            'docker', 'compose', '-f', 'docker-compose.cms-enhanced.yml', 'down'
        ], capture_output=True)
        
        # Stop original Directus services
        subprocess.run([
            'docker', 'compose', '-f', 'docker-compose.directus.yml', 'down'
        ], capture_output=True)
        
        print("  ✅ Existing services stopped")
    
    def _deploy_service(self, service: str) -> bool:
        """Deploy a specific service."""
        print(f"  Deploying {service}...")
        
        try:
            result = subprocess.run([
                'docker', 'compose', '-f', 'docker-compose.cms-enhanced.yml',
                'up', '-d', service
            ], capture_output=True, text=True, timeout=300)
            
            if result.returncode == 0:
                print(f"  ✅ {service} deployed successfully")
                return True
            else:
                print(f"  ❌ {service} deployment failed: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            print(f"  ⏰ {service} deployment timed out")
            return False
        except Exception as e:
            print(f"  💥 {service} deployment error: {str(e)}")
            return False
    
    def _wait_for_infrastructure(self):
        """Wait for infrastructure services to be ready."""
        infrastructure_checks = {
            'postgres': self._check_postgres,
            'redis': self._check_redis,
            'elasticsearch': self._check_elasticsearch
        }
        
        max_wait = 300  # 5 minutes
        start_time = time.time()
        
        while time.time() - start_time < max_wait:
            all_ready = True
            
            for service, check_func in infrastructure_checks.items():
                if not check_func():
                    all_ready = False
                    print(f"  ⏳ Waiting for {service}...")
                    break
            
            if all_ready:
                print("  ✅ All infrastructure services ready")
                return
            
            time.sleep(10)
        
        raise Exception("Infrastructure services did not become ready in time")
    
    def _check_postgres(self) -> bool:
        """Check if PostgreSQL is ready."""
        try:
            result = subprocess.run([
                'docker', 'exec', 'cms_postgres',
                'pg_isready', '-U', 'directus', '-d', 'directus'
            ], capture_output=True, text=True, timeout=10)
            return result.returncode == 0
        except:
            return False
    
    def _check_redis(self) -> bool:
        """Check if Redis is ready."""
        try:
            result = subprocess.run([
                'docker', 'exec', 'cms_redis',
                'redis-cli', 'ping'
            ], capture_output=True, text=True, timeout=10)
            return result.returncode == 0 and 'PONG' in result.stdout
        except:
            return False
    
    def _check_elasticsearch(self) -> bool:
        """Check if Elasticsearch is ready."""
        try:
            response = requests.get(
                'http://localhost:9200/_cluster/health',
                timeout=10
            )
            return response.status_code == 200
        except:
            return False
    
    def _run_health_checks(self) -> Dict[str, Any]:
        """Run health checks for all services."""
        health_results = {}
        
        for service, endpoint in self.health_endpoints.items():
            if endpoint:
                try:
                    response = requests.get(endpoint, timeout=10)
                    health_results[service] = {
                        'status': 'healthy' if response.status_code == 200 else 'unhealthy',
                        'status_code': response.status_code,
                        'response': response.json() if response.headers.get('content-type', '').startswith('application/json') else response.text[:200]
                    }
                    print(f"  ✅ {service} health check passed")
                except Exception as e:
                    health_results[service] = {
                        'status': 'unhealthy',
                        'error': str(e)
                    }
                    print(f"  ❌ {service} health check failed: {str(e)}")
            else:
                # For services without HTTP endpoints, check if container is running
                try:
                    result = subprocess.run([
                        'docker', 'ps', '--filter', f'name=cms_{service}', '--format', '{{.Status}}'
                    ], capture_output=True, text=True)
                    
                    if 'Up' in result.stdout:
                        health_results[service] = {'status': 'healthy', 'container': 'running'}
                        print(f"  ✅ {service} container is running")
                    else:
                        health_results[service] = {'status': 'unhealthy', 'container': 'not_running'}
                        print(f"  ❌ {service} container is not running")
                except Exception as e:
                    health_results[service] = {'status': 'unhealthy', 'error': str(e)}
                    print(f"  ❌ {service} check failed: {str(e)}")
        
        return health_results
    
    def _post_deployment_setup(self):
        """Perform post-deployment setup tasks."""
        print("  Creating Elasticsearch indexes...")
        try:
            # Create CMS content index
            index_config = {
                "mappings": {
                    "properties": {
                        "title": {"type": "text", "analyzer": "standard"},
                        "content": {"type": "text", "analyzer": "standard"},
                        "content_type": {"type": "keyword"},
                        "stakeholder_role": {"type": "keyword"},
                        "tags": {"type": "keyword"},
                        "created_at": {"type": "date"},
                        "updated_at": {"type": "date"},
                        "metadata": {"type": "object"},
                        "embedding": {"type": "dense_vector", "dims": 384}
                    }
                }
            }
            
            response = requests.put(
                'http://localhost:9200/cms_content',
                json=index_config,
                timeout=30
            )
            
            if response.status_code in [200, 201]:
                print("  ✅ Elasticsearch indexes created")
            else:
                print(f"  ⚠️  Elasticsearch index creation warning: {response.status_code}")
                
        except Exception as e:
            print(f"  ⚠️  Elasticsearch setup warning: {str(e)}")
        
        print("  Setting up Directus collections...")
        # Note: This would typically involve API calls to create custom collections
        # For now, we'll just log that this step is needed
        print("  ⚠️  Manual Directus collection setup required")
    
    def _validate_deployment(self) -> bool:
        """Validate the complete deployment."""
        print("  Validating deployment...")
        
        # Check that all critical services are healthy
        critical_services = ['postgres', 'redis', 'elasticsearch', 'directus']
        health_results = self._run_health_checks()
        
        for service in critical_services:
            if service not in health_results or health_results[service]['status'] != 'healthy':
                print(f"  ❌ Critical service {service} is not healthy")
                return False
        
        print("  ✅ All critical services are healthy")
        
        # Test basic functionality
        try:
            # Test Directus API
            response = requests.get('http://localhost:8055/server/info', timeout=10)
            if response.status_code != 200:
                print("  ❌ Directus API test failed")
                return False
            
            # Test Elasticsearch
            response = requests.get('http://localhost:9200/_cluster/health', timeout=10)
            if response.status_code != 200:
                print("  ❌ Elasticsearch test failed")
                return False
            
            print("  ✅ Basic functionality tests passed")
            return True
            
        except Exception as e:
            print(f"  ❌ Functionality test failed: {str(e)}")
            return False
    
    def _print_deployment_summary(self, result: Dict[str, Any]):
        """Print deployment success summary."""
        print("\n" + "=" * 50)
        print("🎉 DEPLOYMENT SUCCESSFUL")
        print("=" * 50)
        print(f"⏱️  Total deployment time: {result['deployment_time']:.1f} seconds")
        print(f"✅ Services deployed: {len(result['services_deployed'])}")
        
        print("\n📊 Service Status:")
        for service in result['services_deployed']:
            print(f"  ✅ {service}")
        
        print("\n🌐 Access URLs:")
        print("  📊 Directus CMS: http://localhost:8055")
        print("  🔍 Elasticsearch: http://localhost:9200")
        print("  📈 Kibana: http://localhost:5601")
        print("  🔎 CMS Search API: http://localhost:8056")
        print("  🔄 Repository Sync API: http://localhost:8057")
        
        print("\n📋 Next Steps:")
        print("  1. Configure Directus collections for stakeholder data")
        print("  2. Set up repository webhooks for automatic sync")
        print("  3. Configure authentication and authorization")
        print("  4. Import existing content and repositories")
    
    def _print_failure_summary(self, result: Dict[str, Any]):
        """Print deployment failure summary."""
        print("\n" + "=" * 50)
        print("❌ DEPLOYMENT FAILED")
        print("=" * 50)
        print(f"⏱️  Deployment time: {result['deployment_time']:.1f} seconds")
        
        if result['services_deployed']:
            print(f"\n✅ Successfully deployed ({len(result['services_deployed'])}):")
            for service in result['services_deployed']:
                print(f"  ✅ {service}")
        
        if result['services_failed']:
            print(f"\n❌ Failed to deploy ({len(result['services_failed'])}):")
            for service in result['services_failed']:
                print(f"  ❌ {service}")
        
        print("\n🔧 Troubleshooting:")
        print("  1. Check Docker logs: docker compose -f docker-compose.cms-enhanced.yml logs")
        print("  2. Verify system resources (memory, disk space)")
        print("  3. Check port conflicts (8055, 9200, 5601, 8056, 8057)")
        print("  4. Review service health checks")
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get health status for Beast Mode compliance."""
        return {
            "service": "cms-deployment-orchestrator",
            "status": "ready",
            "services_monitored": len(self.services),
            "health_endpoints": len([ep for ep in self.health_endpoints.values() if ep])
        }


def main():
    """Main deployment function."""
    if len(sys.argv) > 1 and sys.argv[1] == '--help':
        print("CMS Enhanced Deployment Script")
        print("Usage: python scripts/deploy_cms_enhanced.py")
        print("\nThis script deploys the enhanced CMS architecture with:")
        print("  - PostgreSQL database")
        print("  - Redis cache")
        print("  - Elasticsearch search engine")
        print("  - Directus CMS")
        print("  - Kibana dashboard")
        print("  - CMS Search service")
        print("  - Repository sync service")
        return
    
    try:
        orchestrator = CMSDeploymentOrchestrator()
        result = orchestrator.deploy()
        
        # Exit with appropriate code
        sys.exit(0 if result['success'] else 1)
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Deployment interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Deployment failed with unexpected error: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()