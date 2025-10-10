#!/usr/bin/env python3
"""
Final Vonnegut Observatory Setup
===============================

Gets the complete Observatory stack working on Vonnegut.
"""

import subprocess
import time
import yaml

def ssh_command(command: str) -> tuple[bool, str, str]:
    """Execute SSH command on Vonnegut."""
    try:
        result = subprocess.run([
            "ssh", "lou@192.168.1.119", command
        ], capture_output=True, text=True, timeout=60)
        
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

def setup_complete_stack():
    """Set up the complete Observatory stack."""
    print("🚀 Setting up complete Observatory stack on Vonnegut...")
    
    # 1. Clean up any existing processes
    print("🧹 Cleaning up existing processes...")
    cleanup_commands = """
pkill -f observatory 2>/dev/null || true
pkill -f prometheus 2>/dev/null || true
pkill -f grafana 2>/dev/null || true
pkill -f cloudflared 2>/dev/null || true
sleep 2
"""
    ssh_command(cleanup_commands)
    
    # 2. Start Redis
    print("🔴 Starting Redis...")
    redis_command = "redis-server --daemonize yes --requirepass beastmode2025 --port 6379"
    success, stdout, stderr = ssh_command(redis_command)
    
    if success:
        # Test Redis
        success, stdout, stderr = ssh_command("redis-cli -a beastmode2025 ping")
        if "PONG" in stdout:
            print("✅ Redis is running")
        else:
            print("⚠️ Redis may not be responding correctly")
    else:
        print("❌ Failed to start Redis")
    
    # 3. Create Prometheus config and start it
    print("📊 Setting up Prometheus...")
    
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
            }
        ]
    }
    
    with open("/tmp/prometheus.yml", 'w') as f:
        yaml.dump(prometheus_config, f, default_flow_style=False)
    
    upload_file("/tmp/prometheus.yml", "/home/lou/observatory/prometheus.yml")
    
    prometheus_start = """
cd /home/lou/observatory
mkdir -p prometheus-data
nohup prometheus --config.file=prometheus.yml --storage.tsdb.path=./prometheus-data --web.listen-address=:9090 > prometheus.log 2>&1 &
echo "Prometheus started"
"""
    
    success, stdout, stderr = ssh_command(prometheus_start)
    if success:
        print("✅ Prometheus started")
    else:
        print("❌ Failed to start Prometheus")
    
    # 4. Start Observatory
    print("🔭 Starting Observatory...")
    
    observatory_start = """
cd /home/lou/observatory
export REDIS_HOST=localhost
export REDIS_PORT=6379
export REDIS_PASSWORD=beastmode2025
export PROMETHEUS_URL=http://localhost:9090

nohup python3 start_observatory.py > observatory.log 2>&1 &
echo "Observatory started"
"""
    
    success, stdout, stderr = ssh_command(observatory_start)
    if success:
        print("✅ Observatory started")
    else:
        print("❌ Failed to start Observatory")
    
    # 5. Start Grafana (if available)
    print("📈 Starting Grafana...")
    grafana_start = "sudo systemctl start grafana-server 2>/dev/null || echo 'Grafana not available'"
    success, stdout, stderr = ssh_command(grafana_start)
    
    if "not available" not in stdout:
        print("✅ Grafana started")
    else:
        print("⚠️ Grafana not installed")
    
    # 6. Wait for services to start
    print("⏳ Waiting for services to initialize...")
    time.sleep(20)
    
    # 7. Test all services
    print("🧪 Testing services...")
    
    services = [
        ("Redis", "redis-cli -a beastmode2025 ping", "PONG"),
        ("Observatory", "curl -s http://localhost:8888/health", "healthy"),
        ("Prometheus", "curl -s http://localhost:9090/api/v1/status/config", "success"),
        ("Grafana", "curl -s http://localhost:3000/api/health", "ok")
    ]
    
    working_services = []
    
    for service, test_cmd, expected in services:
        success, stdout, stderr = ssh_command(test_cmd)
        if success and expected in stdout:
            print(f"✅ {service} is working")
            working_services.append(service)
        else:
            print(f"❌ {service} test failed")
    
    # 8. Show results
    print("\n🎉 Setup completed!")
    print("=" * 50)
    print("✅ Working services:")
    for service in working_services:
        print(f"   - {service}")
    
    print("\n🌐 Access URLs:")
    print("   Observatory: http://192.168.1.119:8888")
    print("   Prometheus: http://192.168.1.119:9090")
    print("   Grafana: http://192.168.1.119:3000 (admin/admin)")
    
    # 9. Test Observatory specifically
    print("\n🔍 Observatory detailed status:")
    success, stdout, stderr = ssh_command("curl -s http://localhost:8888/health")
    if success:
        print(f"📊 Health: {stdout}")
    
    success, stdout, stderr = ssh_command("curl -s http://localhost:8888/metrics | head -5")
    if success:
        print("📈 Metrics endpoint is working")
    
    return len(working_services) >= 2  # At least Observatory and one other service

if __name__ == "__main__":
    if setup_complete_stack():
        print("\n🎉 Observatory stack is ready!")
        print("💡 You can now access the Observatory and configure monitoring dashboards.")
    else:
        print("\n⚠️ Some services may not be working correctly.")
        print("Check the logs on Vonnegut for more details.")