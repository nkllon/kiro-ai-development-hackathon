#!/usr/bin/env python3
"""
Setup Docker and Deploy Observatory to Vonnegut
==============================================

Ensures Docker is running on Vonnegut and deploys the containerized Observatory stack.
"""

import os
import sys
import subprocess
import time
from pathlib import Path

class VonnegutDockerSetup:
    def __init__(self):
        self.vonnegut_ip = "192.168.1.119"
        self.ssh_user = "lou"
        self.remote_path = "/home/lou/observatory"
        
    def setup_docker_on_vonnegut(self) -> bool:
        """Setup and start Docker on Vonnegut."""
        print("🐳 Setting up Docker on Vonnegut...")
        
        docker_setup_script = f"""
# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "Installing Docker..."
    
    # Update package index
    sudo apt-get update
    
    # Install prerequisites
    sudo apt-get install -y apt-transport-https ca-certificates curl gnupg lsb-release
    
    # Add Docker's official GPG key
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
    
    # Set up stable repository
    echo "deb [arch=amd64 signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
    
    # Install Docker Engine
    sudo apt-get update
    sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin
    
    # Add user to docker group
    sudo usermod -aG docker $USER
    
    echo "✅ Docker installed"
else
    echo "✅ Docker already installed"
fi

# Start Docker service
echo "🚀 Starting Docker service..."
sudo systemctl start docker
sudo systemctl enable docker

# Wait for Docker to be ready
sleep 5

# Check Docker status
echo "🔍 Checking Docker status..."
sudo systemctl status docker --no-pager -l

# Test Docker
echo "🧪 Testing Docker..."
sudo docker run --rm hello-world

# Install docker-compose if not available
if ! command -v docker-compose &> /dev/null; then
    echo "Installing docker-compose..."
    sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    sudo chmod +x /usr/local/bin/docker-compose
    echo "✅ docker-compose installed"
else
    echo "✅ docker-compose already available"
fi

# Check docker-compose version
docker-compose --version

echo "✅ Docker setup complete!"
"""
        
        try:
            result = subprocess.run([
                "ssh", f"{self.ssh_user}@{self.vonnegut_ip}",
                docker_setup_script
            ], text=True, capture_output=True, timeout=300)
            
            print("📋 Docker setup output:")
            print(result.stdout)
            
            if result.stderr:
                print("⚠️ Docker setup warnings:")
                print(result.stderr)
            
            return result.returncode == 0
            
        except Exception as e:
            print(f"❌ Docker setup failed: {e}")
            return False
    
    def deploy_observatory_containers(self) -> bool:
        """Deploy Observatory containers on Vonnegut."""
        print("🚀 Deploying Observatory containers...")
        
        deployment_script = f"""
cd {self.remote_path}

# Set environment variables
export REDIS_PASSWORD="${os.getenv('REDIS_PASSWORD', 'beastmode2025')}"

# Make sure we're in the right directory
pwd
ls -la

# Stop any existing containers
echo "🛑 Stopping existing containers..."
sudo docker-compose down --remove-orphans 2>/dev/null || true
sudo docker container prune -f 2>/dev/null || true

# Build and start services
echo "🏗️ Building and starting containers..."
sudo docker-compose up -d --build

# Wait for services to start
echo "⏳ Waiting for services to start..."
sleep 60

# Check container status
echo "🏥 Checking container status..."
sudo docker-compose ps

# Check individual container logs
echo "📊 Container logs:"
echo "=== Observatory App ==="
sudo docker logs observatory-app --tail=10 2>/dev/null || echo "Observatory app not running"

echo "=== Prometheus ==="
sudo docker logs observatory-prometheus --tail=10 2>/dev/null || echo "Prometheus not running"

echo "=== Grafana ==="
sudo docker logs observatory-grafana --tail=10 2>/dev/null || echo "Grafana not running"

echo "=== Redis ==="
sudo docker logs observatory-redis --tail=10 2>/dev/null || echo "Redis not running"

echo "=== Tunnel ==="
sudo docker logs observatory-tunnel --tail=10 2>/dev/null || echo "Tunnel not running"

# Check port status
echo ""
echo "🔌 Port status:"
netstat -tlnp | grep -E "(8888|9090|3000|6379)" || echo "No observatory ports listening"

# Test local connectivity
echo ""
echo "🧪 Testing local connectivity:"
curl -s -o /dev/null -w "Observatory: %{http_code}\\n" http://localhost:8888/health || echo "Observatory: FAILED"
curl -s -o /dev/null -w "Prometheus: %{http_code}\\n" http://localhost:9090/-/healthy || echo "Prometheus: FAILED"
curl -s -o /dev/null -w "Grafana: %{http_code}\\n" http://localhost:3000/api/health || echo "Grafana: FAILED"

echo ""
echo "✅ Container deployment complete!"
"""
        
        try:
            result = subprocess.run([
                "ssh", f"{self.ssh_user}@{self.vonnegut_ip}",
                deployment_script
            ], text=True, capture_output=True, timeout=600)
            
            print("📋 Deployment output:")
            print(result.stdout)
            
            if result.stderr:
                print("⚠️ Deployment warnings:")
                print(result.stderr)
            
            return result.returncode == 0
            
        except Exception as e:
            print(f"❌ Container deployment failed: {e}")
            return False
    
    def validate_services(self) -> bool:
        """Validate that services are running properly."""
        print("🔍 Validating Observatory services...")
        
        validation_script = f"""
cd {self.remote_path}

echo "=== Container Status ==="
sudo docker-compose ps

echo ""
echo "=== Service Health ==="
# Test each service
curl -s -f http://localhost:8888/health && echo "✅ Observatory: Healthy" || echo "❌ Observatory: Unhealthy"
curl -s -f http://localhost:9090/-/healthy && echo "✅ Prometheus: Healthy" || echo "❌ Prometheus: Unhealthy"
curl -s -f http://localhost:3000/api/health && echo "✅ Grafana: Healthy" || echo "❌ Grafana: Unhealthy"

echo ""
echo "=== Network Connectivity ==="
# Test container-to-container networking
sudo docker exec observatory-prometheus wget -q --spider http://observatory-app:8888/health && echo "✅ Prometheus -> Observatory: OK" || echo "❌ Prometheus -> Observatory: FAILED"
sudo docker exec observatory-grafana wget -q --spider http://observatory-prometheus:9090/-/healthy && echo "✅ Grafana -> Prometheus: OK" || echo "❌ Grafana -> Prometheus: FAILED"

echo ""
echo "=== Prometheus Targets ==="
curl -s http://localhost:9090/api/v1/targets | python3 -c '
import sys, json
try:
    data = json.load(sys.stdin)
    targets = data.get("data", {}).get("activeTargets", [])
    for target in targets:
        job = target.get("labels", {}).get("job", "unknown")
        health = target.get("health", "unknown")
        print(job + ": " + health)
except:
    print("Could not parse Prometheus targets")
'

echo ""
echo "=== Recent Container Logs ==="
echo "Observatory (last 3 lines):"
sudo docker logs observatory-app --tail=3 2>/dev/null || echo "No logs"

echo "Prometheus (last 3 lines):"
sudo docker logs observatory-prometheus --tail=3 2>/dev/null || echo "No logs"
"""
        
        try:
            result = subprocess.run([
                "ssh", f"{self.ssh_user}@{self.vonnegut_ip}",
                validation_script
            ], text=True, capture_output=True, timeout=120)
            
            print("📋 Validation results:")
            print(result.stdout)
            
            if result.stderr:
                print("⚠️ Validation warnings:")
                print(result.stderr)
            
            # Check for success indicators
            success_indicators = [
                "Observatory: Healthy",
                "Prometheus: Healthy",
                "Grafana: Healthy"
            ]
            
            success_count = sum(1 for indicator in success_indicators if indicator in result.stdout)
            
            if success_count >= 2:
                print(f"✅ Validation passed ({success_count}/3 services healthy)")
                return True
            else:
                print(f"❌ Validation failed ({success_count}/3 services healthy)")
                return False
            
        except Exception as e:
            print(f"❌ Validation failed: {e}")
            return False
    
    def setup_and_deploy(self) -> bool:
        """Complete setup and deployment process."""
        print("🎯 Vonnegut Docker Setup and Observatory Deployment")
        print("=" * 60)
        
        # Setup Docker
        if not self.setup_docker_on_vonnegut():
            print("❌ Docker setup failed")
            return False
        
        # Deploy containers
        if not self.deploy_observatory_containers():
            print("❌ Container deployment failed")
            return False
        
        # Validate services
        if not self.validate_services():
            print("⚠️ Services deployed but validation failed")
            print("🔧 Check container logs for specific issues")
            return False
        
        print("\n🎉 Observatory successfully deployed on Vonnegut!")
        print("🌐 Observatory: https://observatory.niclon.com")
        print("📊 Prometheus: https://prometheus.observatory.niclon.com")
        print("📈 Grafana: https://grafana.observatory.niclon.com")
        print("\n🔧 Service Management:")
        print(f"  SSH to Vonnegut: ssh {self.ssh_user}@{self.vonnegut_ip}")
        print(f"  Check status: cd {self.remote_path} && sudo docker-compose ps")
        print(f"  View logs: cd {self.remote_path} && sudo docker-compose logs")
        print(f"  Restart: cd {self.remote_path} && sudo docker-compose restart")
        
        return True

def main():
    """Main execution."""
    setup = VonnegutDockerSetup()
    
    try:
        success = setup.setup_and_deploy()
        return success
        
    except Exception as e:
        print(f"\n❌ Setup and deployment failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)