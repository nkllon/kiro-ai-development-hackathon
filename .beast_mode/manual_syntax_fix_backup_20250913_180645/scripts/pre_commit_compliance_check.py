#!/usr/bin/env python3
"""
Pre-commit hook: Compliance Check
Ensures all interfaces meet 95%+ compliance standards.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from .continuous_compliance_monitor import ContinuousComplianceMonitor

def main():
    """Run compliance check."""
    monitor = ContinuousComplianceMonitor()
    compliance_status = monitor.check_compliance_status()
    
    if compliance_status['overall_compliance'] < 95.0:
        print(f"❌ Compliance check failed: {compliance_status['overall_compliance']:.1f}% < 95%")
        sys.exit(1)
    else:
        print(f"✅ Compliance check passed: {compliance_status['overall_compliance']:.1f}%")
        sys.exit(0)

if __name__ == "__main__":
    main()
