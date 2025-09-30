#!/usr/bin/env python3
"""
Tunnel Credentials Fix
=====================

Fixes Cloudflare tunnel credentials and configuration issues.
Creates proper tunnel setup for Beast Mode Observatory.

Author: Beast Mode Framework
Date: 2025-01-27
"""

import subprocess
import json
import os
import sys
from pathlib import Path


class TunnelCredentialsFixer:
    """Fixes Cloudflare tunnel credentials and configuration."""
    
    def __init__(self):
        self.cloudflared_dir = Path.home() / ".cloudflared"
        self.tunnel_name = "beast-mode-observatory"
        
    def check_cloudflared_installation(self) -> bool:
        """Check if cloudflared is installed."""
        try:
            result = subprocess.run(
                ["cloudflared", "--version"],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                print(f"✅ Cloudflared installed: {result.stdout.strip()}")
                return True
            else:
                print(f"❌ Cloudflared not working properly")
                return False
                
        except FileNotFoundError:
            print(f"❌ Cloudflared not installed")
            return False
    
    def list_existing_tunnels(self) -> list:
        """List existing Cloudflare tunnels."""
        try:
            result = subprocess.run(
                ["cloudflared", "tunnel", "list"],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                print(f"📋 Existing tunnels:")
                print(result.stdout)
                return result.stdout.split('\n')
            else:
                print(f"⚠️ Could not list tunnels: {result.stderr}")
                return []
                
        except Exception as e:
            print(f"❌ Error listing tunnels: {e}")
            return []
    
    def create_tunnel_if_needed(self) -> bool:
        """Create tunnel if it doesn't exist."""
        try:
            print(f"🔧 Creating tunnel: {self.tunnel_name}")
            
            result = subprocess.run(
                ["cloudflared", "tunnel", "create", self.tunnel_name],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                print(f"✅ Tunnel created successfully")
                print(result.stdout)
                return True
            else:
                # Check if tunnel already exists
                if "already exists" in result.stderr:
                    print(f"ℹ️ Tunnel already exists")
                    return True
                else:
                    print(f"❌ Failed to create tunnel: {result.stderr}")
                    return False
                    
        except Exception as e:
            print(f"❌ Error creating tunnel: {e}")
            return False
    
    def find_tunnel_credentials(self) -> Path:
        """Find the tunnel credentials file."""
        try:
            # Look for credentials files
            if self.cloudflared_dir.exists():
                json_files = list(self.cloudflared_dir.glob("*.json"))
                
                print(f"🔍 Found {len(json_files)} credential files:")
                for json_file in json_files:
                    print(f"   {json_file}")
                
                # Look for our tunnel specifically
                for json_file in json_files:
                    if self.tunnel_name in json_file.name:
                        print(f"✅ Found credentials for {self.tunnel_name}: {json_file}")
                        return json_file
                
                # If not found, use the first available
                if json_files:
                    print(f"⚠️ Using first available credentials: {json_files[0]}")
                    return json_files[0]
            
            print(f"❌ No credentials files found")
            return None
            
        except Exception as e:
            print(f"❌ Error finding credentials: {e}")
            return None
    
    def create_tunnel_config(self, credentials_file: Path) -> bool:
        """Create tunnel configuration file."""
        try:
            print(f"📝 Creating tunnel configuration...")
            
            # Get network IP
            result = subprocess.run(
                ["ifconfig"], 
                capture_output=True, 
                text=True
            )
            
            import re
            ip_pattern = r'inet (192\.168\.\d+\.\d+)'
            matches = re.findall(ip_pattern, result.stdout)
            
            if matches:
                network_ip = matches[0]
                print(f"🌐 Using network IP: {network_ip}")
            else:
                network_ip = "localhost"
                print(f"⚠️ Using localhost (tunnel may not work externally)")
            
            # Create configuration
            config_content = f"""
tunnel: {self.tunnel_name}
credentials-file: {credentials_file}

ingress:
  # Prometheus endpoint
  - hostname: prometheus.observatory.nkllon.com
    service: http://{network_ip}:9090
  
  # Grafana endpoint  
  - hostname: grafana.observatory.nkllon.com
    service: http://{network_ip}:3000
  
  # Main Observatory endpoint
  - hostname: observatory.nkllon.com
    service: http://{network_ip}:8888
  
  # Catch-all
  - service: http_status:404
"""
            
            config_path = self.cloudflared_dir / "config.yml"
            
            with open(config_path, 'w') as f:
                f.write(config_content)
            
            print(f"✅ Configuration created: {config_path}")
            return True
            
        except Exception as e:
            print(f"❌ Error creating configuration: {e}")
            return False
    
    def test_tunnel_start(self) -> bool:
        """Test starting the tunnel."""
        try:
            print(f"🧪 Testing tunnel startup...")
            
            # Try to start tunnel
            process = subprocess.Popen(
                ["cloudflared", "tunnel", "run", self.tunnel_name],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Wait a moment
            import time
            time.sleep(5)
            
            # Check if still running
            if process.poll() is None:
                print(f"✅ Tunnel started successfully (PID: {process.pid})")
                
                # Stop the test
                process.terminate()
                process.wait()
                
                return True
            else:
                stdout, stderr = process.communicate()
                print(f"❌ Tunnel failed to start")
                print(f"   stdout: {stdout}")
                print(f"   stderr: {stderr}")
                return False
                
        except Exception as e:
            print(f"❌ Error testing tunnel: {e}")
            return False
    
    def fix_tunnel_credentials(self) -> bool:
        """Main method to fix tunnel credentials."""
        print("🔧 Fixing Cloudflare Tunnel Credentials")
        print("=" * 50)
        
        # Check cloudflared installation
        if not self.check_cloudflared_installation():
            print("💡 Install cloudflared first:")
            print("   brew install cloudflared")
            return False
        
        # List existing tunnels
        self.list_existing_tunnels()
        
        # Create tunnel if needed
        if not self.create_tunnel_if_needed():
            return False
        
        # Find credentials
        credentials_file = self.find_tunnel_credentials()
        if not credentials_file:
            print("❌ No credentials file found after tunnel creation")
            return False
        
        # Create configuration
        if not self.create_tunnel_config(credentials_file):
            return False
        
        # Test tunnel startup
        if not self.test_tunnel_start():
            print("⚠️ Tunnel configuration created but startup test failed")
            print("💡 Try running manually: cloudflared tunnel run beast-mode-observatory")
            return False
        
        print(f"\n🚀 SUCCESS!")
        print(f"✅ Tunnel credentials and configuration fixed")
        print(f"✅ Tunnel can start successfully")
        print(f"\n💡 Next steps:")
        print(f"   1. Run: python3 bounce_cloudflare_tunnel.py")
        print(f"   2. Verify endpoints are accessible")
        print(f"   3. Check Grafana for data")
        
        return True


def main():
    """Main execution function."""
    fixer = TunnelCredentialsFixer()
    
    try:
        success = fixer.fix_tunnel_credentials()
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