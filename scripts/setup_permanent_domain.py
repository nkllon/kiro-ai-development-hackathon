#!/usr/bin/env python3
"""
Setup permanent domain for Beast Mode Observatory
Creates observatory.nkllon.com pointing to Cloudflare tunnel
"""

import subprocess
import json
import time
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DomainSetup:
    def __init__(self):
        self.domain = "nkllon.com"
        self.subdomain = "observatory"
        self.full_domain = f"{self.subdomain}.{self.domain}"
        
    def create_named_tunnel(self):
        """Create a named Cloudflare tunnel with custom domain."""
        try:
            tunnel_name = "beast-mode-observatory"
            
            logger.info(f"Creating named tunnel: {tunnel_name}")
            
            # Create tunnel
            result = subprocess.run([
                "cloudflared", "tunnel", "create", tunnel_name
            ], capture_output=True, text=True)
            
            if result.returncode != 0:
                logger.error(f"Failed to create tunnel: {result.stderr}")
                return None
            
            # Get tunnel ID from output
            tunnel_id = None
            for line in result.stdout.split('\n'):
                if 'Created tunnel' in line and tunnel_name in line:
                    # Extract tunnel ID (UUID format)
                    import re
                    uuid_match = re.search(r'[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}', line)
                    if uuid_match:
                        tunnel_id = uuid_match.group(0)
                        break
            
            if not tunnel_id:
                logger.error("Could not extract tunnel ID")
                return None
            
            logger.info(f"Tunnel created with ID: {tunnel_id}")
            
            # Create config file
            config_content = f"""tunnel: {tunnel_id}
credentials-file: /Users/{subprocess.getoutput('whoami')}/.cloudflared/{tunnel_id}.json

ingress:
  - hostname: {self.full_domain}
    service: http://localhost:8888
  - service: http_status:404
"""
            
            config_path = Path.home() / ".cloudflared" / "config.yml"
            config_path.parent.mkdir(exist_ok=True)
            
            with open(config_path, 'w') as f:
                f.write(config_content)
            
            logger.info(f"Config written to {config_path}")
            
            # Add DNS record (this requires manual step or API)
            logger.info(f"""
🎯 MANUAL STEP REQUIRED:

Add this DNS record to your domain {self.domain}:

Type: CNAME
Name: {self.subdomain}
Value: {tunnel_id}.cfargotunnel.com
TTL: Auto (or 300)

You can do this in:
1. Squarespace DNS settings, OR
2. NSOne dashboard (if you have access)

Once added, your Observatory will be available at:
https://{self.full_domain}
""")
            
            return {
                'tunnel_id': tunnel_id,
                'tunnel_name': tunnel_name,
                'domain': self.full_domain,
                'cname_target': f"{tunnel_id}.cfargotunnel.com"
            }
            
        except Exception as e:
            logger.error(f"Error creating named tunnel: {e}")
            return None
    
    def start_tunnel(self, tunnel_name):
        """Start the named tunnel."""
        try:
            logger.info(f"Starting tunnel: {tunnel_name}")
            
            # Start tunnel
            process = subprocess.Popen([
                "cloudflared", "tunnel", "run", tunnel_name
            ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            
            logger.info(f"Tunnel started with PID: {process.pid}")
            logger.info(f"🚀 Observatory should be available at: https://{self.full_domain}")
            
            return process
            
        except Exception as e:
            logger.error(f"Error starting tunnel: {e}")
            return None
    
    def setup_systemd_service(self, tunnel_name):
        """Create systemd service for auto-restart (Linux only)."""
        service_content = f"""[Unit]
Description=Cloudflare Tunnel for Beast Mode Observatory
After=network.target

[Service]
Type=simple
User={subprocess.getoutput('whoami')}
ExecStart=/usr/local/bin/cloudflared tunnel run {tunnel_name}
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
"""
        
        service_path = Path("/etc/systemd/system/beast-mode-tunnel.service")
        
        try:
            with open(service_path, 'w') as f:
                f.write(service_content)
            
            # Enable and start service
            subprocess.run(["sudo", "systemctl", "enable", "beast-mode-tunnel"])
            subprocess.run(["sudo", "systemctl", "start", "beast-mode-tunnel"])
            
            logger.info("Systemd service created and started")
            
        except Exception as e:
            logger.error(f"Could not create systemd service: {e}")
            logger.info("You'll need to start the tunnel manually")
    
    def setup_launchd_service(self, tunnel_name):
        """Create launchd service for auto-restart (macOS)."""
        plist_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.beastmode.observatory.tunnel</string>
    <key>ProgramArguments</key>
    <array>
        <string>/usr/local/bin/cloudflared</string>
        <string>tunnel</string>
        <string>run</string>
        <string>{tunnel_name}</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
    <key>StandardOutPath</key>
    <string>/tmp/beast-mode-tunnel.log</string>
    <key>StandardErrorPath</key>
    <string>/tmp/beast-mode-tunnel.error.log</string>
</dict>
</plist>
"""
        
        plist_path = Path.home() / "Library" / "LaunchAgents" / "com.beastmode.observatory.tunnel.plist"
        plist_path.parent.mkdir(exist_ok=True)
        
        try:
            with open(plist_path, 'w') as f:
                f.write(plist_content)
            
            # Load the service
            subprocess.run(["launchctl", "load", str(plist_path)])
            
            logger.info(f"LaunchAgent created at {plist_path}")
            logger.info("Tunnel will auto-start on boot")
            
        except Exception as e:
            logger.error(f"Could not create LaunchAgent: {e}")

def main():
    setup = DomainSetup()
    
    # Create the tunnel
    tunnel_info = setup.create_named_tunnel()
    if not tunnel_info:
        logger.error("Failed to create tunnel")
        return
    
    # Save tunnel info
    with open("tunnel_info.json", 'w') as f:
        json.dump(tunnel_info, f, indent=2)
    
    # Set up auto-restart service
    import platform
    if platform.system() == "Darwin":  # macOS
        setup.setup_launchd_service(tunnel_info['tunnel_name'])
    elif platform.system() == "Linux":
        setup.setup_systemd_service(tunnel_info['tunnel_name'])
    
    # Start tunnel
    process = setup.start_tunnel(tunnel_info['tunnel_name'])
    
    if process:
        logger.info("✅ Setup complete!")
        logger.info(f"🌐 Add the DNS record and visit: https://{setup.full_domain}")
        
        # Keep running
        try:
            process.wait()
        except KeyboardInterrupt:
            logger.info("Shutting down...")
            process.terminate()

if __name__ == "__main__":
    main()