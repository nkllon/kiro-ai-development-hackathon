"""
Cloudflare Tunnel Configuration Generator

Generates tunnel configurations with WebSocket support and proper ingress rules.
Implements safe configuration management with validation and versioning.
"""

import json
import logging
import os
import yaml
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class TunnelConfig:
    """Tunnel configuration data structure"""
    tunnel_name: str
    credentials_file: str
    hostname: str
    service_url: str
    websocket_enabled: bool = True
    connect_timeout: int = 30
    tls_timeout: int = 10
    tcp_keep_alive: int = 30
    keep_alive_connections: int = 10
    keep_alive_timeout: int = 90


class TunnelConfigGenerator:
    """Generates Cloudflare tunnel configurations with WebSocket support"""
    
    def __init__(self, config_dir: str = "/tmp/tunnel_configs"):
        self.config_dir = Path(config_dir)
        self.config_dir.mkdir(parents=True, exist_ok=True)
        
        # Log initialization
        self._log_action("init", "in_progress", {
            "config_dir": str(self.config_dir),
            "websocket_support": True
        })
        
        logger.info("TunnelConfigGenerator initialized")
        self._log_action("init", "completed", {"status": "ready"})
    
    def _log_action(self, action: str, status: str, details: Dict[str, Any] = None):
        """Log actions in JSON format as required"""
        log_entry = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "task": "7.1",
            "action": action,
            "status": status
        }
        if details:
            log_entry["details"] = details
        
        print(json.dumps(log_entry))
    
    def generate_websocket_config(self, tunnel_config: TunnelConfig) -> Dict[str, Any]:
        """
        Generate WebSocket-enabled tunnel configuration
        
        Args:
            tunnel_config: Configuration parameters
            
        Returns:
            Generated configuration dictionary
        """
        self._log_action("generate_websocket_config", "in_progress", {
            "tunnel_name": tunnel_config.tunnel_name,
            "hostname": tunnel_config.hostname,
            "websocket_enabled": tunnel_config.websocket_enabled
        })
        
        try:
            # Base configuration structure
            config = {
                "tunnel": tunnel_config.tunnel_name,
                "credentials-file": tunnel_config.credentials_file,
                "ingress": []
            }
            
            # Primary ingress rule with WebSocket support
            primary_ingress = {
                "hostname": tunnel_config.hostname,
                "service": tunnel_config.service_url,
                "originRequest": {
                    "httpHostHeader": tunnel_config.hostname,
                    "connectTimeout": f"{tunnel_config.connect_timeout}s",
                    "tlsTimeout": f"{tunnel_config.tls_timeout}s",
                    "tcpKeepAlive": f"{tunnel_config.tcp_keep_alive}s",
                    "keepAliveConnections": tunnel_config.keep_alive_connections,
                    "keepAliveTimeout": f"{tunnel_config.keep_alive_timeout}s",
                    "proxyType": ""  # Enable WebSocket upgrade
                }
            }
            
            # Add WebSocket-specific headers if enabled
            if tunnel_config.websocket_enabled:
                primary_ingress["originRequest"]["httpHostHeader"] = tunnel_config.hostname
                primary_ingress["originRequest"]["noTLSVerify"] = False
                primary_ingress["originRequest"]["disableChunkedEncoding"] = False
            
            config["ingress"].append(primary_ingress)
            
            # Catch-all rule for unmatched requests
            config["ingress"].append({
                "service": "http_status:404"
            })
            
            self._log_action("generate_websocket_config", "completed", {
                "ingress_rules": len(config["ingress"]),
                "websocket_headers": tunnel_config.websocket_enabled
            })
            
            return config
            
        except Exception as e:
            self._log_action("generate_websocket_config", "error", {
                "error": str(e),
                "error_type": type(e).__name__
            })
            raise
    
    def generate_config_file(self, tunnel_config: TunnelConfig, filename: Optional[str] = None) -> str:
        """
        Generate configuration file and save to disk
        
        Args:
            tunnel_config: Configuration parameters
            filename: Optional custom filename
            
        Returns:
            Path to generated configuration file
        """
        self._log_action("generate_config_file", "in_progress", {
            "tunnel_name": tunnel_config.tunnel_name,
            "filename": filename
        })
        
        try:
            # Generate configuration
            config = self.generate_websocket_config(tunnel_config)
            
            # Determine filename
            if not filename:
                timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
                filename = f"{tunnel_config.tunnel_name}_{timestamp}.yaml"
            
            config_path = self.config_dir / filename
            
            # Write configuration to file
            with open(config_path, 'w') as f:
                yaml.dump(config, f, default_flow_style=False, sort_keys=False)
            
            self._log_action("generate_config_file", "completed", {
                "config_path": str(config_path),
                "file_size": config_path.stat().st_size,
                "format": "yaml"
            })
            
            return str(config_path)
            
        except Exception as e:
            self._log_action("generate_config_file", "error", {
                "error": str(e),
                "error_type": type(e).__name__
            })
            raise
    
    def generate_minimal_config(self, tunnel_name: str, hostname: str, service_url: str) -> Dict[str, Any]:
        """
        Generate minimal tunnel configuration for quick setup
        
        Args:
            tunnel_name: Name of the tunnel
            hostname: Target hostname
            service_url: Service URL to proxy
            
        Returns:
            Minimal configuration dictionary
        """
        self._log_action("generate_minimal_config", "in_progress", {
            "tunnel_name": tunnel_name,
            "hostname": hostname,
            "service_url": service_url
        })
        
        try:
            config = {
                "tunnel": tunnel_name,
                "credentials-file": f"/tmp/{tunnel_name}_credentials.json",
                "ingress": [
                    {
                        "hostname": hostname,
                        "service": service_url,
                        "originRequest": {
                            "httpHostHeader": hostname,
                            "proxyType": ""
                        }
                    },
                    {
                        "service": "http_status:404"
                    }
                ]
            }
            
            self._log_action("generate_minimal_config", "completed", {
                "ingress_rules": len(config["ingress"])
            })
            
            return config
            
        except Exception as e:
            self._log_action("generate_minimal_config", "error", {
                "error": str(e),
                "error_type": type(e).__name__
            })
            raise
    
    def validate_generated_config(self, config: Dict[str, Any]) -> bool:
        """
        Validate generated configuration structure
        
        Args:
            config: Configuration dictionary to validate
            
        Returns:
            True if valid, False otherwise
        """
        self._log_action("validate_generated_config", "in_progress", {
            "config_keys": list(config.keys())
        })
        
        try:
            # Required fields
            required_fields = ["tunnel", "credentials-file", "ingress"]
            for field in required_fields:
                if field not in config:
                    self._log_action("validate_generated_config", "error", {
                        "missing_field": field,
                        "validation": "failed"
                    })
                    return False
            
            # Validate ingress rules
            if not isinstance(config["ingress"], list) or len(config["ingress"]) == 0:
                self._log_action("validate_generated_config", "error", {
                    "issue": "invalid_ingress_rules",
                    "validation": "failed"
                })
                return False
            
            # Check for catch-all rule
            has_catch_all = any(
                rule.get("service") == "http_status:404" 
                for rule in config["ingress"]
            )
            
            if not has_catch_all:
                self._log_action("validate_generated_config", "error", {
                    "issue": "missing_catch_all_rule",
                    "validation": "failed"
                })
                return False
            
            self._log_action("validate_generated_config", "completed", {
                "validation": "passed",
                "ingress_rules": len(config["ingress"]),
                "has_catch_all": has_catch_all
            })
            
            return True
            
        except Exception as e:
            self._log_action("validate_generated_config", "error", {
                "error": str(e),
                "error_type": type(e).__name__
            })
            return False
    
    def get_config_template(self) -> Dict[str, Any]:
        """
        Get configuration template for reference
        
        Returns:
            Template configuration dictionary
        """
        self._log_action("get_config_template", "in_progress", {})
        
        template = {
            "tunnel": "observatory",
            "credentials-file": "/path/to/credentials.json",
            "ingress": [
                {
                    "hostname": "observatory.nkllon.com",
                    "service": "http://localhost:8888",
                    "originRequest": {
                        "httpHostHeader": "observatory.nkllon.com",
                        "connectTimeout": "30s",
                        "tlsTimeout": "10s",
                        "tcpKeepAlive": "30s",
                        "keepAliveConnections": 10,
                        "keepAliveTimeout": "90s",
                        "proxyType": ""
                    }
                },
                {
                    "service": "http_status:404"
                }
            ]
        }
        
        self._log_action("get_config_template", "completed", {
            "template_type": "websocket_enabled"
        })
        
        return template