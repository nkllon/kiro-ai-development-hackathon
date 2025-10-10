"""
WebSocket-Specific Ingress Rule Creation

Handles WebSocket-specific configuration for Cloudflare tunnel ingress rules.
Implements proper WebSocket upgrade handling and connection management.
"""

import json
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class WebSocketMode(Enum):
    """WebSocket connection modes"""
    ENABLED = "enabled"
    DISABLED = "disabled"
    AUTO = "auto"


@dataclass
class WebSocketConfig:
    """WebSocket-specific configuration parameters"""
    enabled: bool = True
    upgrade_timeout: int = 30
    ping_interval: int = 30
    ping_timeout: int = 10
    max_message_size: int = 1048576  # 1MB
    compression_enabled: bool = True
    subprotocols: List[str] = None
    
    def __post_init__(self):
        if self.subprotocols is None:
            self.subprotocols = ["websocket"]


class WebSocketIngressManager:
    """Manages WebSocket-specific ingress rules for Cloudflare tunnels"""
    
    def __init__(self):
        # Log initialization
        self._log_action("init", "in_progress", {
            "websocket_modes": [mode.value for mode in WebSocketMode],
            "compression_support": True
        })
        
        logger.info("WebSocketIngressManager initialized")
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
    
    def create_websocket_ingress_rule(
        self,
        hostname: str,
        service_url: str,
        websocket_config: WebSocketConfig,
        additional_headers: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        Create WebSocket-enabled ingress rule
        
        Args:
            hostname: Target hostname
            service_url: Service URL to proxy
            websocket_config: WebSocket configuration
            additional_headers: Additional HTTP headers
            
        Returns:
            Ingress rule dictionary
        """
        self._log_action("create_websocket_ingress_rule", "in_progress", {
            "hostname": hostname,
            "service_url": service_url,
            "websocket_enabled": websocket_config.enabled,
            "compression": websocket_config.compression_enabled
        })
        
        try:
            # Base ingress rule
            ingress_rule = {
                "hostname": hostname,
                "service": service_url,
                "originRequest": {
                    "httpHostHeader": hostname,
                    "connectTimeout": f"{websocket_config.upgrade_timeout}s",
                    "tlsTimeout": "10s",
                    "tcpKeepAlive": "30s",
                    "keepAliveConnections": 10,
                    "keepAliveTimeout": "90s"
                }
            }
            
            # WebSocket-specific configuration
            if websocket_config.enabled:
                # Enable WebSocket upgrade
                ingress_rule["originRequest"]["proxyType"] = ""
                
                # WebSocket connection settings
                ingress_rule["originRequest"]["noTLSVerify"] = False
                ingress_rule["originRequest"]["disableChunkedEncoding"] = False
                
                # Add WebSocket-specific headers
                websocket_headers = {
                    "Connection": "Upgrade",
                    "Upgrade": "websocket",
                    "Sec-WebSocket-Version": "13"
                }
                
                # Add compression header if enabled
                if websocket_config.compression_enabled:
                    websocket_headers["Sec-WebSocket-Extensions"] = "permessage-deflate"
                
                # Add subprotocols if specified
                if websocket_config.subprotocols:
                    websocket_headers["Sec-WebSocket-Protocol"] = ", ".join(websocket_config.subprotocols)
                
                # Merge with additional headers
                if additional_headers:
                    websocket_headers.update(additional_headers)
                
                # Add headers to originRequest
                ingress_rule["originRequest"]["httpHostHeader"] = hostname
                ingress_rule["originRequest"]["originServerName"] = hostname
                
                # Store WebSocket headers for reference
                ingress_rule["websocketHeaders"] = websocket_headers
            
            self._log_action("create_websocket_ingress_rule", "completed", {
                "ingress_rule_created": True,
                "websocket_headers": len(ingress_rule.get("websocketHeaders", {})),
                "proxy_type": ingress_rule["originRequest"].get("proxyType", "none")
            })
            
            return ingress_rule
            
        except Exception as e:
            self._log_action("create_websocket_ingress_rule", "error", {
                "error": str(e),
                "error_type": type(e).__name__
            })
            raise
    
    def create_websocket_catch_all_rule(self) -> Dict[str, Any]:
        """
        Create catch-all rule for unmatched WebSocket requests
        
        Returns:
            Catch-all ingress rule
        """
        self._log_action("create_websocket_catch_all_rule", "in_progress", {})
        
        try:
            catch_all_rule = {
                "service": "http_status:404"
            }
            
            self._log_action("create_websocket_catch_all_rule", "completed", {
                "catch_all_created": True
            })
            
            return catch_all_rule
            
        except Exception as e:
            self._log_action("create_websocket_catch_all_rule", "error", {
                "error": str(e),
                "error_type": type(e).__name__
            })
            raise
    
    def create_websocket_tunnel_config(
        self,
        tunnel_name: str,
        credentials_file: str,
        hostname: str,
        service_url: str,
        websocket_config: WebSocketConfig
    ) -> Dict[str, Any]:
        """
        Create complete WebSocket-enabled tunnel configuration
        
        Args:
            tunnel_name: Name of the tunnel
            credentials_file: Path to credentials file
            hostname: Target hostname
            service_url: Service URL to proxy
            websocket_config: WebSocket configuration
            
        Returns:
            Complete tunnel configuration
        """
        self._log_action("create_websocket_tunnel_config", "in_progress", {
            "tunnel_name": tunnel_name,
            "hostname": hostname,
            "websocket_enabled": websocket_config.enabled
        })
        
        try:
            # Create WebSocket ingress rule
            websocket_ingress = self.create_websocket_ingress_rule(
                hostname, service_url, websocket_config
            )
            
            # Create catch-all rule
            catch_all_rule = self.create_websocket_catch_all_rule()
            
            # Assemble complete configuration
            config = {
                "tunnel": tunnel_name,
                "credentials-file": credentials_file,
                "ingress": [websocket_ingress, catch_all_rule]
            }
            
            self._log_action("create_websocket_tunnel_config", "completed", {
                "config_created": True,
                "ingress_rules": len(config["ingress"]),
                "websocket_support": websocket_config.enabled
            })
            
            return config
            
        except Exception as e:
            self._log_action("create_websocket_tunnel_config", "error", {
                "error": str(e),
                "error_type": type(e).__name__
            })
            raise
    
    def validate_websocket_ingress(self, ingress_rule: Dict[str, Any]) -> bool:
        """
        Validate WebSocket ingress rule
        
        Args:
            ingress_rule: Ingress rule to validate
            
        Returns:
            True if valid, False otherwise
        """
        self._log_action("validate_websocket_ingress", "in_progress", {
            "rule_keys": list(ingress_rule.keys())
        })
        
        try:
            # Check required fields
            required_fields = ["hostname", "service"]
            for field in required_fields:
                if field not in ingress_rule:
                    self._log_action("validate_websocket_ingress", "error", {
                        "missing_field": field,
                        "validation": "failed"
                    })
                    return False
            
            # Check originRequest for WebSocket support
            origin_request = ingress_rule.get("originRequest", {})
            if not origin_request:
                self._log_action("validate_websocket_ingress", "error", {
                    "issue": "missing_origin_request",
                    "validation": "failed"
                })
                return False
            
            # Check for WebSocket upgrade support
            proxy_type = origin_request.get("proxyType", "")
            if proxy_type != "":
                self._log_action("validate_websocket_ingress", "error", {
                    "issue": "websocket_upgrade_not_enabled",
                    "proxy_type": proxy_type,
                    "validation": "failed"
                })
                return False
            
            self._log_action("validate_websocket_ingress", "completed", {
                "validation": "passed",
                "websocket_support": True
            })
            
            return True
            
        except Exception as e:
            self._log_action("validate_websocket_ingress", "error", {
                "error": str(e),
                "error_type": type(e).__name__
            })
            return False
    
    def get_websocket_headers_template(self) -> Dict[str, str]:
        """
        Get WebSocket headers template
        
        Returns:
            Template WebSocket headers
        """
        self._log_action("get_websocket_headers_template", "in_progress", {})
        
        template = {
            "Connection": "Upgrade",
            "Upgrade": "websocket",
            "Sec-WebSocket-Version": "13",
            "Sec-WebSocket-Extensions": "permessage-deflate",
            "Sec-WebSocket-Protocol": "websocket"
        }
        
        self._log_action("get_websocket_headers_template", "completed", {
            "headers_count": len(template)
        })
        
        return template
    
    def create_multiple_websocket_rules(
        self,
        rules_config: List[Dict[str, Any]],
        websocket_config: WebSocketConfig
    ) -> List[Dict[str, Any]]:
        """
        Create multiple WebSocket ingress rules
        
        Args:
            rules_config: List of rule configurations
            websocket_config: WebSocket configuration
            
        Returns:
            List of ingress rules
        """
        self._log_action("create_multiple_websocket_rules", "in_progress", {
            "rules_count": len(rules_config),
            "websocket_enabled": websocket_config.enabled
        })
        
        try:
            ingress_rules = []
            
            for rule_config in rules_config:
                ingress_rule = self.create_websocket_ingress_rule(
                    rule_config["hostname"],
                    rule_config["service_url"],
                    websocket_config,
                    rule_config.get("additional_headers")
                )
                ingress_rules.append(ingress_rule)
            
            # Add catch-all rule
            catch_all_rule = self.create_websocket_catch_all_rule()
            ingress_rules.append(catch_all_rule)
            
            self._log_action("create_multiple_websocket_rules", "completed", {
                "rules_created": len(ingress_rules),
                "catch_all_included": True
            })
            
            return ingress_rules
            
        except Exception as e:
            self._log_action("create_multiple_websocket_rules", "error", {
                "error": str(e),
                "error_type": type(e).__name__
            })
            raise