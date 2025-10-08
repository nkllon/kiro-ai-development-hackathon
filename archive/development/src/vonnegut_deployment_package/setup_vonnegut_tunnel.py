#!/usr/bin/env python3
"""
Setup Cloudflare Tunnel on Vonnegut
===================================

Sets up a containerized Cloudflare tunnel on the Vonnegut server to properly
expose Observatory services running on Vonnegut (not local Mac).
"""

import os
import sys
import subprocess
from pathlib import Path

class VonnegutTunnelSetup:
    def __init__(self):
        self.vonnegut_ip = "192.168.1.119"
        self.ssh_user = "lou"
        self.remote_path = "/home/lou/cloudflare-tunnel"
        self.tunnel_credentials = Path.home() / ".cloudflared" / "d1e53e43-033f-4994-8f46-c83962ae3785.json"
    
    def check_ssh_access(self) -> bool:
        """Check SSH access to Vonnegut."""
        print(f"🔐 Testing SSH access to {self.ssh_user}@{self.vonnegut_ip}...")
        
        try:
            result = subprocess.run([
                "ssh", "-o", "ConnectTimeout=10", "-o", "BatchMode=yes",
                f"{self.ssh_user}@{self.vonnegut_ip}", "echo 'SSH OK'"
            ], capture_output=True, text=True, timeout=15)
            
            if result.returncode == 0:
                print(f"✅ SSH access confirmed")
                return True
            else:
                print(f"❌ SSH access failed")
                print(f"💡 Setup SSH key: ssh-copy-id {self.ssh_user}@{self.vonnegut_ip}")
                return False
                
        except Exception as e:
            print(f"❌ SSH test failed: {e}")
            return False
    
    def create_tunnel_config(self) -> str:
        """Create Cloudflare tunnel configuration for Vonnegut."""
        config = """tunnel: d1e53e43-033f-4994-8f46-c83962ae3785
credentials-file: /etc/cloudflared/credentials.json

ingress:
  - hostname: observatory.nkllon.com
    service: http://host.docker.internal:8888
    originRequest:
      httpHostHeader: localhost:8888
      noTLSVerify: false
      connectTimeout: 30s
      tlsTimeout: 10s
      tcpKeepAlive: 30s
      keepAliveConnections: 100
      keepAliveTimeout: 90s
  - hostname: prometheus.observatory.nkllon.com
    service: http://host.docker.internal:9090
    originRequest:
      httpHostHeader: localhost:9090
      noTLSVerify: false
      connectTimeout: 30s
      tlsTimeout: 10s
      tcpKeepAlive: 30s
      keepAliveConnections: 100
      keepAliveTimeout: 90s
  - hostname: grafana.observatory.nkllon.com
    service: http://host.docker.internal:3000
    originRequest:
      httpHostHeader: localhost:3000
      noTLSVerify: false
      connectTimeout: 30s
      tlsTimeout: 10s
      tcpKeepAlive: 30s
      keepAliveConnections: 100
      keepAliveTimeout: 90s
  - service: http_status:404
"""
        return config
    
    def create_docker_compose(self) -> str:
        """Create Docker Compose for tunnel."""
        compose = """version: '3.8'

services:
  cloudflare-tunnel:
    image: cloudflare/cloudflared:latest
    container_name: vonnegut-tunnel
    volumes:
      - ./config.yml:/etc/cloudflared/config.yml:ro
      - ./credentials.json:/etc/cloudflared/credentials.json:ro
    command: ["tunnel", "--config", "/etc/cloudflared/config.yml", "run"]
    restart: unless-stopped
    network_mode: host
    extra_hosts:
      - "host.docker.internal:host-gateway"
"""
        return compose
    
    def setup_tunnel_on_vonnegut(self) -> bool:
        """Setup the tunnel on Vonnegut server."""
        print(f"🚀 Setting up Cloudflare tunnel on Vonnegut...")
        
        # Create local temp directory
        temp_dir = Path("temp_tunnel_setup")
        temp_dir.mkdir(exist_ok=True)
        
        try:
            # Create configuration files
            with open(temp_dir / "config.yml", 'w') as f:
                f.write(self.create_tunnel_config())
            
            with open(temp_dir / "docker-compose.yml", 'w') as f:
                f.write(self.create_docker_compose())
            
            # Copy tunnel credentials
            if self.tunnel_credentials.exists():
                subprocess.run([
                    "cp", str(self.tunnel_credentials), 
                    str(temp_dir / "credentials.json")
                ], check=True)
            else:
                print(f"❌ Tunnel credentials not found: {self.tunnel_credentials}")
                return False
            
            # Create remote directory
            subprocess.run([
                "ssh", f"{self.ssh_user}@{self.vonnegut_ip}",
                f"mkdir -p {self.remote_path}"
            ], check=True)
            
            # Upload files
            subprocess.run([
                "rsync", "-avz",
                f"{temp_dir}/",
                f"{self.ssh_user}@{self.vonnegut_ip}:{self.remote_path}/"
            ], check=True)
            
            # Deploy tunnel on Vonnegut
            deploy_script = f"""
cd {self.remote_path}

# Stop any existing tunnel
docker-compose down 2>/dev/null || true

# Start the tunnel
docker-compose up -d

# Check status
sleep 5
docker-compose ps
docker logs vonnegut-tunnel --tail=20

echo "✅ Cloudflare tunnel deployed on Vonnegut"
"""
            
            result = subprocess.run([
                "ssh", f"{self.ssh_user}@{self.vonnegut_ip}",
                deploy_script
            ], text=True, capture_output=True)
            
            print("📋 Deployment output:")
            print(result.stdout)
            
            if result.stderr:
                print("⚠️ Deployment warnings:")
                print(result.stderr)
            
            # Cleanup temp directory
            subprocess.run(["rm", "-rf", str(temp_dir)], check=True)
            
            return result.returncode == 0
            
        except Exception as e:
            print(f"❌ Tunnel setup failed: {e}")
            # Cleanup temp directory
            subprocess.run(["rm", "-rf", str(temp_dir)], check=False)
            return False
    
    def stop_local_tunnel(self):
        """Stop the local Cloudflare tunnel."""
        print("🛑 Stopping local Cloudflare tunnel...")
        
        try:
            subprocess.run(["pkill", "-f", "cloudflared"], check=False)
            print("✅ Local tunnel stopped")
        except:
            pass
    
    def validate_tunnel(self) -> bool:
        """Validate the tunnel is working."""
        print("🔍 Validating tunnel connectivity...")
        
        try:
            import requests
            
            # Test if we can reach the tunnel
            response = requests.get("https://observatory.nkllon.com/health", timeout=30)
            
            if response.status_code == 200:
                print("✅ Tunnel is working - Observatory accessible via Cloudflare")
                return True
            else:
                print(f"❌ Tunnel test failed: HTTP {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Tunnel validation failed: {e}")
            print("💡 Make sure Observatory is running on Vonnegut:8888")
            return False
    
    def setup(self) -> bool:
        """Execute tunnel setup."""
        print("🎯 Vonnegut Cloudflare Tunnel Setup")
        print("=" * 40)
        
        if not self.check_ssh_access():
            return False
        
        # Stop local tunnel first
        self.stop_local_tunnel()
        
        # Setup tunnel on Vonnegut
        if not self.setup_tunnel_on_vonnegut():
            return False
        
        # Validate tunnel
        if not self.validate_tunnel():
            print("⚠️ Tunnel deployed but validation failed")
            print("🔧 Ensure Observatory is running on Vonnegut:8888")
            return False
        
        print("\n🎉 Cloudflare tunnel successfully deployed to Vonnegut!")
        print("🌐 Observatory should be accessible at: https://observatory.nkllon.com")
        print("📊 Prometheus: https://prometheus.observatory.nkllon.com") 
        print("📈 Grafana: https://grafana.observatory.nkllon.com")
        
        return True

def main():
    """Main setup execution."""
    setup = VonnegutTunnelSetup()
    
    try:
        success = setup.setup()
        return success
        
    except Exception as e:
        print(f"\n❌ Setup failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)