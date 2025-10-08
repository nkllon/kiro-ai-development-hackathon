"""
Cloudflare API Client for Observatory Integration

Provides low-level integration with Cloudflare API v4 for managing
firewall rules, rate limiting, and bot protection configuration.
"""

import asyncio
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import aiohttp
import backoff

logger = logging.getLogger(__name__)


@dataclass
class CloudflareConfig:
    """Configuration for Cloudflare API client"""
    api_token: str
    zone_id: str
    base_url: str = "https://api.cloudflare.com/client/v4"
    timeout: int = 30
    max_retries: int = 3


class CloudflareAPIError(Exception):
    """Custom exception for Cloudflare API errors"""
    
    def __init__(self, message: str, status_code: Optional[int] = None, 
                 response_data: Optional[Dict] = None):
        super().__init__(message)
        self.status_code = status_code
        self.response_data = response_data


class CloudflareAPIClient:
    """
    Low-level client for Cloudflare API v4 integration
    
    Handles authentication, rate limiting, retries, and error handling
    for all Cloudflare API operations.
    """
    
    def __init__(self, config: CloudflareConfig):
        self.config = config
        self.session: Optional[aiohttp.ClientSession] = None
        self._log_action("api_client_init", "in_progress", {
            "zone_id": config.zone_id,
            "base_url": config.base_url
        })
    
    async def __aenter__(self):
        """Async context manager entry"""
        await self._create_session()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self._close_session()
    
    def _log_action(self, action: str, status: str, details: Dict[str, Any]):
        """Log action in JSON format as required"""
        log_entry = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "task": "5.1",
            "action": action,
            "status": status,
            "details": details
        }
        print(json.dumps(log_entry))
        logger.info(f"Cloudflare API action: {action} - {status}")
    
    async def _create_session(self):
        """Create aiohttp session with proper headers"""
        headers = {
            "Authorization": f"Bearer {self.config.api_token}",
            "Content-Type": "application/json",
            "User-Agent": "Observatory-Cloudflare-Integration/1.0"
        }
        
        timeout = aiohttp.ClientTimeout(total=self.config.timeout)
        self.session = aiohttp.ClientSession(
            headers=headers,
            timeout=timeout
        )
        
        self._log_action("session_created", "completed", {
            "timeout": self.config.timeout
        })
    
    async def _close_session(self):
        """Close aiohttp session"""
        if self.session:
            await self.session.close()
            self._log_action("session_closed", "completed", {})
    
    @backoff.on_exception(
        backoff.expo,
        (aiohttp.ClientError, asyncio.TimeoutError),
        max_tries=3,
        max_time=60
    )
    async def _make_request(self, method: str, endpoint: str, 
                          data: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Make authenticated request to Cloudflare API with retry logic
        
        Args:
            method: HTTP method (GET, POST, PUT, DELETE)
            endpoint: API endpoint (relative to base URL)
            data: Request body data
            
        Returns:
            Parsed JSON response
            
        Raises:
            CloudflareAPIError: For API errors or network issues
        """
        if not self.session:
            await self._create_session()
        
        url = f"{self.config.base_url}{endpoint}"
        
        self._log_action("api_request", "in_progress", {
            "method": method,
            "endpoint": endpoint,
            "url": url
        })
        
        try:
            async with self.session.request(method, url, json=data) as response:
                response_data = await response.json()
                
                if response.status >= 400:
                    error_msg = f"API request failed: {response.status}"
                    if response_data.get("errors"):
                        error_msg += f" - {response_data['errors']}"
                    
                    self._log_action("api_request", "error", {
                        "status_code": response.status,
                        "error": error_msg,
                        "response_data": response_data
                    })
                    
                    raise CloudflareAPIError(
                        error_msg, 
                        response.status, 
                        response_data
                    )
                
                self._log_action("api_request", "completed", {
                    "status_code": response.status,
                    "success": response_data.get("success", False)
                })
                
                return response_data
                
        except aiohttp.ClientError as e:
            self._log_action("api_request", "error", {
                "error_type": "client_error",
                "error": str(e)
            })
            raise CloudflareAPIError(f"Network error: {e}")
        except asyncio.TimeoutError as e:
            self._log_action("api_request", "error", {
                "error_type": "timeout",
                "error": str(e)
            })
            raise CloudflareAPIError(f"Request timeout: {e}")
    
    async def get_zone_info(self) -> Dict[str, Any]:
        """Get zone information"""
        endpoint = f"/zones/{self.config.zone_id}"
        return await self._make_request("GET", endpoint)
    
    async def list_firewall_rules(self) -> List[Dict[str, Any]]:
        """List all firewall rules for the zone"""
        endpoint = f"/zones/{self.config.zone_id}/firewall/rules"
        response = await self._make_request("GET", endpoint)
        return response.get("result", [])
    
    async def create_firewall_rule(self, rule_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new firewall rule"""
        endpoint = f"/zones/{self.config.zone_id}/firewall/rules"
        data = {"rules": [rule_data]}
        response = await self._make_request("POST", endpoint, data)
        return response.get("result", [{}])[0]
    
    async def update_firewall_rule(self, rule_id: str, rule_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update an existing firewall rule"""
        endpoint = f"/zones/{self.config.zone_id}/firewall/rules/{rule_id}"
        response = await self._make_request("PUT", endpoint, rule_data)
        return response.get("result", {})
    
    async def delete_firewall_rule(self, rule_id: str) -> bool:
        """Delete a firewall rule"""
        endpoint = f"/zones/{self.config.zone_id}/firewall/rules/{rule_id}"
        response = await self._make_request("DELETE", endpoint)
        return response.get("success", False)
    
    async def list_rate_limit_rules(self) -> List[Dict[str, Any]]:
        """List all rate limiting rules for the zone"""
        endpoint = f"/zones/{self.config.zone_id}/rate_limits"
        response = await self._make_request("GET", endpoint)
        return response.get("result", [])
    
    async def create_rate_limit_rule(self, rule_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new rate limiting rule"""
        endpoint = f"/zones/{self.config.zone_id}/rate_limits"
        response = await self._make_request("POST", endpoint, rule_data)
        return response.get("result", {})
    
    async def get_bot_management_config(self) -> Dict[str, Any]:
        """Get bot management configuration"""
        endpoint = f"/zones/{self.config.zone_id}/bot_management"
        response = await self._make_request("GET", endpoint)
        return response.get("result", {})
    
    async def update_bot_management_config(self, config_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update bot management configuration"""
        endpoint = f"/zones/{self.config.zone_id}/bot_management"
        response = await self._make_request("PUT", endpoint, config_data)
        return response.get("result", {})
    
    async def get_security_events(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get recent security events from the zone"""
        endpoint = f"/zones/{self.config.zone_id}/security/events"
        params = {"limit": limit}
        response = await self._make_request("GET", endpoint)
        return response.get("result", [])
    
    async def test_connection(self) -> bool:
        """Test API connection and authentication"""
        try:
            await self.get_zone_info()
            self._log_action("connection_test", "completed", {
                "zone_id": self.config.zone_id
            })
            return True
        except CloudflareAPIError as e:
            self._log_action("connection_test", "error", {
                "error": str(e),
                "status_code": e.status_code
            })
            return False