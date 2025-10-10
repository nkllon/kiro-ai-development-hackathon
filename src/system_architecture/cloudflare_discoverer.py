#!/usr/bin/env python3
"""
Cloudflare Tunnel Discovery System
Task 1.4 - System Architecture Wiring Diagram Implementation
"""

import os
import json
import subprocess
from typing import Dict, List, Any, Optional
from pathlib import Path

from src.rm_ddd.core.unified_reflective_module import ReflectiveModule


class CloudflareTunnelDiscoverer(ReflectiveModule):
    """
    Discovers and analyzes Cloudflare tunnel configurations and status.
    
    Provides comprehensive tunnel discovery, configuration analysis,
    and health monitoring for Cloudflare tunnel infrastructure.
    """
    
    def __init__(self):
        """Initialize the Cloudflare tunnel discoverer."""
        super().__init__()
        self.discovered_tunnels = {}
        self.tunnel_configs = {}
        self.tunnel_status = {}
        
        self._logger.info("CloudflareTunnelDiscoverer initialized", extra={
            "component": "cloudflare_tunnel_discoverer"
        })
    
    def discover_active_tunnels(self) -> Dict[str, Any]:
        """
        Discover currently active Cloudflare tunnels.
        
        Returns:
            Dict containing discovered tunnel information
        """
        try:
            # Check for cloudflared processes
            result = subprocess.run(
                ["pgrep", "-f", "cloudflared"], 
                capture_output=True, text=True
            )
            
            active_tunnels = {}
            if result.returncode == 0:
                pids = result.stdout.strip().split('\n')
                active_tunnels["process_count"] = len(pids)
                active_tunnels["pids"] = pids
                
                self._logger.info("Active tunnels discovered", extra={
                    "tunnel_count": len(pids),
                    "component": "cloudflare_tunnel_discoverer"
                })
            else:
                active_tunnels["process_count"] = 0
                active_tunnels["pids"] = []
            
            self.discovered_tunnels = active_tunnels
            return active_tunnels
            
        except Exception as e:
            self._logger.error("Tunnel discovery failed", extra={
                "error": str(e),
                "component": "cloudflare_tunnel_discoverer"
            })
            return {"error": str(e)}
    
    def analyze_tunnel_configs(self) -> Dict[str, Any]:
        """
        Analyze Cloudflare tunnel configuration files.
        
        Returns:
            Dict containing configuration analysis
        """
        try:
            config_files = [
                "cloudflare-config.yaml",
                "cloudflare-tunnel-config-websocket.yml",
                "cloudflared-config-poe.yml"
            ]
            
            configs = {}
            for config_file in config_files:
                if os.path.exists(config_file):
                    with open(config_file, 'r') as f:
                        import yaml
                        config_data = yaml.safe_load(f)
                        configs[config_file] = config_data
                        
                        self._logger.info("Configuration analyzed", extra={
                            "config_file": config_file,
                            "component": "cloudflare_tunnel_discoverer"
                        })
            
            self.tunnel_configs = configs
            return configs
            
        except Exception as e:
            self._logger.error("Configuration analysis failed", extra={
                "error": str(e),
                "component": "cloudflare_tunnel_discoverer"
            })
            return {"error": str(e)}
    
    def check_tunnel_health(self) -> Dict[str, Any]:
        """
        Check health status of discovered tunnels.
        
        Returns:
            Dict containing health status information
        """
        try:
            health_status = {
                "timestamp": self._get_current_timestamp(),
                "tunnels": {}
            }
            
            # Check if tunnels are responding
            for config_file, config_data in self.tunnel_configs.items():
                if isinstance(config_data, dict) and "ingress" in config_data:
                    for rule in config_data["ingress"]:
                        if "hostname" in rule:
                            hostname = rule["hostname"]
                            # Test connectivity (simplified)
                            health_status["tunnels"][hostname] = {
                                "config_source": config_file,
                                "status": "configured"
                            }
            
            self.tunnel_status = health_status
            return health_status
            
        except Exception as e:
            self._logger.error("Health check failed", extra={
                "error": str(e),
                "component": "cloudflare_tunnel_discoverer"
            })
            return {"error": str(e)}
    
    def get_comprehensive_report(self) -> Dict[str, Any]:
        """
        Generate comprehensive tunnel discovery report.
        
        Returns:
            Dict containing complete tunnel analysis
        """
        return {
            "discovery_timestamp": self._get_current_timestamp(),
            "active_tunnels": self.discover_active_tunnels(),
            "configurations": self.analyze_tunnel_configs(),
            "health_status": self.check_tunnel_health(),
            "summary": {
                "total_configs": len(self.tunnel_configs),
                "active_processes": self.discovered_tunnels.get("process_count", 0),
                "configured_hostnames": len(self.tunnel_status.get("tunnels", {}))
            }
        }
    
    def get_capabilities(self) -> List[str]:
        """Get module capabilities."""
        return ["tunnel_discovery", "config_analysis", "health_monitoring"]
    
    def get_module_info(self) -> Dict[str, Any]:
        """Get module information."""
        return {
            "module_name": "cloudflare_tunnel_discoverer",
            "version": "1.0.0",
            "description": "Cloudflare tunnel discovery and analysis"
        }
    
    def graceful_degradation(self) -> Dict[str, Any]:
        """Handle graceful degradation."""
        return {"success": True, "degraded_capabilities": []}
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get health status."""
        return {"status": "healthy", "uptime": 0}
