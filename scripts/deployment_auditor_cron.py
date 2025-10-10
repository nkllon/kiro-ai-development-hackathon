#!/usr/bin/env python3
"""
Cron job setup for deployment auditor.

This script helps set up periodic scanning using system cron jobs.
"""

import os
import sys
from pathlib import Path


def generate_cron_entry(interval_minutes=60, directory="deployment"):
    """Generate a cron entry for the deployment auditor."""
    
    # Get absolute paths
    script_dir = Path(__file__).parent.absolute()
    project_dir = script_dir.parent
    daemon_script = script_dir / "deployment_auditor_daemon.py"
    
    # Generate cron entry
    cron_entry = f"""
# Deployment Data Governance Auditor - Auto-generated
# Scans every {interval_minutes} minutes for deployment data violations
*/{interval_minutes} * * * * cd {project_dir} && python {daemon_script} --once --directory {directory} >> /tmp/deployment-auditor.log 2>&1
"""
    
    return cron_entry.strip()


def install_cron_job(interval_minutes=60, directory="deployment"):
    """Install the cron job."""
    
    print(f"🕐 Setting up cron job for deployment auditor")
    print(f"   Interval: Every {interval_minutes} minutes")
    print(f"   Directory: {directory}")
    print(f"   Log file: /tmp/deployment-auditor.log")
    
    cron_entry = generate_cron_entry(interval_minutes, directory)
    
    print(f"\n📋 Cron entry to add:")
    print("-" * 50)
    print(cron_entry)
    print("-" * 50)
    
    print(f"\n🔧 To install:")
    print(f"1. Run: crontab -e")
    print(f"2. Add the above line to your crontab")
    print(f"3. Save and exit")
    
    print(f"\n📊 To monitor:")
    print(f"   tail -f /tmp/deployment-auditor.log")
    
    print(f"\n🗑️  To remove:")
    print(f"   crontab -e  # and delete the deployment auditor line")
    
    return cron_entry


def main():
    """Main function."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Setup cron job for deployment auditor')
    parser.add_argument('--interval', '-i', type=int, default=60,
                       help='Scan interval in minutes (default: 60)')
    parser.add_argument('--directory', '-d', default='deployment',
                       help='Directory to scan (default: deployment)')
    
    args = parser.parse_args()
    
    if not os.path.exists(args.directory):
        print(f"❌ Directory '{args.directory}' not found")
        sys.exit(1)
    
    install_cron_job(args.interval, args.directory)


if __name__ == '__main__':
    main()