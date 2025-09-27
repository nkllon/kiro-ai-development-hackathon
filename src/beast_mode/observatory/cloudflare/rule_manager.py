"""
Rule Manager for Cloudflare Firewall and Rate Limiting Rules.

Manages creation, updating, and deletion of firewall rules and rate limits.
"""

import json
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

from .api_client import CloudflareAPIClient, CloudflareAPIError


class RuleManager:
    """Manages Cloudflare firewall and rate limiting rules."""
    
    def __init__(self, api_client: CloudflareAPIClient):
        self.api_client = api_client
        self.logger = logging.getLogger(__name__)
        
    async def create_whitelist_rule(
        self,
        zone_id: str,
        expression: str,
        description: str,
        action: str = "allow"
    ) -> Dict[str, Any]:
        """Create a whitelist firewall rule."""
        rule_data = {
            "filter": {
                "expression": expression
            },
            "action": action,
            "description": description,
            "paused": False
        }
        
        try:
            self.logger.info(f"Creating whitelist rule: {description}")
            result = await self.api_client.create_firewall_rule(zone_id, rule_data)
            
            self.logger.info(f"Whitelist rule created successfully: {result.get('result', {}).get('id')}")
            return result
            
        except CloudflareAPIError as e:
            self.logger.error(f"Failed to create whitelist rule: {e}")
            raise
            
    async def create_rate_limit_exception(
        self,
        zone_id: str,
        match_expression: str,
        description: str,
        rate_limit: int = 1000,
        period: int = 60
    ) -> Dict[str, Any]:
        """Create a rate limit exception rule."""
        rule_data = {
            "match": {
                "request": {
                    "methods": ["GET", "POST", "PUT", "DELETE", "PATCH", "HEAD", "OPTIONS"],
                    "schemes": ["HTTP", "HTTPS"],
                    "url": match_expression
                }
            },
            "rate": rate_limit,
            "period": period,
            "action": {
                "mode": "simulate",
                "timeout": 86400,
                "response": {
                    "content_type": "text/plain",
                    "body": "Rate limit exceeded"
                }
            },
            "disabled": False,
            "description": description
        }
        
        try:
            self.logger.info(f"Creating rate limit exception: {description}")
            result = await self.api_client.create_rate_limit_rule(zone_id, rule_data)
            
            self.logger.info(f"Rate limit exception created successfully: {result.get('result', {}).get('id')}")
            return result
            
        except CloudflareAPIError as e:
            self.logger.error(f"Failed to create rate limit exception: {e}")
            raise
            
    async def update_rule_description(
        self,
        zone_id: str,
        rule_id: str,
        new_description: str,
        rule_type: str = "firewall"
    ) -> Dict[str, Any]:
        """Update rule description."""
        try:
            if rule_type == "firewall":
                # Get current rule data
                rules = await self.api_client.list_firewall_rules(zone_id)
                current_rule = None
                
                for rule in rules.get("result", []):
                    if rule["id"] == rule_id:
                        current_rule = rule
                        break
                        
                if not current_rule:
                    raise CloudflareAPIError(f"Firewall rule {rule_id} not found")
                    
                # Update with new description
                rule_data = {
                    "filter": current_rule["filter"],
                    "action": current_rule["action"],
                    "description": new_description,
                    "paused": current_rule.get("paused", False)
                }
                
                result = await self.api_client.update_firewall_rule(zone_id, rule_id, rule_data)
                
            elif rule_type == "rate_limit":
                # For rate limits, we'd need to get current data and update
                # This is a simplified implementation
                raise CloudflareAPIError("Rate limit rule updates not fully implemented")
                
            else:
                raise CloudflareAPIError(f"Unknown rule type: {rule_type}")
                
            self.logger.info(f"Rule description updated: {rule_id}")
            return result
            
        except CloudflareAPIError as e:
            self.logger.error(f"Failed to update rule description: {e}")
            raise
            
    async def delete_rule(
        self,
        zone_id: str,
        rule_id: str,
        rule_type: str = "firewall"
    ) -> Dict[str, Any]:
        """Delete a rule."""
        try:
            if rule_type == "firewall":
                result = await self.api_client.delete_firewall_rule(zone_id, rule_id)
            else:
                raise CloudflareAPIError(f"Rule deletion not implemented for type: {rule_type}")
                
            self.logger.info(f"Rule deleted successfully: {rule_id}")
            return result
            
        except CloudflareAPIError as e:
            self.logger.error(f"Failed to delete rule: {e}")
            raise
            
    async def list_observatory_rules(self, zone_id: str) -> List[Dict[str, Any]]:
        """List all rules related to Observatory."""
        try:
            firewall_rules = await self.api_client.list_firewall_rules(zone_id)
            observatory_rules = []
            
            for rule in firewall_rules.get("result", []):
                description = rule.get("description", "").lower()
                if "observatory" in description:
                    observatory_rules.append({
                        "id": rule["id"],
                        "type": "firewall",
                        "description": rule.get("description"),
                        "action": rule.get("action"),
                        "filter": rule.get("filter"),
                        "paused": rule.get("paused", False)
                    })
                    
            return observatory_rules
            
        except CloudflareAPIError as e:
            self.logger.error(f"Failed to list Observatory rules: {e}")
            raise
            
    async def validate_rule_syntax(self, expression: str) -> bool:
        """Validate firewall rule expression syntax."""
        try:
            # Basic validation - Cloudflare expressions should be valid
            # This is a simplified check
            if not expression or not isinstance(expression, str):
                return False
                
            # Check for basic structure
            if "(" not in expression or ")" not in expression:
                return False
                
            # Check for required fields
            required_fields = ["http."]
            if not any(field in expression for field in required_fields):
                return False
                
            return True
            
        except Exception as e:
            self.logger.error(f"Rule syntax validation failed: {e}")
            return False