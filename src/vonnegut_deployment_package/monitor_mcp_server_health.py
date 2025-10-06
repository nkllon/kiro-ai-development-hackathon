#!/usr/bin/env python3
"""
MCP Server Health Monitoring Script
Implements periodic health checks and alerting for MCP servers.
"""

import json
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List


class MCPHealthMonitor:
    """Monitor MCP server health and provide alerting."""
    
    def __init__(self, config_path: str = ".kiro/settings/mcp.json"):
        self.config_path = Path(config_path)
        self.health_log = Path("logs/mcp_health.log")
        self.health_log.parent.mkdir(exist_ok=True)
        
    def load_mcp_config(self) -> Dict[str, Any]:
        """Load MCP configuration."""
        try:
            with open(self.config_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            self.log_event("error", f"Failed to load MCP config: {e}")
            return {}
    
    def log_event(self, level: str, message: str):
        """Log health monitoring events."""
        timestamp = datetime.now().isoformat()
        log_entry = f"[{timestamp}] {level.upper()}: {message}\n"
        
        # Write to log file
        with open(self.health_log, 'a') as f:
            f.write(log_entry)
        
        # Also print to console
        print(log_entry.strip())
    
    def test_server_health(self, server_name: str, server_config: Dict[str, Any]) -> Dict[str, Any]:
        """Test health of individual MCP server."""
        result = {
            "server": server_name,
            "timestamp": datetime.now().isoformat(),
            "healthy": False,
            "response_time": None,
            "error": None
        }
        
        if server_config.get("disabled", False):
            result["healthy"] = True
            result["status"] = "disabled"
            return result
        
        command = server_config.get("command", "")
        args = server_config.get("args", [])
        
        if not command:
            result["error"] = "No command specified"
            return result
        
        try:
            start_time = time.time()
            
            # Test with --help to verify server is accessible
            proc = subprocess.run(
                [command] + args + ["--help"],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            response_time = time.time() - start_time
            result["response_time"] = round(response_time, 3)
            
            if proc.returncode == 0:
                result["healthy"] = True
                result["status"] = "ok"
            else:
                result["error"] = proc.stderr[:200] if proc.stderr else "Unknown error"
                
        except subprocess.TimeoutExpired:
            result["error"] = "Server health check timed out"
        except FileNotFoundError:
            result["error"] = f"Command '{command}' not found"
        except Exception as e:
            result["error"] = str(e)
        
        return result
    
    def check_all_servers(self) -> Dict[str, Any]:
        """Check health of all configured MCP servers."""
        config = self.load_mcp_config()
        servers = config.get("mcpServers", {})
        
        results = {
            "timestamp": datetime.now().isoformat(),
            "total_servers": len(servers),
            "healthy_servers": 0,
            "unhealthy_servers": 0,
            "disabled_servers": 0,
            "servers": {}
        }
        
        for server_name, server_config in servers.items():
            health_result = self.test_server_health(server_name, server_config)
            results["servers"][server_name] = health_result
            
            if health_result["healthy"]:
                if health_result.get("status") == "disabled":
                    results["disabled_servers"] += 1
                else:
                    results["healthy_servers"] += 1
            else:
                results["unhealthy_servers"] += 1
                self.log_event("warning", f"Server {server_name} unhealthy: {health_result.get('error', 'Unknown error')}")
        
        return results
    
    def generate_health_report(self, results: Dict[str, Any]) -> str:
        """Generate human-readable health report."""
        report = []
        report.append("🏥 MCP Server Health Report")
        report.append("=" * 40)
        report.append(f"📅 Timestamp: {results['timestamp']}")
        report.append(f"📊 Summary: {results['healthy_servers']}/{results['total_servers']} healthy")
        
        if results["disabled_servers"] > 0:
            report.append(f"⏸️ Disabled: {results['disabled_servers']}")
        
        if results["unhealthy_servers"] > 0:
            report.append(f"❌ Unhealthy: {results['unhealthy_servers']}")
        
        report.append("")
        
        # Server details
        for server_name, server_result in results["servers"].items():
            status_emoji = "✅" if server_result["healthy"] else "❌"
            if server_result.get("status") == "disabled":
                status_emoji = "⏸️"
            
            report.append(f"{status_emoji} {server_name}")
            
            if server_result.get("response_time"):
                report.append(f"  Response time: {server_result['response_time']}s")
            
            if server_result.get("error"):
                report.append(f"  Error: {server_result['error']}")
        
        return "\n".join(report)
    
    def run_health_check(self, verbose: bool = True) -> Dict[str, Any]:
        """Run a single health check cycle."""
        self.log_event("info", "Starting MCP server health check")
        
        results = self.check_all_servers()
        
        if verbose:
            report = self.generate_health_report(results)
            print(report)
        
        # Log summary
        self.log_event("info", f"Health check complete: {results['healthy_servers']}/{results['total_servers']} healthy")
        
        return results
    
    def run_continuous_monitoring(self, interval: int = 300, max_iterations: int = None):
        """Run continuous health monitoring."""
        self.log_event("info", f"Starting continuous monitoring (interval: {interval}s)")
        
        iteration = 0
        try:
            while True:
                if max_iterations and iteration >= max_iterations:
                    break
                
                results = self.run_health_check(verbose=False)
                
                # Alert on unhealthy servers
                if results["unhealthy_servers"] > 0:
                    self.log_event("alert", f"ALERT: {results['unhealthy_servers']} unhealthy servers detected!")
                
                iteration += 1
                time.sleep(interval)
                
        except KeyboardInterrupt:
            self.log_event("info", "Monitoring stopped by user")
        except Exception as e:
            self.log_event("error", f"Monitoring error: {e}")
    
    def get_recovery_procedures(self, server_name: str) -> List[str]:
        """Get recovery procedures for failed server."""
        procedures = {
            "filesystem": [
                "1. Check if uvx is installed and accessible",
                "2. Verify mcp-filesystem package is available: uvx list",
                "3. Check configuration file exists: mcp-filesystem-config.toml",
                "4. Validate environment variables in .kiro/settings/mcp.json",
                "5. Test manual startup: uvx mcp-filesystem --help",
                "6. Check log files for detailed error messages"
            ],
            "git": [
                "1. Verify git is installed and accessible",
                "2. Check if mcp-server-git package is available",
                "3. Test manual startup: uvx mcp-server-git --help",
                "4. Verify git repository access permissions"
            ]
        }
        
        return procedures.get(server_name, [
            "1. Check if server command is accessible",
            "2. Verify server package installation",
            "3. Test manual server startup",
            "4. Check configuration and environment variables",
            "5. Review server logs for error details"
        ])


def main():
    """Main function for MCP health monitoring."""
    if len(sys.argv) > 1:
        if sys.argv[1] == "--help":
            print("Usage: python monitor_mcp_server_health.py [options]")
            print("Options:")
            print("  --continuous [interval]  Run continuous monitoring (default: 300s)")
            print("  --recovery <server>      Show recovery procedures for server")
            print("  --json                   Output results in JSON format")
            return
        
        elif sys.argv[1] == "--continuous":
            interval = 300
            if len(sys.argv) > 2:
                try:
                    interval = int(sys.argv[2])
                except ValueError:
                    print("Invalid interval, using default 300s")
            
            monitor = MCPHealthMonitor()
            monitor.run_continuous_monitoring(interval)
            return
        
        elif sys.argv[1] == "--recovery":
            if len(sys.argv) < 3:
                print("Please specify server name for recovery procedures")
                return
            
            server_name = sys.argv[2]
            monitor = MCPHealthMonitor()
            procedures = monitor.get_recovery_procedures(server_name)
            
            print(f"🔧 Recovery Procedures for {server_name}")
            print("=" * 40)
            for procedure in procedures:
                print(f"  {procedure}")
            return
        
        elif sys.argv[1] == "--json":
            monitor = MCPHealthMonitor()
            results = monitor.check_all_servers()
            print(json.dumps(results, indent=2))
            return
    
    # Default: single health check
    monitor = MCPHealthMonitor()
    monitor.run_health_check()


if __name__ == "__main__":
    main()