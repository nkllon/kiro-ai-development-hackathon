"""
Cloudflare Whitelist Manager for Observatory Integration

Main orchestrator for managing Observatory traffic whitelisting
while maintaining security posture against actual threats.
"""

import json
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass

from .api_client import CloudflareAPIClient, CloudflareConfig, CloudflareAPIError
from .rule_manager import RuleManager, ObservatoryRule
from .traffic_analyzer import TrafficAnalyzer, TrafficAnalysis
from .security_validator import SecurityValidator, SecurityValidationReport

logger = logging.getLogger(__name__)


@dataclass
class WhitelistOperationResult:
    """Result of a whitelist operation"""
    success: bool
    rules_created: int
    rules_updated: int
    rules_deleted: int
    errors: List[str]
    warnings: List[str]
    security_validation: Optional[SecurityValidationReport] = None


class CloudflareWhitelistManager:
    """
    Main orchestrator for Observatory Cloudflare integration
    
    Manages whitelist rules, rate limiting exceptions, and security validation
    to ensure Observatory traffic is allowed while maintaining protection.
    """
    
    def __init__(self, api_token: str, zone_id: str):
        """
        Initialize Cloudflare Whitelist Manager
        
        Args:
            api_token: Cloudflare API token with appropriate permissions
            zone_id: Cloudflare zone ID for the domain
        """
        self.config = CloudflareConfig(
            api_token=api_token,
            zone_id=zone_id
        )
        
        self.api_client = CloudflareAPIClient(self.config)
        self.rule_manager = RuleManager(self.api_client)
        self.traffic_analyzer = TrafficAnalyzer(self.api_client)
        self.security_validator = SecurityValidator(
            self.api_client, 
            self.rule_manager, 
            self.traffic_analyzer
        )
        
        self._log_action("whitelist_manager_init", "in_progress", {
            "zone_id": zone_id,
            "api_token_provided": bool(api_token)
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
        logger.info(f"Whitelist Manager action: {action} - {status}")
    
    async def __aenter__(self):
        """Async context manager entry"""
        await self.api_client.__aenter__()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.api_client.__aexit__(exc_type, exc_val, exc_tb)
    
    async def whitelist_observatory_patterns(self) -> List[str]:
        """
        Create whitelist rules for Observatory traffic patterns
        
        Returns:
            List of created rule IDs
            
        Raises:
            CloudflareAPIError: If rule creation fails
        """
        self._log_action("whitelist_observatory_patterns", "in_progress", {})
        
        try:
            # Test API connection first
            if not await self.api_client.test_connection():
                raise CloudflareAPIError("Failed to connect to Cloudflare API")
            
            # Create Observatory whitelist rules
            created_rules = await self.rule_manager.create_observatory_whitelist_rules()
            rule_ids = [rule.get("id") for rule in created_rules if rule.get("id")]
            
            self._log_action("whitelist_observatory_patterns", "completed", {
                "rules_created": len(rule_ids),
                "rule_ids": rule_ids
            })
            
            return rule_ids
            
        except CloudflareAPIError as e:
            self._log_action("whitelist_observatory_patterns", "error", {
                "error": str(e),
                "status_code": e.status_code
            })
            raise
    
    async def create_rate_limit_exception(self) -> str:
        """
        Create rate limiting exceptions for Observatory traffic
        
        Returns:
            Created rate limit rule ID
            
        Raises:
            CloudflareAPIError: If rule creation fails
        """
        self._log_action("create_rate_limit_exception", "in_progress", {})
        
        try:
            # Create Observatory rate limit exceptions
            created_rules = await self.rule_manager.create_observatory_rate_limit_exceptions()
            
            # Return the first rule ID (or create a summary ID)
            if created_rules:
                rule_id = created_rules[0].get("id", "multiple_rules_created")
            else:
                rule_id = "no_rules_created"
            
            self._log_action("create_rate_limit_exception", "completed", {
                "rules_created": len(created_rules),
                "rule_id": rule_id
            })
            
            return rule_id
            
        except CloudflareAPIError as e:
            self._log_action("create_rate_limit_exception", "error", {
                "error": str(e),
                "status_code": e.status_code
            })
            raise
    
    async def validate_security_rules(self) -> bool:
        """
        Validate that security rules maintain proper protection
        
        Returns:
            True if security validation passes, False otherwise
            
        Raises:
            CloudflareAPIError: If validation fails
        """
        self._log_action("validate_security_rules", "in_progress", {})
        
        try:
            # Perform comprehensive security validation
            validation_report = await self.security_validator.validate_observatory_integration()
            
            # Check if validation passed
            validation_passed = validation_report.overall_status.value in ["pass", "warning"]
            
            self._log_action("validate_security_rules", "completed", {
                "validation_passed": validation_passed,
                "security_score": validation_report.security_score,
                "overall_status": validation_report.overall_status.value,
                "checks_performed": validation_report.checks_performed
            })
            
            return validation_passed
            
        except Exception as e:
            self._log_action("validate_security_rules", "error", {
                "error": str(e)
            })
            raise CloudflareAPIError(f"Security validation failed: {e}")
    
    async def get_bot_protection_events(self) -> List[Dict]:
        """
        Get recent bot protection events from Cloudflare
        
        Returns:
            List of bot protection events
            
        Raises:
            CloudflareAPIError: If API call fails
        """
        self._log_action("get_bot_protection_events", "in_progress", {})
        
        try:
            # Get security events
            events = await self.api_client.get_security_events(limit=100)
            
            # Filter for bot protection events
            bot_events = [
                event for event in events
                if event.get("action") in ["block", "challenge", "managed_challenge"]
            ]
            
            self._log_action("get_bot_protection_events", "completed", {
                "total_events": len(events),
                "bot_events": len(bot_events)
            })
            
            return bot_events
            
        except CloudflareAPIError as e:
            self._log_action("get_bot_protection_events", "error", {
                "error": str(e),
                "status_code": e.status_code
            })
            raise
    
    async def setup_observatory_integration(self) -> WhitelistOperationResult:
        """
        Complete setup of Observatory Cloudflare integration
        
        Creates all necessary rules, validates security, and monitors effectiveness.
        
        Returns:
            WhitelistOperationResult with operation details
        """
        self._log_action("setup_observatory_integration", "in_progress", {})
        
        result = WhitelistOperationResult(
            success=False,
            rules_created=0,
            rules_updated=0,
            rules_deleted=0,
            errors=[],
            warnings=[]
        )
        
        try:
            # Step 1: Create Observatory whitelist rules
            try:
                rule_ids = await self.whitelist_observatory_patterns()
                result.rules_created = len(rule_ids)
            except CloudflareAPIError as e:
                result.errors.append(f"Failed to create whitelist rules: {e}")
            
            # Step 2: Create rate limiting exceptions
            try:
                rate_limit_id = await self.create_rate_limit_exception()
                if rate_limit_id != "no_rules_created":
                    result.rules_created += 1
            except CloudflareAPIError as e:
                result.errors.append(f"Failed to create rate limit exceptions: {e}")
            
            # Step 3: Validate security posture
            try:
                security_valid = await self.validate_security_rules()
                if not security_valid:
                    result.warnings.append("Security validation failed - review required")
            except Exception as e:
                result.errors.append(f"Security validation failed: {e}")
            
            # Step 4: Get comprehensive security validation report
            try:
                validation_report = await self.security_validator.validate_observatory_integration()
                result.security_validation = validation_report
                
                if validation_report.overall_status.value == "fail":
                    result.warnings.append("Security validation failed - immediate review required")
                elif validation_report.overall_status.value == "warning":
                    result.warnings.append("Security validation passed with warnings")
                    
            except Exception as e:
                result.errors.append(f"Failed to get security validation report: {e}")
            
            # Determine overall success
            result.success = len(result.errors) == 0
            
            self._log_action("setup_observatory_integration", "completed", {
                "success": result.success,
                "rules_created": result.rules_created,
                "errors_count": len(result.errors),
                "warnings_count": len(result.warnings)
            })
            
            return result
            
        except Exception as e:
            result.errors.append(f"Setup failed with unexpected error: {e}")
            self._log_action("setup_observatory_integration", "error", {
                "error": str(e)
            })
            return result
    
    async def monitor_observatory_traffic(self) -> Dict[str, Any]:
        """
        Monitor Observatory traffic patterns and effectiveness
        
        Returns:
            Dictionary with traffic monitoring results
        """
        self._log_action("monitor_observatory_traffic", "in_progress", {})
        
        try:
            # Get traffic analysis
            traffic_summary = await self.traffic_analyzer.get_observatory_traffic_summary()
            
            # Get whitelist effectiveness
            effectiveness = await self.traffic_analyzer.monitor_whitelist_effectiveness()
            
            # Get security status
            security_status = await self.security_validator.get_security_status()
            
            monitoring_result = {
                "traffic_summary": traffic_summary,
                "whitelist_effectiveness": effectiveness,
                "security_status": security_status,
                "monitoring_timestamp": datetime.utcnow().isoformat() + "Z"
            }
            
            self._log_action("monitor_observatory_traffic", "completed", {
                "total_requests": traffic_summary.get("total_requests_24h", 0),
                "observatory_requests": traffic_summary.get("observatory_requests_24h", 0),
                "security_score": security_status.get("security_score", 0)
            })
            
            return monitoring_result
            
        except Exception as e:
            self._log_action("monitor_observatory_traffic", "error", {
                "error": str(e)
            })
            raise CloudflareAPIError(f"Traffic monitoring failed: {e}")
    
    async def cleanup_observatory_rules(self) -> Dict[str, int]:
        """
        Clean up all Observatory-related rules
        
        Returns:
            Dictionary with cleanup statistics
        """
        self._log_action("cleanup_observatory_rules", "in_progress", {})
        
        try:
            cleanup_stats = await self.rule_manager.cleanup_observatory_rules()
            
            self._log_action("cleanup_observatory_rules", "completed", cleanup_stats)
            
            return cleanup_stats
            
        except CloudflareAPIError as e:
            self._log_action("cleanup_observatory_rules", "error", {
                "error": str(e)
            })
            raise
    
    async def get_integration_status(self) -> Dict[str, Any]:
        """
        Get comprehensive status of Observatory Cloudflare integration
        
        Returns:
            Dictionary with complete integration status
        """
        self._log_action("get_integration_status", "in_progress", {})
        
        try:
            # Get existing rules
            firewall_rules, rate_limit_rules = await self.rule_manager.get_existing_observatory_rules()
            
            # Get traffic monitoring
            traffic_monitoring = await self.monitor_observatory_traffic()
            
            # Get security status
            security_status = await self.security_validator.get_security_status()
            
            status = {
                "integration_active": True,
                "firewall_rules_count": len(firewall_rules),
                "rate_limit_rules_count": len(rate_limit_rules),
                "traffic_monitoring": traffic_monitoring,
                "security_status": security_status,
                "last_updated": datetime.utcnow().isoformat() + "Z"
            }
            
            self._log_action("get_integration_status", "completed", {
                "firewall_rules": len(firewall_rules),
                "rate_limit_rules": len(rate_limit_rules),
                "security_score": security_status.get("security_score", 0)
            })
            
            return status
            
        except Exception as e:
            self._log_action("get_integration_status", "error", {
                "error": str(e)
            })
            raise CloudflareAPIError(f"Failed to get integration status: {e}")
    
    async def test_observatory_traffic_flow(self) -> Dict[str, Any]:
        """
        Test Observatory traffic flow through Cloudflare
        
        Returns:
            Dictionary with test results
        """
        self._log_action("test_observatory_traffic_flow", "in_progress", {})
        
        try:
            # Get recent traffic analysis
            analysis = await self.traffic_analyzer.analyze_recent_traffic(hours=1)
            
            # Check for Observatory traffic patterns
            observatory_traffic = analysis.observatory_requests
            blocked_observatory = analysis.blocked_requests
            
            # Calculate success rate
            if observatory_traffic > 0:
                success_rate = ((observatory_traffic - blocked_observatory) / observatory_traffic) * 100
            else:
                success_rate = 100.0  # No traffic to test
            
            test_result = {
                "observatory_traffic_detected": observatory_traffic > 0,
                "observatory_requests": observatory_traffic,
                "blocked_requests": blocked_observatory,
                "success_rate": success_rate,
                "pattern_breakdown": {
                    pattern.value: count 
                    for pattern, count in analysis.pattern_breakdown.items()
                },
                "suspicious_activity": len(analysis.suspicious_activity),
                "test_timestamp": datetime.utcnow().isoformat() + "Z"
            }
            
            self._log_action("test_observatory_traffic_flow", "completed", {
                "observatory_traffic": observatory_traffic,
                "success_rate": success_rate,
                "suspicious_activity": len(analysis.suspicious_activity)
            })
            
            return test_result
            
        except Exception as e:
            self._log_action("test_observatory_traffic_flow", "error", {
                "error": str(e)
            })
            raise CloudflareAPIError(f"Traffic flow test failed: {e}")