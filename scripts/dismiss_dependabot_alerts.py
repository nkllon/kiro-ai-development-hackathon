#!/usr/bin/env python3
"""
Dismiss Dependabot Security Alerts

Systematically dismiss Dependabot security alerts that have been analyzed
and determined to pose no actual risk to the system.

Usage:
    python3 scripts/dismiss_dependabot_alerts.py [--dry-run] [--package PACKAGE]

Examples:
    # Preview all dismissals
    python3 scripts/dismiss_dependabot_alerts.py --dry-run
    
    # Dismiss all configured alerts
    python3 scripts/dismiss_dependabot_alerts.py
    
    # Dismiss specific package only
    python3 scripts/dismiss_dependabot_alerts.py --package python-jose
"""

import argparse
import json
import subprocess
import sys
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime

@dataclass
class DependabotAlert:
    """Represents a Dependabot security alert."""
    number: int
    package_name: str
    severity: str
    summary: str
    state: str
    created_at: str
    
    @classmethod
    def from_api_response(cls, data: Dict[str, Any]) -> 'DependabotAlert':
        """Create DependabotAlert from GitHub API response."""
        return cls(
            number=data['number'],
            package_name=data['dependency']['package']['name'],
            severity=data['security_advisory']['severity'],
            summary=data['security_advisory']['summary'],
            state=data['state'],
            created_at=data['created_at']
        )

# Configuration: Alerts to dismiss with risk acceptance reasoning
DISMISSALS = {
    "python-jose": {
        "reason": "not_used",
        "comment": (
            "Risk Accepted: Listed in requirements-cms-search.txt but no JWT/auth "
            "code exists. Unused dependency. Attack surface: None."
        )
    },
    "gunicorn": {
        "reason": "inaccurate", 
        "comment": (
            "False Positive: Not in any requirements files. System uses uvicorn. "
            "Dependabot scanning stale lock files."
        )
    },
    "jinja2": {
        "reason": "tolerable_risk",
        "comment": (
            "Risk Accepted: No untrusted template rendering. Jinja2 only for "
            "internal FastAPI HTML. Behind Cloudflare WAF. Attack surface: None."
        )
    },
    "python-multipart": {
        "reason": "tolerable_risk",
        "comment": (
            "Risk Accepted: File upload vulnerability requires untrusted file processing. "
            "No file upload endpoints exposed. Behind Cloudflare WAF."
        )
    },
    "urllib3": {
        "reason": "tolerable_risk",
        "comment": (
            "Risk Accepted: HTTPS verification bypass requires malicious code. "
            "All external requests use requests library defaults. Internal only."
        )
    }
}

# Valid dismissal reasons per GitHub API
VALID_REASONS = {
    "fix_started": "A fix has already been started",
    "inaccurate": "This alert is inaccurate or incorrect", 
    "no_bandwidth": "No bandwidth to fix this",
    "not_used": "Vulnerable code is not actually used",
    "tolerable_risk": "The risk is tolerable to us"
}

class DependabotAlertManager:
    """Manages Dependabot security alerts via GitHub API."""
    
    def __init__(self, repo: str = "nkllon/kiro-ai-development-hackathon"):
        self.repo = repo
        
    def get_open_alerts(self) -> List[DependabotAlert]:
        """Fetch all open Dependabot alerts."""
        try:
            cmd = [
                "gh", "api", f"repos/{self.repo}/dependabot/alerts",
                "--jq", "map(select(.state == \"open\"))"
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            alerts_data = json.loads(result.stdout)
            
            return [DependabotAlert.from_api_response(alert) for alert in alerts_data]
            
        except subprocess.CalledProcessError as e:
            print(f"Error fetching alerts: {e}")
            print(f"stderr: {e.stderr}")
            return []
        except json.JSONDecodeError as e:
            print(f"Error parsing API response: {e}")
            return []
    
    def dismiss_alert(self, alert_number: int, reason: str, comment: str, dry_run: bool = False) -> bool:
        """Dismiss a specific alert with reason and comment."""
        if len(comment) > 280:
            print(f"Error: Comment too long ({len(comment)} chars). GitHub limit is 280.")
            return False
            
        if reason not in VALID_REASONS:
            print(f"Error: Invalid reason '{reason}'. Valid reasons: {list(VALID_REASONS.keys())}")
            return False
        
        if dry_run:
            print(f"[DRY RUN] Would dismiss alert #{alert_number}")
            print(f"  Reason: {reason}")
            print(f"  Comment: {comment}")
            return True
        
        try:
            # GitHub API expects PATCH request to dismiss alert
            cmd = [
                "gh", "api", f"repos/{self.repo}/dependabot/alerts/{alert_number}",
                "--method", "PATCH",
                "--field", f"state=dismissed",
                "--field", f"dismissed_reason={reason}",
                "--field", f"dismissed_comment={comment}"
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            print(f"✅ Dismissed alert #{alert_number}")
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"❌ Error dismissing alert #{alert_number}: {e}")
            print(f"stderr: {e.stderr}")
            return False
    
    def get_alert_by_package(self, package_name: str) -> Optional[DependabotAlert]:
        """Find open alert for specific package."""
        alerts = self.get_open_alerts()
        for alert in alerts:
            if alert.package_name == package_name:
                return alert
        return None

def validate_dismissal_config():
    """Validate the dismissal configuration."""
    errors = []
    
    for package, config in DISMISSALS.items():
        # Check required fields
        if 'reason' not in config:
            errors.append(f"{package}: Missing 'reason' field")
        elif config['reason'] not in VALID_REASONS:
            errors.append(f"{package}: Invalid reason '{config['reason']}'")
            
        if 'comment' not in config:
            errors.append(f"{package}: Missing 'comment' field")
        elif len(config['comment']) > 280:
            errors.append(f"{package}: Comment too long ({len(config['comment'])} chars)")
    
    if errors:
        print("❌ Configuration validation errors:")
        for error in errors:
            print(f"  {error}")
        return False
    
    print("✅ Configuration validation passed")
    return True

def main():
    """Main execution function."""
    parser = argparse.ArgumentParser(description="Dismiss Dependabot security alerts")
    parser.add_argument("--dry-run", action="store_true", 
                       help="Preview dismissals without executing")
    parser.add_argument("--package", type=str,
                       help="Dismiss alerts for specific package only")
    
    args = parser.parse_args()
    
    # Validate configuration
    if not validate_dismissal_config():
        return 1
    
    # Initialize manager
    manager = DependabotAlertManager()
    
    # Get open alerts
    print("📡 Fetching open Dependabot alerts...")
    open_alerts = manager.get_open_alerts()
    
    if not open_alerts:
        print("✅ No open Dependabot alerts found")
        return 0
    
    print(f"📊 Found {len(open_alerts)} open alerts")
    
    # Filter by package if specified
    if args.package:
        if args.package not in DISMISSALS:
            print(f"❌ Package '{args.package}' not configured for dismissal")
            return 1
        
        alert = manager.get_alert_by_package(args.package)
        if not alert:
            print(f"❌ No open alert found for package '{args.package}'")
            return 1
        
        alerts_to_process = [alert]
        print(f"🎯 Processing single package: {args.package}")
    else:
        # Process all configured packages
        alerts_to_process = []
        for alert in open_alerts:
            if alert.package_name in DISMISSALS:
                alerts_to_process.append(alert)
        
        print(f"🎯 Processing {len(alerts_to_process)} configured alerts")
    
    if not alerts_to_process:
        print("ℹ️  No alerts match dismissal configuration")
        return 0
    
    # Show what will be processed
    print("\n📋 Alerts to dismiss:")
    for alert in alerts_to_process:
        config = DISMISSALS[alert.package_name]
        print(f"  #{alert.number}: {alert.package_name} ({alert.severity})")
        print(f"    Reason: {config['reason']}")
        print(f"    Comment: {config['comment'][:60]}...")
    
    if args.dry_run:
        print("\n🔍 DRY RUN MODE - No alerts will be dismissed")
    else:
        print(f"\n⚠️  About to dismiss {len(alerts_to_process)} alerts")
        response = input("Continue? (yes/no): ")
        if response.lower() != "yes":
            print("Aborted")
            return 0
    
    # Process dismissals
    success_count = 0
    for alert in alerts_to_process:
        config = DISMISSALS[alert.package_name]
        
        if manager.dismiss_alert(
            alert.number, 
            config['reason'], 
            config['comment'],
            dry_run=args.dry_run
        ):
            success_count += 1
    
    # Summary
    if args.dry_run:
        print(f"\n🔍 DRY RUN COMPLETE: {success_count}/{len(alerts_to_process)} alerts would be dismissed")
    else:
        print(f"\n✅ DISMISSAL COMPLETE: {success_count}/{len(alerts_to_process)} alerts dismissed")
        
        if success_count < len(alerts_to_process):
            print("⚠️  Some dismissals failed. Check error messages above.")
            return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())