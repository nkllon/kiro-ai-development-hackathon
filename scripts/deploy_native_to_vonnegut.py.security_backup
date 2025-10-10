#!/usr/bin/env python3
"""
Deploy Observatory Natively to Vonnegut
=======================================

Deploys Observatory as native Python processes on Vonnegut with containerized tunnel.
"""

import os
import sys
import subprocess
from pathlib import Path

class NativeVonnegutDeployer:
    def __init__(self):
        self.vonnegut_ip = "192.168.1.119"
        self.ssh_user = "lou"
        self.remote_path = "/home/lou/observatory"
        self.tunnel_credentials = Path.home() / ".cloudflared" / "d1e53e43-033f-4994-8f46-c83962ae3785.json"
    
    def deploy_native_observatory(self) -> bool:
        """Deploy Observatory as native Python process on Vonnegut."""
        print("🚀 Deploying native Observatory to Vonnegut...")
        
        deployment_script = f"""
cd {self.remote_path}

# Stop any existing processes
pkill -f "start_observatory" || true
pkill -f "python.*observatory" || true

# Set up Python environment
python3 -m venv venv || true
source venv/bin/activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Set environment variables
export REDIS_HOST="localhost"
export REDIS_PASSWORD="${os.getenv('REDIS_PASSWORD', 'beastmode2025')}"
export PROMETHEUS_URL="http://localhost:9090"

# Create data directories
mkdir -p observatory_data/{{metrics,dashboards,logs,config}}

# Start Observatory in background
nohup python3 start_observatory.py > observatory.log 2>&1 &

# Wait for startup
sleep 10

# Check if it's running
if pgrep -f "start_observatory"; then
    echo "✅ Observatory started successfully"
    echo "📊 Process info:"
    ps aux | grep -E "(start_observatory|python.*observatory)" | grep -v grep
    
    # Test local access
    curl -s http://localhost:8888/health | head -c 200 || echo "⚠️ Health check failed"
else
    echo "❌ Observatory failed to start"
    echo "📋 Log output:"
    tail -20 observatory.log
    exit 1
fi
"""
        
        try:
            result = subprocess.run([
                "ssh", f"{self.ssh_user}@{self.vonnegut_ip}",
                deployment_script
            ], text=True, capture_output=True)
            
            print("📋 Observatory deployment output:")
            print(result.stdout)
            
            if result.stderr:
                print("⚠️ Observatory deployment warnings:")
                print(result.stderr)
            
            return result.returncode == 0
            
        except Exception as e:
            print(f"❌ Observatory deployment failed: {e}")
            return False
    
    def deploy_tunnel_container(self) -> bool:
        """Deploy Cloudflare tunnel in Docker container on Vonnegut."""
        print("🌉 Deploying Cloudflare tunnel container to Vonnegut...")
        
        # Create tunnel configuration for Vonnegut
        tunnel_config = """tunnel: d1e53e43-033f-4994-8f46-c83962ae3785
credentials-file: /etc/cloudflared/credentials.json

ingress:
  - hostname: observatory.nkllon.com
    service: http://localhost:8888
    originRequest:
      httpHostHeader: localhost:8888
      noTLSVerify: false
      connectTimeout: 30s
      tlsTimeout: 10s
      tcpKeepAlive: 30s
      keepAliveConnections: 100
      keepAliveTimeout: 90s
  - hostname: prometheus.observatory.nkllon.com
    service: http://localhost:9090
    originRequest:
      httpHostHeader: localhost:9090
      noTLSVerify: false
  - hostname: grafana.observatory.nkllon.com
    service: http://localhost:3000
    originRequest:
      httpHostHeader: localhost:3000
      noTLSVerify: false
  - service: http_status:404
"""
        
        tunnel_script = f"""
cd {self.remote_path}

# Stop any existing tunnel
docker stop vonnegut-tunnel 2>/dev/null || true
docker rm vonnegut-tunnel 2>/dev/null || true

# Create tunnel config
cat > tunnel-config.yml << 'EOF'
{tunnel_config}
EOF

# Run tunnel container with host networking
docker run -d \\
  --name vonnegut-tunnel \\
  --restart unless-stopped \\
  --network host \\
  -v $(pwd)/tunnel-config.yml:/etc/cloudflared/config.yml:ro \\
  -v $(pwd)/tunnel-credentials.json:/etc/cloudflared/credentials.json:ro \\
  cloudflare/cloudflared:latest \\
  tunnel --config /etc/cloudflared/config.yml run

# Wait for startup
sleep 10

# Check tunnel status
if docker ps | grep vonnegut-tunnel; then
    echo "✅ Cloudflare tunnel started successfully"
    docker logs vonnegut-tunnel --tail=10
else
    echo "❌ Tunnel failed to start"
    docker logs vonnegut-tunnel
    exit 1
fi
"""
        
        try:
            result = subprocess.run([
                "ssh", f"{self.ssh_user}@{self.vonnegut_ip}",
                tunnel_script
            ], text=True, capture_output=True)
            
            print("📋 Tunnel deployment output:")
            print(result.stdout)
            
            if result.stderr:
                print("⚠️ Tunnel deployment warnings:")
                print(result.stderr)
            
            return result.returncode == 0
            
        except Exception as e:
            print(f"❌ Tunnel deployment failed: {e}")
            return False
    
    def validate_deployment(self) -> bool:
        """Validate the complete Vonnegut deployment."""
        print("🔍 Validating Vonnegut deployment...")
        
        # Test external access
        try:
            import requests
            response = requests.get("https://observatory.nkllon.com/health", timeout=30)
            
            if response.status_code == 200:
                print("✅ External access working")
                health_data = response.json()
                print(f"📊 Health status: {health_data.get('status', 'unknown')}")
                return True
            else:
                print(f"❌ External access failed: HTTP {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ External access test failed: {e}")
            return False
    
    def stop_local_services(self):
        """Stop local Observatory services."""
        print("🛑 Stopping local Observatory services...")
        
        # Stop local Observatory process
        try:
            subprocess.run(["pkill", "-f", "start_observatory"], check=False)
            print("✅ Local Observatory process stopped")
        except:
            pass
        
        # Stop local tunnel
        try:
            subprocess.run(["pkill", "-f", "cloudflared"], check=False)
            print("✅ Local Cloudflare tunnel stopped")
        except:
            pass
    
    def deploy(self) -> bool:
        """Execute complete native deployment to Vonnegut."""
        print("🎯 Native Observatory Vonnegut Deployment")
        print("=" * 50)
        
        # Stop local services first
        self.stop_local_services()
        
        # Deploy Observatory natively
        if not self.deploy_native_observatory():
            return False
        
        # Deploy tunnel in container
        if not self.deploy_tunnel_container():
            print("⚠️ Observatory deployed but tunnel failed")
            return False
        
        # Validate deployment
        if not self.validate_deployment():
            print("⚠️ Deployment completed but validation failed")
            return False
        
        print("\n🎉 Observatory successfully deployed to Vonnegut!")
        print("🌐 Access: https://observatory.nkllon.com")
        print("📊 Native Python process on Vonnegut")
        print("🌉 Containerized Cloudflare tunnel")
        
        return True

def main():
    """Main deployment execution."""
    deployer = NativeVonnegutDeployer()
    
    try:
        success = deployer.deploy()
        return success
        
    except Exception as e:
        print(f"\n❌ Deployment failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)