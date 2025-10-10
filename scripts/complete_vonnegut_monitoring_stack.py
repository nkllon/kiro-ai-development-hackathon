#!/usr/bin/env python3
"""
Complete Vonnegut Monitoring Stack Setup
=======================================

Sets up the complete monitoring stack:
1. Observatory (already running)
2. Prometheus (configured to scrape Observatory)
3. Grafana (configured with Prometheus data source)
4. Cloudflare tunnel (routing to all services)
"""

import subprocess
import yaml
import json
import time

def ssh_command(command: str) -> tuple[bool, str, str]:
    """Execute SSH command on Vonnegut."""
    try:
        result = subprocess.run([
            "ssh", "lou@192.168.1.119", command
        ], capture_output=True, text=True, timeout=120)
        
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)

def upload_file(local_path: str, remote_path: str) -> bool:
    """Upload file to Vonnegut."""
    try:
        subprocess.run([
            "scp", local_path, f"lou@192.168.1.119:{remote_path}"
        ], check=True)
        return True
    except Exception as e:
        print(f"❌ Failed to upload {local_path}: {e}")
        return False

def setup_prometheus():
    """Set up Prometheus to scrape Observatory."""
    print("📊 Setting up Prometheus...")
    
    # Create Prometheus config
    prometheus_config = {
        'global': {
            'scrape_interval': '15s',
            'evaluation_interval': '15s'
        },
        'scrape_configs': [
            {
                'job_name': 'prometheus',
                'static_configs': [{'targets': ['localhost:9090']}]
            },
            {
                'job_name': 'observatory',
                'static_configs': [{'targets': ['localhost:8888']}],
                'metrics_path': '/metrics',
                'scrape_interval': '10s'
            },
            {
                'job_name': 'redis',
                'static_configs': [{'targets': ['localhost:6379']}]
            }
        ]
    }
    
    # Write config to temp file
    with open("/tmp/prometheus.yml", 'w') as f:
        yaml.dump(prometheus_config, f, default_flow_style=False)
    
    # Upload to Vonnegut
    if not upload_file("/tmp/prometheus.yml", "/home/lou/observatory/prometheus.yml"):
        return False
    
    # Install and start Prometheus
    setup_commands = """
# Install Prometheus if not already installed
if ! command -v prometheus &> /dev/null; then
    sudo apt-get update
    sudo apt-get install -y prometheus
fi

# Stop existing Prometheus
sudo systemctl stop prometheus 2>/dev/null || true
pkill -f prometheus 2>/dev/null || true

# Create data directory
mkdir -p /home/lou/observatory/prometheus-data

# Start Prometheus with our config
cd /home/lou/observatory
nohup prometheus --config.file=prometheus.yml --storage.tsdb.path=./prometheus-data --web.listen-address=:9090 > prometheus.log 2>&1 &
echo "Prometheus started with PID: $!"
"""
    
    success, stdout, stderr = ssh_command(setup_commands)
    
    if success:
        print("✅ Prometheus started")
        print(f"📋 Output: {stdout}")
    else:
        print("❌ Failed to start Prometheus:")
        print(f"Error: {stderr}")
        return False
    
    # Wait and test
    time.sleep(10)
    success, stdout, stderr = ssh_command("curl -s http://localhost:9090/api/v1/status/config | head -1")
    
    if success:
        print("✅ Prometheus is responding")
        return True
    else:
        print("❌ Prometheus health check failed")
        return False

def setup_grafana():
    """Set up Grafana with Prometheus data source."""
    print("📈 Setting up Grafana...")
    
    # Install and start Grafana
    setup_commands = """
# Install Grafana if not already installed
if ! command -v grafana-server &> /dev/null; then
    sudo apt-get update
    sudo apt-get install -y software-properties-common
    sudo add-apt-repository "deb https://packages.grafana.com/oss/deb stable main"
    wget -q -O - https://packages.grafana.com/gpg.key | sudo apt-key add -
    sudo apt-get update
    sudo apt-get install -y grafana
fi

# Stop existing Grafana
sudo systemctl stop grafana-server 2>/dev/null || true
pkill -f grafana 2>/dev/null || true

# Create data directory
sudo mkdir -p /var/lib/grafana
sudo chown -R grafana:grafana /var/lib/grafana

# Start Grafana
sudo systemctl start grafana-server
sudo systemctl enable grafana-server

echo "Grafana started"
"""
    
    success, stdout, stderr = ssh_command(setup_commands)
    
    if success:
        print("✅ Grafana started")
        print(f"📋 Output: {stdout}")
    else:
        print("❌ Failed to start Grafana:")
        print(f"Error: {stderr}")
        return False
    
    # Wait for Grafana to start
    time.sleep(15)
    
    # Test Grafana
    success, stdout, stderr = ssh_command("curl -s http://localhost:3000/api/health")
    
    if success:
        print("✅ Grafana is responding")
        
        # Configure Prometheus data source
        print("🔗 Configuring Prometheus data source...")
        
        datasource_config = {
            "name": "Prometheus",
            "type": "prometheus",
            "url": "http://localhost:9090",
            "access": "proxy",
            "isDefault": True
        }
        
        # Add data source via API
        add_datasource_command = f"""
curl -X POST http://admin:admin@localhost:3000/api/datasources \\
  -H "Content-Type: application/json" \\
  -d '{json.dumps(datasource_config)}'
"""
        
        success, stdout, stderr = ssh_command(add_datasource_command)
        if success:
            print("✅ Prometheus data source configured")
        else:
            print("⚠️ Data source configuration may have failed (might already exist)")
        
        return True
    else:
        print("❌ Grafana health check failed")
        return False

def setup_tunnel():
    """Set up Cloudflare tunnel for all services."""
    print("☁️ Setting up Cloudflare tunnel...")
    
    # Create tunnel configuration
    tunnel_config = {
        'tunnel': 'd1e53e43-033f-4994-8f46-c83962ae3785',
        'credentials-file': '/home/lou/observatory/tunnel-credentials.json',
        'ingress': [
            {
                'hostname': 'observatory.niclon.com',
                'service': 'http://localhost:8888'
            },
            {
                'hostname': 'grafana.vonnegut.poe.com',
                'service': 'http://localhost:3000'
            },
            {
                'hostname': 'prometheus.vonnegut.poe.com',
                'service': 'http://localhost:9090'
            },
            {
                'service': 'http_status:404'
            }
        ]
    }
    
    # Write config to temp file
    with open("/tmp/cloudflared-config.yml", 'w') as f:
        yaml.dump(tunnel_config, f, default_flow_style=False)
    
    # Upload to Vonnegut
    if not upload_file("/tmp/cloudflared-config.yml", "/home/lou/observatory/cloudflared-config.yml"):
        return False
    
    # Start tunnel
    start_tunnel_command = """
cd /home/lou/observatory
# Stop any existing tunnel
pkill -f cloudflared 2>/dev/null || true
sleep 2

# Start new tunnel
nohup /usr/bin/cloudflared tunnel --config cloudflared-config.yml run > tunnel.log 2>&1 &
echo "Tunnel started with PID: $!"
"""
    
    success, stdout, stderr = ssh_command(start_tunnel_command)
    
    if success:
        print("✅ Tunnel started")
        print(f"📋 Output: {stdout}")
        return True
    else:
        print("❌ Failed to start tunnel:")
        print(f"Error: {stderr}")
        return False

def validate_stack():
    """Validate the complete monitoring stack."""
    print("🔍 Validating monitoring stack...")
    
    services = [
        ("Observatory", "curl -s http://localhost:8888/health"),
        ("Prometheus", "curl -s http://localhost:9090/api/v1/status/config | head -1"),
        ("Grafana", "curl -s http://localhost:3000/api/health"),
        ("Redis", "redis-cli -a beastmode2025 ping")
    ]
    
    all_healthy = True
    
    for service, test_cmd in services:
        success, stdout, stderr = ssh_command(test_cmd)
        if success and stdout.strip():
            print(f"✅ {service} is healthy")
        else:
            print(f"❌ {service} test failed")
            all_healthy = False
    
    # Test Prometheus scraping Observatory
    print("🔗 Testing Prometheus → Observatory integration...")
    success, stdout, stderr = ssh_command("curl -s 'http://localhost:9090/api/v1/query?query=up{job=\"observatory\"}' | grep -o '\"value\":\\[.*\\]'")
    
    if success and "1" in stdout:
        print("✅ Prometheus is successfully scraping Observatory")
    else:
        print("⚠️ Prometheus may not be scraping Observatory yet (check in a few minutes)")
    
    return all_healthy

def main():
    """Main setup process."""
    print("🚀 Setting up Complete Observatory Monitoring Stack on Vonnegut")
    print("=" * 70)
    
    # Check Observatory is running
    print("🔍 Checking Observatory status...")
    success, stdout, stderr = ssh_command("curl -s http://localhost:8888/health")
    if success:
        print("✅ Observatory is running")
    else:
        print("❌ Observatory is not running. Please start it first.")
        return False
    
    # Set up Prometheus
    if not setup_prometheus():
        print("❌ Prometheus setup failed")
        return False
    
    # Set up Grafana
    if not setup_grafana():
        print("❌ Grafana setup failed")
        return False
    
    # Set up tunnel
    if not setup_tunnel():
        print("⚠️ Tunnel setup failed, but services are running locally")
    
    # Validate everything
    validate_stack()
    
    print("\n🎉 Observatory Monitoring Stack Setup Complete!")
    print("=" * 50)
    print("🌐 External URLs (if tunnel is working):")
    print("   Observatory: https://observatory.niclon.com")
    print("   Grafana: https://grafana.vonnegut.poe.com (admin/admin)")
    print("   Prometheus: https://prometheus.vonnegut.poe.com")
    print("\n🏠 Local URLs (always available):")
    print("   Observatory: http://192.168.1.119:8888")
    print("   Grafana: http://192.168.1.119:3000 (admin/admin)")
    print("   Prometheus: http://192.168.1.119:9090")
    print("\n💡 Next steps:")
    print("1. Access Grafana and create Observatory dashboards")
    print("2. Import or create dashboards for Observatory metrics")
    print("3. Set up alerting rules in Prometheus")
    
    return True

if __name__ == "__main__":
    main()