#!/usr/bin/env python3
"""
Deploy Observatory Containers to Remote Servers

This script deploys the updated Observatory containers (with fixed Docker volumes)
to Vonnegut and Poe servers after the January 27, 2025 incident resolution.
"""

import os
import sys
import subprocess
import json
import time
from datetime import datetime
from pathlib import Path


def run_command(cmd, check=True, cwd=None):
    """Run a shell command and return the result."""
    print(f"🔧 Running: {cmd}")
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True, cwd=cwd)
    
    if check and result.returncode != 0:
        print(f"❌ Command failed: {cmd}")
        print(f"Error: {result.stderr}")
        return None
    
    return result


def check_remote_connectivity():
    """Check connectivity to remote servers."""
    print("🔍 Checking remote server connectivity...")
    
    servers = {
        "vonnegut": "192.168.1.119",
        "poe": "192.168.1.120"  # Assuming Poe is .120 based on pattern
    }
    
    connectivity = {}
    
    for server_name, ip in servers.items():
        print(f"   Testing {server_name} ({ip})...")
        
        # Test ping
        result = run_command(f"ping -c 1 -W 3000 {ip}", check=False)
        ping_ok = result and result.returncode == 0
        
        # Test SSH (if available)
        ssh_ok = False
        if ping_ok:
            result = run_command(f"ssh -o ConnectTimeout=5 -o BatchMode=yes {ip} 'echo test' 2>/dev/null", check=False)
            ssh_ok = result and result.returncode == 0
        
        connectivity[server_name] = {
            "ip": ip,
            "ping": ping_ok,
            "ssh": ssh_ok,
            "available": ping_ok
        }
        
        status = "✅" if ping_ok else "❌"
        ssh_status = "✅" if ssh_ok else "❌" if ping_ok else "N/A"
        print(f"     Ping: {status}, SSH: {ssh_status}")
    
    return connectivity


def build_containers():
    """Build the updated containers locally."""
    print("🏗️  Building updated containers...")
    
    # Build observatory container
    print("📦 Building beast-mode-observatory...")
    result = run_command(
        "docker build -t beast-mode-observatory:latest -f deployment/observatory/Dockerfile .",
        cwd="."
    )
    
    if not result:
        return False
    
    # Build engagement manager
    print("📦 Building beast-mode-engagement...")
    result = run_command(
        "docker build -t beast-mode-engagement:latest -f deployment/engagement/Dockerfile .",
        cwd="."
    )
    
    if not result:
        return False
    
    print("✅ Containers built successfully")
    return True


def export_containers():
    """Export containers to tar files for deployment."""
    print("📦 Exporting containers for deployment...")
    
    export_dir = f"container-exports-{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    os.makedirs(export_dir, exist_ok=True)
    
    containers = [
        "beast-mode-observatory:latest",
        "beast-mode-engagement:latest"
    ]
    
    exported_files = []
    
    for container in containers:
        container_name = container.replace(":", "_").replace("/", "_")
        export_file = f"{export_dir}/{container_name}.tar"
        
        print(f"📤 Exporting {container}...")
        result = run_command(f"docker save -o {export_file} {container}")
        
        if result:
            exported_files.append(export_file)
            file_size = os.path.getsize(export_file) / (1024 * 1024)  # MB
            print(f"   Exported: {export_file} ({file_size:.1f} MB)")
        else:
            print(f"❌ Failed to export {container}")
            return None
    
    return export_dir, exported_files


def create_deployment_package():
    """Create a complete deployment package."""
    print("📋 Creating deployment package...")
    
    package_dir = f"observatory-deployment-{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    os.makedirs(package_dir, exist_ok=True)
    
    # Copy essential files
    files_to_copy = [
        "deployment/observatory/docker-compose.yml",
        "deployment/observatory/prometheus.yml",
        "deployment/observatory/cloudflared-config.yml",
        "deployment-auditor-config.yml"
    ]
    
    for file_path in files_to_copy:
        if os.path.exists(file_path):
            dest_path = os.path.join(package_dir, os.path.basename(file_path))
            run_command(f"cp {file_path} {dest_path}")
            print(f"   Copied: {file_path}")
    
    # Copy grafana config directory if it exists
    if os.path.exists("deployment/observatory/grafana-config"):
        run_command(f"cp -r deployment/observatory/grafana-config {package_dir}/")
        print(f"   Copied: grafana-config/")
    
    # Create deployment script
    deploy_script = f"""#!/bin/bash
# Observatory Deployment Script - Generated {datetime.now()}
# Deploy updated containers with fixed Docker volumes

set -e

echo "🚀 Deploying Observatory with Fixed Docker Volumes"
echo "=================================================="

# Stop existing containers
echo "🛑 Stopping existing containers..."
docker-compose down || true

# Load new container images
echo "📦 Loading updated container images..."
docker load -i beast-mode-observatory_latest.tar
docker load -i beast-mode-engagement_latest.tar

# Start services with new configuration
echo "🚀 Starting updated services..."
docker-compose up -d

# Wait for services to be ready
echo "⏳ Waiting for services to start..."
sleep 30

# Health checks
echo "🏥 Checking service health..."
docker ps --filter name=observatory

echo "✅ Deployment completed!"
echo "🌐 Services should be available at:"
echo "   Observatory: http://localhost:8888"
echo "   Grafana: http://localhost:3000"
echo "   Prometheus: http://localhost:9090"
"""
    
    with open(f"{package_dir}/deploy.sh", 'w') as f:
        f.write(deploy_script)
    
    os.chmod(f"{package_dir}/deploy.sh", 0o755)
    
    print(f"✅ Deployment package created: {package_dir}/")
    return package_dir


def deploy_to_server(server_name, server_ip, package_dir, container_exports):
    """Deploy to a specific server."""
    print(f"🚀 Deploying to {server_name} ({server_ip})...")
    
    # Create remote deployment directory
    remote_dir = f"/tmp/observatory-deploy-{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    print(f"📁 Creating remote directory: {remote_dir}")
    result = run_command(f"ssh {server_ip} 'mkdir -p {remote_dir}'", check=False)
    
    if not result or result.returncode != 0:
        print(f"❌ Cannot create directory on {server_name} - SSH access required")
        return False
    
    # Copy deployment package
    print(f"📤 Copying deployment package...")
    result = run_command(f"scp -r {package_dir}/* {server_ip}:{remote_dir}/", check=False)
    
    if not result or result.returncode != 0:
        print(f"❌ Cannot copy files to {server_name}")
        return False
    
    # Copy container exports
    print(f"📤 Copying container images...")
    for export_file in container_exports:
        result = run_command(f"scp {export_file} {server_ip}:{remote_dir}/", check=False)
        if not result or result.returncode != 0:
            print(f"❌ Cannot copy {export_file} to {server_name}")
            return False
    
    # Execute deployment
    print(f"🚀 Executing deployment on {server_name}...")
    result = run_command(f"ssh {server_ip} 'cd {remote_dir} && ./deploy.sh'", check=False)
    
    if result and result.returncode == 0:
        print(f"✅ Deployment to {server_name} completed successfully")
        print(f"📋 Remote deployment directory: {server_ip}:{remote_dir}")
        return True
    else:
        print(f"❌ Deployment to {server_name} failed")
        if result and result.stderr:
            print(f"Error: {result.stderr}")
        return False


def deploy_via_redis_workload(server_name, server_ip):
    """Deploy using Redis workload system (alternative method)."""
    print(f"🔄 Attempting Redis workload deployment to {server_name}...")
    
    try:
        # Add src to path for imports
        sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
        from security.secure_credentials import get_redis_password
        import redis
        
        # Connect to Redis on Vonnegut
        redis_client = redis.Redis(
            host="192.168.1.119",
            port=6379,
            password=get_redis_password(),
            decode_responses=True
        )
        
        # Test connection
        redis_client.ping()
        print("✅ Redis connection established")
        
        # Send deployment workload
        workload_request = {
            "type": "container_deployment",
            "workload_id": f"observatory-deploy-{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "sender": "observatory-deployer",
            "timestamp": datetime.now().isoformat(),
            "task": {
                "description": f"Deploy updated Observatory containers to {server_name}",
                "action": "pull_and_restart_containers",
                "containers": [
                    "beast-mode-observatory:latest",
                    "beast-mode-engagement:latest"
                ],
                "compose_file": "deployment/observatory/docker-compose.yml",
                "priority": "high"
            }
        }
        
        print(f"📤 Sending deployment workload via Redis...")
        redis_client.publish("docker_workloads", json.dumps(workload_request))
        
        print(f"✅ Deployment workload sent to {server_name}")
        print(f"   Monitor with: redis-cli -h 192.168.1.119 -a [password] monitor")
        
        redis_client.close()
        return True
        
    except Exception as e:
        print(f"❌ Redis workload deployment failed: {e}")
        return False


def main():
    """Main deployment function."""
    print("🚀 Observatory Remote Deployment")
    print("=" * 40)
    print("Deploying containers with fixed Docker volumes to remote servers")
    print()
    
    # Check remote connectivity
    connectivity = check_remote_connectivity()
    
    available_servers = [name for name, info in connectivity.items() if info["available"]]
    
    if not available_servers:
        print("❌ No remote servers available for deployment")
        print("   Servers checked:")
        for name, info in connectivity.items():
            print(f"     {name} ({info['ip']}): {'Available' if info['available'] else 'Unavailable'}")
        sys.exit(1)
    
    print(f"✅ Available servers: {', '.join(available_servers)}")
    
    # Choose deployment method
    print("\n🔧 Deployment Methods:")
    print("1. SSH deployment (requires SSH access)")
    print("2. Redis workload deployment (uses existing Redis coordination)")
    print("3. Manual deployment (generate package only)")
    
    method = input("\nChoose deployment method (1-3): ").strip()
    
    if method == "1":
        # SSH deployment
        ssh_servers = [name for name, info in connectivity.items() if info["ssh"]]
        
        if not ssh_servers:
            print("❌ No servers with SSH access available")
            print("   Try method 2 (Redis workload) or 3 (manual)")
            sys.exit(1)
        
        # Build and export containers
        if not build_containers():
            sys.exit(1)
        
        export_dir, exported_files = export_containers()
        if not export_dir:
            sys.exit(1)
        
        # Create deployment package
        package_dir = create_deployment_package()
        
        # Deploy to each available server
        for server_name in ssh_servers:
            server_ip = connectivity[server_name]["ip"]
            success = deploy_to_server(server_name, server_ip, package_dir, exported_files)
            
            if success:
                print(f"✅ {server_name} deployment completed")
            else:
                print(f"❌ {server_name} deployment failed")
    
    elif method == "2":
        # Redis workload deployment
        print("🔄 Using Redis workload deployment...")
        
        for server_name in available_servers:
            server_ip = connectivity[server_name]["ip"]
            success = deploy_via_redis_workload(server_name, server_ip)
            
            if success:
                print(f"✅ {server_name} workload sent")
            else:
                print(f"❌ {server_name} workload failed")
    
    elif method == "3":
        # Manual deployment
        print("📦 Creating manual deployment package...")
        
        # Build and export containers
        if not build_containers():
            sys.exit(1)
        
        export_dir, exported_files = export_containers()
        if not export_dir:
            sys.exit(1)
        
        # Create deployment package
        package_dir = create_deployment_package()
        
        print(f"\n📋 Manual Deployment Instructions:")
        print(f"=" * 40)
        print(f"1. Copy deployment package to servers:")
        for server_name in available_servers:
            server_ip = connectivity[server_name]["ip"]
            print(f"   scp -r {package_dir}/* {server_ip}:/tmp/observatory-deploy/")
            print(f"   scp {export_dir}/*.tar {server_ip}:/tmp/observatory-deploy/")
        
        print(f"\n2. Execute deployment on each server:")
        for server_name in available_servers:
            server_ip = connectivity[server_name]["ip"]
            print(f"   ssh {server_ip}")
            print(f"   cd /tmp/observatory-deploy")
            print(f"   ./deploy.sh")
        
        print(f"\n3. Verify deployment:")
        print(f"   Check containers: docker ps --filter name=observatory")
        print(f"   Check health: curl http://localhost:8888/health")
        
    else:
        print("❌ Invalid choice")
        sys.exit(1)
    
    print(f"\n🎉 Deployment process completed!")
    print(f"📋 Next steps:")
    print(f"   • Verify services are running on remote servers")
    print(f"   • Check tunnel connectivity")
    print(f"   • Monitor logs for any issues")
    print(f"   • Run deployment auditor to verify governance compliance")


if __name__ == "__main__":
    main()