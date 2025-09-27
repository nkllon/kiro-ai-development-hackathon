"""
Security Validator for Cloudflare Rule Validation.

Validates that whitelist rules maintain security posture and don't create vulnerabilities.
"""

import json
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

from .api_client import CloudflareAPIClient, CloudflareAPIError
from .traffic_analyzer import TrafficPattern


class SecurityValidationResult:
    """Result of security validation."""
    
    def __init__(
        self,
        is_valid: bool,
        score: float,
        issues: List[str],
        recommendations: List[str],
        metadata: Optional[Dict[str, Any]] = None
    ):
        self.is_valid = is_valid
        self.score = score  # 0.0 to 1.0, higher is more secure
        self.issues = issues
        self.recommendations = recommendations
        self.metadata = metadata or {}
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "is_valid": self.is_valid,
            "score": self.score,
            "issues": self.issues,
            "recommendations": self.recommendations,
            "metadata": self.metadata
        }


class SecurityValidator:
    """Validates security implications of Cloudflare rules."""
    
    # Dangerous patterns that should be avoided
    DANGEROUS_PATTERNS = [
        r".*\*.*",  # Wildcards in expressions
        r".*\.\*.*",  # Wildcards in domains
        r".*all.*",  # Overly broad terms
        r".*any.*",  # Overly broad terms
    ]
    
    # Required security checks
    REQUIRED_SECURITY_CHECKS = [
        "specific_user_agent",
        "specific_path_pattern",
        "specific_header_value",
        "no_wildcards",
        "limited_scope"
    ]
    
    def __init__(self, api_client: CloudflareAPIClient):
        self.api_client = api_client
        self.logger = logging.getLogger(__name__)
        
    async def validate_whitelist_rule(
        self,
        zone_id: str,
        pattern: TrafficPattern,
        existing_rules: Optional[List[Dict[str, Any]]] = None
    ) -> SecurityValidationResult:
        """Validate a whitelist rule for security implications."""
        issues = []
        recommendations = []
        score = 1.0
        
        try:
            # Check expression syntax
            if not self._validate_expression_syntax(pattern.expression):
                issues.append("Invalid expression syntax")
                score -= 0.3
                
            # Check for dangerous patterns
            if self._contains_dangerous_patterns(pattern.expression):
                issues.append("Expression contains potentially dangerous patterns")
                score -= 0.4
                
            # Check specificity
            specificity_score = self._check_specificity(pattern)
            if specificity_score < 0.7:
                issues.append("Rule is not specific enough")
                recommendations.append("Make the rule more specific to Observatory traffic")
                score -= 0.2
                
            # Check for conflicts with existing rules
            if existing_rules:
                conflicts = self._check_rule_conflicts(pattern, existing_rules)
                if conflicts:
                    issues.extend(conflicts)
                    score -= 0.1 * len(conflicts)
                    
            # Check bot protection impact
            bot_protection_impact = await self._check_bot_protection_impact(zone_id, pattern)
            if bot_protection_impact < 0.8:
                issues.append("Rule may impact bot protection effectiveness")
                recommendations.append("Review bot protection settings after rule deployment")
                score -= 0.1
                
            # Validate against Observatory patterns
            if not self._is_observatory_specific(pattern):
                issues.append("Rule is not specific to Observatory traffic")
                score -= 0.3
                
            # Final validation
            is_valid = len(issues) == 0 and score >= 0.7
            
            if not is_valid:
                recommendations.append("Review and refine the rule before deployment")
                
            return SecurityValidationResult(
                is_valid=is_valid,
                score=score,
                issues=issues,
                recommendations=recommendations,
                metadata={
                    "pattern_type": pattern.pattern_type,
                    "confidence": pattern.confidence,
                    "validated_at": datetime.utcnow().isoformat()
                }
            )
            
        except Exception as e:
            self.logger.error(f"Security validation failed: {e}")
            return SecurityValidationResult(
                is_valid=False,
                score=0.0,
                issues=[f"Validation error: {str(e)}"],
                recommendations=["Fix validation errors before proceeding"]
            )
            
    def _validate_expression_syntax(self, expression: str) -> bool:
        """Validate Cloudflare expression syntax."""
        try:
            # Basic syntax checks
            if not expression or not isinstance(expression, str):
                return False
                
            # Check for balanced parentheses
            if expression.count("(") != expression.count(")"):
                return False
                
            # Check for required Cloudflare expression elements
            if not any(element in expression for element in ["http.", "ip.", "cf."]):
                return False
                
            return True
            
        except Exception:
            return False
            
    def _contains_dangerous_patterns(self, expression: str) -> bool:
        """Check if expression contains dangerous patterns."""
        import re
        
        for pattern in self.DANGEROUS_PATTERNS:
            if re.search(pattern, expression, re.IGNORECASE):
                return True
                
        return False
        
    def _check_specificity(self, pattern: TrafficPattern) -> float:
        """Check how specific a pattern is (0.0 to 1.0)."""
        score = 0.0
        
        # Check for specific user agent
        if "user_agent" in pattern.expression and "Observatory" in pattern.expression:
            score += 0.3
            
        # Check for specific path patterns
        if "uri.path" in pattern.expression:
            score += 0.2
            
        # Check for specific headers
        if "headers" in pattern.expression and "x-observatory" in pattern.expression:
            score += 0.3
            
        # Check for specific values (not wildcards)
        if "*" not in pattern.expression and ".*" not in pattern.expression:
            score += 0.2
            
        return min(score, 1.0)
        
    def _check_rule_conflicts(
        self,
        pattern: TrafficPattern,
        existing_rules: List[Dict[str, Any]]
    ) -> List[str]:
        """Check for conflicts with existing rules."""
        conflicts = []
        
        for rule in existing_rules:
            # Check for duplicate expressions
            if rule.get("filter", {}).get("expression") == pattern.expression:
                conflicts.append(f"Duplicate expression found in rule {rule.get('id')}")
                
            # Check for overlapping scope
            if self._rules_overlap(pattern, rule):
                conflicts.append(f"Potential overlap with rule {rule.get('id')}")
                
        return conflicts
        
    def _rules_overlap(self, pattern: TrafficPattern, rule: Dict[str, Any]) -> bool:
        """Check if two rules have overlapping scope."""
        # Simplified overlap detection
        rule_expression = rule.get("filter", {}).get("expression", "")
        
        # Check for common elements
        common_elements = ["http.user_agent", "http.request.uri.path", "http.request.headers"]
        
        for element in common_elements:
            if element in pattern.expression and element in rule_expression:
                return True
                
        return False
        
    async def _check_bot_protection_impact(
        self,
        zone_id: str,
        pattern: TrafficPattern
    ) -> float:
        """Check impact on bot protection (0.0 to 1.0)."""
        try:
            # Get current bot protection config
            config = await self.api_client.get_bot_management_config(zone_id)
            
            # Check if rule might bypass important bot protection
            if "allow" in pattern.expression.lower():
                # Allow rules should be very specific
                if self._check_specificity(pattern) < 0.8:
                    return 0.5
                    
            return 0.9  # Default to good impact
            
        except CloudflareAPIError:
            # If we can't check, assume moderate impact
            return 0.7
            
    def _is_observatory_specific(self, pattern: TrafficPattern) -> bool:
        """Check if pattern is specific to Observatory."""
        expression_lower = pattern.expression.lower()
        
        # Check for Observatory-specific indicators
        observatory_indicators = [
            "observatory",
            "x-observatory",
            "/ws/",
            "/api/observatory/",
            "/health"
        ]
        
        return any(indicator in expression_lower for indicator in observatory_indicators)
        
    async def validate_rule_set(
        self,
        zone_id: str,
        patterns: List[TrafficPattern]
    ) -> Dict[str, Any]:
        """Validate a complete set of rules."""
        results = []
        overall_score = 0.0
        total_issues = []
        total_recommendations = []
        
        # Get existing rules for conflict checking
        try:
            existing_rules = await self.api_client.list_firewall_rules(zone_id)
            existing_rule_list = existing_rules.get("result", [])
        except CloudflareAPIError:
            existing_rule_list = []
            
        for pattern in patterns:
            result = await self.validate_whitelist_rule(zone_id, pattern, existing_rule_list)
            results.append(result.to_dict())
            overall_score += result.score
            total_issues.extend(result.issues)
            total_recommendations.extend(result.recommendations)
            
        overall_score = overall_score / len(patterns) if patterns else 0.0
        
        return {
            "overall_score": overall_score,
            "individual_results": results,
            "total_issues": total_issues,
            "total_recommendations": list(set(total_recommendations)),  # Remove duplicates
            "recommendation": "Proceed" if overall_score >= 0.8 else "Review required"
        }
        
    async def audit_security_rules(self, zone_id: str) -> Dict[str, Any]:
        """Audit all security rules for potential issues."""
        try:
            # Get all firewall rules
            firewall_rules = await self.api_client.list_firewall_rules(zone_id)
            
            audit_results = {
                "total_rules": len(firewall_rules.get("result", [])),
                "allow_rules": 0,
                "block_rules": 0,
                "challenge_rules": 0,
                "potential_issues": [],
                "recommendations": []
            }
            
            for rule in firewall_rules.get("result", []):
                action = rule.get("action", "").lower()
                
                if action == "allow":
                    audit_results["allow_rules"] += 1
                    
                    # Check for overly permissive allow rules
                    expression = rule.get("filter", {}).get("expression", "")
                    if self._contains_dangerous_patterns(expression):
                        audit_results["potential_issues"].append(
                            f"Rule {rule.get('id')} may be overly permissive"
                        )
                        
                elif action == "block":
                    audit_results["block_rules"] += 1
                elif action == "challenge":
                    audit_results["challenge_rules"] += 1
                    
            # Add recommendations
            if audit_results["allow_rules"] > 10:
                audit_results["recommendations"].append(
                    "Consider consolidating allow rules to reduce complexity"
                )
                
            if audit_results["potential_issues"]:
                audit_results["recommendations"].append(
                    "Review potentially problematic rules"
                )
                
            return audit_results
            
        except CloudflareAPIError as e:
            self.logger.error(f"Security audit failed: {e}")
            return {
                "error": str(e),
                "total_rules": 0,
                "potential_issues": ["Audit failed"],
                "recommendations": ["Fix API access issues"]
            }