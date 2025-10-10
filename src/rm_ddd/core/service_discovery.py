"""
Auto-Configuring Service Discovery
=================================

Automatically discovers and configures services regardless of deployment:
- Local development (localhost)
- Docker Compose (container names)
- Kubernetes (service names)
- Remote services (any IP/hostname)
- Cloud services (any URL)

Tests and components don't need to know where services are - they just work.
"""

import os
import subprocess
import json
import yaml
import socket
import requests
from pathlib import Path
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


@dataclass
class ServiceEndpoint:
    """Discovered service endpoint."""
    host: str
    port: int
    url: str
    health_endpoint: Optional[str] = None
    available: bool = False
    discovery_method: str = "unknown"


class ServiceDiscovery:
    """Auto-configuring service discovery system."""
    
    def __init__(self, config_path: Optional[str] = None):
        self.config_path = config_path or self._find_config_file()
        self.config = self._load_config()
        self.discovered_services = {}
        
    def _find_config_file(self) -> str:
        """Find the services configuration file."""
        possible_paths = [
            'config/services.yml',
            '../config/services.yml', 
            '../../config/services.yml'
        ]
        
        for path in possible_paths:
            if Path(path).exists():
                return path
        
        raise FileNotFoundError("Could not find config/services.yml")
    
    def _load_config(self) -> Dict[str, Any]:
        """Load service discovery configuration."""
        with open(self.config_path, 'r') as f:
            return yaml.safe_load(f)
    
    def discover_service(self, service_name: str) -> ServiceEndpoint:
        """Auto-discover service endpoint using configured methods."""
        if service_name in self.discovered_services:
            return self.discovered_services[service_name]
        
        service_config = self.config['services'].get(service_name, {})
        discovery_methods = self.config.get('discovery', {}).get('methods', [
            'environment_variables', 'docker_compose', 'static_config'
        ])
        
        endpoint = None
        
        # Try each discovery method in order
        for method in discovery_methods:
            try:
                if method == 'environment_variables':
                    endpoint = self._discover_from_env(service_name, service_config)
                elif method == 'docker_compose':
                    endpoint = self._discover_from_docker(service_name, service_config)
                elif method == 'kubernetes':
                    endpoint = self._discover_from_k8s(service_name, service_config)
                elif method == 'static_config':
                    endpoint = self._discover_from_config(service_name, service_config)
                
                if endpoint and self._test_endpoint(endpoint):
                    endpoint.available = True
                    endpoint.discovery_method = method
                    break
                    
            except Exception as e:
                logger.debug(f"Discovery method {method} failed for {service_name}: {e}")
                continue
        
        # If no endpoint found or available, create proxy if needed
        if not endpoint or not endpoint.available:
            if self._should_create_proxy(service_name):
                endpoint = self._create_service_proxy(service_name, service_config)
        
        # Fall back to static config if nothing else works
        if not endpoint:
            endpoint = self._discover_from_config(service_name, service_config)
            endpoint.discovery_method = "fallback"
        
        self.discovered_services[service_name] = endpoint
        
        logger.info(f"Service {service_name} discovered: {endpoint.url} via {endpoint.discovery_method}")
        return endpoint
    
    def _discover_from_env(self, service_name: str, config: Dict) -> Optional[ServiceEndpoint]:
        """Discover service from environment variables."""
        service_upper = service_name.upper()
        
        # Check for service-specific env vars
        host = os.getenv(f"{service_upper}_HOST")
        port = os.getenv(f"{service_upper}_PORT")
        url = os.getenv(f"{service_upper}_URL")
        
        if url:
            # Parse URL to get host and port
            from urllib.parse import urlparse
            parsed = urlparse(url)
            return ServiceEndpoint(
                host=parsed.hostname,
                port=parsed.port or config.get('port', 80),
                url=url,
                health_endpoint=config.get('health_endpoint')
            )
        elif host:
            port = int(port) if port else config.get('port', 80)
            protocol = 'https' if port == 443 else 'http'
            url = f"{protocol}://{host}:{port}"
            return ServiceEndpoint(
                host=host,
                port=port,
                url=url,
                health_endpoint=config.get('health_endpoint')
            )
        
        return None
    
    def _discover_from_docker(self, service_name: str, config: Dict) -> Optional[ServiceEndpoint]:
        """Discover service from Docker Compose."""
        try:
            # Check if service is running in Docker
            result = subprocess.run([
                'docker', 'ps', '--format', 'json', '--filter', f'name={service_name}'
            ], capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0 and result.stdout.strip():
                # Parse docker ps output
                containers = [json.loads(line) for line in result.stdout.strip().split('\n')]
                
                for container in containers:
                    ports = container.get('Ports', '')
                    if ports and '->' in ports:
                        # Extract port mapping (e.g., "0.0.0.0:9090->9090/tcp")
                        for port_mapping in ports.split(', '):
                            if '->' in port_mapping:
                                external_part = port_mapping.split('->')[0]
                                if ':' in external_part:
                                    host_port = external_part.split(':')[-1]
                                    return ServiceEndpoint(
                                        host='localhost',
                                        port=int(host_port),
                                        url=f"http://localhost:{host_port}",
                                        health_endpoint=config.get('health_endpoint')
                                    )
            
            # Try container name resolution
            host = service_name
            port = config.get('port', 80)
            url = f"http://{host}:{port}"
            
            return ServiceEndpoint(
                host=host,
                port=port,
                url=url,
                health_endpoint=config.get('health_endpoint')
            )
            
        except Exception as e:
            logger.debug(f"Docker discovery failed for {service_name}: {e}")
            return None
    
    def _discover_from_k8s(self, service_name: str, config: Dict) -> Optional[ServiceEndpoint]:
        """Discover service from Kubernetes."""
        try:
            # Check if we're in a k8s environment
            if not os.path.exists('/var/run/secrets/kubernetes.io'):
                return None
            
            # Use kubectl to get service info
            result = subprocess.run([
                'kubectl', 'get', 'service', service_name, '-o', 'json'
            ], capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                service_info = json.loads(result.stdout)
                cluster_ip = service_info['spec']['clusterIP']
                ports = service_info['spec']['ports']
                
                if ports:
                    port = ports[0]['port']
                    return ServiceEndpoint(
                        host=cluster_ip,
                        port=port,
                        url=f"http://{cluster_ip}:{port}",
                        health_endpoint=config.get('health_endpoint')
                    )
            
        except Exception as e:
            logger.debug(f"Kubernetes discovery failed for {service_name}: {e}")
            
        return None
    
    def _discover_from_config(self, service_name: str, config: Dict) -> ServiceEndpoint:
        """Discover service from static configuration."""
        host = config.get('host', 'localhost')
        port = config.get('port', 80)
        url = config.get('url', f"http://{host}:{port}")
        
        return ServiceEndpoint(
            host=host,
            port=port,
            url=url,
            health_endpoint=config.get('health_endpoint')
        )
    
    def _test_endpoint(self, endpoint: ServiceEndpoint) -> bool:
        """Test if service endpoint is available."""
        try:
            # First try TCP connection
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)
            result = sock.connect_ex((endpoint.host, endpoint.port))
            sock.close()
            
            if result != 0:
                return False
            
            # If has health endpoint, test HTTP
            if endpoint.health_endpoint:
                health_url = f"{endpoint.url}{endpoint.health_endpoint}"
                response = requests.get(health_url, timeout=5)
                return response.status_code == 200
            
            return True
            
        except Exception as e:
            logger.debug(f"Endpoint test failed for {endpoint.url}: {e}")
            return False
    
    def _should_create_proxy(self, service_name: str) -> bool:
        """Check if we should create a proxy for this service."""
        service_config = self.config['services'].get(service_name, {})
        auto_proxy_config = self.config.get('discovery', {}).get('auto_proxy', {})
        
        return (
            auto_proxy_config.get('enabled', False) and
            service_config.get('required_for_tests', False)
        )
    
    def _create_service_proxy(self, service_name: str, config: Dict) -> Optional[ServiceEndpoint]:
        """Create a proxy container for remote service."""
        try:
            # Check if proxy already exists
            proxy_name = f"beast-mode-{service_name}-proxy"
            
            result = subprocess.run([
                'docker', 'ps', '--filter', f'name={proxy_name}', '--format', '{{.Names}}'
            ], capture_output=True, text=True)
            
            if proxy_name in result.stdout:
                logger.info(f"Proxy {proxy_name} already running")
                return self._discover_from_config(service_name, config)
            
            # Get remote service URL from environment
            remote_url = os.getenv(f"{service_name.upper()}_REMOTE_URL")
            if not remote_url:
                logger.warning(f"No remote URL configured for {service_name}")
                return None
            
            # Create nginx proxy config
            proxy_config = self._generate_proxy_config(service_name, remote_url, config)
            
            # Start proxy container
            proxy_port = config.get('port', 80)
            
            subprocess.run([
                'docker', 'run', '-d',
                '--name', proxy_name,
                '--network', 'beast-mode-network',
                '-p', f"{proxy_port}:{proxy_port}",
                '-v', f"{proxy_config}:/etc/nginx/nginx.conf:ro",
                'nginx:alpine'
            ], check=True)
            
            logger.info(f"Created proxy {proxy_name} for {service_name} -> {remote_url}")
            
            return ServiceEndpoint(
                host='localhost',
                port=proxy_port,
                url=f"http://localhost:{proxy_port}",
                health_endpoint=config.get('health_endpoint'),
                discovery_method="auto_proxy"
            )
            
        except Exception as e:
            logger.error(f"Failed to create proxy for {service_name}: {e}")
            return None
    
    def _generate_proxy_config(self, service_name: str, remote_url: str, config: Dict) -> str:
        """Generate nginx proxy configuration."""
        from urllib.parse import urlparse
        parsed = urlparse(remote_url)
        
        proxy_config = f"""
events {{
    worker_connections 1024;
}}

http {{
    upstream {service_name}_backend {{
        server {parsed.netloc};
    }}

    server {{
        listen {config.get('port', 80)};
        
        location / {{
            proxy_pass {remote_url};
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            
            proxy_http_version 1.1;
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection "upgrade";
            
            proxy_connect_timeout 60s;
            proxy_send_timeout 60s;
            proxy_read_timeout 60s;
        }}
    }}
}}
"""
        
        # Write config to temp file
        config_path = f"/tmp/{service_name}-proxy.conf"
        with open(config_path, 'w') as f:
            f.write(proxy_config)
        
        return config_path
    
    def get_all_required_services(self) -> Dict[str, ServiceEndpoint]:
        """Get all services required for tests."""
        required_services = {}
        
        for service_name, config in self.config['services'].items():
            if config.get('required_for_tests', False):
                endpoint = self.discover_service(service_name)
                required_services[service_name] = endpoint
        
        return required_services
    
    def health_check_all(self) -> Dict[str, bool]:
        """Health check all discovered services."""
        results = {}
        
        for service_name, endpoint in self.discovered_services.items():
            results[service_name] = self._test_endpoint(endpoint)
        
        return results


# Global service discovery instance
_service_discovery = None


def get_service_discovery() -> ServiceDiscovery:
    """Get global service discovery instance."""
    global _service_discovery
    if _service_discovery is None:
        _service_discovery = ServiceDiscovery()
    return _service_discovery


def discover_service(service_name: str) -> ServiceEndpoint:
    """Discover a service endpoint."""
    return get_service_discovery().discover_service(service_name)


def get_prometheus_url() -> str:
    """Get Prometheus URL - auto-discovered."""
    return discover_service('prometheus').url


def get_grafana_url() -> str:
    """Get Grafana URL - auto-discovered."""
    return discover_service('grafana').url


def get_redis_endpoint() -> ServiceEndpoint:
    """Get Redis endpoint - auto-discovered."""
    return discover_service('redis')