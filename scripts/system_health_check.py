#!/usr/bin/env python3
"""
System Health Check - Comprehensive diagnostic assessment
Implements Option 3 from the coordination monitor
"""

import os
import sys
import json
import subprocess
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

try:
    from src.rm_ddd.core.unified_reflective_module import ReflectiveModule
    REFLECTIVE_MODULE_AVAILABLE = True
except ImportError:
    REFLECTIVE_MODULE_AVAILABLE = False
    print("⚠️  ReflectiveModule not available - using basic implementation")

class SystemHealthChecker:
    """Comprehensive system health assessment tool"""
    
    def __init__(self):
        self.report = {
            "timestamp": datetime.now().isoformat(),
            "infrastructure": {},
            "applications": {},
            "development": {},
            "configuration": {},
            "issues": {
                "critical": [],
                "warnings": [],
                "optimizations": []
            },
            "summary": {}
        }
    
    def run_command(self, cmd: str, timeout: int = 10) -> Dict[str, Any]:
        """Run a shell command and capture output safely"""
        try:
            result = subprocess.run(
                cmd, shell=True, capture_output=True, text=True, timeout=timeout
            )
            return {
                "success": result.returncode == 0,
                "stdout": result.stdout.strip(),
                "stderr": result.stderr.strip(),
                "returncode": result.returncode
            }
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "stdout": "",
                "stderr": f"Command timed out after {timeout}s",
                "returncode": -1
            }
        except Exception as e:
            return {
                "success": False,
                "stdout": "",
                "stderr": str(e),
                "returncode": -1
            }
    
    def check_docker_services(self):
        """Check Docker container and service status"""
        print("🐳 Checking Docker services...")
        
        # Check Docker daemon
        docker_status = self.run_command("docker info")
        if docker_status["success"]:
            self.report["infrastructure"]["docker_daemon"] = "🟢 HEALTHY"
        else:
            self.report["infrastructure"]["docker_daemon"] = "🔴 CRITICAL"
            self.report["issues"]["critical"].append("Docker daemon not running")
        
        # Check running containers
        containers = self.run_command("docker ps -a --format 'table {{.Names}}\t{{.Status}}\t{{.Ports}}'")
        if containers["success"]:
            self.report["infrastructure"]["containers"] = containers["stdout"]
            # Count running vs stopped
            running = len([line for line in containers["stdout"].split('\n') if 'Up' in line])
            total = len(containers["stdout"].split('\n')) - 1  # Subtract header
            self.report["infrastructure"]["container_summary"] = f"{running}/{total} containers running"
        
        # Check Docker Compose services
        compose_status = self.run_command("docker-compose ps")
        if compose_status["success"]:
            self.report["infrastructure"]["docker_compose"] = compose_status["stdout"]
        
    def check_port_availability(self):
        """Check critical port availability"""
        print("🔌 Checking port availability...")
        
        critical_ports = {
            "8888": "Observatory",
            "3000": "Grafana", 
            "9090": "Prometheus",
            "6379": "Redis"
        }
        
        port_status = {}
        for port, service in critical_ports.items():
            result = self.run_command(f"lsof -i :{port}")
            if result["success"] and result["stdout"]:
                port_status[port] = f"🟢 {service} running"
            else:
                port_status[port] = f"🔴 {service} not running"
                self.report["issues"]["warnings"].append(f"{service} not running on port {port}")
        
        self.report["infrastructure"]["ports"] = port_status
    
    def check_http_endpoints(self):
        """Test HTTP endpoint availability"""
        print("🌐 Checking HTTP endpoints...")
        
        endpoints = {
            "http://localhost:8888/health": "Observatory Health",
            "http://localhost:3000/api/health": "Grafana Health",
            "http://localhost:9090/-/healthy": "Prometheus Health"
        }
        
        endpoint_status = {}
        for url, name in endpoints.items():
            result = self.run_command(f"curl -s -o /dev/null -w '%{{http_code}}' {url}")
            if result["success"] and result["stdout"] == "200":
                endpoint_status[name] = "🟢 HEALTHY"
            else:
                endpoint_status[name] = f"🔴 DOWN (HTTP {result['stdout']})"
                self.report["issues"]["warnings"].append(f"{name} endpoint not responding")
        
        self.report["applications"]["endpoints"] = endpoint_status
    
    def check_network_connectivity(self):
        """Test network connectivity"""
        print("🌍 Checking network connectivity...")
        
        # Test external connectivity
        ping_result = self.run_command("ping -c 3 8.8.8.8")
        if ping_result["success"]:
            self.report["infrastructure"]["internet"] = "🟢 CONNECTED"
        else:
            self.report["infrastructure"]["internet"] = "🔴 NO INTERNET"
            self.report["issues"]["critical"].append("No internet connectivity")
        
        # Check Cloudflare tunnel
        tunnel_result = self.run_command("pgrep -f cloudflared")
        if tunnel_result["success"]:
            self.report["infrastructure"]["cloudflare_tunnel"] = "🟢 RUNNING"
        else:
            self.report["infrastructure"]["cloudflare_tunnel"] = "🟡 NOT RUNNING"
            self.report["issues"]["warnings"].append("Cloudflare tunnel not running")
    
    def check_python_environment(self):
        """Check Python development environment"""
        print("🐍 Checking Python environment...")
        
        # Python version
        python_version = self.run_command("python --version")
        if python_version["success"]:
            self.report["development"]["python_version"] = python_version["stdout"]
        
        # Virtual environment
        venv_check = self.run_command("which python")
        if ".venv" in venv_check["stdout"]:
            self.report["development"]["virtual_env"] = "🟢 ACTIVE"
        else:
            self.report["development"]["virtual_env"] = "🟡 NOT IN VENV"
            self.report["issues"]["warnings"].append("Not running in virtual environment")
        
        # Test critical imports
        import_tests = {
            "ReflectiveModule": "from src.rm_ddd.core.unified_reflective_module import ReflectiveModule",
            "DeploymentAuditor": "from src.deployment_auditor.auditor import DeploymentDataAuditor"
        }
        
        import_status = {}
        for name, import_cmd in import_tests.items():
            result = self.run_command(f"python -c \"{import_cmd}; print('OK')\"")
            if result["success"] and "OK" in result["stdout"]:
                import_status[name] = "🟢 OK"
            else:
                import_status[name] = f"🔴 BROKEN: {result['stderr']}"
                self.report["issues"]["warnings"].append(f"{name} import failed")
        
        self.report["development"]["imports"] = import_status
    
    def check_file_system_health(self):
        """Check file system health"""
        print("💾 Checking file system health...")
        
        # Disk space
        disk_result = self.run_command("df -h . | tail -1")
        if disk_result["success"]:
            self.report["infrastructure"]["disk_space"] = disk_result["stdout"]
        
        # Large log files
        large_logs = self.run_command("find . -name '*.log' -size +100M 2>/dev/null")
        if large_logs["success"] and large_logs["stdout"]:
            self.report["infrastructure"]["large_logs"] = large_logs["stdout"].split('\n')
            self.report["issues"]["optimizations"].append("Large log files found - consider rotation")
        
        # Stuck processes
        stuck_processes = self.run_command("ps aux | awk '$8 ~ /^D/ {print $2, $11}' | head -10")
        if stuck_processes["success"] and stuck_processes["stdout"]:
            self.report["infrastructure"]["stuck_processes"] = stuck_processes["stdout"]
            self.report["issues"]["warnings"].append("Stuck processes detected")
    
    def check_recent_activity(self):
        """Analyze recent system activity"""
        print("📊 Checking recent activity...")
        
        # Recent file changes
        recent_files = self.run_command("find . -type f -mtime -1 -not -path './.git/*' | head -20")
        if recent_files["success"]:
            self.report["development"]["recent_files"] = recent_files["stdout"].split('\n')
        
        # Git status
        git_status = self.run_command("git status --porcelain")
        if git_status["success"]:
            if git_status["stdout"]:
                self.report["development"]["git_changes"] = git_status["stdout"].split('\n')
            else:
                self.report["development"]["git_status"] = "🟢 CLEAN"
        
        # Recent errors in logs
        recent_errors = self.run_command("find . -name '*.log' -mtime -1 -exec grep -l 'ERROR\\|FAIL\\|Exception' {} \\; 2>/dev/null | head -10")
        if recent_errors["success"] and recent_errors["stdout"]:
            self.report["development"]["recent_errors"] = recent_errors["stdout"].split('\n')
            self.report["issues"]["warnings"].append("Recent errors found in logs")
    
    def generate_summary(self):
        """Generate overall health summary"""
        print("📋 Generating summary...")
        
        critical_count = len(self.report["issues"]["critical"])
        warning_count = len(self.report["issues"]["warnings"])
        optimization_count = len(self.report["issues"]["optimizations"])
        
        if critical_count > 0:
            overall_status = "🔴 CRITICAL"
        elif warning_count > 0:
            overall_status = "🟡 WARNING"
        else:
            overall_status = "🟢 HEALTHY"
        
        self.report["summary"] = {
            "overall_status": overall_status,
            "critical_issues": critical_count,
            "warnings": warning_count,
            "optimizations": optimization_count,
            "reflective_module_available": REFLECTIVE_MODULE_AVAILABLE,
            "assessment_time": datetime.now().isoformat()
        }
    
    def run_full_assessment(self) -> Dict[str, Any]:
        """Run complete system health assessment"""
        print("🏥 Starting Comprehensive System Health Check...")
        print("=" * 60)
        
        try:
            self.check_docker_services()
            self.check_port_availability()
            self.check_http_endpoints()
            self.check_network_connectivity()
            self.check_python_environment()
            self.check_file_system_health()
            self.check_recent_activity()
            self.generate_summary()
            
            print("=" * 60)
            print(f"✅ Health check completed: {self.report['summary']['overall_status']}")
            print(f"📊 Issues found: {self.report['summary']['critical_issues']} critical, {self.report['summary']['warnings']} warnings")
            
            return self.report
            
        except Exception as e:
            print(f"❌ Health check failed: {e}")
            self.report["issues"]["critical"].append(f"Health check failed: {e}")
            self.report["summary"]["overall_status"] = "🔴 CRITICAL"
            return self.report

def main():
    """Main execution function"""
    checker = SystemHealthChecker()
    report = checker.run_full_assessment()
    
    # Save report to file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_file = f"system-health-report-{timestamp}.json"
    
    with open(report_file, 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"\n📄 Full report saved to: {report_file}")
    
    # Create markdown summary
    md_file = f"system-health-report-{timestamp}.md"
    with open(md_file, 'w') as f:
        f.write(f"# System Health Report - {report['timestamp']}\n\n")
        f.write(f"## Overall Status: {report['summary']['overall_status']}\n\n")
        
        f.write("## Infrastructure Status\n")
        for key, value in report['infrastructure'].items():
            f.write(f"- **{key}**: {value}\n")
        f.write("\n")
        
        f.write("## Application Status\n")
        for key, value in report['applications'].items():
            f.write(f"- **{key}**: {value}\n")
        f.write("\n")
        
        f.write("## Development Environment\n")
        for key, value in report['development'].items():
            f.write(f"- **{key}**: {value}\n")
        f.write("\n")
        
        if report['issues']['critical']:
            f.write("## 🔴 Critical Issues\n")
            for issue in report['issues']['critical']:
                f.write(f"- {issue}\n")
            f.write("\n")
        
        if report['issues']['warnings']:
            f.write("## 🟡 Warnings\n")
            for issue in report['issues']['warnings']:
                f.write(f"- {issue}\n")
            f.write("\n")
        
        if report['issues']['optimizations']:
            f.write("## 💡 Optimizations\n")
            for issue in report['issues']['optimizations']:
                f.write(f"- {issue}\n")
            f.write("\n")
    
    print(f"📄 Markdown summary saved to: {md_file}")
    
    return report

if __name__ == "__main__":
    main()