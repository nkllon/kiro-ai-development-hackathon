#!/usr/bin/env python3
"""
Check Dependabot Alerts

Quick script to check current Dependabot security alerts status.

Usage:
    python3 scripts/check_dependabot_alerts.py [--verbose]
"""

import argparse
import json
import subprocess
import sys
from typing import List, Dict, Any

def get_alerts(state: str = "open") -> List[Dict[str, Any]]:
    """Get Dependabot alerts with specified state."""
    try:
        cmd = [
            "gh", "api", "repos/nkllon/kiro-ai-development-hackathon/dependabot/alerts",
            "--jq", f"map(select(.state == \"{state}\"))"
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return json.loads(result.stdout)
        
    except subprocess.CalledProcessError as e:
        print(f"Error fetching alerts: {e}")
        print(f"stderr: {e.stderr}")
        return []
    except json.JSONDecodeError as e:
        print(f"Error parsing API response: {e}")
        return []

def main():
    """Main execution function."""
    parser = argparse.ArgumentParser(description="Check Dependabot alerts")
    parser.add_argument("--verbose", "-v", action="store_true",
                       help="Show detailed alert information")
    
    args = parser.parse_args()
    
    print("🔍 Checking Dependabot security alerts...")
    
    # Get open alerts
    open_alerts = get_alerts("open")
    dismissed_alerts = get_alerts("dismissed")
    
    print(f"\n📊 Alert Summary:")
    print(f"  Open alerts: {len(open_alerts)}")
    print(f"  Dismissed alerts: {len(dismissed_alerts)}")
    
    if open_alerts:
        print(f"\n🚨 Open Alerts ({len(open_alerts)}):")
        for alert in open_alerts:
            package = alert['dependency']['package']['name']
            severity = alert['security_advisory']['severity']
            summary = alert['security_advisory']['summary']
            
            print(f"  #{alert['number']}: {package} ({severity})")
            if args.verbose:
                print(f"    Summary: {summary}")
                print(f"    Created: {alert['created_at']}")
    else:
        print("\n✅ No open security alerts!")
    
    if dismissed_alerts and args.verbose:
        print(f"\n📋 Recently Dismissed Alerts ({len(dismissed_alerts)}):")
        for alert in dismissed_alerts[-5:]:  # Show last 5
            package = alert['dependency']['package']['name']
            reason = alert.get('dismissed_reason', 'unknown')
            comment = alert.get('dismissed_comment', '')
            
            print(f"  #{alert['number']}: {package}")
            print(f"    Reason: {reason}")
            if comment:
                print(f"    Comment: {comment[:100]}...")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())