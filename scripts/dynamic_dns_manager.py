#!/usr/bin/env python3
"""
Dynamic DNS Manager for Local Development Stack
==============================================

Automatically manages /etc/hosts entries for running services based on:
1. Docker container discovery
2. ReflectiveModule Redis registrations
3. Service health status

Features:
- Auto-discovery of running services
- Dynamic /etc/hosts management
- Integration with ReflectiveModule registry
- Cleanup of stale entries
- Backup and restore capabilities
"""

import os
import sys
import json
import redis
import docker
import subprocess
from datetime import datetime
from typing import Dict, List, Set, Optional
from pathlib import Path

class DynamicDNSManager:
    """Manages dynamic DNS entries for local development services."""
    
    def __init__(self):
        self.hosts_file = "/etc/hosts"
        self.backup_dir = Path.home() / ".kiro" / "dns_backups"
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        
        # DNS configuration
        self.dns_domain = "kiro.local"
        self.dns_marker_start = "# === KIRO DYNAMIC DNS START ==="
        self.dns_marker_end = "# === KIRO DYNAMIC DNS END ==="
        
        # Service mappings
        self.service_mappings = {
            'local-grafana': {'hostname': 'grafana', 'port': 3000},
            'local-prometheus': {'hostname': 'prometheus', 'port': 9090},
            'local-jaeger': {'hostname': 'jaeger', 'port': 16686},
            'beast-mode-monitoring-daemon': {'hostname': 'monitoring', 'port': 8000},
        }
        
        # Initialize clients
        try:
            self.docker_client = docker.from_env()
            self.redis_client = redis.Redis(host='localhost', port=6379, decode_responses=True)
        except Exception as e:
            print(f"⚠️  Warning: Could not initialize clients: {e}")
            self.docker_client = None
            self.redis_client = None
    
    def backup_hosts_file(self) -> Path:
        """Create a backup of the current hosts file."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = self.backup_dir / f"hosts_backup_{timestamp}"
        
        try:
            subprocess.run(['cp', self.hosts_file, str(backup_path)], check=True)
            print(f"📁 Hosts file backed up to: {backup_path}")
            return backup_path
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to backup hosts file: {e}")
            raise
    
    def discover_docker_services(self) -> Dict[str, Dict]:
        """Discover running Docker services that should have DNS entries."""
        services = {}
        
        if not self.docker_client:
            return services
        
        try:
            containers = self.docker_client.containers.list(filters={'status': 'running'})
            
            for container in containers:
                name = container.name
                if name in self.service_mappings:
                    # Get port mappings
                    ports = container.attrs.get('NetworkSettings', {}).get('Ports', {})
                    
                    service_info = self.service_mappings[name].copy()
                    service_info.update({
                        'container_id': container.id[:12],
                        'status': container.status,
                        'ports': ports,
                        'source': 'docker'
                    })
                    
                    services[name] = service_info
                    
        except Exception as e:
            print(f"⚠️  Warning: Docker service discovery failed: {e}")
        
        return services
    
    def discover_redis_services(self) -> Dict[str, Dict]:
        """Discover services registered in Redis via ReflectiveModule."""
        services = {}
        
        if not self.redis_client:
            return services
        
        try:
            # Get active modules from Redis
            active_modules = self.redis_client.hgetall("beast_mode:active_modules")
            
            for module_id, module_data_str in active_modules.items():
                module_data = json.loads(module_data_str)
                
                # Only include healthy services
                if module_data.get('status') == 'healthy':
                    # Try to determine if this service should have a DNS entry
                    hostname = self._generate_hostname_for_module(module_id, module_data)
                    
                    if hostname:
                        services[module_id] = {
                            'hostname': hostname,
                            'host': module_data.get('host', 'localhost'),
                            'module_type': module_data.get('module_type'),
                            'capabilities': module_data.get('capabilities', []),
                            'status': module_data.get('status'),
                            'source': 'redis'
                        }
                        
        except Exception as e:
            print(f"⚠️  Warning: Redis service discovery failed: {e}")
        
        return services
    
    def _generate_hostname_for_module(self, module_id: str, module_data: Dict) -> Optional[str]:
        """Generate a hostname for a ReflectiveModule service."""
        # Skip test modules
        if 'test' in module_id.lower():
            return None
        
        # Map known module types to hostnames
        hostname_mappings = {
            'ai_memory_palace': 'memory-palace',
            'runtime_state_registry': 'state-registry',
            'dag_orchestrator': 'orchestrator',
            'beast_mode_monitoring': 'monitoring',
        }
        
        # Check for direct mapping
        for pattern, hostname in hostname_mappings.items():
            if pattern in module_id.lower():
                return hostname
        
        # Generate from module_id
        hostname = module_id.lower().replace('_', '-')
        return hostname
    
    def generate_dns_entries(self) -> List[str]:
        """Generate DNS entries for all discovered services."""
        entries = []
        
        # Add header
        entries.append(self.dns_marker_start)
        entries.append(f"# Generated on {datetime.now().isoformat()}")
        entries.append("# Dynamic DNS entries for Kiro development stack")
        entries.append("")
        
        # Discover services
        docker_services = self.discover_docker_services()
        redis_services = self.discover_redis_services()
        
        # Add Docker services
        if docker_services:
            entries.append("# Docker Services")
            for service_name, service_info in docker_services.items():
                hostname = service_info['hostname']
                port = service_info.get('port', '')
                port_info = f" (:{port})" if port else ""
                
                entries.append(f"127.0.0.1    {hostname}.{self.dns_domain}    # {service_name}{port_info}")
            entries.append("")
        
        # Add Redis services
        if redis_services:
            entries.append("# ReflectiveModule Services")
            for module_id, service_info in redis_services.items():
                hostname = service_info['hostname']
                host = service_info.get('host', '127.0.0.1')
                module_type = service_info.get('module_type', '')
                
                # Use localhost for container services too (they're port-forwarded)
                if host != 'localhost':
                    host = '127.0.0.1'
                
                entries.append(f"{host}    {hostname}.{self.dns_domain}    # {module_id} ({module_type})")
            entries.append("")
        
        # Add footer
        entries.append(self.dns_marker_end)
        
        return entries
    
    def update_hosts_file(self, dry_run: bool = False) -> bool:
        """Update the hosts file with dynamic DNS entries."""
        try:
            # Read current hosts file
            with open(self.hosts_file, 'r') as f:
                current_content = f.read()
            
            # Remove existing Kiro DNS section
            lines = current_content.split('\n')
            new_lines = []
            skip_section = False
            
            for line in lines:
                if line.strip() == self.dns_marker_start:
                    skip_section = True
                    continue
                elif line.strip() == self.dns_marker_end:
                    skip_section = False
                    continue
                elif not skip_section:
                    new_lines.append(line)
            
            # Generate new DNS entries
            dns_entries = self.generate_dns_entries()
            
            # Combine content
            if new_lines and new_lines[-1].strip():
                new_lines.append('')  # Add blank line before our section
            
            new_lines.extend(dns_entries)
            new_content = '\n'.join(new_lines)
            
            if dry_run:
                print("🔍 DRY RUN - Would add these DNS entries:")
                print('\n'.join(dns_entries))
                return True
            
            # Backup current hosts file
            self.backup_hosts_file()
            
            # Write new content
            with open(self.hosts_file, 'w') as f:
                f.write(new_content)
            
            print("✅ Hosts file updated successfully")
            return True
            
        except PermissionError:
            print("❌ Permission denied. Run with sudo to modify /etc/hosts")
            return False
        except Exception as e:
            print(f"❌ Failed to update hosts file: {e}")
            return False
    
    def remove_dns_entries(self) -> bool:
        """Remove all Kiro DNS entries from hosts file."""
        try:
            # Read current hosts file
            with open(self.hosts_file, 'r') as f:
                current_content = f.read()
            
            # Remove existing Kiro DNS section
            lines = current_content.split('\n')
            new_lines = []
            skip_section = False
            
            for line in lines:
                if line.strip() == self.dns_marker_start:
                    skip_section = True
                    continue
                elif line.strip() == self.dns_marker_end:
                    skip_section = False
                    continue
                elif not skip_section:
                    new_lines.append(line)
            
            # Remove trailing empty lines
            while new_lines and not new_lines[-1].strip():
                new_lines.pop()
            
            new_content = '\n'.join(new_lines)
            
            # Backup and write
            self.backup_hosts_file()
            
            with open(self.hosts_file, 'w') as f:
                f.write(new_content)
            
            print("✅ Kiro DNS entries removed successfully")
            return True
            
        except PermissionError:
            print("❌ Permission denied. Run with sudo to modify /etc/hosts")
            return False
        except Exception as e:
            print(f"❌ Failed to remove DNS entries: {e}")
            return False
    
    def show_current_entries(self):
        """Show current DNS entries."""
        docker_services = self.discover_docker_services()
        redis_services = self.discover_redis_services()
        
        print("🌐 Current Service Discovery")
        print("=" * 40)
        
        if docker_services:
            print("\n🐳 Docker Services:")
            for name, info in docker_services.items():
                hostname = info['hostname']
                port = info.get('port', '')
                status = info.get('status', 'unknown')
                print(f"   {hostname}.{self.dns_domain} -> localhost:{port} ({status})")
        
        if redis_services:
            print("\n🧠 ReflectiveModule Services:")
            for module_id, info in redis_services.items():
                hostname = info['hostname']
                host = info.get('host', 'localhost')
                status = info.get('status', 'unknown')
                print(f"   {hostname}.{self.dns_domain} -> {host} ({status})")
        
        if not docker_services and not redis_services:
            print("   No services discovered")
    
    def test_dns_resolution(self):
        """Test DNS resolution for registered services."""
        print("🧪 Testing DNS Resolution")
        print("=" * 30)
        
        # Test known services
        test_hosts = [
            f"grafana.{self.dns_domain}",
            f"prometheus.{self.dns_domain}",
            f"jaeger.{self.dns_domain}",
        ]
        
        for hostname in test_hosts:
            try:
                result = subprocess.run(['nslookup', hostname], 
                                      capture_output=True, text=True, timeout=5)
                if result.returncode == 0:
                    print(f"   ✅ {hostname}")
                else:
                    print(f"   ❌ {hostname}")
            except Exception as e:
                print(f"   ❌ {hostname} - {e}")

def main():
    """Main CLI interface."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Dynamic DNS Manager for Kiro Development Stack")
    parser.add_argument('action', choices=['update', 'remove', 'show', 'test', 'dry-run'],
                       help='Action to perform')
    
    args = parser.parse_args()
    
    dns_manager = DynamicDNSManager()
    
    if args.action == 'update':
        success = dns_manager.update_hosts_file()
        sys.exit(0 if success else 1)
    elif args.action == 'remove':
        success = dns_manager.remove_dns_entries()
        sys.exit(0 if success else 1)
    elif args.action == 'show':
        dns_manager.show_current_entries()
    elif args.action == 'test':
        dns_manager.test_dns_resolution()
    elif args.action == 'dry-run':
        dns_manager.update_hosts_file(dry_run=True)

if __name__ == "__main__":
    main()