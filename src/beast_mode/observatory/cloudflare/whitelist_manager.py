"""
Cloudflare Whitelist Manager for Observatory Traffic.

Main orchestrator for managing Cloudflare bot protection whitelisting.
"""

import asyncio
import json
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

from .api_client import CloudflareAPIClient, CloudflareAPIError
from .rule_manager import RuleManager
from .traffic_analyzer import TrafficAnalyzer, TrafficPattern
from .security_validator import SecurityValidator, SecurityValidationResult


class CloudflareWhitelistManager:
    """Main manager for Cloudflare bot protection whitelisting."""
    
    def __init__(self, api_token: str, zone_id: str):
        self.api_token = api_token
        self.zone_id = zone_id
        self.logger = logging.getLogger(__name__)
        
        # Initialize components
        self.api_client = CloudflareAPIClient(api_token)
        self.rule_manager = RuleManager(self.api_client)
        self.traffic_analyzer = TrafficAnalyzer(self.api_client)
        self.security_validator = SecurityValidator(self.api_client)
        
        # Observatory whitelist rules
        self.observatory_rules = [
            {
                "expression": '(http.user_agent contains "Observatory-Internal")',
                "action": "allow",
                "description": "Observatory internal polling traffic"
            },
            {
                "expression": '(http.request.uri.path matches "^/ws/")',
                "action": "allow", 
                "description": "Observatory WebSocket endpoints"
            },
            {
                "expression": '(http.request.headers["x-observatory-client"][0] eq "internal-polling")',
                "action": "allow",
                "description": "Observatory polling fallback"
            },
            {
                "expression": '(http.request.uri.path matches "^/health")',
                "action": "allow",
                "description": "Observatory health check endpoints"
            },
            {
                "expression": '(http.request.uri.path matches "^/api/observatory/")',
                "action": "allow",
                "description": "Observatory API endpoints"
            }
        ]
        
    def _log_action(self, action: str, status: str, details: Optional[Dict[str, Any]] = None):
        """Log action in JSON format."""
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "task": "5.1",
            "action": action,
            "status": status,
            "details": details or {}
        }
        print(json.dumps(log_entry))
        self.logger.info(f"Task 5.1 - {action}: {status}")
        
    async def __aenter__(self):
        """Async context manager entry."""
        await self.api_client.__aenter__()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.api_client.__aexit__(exc_type, exc_val, exc_tb)
        
    async def whitelist_observatory_patterns(self) -> List[str]:
        """Create whitelist rules for Observatory traffic patterns."""
        self._log_action("whitelist_observatory_patterns", "in_progress")
        
        try:
            created_rule_ids = []
            
            # Get recommended patterns
            recommended_patterns = self.traffic_analyzer.get_recommended_whitelist_rules()
            
            # Validate patterns for security
            validation_result = await self.security_validator.validate_rule_set(
                self.zone_id, recommended_patterns
            )
            
            if validation_result["overall_score"] < 0.8:
                self._log_action(
                    "whitelist_observatory_patterns", 
                    "error",
                    {"reason": "Security validation failed", "score": validation_result["overall_score"]}
                )
                raise ValueError("Security validation failed for Observatory patterns")
                
            # Create rules for each validated pattern
            for pattern in recommended_patterns:
                try:
                    result = await self.rule_manager.create_whitelist_rule(
                        zone_id=self.zone_id,
                        expression=pattern.expression,
                        description=pattern.description,
                        action="allow"
                    )
                    
                    rule_id = result.get("result", {}).get("id")
                    if rule_id:
                        created_rule_ids.append(rule_id)
                        
                    self._log_action(
                        "create_whitelist_rule",
                        "completed",
                        {"rule_id": rule_id, "pattern": pattern.pattern_type}
                    )
                    
                except CloudflareAPIError as e:
                    self._log_action(
                        "create_whitelist_rule",
                        "error",
                        {"pattern": pattern.pattern_type, "error": str(e)}
                    )
                    # Continue with other rules even if one fails
                    continue
                    
            self._log_action(
                "whitelist_observatory_patterns",
                "completed",
                {"created_rules": len(created_rule_ids), "rule_ids": created_rule_ids}
            )
            
            return created_rule_ids
            
        except Exception as e:
            self._log_action(
                "whitelist_observatory_patterns",
                "error",
                {"error": str(e)}
            )
            raise
            
    async def create_rate_limit_exception(self) -> str:
        """Create rate limiting exception for Observatory traffic."""
        self._log_action("create_rate_limit_exception", "in_progress")
        
        try:
            # Create rate limit exception for Observatory patterns
            match_expression = 'http.request.uri.path matches "^/(ws|health|api/observatory)/"'
            
            result = await self.rule_manager.create_rate_limit_exception(
                zone_id=self.zone_id,
                match_expression=match_expression,
                description="Observatory traffic rate limit exception",
                rate_limit=1000,  # Higher limit for Observatory
                period=60  # Per minute
            )
            
            rule_id = result.get("result", {}).get("id")
            
            self._log_action(
                "create_rate_limit_exception",
                "completed",
                {"rule_id": rule_id}
            )
            
            return rule_id
            
        except Exception as e:
            self._log_action(
                "create_rate_limit_exception",
                "error",
                {"error": str(e)}
            )
            raise
            
    async def validate_security_rules(self) -> bool:
        """Validate that security rules are properly configured."""
        self._log_action("validate_security_rules", "in_progress")
        
        try:
            # Audit current security rules
            audit_result = await self.security_validator.audit_security_rules(self.zone_id)
            
            # Check bot protection configuration
            bot_config = await self.api_client.get_bot_management_config(self.zone_id)
            
            # Validate Observatory rules
            observatory_rules = await self.rule_manager.list_observatory_rules(self.zone_id)
            
            validation_passed = (
                audit_result.get("total_rules", 0) > 0 and
                len(observatory_rules) > 0 and
                bot_config.get("result", {}).get("enable_js", False)  # Bot protection enabled
            )
            
            self._log_action(
                "validate_security_rules",
                "completed" if validation_passed else "error",
                {
                    "validation_passed": validation_passed,
                    "total_rules": audit_result.get("total_rules", 0),
                    "observatory_rules": len(observatory_rules),
                    "bot_protection_enabled": bot_config.get("result", {}).get("enable_js", False)
                }
            )
            
            return validation_passed
            
        except Exception as e:
            self._log_action(
                "validate_security_rules",
                "error",
                {"error": str(e)}
            )
            raise
            
    async def get_bot_protection_events(self) -> List[Dict]:
        """Get recent bot protection events for analysis."""
        self._log_action("get_bot_protection_events", "in_progress")
        
        try:
            # Get events from the last 24 hours
            end_time = datetime.utcnow()
            start_time = end_time.replace(hour=0, minute=0, second=0, microsecond=0)
            
            events = await self.api_client.get_security_events(self.zone_id, start_time, end_time)
            
            # Filter for bot protection events
            bot_events = []
            for event in events.get("result", []):
                if event.get("action") in ["block", "challenge", "managed_challenge"]:
                    bot_events.append(event)
                    
            self._log_action(
                "get_bot_protection_events",
                "completed",
                {"total_events": len(bot_events), "time_range": "24_hours"}
            )
            
            return bot_events
            
        except Exception as e:
            self._log_action(
                "get_bot_protection_events",
                "error",
                {"error": str(e)}
            )
            raise
            
    async def analyze_traffic_patterns(self, hours_back: int = 24) -> Dict[str, Any]:
        """Analyze traffic patterns to identify Observatory requests."""
        self._log_action("analyze_traffic_patterns", "in_progress")
        
        try:
            analysis_result = await self.traffic_analyzer.analyze_recent_traffic(
                self.zone_id, hours_back
            )
            
            self._log_action(
                "analyze_traffic_patterns",
                "completed",
                {
                    "patterns_found": len(analysis_result.get("patterns", [])),
                    "observatory_requests": analysis_result.get("summary", {}).get("observatory_requests", 0),
                    "block_rate": analysis_result.get("summary", {}).get("block_rate", 0)
                }
            )
            
            return analysis_result
            
        except Exception as e:
            self._log_action(
                "analyze_traffic_patterns",
                "error",
                {"error": str(e)}
            )
            raise
            
    async def deploy_observatory_whitelist(self) -> Dict[str, Any]:
        """Deploy complete Observatory whitelist configuration."""
        self._log_action("deploy_observatory_whitelist", "in_progress")
        
        try:
            deployment_result = {
                "whitelist_rules": [],
                "rate_limit_exceptions": [],
                "validation_results": {},
                "errors": []
            }
            
            # Step 1: Analyze current traffic
            traffic_analysis = await self.analyze_traffic_patterns()
            
            # Step 2: Create whitelist rules
            try:
                whitelist_rule_ids = await self.whitelist_observatory_patterns()
                deployment_result["whitelist_rules"] = whitelist_rule_ids
            except Exception as e:
                deployment_result["errors"].append(f"Whitelist rules failed: {str(e)}")
                
            # Step 3: Create rate limit exceptions
            try:
                rate_limit_rule_id = await self.create_rate_limit_exception()
                deployment_result["rate_limit_exceptions"] = [rate_limit_rule_id]
            except Exception as e:
                deployment_result["errors"].append(f"Rate limit exceptions failed: {str(e)}")
                
            # Step 4: Validate security
            try:
                security_valid = await self.validate_security_rules()
                deployment_result["validation_results"]["security_valid"] = security_valid
            except Exception as e:
                deployment_result["errors"].append(f"Security validation failed: {str(e)}")
                
            # Step 5: Get bot protection events
            try:
                bot_events = await self.get_bot_protection_events()
                deployment_result["validation_results"]["recent_bot_events"] = len(bot_events)
            except Exception as e:
                deployment_result["errors"].append(f"Bot protection events failed: {str(e)}")
                
            success = len(deployment_result["errors"]) == 0
            
            self._log_action(
                "deploy_observatory_whitelist",
                "completed" if success else "error",
                {
                    "success": success,
                    "whitelist_rules_created": len(deployment_result["whitelist_rules"]),
                    "rate_limit_exceptions_created": len(deployment_result["rate_limit_exceptions"]),
                    "errors": len(deployment_result["errors"])
                }
            )
            
            return deployment_result
            
        except Exception as e:
            self._log_action(
                "deploy_observatory_whitelist",
                "error",
                {"error": str(e)}
            )
            raise
            
    async def cleanup_observatory_rules(self) -> Dict[str, Any]:
        """Clean up Observatory-specific rules."""
        self._log_action("cleanup_observatory_rules", "in_progress")
        
        try:
            # Get existing Observatory rules
            observatory_rules = await self.rule_manager.list_observatory_rules(self.zone_id)
            
            cleanup_result = {
                "deleted_rules": [],
                "errors": []
            }
            
            # Delete each Observatory rule
            for rule in observatory_rules:
                try:
                    await self.rule_manager.delete_rule(
                        self.zone_id, 
                        rule["id"], 
                        rule["type"]
                    )
                    cleanup_result["deleted_rules"].append(rule["id"])
                    
                except Exception as e:
                    cleanup_result["errors"].append(f"Failed to delete rule {rule['id']}: {str(e)}")
                    
            self._log_action(
                "cleanup_observatory_rules",
                "completed",
                {
                    "deleted_rules": len(cleanup_result["deleted_rules"]),
                    "errors": len(cleanup_result["errors"])
                }
            )
            
            return cleanup_result
            
        except Exception as e:
            self._log_action(
                "cleanup_observatory_rules",
                "error",
                {"error": str(e)}
            )
            raise