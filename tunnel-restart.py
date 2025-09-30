#!/usr/bin/env python3
"""
Tunnel Restart Script for Beast Mode Observatory
===============================================

Restarts Cloudflare tunnel and ensures Prometheus metrics are properly exposed
through the tunnel at prometheus.observatory.nkllon.com

Author: Beast Mode Framework
Date: 2025-01-27
"""

import subprocess
import time
import json
import os
import sys
import signal
import logging
import requests
from pathlib import Path
from typing import Optional, Dict, Any

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class TunnelRestarter:
    """Restarts Cloudflare tunnel with proper Prometheus configuration."""
    
    def __init__(self):
        self.tunnel_processes = []
        self.prometheus_port = 9090
        self.grafana_port = 3000
        self.observatory_port = 8888
        
        # Network IP for binding (not localhost)
        self.network_ip = self._get_network_ip()
        
    def _get_network_ip(self) -> str:
        """Get the local network IP address."""
        try:
            # Get network interfaces
            result = subprocess.run(
                ["ifconfig"], 
                capture_output=True, 
                text=True
            )
            
            # Look for 192.168.x.x addresses
            import re
            ip_pattern = r'inet (192\.168\.\d+\.\d+)'
            matches = re.findall(ip_pattern, result.stdout)
            
            if matches:
                # Use the first 192.168.x.x address found
                network_ip = matches[0]
                logger.info(f"Using network IP: {network_ip}")
                return network_ip
            else:
                logger.warning("No 192.168.x.x IP found, using localhost")
                return "127.0.0.1"
                
        except Exception as e:
            logger.error(f"Error getting network IP: {e}")
            return "127.0.0.1"
    
    def kill_existing_tunnels(self):
        """Kill any existing cloudflared processes."""
        try:
            logger.info("🔄 Killing existing tunnel processes...")
            
            # Find cloudflared processes
            result = subprocess.run(
                ["pgrep", "-f", "cloudflared"],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                pids = result.stdout.strip().split('\n')
                for pid in pids:
                    if pid:
                        try:
                            subprocess.run(["kill", "-TERM", pid])
                            logger.info(f"   Killed process {pid}")
                        except Exception as e:
                            logger.warning(f"   Failed to kill process {pid}: {e}")
                
                # Wait for processes to die
                time.sleep(3)
                
                # Force kill if still running
                result = subprocess.run(
                    ["pgrep", "-f", "cloudflared"],
                    capture_output=True,
                    text=True
                )
                
                if result.returncode == 0:
                    pids = result.stdout.strip().split('\n')
                    for pid in pids:
                        if pid:
                            try:
                                subprocess.run(["kill", "-KILL", pid])
                                logger.info(f"   Force killed process {pid}")
                            except Exception:
                                pass
            
            logger.info("✅ Existing tunnels cleaned up")
            
        except Exception as e:
            logger.error(f"Error killing existing tunnels: {e}")
    
    def start_prometheus_if_needed(self) -> bool:
        """Start Prometheus if it's not running."""
        try:
            # Check if Prometheus is already running
            try:
                response = requests.get(f"http://{self.network_ip}:{self.prometheus_port}/api/v1/query?query=up", timeout=5)
                if response.status_code == 200:
                    logger.info("✅ Prometheus is already running")
                    return True
            except requests.exceptions.RequestException:
                pass
            
            logger.info("🚀 Starting Prometheus...")
            
            # Create basic Prometheus config
            prometheus_config = f"""
global:
  scrape_interval: 15s
  evaluation_interval: 15s

scrape_configs:
  - job_name: 'prometheus'
    static_configs:
      - targets: ['{self.network_ip}:{self.prometheus_port}']

  - job_name: 'beast-mode-observatory'
    static_configs:
      - targets: ['{self.network_ip}:{self.observatory_port}']
    metrics_path: '/metrics'
    scrape_interval: 15s

  - job_name: 'beast-mode-dag-orchestration'
    static_configs:
      - targets: ['{self.network_ip}:8000']
    metrics_path: '/metrics'
    scrape_interval: 15s
"""
            
            # Write config file
            config_path = Path("prometheus.yml")
            with open(config_path, 'w') as f:
                f.write(prometheus_config)
            
            # Start Prometheus
            prometheus_cmd = [
                "prometheus",
                f"--config.file={config_path}",
                f"--storage.tsdb.path=./prometheus_data",
                f"--web.console.libraries=./console_libraries",
                f"--web.console.templates=./consoles",
                f"--web.enable-lifecycle",
                f"--web.listen-address={self.network_ip}:{self.prometheus_port}"
            ]
            
            process = subprocess.Popen(
                prometheus_cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            self.prometheus_process = process
            
            # Wait for Prometheus to start
            for i in range(30):
                try:
                    response = requests.get(f"http://{self.network_ip}:{self.prometheus_port}/api/v1/query?query=up", timeout=2)
                    if response.status_code == 200:
                        logger.info(f"✅ Prometheus started successfully on {self.network_ip}:{self.prometheus_port}")
                        return True
                except requests.exceptions.RequestException:
                    pass
                
                time.sleep(1)
            
            logger.error("❌ Prometheus failed to start within 30 seconds")
            return False
            
        except Exception as e:
            logger.error(f"Error starting Prometheus: {e}")
            return False
    
    def generate_metrics_data(self):
        """Generate some test metrics data by running our DAG orchestration components."""
        try:
            logger.info("📊 Generating metrics data...")
            
            # Run our infrastructure validator to generate metrics
            result = subprocess.run([
                "python3", "test_infrastructure_preconditions.py"
            ], capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                logger.info("✅ Infrastructure validation metrics generated")
            
            # Run parallel execution engine test to generate metrics
            result = subprocess.run([
                "python3", "test_parallel_execution_engine.py"
            ], capture_output=True, text=True, timeout=60)
            
            if result.returncode == 0:
                logger.info("✅ Parallel execution metrics generated")
            
        except Exception as e:
            logger.warning(f"Error generating metrics data: {e}")
    
    def create_tunnel_config(self) -> Path:
        """Create Cloudflare tunnel configuration."""
        config_content = f"""
tunnel: beast-mode-observatory
credentials-file: ~/.cloudflared/beast-mode-observatory.json

ingress:
  # Prometheus endpoint
  - hostname: prometheus.observatory.nkllon.com
    service: http://{self.network_ip}:{self.prometheus_port}
  
  # Grafana endpoint  
  - hostname: grafana.observatory.nkllon.com
    service: http://{self.network_ip}:{self.grafana_port}
  
  # Main Observatory endpoint
  - hostname: observatory.nkllon.com
    service: http://{self.network_ip}:{self.observatory_port}
  
  # Catch-all
  - service: http_status:404
"""
        
        config_path = Path.home() / ".cloudflared" / "config.yml"
        config_path.parent.mkdir(exist_ok=True)
        
        with open(config_path, 'w') as f:
            f.write(config_content)
        
        logger.info(f"✅ Tunnel config created: {config_path}")
        return config_path
    
    def start_tunnel(self) -> bool:
        """Start the Cloudflare tunnel."""
        try:
            logger.info("🚀 Starting Cloudflare tunnel...")
            
            # Create tunnel config
            config_path = self.create_tunnel_config()
            
            # Start tunnel
            tunnel_cmd = [
                "cloudflared", "tunnel", "run", "beast-mode-observatory"
            ]
            
            process = subprocess.Popen(
                tunnel_cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            self.tunnel_processes.append(process)
            
            # Wait for tunnel to establish
            logger.info("⏳ Waiting for tunnel to establish...")
            time.sleep(10)
            
            # Test tunnel connectivity
            endpoints = [
                "https://prometheus.observatory.nkllon.com/api/v1/query?query=up",
                "https://grafana.observatory.nkllon.com/api/health",
                "https://observatory.nkllon.com/health"
            ]
            
            for endpoint in endpoints:
                try:
                    response = requests.get(endpoint, timeout=10)
                    if response.status_code == 200:
                        logger.info(f"✅ {endpoint} - accessible")
                    else:
                        logger.warning(f"⚠️ {endpoint} - returned {response.status_code}")
                except requests.exceptions.RequestException as e:
                    logger.warning(f"❌ {endpoint} - not accessible: {e}")
            
            logger.info("✅ Tunnel started successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error starting tunnel: {e}")
            return False
    
    def restart_tunnel(self) -> bool:
        """Main method to restart the tunnel."""
        logger.info("🔄 Restarting Cloudflare Tunnel for Beast Mode Observatory")
        logger.info("=" * 60)
        
        try:
            # Step 1: Kill existing tunnels
            self.kill_existing_tunnels()
            
            # Step 2: Start Prometheus if needed
            if not self.start_prometheus_if_needed():
                logger.error("❌ Failed to start Prometheus")
                return False
            
            # Step 3: Generate some metrics data
            self.generate_metrics_data()
            
            # Step 4: Start tunnel
            if not self.start_tunnel():
                logger.error("❌ Failed to start tunnel")
                return False
            
            # Step 5: Final verification
            logger.info("\n🧪 Final Verification:")
            logger.info("=" * 30)
            
            endpoints = {
                "Prometheus": "https://prometheus.observatory.nkllon.com/api/v1/query?query=up",
                "Grafana": "https://grafana.observatory.nkllon.com/api/health", 
                "Observatory": "https://observatory.nkllon.com/health"
            }
            
            all_good = True
            for name, url in endpoints.items():
                try:
                    response = requests.get(url, timeout=15)
                    if response.status_code == 200:
                        logger.info(f"✅ {name}: Accessible")
                    else:
                        logger.warning(f"⚠️ {name}: HTTP {response.status_code}")
                        all_good = False
                except Exception as e:
                    logger.error(f"❌ {name}: Not accessible - {e}")
                    all_good = False
            
            if all_good:
                logger.info("\n🚀 SUCCESS! All endpoints are accessible")
                logger.info("🎯 Prometheus should now have data in Grafana")
                logger.info("\n📊 Access points:")
                logger.info("   • Prometheus: https://prometheus.observatory.nkllon.com")
                logger.info("   • Grafana: https://grafana.observatory.nkllon.com")
                logger.info("   • Observatory: https://observatory.nkllon.com")
            else:
                logger.warning("\n⚠️ Some endpoints are not accessible")
                logger.info("💡 Try waiting a few more minutes for tunnel to fully establish")
            
            return all_good
            
        except Exception as e:
            logger.error(f"Unexpected error during tunnel restart: {e}")
            return False
    
    def cleanup(self):
        """Clean up processes."""
        logger.info("🧹 Cleaning up...")
        
        for process in self.tunnel_processes:
            try:
                process.terminate()
                process.wait(timeout=5)
            except Exception:
                try:
                    process.kill()
                except Exception:
                    pass


def main():
    """Main execution function."""
    restarter = TunnelRestarter()
    
    try:
        success = restarter.restart_tunnel()
        
        if success:
            logger.info("\n✅ Tunnel restart completed successfully!")
            logger.info("🔄 Tunnel will continue running in background")
            logger.info("💡 Use Ctrl+C to stop if needed")
            
            # Keep running to maintain tunnel
            try:
                while True:
                    time.sleep(60)
            except KeyboardInterrupt:
                logger.info("\n🛑 Received interrupt, shutting down...")
                restarter.cleanup()
        else:
            logger.error("\n❌ Tunnel restart failed")
            sys.exit(1)
            
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        restarter.cleanup()
        sys.exit(1)


if __name__ == "__main__":
    main()