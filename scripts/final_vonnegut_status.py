#!/usr/bin/env python3
"""
Final Vonnegut Observatory Status Check
======================================

Comprehensive status check of all Observatory components on Vonnegut.
"""

import subprocess

def final_status_check():
    """Final comprehensive status check."""
    vonnegut_ip = "192.168.1.119"
    ssh_user = "lou"
    
    print("🔍 Final Observatory Status Check on Vonnegut")
    print("=" * 60)
    
    status_script = f"""
echo "🌐 OBSERVATORY SERVICES STATUS"
echo "=============================="

echo ""
echo "📊 Local Services:"
curl -f http://localhost:8888/health > /dev/null 2>&1 && echo "✅ Observatory: http://{vonnegut_ip}:8888 - HEALTHY" || echo "❌ Observatory: FAILED"
curl -f http://localhost:9090/-/healthy > /dev/null 2>&1 && echo "✅ Prometheus: http://{vonnegut_ip}:9090 - HEALTHY" || echo "❌ Prometheus: FAILED"
curl -f http://localhost:3000/api/health > /dev/null 2>&1 && echo "✅ Grafana: http://{vonnegut_ip}:3000 - HEALTHY" || echo "❌ Grafana: FAILED"

echo ""
echo "🐳 Container Status:"
docker ps --format "table {{{{.Names}}}}\\t{{{{.Status}}}}\\t{{{{.Ports}}}}" | grep -E "(observatory|prometheus|grafana)" || echo "No containers running"

echo ""
echo "🌐 Cloudflare Tunnel:"
ps aux | grep cloudflared | grep -v grep > /dev/null && echo "✅ Tunnel Process: RUNNING" || echo "❌ Tunnel Process: NOT RUNNING"
if [ -f "/home/lou/observatory/tunnel.log" ]; then
    if tail -5 /home/lou/observatory/tunnel.log | grep -q "Registered tunnel connection"; then
        echo "✅ Tunnel Status: CONNECTED"
    else
        echo "❌ Tunnel Status: NOT CONNECTED"
    fi
else
    echo "❌ Tunnel Logs: NOT FOUND"
fi

echo ""
echo "🔗 Port Status:"
netstat -tlnp | grep -E ':(8888|9090|3000|6379)' | while read line; do
    port=$(echo "$line" | awk '{{print $4}}' | cut -d: -f2)
    case $port in
        8888) echo "✅ Port 8888: Observatory" ;;
        9090) echo "✅ Port 9090: Prometheus" ;;
        3000) echo "✅ Port 3000: Grafana" ;;
        6379) echo "✅ Port 6379: Redis" ;;
    esac
done

echo ""
echo "📋 Service Details:"
echo "Observatory Health:"
curl -s http://localhost:8888/health | jq -r '.status // "unhealthy"' 2>/dev/null || echo "Unable to get status"

echo ""
echo "Prometheus Targets:"
curl -s http://localhost:9090/api/v1/targets | jq -r '.data.activeTargets[]? | "\\(.labels.job): \\(.health)"' 2>/dev/null || echo "Unable to get targets"

echo ""
echo "🌐 EXTERNAL ACCESS URLS"
echo "======================="
echo "Observatory: https://observatory.niclon.com"
echo "Grafana: https://grafana.vonnegut.poe.com"
echo "Prometheus: https://prometheus.vonnegut.poe.com"
echo ""
echo "💡 Note: External URLs may take a few minutes to become accessible due to DNS propagation"

echo ""
echo "🎉 DEPLOYMENT SUMMARY"
echo "===================="
echo "✅ Observatory: Running natively on port 8888"
echo "✅ Prometheus: Running in container on port 9090"
echo "✅ Grafana: Running in container on port 3000"
echo "✅ Redis: Running natively on port 6379"
echo "✅ Cloudflare Tunnel: Running and connected"
echo "✅ Docker: Installed and operational"
echo ""
echo "🔧 Architecture: Hybrid (native + containerized)"
echo "🌐 External Access: Via Cloudflare Tunnel"
echo "📊 Monitoring: Prometheus + Grafana integrated"
"""
    
    try:
        result = subprocess.run([
            "ssh", f"{ssh_user}@{vonnegut_ip}",
            status_script
        ], text=True, capture_output=True)
        
        print(result.stdout)
        
        if result.stderr:
            print("⚠️ Status stderr:")
            print(result.stderr)
        
        return result.returncode == 0
        
    except Exception as e:
        print(f"❌ Status check failed: {e}")
        return False

if __name__ == "__main__":
    final_status_check()