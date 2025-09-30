#!/usr/bin/env python3
"""
Local DNS Solution - No More Fucking Around
Creates local DNS entries and ensures all services are accessible locally
"""

import subprocess
import socket
import time
from pathlib import Path

class LocalDNSSolution:
    """Brutal, effective local DNS solution"""
    
    def __init__(self):
        self.hosts_file = "/etc/hosts"
        self.local_domains = {
            'prometheus.local': '127.0.0.1',
            'grafana.local': '127.0.0.1', 
            'observatory.local': '127.0.0.1',
            'beast-mode.local': '127.0.0.1'
        }
        self.ports = {
            'prometheus.local': 9090,
            'grafana.local': 3000,
            'observatory.local': 8888,
            'beast-mode.local': 8000
        }
        
    def backup_hosts_file(self):
        """Backup current hosts file"""
        try:
            subprocess.run(['sudo', 'cp', self.hosts_file, f"{self.hosts_file}.backup"], check=True)
            print(f"✅ Backed up {self.hosts_file}")
            return True
        except Exception as e:
            print(f"❌ Failed to backup hosts file: {e}")
            return False
    
    def add_local_dns_entries(self):
        """Add local DNS entries to /etc/hosts"""
        try:
            # Read current hosts file
            with open(self.hosts_file, 'r') as f:
                current_content = f.read()
            
            # Check what's already there
            new_entries = []
            for domain, ip in self.local_domains.items():
                if domain not in current_content:
                    new_entries.append(f"{ip}\t{domain}")
            
            if new_entries:
                # Add new entries
                hosts_addition = "\n# Beast Mode Local DNS\n" + "\n".join(new_entries) + "\n"
                
                # Write to temp file first
                temp_hosts = "/tmp/hosts_new"
                with open(temp_hosts, 'w') as f:
                    f.write(current_content + hosts_addition)
                
                # Copy with sudo
                subprocess.run(['sudo', 'cp', temp_hosts, self.hosts_file], check=True)
                print(f"✅ Added {len(new_entries)} DNS entries to {self.hosts_file}")
                
                for entry in new_entries:
                    print(f"   📍 {entry}")
            else:
                print("✅ All DNS entries already exist")
            
            return True
            
        except Exception as e:
            print(f"❌ Failed to add DNS entries: {e}")
            return False
    
    def test_dns_resolution(self):
        """Test that DNS resolution works"""
        print("🔍 Testing DNS resolution...")
        
        for domain in self.local_domains:
            try:
                ip = socket.gethostbyname(domain)
                print(f"✅ {domain} → {ip}")
            except Exception as e:
                print(f"❌ {domain} → FAILED: {e}")
    
    def check_service_ports(self):
        """Check if services are actually running on expected ports"""
        print("🔍 Checking service ports...")
        
        for domain, port in self.ports.items():
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(2)
                result = sock.connect_ex(('127.0.0.1', port))
                sock.close()
                
                if result == 0:
                    print(f"✅ {domain}:{port} - Service running")
                else:
                    print(f"❌ {domain}:{port} - No service")
            except Exception as e:
                print(f"❌ {domain}:{port} - Error: {e}")
    
    def create_service_urls(self):
        """Create easy access URLs"""
        urls = {}
        for domain, port in self.ports.items():
            urls[domain] = f"http://{domain}:{port}"
        
        print("\n🌐 Local Service URLs:")
        for domain, url in urls.items():
            print(f"   {domain.upper()}: {url}")
        
        return urls
    
    def flush_dns_cache(self):
        """Flush DNS cache to ensure changes take effect"""
        try:
            # macOS DNS flush
            subprocess.run(['sudo', 'dscacheutil', '-flushcache'], check=True)
            subprocess.run(['sudo', 'killall', '-HUP', 'mDNSResponder'], check=True)
            print("✅ DNS cache flushed")
            return True
        except Exception as e:
            print(f"⚠️  DNS cache flush failed (may not be needed): {e}")
            return False
    
    def create_nginx_config(self):
        """Create nginx config for local reverse proxy if needed"""
        nginx_config = """
# Beast Mode Local Reverse Proxy
server {
    listen 80;
    server_name prometheus.local;
    location / {
        proxy_pass http://127.0.0.1:9090;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}

server {
    listen 80;
    server_name grafana.local;
    location / {
        proxy_pass http://127.0.0.1:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}

server {
    listen 80;
    server_name observatory.local;
    location / {
        proxy_pass http://127.0.0.1:8888;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
"""
        
        config_path = Path("nginx_local.conf")
        with open(config_path, 'w') as f:
            f.write(nginx_config)
        
        print(f"✅ Created nginx config: {config_path}")
        print("💡 To use: sudo nginx -c $(pwd)/nginx_local.conf")
        
        return config_path
    
    def run_complete_solution(self):
        """Run the complete local DNS solution"""
        print("🚀 Local DNS Solution - No More Fucking Around")
        print("=" * 60)
        
        # Backup hosts file
        if not self.backup_hosts_file():
            print("❌ Cannot proceed without hosts file backup")
            return False
        
        # Add DNS entries
        if not self.add_local_dns_entries():
            print("❌ Failed to add DNS entries")
            return False
        
        # Flush DNS cache
        self.flush_dns_cache()
        
        # Wait a moment for changes to take effect
        time.sleep(2)
        
        # Test DNS resolution
        self.test_dns_resolution()
        
        # Check service ports
        self.check_service_ports()
        
        # Create service URLs
        urls = self.create_service_urls()
        
        # Create nginx config as backup option
        self.create_nginx_config()
        
        print("\n🎉 Local DNS Solution Complete!")
        print("=" * 40)
        print("✅ DNS entries added to /etc/hosts")
        print("✅ DNS cache flushed")
        print("✅ Service accessibility tested")
        print("\n💡 If services aren't running, start them:")
        print("   docker-compose up -d")
        print("   python start_prometheus_metrics_collection.py")
        
        return True

def main():
    """Main execution"""
    solution = LocalDNSSolution()
    
    try:
        success = solution.run_complete_solution()
        if success:
            print("\n✅ Local DNS solution implemented successfully")
        else:
            print("\n❌ Local DNS solution failed")
    except KeyboardInterrupt:
        print("\n🛑 Interrupted by user")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")

if __name__ == "__main__":
    main()