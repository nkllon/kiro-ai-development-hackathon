#!/usr/bin/env python3
"""
Bot Protection Configuration for Observatory HTTP Polling Fallback

This script provides configuration guidance and automated setup for
whitelisting legitimate HTTP polling patterns to prevent Error 1033.
"""

import json
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any

def generate_bot_protection_config():
    """Generate Cloudflare bot protection configuration for Observatory"""
    
    config = {
        "timestamp": datetime.now().isoformat(),
        "domain": "observatory.nkllon.com",
        "purpose": "Whitelist legitimate HTTP polling fallback patterns",
        "rules": {
            "observatory_polling_whitelist": {
                "description": "Allow Observatory internal polling patterns",
                "conditions": [
                    {
                        "field": "http.user_agent",
                        "operator": "contains",
                        "value": "Observatory-Internal"
                    },
                    {
                        "field": "http.request.headers.x-observatory-client",
                        "operator": "equals",
                        "value": "internal-polling"
                    },
                    {
                        "field": "http.request.headers.x-polling-reason",
                        "operator": "equals",
                        "value": "websocket-fallback"
                    }
                ],
                "action": "allow",
                "priority": 1
            },
            "observatory_api_whitelist": {
                "description": "Allow Observatory API endpoints",
                "conditions": [
                    {
                        "field": "http.request.uri.path",
                        "operator": "starts_with",
                        "value": "/api/"
                    },
                    {
                        "field": "http.request.headers.x-requested-with",
                        "operator": "equals",
                        "value": "XMLHttpRequest"
                    }
                ],
                "action": "allow",
                "priority": 2
            },
            "observatory_rate_limit": {
                "description": "Rate limit Observatory polling to prevent abuse",
                "conditions": [
                    {
                        "field": "http.request.uri.path",
                        "operator": "starts_with",
                        "value": "/api/"
                    }
                ],
                "action": "rate_limit",
                "rate_limit": {
                    "requests_per_minute": 60,
                    "burst_size": 10
                },
                "priority": 3
            }
        },
        "waf_rules": {
            "disable_bot_fight_mode": {
                "description": "Disable Bot Fight Mode for Observatory domain",
                "action": "disable",
                "reason": "Interferes with legitimate polling patterns"
            },
            "custom_rule": {
                "description": "Custom rule for Observatory polling",
                "expression": """
                    (http.user_agent contains "Observatory-Internal" and 
                     http.request.headers.x-observatory-client eq "internal-polling" and
                     http.request.uri.path starts_with "/api/")
                """,
                "action": "allow"
            }
        },
        "firewall_rules": {
            "observatory_allow": {
                "description": "Allow Observatory traffic",
                "expression": """
                    (http.host eq "observatory.nkllon.com" and
                     http.request.uri.path starts_with "/api/" and
                     http.request.headers.x-polling-reason eq "websocket-fallback")
                """,
                "action": "allow"
            }
        }
    }
    
    return config

def generate_http_polling_headers():
    """Generate bot-safe headers for HTTP polling fallback"""
    
    headers = {
        "User-Agent": "Observatory-Internal/1.0 (WebSocket-Fallback)",
        "X-Observatory-Client": "internal-polling",
        "X-Requested-With": "XMLHttpRequest",
        "Accept": "application/json",
        "Cache-Control": "no-cache",
        "X-Polling-Reason": "websocket-fallback",
        "X-Observatory-Version": "1.0.0",
        "X-Observatory-Session": "internal-session"
    }
    
    return headers

def generate_polling_strategy():
    """Generate intelligent polling strategy to avoid bot detection"""
    
    strategy = {
        "base_interval": 5.0,  # 5 seconds base
        "max_interval": 60.0,  # 60 seconds max
        "backoff_multiplier": 1.5,
        "jitter_factor": 0.1,
        "max_retries": 3,
        "endpoints": {
            "/api/emoji-rain/stats": {
                "interval": 5.0,
                "priority": "high",
                "fallback": True
            },
            "/api/dashboard/all-data": {
                "interval": 10.0,
                "priority": "medium",
                "fallback": True
            },
            "/api/observatory/status": {
                "interval": 15.0,
                "priority": "low",
                "fallback": True
            }
        },
        "bot_avoidance": {
            "randomize_intervals": True,
            "batch_requests": True,
            "respect_rate_limits": True,
            "exponential_backoff": True
        }
    }
    
    return strategy

def generate_cloudflare_dashboard_instructions():
    """Generate step-by-step Cloudflare dashboard configuration instructions"""
    
    instructions = {
        "title": "Cloudflare Dashboard Configuration for Observatory",
        "steps": [
            {
                "step": 1,
                "title": "Enable WebSockets",
                "description": "Enable WebSocket support in Cloudflare dashboard",
                "location": "Network → WebSockets",
                "action": "Toggle WebSockets to ON",
                "reason": "Required for WebSocket connections through tunnel"
            },
            {
                "step": 2,
                "title": "Configure Bot Protection",
                "description": "Set up bot protection rules for Observatory",
                "location": "Security → Bot Fight Mode",
                "action": "Disable Bot Fight Mode for observatory.nkllon.com",
                "reason": "Prevents false positives on legitimate polling"
            },
            {
                "step": 3,
                "title": "Create WAF Rules",
                "description": "Create custom WAF rules for Observatory polling",
                "location": "Security → WAF → Custom Rules",
                "action": "Create rule with Observatory polling conditions",
                "reason": "Whitelist legitimate polling patterns"
            },
            {
                "step": 4,
                "title": "Configure Rate Limiting",
                "description": "Set appropriate rate limits for Observatory",
                "location": "Security → Rate Limiting",
                "action": "Create rate limit rule for /api/* endpoints",
                "reason": "Prevent abuse while allowing legitimate polling"
            },
            {
                "step": 5,
                "title": "Firewall Rules",
                "description": "Create firewall rules for Observatory traffic",
                "location": "Security → Firewall Rules",
                "action": "Allow Observatory polling traffic",
                "reason": "Ensure Observatory traffic is not blocked"
            }
        ]
    }
    
    return instructions

def main():
    """Main configuration generation"""
    print("🔧 Observatory Bot Protection Configuration Generator")
    print("=" * 60)
    
    # Generate configurations
    bot_config = generate_bot_protection_config()
    headers = generate_http_polling_headers()
    strategy = generate_polling_strategy()
    instructions = generate_cloudflare_dashboard_instructions()
    
    # Save configurations
    config_dir = Path("config/bot_protection")
    config_dir.mkdir(parents=True, exist_ok=True)
    
    # Save bot protection config
    with open(config_dir / "cloudflare_bot_protection.json", "w") as f:
        json.dump(bot_config, f, indent=2)
    
    # Save headers config
    with open(config_dir / "http_polling_headers.json", "w") as f:
        json.dump(headers, f, indent=2)
    
    # Save polling strategy
    with open(config_dir / "polling_strategy.json", "w") as f:
        json.dump(strategy, f, indent=2)
    
    # Save dashboard instructions
    with open(config_dir / "dashboard_instructions.json", "w") as f:
        json.dump(instructions, f, indent=2)
    
    print(f"✅ Configuration files generated in {config_dir}")
    print(f"   • cloudflare_bot_protection.json")
    print(f"   • http_polling_headers.json")
    print(f"   • polling_strategy.json")
    print(f"   • dashboard_instructions.json")
    
    print(f"\n📋 Next Steps:")
    print(f"   1. Review generated configurations")
    print(f"   2. Apply Cloudflare dashboard settings")
    print(f"   3. Update Observatory polling implementation")
    print(f"   4. Test WebSocket connectivity through tunnel")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())

