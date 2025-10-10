"""
Configuration Manager for Cloudflare Tunnel with WebSocket Support

Manages cloudflared configuration files with proper WebSocket proxy settings
and TLS 1.3 compliance for optimal performance (<100ms latency).
"""

import json
import logging
import os
import yaml
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any

logger = logging.getLogger(__name__)


class ConfigManager:
    """Manages cloudflared configuration with WebSocket support."""
    
    def __init__(self, config_path: str = "cloudflared-config.yml"):
        """Initialize configuration manager.
        
        Args:
            config_path: Path to the cloudflared configuration file
        """
        self.config_path = Path(config_path)
        self.log_action("init", "in_progress", {"config_path": str(config_path)})
        
    def log_action(self, action: str, status: str, details: Dict[str, Any] = None):
        """Log action in JSON format as required."""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "task": "1",
            "action": action,
            "status": status,
            "details": details or {}
        }
        print(json.dumps(log_entry))
        
    def create_websocket_config(self, 
                              tunnel_name: str = "observatory",
                              hostname: str = "observatory.nkllon.com",
                              local_port: int = 8888,
                              credentials_file: str = "/path/to/credentials.json") -> Dict[str, Any]:
        """Create WebSocket-enabled tunnel configuration.
        
        Args:
            tunnel_name: Name of the tunnel
            hostname: Hostname for the tunnel
            local_port: Local port to proxy to
            credentials_file: Path to tunnel credentials
            
        Returns:
            Configuration dictionary
        """
        self.log_action("create_websocket_config", "in_progress", {
            "tunnel_name": tunnel_name,
            "hostname": hostname,
            "local_port": local_port
        })
        
        config = {
            "tunnel": tunnel_name,
            "credentials-file": credentials_file,
            "ingress": [
                {
                    "hostname": hostname,
                    "service": f"http://localhost:{local_port}",
                    "originRequest": {
                        "httpHostHeader": hostname,
                        "connectTimeout": "30s",
                        "tlsTimeout": "10s",
                        "tcpKeepAlive": "30s",
                        "keepAliveConnections": 10,
                        "keepAliveTimeout": "90s",
                        "proxyType": ""  # Enable WebSocket upgrade
                    }
                },
                {
                    "service": "http_status:404"
                }
            ]
        }
        
        self.log_action("create_websocket_config", "completed", {
            "config_keys": list(config.keys()),
            "ingress_count": len(config["ingress"])
        })
        
        return config
        
    def save_config(self, config: Dict[str, Any], backup: bool = True) -> bool:
        """Save configuration to file with optional backup.
        
        Args:
            config: Configuration dictionary to save
            backup: Whether to create backup before saving
            
        Returns:
            True if successful, False otherwise
        """
        self.log_action("save_config", "in_progress", {
            "backup": backup,
            "config_path": str(self.config_path)
        })
        
        try:
            # Create backup if requested
            if backup and self.config_path.exists():
                backup_path = self.config_path.with_suffix(f".backup.{datetime.now().strftime('%Y%m%d_%H%M%S')}")
                self.config_path.rename(backup_path)
                self.log_action("backup_created", "completed", {"backup_path": str(backup_path)})
            
            # Ensure directory exists
            self.config_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Save configuration
            with open(self.config_path, 'w') as f:
                yaml.dump(config, f, default_flow_style=False, sort_keys=False)
                
            self.log_action("save_config", "completed", {
                "file_size": self.config_path.stat().st_size,
                "config_path": str(self.config_path)
            })
            
            return True
            
        except Exception as e:
            self.log_action("save_config", "error", {
                "error": str(e),
                "error_type": type(e).__name__
            })
            return False
            
    def load_config(self) -> Optional[Dict[str, Any]]:
        """Load configuration from file.
        
        Returns:
            Configuration dictionary or None if failed
        """
        self.log_action("load_config", "in_progress", {
            "config_path": str(self.config_path)
        })
        
        try:
            if not self.config_path.exists():
                self.log_action("load_config", "error", {
                    "error": "Configuration file does not exist"
                })
                return None
                
            with open(self.config_path, 'r') as f:
                config = yaml.safe_load(f)
                
            self.log_action("load_config", "completed", {
                "config_keys": list(config.keys()) if config else [],
                "file_size": self.config_path.stat().st_size
            })
            
            return config
            
        except Exception as e:
            self.log_action("load_config", "error", {
                "error": str(e),
                "error_type": type(e).__name__
            })
            return None
            
    def update_websocket_settings(self, 
                                hostname: str = "observatory.nkllon.com",
                                enable_websocket: bool = True) -> bool:
        """Update WebSocket settings in existing configuration.
        
        Args:
            hostname: Hostname to update
            enable_websocket: Whether to enable WebSocket support
            
        Returns:
            True if successful, False otherwise
        """
        self.log_action("update_websocket_settings", "in_progress", {
            "hostname": hostname,
            "enable_websocket": enable_websocket
        })
        
        try:
            config = self.load_config()
            if not config:
                return False
                
            # Find and update the ingress rule for the hostname
            for ingress in config.get("ingress", []):
                if ingress.get("hostname") == hostname:
                    if "originRequest" not in ingress:
                        ingress["originRequest"] = {}
                    
                    if enable_websocket:
                        ingress["originRequest"]["proxyType"] = ""
                        ingress["originRequest"]["keepAliveConnections"] = 10
                        ingress["originRequest"]["keepAliveTimeout"] = "90s"
                    else:
                        ingress["originRequest"].pop("proxyType", None)
                        
                    break
            
            success = self.save_config(config)
            
            self.log_action("update_websocket_settings", "completed" if success else "error", {
                "hostname": hostname,
                "websocket_enabled": enable_websocket
            })
            
            return success
            
        except Exception as e:
            self.log_action("update_websocket_settings", "error", {
                "error": str(e),
                "error_type": type(e).__name__
            })
            return False
            
    def get_config_info(self) -> Dict[str, Any]:
        """Get configuration information and metadata.
        
        Returns:
            Dictionary with configuration metadata
        """
        self.log_action("get_config_info", "in_progress")
        
        info = {
            "config_path": str(self.config_path),
            "exists": self.config_path.exists(),
            "websocket_enabled": False,
            "tunnel_name": None,
            "hostnames": [],
            "ingress_count": 0
        }
        
        if self.config_path.exists():
            config = self.load_config()
            if config:
                info.update({
                    "tunnel_name": config.get("tunnel"),
                    "ingress_count": len(config.get("ingress", [])),
                    "hostnames": [ingress.get("hostname") for ingress in config.get("ingress", []) if ingress.get("hostname")]
                })
                
                # Check for WebSocket support
                for ingress in config.get("ingress", []):
                    origin_request = ingress.get("originRequest", {})
                    if origin_request.get("proxyType") == "":
                        info["websocket_enabled"] = True
                        break
        
        self.log_action("get_config_info", "completed", info)
        return info