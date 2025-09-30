#!/usr/bin/env python3
"""
Bounce Cloudflare Tunnel
========================

Restarts the Cloudflare tunnel to refresh connections and fix potential
connectivity issues with Prometheus/Grafana endpoints.

Author: Beast Mode Framework
Date: 2025-01-27
"""

import subprocess
import time
import sys
import signal
import os
from typing import Optional, List


class CloudflareTunnelManager:
    """Manages Cloudflare tunnel operations."""
    
    def __init__(self):
        self.tunnel_name = "observatory-tunnel"
        self.tunnel_process_id: Optional[int] = None
    
    def find_tunnel_process(self) -> Optional[int]:
        """Find the running Cloudflare tunnel process."""
        try:
            # Get all cloudflared processes
            result = subprocess.run(
                ["ps", "aux"], 
                capture_output=True, 
                text=True, 
                check=True
            )
            
            for line in result.stdout.split('\n'):
                if 'cloudflared tunnel run' in line and self.tunnel_name in line:
                    # Extract PID (second column)
                    parts = line.split()
                    if len(parts) >= 2:
                        try:
                            pid = int(parts[1])
                            print(f"✅ Found tunnel process: PID {pid}")
                            return pid
                        except ValueError:
                            continue
            
            print(f"❌ No running tunnel process found for {self.tunnel_name}")
            return None
            
        except Exception as e:
            print(f"❌ Error finding tunnel process: {e}")
            return None
    
    def stop_tunnel(self, pid: int) -> bool:
        """Stop the tunnel process gracefully."""
        try:
            print(f"🛑 Stopping tunnel process {pid}...")
            
            # Send SIGTERM for graceful shutdown
            os.kill(pid, signal.SIGTERM)
            
            # Wait for process to stop
            for i in range(10):  # Wait up to 10 seconds
                try:
                    # Check if process still exists
                    os.kill(pid, 0)  # This will raise OSError if process doesn't exist
                    print(f"   Waiting for graceful shutdown... ({i+1}/10)")
                    time.sleep(1)
                except OSError:
                    print(f"✅ Tunnel stopped gracefully")
                    return True
            
            # If still running, force kill
            print(f"⚠️ Graceful shutdown timeout, force killing...")
            os.kill(pid, signal.SIGKILL)
            time.sleep(2)
            
            try:
                os.kill(pid, 0)
                print(f"❌ Failed to stop tunnel process")
                return False
            except OSError:
                print(f"✅ Tunnel force stopped")
                return True
                
        except Exception as e:
            print(f"❌ Error stopping tunnel: {e}")
            return False
    
    def start_tunnel(self) -> bool:
        """Start the Cloudflare tunnel."""
        try:
            print(f"🚀 Starting Cloudflare tunnel: {self.tunnel_name}")
            
            # Start tunnel in background
            process = subprocess.Popen(
                ["cloudflared", "tunnel", "run", self.tunnel_name],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Give it a moment to start
            time.sleep(3)
            
            # Check if process is still running
            if process.poll() is None:
                print(f"✅ Tunnel started successfully (PID: {process.pid})")
                return True
            else:
                stdout, stderr = process.communicate()
                print(f"❌ Tunnel failed to start")
                print(f"   stdout: {stdout}")
                print(f"   stderr: {stderr}")
                return False
                
        except Exception as e:
            print(f"❌ Error starting tunnel: {e}")
            return False
    
    def check_tunnel_status(self) -> bool:
        """Check if tunnel is running and accessible."""
        try:
            print(f"🔍 Checking tunnel status...")
            
            # Check process
            pid = self.find_tunnel_process()
            if not pid:
                return False
            
            # Test connectivity to endpoints
            import requests
            
            endpoints = [
                "https://prometheus.observatory.nkllon.com/api/v1/query?query=up",
                "https://grafana.observatory.nkllon.com/api/health"
            ]
            
            for endpoint in endpoints:
                try:
                    response = requests.get(endpoint, timeout=10)
                    service_name = endpoint.split('.')[0].split('//')[-1]
                    if response.status_code == 200:
                        print(f"   ✅ {service_name}: Accessible")
                    else:
                        print(f"   ⚠️ {service_name}: HTTP {response.status_code}")
                except Exception as e:
                    service_name = endpoint.split('.')[0].split('//')[-1]
                    print(f"   ❌ {service_name}: {e}")
            
            return True
            
        except Exception as e:
            print(f"❌ Error checking tunnel status: {e}")
            return False
    
    def bounce_tunnel(self) -> bool:
        """Bounce (restart) the Cloudflare tunnel."""
        print("🔄 Bouncing Cloudflare Tunnel")
        print("=" * 40)
        
        # Find current process
        pid = self.find_tunnel_process()
        
        if pid:
            # Stop current tunnel
            if not self.stop_tunnel(pid):
                print("❌ Failed to stop tunnel")
                return False
            
            # Wait a moment
            print("⏳ Waiting before restart...")
            time.sleep(2)
        else:
            print("ℹ️ No running tunnel found, starting fresh...")
        
        # Start tunnel
        if not self.start_tunnel():
            print("❌ Failed to start tunnel")
            return False
        
        # Wait for startup
        print("⏳ Waiting for tunnel to stabilize...")
        time.sleep(5)
        
        # Check status
        if self.check_tunnel_status():
            print("\n🚀 SUCCESS!")
            print("✅ Cloudflare tunnel bounced successfully")
            print("✅ Endpoints should now be accessible")
            return True
        else:
            print("\n⚠️ Tunnel restarted but status check failed")
            print("💡 Give it a few more moments and check manually")
            return False


def main():
    """Main execution function."""
    print("🔄 Cloudflare Tunnel Bounce Utility")
    print("=" * 50)
    print("This will restart the Cloudflare tunnel to refresh connections")
    print("and potentially fix 'no data' issues in Grafana/Prometheus.")
    print("=" * 50)
    
    manager = CloudflareTunnelManager()
    
    try:
        success = manager.bounce_tunnel()
        
        if success:
            print(f"\n💡 Next steps:")
            print(f"   1. Wait 30 seconds for full stabilization")
            print(f"   2. Check Grafana: https://grafana.observatory.nkllon.com")
            print(f"   3. Check Prometheus: https://prometheus.observatory.nkllon.com")
            print(f"   4. Verify data is now flowing in dashboards")
            
        return success
        
    except KeyboardInterrupt:
        print(f"\n⚠️ Operation cancelled by user")
        return False
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)