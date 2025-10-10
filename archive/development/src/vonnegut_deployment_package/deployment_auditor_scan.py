#!/usr/bin/env python3
"""
Deployment Data Governance Scanner Script

Quick script to scan deployment directories for governance violations
and generate remediation recommendations.
"""

import os
import sys
import json
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from deployment_auditor.auditor import DeploymentDataAuditor


def main():
    """Main scanner function."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Deployment Data Governance Scanner')
    parser.add_argument('directory', nargs='?', default='deployment',
                       help='Directory to scan (default: deployment)')
    parser.add_argument('--quiet', '-q', action='store_true',
                       help='Suppress output except violations')
    parser.add_argument('--exit-on-violations', action='store_true',
                       help='Exit with error code if violations found (for CI/CD)')
    parser.add_argument('--format', choices=['text', 'json'], default='text',
                       help='Output format')
    
    args = parser.parse_args()
    scan_dir = args.directory
    
    if not args.quiet:
        print("🔍 Deployment Data Governance Scanner")
        print("=" * 40)
    
    if not os.path.exists(scan_dir):
        if not args.quiet:
            print(f"❌ Directory '{scan_dir}' not found")
        sys.exit(1)
    
    # Initialize auditor
    auditor = DeploymentDataAuditor()
    
    # Perform scan
    if not args.quiet:
        print(f"Scanning: {scan_dir}")
    result = auditor.scan_directory(scan_dir)
    
    # Handle JSON output
    if args.format == 'json':
        print(json.dumps(result, indent=2))
        if args.exit_on_violations and result['violations_found'] > 0:
            sys.exit(1)
        return
    
    # Display results
    if not args.quiet:
        print(f"\n📊 Scan Results:")
        print(f"   Files scanned: {result['total_files_scanned']}")
        print(f"   Violations found: {result['violations_found']}")
    
    if result['violations_found'] > 0:
        print(f"\n⚠️  Violations Detected:")
        
        # Group by category
        by_category = {}
        for violation in result['violations']:
            category = violation['category']
            if category not in by_category:
                by_category[category] = []
            by_category[category].append(violation)
        
        for category, violations in by_category.items():
            print(f"\n   {category.upper()} ({len(violations)} files):")
            for violation in violations[:5]:  # Show first 5
                rel_path = os.path.relpath(violation['file_path'], scan_dir)
                print(f"     • {rel_path}")
            if len(violations) > 5:
                print(f"     ... and {len(violations) - 5} more")
        
        # Generate remediation
        print(f"\n🔧 Remediation Recommendations:")
        patterns = auditor.generate_gitignore_patterns(result['violations'])
        
        print(f"   Add these patterns to .gitignore:")
        for pattern in patterns:
            print(f"     {pattern}")
        
        print(f"\n   Commands to fix:")
        print(f"     # Remove from git tracking")
        for violation in result['violations'][:3]:  # Show first 3
            rel_path = os.path.relpath(violation['file_path'], ".")
            print(f"     git rm --cached '{rel_path}'")
        
        if len(result['violations']) > 3:
            print(f"     # ... and {len(result['violations']) - 3} more files")
        
        print(f"\n     # Update .gitignore and commit")
        print(f"     echo '# Deployment data governance' >> .gitignore")
        for pattern in patterns[:3]:
            print(f"     echo '{pattern}' >> .gitignore")
        print(f"     git add .gitignore")
        print(f"     git commit -m 'Add deployment data governance patterns'")
        
    else:
        if not args.quiet:
            print(f"\n✅ No violations found - deployment directory is clean!")
    
    # Save detailed report (unless quiet mode)
    if not args.quiet:
        report_file = f"deployment-audit-{result['scan_timestamp'][:10]}.json"
        with open(report_file, 'w') as f:
            json.dump(result, f, indent=2)
        print(f"\n📄 Detailed report saved: {report_file}")
    
    # Exit with error if violations found and flag is set
    if args.exit_on_violations and result['violations_found'] > 0:
        sys.exit(1)


if __name__ == "__main__":
    main()