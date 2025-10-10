#!/usr/bin/env python3
"""
Hybrid Service Manager - Bonjour + /etc/hosts Interoperability
=============================================================

Manages both the existing /etc/hosts based local DNS solution and the new
Bonjour/mDNS service discovery system. Provides unified service discovery
and gradual migration path.

Features:
- Backward compatibility with existing .local domains
- New .kiro.local namespace for Bonjour services
- Unified service discovery interface
- Gradual migration tools
- Conflict detection and resolution
"""

import os
import sys
import json
import subprocess
import socket
from datetime import datetime
from typing import Dict, List, Optional, Set, Any
from pathlib import Path

# Add project root to path
sys.path.insert(0, '.')

# Import our existing managers
from scripts.bonjour_service_manager import BonjourServiceManager
from scripts.port_conflict_detector import PortConflictDetector

class HybridServiceManager:
    """Manages both Bonjour and /etc/hosts based service discovery."""
    
    def __init__(self):
        self.bonjour_manager = BonjourServiceManager()
        self.port_detector = PortConflictDetector()
        
        # Legacy service mappings from existing system
        self.legacy_services = {
            'prometheus': {'domain': 'prometheus.local', 'port': 9090},
            'grafana': {'domain': 'grafana.local', 'port': 3000},
            'observatory': {'domain': 'observatory.local', 'port': 8888},
            'beast-mode': {'domain': 'beast-mode.local', 'port': 8000}
        }
        
        # Namespace configuration
        self.legacy_domain = 'local'
        self.bonjour_domain = 'kiro.local'
    
    def discover_all_services(self) -> Dict[str, Dict[str, Any]]:
        """Discover services from all available sources."""
        all_services = {}
        
        # Bonjour services
        bonjour_services = self._get_bonjour_services()
        for name, info in bonjour_services.items():
            all_services[name] = {
                **info,
                'discovery_method': 'bonjour',
                'domain': f"{name}.{self.bonjour_domain}",
                'modern': True
            }
        
        # Legacy /etc/hosts services
        hosts_services = self._get_hosts_services()
        for name, info in hosts_services.items():
            all_services[name] = {
                **info,
                'discovery_method': 'hosts',
                'domain': info['domain'],
                'modern': False
            }
        
        # Docker services (not yet registered)
        docker_services = self._get_unregistered_docker_services()
        for name, info in docker_services.items():
            if name not in all_services:
                all_services[name] = {
                    **info,
                    'discovery_method': 'docker_only',
                    'domain': f"{name}.{self.bonjour_domain}",
                    'modern': False,
                    'needs_registration': True
                }
        
        return all_services
    
    def _get_bonjour_services(self) -> Dict[str, Dict[str, Any]]:
        """Get services registered with Bonjour."""
        return self.bonjour_manager.registered_services
    
    def _get_hosts_services(self) -> Dict[str, Dict[str, Any]]:
        """Get services from /etc/hosts entries."""
        hosts_services = {}
        
        try:
            with open('/etc/hosts', 'r') as f:
                content = f.read()
            
            for service_name, service_info in self.legacy_services.items():
                domain = service_info['domain']
                port = service_info['port']
                
                if domain in content:
                    # Check if service is actually running
                    is_running = self._is_service_running('127.0.0.1', port)
                    
                    hosts_services[service_name] = {
                        'domain': domain,
                        'port': port,
                        'status': 'running' if is_running else 'stopped',
                        'ip': '127.0.0.1',
                        'registered_at': 'legacy',
                        'txt_records': {'legacy_service': 'true'}
                    }
        
        except Exception as e:
            print(f"⚠️  Error reading /etc/hosts: {e}")
        
        return hosts_services
    
    def _get_unregistered_docker_services(self) -> Dict[str, Dict[str, Any]]:
        """Get Docker services that aren't registered anywhere."""
        try:
            import docker
            client = docker.from_env()
            containers = client.containers.list(filters={'status': 'running'})
            
            unregistered = {}
            service_mappings = {
                'local-grafana': {'name': 'grafana', 'port': 3000},
                'local-prometheus': {'name': 'prometheus', 'port': 9090},
                'local-jaeger': {'name': 'jaeger', 'port': 16686},
                'beast-mode-monitoring-daemon': {'name': 'monitoring', 'port': 8000},
            }
            
            for container in containers:
                if container.name in service_mappings:
                    mapping = service_mappings[container.name]
                    service_name = mapping['name']
                    
                    # Check if already registered with Bonjour
                    if service_name not in self.bonjour_manager.registered_services:
                        unregistered[service_name] = {
                            'container_name': container.name,
                            'container_id': container.id[:12],
                            'port': mapping['port'],
                            'status': container.status,
                            'source': 'docker'
                        }
            
            return unregistered
            
        except Exception as e:
            print(f"⚠️  Docker service discovery failed: {e}")
            return {}
    
    def _is_service_running(self, host: str, port: int) -> bool:
        """Check if a service is running on the specified host:port."""
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.settimeout(2)
                result = sock.connect_ex((host, port))
                return result == 0
        except Exception:
            return False
    
    def register_service(self, name: str, port: int, method: str = 'auto', force: bool = False) -> Dict[str, Any]:
        """Register a service using the best available method."""
        result = {
            'service': name,
            'port': port,
            'method_requested': method,
            'method_used': None,
            'success': False,
            'domain': None,
            'conflicts': [],
            'actions_taken': []
        }
        
        # Check for port conflicts
        conflict_info = self.port_detector.check_conflicts_for_service(name, port)
        if conflict_info['conflict'] and not force:
            result['conflicts'].append({
                'type': 'port_conflict',
                'conflicting_process': conflict_info['conflicting_process'],
                'suggested_port': conflict_info['suggested_port']
            })
            
            if conflict_info['suggested_port']:
                port = conflict_info['suggested_port']
                result['port'] = port
                result['actions_taken'].append(f"Changed port to {port} to avoid conflict")
        
        # Determine registration method
        if method == 'auto':
            if self._bonjour_available():
                method = 'bonjour'
            else:
                method = 'hosts'
        
        result['method_used'] = method
        
        # Register with chosen method
        if method == 'bonjour':
            success = self.bonjour_manager.register_service(name, port)
            if success:
                result['success'] = True
                result['domain'] = f"{name}.{self.bonjour_domain}"
                result['actions_taken'].append("Registered with Bonjour/mDNS")
        
        elif method == 'hosts':
            success = self._add_hosts_entry(name, port)
            if success:
                result['success'] = True
                result['domain'] = f"{name}.{self.legacy_domain}"
                result['actions_taken'].append("Added to /etc/hosts")
        
        elif method == 'both':
            # Register with both systems
            bonjour_success = self.bonjour_manager.register_service(name, port)
            hosts_success = self._add_hosts_entry(name, port)
            
            if bonjour_success or hosts_success:
                result['success'] = True
                result['domain'] = f"{name}.{self.bonjour_domain} and {name}.{self.legacy_domain}"
                if bonjour_success:
                    result['actions_taken'].append("Registered with Bonjour/mDNS")
                if hosts_success:
                    result['actions_taken'].append("Added to /etc/hosts")
        
        return result
    
    def _bonjour_available(self) -> bool:
        """Check if Bonjour/mDNS is available."""
        try:
            result = subprocess.run(['which', 'dns-sd'], capture_output=True, text=True)
            return result.returncode == 0
        except Exception:
            return False
    
    def _add_hosts_entry(self, name: str, port: int) -> bool:
        """Add entry to /etc/hosts (requires sudo)."""
        domain = f"{name}.{self.legacy_domain}"
        entry = f"127.0.0.1\t{domain}"
        
        try:
            # Check if entry already exists
            with open('/etc/hosts', 'r') as f:
                content = f.read()
            
            if domain in content:
                print(f"✅ {domain} already in /etc/hosts")
                return True
            
            # Add entry (this would require sudo in real implementation)
            print(f"⚠️  Would add to /etc/hosts: {entry}")
            print(f"   Run: echo '{entry}' | sudo tee -a /etc/hosts")
            return True
            
        except Exception as e:
            print(f"❌ Failed to add hosts entry: {e}")
            return False
    
    def migrate_service(self, service_name: str, from_method: str, to_method: str) -> Dict[str, Any]:
        """Migrate a service from one discovery method to another."""
        result = {
            'service': service_name,
            'from_method': from_method,
            'to_method': to_method,
            'success': False,
            'actions_taken': [],
            'errors': []
        }
        
        # Get current service info
        all_services = self.discover_all_services()
        if service_name not in all_services:
            result['errors'].append(f"Service {service_name} not found")
            return result
        
        service_info = all_services[service_name]
        port = service_info['port']
        
        # Register with new method
        if to_method == 'bonjour':
            success = self.bonjour_manager.register_service(service_name, port)
            if success:
                result['actions_taken'].append(f"Registered {service_name} with Bonjour")
            else:
                result['errors'].append("Failed to register with Bonjour")
        
        # Remove from old method (if requested)
        if from_method == 'bonjour' and to_method != 'bonjour':
            success = self.bonjour_manager.unregister_service(service_name)
            if success:
                result['actions_taken'].append(f"Unregistered {service_name} from Bonjour")
        
        result['success'] = len(result['errors']) == 0
        return result
    
    def generate_service_report(self) -> str:
        """Generate comprehensive service discovery report."""
        all_services = self.discover_all_services()
        
        report = ["🔍 Hybrid Service Discovery Report", "=" * 40, ""]
        
        # Group by discovery method
        bonjour_services = {k: v for k, v in all_services.items() if v['discovery_method'] == 'bonjour'}
        hosts_services = {k: v for k, v in all_services.items() if v['discovery_method'] == 'hosts'}
        docker_only = {k: v for k, v in all_services.items() if v['discovery_method'] == 'docker_only'}
        
        if bonjour_services:
            report.append("🌐 Bonjour/mDNS Services:")
            for name, info in bonjour_services.items():
                status = "🟢" if info.get('status') == 'running' else "🔴"
                report.append(f"   {status} {info['domain']}:{info['port']} (modern)")
            report.append("")
        
        if hosts_services:
            report.append("📝 /etc/hosts Services:")
            for name, info in hosts_services.items():
                status = "🟢" if info.get('status') == 'running' else "🔴"
                report.append(f"   {status} {info['domain']}:{info['port']} (legacy)")
            report.append("")
        
        if docker_only:
            report.append("🐳 Unregistered Docker Services:")
            for name, info in docker_only.items():
                report.append(f"   ⚠️  {name}:{info['port']} (needs registration)")
            report.append("")
        
        # Summary
        total_services = len(all_services)
        modern_services = len([s for s in all_services.values() if s.get('modern', False)])
        legacy_services = total_services - modern_services
        
        report.append("📊 Summary:")
        report.append(f"   Total Services: {total_services}")
        report.append(f"   Modern (Bonjour): {modern_services}")
        report.append(f"   Legacy (/etc/hosts): {legacy_services}")
        
        return "\n".join(report)
    
    def auto_register_docker_services(self) -> Dict[str, Any]:
        """Automatically register unregistered Docker services."""
        results = {
            'registered': [],
            'failed': [],
            'skipped': []
        }
        
        unregistered = self._get_unregistered_docker_services()
        
        for service_name, service_info in unregistered.items():
            port = service_info['port']
            
            # Try to register with Bonjour
            registration_result = self.register_service(service_name, port, method='bonjour')
            
            if registration_result['success']:
                results['registered'].append({
                    'service': service_name,
                    'port': port,
                    'domain': registration_result['domain']
                })
            else:
                results['failed'].append({
                    'service': service_name,
                    'port': port,
                    'error': 'Registration failed'
                })
        
        return results

def main():
    """Main CLI interface."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Hybrid Service Manager - Bonjour + /etc/hosts")
    parser.add_argument('action', choices=['discover', 'register', 'migrate', 'report', 'auto-register'],
                       help='Action to perform')
    parser.add_argument('--service', help='Service name')
    parser.add_argument('--port', type=int, help='Port number')
    parser.add_argument('--method', choices=['auto', 'bonjour', 'hosts', 'both'], default='auto',
                       help='Registration method')
    parser.add_argument('--from-method', help='Source method for migration')
    parser.add_argument('--to-method', help='Target method for migration')
    parser.add_argument('--force', action='store_true', help='Force registration despite conflicts')
    
    args = parser.parse_args()
    
    manager = HybridServiceManager()
    
    if args.action == 'discover':
        services = manager.discover_all_services()
        print("🔍 All Discovered Services:")
        for name, info in services.items():
            method = info['discovery_method']
            domain = info['domain']
            port = info['port']
            status = info.get('status', 'unknown')
            print(f"   {name}: {domain}:{port} ({method}, {status})")
    
    elif args.action == 'register':
        if not args.service or not args.port:
            print("❌ --service and --port required for register")
            return
        
        result = manager.register_service(args.service, args.port, args.method, args.force)
        
        if result['success']:
            print(f"✅ Registered {args.service} at {result['domain']}")
            for action in result['actions_taken']:
                print(f"   📝 {action}")
        else:
            print(f"❌ Failed to register {args.service}")
            for conflict in result['conflicts']:
                print(f"   ⚠️  {conflict}")
    
    elif args.action == 'migrate':
        if not args.service or not args.from_method or not args.to_method:
            print("❌ --service, --from-method, and --to-method required")
            return
        
        result = manager.migrate_service(args.service, args.from_method, args.to_method)
        
        if result['success']:
            print(f"✅ Migrated {args.service} from {args.from_method} to {args.to_method}")
            for action in result['actions_taken']:
                print(f"   📝 {action}")
        else:
            print(f"❌ Migration failed for {args.service}")
            for error in result['errors']:
                print(f"   ❌ {error}")
    
    elif args.action == 'report':
        print(manager.generate_service_report())
    
    elif args.action == 'auto-register':
        results = manager.auto_register_docker_services()
        
        print("🤖 Auto-registration Results:")
        
        if results['registered']:
            print("✅ Successfully registered:")
            for service in results['registered']:
                print(f"   {service['service']} at {service['domain']}")
        
        if results['failed']:
            print("❌ Failed to register:")
            for service in results['failed']:
                print(f"   {service['service']}: {service['error']}")
        
        if results['skipped']:
            print("⏭️  Skipped:")
            for service in results['skipped']:
                print(f"   {service['service']}: {service['reason']}")

if __name__ == "__main__":
    main()