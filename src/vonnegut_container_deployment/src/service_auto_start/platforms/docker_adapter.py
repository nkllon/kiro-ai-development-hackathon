#!/usr/bin/env python3
"""
Docker Compose Adapter - Platform Adapter for Docker Auto-Start

Generates Docker Compose service configurations with proper restart policies
and health checks using container-native tools only.
"""

import os
import yaml
import subprocess
from pathlib import Path
from typing import Dict, Any, Optional, List

from ..core.service_auto_starter import ServiceAutoStarter, ServiceDefinition
from ..health.health_check_validator import HealthCheckValidator, HealthCheckConfig


class DockerComposeAdapter(ServiceAutoStarter):
    """
    Docker Compose adapter for service auto-start management.
    
    Creates and manages Docker Compose service definitions with proper
    restart policies, health checks, and dependency management.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize Docker Compose adapter."""
        super().__init__(config)
        
        # Docker Compose configuration
        self._compose_file = config.get("compose_file", "docker-compose.yml") if config else "docker-compose.yml"
        self._compose_path = Path(self._compose_file)
        
        # Health check validator
        self._health_validator = HealthCheckValidator()
        
        self._logger.info(f"Docker Compose adapter initialized, compose file: {self._compose_path}")
    
    def generate_config(self, service: ServiceDefinition) -> Dict[str, Any]:
        """
        Generate Docker Compose service configuration.
        
        Args:
            service: Service definition
            
        Returns:
            Docker Compose service configuration dictionary
        """
        try:
            # Base service configuration
            service_config = {
                "image": self._get_service_image(service),
                "container_name": service.name,
                "restart": self._convert_restart_policy(service.restart_policy),
                "working_dir": service.working_directory,
                "command": service.command
            }
            
            # Add environment variables
            if service.environment:
                service_config["environment"] = service.environment
            
            # Add dependencies
            if service.dependencies:
                service_config["depends_on"] = service.dependencies
            
            # Add health check if URL is provided
            if service.health_check_url:
                health_config = HealthCheckConfig(url=service.health_check_url)
                health_check = self._health_validator.generate_docker_healthcheck(
                    health_config, service.name
                )
                if health_check:
                    service_config["healthcheck"] = health_check
                else:
                    self._logger.warning(f"Could not generate health check for {service.name}")
            
            # Add volumes if working directory needs to be mounted
            if self._should_mount_working_dir(service):
                service_config["volumes"] = [
                    f"{service.working_directory}:{service.working_directory}"
                ]
            
            # Add user if specified
            if service.user:
                service_config["user"] = service.user
            
            # Add logging configuration
            service_config["logging"] = {
                "driver": "json-file",
                "options": {
                    "max-size": "10m",
                    "max-file": "3"
                }
            }
            
            config = {
                "service_config": service_config,
                "service_name": service.name,
                "compose_file": str(self._compose_path)
            }
            
            self._logger.info(f"Generated Docker Compose config for {service.name}")
            return config
            
        except Exception as e:
            self._logger.error(f"Failed to generate config for {service.name}: {e}")
            return {}
    
    def install_config(self, service: ServiceDefinition, config: Dict[str, Any]) -> bool:
        """
        Install Docker Compose service configuration.
        
        Args:
            service: Service definition
            config: Generated Docker Compose configuration
            
        Returns:
            True if installation successful, False otherwise
        """
        try:
            service_config = config["service_config"]
            service_name = config["service_name"]
            
            # Load existing compose file or create new one
            compose_data = self._load_compose_file()
            
            # Add or update service
            if "services" not in compose_data:
                compose_data["services"] = {}
            
            compose_data["services"][service_name] = service_config
            
            # Write updated compose file
            self._save_compose_file(compose_data)
            
            self._logger.info(f"Updated Docker Compose file with service: {service_name}")
            
            # Start the service
            result = subprocess.run([
                "docker-compose", "-f", str(self._compose_path),
                "up", "-d", service_name
            ], capture_output=True, text=True)
            
            if result.returncode != 0:
                self._logger.error(f"Failed to start Docker service: {result.stderr}")
                return False
            
            self._logger.info(f"Successfully started Docker service: {service_name}")
            return True
            
        except Exception as e:
            self._logger.error(f"Failed to install config for {service.name}: {e}")
            return False
    
    def verify_autostart(self, service: ServiceDefinition) -> bool:
        """
        Verify that the Docker service is properly configured with restart policy.
        
        Args:
            service: Service definition to verify
            
        Returns:
            True if auto-start is properly configured, False otherwise
        """
        try:
            # Check if service exists in compose file
            compose_data = self._load_compose_file()
            
            if "services" not in compose_data or service.name not in compose_data["services"]:
                self._logger.error(f"Service {service.name} not found in compose file")
                return False
            
            service_config = compose_data["services"][service.name]
            
            # Check restart policy
            restart_policy = service_config.get("restart", "no")
            if restart_policy == "no":
                self._logger.error(f"Service {service.name} has no restart policy")
                return False
            
            # Check if container exists and has correct restart policy
            result = subprocess.run([
                "docker", "inspect", service.name, "--format", "{{.HostConfig.RestartPolicy.Name}}"
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                actual_policy = result.stdout.strip()
                expected_policy = self._convert_restart_policy_to_docker(service.restart_policy)
                
                if actual_policy != expected_policy:
                    self._logger.warning(f"Container restart policy mismatch: {actual_policy} != {expected_policy}")
            
            self._logger.info(f"Docker service {service.name} is properly configured")
            return True
            
        except Exception as e:
            self._logger.error(f"Failed to verify auto-start for {service.name}: {e}")
            return False
    
    def remove_autostart(self, service: ServiceDefinition) -> bool:
        """
        Remove Docker service configuration and stop the container.
        
        Args:
            service: Service definition to remove
            
        Returns:
            True if removal successful, False otherwise
        """
        try:
            # Stop and remove container
            subprocess.run([
                "docker-compose", "-f", str(self._compose_path),
                "stop", service.name
            ], capture_output=True, text=True)
            
            subprocess.run([
                "docker-compose", "-f", str(self._compose_path),
                "rm", "-f", service.name
            ], capture_output=True, text=True)
            
            # Remove from compose file
            compose_data = self._load_compose_file()
            
            if "services" in compose_data and service.name in compose_data["services"]:
                del compose_data["services"][service.name]
                self._save_compose_file(compose_data)
                self._logger.info(f"Removed service {service.name} from compose file")
            
            self._logger.info(f"Successfully removed Docker service for {service.name}")
            return True
            
        except Exception as e:
            self._logger.error(f"Failed to remove auto-start for {service.name}: {e}")
            return False
    
    def get_service_status(self, service: ServiceDefinition) -> Dict[str, Any]:
        """
        Get current status of the Docker service.
        
        Args:
            service: Service definition
            
        Returns:
            Status information dictionary
        """
        try:
            # Get container status
            result = subprocess.run([
                "docker", "ps", "-a", "--filter", f"name={service.name}",
                "--format", "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
            ], capture_output=True, text=True)
            
            # Get compose service status
            compose_result = subprocess.run([
                "docker-compose", "-f", str(self._compose_path),
                "ps", service.name
            ], capture_output=True, text=True)
            
            return {
                "container_status": result.stdout,
                "compose_status": compose_result.stdout,
                "service_name": service.name
            }
            
        except Exception as e:
            return {"error": str(e)}
    
    def _load_compose_file(self) -> Dict[str, Any]:
        """Load existing Docker Compose file or return empty structure."""
        if self._compose_path.exists():
            try:
                with open(self._compose_path, 'r') as f:
                    return yaml.safe_load(f) or {}
            except Exception as e:
                self._logger.warning(f"Failed to load compose file: {e}")
        
        return {"version": "3.8", "services": {}}
    
    def _save_compose_file(self, data: Dict[str, Any]):
        """Save Docker Compose file."""
        with open(self._compose_path, 'w') as f:
            yaml.dump(data, f, default_flow_style=False, indent=2)
    
    def _get_service_image(self, service: ServiceDefinition) -> str:
        """Determine Docker image for service."""
        # This is a simplified implementation
        # In practice, this would be configured per service
        if "python" in service.command.lower():
            return "python:3.9-slim"
        elif "node" in service.command.lower():
            return "node:16-alpine"
        else:
            return "ubuntu:20.04"
    
    def _convert_restart_policy(self, policy: str) -> str:
        """Convert service restart policy to Docker Compose format."""
        policy_map = {
            "always": "always",
            "unless-stopped": "unless-stopped",
            "on-failure": "on-failure",
            "no": "no"
        }
        return policy_map.get(policy, "unless-stopped")
    
    def _convert_restart_policy_to_docker(self, policy: str) -> str:
        """Convert service restart policy to Docker inspect format."""
        policy_map = {
            "always": "always",
            "unless-stopped": "unless-stopped",
            "on-failure": "on-failure",
            "no": ""
        }
        return policy_map.get(policy, "unless-stopped")
    
    def _should_mount_working_dir(self, service: ServiceDefinition) -> bool:
        """Determine if working directory should be mounted as volume."""
        # Mount if working directory is not a standard container path
        standard_paths = ["/app", "/usr/src/app", "/opt", "/home"]
        return not any(service.working_directory.startswith(path) for path in standard_paths)
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get health status for Docker Compose adapter."""
        base_status = super().get_health_status()
        
        # Add Docker-specific status
        base_status.update({
            "compose_file": str(self._compose_path),
            "compose_file_exists": self._compose_path.exists(),
            "docker_available": self._check_docker_available(),
            "docker_compose_available": self._check_docker_compose_available()
        })
        
        return base_status
    
    def _check_docker_available(self) -> bool:
        """Check if Docker is available."""
        try:
            result = subprocess.run(["docker", "--version"], 
                                  capture_output=True, timeout=5)
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return False
    
    def _check_docker_compose_available(self) -> bool:
        """Check if Docker Compose is available."""
        try:
            result = subprocess.run(["docker-compose", "--version"], 
                                  capture_output=True, timeout=5)
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return False