#!/usr/bin/env python3
"""
Observatory Deployment Script
Handles containerized deployment with zero-downtime transition.
"""

import os
import sys
import subprocess
import time
import requests
from pathlib import Path

class ObservatoryDeployer:
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.cloudflared_config = Path.home() / '.cloudflared'
        
    def check_prerequisites(self):
        """Check if Docker and required files exist."""
        print("🔍 Checking prerequisites...")
        
        # Check Docker
        try:
            subprocess.run(['docker', '--version'], check=True, capture_output=True)
            subprocess.run(['docker-compose', '--version'], check=True, capture_output=True)
            print("✅ Docker and Docker Compose are installed")
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("❌ Docker or Docker Compose not found. Please install Docker Desktop.")
            return False
        
        # Check cloudflared config
        if not (self.cloudflared_config / 'config.yml').exists():
            print("❌ Cloudflared config not found at ~/.cloudflared/config.yml")
            return False
        
        if not (self.cloudflared_config / 'd1e53e43-033f-4994-8f46-c83962ae3785.json').exists():
            print("❌ Cloudflared credentials not found")
            return False
        
        print("✅ Cloudflared configuration found")
        return True
    
    def stop_existing_processes(self):
        """Stop existing Observatory and cloudflared processes."""
        print("🛑 Stopping existing processes...")
        
        # Find and stop processes
        try:
            # Stop cloudflared
            result = subprocess.run(['pkill', '-f', 'cloudflared tunnel'], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                print("✅ Stopped existing cloudflared process")
            
            # Stop Observatory (look for Python process on port 8888)
            result = subprocess.run(['lsof', '-ti:8888'], capture_output=True, text=True)
            if result.stdout.strip():
                pids = result.stdout.strip().split('\n')
                for pid in pids:
                    subprocess.run(['kill', pid], capture_output=True)
                print("✅ Stopped existing Observatory process")
            
            # Wait a moment for processes to stop
            time.sleep(2)
            
        except Exception as e:
            print(f"⚠️  Warning: Could not stop some processes: {e}")
    
    def create_directories(self):
        """Create necessary directories for Docker volumes."""
        print("📁 Creating directories...")
        
        dirs = ['logs', 'data']
        for dir_name in dirs:
            dir_path = self.project_root / dir_name
            dir_path.mkdir(exist_ok=True)
            print(f"✅ Created {dir_name}/ directory")
    
    def build_and_start_container(self):
        """Build and start the Observatory container."""
        print("🐳 Building and starting Observatory container...")
        
        os.chdir(self.project_root)
        
        # Build the container
        result = subprocess.run(['docker-compose', 'build'], capture_output=True, text=True)
        if result.returncode != 0:
            print(f"❌ Docker build failed: {result.stderr}")
            return False
        
        print("✅ Container built successfully")
        
        # Start the container
        result = subprocess.run(['docker-compose', 'up', '-d'], capture_output=True, text=True)
        if result.returncode != 0:
            print(f"❌ Container start failed: {result.stderr}")
            return False
        
        print("✅ Container started successfully")
        return True
    
    def wait_for_health_check(self, max_wait=60):
        """Wait for Observatory to be healthy."""
        print("⏳ Waiting for Observatory to be healthy...")
        
        start_time = time.time()
        while time.time() - start_time < max_wait:
            try:
                response = requests.get('http://localhost:8888/health', timeout=5)
                if response.status_code == 200:
                    print("✅ Observatory is healthy!")
                    return True
            except requests.RequestException:
                pass
            
            print("⏳ Still waiting...")
            time.sleep(5)
        
        print("❌ Observatory failed to become healthy within timeout")
        return False
    
    def verify_tunnel_connection(self):
        """Verify the Cloudflare tunnel is working."""
        print("🌐 Verifying tunnel connection...")
        
        try:
            # Test the public URL
            response = requests.get('https://observatory.nkllon.com/', timeout=10)
            if response.status_code == 200:
                print("✅ Public URL is working: https://observatory.nkllon.com/")
                return True
            else:
                print(f"⚠️  Public URL returned status {response.status_code}")
        except requests.RequestException as e:
            print(f"⚠️  Could not reach public URL: {e}")
        
        return False
    
    def show_status(self):
        """Show deployment status and useful commands."""
        print("\n" + "="*60)
        print("🎉 OBSERVATORY DEPLOYMENT COMPLETE!")
        print("="*60)
        
        print("\n📊 Status:")
        print("  • Observatory: https://observatory.nkllon.com/")
        print("  • Local: http://localhost:8888/")
        print("  • Container: observatory")
        
        print("\n🔧 Useful Commands:")
        print("  • View logs: docker-compose logs -f")
        print("  • Restart: docker-compose restart")
        print("  • Stop: docker-compose down")
        print("  • Rebuild: docker-compose build && docker-compose up -d")
        
        print("\n📁 Persistent Data:")
        print("  • Logs: ./logs/")
        print("  • Data: ./data/")
        print("  • Config: ~/.cloudflared/ (mounted read-only)")
        
        print("\n🚀 Your Observatory is now running in Docker!")
        print("   It will automatically restart if it crashes or if you reboot.")
    
    def deploy(self):
        """Main deployment workflow."""
        print("🚀 Starting Observatory Deployment")
        print("="*50)
        
        if not self.check_prerequisites():
            sys.exit(1)
        
        self.stop_existing_processes()
        self.create_directories()
        
        if not self.build_and_start_container():
            sys.exit(1)
        
        if not self.wait_for_health_check():
            print("❌ Deployment failed - Observatory not healthy")
            print("🔍 Check logs with: docker-compose logs")
            sys.exit(1)
        
        # Give tunnel a moment to connect
        time.sleep(10)
        self.verify_tunnel_connection()
        
        self.show_status()

def main():
    deployer = ObservatoryDeployer()
    deployer.deploy()

if __name__ == "__main__":
    main()