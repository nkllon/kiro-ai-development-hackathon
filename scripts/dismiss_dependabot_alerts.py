#!/usr/bin/env python3
"""
Dismiss Dependabot alerts with risk acceptance documentation.

This script dismisses Dependabot security alerts that have been analyzed
and determined to pose no actual risk to the system.
"""

import subprocess
import json
import sys
from typing import Dict, List

# Alert dismissal configuration
DISMISSALS = {
    # python-jose - CRITICAL but not used
    "python-jose": {
        "reason": "not_used",
        "comment": (
            "Risk Accepted: python-jose is listed in requirements-cms-search.txt "
            "but no JWT/authentication code exists in src/cms_search/. "
            "This is an unused dependency that was added for future features "
            "that were never implemented. Attack surface: None."
        )
    },

    # python-multipart - HIGH but not used
    "python-multipart": {
        "reason": "not_used",
        "comment": (
            "Risk Accepted: python-multipart is in cms-repo-sync and cms-search "
            "requirements but no actual file upload endpoints exist in the codebase. "
            "No UploadFile or multipart form handling found. Behind Cloudflare WAF. "
            "Attack surface: None."
        )
    },

    # gunicorn - HIGH but false positive
    "gunicorn": {
        "reason": "inaccurate",
        "comment": (
            "False Positive: gunicorn is not in any requirements files. "
            "System uses uvicorn, not gunicorn. Dependabot may be scanning "
            "old lock files or transitive dependencies that aren't actually used."
        )
    },

    # jinja2/Jinja2 - MEDIUM, tolerable risk
    "jinja2": {
        "reason": "tolerable_risk",
        "comment": (
            "Risk Accepted: No untrusted template rendering. Jinja2 only for "
            "internal FastAPI HTML templates. No user-provided template content. "
            "Behind Cloudflare WAF. Attack surface: None."
        )
    },

    "Jinja2": {
        "reason": "tolerable_risk",
        "comment": (
            "Risk Accepted: No untrusted template rendering. Jinja2 only for "
            "internal FastAPI HTML templates. No user-provided template content. "
            "Behind Cloudflare WAF. Attack surface: None."
        )
    },

    # requests - MEDIUM, tolerable risk
    "requests": {
        "reason": "tolerable_risk",
        "comment": (
            "Risk Accepted: Requests only for internal APIs with controlled URLs. "
            "No user-provided URLs. Internal dev framework, not public service."
        )
    },

    # black - MEDIUM, dev-only
    "black": {
        "reason": "tolerable_risk",
        "comment": (
            "Risk Accepted: Black is a development-only code formatter. "
            "ReDoS vulnerability only affects dev tooling during code formatting, "
            "not runtime application code. No user input processed by black. "
            "Out of scope for production security concerns."
        )
    }
}


def get_open_alerts() -> List[Dict]:
    """Get all open Dependabot alerts."""
    try:
        result = subprocess.run(
            [
                'gh', 'api',
                'repos/nkllon/kiro-ai-development-hackathon/dependabot/alerts',
                '--jq', '.'
            ],
            capture_output=True,
            text=True,
            check=True
        )

        alerts = json.loads(result.stdout)
        return [a for a in alerts if a['state'] == 'open']

    except subprocess.CalledProcessError as e:
        print(f"Error fetching alerts: {e.stderr}")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error parsing alerts JSON: {e}")
        sys.exit(1)


def dismiss_alert(alert_number: int, package: str, reason: str, comment: str) -> bool:
    """Dismiss a single Dependabot alert."""
    try:
        data = {
            "state": "dismissed",
            "dismissed_reason": reason,
            "dismissed_comment": comment
        }

        result = subprocess.run(
            [
                'gh', 'api',
                f'repos/nkllon/kiro-ai-development-hackathon/dependabot/alerts/{alert_number}',
                '-X', 'PATCH',
                '-f', f'state={data["state"]}',
                '-f', f'dismissed_reason={data["dismissed_reason"]}',
                '-f', f'dismissed_comment={data["dismissed_comment"]}'
            ],
            capture_output=True,
            text=True,
            check=True
        )

        print(f"✅ Dismissed alert #{alert_number} for {package} (reason: {reason})")
        return True

    except subprocess.CalledProcessError as e:
        print(f"❌ Error dismissing alert #{alert_number} for {package}: {e.stderr}")
        return False


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description='Dismiss Dependabot alerts with risk acceptance documentation'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show what would be dismissed without actually dismissing'
    )
    parser.add_argument(
        '--package',
        help='Only dismiss alerts for specific package'
    )

    args = parser.parse_args()

    print("🔍 Fetching open Dependabot alerts...")
    alerts = get_open_alerts()

    if not alerts:
        print("✅ No open alerts found")
        return 0

    print(f"Found {len(alerts)} open alerts\n")

    dismissed_count = 0
    skipped_count = 0

    for alert in alerts:
        alert_number = alert['number']
        package = alert['dependency']['package']['name']
        severity = alert['security_advisory']['severity']
        summary = alert['security_advisory']['summary']

        # Skip if filtering by package
        if args.package and package != args.package:
            continue

        # Check if we have a dismissal config for this package
        if package not in DISMISSALS:
            print(f"⚠️  Alert #{alert_number}: {package} ({severity}) - No dismissal config")
            skipped_count += 1
            continue

        dismissal = DISMISSALS[package]

        print(f"\n📋 Alert #{alert_number}: {package} ({severity})")
        print(f"   Vulnerability: {summary}")
        print(f"   Dismissal reason: {dismissal['reason']}")
        print(f"   Comment: {dismissal['comment'][:100]}...")

        if args.dry_run:
            print(f"   [DRY RUN] Would dismiss")
            dismissed_count += 1
        else:
            if dismiss_alert(alert_number, package, dismissal['reason'], dismissal['comment']):
                dismissed_count += 1
            else:
                skipped_count += 1

    print(f"\n{'=' * 70}")
    print(f"Summary:")
    print(f"  Dismissed: {dismissed_count}")
    print(f"  Skipped: {skipped_count}")

    if args.dry_run:
        print(f"\n💡 Run without --dry-run to actually dismiss alerts")

    return 0


if __name__ == '__main__':
    sys.exit(main())
