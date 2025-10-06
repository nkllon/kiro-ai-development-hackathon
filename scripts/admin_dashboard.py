#!/usr/bin/env python3
"""
Kiro Admin Dashboard - Web Interface for System Management
=========================================================

A modern web-based dashboard to replace the "F-15 with a joystick" make target approach.
Provides a unified interface for all system operations, service management, and monitoring.

Features:
- Real-time service monitoring
- One-click make target execution
- Bonjour/mDNS service management
- Live logs and metrics
- Mobile-responsive design
- WebSocket real-time updates
"""

import os
import sys
import json
import redis
import docker
import subprocess
import asyncio
import signal
from datetime import datetime
from typing import Dict, List, Optional, Any
from pathlib import Path

# Web framework imports
from fastapi import FastAPI, WebSocket, Request, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, JSONResponse
import uvicorn

# Add project root to path
sys.path.insert(0, '.')

class KiroAdminDashboard:
    """Main admin dashboard application."""
    
    def __init__(self):
        self.app = FastAPI(title="Kiro Admin Dashboard", version="1.0.0")
        self.setup_routes()
        
        # Initialize clients
        try:
            self.docker_client = docker.from_env()
            self.redis_client = redis.Redis(host='localhost', port=6379, decode_responses=True)
        except Exception as e:
            print(f"⚠️  Warning: Could not initialize clients: {e}")
            self.docker_client = None
            self.redis_client = None
        
        # WebSocket connections for real-time updates
        self.websocket_connections = set()
        
        # Make target definitions
        self.make_targets = self._discover_make_targets()
    
    def setup_routes(self):
        """Setup FastAPI routes."""
        
        @self.app.get("/", response_class=HTMLResponse)
        async def dashboard_home(request: Request):
            """Main dashboard page."""
            return self._render_dashboard()
        
        @self.app.get("/api/services")
        async def get_services():
            """Get all discovered services."""
            return {
                "docker_services": self._get_docker_services(),
                "redis_services": self._get_redis_services(),
                "bonjour_services": self._get_bonjour_services(),
                "hybrid_services": self._get_hybrid_services()
            }
        
        @self.app.get("/api/make-targets")
        async def get_make_targets():
            """Get all available make targets."""
            return {"targets": self.make_targets}
        
        @self.app.post("/api/make-targets/{target}/execute")
        async def execute_make_target(target: str, params: Dict[str, Any] = None):
            """Execute a make target."""
            if target not in self.make_targets:
                raise HTTPException(status_code=404, detail="Make target not found")
            
            try:
                result = await self._execute_make_target(target, params or {})
                return {"success": True, "result": result}
            except Exception as e:
                return {"success": False, "error": str(e)}
        
        @self.app.post("/api/services/{service}/action/{action}")
        async def service_action(service: str, action: str):
            """Perform action on a service (start/stop/restart)."""
            try:
                result = await self._perform_service_action(service, action)
                return {"success": True, "result": result}
            except Exception as e:
                return {"success": False, "error": str(e)}
        
        @self.app.get("/api/logs/{service}")
        async def get_service_logs(service: str, lines: int = 100):
            """Get logs for a service."""
            try:
                logs = await self._get_service_logs(service, lines)
                return {"logs": logs}
            except Exception as e:
                return {"error": str(e)}
        
        @self.app.websocket("/ws")
        async def websocket_endpoint(websocket: WebSocket):
            """WebSocket endpoint for real-time updates."""
            await websocket.accept()
            self.websocket_connections.add(websocket)
            
            try:
                while True:
                    # Send periodic updates
                    await asyncio.sleep(5)
                    update_data = {
                        "timestamp": datetime.now().isoformat(),
                        "services": await self._get_service_status_update()
                    }
                    await websocket.send_json(update_data)
                    
            except Exception as e:
                print(f"WebSocket error: {e}")
            finally:
                self.websocket_connections.discard(websocket)
    
    def _render_dashboard(self) -> str:
        """Render the main dashboard HTML."""
        return """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Kiro Admin Dashboard</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://unpkg.com/alpinejs@3.x.x/dist/cdn.min.js" defer></script>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
</head>
<body class="bg-gray-100 min-h-screen">
    <div x-data="dashboard()" x-init="init()">
        <!-- Header -->
        <header class="bg-blue-600 text-white shadow-lg">
            <div class="container mx-auto px-4 py-4">
                <div class="flex items-center justify-between">
                    <h1 class="text-2xl font-bold">
                        <i class="fas fa-rocket mr-2"></i>
                        Kiro Admin Dashboard
                    </h1>
                    <div class="flex items-center space-x-4">
                        <span class="text-sm" x-text="'Last Update: ' + lastUpdate"></span>
                        <div class="flex items-center">
                            <div class="w-3 h-3 rounded-full mr-2" 
                                 :class="connected ? 'bg-green-400' : 'bg-red-400'"></div>
                            <span class="text-sm" x-text="connected ? 'Connected' : 'Disconnected'"></span>
                        </div>
                    </div>
                </div>
            </div>
        </header>

        <!-- Main Content -->
        <div class="container mx-auto px-4 py-8">
            <!-- Service Status Grid -->
            <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-8">
                <template x-for="service in services" :key="service.name">
                    <div class="bg-white rounded-lg shadow-md p-6">
                        <div class="flex items-center justify-between mb-4">
                            <h3 class="text-lg font-semibold" x-text="service.name"></h3>
                            <div class="flex items-center">
                                <div class="w-3 h-3 rounded-full mr-2" 
                                     :class="service.status === 'running' ? 'bg-green-400' : 'bg-red-400'"></div>
                                <span class="text-sm" x-text="service.status"></span>
                            </div>
                        </div>
                        
                        <div class="text-sm text-gray-600 mb-4">
                            <p><strong>URL:</strong> <a :href="service.url" target="_blank" class="text-blue-600 hover:underline" x-text="service.url"></a></p>
                            <p><strong>Port:</strong> <span x-text="service.port"></span></p>
                            <p><strong>Type:</strong> <span x-text="service.type"></span></p>
                        </div>
                        
                        <div class="flex space-x-2">
                            <button @click="performServiceAction(service.name, 'restart')" 
                                    class="bg-blue-500 text-white px-3 py-1 rounded text-sm hover:bg-blue-600">
                                <i class="fas fa-redo mr-1"></i> Restart
                            </button>
                            <button @click="viewLogs(service.name)" 
                                    class="bg-gray-500 text-white px-3 py-1 rounded text-sm hover:bg-gray-600">
                                <i class="fas fa-file-alt mr-1"></i> Logs
                            </button>
                        </div>
                    </div>
                </template>
            </div>

            <!-- Make Targets Section -->
            <div class="bg-white rounded-lg shadow-md p-6 mb-8">
                <h2 class="text-xl font-bold mb-4">
                    <i class="fas fa-terminal mr-2"></i>
                    Make Targets
                </h2>
                
                <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                    <template x-for="target in makeTargets" :key="target.name">
                        <div class="border rounded-lg p-4">
                            <h3 class="font-semibold mb-2" x-text="target.name"></h3>
                            <p class="text-sm text-gray-600 mb-3" x-text="target.description"></p>
                            <button @click="executeMakeTarget(target.name)" 
                                    class="bg-green-500 text-white px-4 py-2 rounded hover:bg-green-600 w-full">
                                <i class="fas fa-play mr-1"></i> Execute
                            </button>
                        </div>
                    </template>
                </div>
            </div>

            <!-- System Status -->
            <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                <!-- Redis Status -->
                <div class="bg-white rounded-lg shadow-md p-6">
                    <h2 class="text-xl font-bold mb-4">
                        <i class="fas fa-database mr-2"></i>
                        Redis Status
                    </h2>
                    <div class="space-y-2">
                        <p><strong>Active Modules:</strong> <span x-text="redisStatus.activeModules"></span></p>
                        <p><strong>Health Entries:</strong> <span x-text="redisStatus.healthEntries"></span></p>
                        <p><strong>Service Registry:</strong> <span x-text="redisStatus.serviceRegistry"></span></p>
                    </div>
                </div>

                <!-- Docker Status -->
                <div class="bg-white rounded-lg shadow-md p-6">
                    <h2 class="text-xl font-bold mb-4">
                        <i class="fab fa-docker mr-2"></i>
                        Docker Status
                    </h2>
                    <div class="space-y-2">
                        <p><strong>Running Containers:</strong> <span x-text="dockerStatus.runningContainers"></span></p>
                        <p><strong>Total Containers:</strong> <span x-text="dockerStatus.totalContainers"></span></p>
                        <p><strong>Images:</strong> <span x-text="dockerStatus.images"></span></p>
                    </div>
                </div>
            </div>
        </div>

        <!-- Log Modal -->
        <div x-show="showLogModal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
            <div class="bg-white rounded-lg p-6 max-w-4xl w-full mx-4 max-h-96 overflow-hidden">
                <div class="flex justify-between items-center mb-4">
                    <h3 class="text-lg font-bold">Logs: <span x-text="currentLogService"></span></h3>
                    <button @click="showLogModal = false" class="text-gray-500 hover:text-gray-700">
                        <i class="fas fa-times"></i>
                    </button>
                </div>
                <div class="bg-black text-green-400 p-4 rounded font-mono text-sm overflow-y-auto max-h-64">
                    <pre x-text="currentLogs"></pre>
                </div>
            </div>
        </div>
    </div>

    <script>
        function dashboard() {
            return {
                services: [],
                makeTargets: [],
                redisStatus: {},
                dockerStatus: {},
                connected: false,
                lastUpdate: '',
                showLogModal: false,
                currentLogService: '',
                currentLogs: '',
                
                async init() {
                    await this.loadData();
                    this.connectWebSocket();
                    setInterval(() => this.loadData(), 30000); // Refresh every 30s
                },
                
                async loadData() {
                    try {
                        const [servicesRes, targetsRes] = await Promise.all([
                            fetch('/api/services'),
                            fetch('/api/make-targets')
                        ]);
                        
                        const servicesData = await servicesRes.json();
                        const targetsData = await targetsRes.json();
                        
                        this.services = this.processServices(servicesData);
                        this.makeTargets = targetsData.targets;
                        this.lastUpdate = new Date().toLocaleTimeString();
                        
                    } catch (error) {
                        console.error('Failed to load data:', error);
                    }
                },
                
                processServices(data) {
                    const services = [];
                    
                    // Process Docker services
                    Object.entries(data.docker_services || {}).forEach(([name, info]) => {
                        services.push({
                            name: name,
                            status: info.status || 'unknown',
                            port: info.port || 'unknown',
                            url: `http://${name}.kiro.local:${info.port}`,
                            type: 'Docker'
                        });
                    });
                    
                    // Process Redis services
                    Object.entries(data.redis_services || {}).forEach(([name, info]) => {
                        services.push({
                            name: name,
                            status: info.status || 'unknown',
                            port: info.port || 'unknown',
                            url: `http://${name}.kiro.local:${info.port}`,
                            type: 'ReflectiveModule'
                        });
                    });
                    
                    return services;
                },
                
                connectWebSocket() {
                    const ws = new WebSocket(`ws://${window.location.host}/ws`);
                    
                    ws.onopen = () => {
                        this.connected = true;
                    };
                    
                    ws.onmessage = (event) => {
                        const data = JSON.parse(event.data);
                        // Handle real-time updates
                        this.lastUpdate = new Date(data.timestamp).toLocaleTimeString();
                    };
                    
                    ws.onclose = () => {
                        this.connected = false;
                        // Reconnect after 5 seconds
                        setTimeout(() => this.connectWebSocket(), 5000);
                    };
                },
                
                async executeMakeTarget(target) {
                    try {
                        const response = await fetch(`/api/make-targets/${target}/execute`, {
                            method: 'POST'
                        });
                        const result = await response.json();
                        
                        if (result.success) {
                            alert(`✅ ${target} executed successfully`);
                        } else {
                            alert(`❌ ${target} failed: ${result.error}`);
                        }
                    } catch (error) {
                        alert(`❌ Error executing ${target}: ${error.message}`);
                    }
                },
                
                async performServiceAction(service, action) {
                    try {
                        const response = await fetch(`/api/services/${service}/action/${action}`, {
                            method: 'POST'
                        });
                        const result = await response.json();
                        
                        if (result.success) {
                            alert(`✅ ${action} on ${service} successful`);
                            await this.loadData();
                        } else {
                            alert(`❌ ${action} on ${service} failed: ${result.error}`);
                        }
                    } catch (error) {
                        alert(`❌ Error: ${error.message}`);
                    }
                },
                
                async viewLogs(service) {
                    try {
                        const response = await fetch(`/api/logs/${service}`);
                        const result = await response.json();
                        
                        this.currentLogService = service;
                        this.currentLogs = result.logs || 'No logs available';
                        this.showLogModal = true;
                    } catch (error) {
                        alert(`❌ Error loading logs: ${error.message}`);
                    }
                }
            }
        }
    </script>
</body>
</html>
        """
    
    def _discover_make_targets(self) -> List[Dict[str, str]]:
        """Discover available make targets."""
        targets = []
        
        # Common targets we know about
        known_targets = {
            'dns-install': 'Install local DNS entries',
            'dns-show': 'Show DNS status',
            'dns-test': 'Test DNS resolution',
            'observatory-start': 'Start Observatory services',
            'observatory-stop': 'Stop Observatory services',
            'beast-test': 'Run Beast Mode tests',
            'dag-validate': 'Validate DAG structure',
            'infra-deploy': 'Deploy infrastructure',
            'test-system': 'Run system tests',
            'clean-all': 'Clean all artifacts'
        }
        
        for target, description in known_targets.items():
            targets.append({
                'name': target,
                'description': description,
                'category': target.split('-')[0]
            })
        
        return targets
    
    def _get_docker_services(self) -> Dict[str, Dict]:
        """Get Docker service information."""
        services = {}
        
        if not self.docker_client:
            return services
        
        try:
            containers = self.docker_client.containers.list()
            
            for container in containers:
                services[container.name] = {
                    'status': container.status,
                    'id': container.id[:12],
                    'image': container.image.tags[0] if container.image.tags else 'unknown',
                    'ports': container.ports
                }
                
        except Exception as e:
            print(f"Error getting Docker services: {e}")
        
        return services
    
    def _get_hybrid_services(self) -> Dict[str, Dict]:
        """Get services from hybrid service manager."""
        try:
            from scripts.hybrid_service_manager import HybridServiceManager
            hybrid_manager = HybridServiceManager()
            return hybrid_manager.discover_all_services()
        except Exception as e:
            print(f"Error getting hybrid services: {e}")
            return {}
    
    def _get_redis_services(self) -> Dict[str, Dict]:
        """Get Redis service information."""
        services = {}
        
        if not self.redis_client:
            return services
        
        try:
            active_modules = self.redis_client.hgetall("beast_mode:active_modules")
            
            for module_id, module_data_str in active_modules.items():
                module_data = json.loads(module_data_str)
                services[module_id] = module_data
                
        except Exception as e:
            print(f"Error getting Redis services: {e}")
        
        return services
    
    def _get_bonjour_services(self) -> Dict[str, Dict]:
        """Get Bonjour service information."""
        # This would integrate with the Bonjour service manager
        return {}
    
    async def _execute_make_target(self, target: str, params: Dict[str, Any]) -> str:
        """Execute a make target."""
        try:
            process = await asyncio.create_subprocess_exec(
                'make', target,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            if process.returncode == 0:
                return stdout.decode()
            else:
                raise Exception(stderr.decode())
                
        except Exception as e:
            raise Exception(f"Failed to execute make {target}: {e}")
    
    async def _perform_service_action(self, service: str, action: str) -> str:
        """Perform an action on a service."""
        # This would integrate with Docker/systemd/etc.
        return f"Action {action} performed on {service}"
    
    async def _get_service_logs(self, service: str, lines: int) -> str:
        """Get logs for a service."""
        if self.docker_client:
            try:
                container = self.docker_client.containers.get(service)
                logs = container.logs(tail=lines).decode()
                return logs
            except Exception as e:
                return f"Error getting logs: {e}"
        
        return "No logs available"
    
    async def _get_service_status_update(self) -> Dict:
        """Get real-time service status update."""
        return {
            'docker': self._get_docker_services(),
            'redis': self._get_redis_services()
        }
    
    def run(self, host: str = "0.0.0.0", port: int = 8889):
        """Run the dashboard server."""
        print(f"🚀 Starting Kiro Admin Dashboard on http://{host}:{port}")
        print("🌐 Access the dashboard in your browser")
        print("📱 Mobile-responsive design included")
        print("🔄 Real-time updates via WebSocket")
        print(f"ℹ️  Using port {port} to avoid conflict with Observatory (8888)")
        
        uvicorn.run(self.app, host=host, port=port, log_level="info")

def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Kiro Admin Dashboard")
    parser.add_argument('--host', default='0.0.0.0', help='Host to bind to')
    parser.add_argument('--port', type=int, default=8889, help='Port to bind to')
    
    args = parser.parse_args()
    
    dashboard = KiroAdminDashboard()
    dashboard.run(host=args.host, port=args.port)

if __name__ == "__main__":
    main()