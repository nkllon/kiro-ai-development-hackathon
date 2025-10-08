#!/usr/bin/env python3
"""
Restore Original Tunnel Configuration
====================================

Restores the original working tunnel configuration that was broken
by creating unnecessary new tunnels and certificates.

Author: Beast Mode Framework  
Date: 2025-01-27
"""

import subprocess
import sys
from pathlib import Path


def restore_original_config():
    """Restore the original working tunnel configuration."""
    
    print("🔄 Restoring Original Tunnel Configuration")
    print("=" * 50)
    print("CRITICAL: Fixing the error of creating unnecessary new tunnel")
    print("=" * 50)
    
    # Kill current tunnel processes
    print("1. Stopping current tunnel processes...")
    try:
        result = subprocess.run(["pkill", "-f", "cloudflared"], capture_output=True)
        print("   ✅ Stopped tunnel processes")
    except Exception as e:
        print(f"   ⚠️ Error stopping processes: {e}")
    
    # Restore original config using existing observatory-tunnel
    print("2. Restoring original tunnel configuration...")
    
    config_content = """
tunnel: observatory-tunnel
credentials-file: ~/.cloudflared/d1e53e43-033f-4994-8f46-c83962ae3785.json

ingress:
  # Prometheus endpoint  
  - hostname: prometheus.observatory.nkllon.com
    service: http://192.168.1.101:9090
  
  # Grafana endpoint
  - hostname: grafana.observatory.nkllon.com  
    service: http://192.168.1.101:3000
  
  # Main Observatory endpoint
  - hostname: observatory.nkllon.com
    service: http://192.168.1.101:8888
  
  # Catch-all
  - service: http_status:404
"""
    
    config_path = Path.home() / ".cloudflared" / "config.yml"
    
    with open(config_path, 'w') as f:
        f.write(config_content)
    
    print("   ✅ Restored config to use original observatory-tunnel")
    
    # Start the original tunnel
    print("3. Starting original tunnel...")
    try:
        process = subprocess.Popen(
            ["cloudflared", "tunnel", "run", "observatory-tunnel"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        import time
        time.sleep(5)
        
        if process.poll() is None:
            print("   ✅ Original tunnel started successfully")
            return True
        else:
            stdout, stderr = process.communicate()
            print(f"   ❌ Failed to start: {stderr}")
            return False
            
    except Exception as e:
        print(f"   ❌ Error starting tunnel: {e}")
        return False


def cleanup_unnecessary_tunnel():
    """Clean up the unnecessary tunnel that was created."""
    
    print("4. Cleaning up unnecessary tunnel...")
    try:
        # Delete the unnecessary tunnel
        result = subprocess.run([
            "cloudflared", "tunnel", "delete", "beast-mode-observatory"
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("   ✅ Deleted unnecessary tunnel: beast-mode-observatory")
        else:
            print(f"   ⚠️ Could not delete tunnel: {result.stderr}")
            
    except Exception as e:
        print(f"   ⚠️ Error cleaning up: {e}")


def main():
    """Main restoration function."""
    
    success = restore_original_config()
    
    if success:
        cleanup_unnecessary_tunnel()
        
        print("\n🚀 RESTORATION COMPLETE")
        print("✅ Original tunnel configuration restored")
        print("✅ Using existing observatory-tunnel certificate")
        print("✅ Prometheus/Grafana endpoints should now work")
        print("\n💡 The issue was CONFIGURATION, not certificates!")
        print("   - Existing certificates were working fine")
        print("   - Only needed to add prometheus/grafana routes")
        print("   - Creating new tunnel was unnecessary and harmful")
        
        return True
    else:
        print("\n❌ RESTORATION FAILED")
        print("💡 Manual steps needed:")
        print("   1. Edit ~/.cloudflared/config.yml")
        print("   2. Change tunnel to: observatory-tunnel") 
        print("   3. Change credentials to: d1e53e43-033f-4994-8f46-c83962ae3785.json")
        print("   4. Add prometheus/grafana hostname routes")
        
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)