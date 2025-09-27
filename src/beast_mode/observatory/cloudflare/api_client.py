"""
Cloudflare API Client for Zone Management and Firewall Rules.

Handles authentication, rate limiting, and API communication with Cloudflare.
"""

import asyncio
import json
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional
from urllib.parse import urljoin

import aiohttp
from pydantic import BaseModel, Field


class CloudflareAPIError(Exception):
    """Exception raised for Cloudflare API errors."""
    
    def __init__(self, message: str, status_code: Optional[int] = None, response_data: Optional[Dict] = None):
        super().__init__(message)
        self.status_code = status_code
        self.response_data = response_data


class CloudflareAPIClient:
    """Client for interacting with Cloudflare API v4."""
    
    BASE_URL = "https://api.cloudflare.com/client/v4"
    
    def __init__(self, api_token: str, timeout: int = 30):
        self.api_token = api_token
        self.timeout = timeout
        self.session: Optional[aiohttp.ClientSession] = None
        self.logger = logging.getLogger(__name__)
        
    async def __aenter__(self):
        """Async context manager entry."""
        await self._ensure_session()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self.session:
            await self.session.close()
            
    async def _ensure_session(self):
        """Ensure HTTP session is available."""
        if not self.session or self.session.closed:
            timeout = aiohttp.ClientTimeout(total=self.timeout)
            headers = {
                "Authorization": f"Bearer {self.api_token}",
                "Content-Type": "application/json",
            }
            self.session = aiohttp.ClientSession(
                timeout=timeout,
                headers=headers
            )
            
    async def _make_request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
        retries: int = 3
    ) -> Dict[str, Any]:
        """Make HTTP request to Cloudflare API with retry logic."""
        await self._ensure_session()
        
        url = urljoin(self.BASE_URL, endpoint)
        
        for attempt in range(retries + 1):
            try:
                self.logger.info(f"Making {method} request to {endpoint} (attempt {attempt + 1})")
                
                async with self.session.request(
                    method=method,
                    url=url,
                    json=data,
                    params=params
                ) as response:
                    response_data = await response.json()
                    
                    if response.status == 429:  # Rate limited
                        if attempt < retries:
                            retry_after = int(response.headers.get("Retry-After", 60))
                            self.logger.warning(f"Rate limited, retrying after {retry_after} seconds")
                            await asyncio.sleep(retry_after)
                            continue
                        else:
                            raise CloudflareAPIError(
                                "Rate limit exceeded after retries",
                                status_code=response.status,
                                response_data=response_data
                            )
                    
                    if not response.ok:
                        raise CloudflareAPIError(
                            f"API request failed: {response_data.get('errors', [{}])[0].get('message', 'Unknown error')}",
                            status_code=response.status,
                            response_data=response_data
                        )
                    
                    return response_data
                    
            except aiohttp.ClientError as e:
                if attempt < retries:
                    self.logger.warning(f"Request failed, retrying: {e}")
                    await asyncio.sleep(2 ** attempt)  # Exponential backoff
                    continue
                else:
                    raise CloudflareAPIError(f"Request failed after retries: {e}")
                    
        raise CloudflareAPIError("Max retries exceeded")
        
    async def get_zone_info(self, zone_id: str) -> Dict[str, Any]:
        """Get zone information."""
        return await self._make_request("GET", f"zones/{zone_id}")
        
    async def list_firewall_rules(self, zone_id: str, page: int = 1, per_page: int = 100) -> Dict[str, Any]:
        """List firewall rules for a zone."""
        params = {"page": page, "per_page": per_page}
        return await self._make_request("GET", f"zones/{zone_id}/firewall/rules", params=params)
        
    async def create_firewall_rule(self, zone_id: str, rule_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new firewall rule."""
        return await self._make_request("POST", f"zones/{zone_id}/firewall/rules", data=rule_data)
        
    async def update_firewall_rule(self, zone_id: str, rule_id: str, rule_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update an existing firewall rule."""
        return await self._make_request("PUT", f"zones/{zone_id}/firewall/rules/{rule_id}", data=rule_data)
        
    async def delete_firewall_rule(self, zone_id: str, rule_id: str) -> Dict[str, Any]:
        """Delete a firewall rule."""
        return await self._make_request("DELETE", f"zones/{zone_id}/firewall/rules/{rule_id}")
        
    async def list_rate_limit_rules(self, zone_id: str, page: int = 1, per_page: int = 100) -> Dict[str, Any]:
        """List rate limit rules for a zone."""
        params = {"page": page, "per_page": per_page}
        return await self._make_request("GET", f"zones/{zone_id}/rate_limits", params=params)
        
    async def create_rate_limit_rule(self, zone_id: str, rule_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new rate limit rule."""
        return await self._make_request("POST", f"zones/{zone_id}/rate_limits", data=rule_data)
        
    async def get_bot_management_config(self, zone_id: str) -> Dict[str, Any]:
        """Get bot management configuration."""
        return await self._make_request("GET", f"zones/{zone_id}/bot_management")
        
    async def update_bot_management_config(self, zone_id: str, config_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update bot management configuration."""
        return await self._make_request("PUT", f"zones/{zone_id}/bot_management", data=config_data)
        
    async def get_security_events(self, zone_id: str, start_time: Optional[datetime] = None, end_time: Optional[datetime] = None) -> Dict[str, Any]:
        """Get security events for analysis."""
        params = {}
        if start_time:
            params["since"] = start_time.isoformat()
        if end_time:
            params["until"] = end_time.isoformat()
            
        return await self._make_request("GET", f"zones/{zone_id}/security/events", params=params)