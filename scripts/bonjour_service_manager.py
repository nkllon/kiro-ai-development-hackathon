#!/usr/bin/env python3
"""
Bonjour/mDNS Service Manager for Kiro Development Stack
======================================================

Uses macOS native Bonjour (mDNS) for service discovery instead of /etc/hosts hacking.
Much cleaner, automatic, and network-wide discovery.

Features:
- Automatic service registration with mDNS
- Integration with ReflectiveModule registry
- Docker service discovery
- No root privileges required
- Network-wide discovery
- Automatic cleanup on service shutdown
"""

import os
import sys
import json
import redis
import docker
import subprocess
import signal
import time
from datetime import datetime
from typing import Dict, List, Set, Optional
from pathlib import Path
import threading

class BonjourServiceManager:
    """Manages Bonjour/mDNS service registration for local development."""
    
    def __init__(self):
        self.domain = "kiro.local"
        self.registered_services = {}
        self.dns_sd_processes = {}
        self.running = True
        
        # Service type mappings
        self.service_types = {
            'grafana': '_http._tcp',
            'prometheus': '_http._tcp', 
            'jaeger': '_http._tcp',
            'monitoring': '_http._tcp',
            'redis': '_redis._tcp',
            'default': '_http._tcp'
        }
        
        # Initialize clients
        try:
            self.docker_client = docker.from_env()
            self.redis_client = redis.Redis(host='localhost', port=6379, decode_responses=True)
        except Exception as e:
            print(f"⚠️  Warning: Could not initialize clients: {e}")
            self.docker_client = None
            self.redis_client = None
    
    def register_service(self, name: str, port: int, service_type: str = None, txt_records: Dict[str, str] = None) -> bool:
        """Register a service with Bonjour/mDNS."""
        if service_type is None:
            service_type = self.service_types.get(name, self.service_types['default'])
        
        # Build dns-sd command
        cmd = [
            'dns-sd', '-R',
            name,  # Service name
            service_type,  # Service type
            'local',  # Domain
            str(port)  # Port
        ]
        
        # Add TXT records if provided
        if txt_records:
            for key, value in txt_records.items():
                cmd.append(f"{key}={value}")
        
        try:
            # Start dns-sd process
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Give it a moment to register
            time.sleep(1)
            
            # Check if process is still running (success)
            if process.poll() is None:
                self.dns_sd_processes[name] = process
                self.registered_services[name] = {
                    'port': port,
                    'service_type': service_type,
                    'txt_records': txt_records or {},
                    'registered_at': datetime.now().isoformat(),
                    'process': process
                }
                print(f"✅ Registered {name}.{self.domain}:{port} via Bonjour")
                return True
            else:
                stdout, stderr = process.communicate()
                print(f"❌ Failed to register {name}: {stderr}")
                return False
                
        except Exception as e:
            print(f"❌ Error registering {name}: {e}")
            return False
    
    def unregister_service(self, name: str) -> bool:
        """Unregister a service from Bonjour/mDNS."""
        if name in self.dns_sd_processes:
            try:
                process = self.dns_sd_processes[name]
                process.terminate()
                process.wait(timeout=5)
                
                del self.dns_sd_processes[name]
                del self.registered_services[name]
                
                print(f"✅ Unregistered {name}.{self.domain}")
                return True
                
            except Exception as e:
                print(f"❌ Error unregistering {name}: {e}")
                return False
        else:
            print(f"⚠️  Service {name} not registered")
            return False
    
    def discover_and_register_docker_services(self):
        """Discover and register Docker services."""
        if not self.docker_client:
            return
        
        service_mappings = {
            'local-grafana': {'name': 'grafana', 'port': 3000},
            'local-prometheus': {'name': 'prometheus', 'port': 9090},
            'local-jaeger': {'name': 'jaeger', 'port': 16686},
            'beast-mode-monitoring-daemon': {'name': 'monitoring', 'port': 8000},
        }
        
        try:
            containers = self.docker_client.containers.list(filters={'status': 'running'})
            
            for container in containers:
                if container.name in service_mappings:
                    mapping = service_mappings[container.name]
                    service_name = mapping['name']
                    port = mapping['port']
                    
                    # Add container info as TXT records
                    txt_records = {
                        'container_id': container.id[:12],
                        'container_name': container.name,
                        'status': container.status,
                        'kiro_service': 'true'
                    }
                    
                    if service_name not in self.registered_services:
                        self.register_service(service_name, port, txt_records=txt_records)
                        
        except Exception as e:
            print(f"⚠️  Docker service discovery failed: {e}")
    
    def discover_and_register_redis_services(self):
        """Discover and register ReflectiveModule services from Redis."""
        if not self.redis_client:
            return
        
        try:
            active_modules = self.redis_client.hgetall("beast_mode:active_modules")
            
            for module_id, module_data_str in active_modules.items():
                module_data = json.loads(module_data_str)
                
                # Skip test modules and unhealthy services
                if 'test' in module_id.lower() or module_data.get('status') != 'healthy':
                    continue
                
                # Generate service name
                service_name = self._generate_service_name(module_id)
                if not service_name:
                    continue
                
                # Try to determine port (default to 8080 for web services)
                port = self._determine_service_port(module_id, module_data)
                
                # Add module info as TXT records
                txt_records = {
                    'module_id': module_id,
                    'module_type': module_data.get('module_type', ''),
                    'capabilities': ','.join(module_data.get('capabilities', [])),
                    'status': module_data.get('status', ''),
                    'kiro_service': 'true',
                    'reflective_module': 'true'
                }
                
                if service_name not in self.registered_services:
                    self.register_service(service_name, port, txt_records=txt_records)
                    
        except Exception as e:
            print(f"⚠️  Redis service discovery failed: {e}")
    
    def _generate_service_name(self, module_id: str) -> Optional[str]:
        """Generate a service name from module ID."""
        # Skip test modules
        if 'test' in module_id.lower():
            return None
        
        # Known mappings
        mappings = {
            'ai_memory_palace': 'memory-palace',
            'runtime_state_registry': 'state-registry',
            'dag_orchestrator': 'orchestrator',
            'beast_mode_monitoring': 'monitoring',
        }
        
        for pattern, name in mappings.items():
            if pattern in module_id.lower():
                return name
        
        # Generate from module_id
        return module_id.lower().replace('_', '-')
    
    def _determine_service_port(self, module_id: str, module_data: Dict) -> int:
        """Determine the port for a service."""
        # Default ports for known services
        port_mappings = {
            'memory-palace': 8081,
            'state-registry': 8082,
            'orchestrator': 8083,
            'monitoring': 8000,
        }
        
        service_name = self._generate_service_name(module_id)
        return port_mappings.get(service_name, 8080)
    
    def list_registered_services(self):
        """List all registered services."""
        print("🌐 Registered Bonjour Services")
        print("=" * 40)
        
        if not self.registered_services:
            print("   No services registered")
            return
        
        for name, info in self.registered_services.items():
            port = info['port']
            service_type = info['service_type']
            registered_at = info['registered_at']
            
            print(f"   ✅ {name}.{self.domain}:{port}")
            print(f"      Type: {service_type}")
            print(f"      Registered: {registered_at}")
            
            # Show TXT records
            txt_records = info.get('txt_records', {})
            if txt_records:
                print(f"      TXT Records:")
                for key, value in txt_records.items():
                    print(f"        {key}={value}")
            print()
    
    def browse_services(self):
        """Browse available Bonjour services on the network."""
        print("🔍 Browsing Bonjour Services")
        print("=" * 30)
        
        # Browse for HTTP services
        try:
            result = subprocess.run(
                ['dns-sd', '-B', '_http._tcp'],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')
                for line in lines:
                    if 'kiro' in line.lower():
                        print(f"   📡 {line}")
            else:
                print("   No HTTP services found")
                
        except Exception as e:
            print(f"   ❌ Browse failed: {e}")
    
    def test_service_resolution(self):
        """Test that registered services can be resolved."""
        print("🧪 Testing Service Resolution")
        print("=" * 30)
        
        for name in self.registered_services:
            hostname = f"{name}.{self.domain}"
            
            try:
                # Test DNS resolution
                result = subprocess.run(
                    ['ping', '-c', '1', '-W', '1000', hostname],
                    capture_output=True,
                    text=True,
                    timeout=3
                )
                
                if result.returncode == 0:
                    print(f"   ✅ {hostname} resolves")
                else:
                    print(f"   ❌ {hostname} does not resolve")
                    
            except Exception as e:
                print(f"   ❌ {hostname} - {e}")
    
    def cleanup_all_services(self):
        """Clean up all registered services."""
        print("🧹 Cleaning up all Bonjour services...")
        
        for name in list(self.registered_services.keys()):
            self.unregister_service(name)
        
        print("✅ Cleanup complete")
    
    def run_continuous_discovery(self, interval: int = 30):
        """Run continuous service discovery and registration."""
        print(f"🔄 Starting continuous discovery (every {interval}s)")
        print("Press Ctrl+C to stop")
        
        def signal_handler(signum, frame):
            print("\n🛑 Stopping continuous discovery...")
            self.running = False
            self.cleanup_all_services()
            sys.exit(0)
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        
        try:
            while self.running:
                print(f"\n🔍 Discovery cycle at {datetime.now().strftime('%H:%M:%S')}")
                
                # Discover and register services
                self.discover_and_register_docker_services()
                self.discover_and_register_redis_services()
                
                # Show current status
                self.list_registered_services()
                
                # Wait for next cycle
                time.sleep(interval)
                
        except KeyboardInterrupt:
            print("\n🛑 Stopping...")
            self.cleanup_all_services()

def main():
    """Main CLI interface."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Bonjour/mDNS Service Manager for Kiro")
    parser.add_argument('action', choices=['register', 'unregister', 'list', 'browse', 'test', 'cleanup', 'discover', 'daemon'],
                       help='Action to perform')
    parser.add_argument('--name', help='Service name for register/unregister')
    parser.add_argument('--port', type=int, help='Port for register')
    parser.add_argument('--interval', type=int, default=30, help='Discovery interval for daemon mode')
    
    args = parser.parse_args()
    
    manager = BonjourServiceManager()
    
    if args.action == 'register':
        if not args.name or not args.port:
            print("❌ --name and --port required for register")
            sys.exit(1)
        success = manager.register_service(args.name, args.port)
        sys.exit(0 if success else 1)
        
    elif args.action == 'unregister':
        if not args.name:
            print("❌ --name required for unregister")
            sys.exit(1)
        success = manager.unregister_service(args.name)
        sys.exit(0 if success else 1)
        
    elif args.action == 'list':
        manager.list_registered_services()
        
    elif args.action == 'browse':
        manager.browse_services()
        
    elif args.action == 'test':
        manager.test_service_resolution()
        
    elif args.action == 'cleanup':
        manager.cleanup_all_services()
        
    elif args.action == 'discover':
        print("🔍 Running one-time discovery...")
        manager.discover_and_register_docker_services()
        manager.discover_and_register_redis_services()
        manager.list_registered_services()
        
    elif args.action == 'daemon':
        manager.run_continuous_discovery(args.interval)

if __name__ == "__main__":
    main()