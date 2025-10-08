#!/usr/bin/env python3
"""
Installation Validator and Health Checker for Beast Mode AI Development Framework

This script validates the installation and performs comprehensive health checks.
"""

import os
import sys
import subprocess
import importlib
import json
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import platform
import socket
from dataclasses import dataclass, asdict

@dataclass
class ValidationResult:
    """Result of a validation check."""
    name: str
    status: str  # "pass", "fail", "warning"
    message: str
    details: Optional[Dict] = None

class InstallationValidator:
    """Validates Beast Mode AI Development Framework installation."""
    
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.results: List[ValidationResult] = []
        
    def log_result(self, name: str, status: str, message: str, details: Optional[Dict] = None):
        """Log a validation result."""
        result = ValidationResult(name, status, message, details)
        self.results.append(result)
        
        # Print result with color coding
        status_symbols = {"pass": "✅", "fail": "❌", "warning": "⚠️"}
        symbol = status_symbols.get(status, "❓")
        print(f"{symbol} {name}: {message}")
        
        if details and status != "pass":
            for key, value in details.items():
                print(f"   {key}: {value}")
    
    def check_python_version(self) -> bool:
        """Check Python version compatibility."""
        version_info = sys.version_info
        min_version = (3, 9)
        
        if version_info >= min_version:
            self.log_result(
                "Python Version",
                "pass",
                f"Python {version_info.major}.{version_info.minor}.{version_info.micro} is compatible"
            )
            return True
        else:
            self.log_result(
                "Python Version",
                "fail",
                f"Python {version_info.major}.{version_info.minor}.{version_info.micro} is too old (requires 3.9+)"
            )
            return False
    
    def check_virtual_environment(self) -> bool:
        """Check if running in virtual environment."""
        in_venv = hasattr(sys, 'real_prefix') or (
            hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix
        )
        
        if in_venv:
            self.log_result(
                "Virtual Environment",
                "pass",
                f"Running in virtual environment: {sys.prefix}"
            )
            return True
        else:
            self.log_result(
                "Virtual Environment",
                "warning",
                "Not running in virtual environment (recommended for isolation)"
            )
            return False
    
    def check_core_dependencies(self) -> bool:
        """Check if core dependencies are installed."""
        core_deps = [
            "pydantic",
            "fastapi", 
            "uvicorn",
            "redis",
            "requests",
            "cryptography",
            "click",
            "prometheus_client",
            "psutil",
            "toml"
        ]
        
        missing_deps = []
        installed_deps = {}
        
        for dep in core_deps:
            try:
                module = importlib.import_module(dep)
                version = getattr(module, '__version__', 'unknown')
                installed_deps[dep] = version
            except ImportError:
                missing_deps.append(dep)
        
        if not missing_deps:
            self.log_result(
                "Core Dependencies",
                "pass",
                f"All {len(core_deps)} core dependencies installed",
                installed_deps
            )
            return True
        else:
            self.log_result(
                "Core Dependencies",
                "fail",
                f"Missing dependencies: {', '.join(missing_deps)}",
                {"missing": missing_deps, "installed": installed_deps}
            )
            return False
    
    def check_optional_dependencies(self) -> bool:
        """Check optional dependencies."""
        optional_deps = [
            ("torch", "ML/AI functionality"),
            ("transformers", "NLP models"),
            ("scipy", "Scientific computing"),
            ("numpy", "Numerical computing"),
            ("aiohttp", "Async HTTP client"),
            ("datasets", "ML datasets")
        ]
        
        installed_optional = {}
        missing_optional = []
        
        for dep, description in optional_deps:
            try:
                module = importlib.import_module(dep)
                version = getattr(module, '__version__', 'unknown')
                installed_optional[dep] = {"version": version, "purpose": description}
            except ImportError:
                missing_optional.append({"name": dep, "purpose": description})
        
        if installed_optional:
            self.log_result(
                "Optional Dependencies",
                "pass" if not missing_optional else "warning",
                f"Installed: {len(installed_optional)}, Missing: {len(missing_optional)}",
                {"installed": installed_optional, "missing": missing_optional}
            )
        else:
            self.log_result(
                "Optional Dependencies",
                "warning",
                "No optional dependencies installed (some features may be limited)"
            )
        
        return len(installed_optional) > 0
    
    def check_environment_configuration(self) -> bool:
        """Check environment configuration."""
        env_files = [
            self.project_root / ".env",
            Path.home() / ".env"
        ]
        
        env_found = False
        env_details = {}
        
        for env_file in env_files:
            if env_file.exists():
                env_found = True
                env_details[str(env_file)] = "exists"
                
                # Check for required environment variables
                required_vars = ["REDIS_HOST", "REDIS_PORT"]
                optional_vars = ["OPENAI_API_KEY", "ANTHROPIC_API_KEY", "REDIS_PASSWORD"]
                
                with open(env_file, 'r') as f:
                    content = f.read()
                    
                for var in required_vars + optional_vars:
                    if f"{var}=" in content:
                        env_details[f"{var}_configured"] = "yes"
                    else:
                        env_details[f"{var}_configured"] = "no"
        
        if env_found:
            self.log_result(
                "Environment Configuration",
                "pass",
                "Environment files found and configured",
                env_details
            )
            return True
        else:
            self.log_result(
                "Environment Configuration",
                "warning",
                "No .env files found (using defaults)",
                {"recommendation": "Create .env file for custom configuration"}
            )
            return False
    
    def check_redis_connection(self) -> bool:
        """Check Redis connection."""
        try:
            import redis
            
            # Load environment variables
            self._load_env_vars()
            
            redis_host = os.getenv('REDIS_HOST', 'localhost')
            redis_port = int(os.getenv('REDIS_PORT', '6379'))
            redis_password = os.getenv('REDIS_PASSWORD', '') or None
            
            # Test connection
            r = redis.Redis(
                host=redis_host,
                port=redis_port,
                password=redis_password,
                decode_responses=True,
                socket_connect_timeout=5
            )
            
            # Test basic operations
            r.ping()
            r.set('beast_mode_test', 'installation_check')
            value = r.get('beast_mode_test')
            r.delete('beast_mode_test')
            
            if value == 'installation_check':
                self.log_result(
                    "Redis Connection",
                    "pass",
                    f"Redis connection successful at {redis_host}:{redis_port}",
                    {"host": redis_host, "port": redis_port, "auth": "yes" if redis_password else "no"}
                )
                return True
            else:
                self.log_result(
                    "Redis Connection",
                    "fail",
                    "Redis connection failed: data integrity issue"
                )
                return False
                
        except ImportError:
            self.log_result(
                "Redis Connection",
                "fail",
                "Redis client not installed"
            )
            return False
        except Exception as e:
            self.log_result(
                "Redis Connection",
                "warning",
                f"Redis connection failed: {str(e)}",
                {"recommendation": "Redis is optional for basic functionality"}
            )
            return False
    
    def check_port_availability(self) -> bool:
        """Check if required ports are available."""
        ports_to_check = [
            (8080, "Observatory"),
            (9090, "Prometheus"),
            (3000, "Grafana"),
            (6379, "Redis")
        ]
        
        port_status = {}
        all_available = True
        
        for port, service in ports_to_check:
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.settimeout(1)
                    result = s.connect_ex(('localhost', port))
                    if result == 0:
                        port_status[f"{service} ({port})"] = "in_use"
                        if service != "Redis":  # Redis being in use is expected
                            all_available = False
                    else:
                        port_status[f"{service} ({port})"] = "available"
            except Exception as e:
                port_status[f"{service} ({port})"] = f"error: {str(e)}"
        
        status = "pass" if all_available else "warning"
        message = "All ports available" if all_available else "Some ports are in use"
        
        self.log_result(
            "Port Availability",
            status,
            message,
            port_status
        )
        
        return all_available
    
    def check_file_structure(self) -> bool:
        """Check project file structure."""
        required_files = [
            "requirements.txt",
            "pyproject.toml",
            "README.md",
            "src",
            "examples",
            "docs"
        ]
        
        missing_files = []
        existing_files = {}
        
        for file_path in required_files:
            full_path = self.project_root / file_path
            if full_path.exists():
                if full_path.is_dir():
                    existing_files[file_path] = "directory"
                else:
                    existing_files[file_path] = "file"
            else:
                missing_files.append(file_path)
        
        if not missing_files:
            self.log_result(
                "File Structure",
                "pass",
                "All required files and directories present",
                existing_files
            )
            return True
        else:
            self.log_result(
                "File Structure",
                "fail",
                f"Missing files/directories: {', '.join(missing_files)}",
                {"existing": existing_files, "missing": missing_files}
            )
            return False
    
    def check_system_resources(self) -> bool:
        """Check system resources."""
        try:
            import psutil
            
            # Check memory
            memory = psutil.virtual_memory()
            memory_gb = memory.total / (1024**3)
            
            # Check disk space
            disk = psutil.disk_usage(str(self.project_root))
            disk_free_gb = disk.free / (1024**3)
            
            # Check CPU
            cpu_count = psutil.cpu_count()
            
            resources = {
                "memory_total_gb": round(memory_gb, 2),
                "memory_available_gb": round(memory.available / (1024**3), 2),
                "disk_free_gb": round(disk_free_gb, 2),
                "cpu_cores": cpu_count
            }
            
            # Determine status based on resources
            status = "pass"
            issues = []
            
            if memory_gb < 4:
                status = "warning"
                issues.append("Low memory (< 4GB)")
            
            if disk_free_gb < 5:
                status = "warning"
                issues.append("Low disk space (< 5GB)")
            
            if cpu_count < 2:
                status = "warning"
                issues.append("Low CPU cores (< 2)")
            
            message = "System resources adequate" if status == "pass" else f"Resource concerns: {', '.join(issues)}"
            
            self.log_result(
                "System Resources",
                status,
                message,
                resources
            )
            
            return status == "pass"
            
        except ImportError:
            self.log_result(
                "System Resources",
                "warning",
                "psutil not available for resource checking"
            )
            return False
    
    def _load_env_vars(self):
        """Load environment variables from .env files."""
        env_files = [
            Path.home() / ".env",
            self.project_root / ".env"
        ]
        
        for env_file in env_files:
            if env_file.exists():
                with open(env_file, 'r') as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith('#') and '=' in line:
                            key, value = line.split('=', 1)
                            key = key.strip()
                            value = value.strip().strip('"').strip("'")
                            if key not in os.environ:  # Don't override existing env vars
                                os.environ[key] = value
    
    def run_comprehensive_validation(self) -> Dict:
        """Run all validation checks."""
        print("🔍 Running comprehensive installation validation...\n")
        
        # System checks
        self.check_python_version()
        self.check_virtual_environment()
        self.check_system_resources()
        
        # Dependency checks
        self.check_core_dependencies()
        self.check_optional_dependencies()
        
        # Configuration checks
        self.check_environment_configuration()
        self.check_file_structure()
        
        # Service checks
        self.check_redis_connection()
        self.check_port_availability()
        
        # Generate summary
        summary = self._generate_summary()
        self._print_summary(summary)
        
        return summary
    
    def _generate_summary(self) -> Dict:
        """Generate validation summary."""
        total_checks = len(self.results)
        passed = len([r for r in self.results if r.status == "pass"])
        failed = len([r for r in self.results if r.status == "fail"])
        warnings = len([r for r in self.results if r.status == "warning"])
        
        overall_status = "healthy"
        if failed > 0:
            overall_status = "issues"
        elif warnings > 0:
            overall_status = "warnings"
        
        return {
            "overall_status": overall_status,
            "total_checks": total_checks,
            "passed": passed,
            "failed": failed,
            "warnings": warnings,
            "pass_rate": round((passed / total_checks) * 100, 1) if total_checks > 0 else 0,
            "system_info": {
                "platform": platform.platform(),
                "python_version": sys.version,
                "working_directory": str(Path.cwd()),
                "project_root": str(self.project_root)
            },
            "results": [asdict(r) for r in self.results]
        }
    
    def _print_summary(self, summary: Dict):
        """Print validation summary."""
        print("\n" + "="*60)
        print("📊 INSTALLATION VALIDATION SUMMARY")
        print("="*60)
        
        status_emoji = {
            "healthy": "✅",
            "warnings": "⚠️",
            "issues": "❌"
        }
        
        emoji = status_emoji.get(summary["overall_status"], "❓")
        print(f"\n{emoji} Overall Status: {summary['overall_status'].upper()}")
        print(f"📈 Pass Rate: {summary['pass_rate']}%")
        print(f"✅ Passed: {summary['passed']}")
        print(f"⚠️  Warnings: {summary['warnings']}")
        print(f"❌ Failed: {summary['failed']}")
        
        if summary["failed"] > 0:
            print("\n🔧 CRITICAL ISSUES TO FIX:")
            for result in self.results:
                if result.status == "fail":
                    print(f"  • {result.name}: {result.message}")
        
        if summary["warnings"] > 0:
            print("\n⚠️  RECOMMENDATIONS:")
            for result in self.results:
                if result.status == "warning":
                    print(f"  • {result.name}: {result.message}")
        
        print(f"\n🖥️  System: {summary['system_info']['platform']}")
        print(f"🐍 Python: {summary['system_info']['python_version'].split()[0]}")
        
        print("\n" + "="*60)
    
    def save_report(self, filename: str = "installation_validation_report.json"):
        """Save validation report to file."""
        summary = self._generate_summary()
        report_path = self.project_root / filename
        
        with open(report_path, 'w') as f:
            json.dump(summary, f, indent=2)
        
        print(f"📄 Validation report saved to: {report_path}")
        return report_path

def main():
    """Main validation process."""
    validator = InstallationValidator()
    
    # Handle command line arguments
    if len(sys.argv) > 1:
        if sys.argv[1] in ["--help", "-h"]:
            print("Beast Mode AI Development Framework - Installation Validator")
            print("\nUsage: python scripts/installation_validator.py [OPTIONS]")
            print("\nOptions:")
            print("  --help, -h     Show this help message")
            print("  --report       Save detailed report to file")
            print("  --quick        Run quick validation (core checks only)")
            return
        
        elif sys.argv[1] == "--quick":
            print("🚀 Running quick validation...\n")
            validator.check_python_version()
            validator.check_core_dependencies()
            validator.check_file_structure()
            summary = validator._generate_summary()
            validator._print_summary(summary)
            return
    
    # Run comprehensive validation
    summary = validator.run_comprehensive_validation()
    
    # Save report if requested
    if len(sys.argv) > 1 and sys.argv[1] == "--report":
        validator.save_report()
    
    # Exit with appropriate code
    if summary["overall_status"] == "issues":
        sys.exit(1)
    elif summary["overall_status"] == "warnings":
        sys.exit(2)
    else:
        sys.exit(0)

if __name__ == "__main__":
    main()