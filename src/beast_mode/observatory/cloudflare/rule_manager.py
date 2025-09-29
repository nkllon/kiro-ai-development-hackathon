"""
Rule Manager for Cloudflare Firewall and Rate Limiting

Manages creation, updating, and deletion of Cloudflare firewall rules
and rate limiting exceptions for Observatory traffic patterns.
"""

import json
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum

from .api_client import CloudflareAPIClient, CloudflareAPIError

logger = logging.getLogger(__name__)


class RuleType(Enum):
    """Types of Cloudflare rules"""
    FIREWALL = "firewall"
    RATE_LIMIT = "rate_limit"
    BOT_MANAGEMENT = "bot_management"


class RuleAction(Enum):
    """Rule actions"""
    ALLOW = "allow"
    BLOCK = "block"
    CHALLENGE = "challenge"
    BYPASS = "bypass"


@dataclass
class ObservatoryRule:
    """Observatory-specific rule configuration"""
    name: str
    expression: str
    action: RuleAction
    description: str
    priority: int
    enabled: bool = True
    rule_type: RuleType = RuleType.FIREWALL


class RuleManager:
    """
    Manages Cloudflare firewall and rate limiting rules for Observatory
    
    Provides high-level operations for creating Observatory-specific
    whitelist rules and rate limiting exceptions.
    """
    
    # Observatory whitelist rules as specified in requirements
    OBSERVATORY_WHITELIST_RULES = [
        ObservatoryRule(
            name="observatory-internal-polling",
            expression='(http.user_agent contains "Observatory-Internal")',
            action=RuleAction.ALLOW,
            description="Observatory internal polling traffic",
            priority=1
        ),
        ObservatoryRule(
            name="observatory-websocket-endpoints",
            expression='(http.request.uri.path matches "^/ws/")',
            action=RuleAction.ALLOW,
            description="Observatory WebSocket endpoints",
            priority=2
        ),
        ObservatoryRule(
            name="observatory-polling-fallback",
            expression='(http.request.headers["x-observatory-client"][0] eq "internal-polling")',
            action=RuleAction.ALLOW,
            description="Observatory polling fallback",
            priority=3
        ),
        ObservatoryRule(
            name="observatory-health-checks",
            expression='(http.request.uri.path matches "^/health")',
            action=RuleAction.ALLOW,
            description="Observatory health check endpoints",
            priority=4
        ),
        ObservatoryRule(
            name="observatory-metrics-endpoints",
            expression='(http.request.uri.path matches "^/metrics")',
            action=RuleAction.ALLOW,
            description="Observatory metrics endpoints",
            priority=5
        )
    ]
    
    def __init__(self, api_client: CloudflareAPIClient):
        self.api_client = api_client
        self._log_action("rule_manager_init", "in_progress", {
            "rule_count": len(self.OBSERVATORY_WHITELIST_RULES)
        })
    
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
        logger.info(f"Rule Manager action: {action} - {status}")
    
    async def create_observatory_whitelist_rules(self) -> List[Dict[str, Any]]:
        """
        Create all Observatory whitelist rules
        
        Returns:
            List of created rule data
            
        Raises:
            CloudflareAPIError: If rule creation fails
        """
        self._log_action("create_whitelist_rules", "in_progress", {
            "rule_count": len(self.OBSERVATORY_WHITELIST_RULES)
        })
        
        created_rules = []
        
        try:
            for rule in self.OBSERVATORY_WHITELIST_RULES:
                rule_data = self._build_firewall_rule_data(rule)
                created_rule = await self.api_client.create_firewall_rule(rule_data)
                created_rules.append(created_rule)
                
                self._log_action("rule_created", "completed", {
                    "rule_name": rule.name,
                    "rule_id": created_rule.get("id"),
                    "expression": rule.expression
                })
            
            self._log_action("create_whitelist_rules", "completed", {
                "created_count": len(created_rules)
            })
            
            return created_rules
            
        except CloudflareAPIError as e:
            self._log_action("create_whitelist_rules", "error", {
                "error": str(e),
                "status_code": e.status_code
            })
            raise
    
    def _build_firewall_rule_data(self, rule: ObservatoryRule) -> Dict[str, Any]:
        """Build Cloudflare API format for firewall rule"""
        return {
            "action": rule.action.value,
            "expression": rule.expression,
            "description": rule.description,
            "paused": not rule.enabled,
            "priority": rule.priority
        }
    
    async def create_rate_limit_exception(self, 
                                        pattern: str,
                                        description: str,
                                        rate_limit: int = 1000) -> Dict[str, Any]:
        """
        Create rate limiting exception for Observatory traffic
        
        Args:
            pattern: Traffic pattern to exempt from rate limiting
            description: Description of the exception
            rate_limit: Higher rate limit for exempted traffic
            
        Returns:
            Created rate limit rule data
        """
        self._log_action("create_rate_limit_exception", "in_progress", {
            "pattern": pattern,
            "rate_limit": rate_limit
        })
        
        try:
            rule_data = {
                "match": {
                    "request": {
                        "url": pattern
                    }
                },
                "rate": rate_limit,
                "period": 60,  # 1 minute window
                "action": {
                    "mode": "simulate",
                    "timeout": 0,
                    "response": {
                        "content_type": "text/plain",
                        "body": "Rate limit exceeded for Observatory traffic"
                    }
                },
                "description": description,
                "disabled": False
            }
            
            created_rule = await self.api_client.create_rate_limit_rule(rule_data)
            
            self._log_action("create_rate_limit_exception", "completed", {
                "rule_id": created_rule.get("id"),
                "pattern": pattern
            })
            
            return created_rule
            
        except CloudflareAPIError as e:
            self._log_action("create_rate_limit_exception", "error", {
                "error": str(e),
                "pattern": pattern
            })
            raise
    
    async def create_observatory_rate_limit_exceptions(self) -> List[Dict[str, Any]]:
        """
        Create rate limiting exceptions for all Observatory traffic patterns
        
        Returns:
            List of created rate limit exception rules
        """
        self._log_action("create_observatory_rate_exceptions", "in_progress", {})
        
        exceptions = [
            ("/ws/*", "Observatory WebSocket connections", 5000),
            ("/health", "Observatory health checks", 10000),
            ("/metrics", "Observatory metrics collection", 2000),
            ("/api/observatory/*", "Observatory API endpoints", 3000)
        ]
        
        created_rules = []
        
        try:
            for pattern, description, rate_limit in exceptions:
                rule = await self.create_rate_limit_exception(pattern, description, rate_limit)
                created_rules.append(rule)
            
            self._log_action("create_observatory_rate_exceptions", "completed", {
                "created_count": len(created_rules)
            })
            
            return created_rules
            
        except CloudflareAPIError as e:
            self._log_action("create_observatory_rate_exceptions", "error", {
                "error": str(e)
            })
            raise
    
    async def get_existing_observatory_rules(self) -> Tuple[List[Dict], List[Dict]]:
        """
        Get existing Observatory-related rules
        
        Returns:
            Tuple of (firewall_rules, rate_limit_rules)
        """
        self._log_action("get_existing_rules", "in_progress", {})
        
        try:
            firewall_rules = await self.api_client.list_firewall_rules()
            rate_limit_rules = await self.api_client.list_rate_limit_rules()
            
            # Filter for Observatory-related rules
            observatory_firewall = [
                rule for rule in firewall_rules
                if any(keyword in rule.get("description", "").lower() 
                      for keyword in ["observatory", "internal-polling"])
            ]
            
            observatory_rate_limit = [
                rule for rule in rate_limit_rules
                if any(keyword in rule.get("description", "").lower()
                      for keyword in ["observatory", "websocket", "health", "metrics"])
            ]
            
            self._log_action("get_existing_rules", "completed", {
                "firewall_count": len(observatory_firewall),
                "rate_limit_count": len(observatory_rate_limit)
            })
            
            return observatory_firewall, observatory_rate_limit
            
        except CloudflareAPIError as e:
            self._log_action("get_existing_rules", "error", {
                "error": str(e)
            })
            raise
    
    async def update_rule_priority(self, rule_id: str, new_priority: int) -> Dict[str, Any]:
        """
        Update the priority of an existing rule
        
        Args:
            rule_id: ID of the rule to update
            new_priority: New priority value
            
        Returns:
            Updated rule data
        """
        self._log_action("update_rule_priority", "in_progress", {
            "rule_id": rule_id,
            "new_priority": new_priority
        })
        
        try:
            # Get current rule data
            firewall_rules = await self.api_client.list_firewall_rules()
            current_rule = next(
                (rule for rule in firewall_rules if rule.get("id") == rule_id),
                None
            )
            
            if not current_rule:
                raise CloudflareAPIError(f"Rule {rule_id} not found")
            
            # Update priority
            updated_data = {
                "action": current_rule.get("action"),
                "expression": current_rule.get("expression"),
                "description": current_rule.get("description"),
                "paused": current_rule.get("paused", False),
                "priority": new_priority
            }
            
            updated_rule = await self.api_client.update_firewall_rule(rule_id, updated_data)
            
            self._log_action("update_rule_priority", "completed", {
                "rule_id": rule_id,
                "old_priority": current_rule.get("priority"),
                "new_priority": new_priority
            })
            
            return updated_rule
            
        except CloudflareAPIError as e:
            self._log_action("update_rule_priority", "error", {
                "error": str(e),
                "rule_id": rule_id
            })
            raise
    
    async def disable_rule(self, rule_id: str) -> Dict[str, Any]:
        """
        Disable a rule without deleting it
        
        Args:
            rule_id: ID of the rule to disable
            
        Returns:
            Updated rule data
        """
        self._log_action("disable_rule", "in_progress", {
            "rule_id": rule_id
        })
        
        try:
            # Get current rule data
            firewall_rules = await self.api_client.list_firewall_rules()
            current_rule = next(
                (rule for rule in firewall_rules if rule.get("id") == rule_id),
                None
            )
            
            if not current_rule:
                raise CloudflareAPIError(f"Rule {rule_id} not found")
            
            # Disable rule
            updated_data = {
                "action": current_rule.get("action"),
                "expression": current_rule.get("expression"),
                "description": current_rule.get("description"),
                "paused": True,  # Disable the rule
                "priority": current_rule.get("priority")
            }
            
            updated_rule = await self.api_client.update_firewall_rule(rule_id, updated_data)
            
            self._log_action("disable_rule", "completed", {
                "rule_id": rule_id
            })
            
            return updated_rule
            
        except CloudflareAPIError as e:
            self._log_action("disable_rule", "error", {
                "error": str(e),
                "rule_id": rule_id
            })
            raise
    
    async def cleanup_observatory_rules(self) -> Dict[str, int]:
        """
        Clean up all Observatory-related rules
        
        Returns:
            Dictionary with cleanup statistics
        """
        self._log_action("cleanup_observatory_rules", "in_progress", {})
        
        try:
            observatory_firewall, observatory_rate_limit = await self.get_existing_observatory_rules()
            
            cleanup_stats = {
                "firewall_rules_deleted": 0,
                "rate_limit_rules_deleted": 0,
                "errors": 0
            }
            
            # Delete firewall rules
            for rule in observatory_firewall:
                try:
                    success = await self.api_client.delete_firewall_rule(rule.get("id"))
                    if success:
                        cleanup_stats["firewall_rules_deleted"] += 1
                except CloudflareAPIError:
                    cleanup_stats["errors"] += 1
            
            # Note: Rate limit rules deletion would require additional API calls
            # For now, we'll mark them for manual cleanup
            
            self._log_action("cleanup_observatory_rules", "completed", cleanup_stats)
            
            return cleanup_stats
            
        except CloudflareAPIError as e:
            self._log_action("cleanup_observatory_rules", "error", {
                "error": str(e)
            })
            raise