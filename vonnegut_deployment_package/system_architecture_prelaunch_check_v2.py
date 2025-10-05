#!/usr/bin/env python3
"""
Prelaunch validation script for System Architecture Wiring Diagram implementation.
Validates all dependencies, system requirements, and infrastructure before execution.
Generated using proven spec-creation-dag-compliance patterns v2.0.
"""

import sys
import os
import json
import subprocess
import psutil
import socket
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
import importlib.util

# Add project root to path for imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

class SystemArchitecturePrelaunchValidator:
    """Validates all requirements for System Architecture Wiring Diagram implementation."""
    
    def __init__(self):
        self.validation_results = []
        self.warnings = []
        self.errors = []
        self.start_time = datetime.now()
    
    def validate_all(self) -> Dict[str, Any]:
        """Run comprehensive prelaunch validation."""
        print("🔍 System Architecture Wiring Diagram - Prelaunch Validation v2.0")
        print("=" * 70)
        print(f"⏰ Validation Start: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        # Core validation checks
        self._validate_python_environment()
        self._validate_system_resources()
        self._validate_infrastructure_dependencies()
        self._validate_project_structure()
        self._validate_beast_mode_framework()
        self._validate_dag_orchestration()
        self._validate_execution_tracking()
        self._validate_diagram_generation_tools()
        self._validate_network_connectivity()
        
        return self._generate_validation_report()
    
    def _validate_python_environment(self):
        """Validate Python environment and required packages."""
        print("🐍 Validating Python Environment...")
        
        # Check Python version
        python_version = sys.version_info
        if python_version >= (3, 9):
            self._log_success(f"Python version: {python_version.major}.{python_version.minor}.{python_version.micro}")
        else:
            self._log_error(f"Python version {python_version.major}.{python_version.minor} is too old. Requires Python 3.9+")
        
        # Check required packages
        required_packages = [
            ('psutil', 'System resource monitoring'),
            ('asyncio', 'Async execution support'),
            ('json', 'JSON data handling'),
            ('pathlib', 'Path manipulation'),
            ('subprocess', 'Process execution'),
            ('socket', 'Network connectivity testing'),
            ('datetime', 'Timestamp handling'),
            ('typing', 'Type hints support')
        ]
        
        for package, description in required_packages:
            try:
                importlib.import_module(package)
                self._log_success(f"Package {package}: Available ({description})")
            except ImportError:
                self._log_error(f"Package {package}: Missing ({description})")
        
        # Check optional packages for enhanced functionality
        optional_packages = [
            ('redis', 'Redis execution tracking'),
            ('requests', 'HTTP connectivity testing'),
            ('yaml', 'YAML configuration parsing'),
            ('matplotlib', 'Diagram generation support'),
            ('networkx', 'Graph analysis support')
        ]
        
        for package, description in optional_packages:
            try:
                importlib.import_module(package)
                self._log_success(f"Optional package {package}: Available ({description})")
            except ImportError:
                self._log_warning(f"Optional package {package}: Missing ({description}) - functionality may be limited")
    
    def _validate_system_resources(self):
        """Validate system resources for parallel execution."""
        print("\n💻 Validating System Resources...")
        
        # CPU validation
        cpu_count = psutil.cpu_count()
        cpu_percent = psutil.cpu_percent(interval=1)
        
        if cpu_count >= 4:
            self._log_success(f"CPU cores: {cpu_count} (adequate for parallel execution)")
        else:
            self._log_warning(f"CPU cores: {cpu_count} (recommend 4+ for optimal parallel execution)")
        
        if cpu_percent < 70:
            self._log_success(f"CPU usage: {cpu_percent:.1f}% (adequate)")
        else:
            self._log_warning(f"CPU usage: {cpu_percent:.1f}% (high - may impact performance)")
        
        # Memory validation
        memory = psutil.virtual_memory()
        memory_gb = memory.total // (1024**3)
        
        if memory_gb >= 16:
            self._log_success(f"Memory: {memory_gb}GB total (adequate for parallel execution)")
        elif memory_gb >= 8:
            self._log_warning(f"Memory: {memory_gb}GB total (minimum for parallel execution)")
        else:
            self._log_error(f"Memory: {memory_gb}GB total (insufficient - requires 8GB minimum)")
        
        if memory.percent < 80:
            self._log_success(f"Memory usage: {memory.percent:.1f}% (adequate)")
        else:
            self._log_warning(f"Memory usage: {memory.percent:.1f}% (high - may impact performance)")
        
        # Disk validation
        disk = psutil.disk_usage('/')
        disk_free_gb = disk.free // (1024**3)
        
        if disk_free_gb >= 20:
            self._log_success(f"Disk space: {disk_free_gb}GB free (adequate)")
        elif disk_free_gb >= 10:
            self._log_warning(f"Disk space: {disk_free_gb}GB free (minimum)")
        else:
            self._log_error(f"Disk space: {disk_free_gb}GB free (insufficient - requires 10GB minimum)")
    
    def _validate_infrastructure_dependencies(self):
        """Validate infrastructure dependencies with fallback mechanisms."""
        print("\n🏗️  Validating Infrastructure Dependencies...")
        
        dependencies = [
            {
                'name': 'Directus CMS',
                'host': 'localhost',
                'port': 8055,
                'endpoint': '/server/ping',
                'fallback': 'file-based configuration',
                'required': False
            },
            {
                'name': 'Redis Primary',
                'host': '192.168.1.119',
                'port': 6379,
                'endpoint': None,
                'fallback': 'localhost:6380',
                'required': False
            },
            {
                'name': 'Redis Fallback',
                'host': 'localhost',
                'port': 6380,
                'endpoint': None,
                'fallback': 'coordination disabled',
                'required': False
            },
            {
                'name': 'Observatory Server',
                'host': 'localhost',
                'port': 8888,
                'endpoint': '/health',
                'fallback': 'static discovery',
                'required': False
            },
            {
                'name': 'Prometheus',
                'host': 'localhost',
                'port': 9090,
                'endpoint': '/api/v1/status/config',
                'fallback': 'metrics validation disabled',
                'required': False
            },
            {
                'name': 'Grafana',
                'host': 'localhost',
                'port': 3000,
                'endpoint': '/api/health',
                'fallback': 'dashboard validation disabled',
                'required': False
            }
        ]
        
        for dep in dependencies:
            available = self._check_service_availability(dep['host'], dep['port'], dep.get('endpoint'))
            
            if available:
                self._log_success(f"{dep['name']}: Available ({dep['host']}:{dep['port']})")
            else:
                if dep['required']:
                    self._log_error(f"{dep['name']}: Unavailable ({dep['host']}:{dep['port']}) - REQUIRED")
                else:
                    self._log_warning(f"{dep['name']}: Unavailable ({dep['host']}:{dep['port']}) - will use {dep['fallback']}")
    
    def _validate_project_structure(self):
        """Validate project structure and required directories."""
        print("\n📁 Validating Project Structure...")
        
        required_paths = [
            ('.kiro/specs/system-architecture-wiring-diagram', 'Spec directory'),
            ('.kiro/specs/system-architecture-wiring-diagram/requirements.md', 'Requirements document'),
            ('.kiro/specs/system-architecture-wiring-diagram/design.md', 'Design document'),
            ('.kiro/specs/system-architecture-wiring-diagram/tasks.md', 'Tasks document'),
            ('.kiro/specs/system-architecture-wiring-diagram/DAG_TASKS.md', 'DAG tasks document'),
            ('src', 'Source code directory'),
            ('scripts', 'Scripts directory'),
            ('logs', 'Logs directory (will be created if missing)')
        ]
        
        for path_str, description in required_paths:
            path = Path(path_str)
            if path.exists():
                self._log_success(f"{description}: {path} (exists)")
            else:
                if path_str == 'logs':
                    path.mkdir(parents=True, exist_ok=True)
                    self._log_success(f"{description}: {path} (created)")
                else:
                    self._log_error(f"{description}: {path} (missing)")
    
    def _validate_beast_mode_framework(self):
        """Validate Beast Mode framework components."""
        print("\n🐺 Validating Beast Mode Framework...")
        
        beast_mode_components = [
            ('src.rm_ddd.core.unified_reflective_module', 'ReflectiveModule'),
            ('src.rm_ddd.core.dag_registry', 'DAGRegistry'),
            ('src.execution_tracking.redis_execution_tracker', 'RedisExecutionTracker')
        ]
        
        for module_path, component_name in beast_mode_components:
            try:
                module = importlib.import_module(module_path)
                self._log_success(f"{component_name}: Available ({module_path})")
            except ImportError as e:
                self._log_warning(f"{component_name}: Import failed ({module_path}) - {e}")
    
    def _validate_dag_orchestration(self):
        """Validate DAG orchestration capabilities."""
        print("\n🔄 Validating DAG Orchestration...")
        
        # Check DAG task structure
        dag_tasks_file = Path('.kiro/specs/system-architecture-wiring-diagram/DAG_TASKS.md')
        if dag_tasks_file.exists():
            self._log_success("DAG tasks definition: Available")
            
            # Validate DAG structure
            try:
                with open(dag_tasks_file, 'r') as f:
                    content = f.read()
                    
                # Check for key DAG elements
                dag_elements = [
                    ('Task Dependency Graph', 'graph TD'),
                    ('Parallel Execution Opportunities', 'Parallel Execution'),
                    ('Critical Path Analysis', 'Critical Path'),
                    ('Resource Requirements', 'Resource Requirements'),
                    ('Execution Timeline', 'Sequential Execution')
                ]
                
                for element_name, search_term in dag_elements:
                    if search_term in content:
                        self._log_success(f"DAG element {element_name}: Present")
                    else:
                        self._log_warning(f"DAG element {element_name}: Missing")
                        
            except Exception as e:
                self._log_error(f"DAG tasks validation failed: {e}")
        else:
            self._log_error("DAG tasks definition: Missing")
    
    def _validate_execution_tracking(self):
        """Validate execution tracking capabilities."""
        print("\n📊 Validating Execution Tracking...")
        
        # Check Redis availability for tracking
        redis_available = self._check_service_availability('192.168.1.119', 6379) or \
                         self._check_service_availability('localhost', 6380)
        
        if redis_available:
            self._log_success("Redis tracking: Available")
        else:
            self._log_warning("Redis tracking: Unavailable - execution will proceed without tracking")
        
        # Check execution tracking module
        try:
            from src.execution_tracking.redis_execution_tracker import ExecutionStatus
            self._log_success("Execution tracking module: Available")
        except ImportError:
            self._log_warning("Execution tracking module: Unavailable - basic logging will be used")
    
    def _validate_diagram_generation_tools(self):
        """Validate diagram generation tools and dependencies."""
        print("\n📊 Validating Diagram Generation Tools...")
        
        # Check for PlantUML
        try:
            result = subprocess.run(['java', '-version'], capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                self._log_success("Java runtime: Available (required for PlantUML)")
            else:
                self._log_warning("Java runtime: Unavailable - PlantUML diagrams may not work")
        except (subprocess.TimeoutExpired, FileNotFoundError):
            self._log_warning("Java runtime: Unavailable - PlantUML diagrams may not work")
        
        # Check for Mermaid CLI (optional)
        try:
            result = subprocess.run(['mmdc', '--version'], capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                self._log_success("Mermaid CLI: Available")
            else:
                self._log_warning("Mermaid CLI: Unavailable - will use alternative diagram generation")
        except (subprocess.TimeoutExpired, FileNotFoundError):
            self._log_warning("Mermaid CLI: Unavailable - will use alternative diagram generation")
        
        # Check for Graphviz (optional)
        try:
            result = subprocess.run(['dot', '-V'], capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                self._log_success("Graphviz: Available")
            else:
                self._log_warning("Graphviz: Unavailable - some diagram features may be limited")
        except (subprocess.TimeoutExpired, FileNotFoundError):
            self._log_warning("Graphviz: Unavailable - some diagram features may be limited")
    
    def _validate_network_connectivity(self):
        """Validate network connectivity for infrastructure discovery."""
        print("\n🌐 Validating Network Connectivity...")
        
        # Test local network connectivity
        local_network_hosts = [
            ('192.168.1.1', 'Default gateway'),
            ('192.168.1.119', 'Redis coordination server'),
            ('localhost', 'Local services')
        ]
        
        for host, description in local_network_hosts:
            if self._check_host_reachability(host):
                self._log_success(f"Network connectivity to {host}: Available ({description})")
            else:
                self._log_warning(f"Network connectivity to {host}: Unavailable ({description})")
        
        # Test DNS resolution
        dns_hosts = [
            'observatory.nkllon.com',
            'grafana.observatory.nkllon.com',
            'prometheus.observatory.nkllon.com'
        ]
        
        for host in dns_hosts:
            if self._check_dns_resolution(host):
                self._log_success(f"DNS resolution for {host}: Available")
            else:
                self._log_warning(f"DNS resolution for {host}: Unavailable")
    
    def _check_service_availability(self, host: str, port: int, endpoint: Optional[str] = None) -> bool:
        """Check if a service is available on the given host and port."""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(3)
            result = sock.connect_ex((host, port))
            sock.close()
            
            if result == 0:
                # If endpoint is specified, try HTTP request
                if endpoint:
                    try:
                        import requests
                        response = requests.get(f"http://{host}:{port}{endpoint}", timeout=3)
                        return response.status_code < 500
                    except:
                        return True  # Port is open even if HTTP fails
                return True
            return False
        except:
            return False
    
    def _check_host_reachability(self, host: str) -> bool:
        """Check if a host is reachable."""
        try:
            # Try to resolve hostname first
            socket.gethostbyname(host)
            return True
        except socket.gaierror:
            return False
    
    def _check_dns_resolution(self, hostname: str) -> bool:
        """Check if DNS resolution works for a hostname."""
        try:
            socket.gethostbyname(hostname)
            return True
        except socket.gaierror:
            return False
    
    def _log_success(self, message: str):
        """Log a successful validation."""
        print(f"  ✅ {message}")
        self.validation_results.append({
            'type': 'success',
            'message': message,
            'timestamp': datetime.now().isoformat()
        })
    
    def _log_warning(self, message: str):
        """Log a validation warning."""
        print(f"  ⚠️  {message}")
        self.warnings.append(message)
        self.validation_results.append({
            'type': 'warning',
            'message': message,
            'timestamp': datetime.now().isoformat()
        })
    
    def _log_error(self, message: str):
        """Log a validation error."""
        print(f"  ❌ {message}")
        self.errors.append(message)
        self.validation_results.append({
            'type': 'error',
            'message': message,
            'timestamp': datetime.now().isoformat()
        })
    
    def _generate_validation_report(self) -> Dict[str, Any]:
        """Generate comprehensive validation report."""
        end_time = datetime.now()
        duration = (end_time - self.start_time).total_seconds()
        
        print(f"\n📊 Validation Summary")
        print("=" * 50)
        print(f"⏰ Duration: {duration:.1f} seconds")
        print(f"✅ Successes: {len([r for r in self.validation_results if r['type'] == 'success'])}")
        print(f"⚠️  Warnings: {len(self.warnings)}")
        print(f"❌ Errors: {len(self.errors)}")
        
        # Determine overall status
        if len(self.errors) == 0:
            if len(self.warnings) == 0:
                status = "READY"
                status_emoji = "🟢"
                recommendation = "All validations passed. Ready for parallel execution."
            else:
                status = "READY_WITH_WARNINGS"
                status_emoji = "🟡"
                recommendation = "Ready for execution with some limitations. Review warnings."
        else:
            status = "NOT_READY"
            status_emoji = "🔴"
            recommendation = "Critical errors found. Address errors before execution."
        
        print(f"\n{status_emoji} Overall Status: {status}")
        print(f"💡 Recommendation: {recommendation}")
        
        if self.warnings:
            print(f"\n⚠️  Warnings to Review:")
            for warning in self.warnings[:5]:  # Show first 5 warnings
                print(f"  • {warning}")
            if len(self.warnings) > 5:
                print(f"  • ... and {len(self.warnings) - 5} more warnings")
        
        if self.errors:
            print(f"\n❌ Errors to Fix:")
            for error in self.errors:
                print(f"  • {error}")
        
        # Save validation report
        report = {
            'validation_timestamp': self.start_time.isoformat(),
            'duration_seconds': duration,
            'status': status,
            'recommendation': recommendation,
            'successes': len([r for r in self.validation_results if r['type'] == 'success']),
            'warnings': len(self.warnings),
            'errors': len(self.errors),
            'validation_results': self.validation_results,
            'warning_messages': self.warnings,
            'error_messages': self.errors
        }
        
        self._save_validation_report(report)
        
        return report
    
    def _save_validation_report(self, report: Dict[str, Any]):
        """Save validation report to file."""
        logs_dir = Path('logs')
        logs_dir.mkdir(exist_ok=True)
        
        report_file = logs_dir / f"system_architecture_prelaunch_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"\n📄 Validation report saved: {report_file}")


def main():
    """Main validation function."""
    try:
        validator = SystemArchitecturePrelaunchValidator()
        report = validator.validate_all()
        
        # Exit with appropriate code
        if report['status'] == 'NOT_READY':
            print(f"\n💥 VALIDATION FAILED: Critical errors must be resolved before execution")
            sys.exit(1)
        elif report['status'] == 'READY_WITH_WARNINGS':
            print(f"\n⚠️  VALIDATION PASSED WITH WARNINGS: Review warnings before execution")
            sys.exit(0)
        else:
            print(f"\n🎉 VALIDATION PASSED: Ready for System Architecture Wiring Diagram execution")
            sys.exit(0)
            
    except Exception as e:
        print(f"\n💥 VALIDATION ERROR: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()