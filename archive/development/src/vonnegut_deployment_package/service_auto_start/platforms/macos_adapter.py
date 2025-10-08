#!/usr/bin/env python3
"""
macOS LaunchAgent Generator - Platform Adapter for macOS Auto-Start

Generates and manages macOS LaunchAgent plist files for service auto-start
configuration with proper user session integration.
"""

import os
import plistlib
import subprocess
from pathlib import Path
from typing import Dict, Any, Optional

from ..core.service_auto_starter import ServiceAutoStarter, ServiceDefinition


class MacOSLaunchAgentAdapter(ServiceAutoStarter):
    """
    macOS LaunchAgent adapter for service auto-start management.
    
    Creates and manages LaunchAgent plist files in ~/Library/LaunchAgents/
    with proper macOS service integration and user session handling.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize macOS adapter."""
        super().__init__(config)
        
        # macOS-specific paths
        self._launch_agents_dir = Path.home() / "Library" / "LaunchAgents"
        self._launch_agents_dir.mkdir(parents=True, exist_ok=True)
        
        self._logger.info(f"macOS LaunchAgent adapter initialized, agents dir: {self._launch_agents_dir}")
    
    def get_capabilities(self) -> Dict[str, Any]:
        """Get MacOSLaunchAgentAdapter capabilities."""
        return {
            "launchd_integration": True,
            "user_agents": True,
            "plist_generation": True,
            "automatic_startup": True
        }
    
    def get_module_info(self) -> Dict[str, Any]:
        """Get module information."""
        return {
            "name": "MacOSLaunchAgentAdapter",
            "version": "1.0.0",
            "description": "macOS LaunchAgent service auto-start adapter",
            "author": "Beast Mode Framework"
        }
    
    def graceful_degradation(self, error: Exception) -> Dict[str, Any]:
        """Handle graceful degradation on errors."""
        self._logger.error(f"MacOSLaunchAgentAdapter degradation: {error}")
        return {
            "status": "degraded",
            "error": str(error),
            "fallback_mode": "manual_launchctl"
        }
    
    def generate_config(self, service: ServiceDefinition) -> Dict[str, Any]:
        """
        Generate macOS LaunchAgent plist configuration.
        
        Args:
            service: Service definition
            
        Returns:
            LaunchAgent plist configuration dictionary
        """
        try:
            # Build command array
            command_parts = service.command.split()
            
            # Create LaunchAgent plist structure
            plist_config = {
                "Label": f"com.beastmode.{service.name}",
                "ProgramArguments": command_parts,
                "WorkingDirectory": service.working_directory,
                "RunAtLoad": True,
                "KeepAlive": True,
                "StandardOutPath": f"/tmp/{service.name}.out.log",
                "StandardErrorPath": f"/tmp/{service.name}.err.log"
            }
            
            # Add environment variables if specified
            if service.environment:
                plist_config["EnvironmentVariables"] = service.environment
            
            # Add user if specified
            if service.user:
                plist_config["UserName"] = service.user
            
            # Configure restart behavior based on restart policy
            if service.restart_policy == "always":
                plist_config["KeepAlive"] = True
            elif service.restart_policy == "on-failure":
                plist_config["KeepAlive"] = {"SuccessfulExit": False}
            elif service.restart_policy == "no":
                plist_config["KeepAlive"] = False
            
            self._logger.info(f"Generated LaunchAgent config for {service.name}")
            return plist_config
            
        except Exception as e:
            self._logger.error(f"Failed to generate config for {service.name}: {e}")
            return {}
    
    def install_config(self, service: ServiceDefinition, config: Dict[str, Any]) -> bool:
        """
        Install LaunchAgent plist file and load the service.
        
        Args:
            service: Service definition
            config: Generated plist configuration
            
        Returns:
            True if installation successful, False otherwise
        """
        try:
            plist_filename = f"com.beastmode.{service.name}.plist"
            plist_path = self._launch_agents_dir / plist_filename
            
            # Write plist file
            with open(plist_path, 'wb') as f:
                plistlib.dump(config, f)
            
            self._logger.info(f"Created plist file: {plist_path}")
            
            # Load the LaunchAgent
            result = subprocess.run([
                "launchctl", "load", str(plist_path)
            ], capture_output=True, text=True)
            
            if result.returncode != 0:
                self._logger.error(f"Failed to load LaunchAgent: {result.stderr}")
                return False
            
            # Start the service
            label = config["Label"]
            result = subprocess.run([
                "launchctl", "start", label
            ], capture_output=True, text=True)
            
            if result.returncode != 0:
                self._logger.warning(f"Failed to start service immediately: {result.stderr}")
                # This is not necessarily a failure - service might start on next login
            
            self._logger.info(f"Successfully installed and loaded LaunchAgent for {service.name}")
            return True
            
        except Exception as e:
            self._logger.error(f"Failed to install config for {service.name}: {e}")
            return False
    
    def verify_autostart(self, service: ServiceDefinition) -> bool:
        """
        Verify that the LaunchAgent is properly configured and loaded.
        
        Args:
            service: Service definition to verify
            
        Returns:
            True if auto-start is properly configured, False otherwise
        """
        try:
            label = f"com.beastmode.{service.name}"
            
            # Check if LaunchAgent is loaded
            result = subprocess.run([
                "launchctl", "list", label
            ], capture_output=True, text=True)
            
            if result.returncode != 0:
                self._logger.error(f"LaunchAgent {label} is not loaded")
                return False
            
            # Parse launchctl output to check status
            output_lines = result.stdout.strip().split('\n')
            if len(output_lines) < 2:
                self._logger.error(f"Unexpected launchctl output for {label}")
                return False
            
            # Check if plist file exists
            plist_path = self._launch_agents_dir / f"{label}.plist"
            if not plist_path.exists():
                self._logger.error(f"Plist file not found: {plist_path}")
                return False
            
            self._logger.info(f"LaunchAgent {label} is properly configured and loaded")
            return True
            
        except Exception as e:
            self._logger.error(f"Failed to verify auto-start for {service.name}: {e}")
            return False
    
    def remove_autostart(self, service: ServiceDefinition) -> bool:
        """
        Remove LaunchAgent configuration and unload the service.
        
        Args:
            service: Service definition to remove
            
        Returns:
            True if removal successful, False otherwise
        """
        try:
            label = f"com.beastmode.{service.name}"
            plist_path = self._launch_agents_dir / f"{label}.plist"
            
            # Stop the service if running
            subprocess.run([
                "launchctl", "stop", label
            ], capture_output=True, text=True)
            
            # Unload the LaunchAgent
            if plist_path.exists():
                result = subprocess.run([
                    "launchctl", "unload", str(plist_path)
                ], capture_output=True, text=True)
                
                if result.returncode != 0:
                    self._logger.warning(f"Failed to unload LaunchAgent: {result.stderr}")
                
                # Remove plist file
                plist_path.unlink()
                self._logger.info(f"Removed plist file: {plist_path}")
            
            self._logger.info(f"Successfully removed LaunchAgent for {service.name}")
            return True
            
        except Exception as e:
            self._logger.error(f"Failed to remove auto-start for {service.name}: {e}")
            return False
    
    def get_service_status(self, service: ServiceDefinition) -> Dict[str, Any]:
        """
        Get current status of the LaunchAgent service.
        
        Args:
            service: Service definition
            
        Returns:
            Status information dictionary
        """
        try:
            label = f"com.beastmode.{service.name}"
            
            result = subprocess.run([
                "launchctl", "list", label
            ], capture_output=True, text=True)
            
            if result.returncode != 0:
                return {
                    "loaded": False,
                    "running": False,
                    "error": result.stderr
                }
            
            # Parse output
            lines = result.stdout.strip().split('\n')
            if len(lines) >= 2:
                status_line = lines[1].split('\t')
                pid = status_line[0] if status_line[0] != '-' else None
                exit_code = status_line[1] if len(status_line) > 1 and status_line[1] != '-' else None
                
                return {
                    "loaded": True,
                    "running": pid is not None,
                    "pid": pid,
                    "exit_code": exit_code,
                    "label": label
                }
            
            return {"loaded": True, "running": False}
            
        except Exception as e:
            return {"error": str(e)}
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get health status for macOS adapter."""
        base_status = super().get_health_status()
        
        # Add macOS-specific status
        base_status.update({
            "launch_agents_dir": str(self._launch_agents_dir),
            "launch_agents_dir_exists": self._launch_agents_dir.exists(),
            "launchctl_available": self._check_launchctl_available()
        })
        
        return base_status
    
    def _check_launchctl_available(self) -> bool:
        """Check if launchctl command is available."""
        try:
            result = subprocess.run(["launchctl", "version"], 
                                  capture_output=True, timeout=5)
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return False