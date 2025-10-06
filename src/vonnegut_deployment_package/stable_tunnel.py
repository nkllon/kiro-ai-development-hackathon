#!/usr/bin/env python3
"""
Stable Tunnel Manager for Beast Mode Observatory
Creates a persistent tunnel and provides DNS setup instructions
"""

import subprocess
import time
import json
import os
import signal
import logging
import re
from pathlib import Path

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class StableTunnel:
    def __init__(self):
        self.tunnel_process = None
        self.tunnel_url = None
        self.running = True
        
        # Handle shutdown gracefully
        signal.signal(signal.SIGINT, self._shutdown)
        signal.signal(signal.SIGTERM, self._shutdown)
    
    def _shutdown(self, signum, frame):
        logger.info("Shutting down...")
        self.running = False
        if self.tunnel_process:
            self.tunnel_process.terminate()
        exit(0)
    
    def ensure_observatory_running(self):
        """Ensure Observatory service is running."""
        try:
            result = subprocess.run(
                ["python3", "scripts/observatory-daemon.py", "status"],
                capture_output=True, text=True, timeout=10
            )
            
            if result.returncode != 0:
                logger.info("Starting Observatory service...")
                subprocess.run(
                    ["python3", "scripts/observatory-daemon.py", "start"],
                    timeout=30
                )
                time.sleep(5)  # Give it time to start
            
            return True
        except Exception as e:
            logger.error(f"Error with Observatory service: {e}")
            return False
    
    def create_tunnel(self):
        """Create a stable tunnel."""
        try:
            logger.info("Creating stable tunnel...")
            
            # Start tunnel process
            self.tunnel_process = subprocess.Popen([
                "cloudflared", "tunnel", "--url", "localhost:8888"
            ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            
            # Parse output for tunnel URL
            start_time = time.time()
            while time.time() - start_time < 30:  # Wait up to 30 seconds
                if self.tunnel_process.poll() is not None:
                    logger.error("Tunnel process died")
                    return False
                
                # Read a line from stdout
                line = self.tunnel_process.stdout.readline()
                if line and "trycloudflare.com" in line:
                    # Extract URL
                    url_match = re.search(r'https://[a-zA-Z0-9-]+\.trycloudflare\.com', line)
                    if url_match:
                        self.tunnel_url = url_match.group(0)
                        logger.info(f"✅ Tunnel created: {self.tunnel_url}")
                        return True
                
                time.sleep(0.5)
            
            logger.error("Failed to get tunnel URL")
            return False
            
        except Exception as e:
            logger.error(f"Error creating tunnel: {e}")
            return False
    
    def save_tunnel_info(self):
        """Save tunnel info to file."""
        if self.tunnel_url:
            tunnel_info = {
                'url': self.tunnel_url,
                'created': time.time(),
                'domain_setup_instructions': {
                    'domain': 'nkllon.com',
                    'subdomain': 'observatory',
                    'full_domain': 'observatory.nkllon.com',
                    'dns_setup': [
                        "Option 1 - Squarespace DNS:",
                        "1. Log into your Squarespace account",
                        "2. Go to Settings > Domains > nkllon.com",
                        "3. Click 'DNS Settings'",
                        "4. Add CNAME record:",
                        "   Name: observatory",
                        f"   Value: {self.tunnel_url.replace('https://', '')}",
                        "",
                        "Option 2 - NSOne DNS (if you have access):",
                        "1. Log into NSOne dashboard",
                        "2. Find zone nkllon.com",
                        "3. Add CNAME record:",
                        "   Name: observatory",
                        f"   Value: {self.tunnel_url.replace('https://', '')}",
                        "",
                        "After DNS setup, your Observatory will be available at:",
                        "https://observatory.nkllon.com"
                    ]
                }
            }
            
            with open('tunnel_info.json', 'w') as f:
                json.dump(tunnel_info, f, indent=2)
            
            logger.info("Tunnel info saved to tunnel_info.json")
    
    def monitor_tunnel(self):
        """Monitor tunnel and restart if needed."""
        logger.info("Monitoring tunnel...")
        
        while self.running:
            try:
                if self.tunnel_process and self.tunnel_process.poll() is not None:
                    logger.warning("Tunnel died, restarting...")
                    if self.create_tunnel():
                        self.save_tunnel_info()
                        self.print_status()
                
                time.sleep(30)  # Check every 30 seconds
                
            except Exception as e:
                logger.error(f"Error in monitoring: {e}")
                time.sleep(10)
    
    def print_status(self):
        """Print current status."""
        if self.tunnel_url:
            print(f"""
🚀 Beast Mode Observatory Tunnel Status:

📊 Current URL: {self.tunnel_url}
🎯 Target Domain: https://observatory.nkllon.com (after DNS setup)

📋 DNS Setup Instructions:
1. Log into your domain provider (Squarespace or NSOne)
2. Add a CNAME record:
   Name: observatory
   Value: {self.tunnel_url.replace('https://', '')}
3. Wait for DNS propagation (5-30 minutes)
4. Access your Observatory at: https://observatory.nkllon.com

💡 Current tunnel will stay active as long as this script runs.
""")
    
    def run(self):
        """Main run method."""
        logger.info("Starting Stable Tunnel Manager...")
        
        # Ensure Observatory is running
        if not self.ensure_observatory_running():
            logger.error("Failed to start Observatory service")
            return False
        
        # Create tunnel
        if not self.create_tunnel():
            logger.error("Failed to create tunnel")
            return False
        
        # Save info and print status
        self.save_tunnel_info()
        self.print_status()
        
        # Monitor tunnel
        self.monitor_tunnel()
        
        return True

def main():
    tunnel = StableTunnel()
    try:
        tunnel.run()
    except KeyboardInterrupt:
        logger.info("Received interrupt, shutting down...")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")

if __name__ == "__main__":
    main()