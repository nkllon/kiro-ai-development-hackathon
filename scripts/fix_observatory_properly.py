#!/usr/bin/env python3
"""
Fix Observatory deployment based on actual validation results
Addresses the real issues found by the monitoring script
"""

import subprocess
import sys
import time

def run_ssh_command(command, description=""):
    """Run command via SSH on Vonnegut server"""
    ssh_command = f'ssh -o StrictHostKeyChecking=no lou@192.168.1.119 "{command}"'
    print(f"🔧 {description}")
    print(f"Running: {command}")
    
    try:
        result = subprocess.run(ssh_command, shell=True, capture_output=True, text=True, timeout=60)
        if result.stdout:
            print(f"✅ Output: {result.stdout.strip()}")
        if result.stderr:
            print(f"⚠️ Stderr: {result.stderr.strip()}")
        return result.returncode == 0, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        print(f"❌ Command timed out")
        return False, "", "Command timed out"
    except Exception as e:
        print(f"❌ Error: {e}")
        return False, "", str(e)

def fix_observatory_service():
    """Fix Observatory service to be accessible on port 8888"""
    print("🔧 Fixing Observatory service...")
    
    # Check what's actually running on port 8888
    run_ssh_command("netstat -tlnp | grep 8888", "Checking port 8888")
    run_ssh_command("ps aux | grep observatory", "Checking Observatory processes")
    
    # Kill any existing Observatory processes
    run_ssh_command("pkill -f observatory", "Stopping existing Observatory processes")
    time.sleep(3)
    
    # Start Observatory properly
    start_command = """
cd /home/lou/kiro-ai-development-hackathon
nohup python start_observatory_minimal.py > observatory.log 2>&1 &
echo "Observatory started"
"""
    
    run_ssh_command(start_command, "Starting Observatory")
    time.sleep(10)
    
    # Verify it's running
    run_ssh_command("netstat -tlnp | grep 8888", "Verifying port 8888")
    run_ssh_command("curl -s -o /dev/null -w '%{http_code}' http://localhost:8888/health", "Testing Observatory health")

def fix_prometheus_service():
    """Fix Prometheus to work properly"""
    print("\n🔧 Fixing Prometheus service...")
    
    # Stop any existing Prometheus
    run_ssh_command("docker stop observatory-prometheus 2>/dev/null || true", "Stopping Prometheus")
    run_ssh_command("docker rm observatory-prometheus 2>/dev/null || true", "Removing Prometheus")
    
    # Create simple Prometheus config
    config_cmd = """
cat > /tmp/prometheus.yml << 'EOF'
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'prometheus'
    static_configs:
      - targets: ['localhost:9090']
  - job_name: 'observatory'
    static_configs:
      - targets: ['localhost:8888']
    metrics_path: '/metrics'
EOF
"""
    
    run_ssh_command(config_cmd, "Creating Prometheus config")
    
    # Start Prometheus with working config
    prom_cmd = """docker run -d \\
  --name observatory-prometheus \\
  --network host \\
  -v /tmp/prometheus.yml:/etc/prometheus/prometheus.yml:ro \\
  -v prometheus-data:/prometheus \\
  prom/prometheus:latest \\
  --config.file=/etc/prometheus/prometheus.yml \\
  --storage.tsdb.path=/prometheus"""
    
    run_ssh_command(prom_cmd, "Starting Prometheus")
    time.sleep(10)
    
    # Test Prometheus
    run_ssh_command("curl -s -o /dev/null -w '%{http_code}' http://localhost:9090/", "Testing Prometheus")

def fix_grafana_service():
    """Fix Grafana with proper anonymous access"""
    print("\n🔧 Fixing Grafana service...")
    
    # Stop existing Grafana
    run_ssh_command("docker stop observatory-grafana 2>/dev/null || true", "Stopping Grafana")
    run_ssh_command("docker rm observatory-grafana 2>/dev/null || true", "Removing Grafana")
    
    # Start Grafana with proper config
    grafana_cmd = """docker run -d \\
  --name observatory-grafana \\
  --network host \\
  -v grafana-storage:/var/lib/grafana \\
  -e GF_AUTH_ANONYMOUS_ENABLED=true \\
  -e GF_AUTH_ANONYMOUS_ORG_ROLE=Viewer \\
  -e GF_SECURITY_ADMIN_PASSWORD=admin \\
  -e GF_SERVER_DOMAIN=grafana.observatory.nkllon.com \\
  -e GF_SERVER_ROOT_URL=https://grafana.observatory.nkllon.com/ \\
  grafana/grafana:latest"""
    
    run_ssh_command(grafana_cmd, "Starting Grafana")
    time.sleep(15)
    
    # Test Grafana
    run_ssh_command("curl -s -o /dev/null -w '%{http_code}' http://localhost:3000/api/health", "Testing Grafana")

def fix_tunnel_service():
    """Fix Cloudflare tunnel"""
    print("\n🔧 Fixing Cloudflare tunnel...")
    
    # Stop existing tunnel
    run_ssh_command("pkill -f cloudflared", "Stopping existing tunnel")
    time.sleep(3)
    
    # Create tunnel config
    tunnel_config = """
cat > /tmp/tunnel_config.yml << 'EOF'
tunnel: d1e53e43-033f-4994-8f46-c83962ae3785
credentials-file: /home/lou/.cloudflared/d1e53e43-033f-4994-8f46-c83962ae3785.json

ingress:
  - hostname: observatory.nkllon.com
    service: http://localhost:8888
  - hostname: prometheus.observatory.nkllon.com
    service: http://localhost:9090
  - hostname: grafana.observatory.nkllon.com
    service: http://localhost:3000
  - service: http_status:404
EOF

sudo cp /tmp/tunnel_config.yml /etc/cloudflared/config.yml
sudo chown root:root /etc/cloudflared/config.yml
"""
    
    run_ssh_command(tunnel_config, "Creating tunnel config")
    
    # Start tunnel
    start_tunnel = "nohup cloudflared tunnel --config /etc/cloudflared/config.yml run > /tmp/tunnel.log 2>&1 &"
    run_ssh_command(start_tunnel, "Starting tunnel")
    time.sleep(5)
    
    # Verify tunnel
    run_ssh_command("pgrep -f cloudflared", "Checking tunnel process")

def validate_fixes():
    """Validate that fixes worked"""
    print("\n📊 Validating fixes...")
    
    services = [
        ("Observatory", "http://localhost:8888/health"),
        ("Prometheus", "http://localhost:9090/"),
        ("Grafana", "http://localhost:3000/api/health")
    ]
    
    for name, url in services:
        run_ssh_command(f"curl -s -o /dev/null -w '{name}: %{{http_code}}\\n' {url}", f"Testing {name}")
    
    # Check processes
    run_ssh_command("pgrep -f cloudflared", "Tunnel process")
    run_ssh_command("docker ps | grep observatory", "Container status")

def main():
    print("🔧 Observatory Proper Fix - Based on Validation Results")
    print("=" * 60)
    print("Fixing the actual issues found by the monitoring script:")
    print("• Observatory not accessible locally (connection refused)")
    print("• No tunnel process running")
    print("• Prometheus 502 errors")
    print("• Grafana configuration issues")
    print()
    
    try:
        fix_observatory_service()
        fix_prometheus_service()
        fix_grafana_service()
        fix_tunnel_service()
        validate_fixes()
        
        print("\n✅ Observatory fixes completed!")
        print("\n🌐 Services should now be accessible:")
        print("   Observatory: https://observatory.nkllon.com")
        print("   Prometheus: https://prometheus.observatory.nkllon.com")
        print("   Grafana: https://grafana.observatory.nkllon.com")
        print("\n📝 Run the validation script to confirm:")
        print("   python scripts/validate_observatory_deployment.py")
        
    except Exception as e:
        print(f"\n❌ Error during fixes: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())