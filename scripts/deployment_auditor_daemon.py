#!/usr/bin/env python3
"""
Simple deployment auditor daemon for periodic scanning.

This provides basic scheduled scanning functionality until the full
real-time monitoring system is implemented.
"""

import os
import sys
import time
import signal
import json
from datetime import datetime
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from deployment_auditor.auditor import DeploymentDataAuditor


class DeploymentAuditorDaemon:
    """Simple daemon for periodic deployment scanning."""
    
    def __init__(self, scan_interval=300, scan_directory="deployment"):
        self.scan_interval = scan_interval  # seconds
        self.scan_directory = scan_directory
        self.running = False
        self.auditor = DeploymentDataAuditor()
        self.last_scan_result = None
        
        # Set up signal handlers
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals."""
        print(f"\n📡 Received signal {signum}, shutting down daemon...")
        self.running = False
    
    def start(self):
        """Start the daemon."""
        print(f"🚀 Starting Deployment Auditor Daemon")
        print(f"   Scan directory: {self.scan_directory}")
        print(f"   Scan interval: {self.scan_interval} seconds")
        print(f"   PID: {os.getpid()}")
        print(f"   Press Ctrl+C to stop")
        print("=" * 50)
        
        self.running = True
        scan_count = 0
        
        while self.running:
            try:
                scan_count += 1
                print(f"\n🔍 Scan #{scan_count} - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                
                # Perform scan
                result = self.auditor.scan_directory(self.scan_directory)
                self.last_scan_result = result
                
                # Report results
                violations = result['violations_found']
                files_scanned = result['total_files_scanned']
                
                if violations > 0:
                    print(f"⚠️  Found {violations} violations in {files_scanned} files")
                    
                    # Save violation report
                    report_file = f"violation-report-{datetime.now().strftime('%Y%m%d-%H%M%S')}.json"
                    with open(report_file, 'w') as f:
                        json.dump(result, f, indent=2)
                    
                    print(f"📄 Detailed report saved: {report_file}")
                    
                    # Show top violations
                    violations_by_category = {}
                    for violation in result['violations']:
                        category = violation['category']
                        if category not in violations_by_category:
                            violations_by_category[category] = 0
                        violations_by_category[category] += 1
                    
                    print("   Violations by category:")
                    for category, count in violations_by_category.items():
                        print(f"     {category}: {count}")
                        
                else:
                    print(f"✅ No violations found in {files_scanned} files")
                
                # Wait for next scan
                if self.running:
                    print(f"😴 Sleeping for {self.scan_interval} seconds...")
                    for i in range(self.scan_interval):
                        if not self.running:
                            break
                        time.sleep(1)
                        
            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"❌ Scan error: {e}")
                print("   Continuing with next scan...")
                time.sleep(10)  # Brief pause before retry
        
        print(f"\n🛑 Daemon stopped after {scan_count} scans")
    
    def status(self):
        """Get daemon status."""
        return {
            'running': self.running,
            'scan_interval': self.scan_interval,
            'scan_directory': self.scan_directory,
            'last_scan': self.last_scan_result
        }


def main():
    """Main daemon function."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Deployment Auditor Daemon')
    parser.add_argument('--interval', '-i', type=int, default=300,
                       help='Scan interval in seconds (default: 300)')
    parser.add_argument('--directory', '-d', default='deployment',
                       help='Directory to scan (default: deployment)')
    parser.add_argument('--once', action='store_true',
                       help='Run once and exit (no daemon mode)')
    
    args = parser.parse_args()
    
    if not os.path.exists(args.directory):
        print(f"❌ Directory '{args.directory}' not found")
        sys.exit(1)
    
    daemon = DeploymentAuditorDaemon(
        scan_interval=args.interval,
        scan_directory=args.directory
    )
    
    if args.once:
        print("🔍 Running single scan...")
        result = daemon.auditor.scan_directory(args.directory)
        violations = result['violations_found']
        
        if violations > 0:
            print(f"⚠️  Found {violations} violations")
            sys.exit(1)  # Exit with error for CI/CD
        else:
            print("✅ No violations found")
            sys.exit(0)
    else:
        daemon.start()


if __name__ == '__main__':
    main()