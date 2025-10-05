#!/usr/bin/env python3
"""
Infrastructure Integration Module
=================================

Integration module for Infrastructure management with Makefile governance.
Provides infrastructure deployment, monitoring, and management capabilities.

Author: Beast Mode Framework
Date: 2025-01-27
Purpose: Infrastructure management integration for Makefile governance
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


class InfrastructureComponent(Enum):
    """Infrastructure component types."""
    DOCKER = "docker"
    KUBERNETES = "kubernetes"
    NETWORKING = "networking"
    STORAGE = "storage"
    MONITORING = "monitoring"
    SECURITY = "security"
    BACKUP = "backup"
    DEPLOYMENT = "deployment"


@dataclass
class InfrastructureConfig:
    """Infrastructure component configuration."""
    name: str
    component_type: InfrastructureComponent
    config_file: Optional[str] = None
    deploy_script: Optional[str] = None
    health_check: Optional[str] = None
    dependencies: List[str] = field(default_factory=list)
    ports: List[int] = field(default_factory=list)
    volumes: List[str] = field(default_factory=list)


class InfrastructureIntegration(ReflectiveModule):
    """
    🏗️ INFRASTRUCTURE INTEGRATION MODULE 🏗️
    
    Integration module for Infrastructure management with Makefile governance.
    Provides systematic infrastructure operations and monitoring.
    """
    
    def __init__(self, repository_root: str = "."):
        super().__init__()
        self.module_id = "infrastructure_integration"
        self.repository_root = Path(repository_root)
        
        # Infrastructure paths
        self.infra_dir = self.repository_root / "infrastructure"
        self.docker_dir = self.repository_root / "docker"
        self.k8s_dir = self.repository_root / "k8s"
        self.scripts_dir = self.repository_root / "scripts"
        self.config_dir = self.repository_root / "config"
        
        # Infrastructure configurations
        self.components = self._initialize_infrastructure_configs()
    
    def _initialize_infrastructure_configs(self) -> Dict[str, InfrastructureConfig]:
        """Initialize infrastructure component configurations."""
        return {
            "redis": InfrastructureConfig(
                name="redis",
                component_type=InfrastructureComponent.STORAGE,
                config_file="redis.conf",
                deploy_script="deploy_redis.py",
                health_check="redis-cli ping",
                ports=[6379]
            ),
            "postgresql": InfrastructureConfig(
                name="postgresql",
                component_type=InfrastructureComponent.STORAGE,
                config_file="postgresql.conf",
                deploy_script="deploy_postgresql.py",
                health_check="pg_isready",
                ports=[5432]
            ),
            "nginx": InfrastructureConfig(
                name="nginx",
                component_type=InfrastructureComponent.NETWORKING,
                config_file="nginx.conf",
                deploy_script="deploy_nginx.py",
                health_check="curl -f http://localhost/health",
                ports=[80, 443]
            ),
            "prometheus": InfrastructureConfig(
                name="prometheus",
                component_type=InfrastructureComponent.MONITORING,
                config_file="prometheus.yml",
                deploy_script="deploy_prometheus.py",
                health_check="curl -f http://localhost:9090/-/healthy",
                ports=[9090]
            ),
            "grafana": InfrastructureConfig(
                name="grafana",
                component_type=InfrastructureComponent.MONITORING,
                config_file="grafana.ini",
                deploy_script="deploy_grafana.py",
                health_check="curl -f http://localhost:3000/api/health",
                ports=[3000],
                dependencies=["prometheus"]
            ),
            "docker_registry": InfrastructureConfig(
                name="docker_registry",
                component_type=InfrastructureComponent.DEPLOYMENT,
                config_file="registry.yml",
                deploy_script="deploy_docker_registry.py",
                health_check="curl -f http://localhost:5000/v2/",
                ports=[5000]
            ),
            "backup_system": InfrastructureConfig(
                name="backup_system",
                component_type=InfrastructureComponent.BACKUP,
                config_file="backup.conf",
                deploy_script="setup_backup_system.py",
                health_check="python scripts/check_backup_status.py"
            ),
            "security_scanner": InfrastructureConfig(
                name="security_scanner",
                component_type=InfrastructureComponent.SECURITY,
                config_file="security.yml",
                deploy_script="deploy_security_scanner.py",
                health_check="python scripts/check_security_status.py"
            )
        }
    
    def generate_infrastructure_targets(self) -> Dict[str, Dict[str, Any]]:
        """Generate Infrastructure-specific Makefile targets."""
        targets = {}
        
        # Component-specific targets
        for component_name, config in self.components.items():
            component_targets = self._generate_component_targets(component_name, config)
            targets.update(component_targets)
        
        # System-level targets
        system_targets = self._generate_system_targets()
        targets.update(system_targets)
        
        # Docker-specific targets
        docker_targets = self._generate_docker_targets()
        targets.update(docker_targets)
        
        # Kubernetes targets
        k8s_targets = self._generate_kubernetes_targets()
        targets.update(k8s_targets)
        
        # Monitoring and maintenance targets
        monitoring_targets = self._generate_monitoring_targets()
        targets.update(monitoring_targets)
        
        return targets
    
    def _generate_component_targets(self, component_name: str, 
                                  config: InfrastructureConfig) -> Dict[str, Dict[str, Any]]:
        """Generate targets for a specific infrastructure component."""
        targets = {}
        
        # Deploy component target
        targets[f"infra-{component_name}-deploy"] = {
            "description": f"Deploy {component_name} infrastructure",
            "commands": self._get_deploy_commands(config),
            "phony": True,
            "category": "infrastructure"
        }
        
        # Start component target
        targets[f"infra-{component_name}-start"] = {
            "description": f"Start {component_name} service",
            "commands": self._get_start_commands(config),
            "phony": True,
            "category": "infrastructure"
        }
        
        # Stop component target
        targets[f"infra-{component_name}-stop"] = {
            "description": f"Stop {component_name} service",
            "commands": self._get_stop_commands(config),
            "phony": True,
            "category": "infrastructure"
        }
        
        # Status check target
        targets[f"infra-{component_name}-status"] = {
            "description": f"Check {component_name} status",
            "commands": self._get_status_commands(config),
            "phony": True,
            "category": "infrastructure"
        }
        
        # Health check target
        targets[f"infra-{component_name}-health"] = {
            "description": f"Check {component_name} health",
            "commands": self._get_health_commands(config),
            "phony": True,
            "category": "infrastructure"
        }
        
        # Backup component target
        if config.component_type in [InfrastructureComponent.STORAGE, InfrastructureComponent.MONITORING]:
            targets[f"infra-{component_name}-backup"] = {
                "description": f"Backup {component_name} data",
                "commands": [
                    f"@echo '🏗️ Backing up {component_name}...'",
                    f"python scripts/backup_{component_name}.py",
                    f"@echo '✅ {component_name} backup complete'"
                ],
                "phony": True,
                "category": "infrastructure"
            }
        
        return targets
    
    def _generate_system_targets(self) -> Dict[str, Dict[str, Any]]:
        """Generate system-level infrastructure targets."""
        return {
            "infra-deploy-all": {
                "description": "Deploy all infrastructure components",
                "commands": [
                    "@echo '🏗️ Deploying all infrastructure components...'",
                    "$(MAKE) infra-redis-deploy",
                    "$(MAKE) infra-postgresql-deploy",
                    "$(MAKE) infra-prometheus-deploy",
                    "$(MAKE) infra-grafana-deploy",
                    "$(MAKE) infra-nginx-deploy",
                    "$(MAKE) infra-docker-registry-deploy",
                    "$(MAKE) infra-backup-system-deploy",
                    "$(MAKE) infra-security-scanner-deploy",
                    "@echo '✅ All infrastructure components deployed'"
                ],
                "phony": True,
                "category": "infrastructure"
            },
            "infra-start-all": {
                "description": "Start all infrastructure services",
                "commands": [
                    "@echo '🏗️ Starting all infrastructure services...'",
                    "$(MAKE) infra-redis-start",
                    "$(MAKE) infra-postgresql-start",
                    "$(MAKE) infra-prometheus-start",
                    "$(MAKE) infra-grafana-start",
                    "$(MAKE) infra-nginx-start",
                    "@echo '✅ All infrastructure services started'"
                ],
                "phony": True,
                "category": "infrastructure"
            },
            "infra-stop-all": {
                "description": "Stop all infrastructure services",
                "commands": [
                    "@echo '🏗️ Stopping all infrastructure services...'",
                    "$(MAKE) infra-nginx-stop",
                    "$(MAKE) infra-grafana-stop",
                    "$(MAKE) infra-prometheus-stop",
                    "$(MAKE) infra-postgresql-stop",
                    "$(MAKE) infra-redis-stop",
                    "@echo '✅ All infrastructure services stopped'"
                ],
                "phony": True,
                "category": "infrastructure"
            },
            "infra-status-all": {
                "description": "Check status of all infrastructure components",
                "commands": [
                    "@echo '🏗️ Infrastructure Status Report:'",
                    "@echo '================================='",
                    "$(MAKE) infra-redis-status",
                    "$(MAKE) infra-postgresql-status",
                    "$(MAKE) infra-prometheus-status",
                    "$(MAKE) infra-grafana-status",
                    "$(MAKE) infra-nginx-status",
                    "$(MAKE) infra-docker-registry-status",
                    "$(MAKE) infra-backup-system-status",
                    "$(MAKE) infra-security-scanner-status"
                ],
                "phony": True,
                "category": "infrastructure"
            },
            "infra-health-all": {
                "description": "Check health of all infrastructure components",
                "commands": [
                    "@echo '🏗️ Infrastructure Health Check:'",
                    "@echo '==============================='",
                    "$(MAKE) infra-redis-health",
                    "$(MAKE) infra-postgresql-health",
                    "$(MAKE) infra-prometheus-health",
                    "$(MAKE) infra-grafana-health",
                    "$(MAKE) infra-nginx-health"
                ],
                "phony": True,
                "category": "infrastructure"
            },
            "infra-validate": {
                "description": "Validate infrastructure configuration",
                "commands": [
                    "@echo '🏗️ Validating infrastructure configuration...'",
                    "python scripts/validate_infrastructure_config.py",
                    "python scripts/check_infrastructure_dependencies.py",
                    "python scripts/validate_network_configuration.py",
                    "@echo '✅ Infrastructure validation complete'"
                ],
                "phony": True,
                "category": "infrastructure"
            }
        }
    
    def _generate_docker_targets(self) -> Dict[str, Dict[str, Any]]:
        """Generate Docker-specific targets."""
        return {
            "infra-docker-build": {
                "description": "Build all Docker images",
                "commands": [
                    "@echo '🐳 Building Docker images...'",
                    "docker-compose build",
                    "@echo '✅ Docker images built'"
                ],
                "phony": True,
                "category": "infrastructure"
            },
            "infra-docker-up": {
                "description": "Start Docker infrastructure",
                "commands": [
                    "@echo '🐳 Starting Docker infrastructure...'",
                    "docker-compose up -d",
                    "@echo '✅ Docker infrastructure started'"
                ],
                "phony": True,
                "category": "infrastructure"
            },
            "infra-docker-down": {
                "description": "Stop Docker infrastructure",
                "commands": [
                    "@echo '🐳 Stopping Docker infrastructure...'",
                    "docker-compose down",
                    "@echo '✅ Docker infrastructure stopped'"
                ],
                "phony": True,
                "category": "infrastructure"
            },
            "infra-docker-logs": {
                "description": "View Docker infrastructure logs",
                "commands": [
                    "@echo '🐳 Docker Infrastructure Logs:'",
                    "@echo '=============================='",
                    "docker-compose logs --tail=50"
                ],
                "phony": True,
                "category": "infrastructure"
            },
            "infra-docker-clean": {
                "description": "Clean Docker infrastructure",
                "commands": [
                    "@echo '🐳 Cleaning Docker infrastructure...'",
                    "docker-compose down -v --remove-orphans",
                    "docker system prune -f",
                    "@echo '✅ Docker infrastructure cleaned'"
                ],
                "phony": True,
                "category": "infrastructure"
            }
        }
    
    def _generate_kubernetes_targets(self) -> Dict[str, Dict[str, Any]]:
        """Generate Kubernetes-specific targets."""
        return {
            "infra-k8s-deploy": {
                "description": "Deploy to Kubernetes",
                "commands": [
                    "@echo '☸️ Deploying to Kubernetes...'",
                    "kubectl apply -f k8s/",
                    "@echo '✅ Kubernetes deployment complete'"
                ],
                "phony": True,
                "category": "infrastructure"
            },
            "infra-k8s-status": {
                "description": "Check Kubernetes deployment status",
                "commands": [
                    "@echo '☸️ Kubernetes Status:'",
                    "@echo '===================='",
                    "kubectl get pods",
                    "kubectl get services",
                    "kubectl get deployments"
                ],
                "phony": True,
                "category": "infrastructure"
            },
            "infra-k8s-logs": {
                "description": "View Kubernetes logs",
                "commands": [
                    "@echo '☸️ Kubernetes Logs:'",
                    "@echo '==================='",
                    "kubectl logs -l app=infrastructure --tail=50"
                ],
                "phony": True,
                "category": "infrastructure"
            },
            "infra-k8s-delete": {
                "description": "Delete Kubernetes deployment",
                "commands": [
                    "@echo '☸️ Deleting Kubernetes deployment...'",
                    "kubectl delete -f k8s/",
                    "@echo '✅ Kubernetes deployment deleted'"
                ],
                "phony": True,
                "category": "infrastructure"
            }
        }
    
    def _generate_monitoring_targets(self) -> Dict[str, Dict[str, Any]]:
        """Generate monitoring and maintenance targets."""
        return {
            "infra-monitor": {
                "description": "Start infrastructure monitoring",
                "commands": [
                    "@echo '🏗️ Starting infrastructure monitoring...'",
                    "python scripts/start_infrastructure_monitoring.py",
                    "@echo '✅ Infrastructure monitoring started'"
                ],
                "phony": True,
                "category": "infrastructure"
            },
            "infra-metrics": {
                "description": "Display infrastructure metrics",
                "commands": [
                    "@echo '🏗️ Infrastructure Metrics:'",
                    "@echo '=========================='",
                    "python scripts/display_infrastructure_metrics.py",
                    "curl -s http://localhost:9090/api/v1/query?query=up | jq '.' || echo 'Prometheus not available'"
                ],
                "phony": True,
                "category": "infrastructure"
            },
            "infra-backup-all": {
                "description": "Backup all infrastructure data",
                "commands": [
                    "@echo '🏗️ Backing up all infrastructure data...'",
                    "$(MAKE) infra-redis-backup",
                    "$(MAKE) infra-postgresql-backup",
                    "$(MAKE) infra-prometheus-backup",
                    "python scripts/backup_infrastructure_configs.py",
                    "@echo '✅ All infrastructure backups complete'"
                ],
                "phony": True,
                "category": "infrastructure"
            },
            "infra-restore": {
                "description": "Restore infrastructure from backup",
                "commands": [
                    "@echo '🏗️ Restoring infrastructure from backup...'",
                    "python scripts/restore_infrastructure.py",
                    "@echo '✅ Infrastructure restore complete'"
                ],
                "phony": True,
                "category": "infrastructure"
            },
            "infra-security-scan": {
                "description": "Run infrastructure security scan",
                "commands": [
                    "@echo '🏗️ Running infrastructure security scan...'",
                    "python scripts/security_scan_infrastructure.py",
                    "docker run --rm -v /var/run/docker.sock:/var/run/docker.sock aquasec/trivy image --severity HIGH,CRITICAL",
                    "@echo '✅ Security scan complete'"
                ],
                "phony": True,
                "category": "infrastructure"
            },
            "infra-update": {
                "description": "Update infrastructure components",
                "commands": [
                    "@echo '🏗️ Updating infrastructure components...'",
                    "python scripts/update_infrastructure.py",
                    "docker-compose pull",
                    "@echo '✅ Infrastructure update complete'"
                ],
                "phony": True,
                "category": "infrastructure"
            }
        }
    
    def _get_deploy_commands(self, config: InfrastructureConfig) -> List[str]:
        """Get deployment commands for a component."""
        commands = [f"@echo '🏗️ Deploying {config.name}...'"]
        
        if config.deploy_script:
            script_path = self.scripts_dir / config.deploy_script
            if script_path.exists():
                commands.append(f"python {script_path}")
            else:
                commands.append(f"@echo 'Deploy script not found: {script_path}'")
        else:
            commands.append(f"@echo 'No deploy script configured for {config.name}'")
        
        commands.append(f"@echo '✅ {config.name} deployment complete'")
        return commands
    
    def _get_start_commands(self, config: InfrastructureConfig) -> List[str]:
        """Get start commands for a component."""
        commands = [f"@echo '🏗️ Starting {config.name}...'"]
        
        if config.component_type == InfrastructureComponent.DOCKER:
            commands.append(f"docker start {config.name} || docker run -d --name {config.name} {config.name}")
        else:
            commands.append(f"systemctl start {config.name} || echo 'Service start attempted'")
        
        return commands
    
    def _get_stop_commands(self, config: InfrastructureConfig) -> List[str]:
        """Get stop commands for a component."""
        commands = [f"@echo '🏗️ Stopping {config.name}...'"]
        
        if config.component_type == InfrastructureComponent.DOCKER:
            commands.append(f"docker stop {config.name} || echo 'Container not running'")
        else:
            commands.append(f"systemctl stop {config.name} || echo 'Service stop attempted'")
        
        return commands
    
    def _get_status_commands(self, config: InfrastructureConfig) -> List[str]:
        """Get status check commands for a component."""
        commands = [f"@echo 'Checking {config.name} status...'"]
        
        if config.ports:
            for port in config.ports:
                commands.append(f"@lsof -i:{port} >/dev/null 2>&1 && echo '✅ {config.name} is running on port {port}' || echo '❌ {config.name} is not running on port {port}'")
        else:
            commands.append(f"@echo 'No port configuration for {config.name}'")
        
        return commands
    
    def _get_health_commands(self, config: InfrastructureConfig) -> List[str]:
        """Get health check commands for a component."""
        commands = [f"@echo 'Checking {config.name} health...'"]
        
        if config.health_check:
            commands.append(f"@{config.health_check} >/dev/null 2>&1 && echo '✅ {config.name} is healthy' || echo '❌ {config.name} health check failed'")
        else:
            commands.append(f"@echo 'No health check configured for {config.name}'")
        
        return commands
    
    def check_infrastructure_status(self) -> Dict[str, Any]:
        """Check the status of all infrastructure components."""
        status = {
            "timestamp": time.strftime('%Y-%m-%d %H:%M:%S'),
            "components": {},
            "overall_status": "unknown"
        }
        
        healthy_components = 0
        total_components = len(self.components)
        
        for component_name, config in self.components.items():
            component_status = self._check_component_status(config)
            status["components"][component_name] = component_status
            
            if component_status["healthy"]:
                healthy_components += 1
        
        # Determine overall status
        if healthy_components == total_components:
            status["overall_status"] = "healthy"
        elif healthy_components > total_components * 0.7:
            status["overall_status"] = "mostly_healthy"
        elif healthy_components > 0:
            status["overall_status"] = "partial"
        else:
            status["overall_status"] = "down"
        
        status["healthy_components"] = healthy_components
        status["total_components"] = total_components
        
        return status
    
    def _check_component_status(self, config: InfrastructureConfig) -> Dict[str, Any]:
        """Check the status of a specific infrastructure component."""
        status = {
            "name": config.name,
            "type": config.component_type.value,
            "running": False,
            "healthy": False,
            "ports_open": []
        }
        
        try:
            # Check if ports are open
            for port in config.ports:
                try:
                    import socket
                    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                        sock.settimeout(2)
                        result = sock.connect_ex(('localhost', port))
                        if result == 0:
                            status["ports_open"].append(port)
                except:
                    pass
            
            status["running"] = len(status["ports_open"]) > 0
            
            # If running, check health
            if status["running"] and config.health_check:
                try:
                    result = subprocess.run(
                        config.health_check,
                        shell=True,
                        capture_output=True,
                        timeout=5
                    )
                    status["healthy"] = result.returncode == 0
                except:
                    status["healthy"] = False
            else:
                status["healthy"] = status["running"]
        
        except Exception:
            pass
        
        return status
    
    def generate_infrastructure_makefile(self, output_path: Optional[Path] = None) -> Path:
        """Generate Infrastructure-specific Makefile."""
        if output_path is None:
            output_path = self.repository_root / "makefiles" / "infrastructure.mk"
        
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        targets = self.generate_infrastructure_targets()
        
        content_lines = [
            "# Infrastructure Management Makefile",
            "# Generated by Infrastructure Integration Module",
            f"# Generated on: {self._get_current_timestamp()}",
            "",
            "# Infrastructure deployment, monitoring, and management targets",
            "",
            "# Phony targets"
        ]
        
        # Collect phony targets
        phony_targets = [name for name, target in targets.items() if target.get("phony", False)]
        content_lines.append(f".PHONY: {' '.join(sorted(phony_targets))}")
        content_lines.append("")
        
        # Generate targets grouped by type
        target_groups = {
            "System Operations": [name for name in targets if any(x in name for x in ["deploy-all", "start-all", "stop-all", "status-all", "health-all", "validate"])],
            "Component Management": [name for name in targets if any(comp in name for comp in self.components.keys())],
            "Docker Operations": [name for name in targets if "docker" in name],
            "Kubernetes Operations": [name for name in targets if "k8s" in name],
            "Monitoring & Maintenance": [name for name in targets if any(x in name for x in ["monitor", "metrics", "backup", "restore", "security", "update"])]
        }
        
        for group_name, target_names in target_groups.items():
            if target_names:
                content_lines.extend([
                    f"# {group_name}",
                    "# " + "=" * len(group_name),
                    ""
                ])
                
                for target_name in sorted(target_names):
                    if target_name in targets:
                        target_config = targets[target_name]
                        
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
        
        self._logger.info(f"🏗️ Infrastructure Makefile generated: {output_path}")
        return output_path
    
    def get_capabilities(self) -> List[str]:
        """Get module capabilities."""
        return ["infrastructure_integration", "deployment_management", "monitoring"]
    
    def get_module_info(self) -> Dict[str, Any]:
        """Get module information."""
        return {
            "module_id": self.module_id,
            "name": "Infrastructure Integration",
            "version": "1.0.0",
            "description": "Integration module for Infrastructure management with Makefile governance"
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
            "fallback_mode": "basic_infrastructure_integration"
        }


def main():
    """Main execution function."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Infrastructure Integration Module")
    parser.add_argument("--root", default=".", help="Repository root directory")
    parser.add_argument("--generate-makefile", help="Generate Infrastructure Makefile")
    parser.add_argument("--status", action="store_true", help="Check Infrastructure status")
    parser.add_argument("--verbose", action="store_true", help="Verbose logging")
    
    args = parser.parse_args()
    
    # Configure logging
    import logging
    level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(level=level, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    # Create integration module
    integration = InfrastructureIntegration(args.root)
    
    if args.status:
        status = integration.check_infrastructure_status()
        print(f"\n🏗️ INFRASTRUCTURE STATUS")
        print(f"Overall Status: {status['overall_status'].upper()}")
        print(f"Healthy Components: {status['healthy_components']}/{status['total_components']}")
        print("\nComponent Details:")
        
        for component_name, component_status in status["components"].items():
            status_icon = "✅" if component_status["healthy"] else "❌"
            running_icon = "🟢" if component_status["running"] else "🔴"
            print(f"  {status_icon} {component_name} ({component_status['type']}) {running_icon}")
            
            if component_status["ports_open"]:
                print(f"    Ports: {', '.join(map(str, component_status['ports_open']))}")
    
    if args.generate_makefile:
        output_path = integration.generate_infrastructure_makefile(Path(args.generate_makefile))
        print(f"\n🏗️ Infrastructure Makefile generated: {output_path}")
        
        targets = integration.generate_infrastructure_targets()
        print(f"Generated {len(targets)} Infrastructure targets")
    
    if not args.status and not args.generate_makefile:
        # Default: show available targets
        targets = integration.generate_infrastructure_targets()
        print(f"\n🏗️ INFRASTRUCTURE INTEGRATION MODULE")
        print(f"Available targets: {len(targets)}")
        
        # Group by component type
        by_type = {}
        for name, target in targets.items():
            if "docker" in name:
                target_type = "Docker"
            elif "k8s" in name:
                target_type = "Kubernetes"
            elif "backup" in name or "restore" in name:
                target_type = "Backup & Recovery"
            elif "monitor" in name or "metrics" in name:
                target_type = "Monitoring"
            else:
                target_type = "General"
            
            if target_type not in by_type:
                by_type[target_type] = []
            by_type[target_type].append(name)
        
        for target_type, target_names in by_type.items():
            print(f"\n{target_type} targets ({len(target_names)}):")
            for name in sorted(target_names)[:5]:  # Show first 5
                print(f"  {name}")
            if len(target_names) > 5:
                print(f"  ... and {len(target_names) - 5} more")


if __name__ == "__main__":
    main()