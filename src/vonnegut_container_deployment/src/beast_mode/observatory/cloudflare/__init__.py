"""
Cloudflare Bot Protection Integration for Observatory System

This module provides integration with Cloudflare's bot protection and firewall
rules to whitelist legitimate Observatory traffic while maintaining security
posture against actual threats.

Key Components:
- CloudflareWhitelistManager: Main orchestrator for whitelist operations
- CloudflareAPIClient: Low-level API client for Cloudflare API v4
- RuleManager: Manages firewall and rate limiting rules
- TrafficAnalyzer: Analyzes Observatory traffic patterns
- SecurityValidator: Validates security posture maintenance
"""

from .whitelist_manager import CloudflareWhitelistManager
from .api_client import CloudflareAPIClient
from .rule_manager import RuleManager
from .traffic_analyzer import TrafficAnalyzer
from .security_validator import SecurityValidator

__all__ = [
    "CloudflareWhitelistManager",
    "CloudflareAPIClient", 
    "RuleManager",
    "TrafficAnalyzer",
    "SecurityValidator"
]

__version__ = "1.0.0"