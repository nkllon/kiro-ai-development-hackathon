#!/usr/bin/env python3
"""
Comprehensive Makefile System Discovery Engine
=============================================

Automated system discovery for comprehensive Makefile generation.
Scans project structure to identify available systems, scripts, and capabilities.

Author: Beast Mode Framework
Date: 2025-01-27
Purpose: Automated system discovery and capability mapping
"""

import os
import json
import re
import subprocess
import time
from pathlib import Path
from typing import Dict, List, Set, Any, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum

from src.rm_ddd.core.unified_reflective_module import ReflectiveModule


class SystemType(Enum):
    """System types for categorization."""
    OBSERVATORY = "observatory"
    BEAST_MODE = "beast_mode"
    DAG_ORCHESTRATION = "dag_orchestration"
    INFRASTRUCTURE = "infrastructure"
    DEVELOPMENT = "development"
    TESTING = "testing"
    GOVERNANCE = "governance"
    INTEGRATION = "integration"


@dataclass
class DiscoveredScript:
    """Represents a discovered script with metadata."""
    name: str
    path: Path
    system_type: SystemType
    capabilities: List[str] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)
    description: str = ""
    executable: bool = True
    priority: int = 1


@dataclass
class DiscoveredService:
    """Represents a discovered service."""
    name: str
    port: Optional[int] = None
    status: str = "unknown"
    health_endpoint: Optional[str] = None
    docker_container: bool = False
    process_id: Optional[int] = None


@dataclass
class SystemCapabilities:
    """System capabilities summary."""
    scripts: List[DiscoveredScript] = field(default_factory=list)
    services: List[DiscoveredService] = field(default_factory=list)
    directories: List[Path] = field(default_factory=list)
    makefile_targets: List[str] = field(default_factory=list)


class MakefileSystemDiscovery(ReflectiveModule):
    """
    🔍 COMPREHENSIVE MAKEFILE SYSTEM DISCOVERY ENGINE 🔍
    
    Automatically discovers and catalogs all system capabilities for
    comprehensive Makefile generation.
    """
    
    def __init__(self, repository_root: str = "."):
        super().__init__()
        self.module_id = "makefile_system_discovery"
        self.repository_root = Path(repository_root)
        
        # Discovery patterns
        self.script_patterns = {
            SystemType.OBSERVATORY: [
                r"observatory", r"monitor", r"health", r"metrics", r"dashboard"
            ],
            SystemType.BEAST_MODE: [
                r"beast", r"systematic", r"compliance", r"quality", r"validation"
            ],
            SystemType.DAG_ORCHESTRATION: [
                r"dag", r"orchestrat", r"workflow", r"task", r"schedule"
            ],
            SystemType.INFRASTRUCTURE: [
                r"deploy", r"infra", r"service", r"docker", r"tunnel", r"server"
            ],
            SystemType.DEVELOPMENT: [
                r"dev", r"build", r"test", r"lint", r"format", r"debug"
            ],
            SystemType.TESTING: [
                r"test", r"spec", r"validate", r"verify", r"check"
            ],
            SystemType.GOVERNANCE: [
                r"governance", r"orphan", r"scan", r"compliance", r"audit"
            ],
            SystemType.INTEGRATION: [
                r"integration", r"sync", r"connect", r"bridge", r"adapter"
            ]
        }
        
        # Capability keywords
        self.capability_keywords = {
            "start": ["start", "run", "launch", "boot", "init"],
            "stop": ["stop", "kill", "shutdown", "terminate", "halt"],
            "deploy": ["deploy", "install", "setup", "provision", "configure"],
            "status": ["status", "info", "state", "check", "ping"],
            "health": ["health", "alive", "ready", "heartbeat", "wellness"],
            "logs": ["logs", "log", "output", "trace", "debug"],
            "test": ["test", "spec", "verify", "validate", "check"],
            "clean": ["clean", "purge", "remove", "delete", "clear"],
            "backup": ["backup", "save", "export", "archive", "snapshot"],
            "restore": ["restore", "import", "recover", "load", "replay"]
        }
        
        # Results storage
        self.discovered_systems: Dict[SystemType, SystemCapabilities] = {}
        self.all_scripts: List[DiscoveredScript] = []
        self.all_services: List[DiscoveredService] = []
        
    def discover_all_systems(self) -> Dict[SystemType, SystemCapabilities]:
        """Discover all system capabilities."""
        self._logger.info("🔍 Starting comprehensive system discovery...")
        
        # Initialize system capabilities
        for system_type in SystemType:
            self.discovered_systems[system_type] = SystemCapabilities()
        
        # Discovery phases
        self._discover_scripts()
        self._discover_services()
        self._discover_directories()
        self._discover_existing_makefile_targets()
        
        # Categorize discoveries
        self._categorize_scripts()
        self._categorize_services()
        
        self._logger.info(f"✅ Discovery complete: {len(self.all_scripts)} scripts, {len(self.all_services)} services")
        return self.discovered_systems
    
    def _discover_scripts(self):
        """Discover all Python scripts in the project."""
        self._logger.info("📜 Discovering Python scripts...")
        
        script_directories = [
            self.repository_root / "scripts",
            self.repository_root / "src",
            self.repository_root
        ]
        
        for directory in script_directories:
            if not directory.exists():
                continue
                
            for script_path in directory.rglob("*.py"):
                if self._should_include_script(script_path):
                    script = self._analyze_script(script_path)
                    if script:
                        self.all_scripts.append(script)
    
    def _should_include_script(self, script_path: Path) -> bool:
        """Check if script should be included in discovery."""
        # Skip test files, __pycache__, and hidden files
        if any(part.startswith('.') or part == '__pycache__' for part in script_path.parts):
            return False
        if 'test_' in script_path.name or script_path.name.startswith('test'):
            return False
        if script_path.suffix != '.py':
            return False
        return True
    
    def _analyze_script(self, script_path: Path) -> Optional[DiscoveredScript]:
        """Analyze a script to extract metadata."""
        try:
            with open(script_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Extract basic info
            name = script_path.stem
            description = self._extract_description(content)
            capabilities = self._extract_capabilities(content)
            dependencies = self._extract_dependencies(content)
            executable = self._is_executable(script_path, content)
            
            return DiscoveredScript(
                name=name,
                path=script_path,
                system_type=SystemType.DEVELOPMENT,  # Will be categorized later
                capabilities=capabilities,
                dependencies=dependencies,
                description=description,
                executable=executable
            )
            
        except Exception as e:
            self._logger.warning(f"Failed to analyze script {script_path}: {e}")
            return None
    
    def _extract_description(self, content: str) -> str:
        """Extract description from script docstring."""
        # Look for module docstring
        docstring_match = re.search(r'"""(.*?)"""', content, re.DOTALL)
        if docstring_match:
            docstring = docstring_match.group(1).strip()
            # Get first line as description
            first_line = docstring.split('\n')[0].strip()
            return first_line
        return ""
    
    def _extract_capabilities(self, content: str) -> List[str]:
        """Extract capabilities from script content."""
        capabilities = []
        content_lower = content.lower()
        
        for capability, keywords in self.capability_keywords.items():
            if any(keyword in content_lower for keyword in keywords):
                capabilities.append(capability)
        
        return capabilities
    
    def _extract_dependencies(self, content: str) -> List[str]:
        """Extract dependencies from imports."""
        dependencies = []
        
        # Find import statements
        import_matches = re.findall(r'^(?:from|import)\s+([^\s]+)', content, re.MULTILINE)
        for match in import_matches:
            if not match.startswith('.') and not match in ['os', 'sys', 'json', 're', 'pathlib']:
                dependencies.append(match.split('.')[0])
        
        return list(set(dependencies))
    
    def _is_executable(self, script_path: Path, content: str) -> bool:
        """Check if script is executable."""
        # Check shebang
        if content.startswith('#!'):
            return True
        
        # Check if main function exists
        if 'if __name__ == "__main__"' in content:
            return True
        
        # Check file permissions
        try:
            return os.access(script_path, os.X_OK)
        except:
            return False
    
    def _discover_services(self):
        """Discover running services."""
        self._logger.info("🔧 Discovering running services...")
        
        # Check common ports
        common_ports = {
            8888: "observatory",
            9090: "prometheus", 
            3000: "grafana",
            6379: "redis",
            5432: "postgresql",
            3306: "mysql"
        }
        
        for port, service_name in common_ports.items():
            if self._is_port_open(port):
                service = DiscoveredService(
                    name=service_name,
                    port=port,
                    status="running",
                    health_endpoint=self._get_health_endpoint(service_name, port)
                )
                self.all_services.append(service)
        
        # Check Docker containers
        self._discover_docker_services()
    
    def _is_port_open(self, port: int) -> bool:
        """Check if port is open."""
        try:
            import socket
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.settimeout(1)
                result = sock.connect_ex(('localhost', port))
                return result == 0
        except:
            return False
    
    def _get_health_endpoint(self, service_name: str, port: int) -> Optional[str]:
        """Get health endpoint for service."""
        health_endpoints = {
            "observatory": "/health",
            "prometheus": "/metrics",
            "grafana": "/api/health"
        }
        return health_endpoints.get(service_name)
    
    def _discover_docker_services(self):
        """Discover Docker services."""
        try:
            result = subprocess.run(
                ["docker", "ps", "--format", "{{.Names}}\t{{.Ports}}\t{{.Status}}"],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode == 0:
                for line in result.stdout.strip().split('\n'):
                    if line:
                        parts = line.split('\t')
                        if len(parts) >= 3:
                            name = parts[0]
                            ports = parts[1]
                            status = parts[2]
                            
                            service = DiscoveredService(
                                name=name,
                                status="running" if "Up" in status else "stopped",
                                docker_container=True
                            )
                            
                            # Extract port if available
                            port_match = re.search(r':(\d+)->', ports)
                            if port_match:
                                service.port = int(port_match.group(1))
                            
                            self.all_services.append(service)
                            
        except Exception as e:
            self._logger.debug(f"Docker discovery failed: {e}")
    
    def _discover_directories(self):
        """Discover important directories."""
        important_dirs = [
            "src", "scripts", "docs", "tests", "makefiles", 
            ".kiro", "reports", "logs", "data", "config"
        ]
        
        for system_type in SystemType:
            capabilities = self.discovered_systems[system_type]
            
            for dir_name in important_dirs:
                dir_path = self.repository_root / dir_name
                if dir_path.exists() and dir_path.is_dir():
                    capabilities.directories.append(dir_path)
    
    def _discover_existing_makefile_targets(self):
        """Discover existing Makefile targets."""
        makefile_paths = [
            self.repository_root / "Makefile",
            self.repository_root / "makefiles" / "governance.mk",
            self.repository_root / "makefiles" / "testing.mk"
        ]
        
        all_targets = []
        
        for makefile_path in makefile_paths:
            if makefile_path.exists():
                targets = self._extract_makefile_targets(makefile_path)
                all_targets.extend(targets)
        
        # Distribute targets to appropriate systems
        for target in all_targets:
            system_type = self._categorize_target(target)
            self.discovered_systems[system_type].makefile_targets.append(target)
    
    def _extract_makefile_targets(self, makefile_path: Path) -> List[str]:
        """Extract targets from Makefile."""
        targets = []
        
        try:
            with open(makefile_path, 'r') as f:
                content = f.read()
            
            # Find target definitions
            target_matches = re.findall(r'^([a-zA-Z][a-zA-Z0-9_-]*):(?:[^=]|$)', content, re.MULTILINE)
            targets.extend(target_matches)
            
        except Exception as e:
            self._logger.warning(f"Failed to parse {makefile_path}: {e}")
        
        return targets
    
    def _categorize_target(self, target: str) -> SystemType:
        """Categorize a Makefile target."""
        target_lower = target.lower()
        
        for system_type, patterns in self.script_patterns.items():
            if any(re.search(pattern, target_lower) for pattern in patterns):
                return system_type
        
        return SystemType.DEVELOPMENT
    
    def _categorize_scripts(self):
        """Categorize discovered scripts by system type."""
        for script in self.all_scripts:
            script.system_type = self._categorize_script(script)
            self.discovered_systems[script.system_type].scripts.append(script)
    
    def _categorize_script(self, script: DiscoveredScript) -> SystemType:
        """Categorize a script by system type."""
        script_name_lower = script.name.lower()
        script_path_lower = str(script.path).lower()
        
        # Check path-based categorization first
        if 'observatory' in script_path_lower:
            return SystemType.OBSERVATORY
        if 'beast_mode' in script_path_lower:
            return SystemType.BEAST_MODE
        if 'dag' in script_path_lower:
            return SystemType.DAG_ORCHESTRATION
        if 'infrastructure' in script_path_lower:
            return SystemType.INFRASTRUCTURE
        if 'governance' in script_path_lower:
            return SystemType.GOVERNANCE
        
        # Check name-based categorization
        for system_type, patterns in self.script_patterns.items():
            if any(re.search(pattern, script_name_lower) for pattern in patterns):
                return system_type
        
        return SystemType.DEVELOPMENT
    
    def _categorize_services(self):
        """Categorize discovered services by system type."""
        for service in self.all_services:
            system_type = self._categorize_service(service)
            self.discovered_systems[system_type].services.append(service)
    
    def _categorize_service(self, service: DiscoveredService) -> SystemType:
        """Categorize a service by system type."""
        service_name_lower = service.name.lower()
        
        if 'observatory' in service_name_lower or service.port == 8888:
            return SystemType.OBSERVATORY
        if 'prometheus' in service_name_lower or service.port == 9090:
            return SystemType.OBSERVATORY
        if 'grafana' in service_name_lower or service.port == 3000:
            return SystemType.OBSERVATORY
        if 'redis' in service_name_lower or service.port == 6379:
            return SystemType.INFRASTRUCTURE
        
        return SystemType.INFRASTRUCTURE
    
    def generate_discovery_report(self) -> Dict[str, Any]:
        """Generate comprehensive discovery report."""
        report = {
            "discovery_timestamp": time.strftime('%Y-%m-%d %H:%M:%S'),
            "repository_root": str(self.repository_root),
            "summary": {
                "total_scripts": len(self.all_scripts),
                "total_services": len(self.all_services),
                "systems_discovered": len([s for s in self.discovered_systems.values() if s.scripts or s.services])
            },
            "systems": {}
        }
        
        for system_type, capabilities in self.discovered_systems.items():
            if capabilities.scripts or capabilities.services or capabilities.makefile_targets:
                report["systems"][system_type.value] = {
                    "scripts": [
                        {
                            "name": script.name,
                            "path": str(script.path),
                            "capabilities": script.capabilities,
                            "executable": script.executable,
                            "description": script.description
                        }
                        for script in capabilities.scripts
                    ],
                    "services": [
                        {
                            "name": service.name,
                            "port": service.port,
                            "status": service.status,
                            "docker": service.docker_container
                        }
                        for service in capabilities.services
                    ],
                    "existing_targets": capabilities.makefile_targets,
                    "directories": [str(d) for d in capabilities.directories]
                }
        
        return report
    
    def save_discovery_report(self, output_path: Optional[Path] = None) -> Path:
        """Save discovery report to file."""
        if output_path is None:
            output_path = self.repository_root / "reports" / "makefile_system_discovery.json"
        
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        report = self.generate_discovery_report()
        
        with open(output_path, 'w') as f:
            json.dump(report, f, indent=2)
        
        self._logger.info(f"📊 Discovery report saved: {output_path}")
        return output_path
    
    def get_capabilities(self) -> List[str]:
        """Get module capabilities."""
        return ["system_discovery", "script_analysis", "service_detection"]
    
    def get_module_info(self) -> Dict[str, Any]:
        """Get module information."""
        return {
            "module_id": self.module_id,
            "name": "Makefile System Discovery",
            "version": "1.0.0",
            "description": "Automated system discovery for comprehensive Makefile generation"
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
            "fallback_mode": "basic_discovery"
        }


def main():
    """Main execution function."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Makefile System Discovery Engine")
    parser.add_argument("--root", default=".", help="Repository root directory")
    parser.add_argument("--output", help="Output file for discovery report")
    parser.add_argument("--verbose", action="store_true", help="Verbose logging")
    
    args = parser.parse_args()
    
    # Configure logging
    import logging
    level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(level=level, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    # Run discovery
    discovery = MakefileSystemDiscovery(args.root)
    systems = discovery.discover_all_systems()
    
    # Save report
    output_path = Path(args.output) if args.output else None
    report_path = discovery.save_discovery_report(output_path)
    
    # Print summary
    print(f"\n🔍 MAKEFILE SYSTEM DISCOVERY COMPLETE")
    print(f"📊 Report saved: {report_path}")
    print(f"📜 Scripts discovered: {len(discovery.all_scripts)}")
    print(f"🔧 Services discovered: {len(discovery.all_services)}")
    print(f"🏗️ Systems identified: {len([s for s in systems.values() if s.scripts or s.services])}")


if __name__ == "__main__":
    main()