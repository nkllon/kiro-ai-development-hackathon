#!/usr/bin/env python3
"""
Docker MCP Integration Helper

Since there's no official Docker MCP server, this script provides Docker
functionality that can be used through the existing MCP infrastructure.
"""

import subprocess
import json
import sys
from typing import Dict, List, Any, Optional
from datetime import datetime

class DockerMCPHelper:
    """Helper class to provide Docker functionality through MCP-compatible interface."""
    
    def __init__(self):
        self.docker_available = self._check_docker_availability()
    
    def _check_docker_availability(self) -> bool:
        """Check if Docker is available and running."""
        try:
            result = subprocess.run(["docker", "--version"], 
                                  capture_output=True, text=True, timeout=5)
            if result.returncode != 0:
                return False
            
            # Check if daemon is running
            result = subprocess.run(["docker", "info"], 
                                  capture_output=True, text=True, timeout=10)
            return result.returncode == 0
        except Exception:
            return False
    
    def list_containers(self, all_containers: bool = False) -> Dict[str, Any]:
        """List Docker containers."""
        if not self.docker_available:
            return {"error": "Docker not available", "containers": []}
        
        try:
            cmd = ["docker", "ps", "--format", "json"]
            if all_containers:
                cmd.append("-a")
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            if result.returncode != 0:
                return {"error": result.stderr, "containers": []}
            
            containers = []
            for line in result.stdout.strip().split('\n'):
                if line:
                    try:
                        containers.append(json.loads(line))
                    except json.JSONDecodeError:
                        continue
            
            return {
                "success": True,
                "containers": containers,
                "count": len(containers),
                "timestamp": datetime.utcnow().isoformat()
            }
        except Exception as e:
            return {"error": str(e), "containers": []}
    
    def get_container_logs(self, container_name: str, tail: int = 100) -> Dict[str, Any]:
        """Get logs from a specific container."""
        if not self.docker_available:
            return {"error": "Docker not available", "logs": ""}
        
        try:
            cmd = ["docker", "logs", "--tail", str(tail), container_name]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            return {
                "success": result.returncode == 0,
                "logs": result.stdout,
                "errors": result.stderr,
                "container": container_name,
                "timestamp": datetime.utcnow().isoformat()
            }
        except Exception as e:
            return {"error": str(e), "logs": ""}
    
    def get_container_stats(self, container_name: Optional[str] = None) -> Dict[str, Any]:
        """Get container statistics."""
        if not self.docker_available:
            return {"error": "Docker not available", "stats": []}
        
        try:
            cmd = ["docker", "stats", "--no-stream", "--format", "json"]
            if container_name:
                cmd.append(container_name)
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            if result.returncode != 0:
                return {"error": result.stderr, "stats": []}
            
            stats = []
            for line in result.stdout.strip().split('\n'):
                if line:
                    try:
                        stats.append(json.loads(line))
                    except json.JSONDecodeError:
                        continue
            
            return {
                "success": True,
                "stats": stats,
                "timestamp": datetime.utcnow().isoformat()
            }
        except Exception as e:
            return {"error": str(e), "stats": []}
    
    def inspect_container(self, container_name: str) -> Dict[str, Any]:
        """Inspect a container for detailed information."""
        if not self.docker_available:
            return {"error": "Docker not available", "info": {}}
        
        try:
            cmd = ["docker", "inspect", container_name]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            if result.returncode != 0:
                return {"error": result.stderr, "info": {}}
            
            info = json.loads(result.stdout)
            return {
                "success": True,
                "info": info[0] if info else {},
                "container": container_name,
                "timestamp": datetime.utcnow().isoformat()
            }
        except Exception as e:
            return {"error": str(e), "info": {}}
    
    def execute_command(self, container_name: str, command: List[str]) -> Dict[str, Any]:
        """Execute a command in a container."""
        if not self.docker_available:
            return {"error": "Docker not available", "output": ""}
        
        try:
            cmd = ["docker", "exec", container_name] + command
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            
            return {
                "success": result.returncode == 0,
                "output": result.stdout,
                "errors": result.stderr,
                "return_code": result.returncode,
                "container": container_name,
                "command": " ".join(command),
                "timestamp": datetime.utcnow().isoformat()
            }
        except Exception as e:
            return {"error": str(e), "output": ""}

def main():
    """Main CLI interface for Docker MCP helper."""
    if len(sys.argv) < 2:
        print("Usage: python docker_mcp_integration.py <command> [args...]")
        print("Commands:")
        print("  list [--all]                    - List containers")
        print("  logs <container> [--tail N]     - Get container logs")
        print("  stats [container]               - Get container stats")
        print("  inspect <container>             - Inspect container")
        print("  exec <container> <command>      - Execute command in container")
        return
    
    helper = DockerMCPHelper()
    command = sys.argv[1]
    
    if command == "list":
        all_containers = "--all" in sys.argv
        result = helper.list_containers(all_containers)
        print(json.dumps(result, indent=2))
    
    elif command == "logs":
        if len(sys.argv) < 3:
            print("Error: Container name required")
            return
        container = sys.argv[2]
        tail = 100
        if "--tail" in sys.argv:
            tail_idx = sys.argv.index("--tail")
            if tail_idx + 1 < len(sys.argv):
                tail = int(sys.argv[tail_idx + 1])
        result = helper.get_container_logs(container, tail)
        print(json.dumps(result, indent=2))
    
    elif command == "stats":
        container = sys.argv[2] if len(sys.argv) > 2 else None
        result = helper.get_container_stats(container)
        print(json.dumps(result, indent=2))
    
    elif command == "inspect":
        if len(sys.argv) < 3:
            print("Error: Container name required")
            return
        container = sys.argv[2]
        result = helper.inspect_container(container)
        print(json.dumps(result, indent=2))
    
    elif command == "exec":
        if len(sys.argv) < 4:
            print("Error: Container name and command required")
            return
        container = sys.argv[2]
        cmd = sys.argv[3:]
        result = helper.execute_command(container, cmd)
        print(json.dumps(result, indent=2))
    
    else:
        print(f"Unknown command: {command}")

if __name__ == "__main__":
    main()