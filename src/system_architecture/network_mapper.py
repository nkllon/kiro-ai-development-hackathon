#!/usr/bin/env python3
"""
Network Topology Discovery System
Task 1.6 - System Architecture Wiring Diagram Implementation
"""

import os
import subprocess
import socket
from typing import Dict, List, Any, Optional
from pathlib import Path

from src.rm_ddd.core.unified_reflective_module import ReflectiveModule


class NetworkTopologyMapper(ReflectiveModule):
    """
    Maps network topology and service connectivity for system architecture.
    
    Provides comprehensive network discovery, port analysis,
    and service connectivity mapping.
    """
    
    def __init__(self):
        """Initialize the network topology mapper."""
        super().__init__()
        self.discovered_services = {}
        self.port_mappings = {}
        self.network_interfaces = {}
        
        self._logger.info("NetworkTopologyMapper initialized", extra={
            "component": "network_topology_mapper"
        })
    
    def discover_listening_ports(self) -> Dict[str, Any]:
        """
        Discover services listening on network ports.
        
        Returns:
            Dict containing port and service information
        """
        try:
            # Use lsof to find listening ports
            result = subprocess.run(
                ["lsof", "-i", "-P", "-n"], 
                capture_output=True, text=True
            )
            
            services = {}
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')[1:]  # Skip header
                
                for line in lines:
                    parts = line.split()
                    if len(parts) >= 9 and "LISTEN" in line:
                        command = parts[0]
                        pid = parts[1]
                        address_port = parts[8]
                        
                        if ':' in address_port:
                            address, port = address_port.rsplit(':', 1)
                            
                            services[port] = {
                                "command": command,
                                "pid": pid,
                                "address": address,
                                "port": port,
                                "full_address": address_port
                            }
            
            self.discovered_services = services
            
            self._logger.info("Listening ports discovered", extra={
                "service_count": len(services),
                "component": "network_topology_mapper"
            })
            
            return services
            
        except Exception as e:
            self._logger.error("Port discovery failed", extra={
                "error": str(e),
                "component": "network_topology_mapper"
            })
            return {"error": str(e)}
    
    def map_service_connectivity(self) -> Dict[str, Any]:
        """
        Map connectivity between discovered services.
        
        Returns:
            Dict containing service connectivity map
        """
        try:
            connectivity_map = {
                "services": self.discovered_services,
                "connections": [],
                "service_groups": {}
            }
            
            # Group services by type
            web_services = []
            database_services = []
            monitoring_services = []
            other_services = []
            
            for port, service in self.discovered_services.items():
                command = service["command"].lower()
                
                if any(web in command for web in ["nginx", "apache", "httpd", "node", "python"]):
                    web_services.append(service)
                elif any(db in command for db in ["postgres", "mysql", "redis", "mongo"]):
                    database_services.append(service)
                elif any(mon in command for mon in ["prometheus", "grafana", "jaeger"]):
                    monitoring_services.append(service)
                else:
                    other_services.append(service)
            
            connectivity_map["service_groups"] = {
                "web_services": web_services,
                "database_services": database_services,
                "monitoring_services": monitoring_services,
                "other_services": other_services
            }
            
            self._logger.info("Service connectivity mapped", extra={
                "web_services": len(web_services),
                "database_services": len(database_services),
                "monitoring_services": len(monitoring_services),
                "component": "network_topology_mapper"
            })
            
            return connectivity_map
            
        except Exception as e:
            self._logger.error("Connectivity mapping failed", extra={
                "error": str(e),
                "component": "network_topology_mapper"
            })
            return {"error": str(e)}
    
    def discover_network_interfaces(self) -> Dict[str, Any]:
        """
        Discover network interfaces and their configurations.
        
        Returns:
            Dict containing network interface information
        """
        try:
            interfaces = {}
            
            # Get hostname
            hostname = socket.gethostname()
            
            # Get local IP addresses
            try:
                # Connect to a remote address to determine local IP
                s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                s.connect(("8.8.8.8", 80))
                local_ip = s.getsockname()[0]
                s.close()
            except:
                local_ip = "127.0.0.1"
            
            interfaces["primary"] = {
                "hostname": hostname,
                "local_ip": local_ip,
                "loopback": "127.0.0.1"
            }
            
            self.network_interfaces = interfaces
            
            self._logger.info("Network interfaces discovered", extra={
                "hostname": hostname,
                "local_ip": local_ip,
                "component": "network_topology_mapper"
            })
            
            return interfaces
            
        except Exception as e:
            self._logger.error("Network interface discovery failed", extra={
                "error": str(e),
                "component": "network_topology_mapper"
            })
            return {"error": str(e)}
    
    def get_comprehensive_topology(self) -> Dict[str, Any]:
        """
        Generate comprehensive network topology report.
        
        Returns:
            Dict containing complete topology analysis
        """
        return {
            "topology_timestamp": self._get_current_timestamp(),
            "listening_services": self.discover_listening_ports(),
            "service_connectivity": self.map_service_connectivity(),
            "network_interfaces": self.discover_network_interfaces(),
            "summary": {
                "total_services": len(self.discovered_services),
                "unique_commands": len(set(s["command"] for s in self.discovered_services.values())),
                "hostname": self.network_interfaces.get("primary", {}).get("hostname", "unknown")
            }
        }
    
    def get_capabilities(self) -> List[str]:
        """Get module capabilities."""
        return ["network_discovery", "service_mapping", "topology_analysis"]
    
    def get_module_info(self) -> Dict[str, Any]:
        """Get module information."""
        return {
            "module_name": "network_topology_mapper",
            "version": "1.0.0",
            "description": "Network topology discovery and service mapping"
        }
    
    def graceful_degradation(self) -> Dict[str, Any]:
        """Handle graceful degradation."""
        return {"success": True, "degraded_capabilities": []}
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get health status."""
        return {"status": "healthy", "uptime": 0}
