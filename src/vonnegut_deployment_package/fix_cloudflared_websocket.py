#!/usr/bin/env python3
"""
Cloudflared WebSocket Configuration Fix Script

This script updates the Cloudflared configuration to support WebSocket connections
for the Observatory infrastructure and restarts the service.
"""

import os
import subprocess
import sys
import time
import json
from pathlib import Path

def main():
    """Main function to fix Cloudflared WebSocket configuration."""
    print("🔧 Cloudflared WebSocket Configuration Fix")
    print("=" * 50)
    
    # Configuration file path
    config_path = Path.home() / ".cloudflared" / "config.yml"
    backup_path = Path.home() / ".cloudflared" / "config.yml.backup"
    
    # New configuration with WebSocket support
    new_config = """tunnel: d1e53e43-033f-4994-8f46-c83962ae3785
credentials-file: /Users/lou/.cloudflared/d1e53e43-033f-4994-8f46-c83962ae3785.json

ingress:
  - hostname: observatory.nkllon.com
    service: http://localhost:8888
    originRequest:
      httpHostHeader: localhost:8888
      # WebSocket support configuration
      noTLSVerify: true
      connectTimeout: 30s
      tlsTimeout: 10s
      tcpKeepAlive: 30s
      keepAliveConnections: 100
      keepAliveTimeout: 90s
  - hostname: observatory-container.nkllon.com  
    service: http://localhost:8889
    originRequest:
      httpHostHeader: localhost:8889
      # WebSocket support configuration
      noTLSVerify: true
      connectTimeout: 30s
      tlsTimeout: 10s
      tcpKeepAlive: 30s
      keepAliveConnections: 100
      keepAliveTimeout: 90s
  - service: http_status:404
"""
    
    try:
        # Step 1: Backup current configuration
        print("📋 Step 1: Backing up current configuration...")
        if config_path.exists():
            with open(config_path, 'r') as f:
                current_config = f.read()
            with open(backup_path, 'w') as f:
                f.write(current_config)
            print(f"✅ Backup created: {backup_path}")
        else:
            print("⚠️  No existing configuration found")
        
        # Step 2: Update configuration
        print("📝 Step 2: Updating configuration with WebSocket support...")
        with open(config_path, 'w') as f:
            f.write(new_config)
        print(f"✅ Configuration updated: {config_path}")
        
        # Step 3: Restart cloudflared service
        print("🔄 Step 3: Restarting cloudflared service...")
        
        # Check if cloudflared is running
        try:
            result = subprocess.run(['pgrep', '-f', 'cloudflared'], 
                                 capture_output=True, text=True)
            if result.returncode == 0:
                print("🛑 Stopping existing cloudflared processes...")
                subprocess.run(['pkill', '-f', 'cloudflared'], check=True)
                time.sleep(2)
        except subprocess.CalledProcessError:
            print("ℹ️  No existing cloudflared processes found")
        
        # Start cloudflared
        print("🚀 Starting cloudflared with new configuration...")
        subprocess.run(['cloudflared', 'tunnel', 'run'], check=True)
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Error running cloudflared: {e}")
        return 1
    except Exception as e:
        print(f"❌ Error: {e}")
        return 1
    
    print("✅ Cloudflared WebSocket configuration fix completed!")
    return 0

if __name__ == "__main__":
    sys.exit(main())