#!/usr/bin/env python3
"""
Permanent Tunnel Manager for Beast Mode Observatory
Ensures both the Observatory service and tunnel are always running.
"""

import subprocess
import time
import json
import os
import sys
import signal
import logging
from pathlib import Path
from typing import Optional, Dict, Any

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('tunnel_manager.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class PermanentTunnelManager:
    def __init__(self):
        self.observatory_pid: Optional[int] = None
        self.tunnel_pid: Optional[int] = None
        self.tunnel_url: Optional[str] = None
        self.config_file = Path("tunnel_config.json")
        self.running = True
        
        # Register signal handlers
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals gracefully."""
        logger.info(f"Received signal {signum}, shutting down...")
        self.running = False
        self.cleanup()
        sys.exit(0)
    
    def check_observatory_service(self) -> bool:
        """Check if Observatory service is running."""
        try:
            result = subprocess.run(
                ["python3", "scripts/observatory-daemon.py", "status"],
                capture_output=True,
                text=True,
                timeout=10
            )
            return result.returncode == 0
        except Exception as e:
            logger.error(f"Error checking Observatory service: {e}")
            return False
    
    def start_observatory_service(self) -> bool:
        """Start the Observatory service."""
        try:
            logger.info("Starting Observatory service...")
            result = subprocess.run(
                ["python3", "scripts/observatory-daemon.py", "start"],
                capture_output=True,
                text=True,
                timeout=30
            )
            if result.returncode == 0:
                logger.info("Observatory service started successfully")
                return True
            else:
                logger.error(f"Failed to start Observatory service: {result.stderr}")
                return False
        except Exception as e:
            logger.error(f"Error starting Observatory service: {e}")
            return False
    
    def create_named_tunnel(self) -> Optional[str]:
        """Create a named Cloudflare tunnel for persistence."""
        try:
            # Check if we already have a tunnel configured
            if self.config_file.exists():
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                    if 'tunnel_name' in config:
                        return self.start_existing_tunnel(config['tunnel_name'])
            
            # Create new named tunnel
            tunnel_name = f"beast-mode-observatory-{int(time.time())}"
            logger.info(f"Creating named tunnel: {tunnel_name}")
            
            # Create tunnel
            result = subprocess.run([
                "cloudflared", "tunnel", "create", tunnel_name
            ], capture_output=True, text=True)
            
            if result.returncode != 0:
                logger.error(f"Failed to create tunnel: {result.stderr}")
                return None
            
            # Configure tunnel
            config_content = f"""
tunnel: {tunnel_name}
credentials-file: ~/.cloudflared/{tunnel_name}.json

ingress:
  - hostname: {tunnel_name}.cfargotunnel.com
    service: http://localhost:8888
  - service: http_status:404
"""
            
            config_path = Path.home() / ".cloudflared" / "config.yml"
            with open(config_path, 'w') as f:
                f.write(config_content)
            
            # Save our config
            with open(self.config_file, 'w') as f:
                json.dump({
                    'tunnel_name': tunnel_name,
                    'tunnel_url': f"https://{tunnel_name}.cfargotunnel.com"
                }, f)
            
            return self.start_existing_tunnel(tunnel_name)
            
        except Exception as e:
            logger.error(f"Error creating named tunnel: {e}")
            return None
    
    def start_existing_tunnel(self, tunnel_name: str) -> Optional[str]:
        """Start an existing named tunnel."""
        try:
            logger.info(f"Starting tunnel: {tunnel_name}")
            
            # Start tunnel in background
            process = subprocess.Popen([
                "cloudflared", "tunnel", "run", tunnel_name
            ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            
            self.tunnel_pid = process.pid
            tunnel_url = f"https://{tunnel_name}.cfargotunnel.com"
            
            # Wait a moment for tunnel to establish
            time.sleep(5)
            
            # Check if process is still running
            if process.poll() is None:
                logger.info(f"Tunnel started successfully: {tunnel_url}")
                return tunnel_url
            else:
                logger.error("Tunnel process died immediately")
                return None
                
        except Exception as e:
            logger.error(f"Error starting tunnel: {e}")
            return None
    
    def create_quick_tunnel_fallback(self) -> Optional[str]:
        """Create a quick tunnel as fallback."""
        try:
            logger.info("Creating quick tunnel as fallback...")
            
            process = subprocess.Popen([
                "cloudflared", "tunnel", "--url", "localhost:8888"
            ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            
            self.tunnel_pid = process.pid
            
            # Parse output for tunnel URL
            for _ in range(30):  # Wait up to 30 seconds
                if process.poll() is not None:
                    break
                    
                line = process.stdout.readline()
                if "trycloudflare.com" in line:
                    # Extract URL from line
                    import re
                    url_match = re.search(r'https://[a-zA-Z0-9-]+\.trycloudflare\.com', line)
                    if url_match:
                        tunnel_url = url_match.group(0)
                        logger.info(f"Quick tunnel created: {tunnel_url}")
                        return tunnel_url
                
                time.sleep(1)
            
            logger.error("Failed to get tunnel URL from output")
            return None
            
        except Exception as e:
            logger.error(f"Error creating quick tunnel: {e}")
            return None
    
    def monitor_services(self):
        """Monitor both services and restart if needed."""
        logger.info("Starting service monitoring...")
        
        while self.running:
            try:
                # Check Observatory service
                if not self.check_observatory_service():
                    logger.warning("Observatory service is down, restarting...")
                    if not self.start_observatory_service():
                        logger.error("Failed to restart Observatory service")
                
                # Check tunnel process
                if self.tunnel_pid:
                    try:
                        os.kill(self.tunnel_pid, 0)  # Check if process exists
                    except OSError:
                        logger.warning("Tunnel process died, restarting...")
                        self.tunnel_url = self.create_quick_tunnel_fallback()
                        if self.tunnel_url:
                            logger.info(f"Tunnel restarted: {self.tunnel_url}")
                
                time.sleep(30)  # Check every 30 seconds
                
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                time.sleep(10)
    
    def cleanup(self):
        """Clean up processes on shutdown."""
        logger.info("Cleaning up...")
        
        if self.tunnel_pid:
            try:
                os.kill(self.tunnel_pid, signal.SIGTERM)
                logger.info("Tunnel process terminated")
            except OSError:
                pass
    
    def run(self):
        """Main run loop."""
        logger.info("Starting Permanent Tunnel Manager...")
        
        # Ensure Observatory service is running
        if not self.check_observatory_service():
            if not self.start_observatory_service():
                logger.error("Failed to start Observatory service")
                return False
        
        # Try to create named tunnel first, fallback to quick tunnel
        self.tunnel_url = self.create_named_tunnel()
        if not self.tunnel_url:
            logger.warning("Named tunnel failed, using quick tunnel...")
            self.tunnel_url = self.create_quick_tunnel_fallback()
        
        if not self.tunnel_url:
            logger.error("Failed to create any tunnel")
            return False
        
        logger.info(f"🚀 Beast Mode Observatory is live at: {self.tunnel_url}")
        
        # Start monitoring
        self.monitor_services()
        
        return True

def main():
    manager = PermanentTunnelManager()
    try:
        success = manager.run()
        if not success:
            sys.exit(1)
    except KeyboardInterrupt:
        logger.info("Received interrupt, shutting down...")
        manager.cleanup()
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        manager.cleanup()
        sys.exit(1)

if __name__ == "__main__":
    main()