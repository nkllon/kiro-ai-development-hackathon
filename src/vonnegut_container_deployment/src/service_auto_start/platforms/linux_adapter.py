#!/usr/bin/env python3
"""
Linux systemd Generator - Platform Adapter for Linux Auto-Start

Generates and manages systemd service unit files for service auto-start
configuration with proper dependency management and restart policies.
"""

import os
import subprocess
from pathlib import Path
from typing import Dict, Any, Optional

from ..core.service_auto_starter import ServiceAutoStarter, ServiceDefinition


class LinuxSystemdAdapter(ServiceAutoStarter):
    """
    Linux systemd adapter for service auto-start management.
    
    Creates and manages systemd service unit files with proper dependency
    resolution, restart policies, and user/system service integration.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize Linux systemd adapter."""
        super().__init__(config)
        
        # Determine if we should use user or system services
        self._use_user_services = config.get("use_user_services", True) if config else True
        
        if self._use_user_services:
            # User service directory
            self._systemd_dir = Path.home() / ".config" / "systemd" / "user"
        else:
            # System service directory (requires root)
            self._systemd_dir = Path("/etc/systemd/system")
        
        self._systemd_dir.mkdir(parents=True, exist_ok=True)
        
        self._logger.info(f"Linux systemd adapter initialized, services dir: {self._systemd_dir}")
        self._logger.info(f"Using {'user' if self._use_user_services else 'system'} services")
    
    def generate_config(self, service: ServiceDefinition) -> Dict[str, Any]:
        """
        Generate systemd service unit file configuration.
        
        Args:
            service: Service definition
            
        Returns:
            Systemd service configuration dictionary
        """
        try:
            # Build systemd unit file content
            unit_content = "[Unit]\n"
            unit_content += f"Description={service.description or service.name}\n"
            
            # Add dependencies
            if service.dependencies:
                # Convert service names to systemd service names
                systemd_deps = [f"{dep}.service" for dep in service.dependencies]
                unit_content += f"After={' '.join(systemd_deps)}\n"
                unit_content += f"Wants={' '.join(systemd_deps)}\n"
            
            unit_content += "\n[Service]\n"
            unit_content += f"Type=simple\n"
            unit_content += f"ExecStart={service.command}\n"
            unit_content += f"WorkingDirectory={service.working_directory}\n"
            
            # Add restart policy
            if service.restart_policy == "always":
                unit_content += "Restart=always\n"
                unit_content += "RestartSec=10\n"
            elif service.restart_policy == "on-failure":
                unit_content += "Restart=on-failure\n"
                unit_content += "RestartSec=10\n"
            elif service.restart_policy == "unless-stopped":
                unit_content += "Restart=on-failure\n"
                unit_content += "RestartSec=10\n"
            
            # Add user if specified
            if service.user and not self._use_user_services:
                unit_content += f"User={service.user}\n"
            
            # Add environment variables
            if service.environment:
                for key, value in service.environment.items():
                    unit_content += f"Environment={key}={value}\n"
            
            # Add logging
            unit_content += "StandardOutput=journal\n"
            unit_content += "StandardError=journal\n"
            unit_content += f"SyslogIdentifier={service.name}\n"
            
            unit_content += "\n[Install]\n"
            if self._use_user_services:
                unit_content += "WantedBy=default.target\n"
            else:
                unit_content += "WantedBy=multi-user.target\n"
            
            config = {
                "unit_content": unit_content,
                "service_name": f"{service.name}.service",
                "use_user_services": self._use_user_services
            }
            
            self._logger.info(f"Generated systemd config for {service.name}")
            return config
            
        except Exception as e:
            self._logger.error(f"Failed to generate config for {service.name}: {e}")
            return {}
    
    def install_config(self, service: ServiceDefinition, config: Dict[str, Any]) -> bool:
        """
        Install systemd service unit file and enable the service.
        
        Args:
            service: Service definition
            config: Generated systemd configuration
            
        Returns:
            True if installation successful, False otherwise
        """
        try:
            service_filename = config["service_name"]
            service_path = self._systemd_dir / service_filename
            
            # Write service unit file
            with open(service_path, 'w') as f:
                f.write(config["unit_content"])
            
            self._logger.info(f"Created service file: {service_path}")
            
            # Reload systemd daemon
            systemctl_cmd = ["systemctl"]
            if self._use_user_services:
                systemctl_cmd.append("--user")
            
            result = subprocess.run(
                systemctl_cmd + ["daemon-reload"],
                capture_output=True, text=True
            )
            
            if result.returncode != 0:
                self._logger.error(f"Failed to reload systemd daemon: {result.stderr}")
                return False
            
            # Enable the service
            result = subprocess.run(
                systemctl_cmd + ["enable", service_filename],
                capture_output=True, text=True
            )
            
            if result.returncode != 0:
                self._logger.error(f"Failed to enable service: {result.stderr}")
                return False
            
            # Start the service
            result = subprocess.run(
                systemctl_cmd + ["start", service_filename],
                capture_output=True, text=True
            )
            
            if result.returncode != 0:
                self._logger.warning(f"Failed to start service immediately: {result.stderr}")
                # This is not necessarily a failure - service will start on boot
            
            self._logger.info(f"Successfully installed and enabled systemd service for {service.name}")
            return True
            
        except Exception as e:
            self._logger.error(f"Failed to install config for {service.name}: {e}")
            return False
    
    def verify_autostart(self, service: ServiceDefinition) -> bool:
        """
        Verify that the systemd service is properly configured and enabled.
        
        Args:
            service: Service definition to verify
            
        Returns:
            True if auto-start is properly configured, False otherwise
        """
        try:
            service_name = f"{service.name}.service"
            systemctl_cmd = ["systemctl"]
            if self._use_user_services:
                systemctl_cmd.append("--user")
            
            # Check if service is enabled
            result = subprocess.run(
                systemctl_cmd + ["is-enabled", service_name],
                capture_output=True, text=True
            )
            
            if result.returncode != 0:
                self._logger.error(f"Service {service_name} is not enabled: {result.stdout.strip()}")
                return False
            
            # Check if service file exists
            service_path = self._systemd_dir / service_name
            if not service_path.exists():
                self._logger.error(f"Service file not found: {service_path}")
                return False
            
            # Check service status
            result = subprocess.run(
                systemctl_cmd + ["status", service_name],
                capture_output=True, text=True
            )
            
            # Service might not be running but still be properly configured
            self._logger.info(f"Service {service_name} is properly configured and enabled")
            return True
            
        except Exception as e:
            self._logger.error(f"Failed to verify auto-start for {service.name}: {e}")
            return False
    
    def remove_autostart(self, service: ServiceDefinition) -> bool:
        """
        Remove systemd service configuration and disable the service.
        
        Args:
            service: Service definition to remove
            
        Returns:
            True if removal successful, False otherwise
        """
        try:
            service_name = f"{service.name}.service"
            service_path = self._systemd_dir / service_name
            systemctl_cmd = ["systemctl"]
            if self._use_user_services:
                systemctl_cmd.append("--user")
            
            # Stop the service if running
            subprocess.run(
                systemctl_cmd + ["stop", service_name],
                capture_output=True, text=True
            )
            
            # Disable the service
            result = subprocess.run(
                systemctl_cmd + ["disable", service_name],
                capture_output=True, text=True
            )
            
            if result.returncode != 0:
                self._logger.warning(f"Failed to disable service: {result.stderr}")
            
            # Remove service file
            if service_path.exists():
                service_path.unlink()
                self._logger.info(f"Removed service file: {service_path}")
            
            # Reload systemd daemon
            subprocess.run(
                systemctl_cmd + ["daemon-reload"],
                capture_output=True, text=True
            )
            
            self._logger.info(f"Successfully removed systemd service for {service.name}")
            return True
            
        except Exception as e:
            self._logger.error(f"Failed to remove auto-start for {service.name}: {e}")
            return False
    
    def get_service_status(self, service: ServiceDefinition) -> Dict[str, Any]:
        """
        Get current status of the systemd service.
        
        Args:
            service: Service definition
            
        Returns:
            Status information dictionary
        """
        try:
            service_name = f"{service.name}.service"
            systemctl_cmd = ["systemctl"]
            if self._use_user_services:
                systemctl_cmd.append("--user")
            
            # Get service status
            result = subprocess.run(
                systemctl_cmd + ["status", service_name, "--no-pager"],
                capture_output=True, text=True
            )
            
            # Get enabled status
            enabled_result = subprocess.run(
                systemctl_cmd + ["is-enabled", service_name],
                capture_output=True, text=True
            )
            
            # Get active status
            active_result = subprocess.run(
                systemctl_cmd + ["is-active", service_name],
                capture_output=True, text=True
            )
            
            return {
                "enabled": enabled_result.returncode == 0,
                "enabled_status": enabled_result.stdout.strip(),
                "active": active_result.returncode == 0,
                "active_status": active_result.stdout.strip(),
                "status_output": result.stdout,
                "service_name": service_name
            }
            
        except Exception as e:
            return {"error": str(e)}
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get health status for Linux systemd adapter."""
        base_status = super().get_health_status()
        
        # Add systemd-specific status
        base_status.update({
            "systemd_dir": str(self._systemd_dir),
            "systemd_dir_exists": self._systemd_dir.exists(),
            "use_user_services": self._use_user_services,
            "systemctl_available": self._check_systemctl_available()
        })
        
        return base_status
    
    def _check_systemctl_available(self) -> bool:
        """Check if systemctl command is available."""
        try:
            cmd = ["systemctl"]
            if self._use_user_services:
                cmd.append("--user")
            cmd.append("--version")
            
            result = subprocess.run(cmd, capture_output=True, timeout=5)
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return False