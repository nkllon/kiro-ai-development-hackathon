#!/usr/bin/env python3
"""
Quality Comparison Baseline CLI
==============================

Command line interface for QualityComparisonBaseline operations.
Demonstrates proper CLI usage with arguments.
"""

import sys
import os
import argparse
import json

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from multi_perspective_ghostbusters.quality_comparison_baseline import QualityComparisonBaseline

def main():
    parser = argparse.ArgumentParser(description='Quality Comparison Baseline CLI')
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Health check command
    health_parser = subparsers.add_parser('health', help='Check component health')
    
    # Execute command
    exec_parser = subparsers.add_parser('execute', help='Execute component')
    
    # Get health status command
    status_parser = subparsers.add_parser('status', help='Get detailed health status')
    
    # List capabilities command
    caps_parser = subparsers.add_parser('capabilities', help='List component capabilities')
    
    # DDD metadata command
    ddd_parser = subparsers.add_parser('ddd-info', help='Get DDD metadata')
    
    # Validate DDD compliance
    validate_parser = subparsers.add_parser('validate', help='Validate DDD compliance')
    
    # Generate quality report
    report_parser = subparsers.add_parser('generate-report', help='Generate quality comparison report')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    # Create QualityComparisonBaseline instance
    baseline = QualityComparisonBaseline()
    
    print(f"🚨 Quality Comparison Baseline CLI - Command: {args.command} 🚨")
    print("=" * 60)
    
    if args.command == 'health':
        health = baseline.health_check()
        print(f"Health Status: {health.status.value}")
        print(f"Uptime: {health.uptime:.3f}s")
        print(f"Error Count: {health.error_count}")
        print(f"Success Rate: {health.success_rate:.1%}")
        
    elif args.command == 'execute':
        result = baseline.execute()
        print("Execute Result:")
        print(json.dumps(result, indent=2, default=str))
        
    elif args.command == 'status':
        status = baseline.get_health_status()
        print("Detailed Health Status:")
        print(json.dumps(status, indent=2, default=str))
        
    elif args.command == 'capabilities':
        capabilities = baseline.list_capabilities()
        print(f"Available Capabilities ({len(capabilities)}):")
        for i, cap in enumerate(capabilities, 1):
            print(f"  {i:2d}. {cap}")
            
    elif args.command == 'ddd-info':
        ddd_info = baseline.get_ddd_metadata()
        print("DDD Metadata:")
        print(json.dumps(ddd_info, indent=2, default=str))
        
    elif args.command == 'validate':
        validation = baseline.validate_ddd_compliance()
        print("DDD Compliance Validation:")
        print(json.dumps(validation, indent=2, default=str))
        
    elif args.command == 'generate-report':
        # Generate a sample quality comparison report
        sample_comparisons = []  # Empty for demo
        report = baseline.generate_quality_comparison_report(sample_comparisons)
        print("Quality Comparison Report:")
        print(json.dumps(report, indent=2, default=str))
    
    print("\n✅ Command completed successfully!")

if __name__ == "__main__":
    main()