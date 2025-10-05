#!/usr/bin/env python3
"""
Observatory Integration Module
==============================

Integration module for Observatory system with Makefile governance.
Provides Observatory-specific targets and management capabilities.

Author: Beast Mode Framework
Date: 2025-01-27
Purpose: Observatory system integration for Makefile governance
"""

import os
import sys
import json
import subprocess
import time
from pathlib import Path
from typing import Dict, List, Set, Any, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum

from src.rm_ddd.core.unified_reflective_module import ReflectiveModule


class ObservatoryService(Enum):
    """Observatory service types."""
    MAIN = "observatory"
    PROMETHEUS = "prometheus"
    GRAFANA = "grafana"
    WEBSOCKET = "websocket"
    HEALTH_MONITOR = "health_monitor"


@dataclass
class ServiceConfig:
    """Observatory service configuration."""
    name: str
    port: int
    health_endpoint: str
    start_script: Optional[str] = None
    stop_script: Optional[str] = None
    config_file: Optional[str] = None
    log_file: Optional[str] = None


class ObservatoryIntegration(ReflectiveModule):
    """
    🔭 OBSERVATORY INTEGRATION MODULE 🔭
    
    Integration module for Observatory system with Makefile governance.
    Provides Observatory-specific targets and management capabilities.
    """
    
    def __init__(self, repository_root: str = "."):
        super().__init__()
        self.module_id = "observatory_integration"
        self.repository_root = Path(repository_root)
        
        # Service configurations
        self.services = self._initialize_service_configs()
        
        # Observatory paths
        self.observatory_dir = self.repository_root / "src" / "observatory_infrastructure"
        self.scripts_dir = self.repository_root / "scripts"
        self.config_dir = self.repository_root / "config"
        self.logs_dir = self.repository_root / "logs"
    
    def _initialize_service_configs(self) -> Dict[ObservatoryService, ServiceConfig]:
        """Initialize Observatory service configurations."""
        return {
            ObservatoryService.MAIN: ServiceConfig(
                name="observatory",
                port=8888,
                health_endpoint="/health",
                start_script="deploy_observatory.py",
                stop_script="stop_observatory.py",
                config_file="observatory_config.json",
                log_file="observatory.log"
            ),
            ObservatoryService.PROMETHEUS: ServiceConfig(
                name="prometheus",
                port=9090,
                health_endpoint="/metrics",
                start_script="start_prometheus.py",
                stop_script="stop_prometheus.py",
                config_file="prometheus.yml",
                log_file="prometheus.log"
            ),
            ObservatoryService.GRAFANA: ServiceConfig(
                name="grafana",
                port=3000,
                health_endpoint="/api/health",
                start_script="start_grafana.py",
                stop_script="stop_grafana.py",
                config_file="grafana.ini",
                log_file="grafana.log"
            ),
            ObservatoryService.WEBSOCKET: ServiceConfig(
                name="websocket",
                port=8889,
                health_endpoint="/ws/health",
                start_script="start_websocket_server.py",
                stop_script="stop_websocket_server.py",
                log_file="websocket.log"
            ),
            ObservatoryService.HEALTH_MONITOR: ServiceConfig(
                name="health_monitor",
                port=8890,
                health_endpoint="/monitor/health",
                start_script="start_health_monitor.py",
                stop_script="stop_health_monitor.py",
                log_file="health_monitor.log"
            )
        }
    
    def generate_observatory_targets(self) -> Dict[str, Dict[str, Any]]:
        """Generate Observatory-specific Makefile targets."""
        targets = {}
        
        # Service management targets
        for service_type, config in self.services.items():
            service_targets = self._generate_service_targets(service_type, config)
            targets.update(service_targets)
        
        # System-level targets
        system_targets = self._generate_system_targets()
        targets.update(system_targets)
        
        # Monitoring and health targets
        monitoring_targets = self._generate_monitoring_targets()
        targets.update(monitoring_targets)
        
        return targets
    
    def _generate_service_targets(self, service_type: ObservatoryService, 
                                config: ServiceConfig) -> Dict[str, Dict[str, Any]]:
        """Generate targets for a specific Observatory service."""
        service_name = config.name
        targets = {}
        
        # Start service target
        targets[f"observatory-{service_name}-start"] = {
            "description": f"Start {service_name} service",
            "commands": self._get_start_commands(config),
            "phony": True,
            "category": "observatory"
        }
        
        # Stop service target
        targets[f"observatory-{service_name}-stop"] = {
            "description": f"Stop {service_name} service",
            "commands": self._get_stop_commands(config),
            "phony": True,
            "category": "observatory"
        }
        
        # Restart service target
        targets[f"observatory-{service_name}-restart"] = {
            "description": f"Restart {service_name} service",
            "commands": [
                f"$(MAKE) observatory-{service_name}-stop",
                "@sleep 2",
                f"$(MAKE) observatory-{service_name}-start"
            ],
            "phony": True,
            "category": "observatory"
        }
        
        # Status check target
        targets[f"observatory-{service_name}-status"] = {
            "description": f"Check {service_name} service status",
            "commands": self._get_status_commands(config),
            "phony": True,
            "category": "observatory"
        }
        
        # Health check target
        targets[f"observatory-{service_name}-health"] = {
            "description": f"Check {service_name} service health",
            "commands": self._get_health_commands(config),
            "phony": True,
            "category": "observatory"
        }
        
        # Logs target
        targets[f"observatory-{service_name}-logs"] = {
            "description": f"View {service_name} service logs",
            "commands": self._get_logs_commands(config),
            "phony": True,
            "category": "observatory"
        }
        
        return targets
    
    def _generate_system_targets(self) -> Dict[str, Dict[str, Any]]:
        """Generate system-level Observatory targets."""
        return {
            "observatory-deploy": {
                "description": "Deploy complete Observatory system",
                "commands": [
                    "@echo '🔭 Deploying Observatory system...'",
                    "$(MAKE) observatory-prometheus-start",
                    "@sleep 3",
                    "$(MAKE) observatory-grafana-start", 
                    "@sleep 3",
                    "$(MAKE) observatory-websocket-start",
                    "@sleep 2",
                    "$(MAKE) observatory-health-monitor-start",
                    "@sleep 2",
                    "$(MAKE) observatory-observatory-start",
                    "@echo '✅ Observatory system deployed'"
                ],
                "phony": True,
                "category": "observatory"
            },
            "observatory-shutdown": {
                "description": "Shutdown complete Observatory system",
                "commands": [
                    "@echo '🔭 Shutting down Observatory system...'",
                    "$(MAKE) observatory-observatory-stop",
                    "$(MAKE) observatory-health-monitor-stop",
                    "$(MAKE) observatory-websocket-stop",
                    "$(MAKE) observatory-grafana-stop",
                    "$(MAKE) observatory-prometheus-stop",
                    "@echo '✅ Observatory system shutdown complete'"
                ],
                "phony": True,
                "category": "observatory"
            },
            "observatory-status": {
                "description": "Check status of all Observatory services",
                "commands": [
                    "@echo '🔭 Observatory System Status:'",
                    "@echo '================================'",
                    "$(MAKE) observatory-prometheus-status",
                    "$(MAKE) observatory-grafana-status",
                    "$(MAKE) observatory-websocket-status",
                    "$(MAKE) observatory-health-monitor-status",
                    "$(MAKE) observatory-observatory-status"
                ],
                "phony": True,
                "category": "observatory"
            },
            "observatory-health": {
                "description": "Check health of all Observatory services",
                "commands": [
                    "@echo '🔭 Observatory System Health Check:'",
                    "@echo '===================================='",
                    "$(MAKE) observatory-prometheus-health",
                    "$(MAKE) observatory-grafana-health",
                    "$(MAKE) observatory-websocket-health",
                    "$(MAKE) observatory-health-monitor-health",
                    "$(MAKE) observatory-observatory-health"
                ],
                "phony": True,
                "category": "observatory"
            },
            "observatory-logs": {
                "description": "View logs from all Observatory services",
                "commands": [
                    "@echo '🔭 Observatory System Logs:'",
                    "@echo '============================'",
                    "$(MAKE) observatory-prometheus-logs",
                    "$(MAKE) observatory-grafana-logs",
                    "$(MAKE) observatory-websocket-logs",
                    "$(MAKE) observatory-health-monitor-logs",
                    "$(MAKE) observatory-observatory-logs"
                ],
                "phony": True,
                "category": "observatory"
            },
            "observatory-validate": {
                "description": "Validate Observatory system configuration",
                "commands": [
                    "@echo '🔭 Validating Observatory configuration...'",
                    "python scripts/validate_observatory_config.py",
                    "python scripts/check_observatory_dependencies.py",
                    "@echo '✅ Observatory validation complete'"
                ],
                "phony": True,
                "category": "observatory"
            }
        }
    
    def _generate_monitoring_targets(self) -> Dict[str, Dict[str, Any]]:
        """Generate monitoring and diagnostic targets."""
        return {
            "observatory-dashboard": {
                "description": "Open Observatory dashboard",
                "commands": [
                    "@echo '🔭 Opening Observatory dashboard...'",
                    "python scripts/open_observatory_dashboard.py",
                    "@echo 'Dashboard available at: http://localhost:8888'"
                ],
                "phony": True,
                "category": "observatory"
            },
            "observatory-metrics": {
                "description": "Display Observatory metrics",
                "commands": [
                    "@echo '🔭 Observatory Metrics:'",
                    "@echo '======================'",
                    "curl -s http://localhost:9090/api/v1/query?query=up | jq '.' || echo 'Prometheus not available'",
                    "curl -s http://localhost:8888/metrics | head -20 || echo 'Observatory metrics not available'"
                ],
                "phony": True,
                "category": "observatory"
            },
            "observatory-test": {
                "description": "Run Observatory system tests",
                "commands": [
                    "@echo '🔭 Running Observatory tests...'",
                    "python -m pytest tests/integration/observatory/ -v",
                    "python scripts/test_observatory_endpoints.py",
                    "@echo '✅ Observatory tests complete'"
                ],
                "phony": True,
                "category": "observatory"
            },
            "observatory-backup": {
                "description": "Backup Observatory configuration and data",
                "commands": [
                    "@echo '🔭 Backing up Observatory system...'",
                    "python scripts/backup_observatory_config.py",
                    "python scripts/backup_observatory_data.py",
                    "@echo '✅ Observatory backup complete'"
                ],
                "phony": True,
                "category": "observatory"
            },
            "observatory-restore": {
                "description": "Restore Observatory from backup",
                "commands": [
                    "@echo '🔭 Restoring Observatory system...'",
                    "python scripts/restore_observatory_config.py",
                    "python scripts/restore_observatory_data.py",
                    "@echo '✅ Observatory restore complete'"
                ],
                "phony": True,
                "category": "observatory"
            }
        }
    
    def _get_start_commands(self, config: ServiceConfig) -> List[str]:
        """Get start commands for a service."""
        commands = []
        
        if config.start_script:
            script_path = self.scripts_dir / config.start_script
            if script_path.exists():
                commands.append(f"python {script_path}")
            else:
                commands.append(f"@echo 'Starting {config.name}...'")
                commands.append(f"@echo 'Start script not found: {script_path}'")
        else:
            commands.append(f"@echo 'Starting {config.name} service...'")
            commands.append(f"@echo 'No start script configured for {config.name}'")
        
        return commands
    
    def _get_stop_commands(self, config: ServiceConfig) -> List[str]:
        """Get stop commands for a service."""
        commands = []
        
        if config.stop_script:
            script_path = self.scripts_dir / config.stop_script
            if script_path.exists():
                commands.append(f"python {script_path}")
            else:
                commands.append(f"@echo 'Stopping {config.name}...'")
                # Fallback: try to kill by port
                commands.append(f"@lsof -ti:{config.port} | xargs kill -9 2>/dev/null || echo 'No process found on port {config.port}'")
        else:
            commands.append(f"@echo 'Stopping {config.name} service...'")
            commands.append(f"@lsof -ti:{config.port} | xargs kill -9 2>/dev/null || echo 'No process found on port {config.port}'")
        
        return commands
    
    def _get_status_commands(self, config: ServiceConfig) -> List[str]:
        """Get status check commands for a service."""
        return [
            f"@echo 'Checking {config.name} status...'",
            f"@lsof -i:{config.port} >/dev/null 2>&1 && echo '✅ {config.name} is running on port {config.port}' || echo '❌ {config.name} is not running'"
        ]
    
    def _get_health_commands(self, config: ServiceConfig) -> List[str]:
        """Get health check commands for a service."""
        return [
            f"@echo 'Checking {config.name} health...'",
            f"@curl -s http://localhost:{config.port}{config.health_endpoint} >/dev/null 2>&1 && echo '✅ {config.name} is healthy' || echo '❌ {config.name} health check failed'"
        ]
    
    def _get_logs_commands(self, config: ServiceConfig) -> List[str]:
        """Get log viewing commands for a service."""
        commands = []
        
        if config.log_file:
            log_path = self.logs_dir / config.log_file
            commands.extend([
                f"@echo '{config.name} logs:'",
                f"@echo '{'=' * (len(config.name) + 6)}'",
                f"@tail -20 {log_path} 2>/dev/null || echo 'No logs found for {config.name}'"
            ])
        else:
            commands.extend([
                f"@echo '{config.name} logs:'",
                f"@echo '{'=' * (len(config.name) + 6)}'",
                f"@echo 'No log file configured for {config.name}'"
            ])
        
        return commands
    
    def check_observatory_status(self) -> Dict[str, Any]:
        """Check the status of all Observatory services."""
        status = {
            "timestamp": time.strftime('%Y-%m-%d %H:%M:%S'),
            "services": {},
            "overall_status": "unknown"
        }
        
        running_services = 0
        total_services = len(self.services)
        
        for service_type, config in self.services.items():
            service_status = self._check_service_status(config)
            status["services"][config.name] = service_status
            
            if service_status["running"]:
                running_services += 1
        
        # Determine overall status
        if running_services == total_services:
            status["overall_status"] = "healthy"
        elif running_services > 0:
            status["overall_status"] = "partial"
        else:
            status["overall_status"] = "down"
        
        status["running_services"] = running_services
        status["total_services"] = total_services
        
        return status
    
    def _check_service_status(self, config: ServiceConfig) -> Dict[str, Any]:
        """Check the status of a specific service."""
        status = {
            "name": config.name,
            "port": config.port,
            "running": False,
            "healthy": False,
            "response_time": None
        }
        
        try:
            # Check if port is open
            import socket
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.settimeout(2)
                result = sock.connect_ex(('localhost', config.port))
                status["running"] = result == 0
            
            # If running, check health endpoint
            if status["running"]:
                try:
                    import requests
                    start_time = time.time()
                    response = requests.get(
                        f"http://localhost:{config.port}{config.health_endpoint}",
                        timeout=5
                    )
                    status["response_time"] = time.time() - start_time
                    status["healthy"] = response.status_code == 200
                except:
                    status["healthy"] = False
        
        except Exception:
            pass
        
        return status
    
    def generate_observatory_makefile(self, output_path: Optional[Path] = None) -> Path:
        """Generate Observatory-specific Makefile."""
        if output_path is None:
            output_path = self.repository_root / "makefiles" / "observatory.mk"
        
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        targets = self.generate_observatory_targets()
        
        content_lines = [
            "# Observatory System Makefile",
            "# Generated by Observatory Integration Module",
            f"# Generated on: {self._get_current_timestamp()}",
            "",
            "# Observatory service management and monitoring targets",
            "",
            "# Phony targets"
        ]
        
        # Collect phony targets
        phony_targets = [name for name, target in targets.items() if target.get("phony", False)]
        content_lines.append(f".PHONY: {' '.join(sorted(phony_targets))}")
        content_lines.append("")
        
        # Generate targets
        for target_name, target_config in sorted(targets.items()):
            # Target definition
            target_line = f"{target_name}:"
            if target_config.get("dependencies"):
                target_line += " " + " ".join(target_config["dependencies"])
            target_line += f" ## {target_config['description']}"
            
            content_lines.append(target_line)
            
            # Target commands
            for command in target_config["commands"]:
                content_lines.append(f"\t{command}")
            
            content_lines.append("")
        
        with open(output_path, 'w') as f:
            f.write("\n".join(content_lines))
        
        self._logger.info(f"🔭 Observatory Makefile generated: {output_path}")
        return output_path
    
    def get_capabilities(self) -> List[str]:
        """Get module capabilities."""
        return ["observatory_integration", "service_management", "health_monitoring"]
    
    def get_module_info(self) -> Dict[str, Any]:
        """Get module information."""
        return {
            "module_id": self.module_id,
            "name": "Observatory Integration",
            "version": "1.0.0",
            "description": "Integration module for Observatory system with Makefile governance"
        }
    
    def get_health_status(self):
        """Get module health status."""
        from src.rm_ddd.core.unified_reflective_module import ModuleStatus, HealthStatus
        return HealthStatus(
            module_id=self.module_id,
            status=ModuleStatus.HEALTHY,
            health_score=1.0,
            last_check=time.strftime('%Y-%m-%d %H:%M:%S')
        )
    
    def graceful_degradation(self, error: Exception) -> Dict[str, Any]:
        """Handle graceful degradation."""
        return {
            "status": "degraded",
            "error": str(error),
            "fallback_mode": "basic_observatory_integration"
        }


def main():
    """Main execution function."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Observatory Integration Module")
    parser.add_argument("--root", default=".", help="Repository root directory")
    parser.add_argument("--generate-makefile", help="Generate Observatory Makefile")
    parser.add_argument("--status", action="store_true", help="Check Observatory status")
    parser.add_argument("--verbose", action="store_true", help="Verbose logging")
    
    args = parser.parse_args()
    
    # Configure logging
    import logging
    level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(level=level, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    # Create integration module
    integration = ObservatoryIntegration(args.root)
    
    if args.status:
        status = integration.check_observatory_status()
        print(f"\n🔭 OBSERVATORY SYSTEM STATUS")
        print(f"Overall Status: {status['overall_status'].upper()}")
        print(f"Running Services: {status['running_services']}/{status['total_services']}")
        print("\nService Details:")
        
        for service_name, service_status in status["services"].items():
            status_icon = "✅" if service_status["running"] else "❌"
            health_icon = "🟢" if service_status["healthy"] else "🔴"
            print(f"  {status_icon} {service_name} (port {service_status['port']}) {health_icon}")
            
            if service_status["response_time"]:
                print(f"    Response time: {service_status['response_time']:.3f}s")
    
    if args.generate_makefile:
        output_path = integration.generate_observatory_makefile(Path(args.generate_makefile))
        print(f"\n🔭 Observatory Makefile generated: {output_path}")
        
        targets = integration.generate_observatory_targets()
        print(f"Generated {len(targets)} Observatory targets")
    
    if not args.status and not args.generate_makefile:
        # Default: show available targets
        targets = integration.generate_observatory_targets()
        print(f"\n🔭 OBSERVATORY INTEGRATION MODULE")
        print(f"Available targets: {len(targets)}")
        
        # Group by category
        by_category = {}
        for name, target in targets.items():
            category = target.get("category", "other")
            if category not in by_category:
                by_category[category] = []
            by_category[category].append(name)
        
        for category, target_names in by_category.items():
            print(f"\n{category.title()} targets ({len(target_names)}):")
            for name in sorted(target_names)[:5]:  # Show first 5
                print(f"  {name}")
            if len(target_names) > 5:
                print(f"  ... and {len(target_names) - 5} more")


if __name__ == "__main__":
    main()