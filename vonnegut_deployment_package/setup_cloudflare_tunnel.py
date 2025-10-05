#!/usr/bin/env python3
"""
Setup proper Cloudflare tunnel with paid account
Creates a named tunnel that won't change URLs
"""

import subprocess
import json
import time
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def setup_cloudflare_tunnel():
    """Set up a proper named Cloudflare tunnel."""
    
    # First, login to Cloudflare (if not already)
    logger.info("Checking Cloudflare authentication...")
    
    try:
        result = subprocess.run([
            "cloudflared", "tunnel", "list"
        ], capture_output=True, text=True)
        
        if "login" in result.stderr.lower() or result.returncode != 0:
            logger.info("Need to authenticate with Cloudflare...")
            logger.info("Run: cloudflared tunnel login")
            logger.info("This will open a browser to authenticate with your Cloudflare account")
            return False
            
    except Exception as e:
        logger.error(f"Error checking auth: {e}")
        return False
    
    # Create named tunnel
    tunnel_name = "beast-mode-observatory"
    logger.info(f"Creating tunnel: {tunnel_name}")
    
    try:
        # Check if tunnel already exists
        result = subprocess.run([
            "cloudflared", "tunnel", "list"
        ], capture_output=True, text=True)
        
        if tunnel_name in result.stdout:
            logger.info(f"Tunnel {tunnel_name} already exists")
        else:
            # Create new tunnel
            result = subprocess.run([
                "cloudflared", "tunnel", "create", tunnel_name
            ], capture_output=True, text=True)
            
            if result.returncode != 0:
                logger.error(f"Failed to create tunnel: {result.stderr}")
                return False
            
            logger.info(f"Created tunnel: {tunnel_name}")
        
        # Create DNS record
        logger.info("Creating DNS record...")
        result = subprocess.run([
            "cloudflared", "tunnel", "route", "dns", tunnel_name, "observatory.nkllon.com"
        ], capture_output=True, text=True)
        
        if result.returncode != 0:
            logger.warning(f"DNS route creation: {result.stderr}")
            logger.info("You may need to manually add the DNS record in Cloudflare dashboard")
        else:
            logger.info("DNS record created successfully")
        
        # Create config file
        config_content = f"""tunnel: {tunnel_name}
credentials-file: ~/.cloudflared/{tunnel_name}.json

ingress:
  - hostname: observatory.nkllon.com
    service: http://localhost:8888
  - service: http_status:404
"""
        
        import os
        config_dir = os.path.expanduser("~/.cloudflared")
        os.makedirs(config_dir, exist_ok=True)
        
        config_path = os.path.join(config_dir, "config.yml")
        with open(config_path, 'w') as f:
            f.write(config_content)
        
        logger.info(f"Config written to {config_path}")
        
        # Start tunnel
        logger.info("Starting tunnel...")
        process = subprocess.Popen([
            "cloudflared", "tunnel", "run", tunnel_name
        ])
        
        logger.info(f"✅ Tunnel started! Your Observatory is now available at:")
        logger.info(f"🌐 https://observatory.nkllon.com")
        logger.info(f"📊 This URL will never change!")
        
        return True
        
    except Exception as e:
        logger.error(f"Error setting up tunnel: {e}")
        return False

if __name__ == "__main__":
    success = setup_cloudflare_tunnel()
    if not success:
        print("\n❌ Setup failed. Make sure you're authenticated with Cloudflare:")
        print("1. Run: cloudflared tunnel login")
        print("2. Complete authentication in browser")
        print("3. Run this script again")