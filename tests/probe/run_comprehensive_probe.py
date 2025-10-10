#!/usr/bin/env python3
"""
Comprehensive WebSocket Infrastructure Test Probe Execution Script

This script executes the comprehensive test probe to validate all WebSocket
infrastructure components, integration points, and system reliability.

Usage:
    python run_comprehensive_probe.py [--quick] [--base-url URL] [--websocket-url URL]

Options:
    --quick: Run quick validation instead of full comprehensive test
    --base-url: Base URL for HTTP endpoints (default: https://observatory.nkllon.com)
    --websocket-url: WebSocket URL (default: wss://observatory.nkllon.com)
"""

import asyncio
import json
import sys
import argparse
from datetime import datetime
from typing import Dict, Any

from comprehensive_test_suite import ComprehensiveTestSuite


def log_probe_start():
    """Log probe start"""
    log_entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "probe": "test_probe",
        "action": "probe_deployment",
        "status": "in_progress",
        "results": {
            "mission": "Comprehensive WebSocket Infrastructure Validation",
            "objectives": [
                "WebSocket Connectivity Validation",
                "Fallback Mechanism Testing", 
                "Bot Protection Integration",
                "Performance Benchmarking",
                "Failure Recovery Testing"
            ]
        }
    }
    print(json.dumps(log_entry))


def log_probe_completion(result: Dict[str, Any]):
    """Log probe completion"""
    log_entry = {
        "probe": "test_probe",
        "status": "completed",
        "summary": "Comprehensive WebSocket infrastructure validation complete",
        "tests_run": result.get("total_tests", 0),
        "success_rate": f"{result.get('success_rate', 0):.1f}%",
        "critical_issues": len(result.get("critical_issues", [])),
        "recommendations": len(result.get("recommendations", [])),
        "performance_metrics": result.get("performance_metrics", {}),
        "timestamp": datetime.utcnow().isoformat()
    }
    print(json.dumps(log_entry))


async def main():
    """Main execution function"""
    parser = argparse.ArgumentParser(description="Comprehensive WebSocket Infrastructure Test Probe")
    parser.add_argument("--quick", action="store_true", help="Run quick validation")
    parser.add_argument("--base-url", default="https://observatory.nkllon.com", 
                       help="Base URL for HTTP endpoints")
    parser.add_argument("--websocket-url", default="wss://observatory.nkllon.com",
                       help="WebSocket URL")
    parser.add_argument("--output-file", help="Output file for detailed report")
    
    args = parser.parse_args()
    
    # Log probe start
    log_probe_start()
    
    try:
        # Initialize test suite
        test_suite = ComprehensiveTestSuite(args.base_url)
        
        if args.quick:
            # Run quick validation
            result = await test_suite.run_quick_validation()
            print("\n" + "="*60)
            print("QUICK VALIDATION RESULTS")
            print("="*60)
            print(json.dumps(result, indent=2))
        else:
            # Run comprehensive validation
            comprehensive_result = await test_suite.run_comprehensive_validation()
            
            # Convert result to dictionary for logging
            result_dict = {
                "total_tests": comprehensive_result.total_tests,
                "passed_tests": comprehensive_result.passed_tests,
                "failed_tests": comprehensive_result.failed_tests,
                "success_rate": comprehensive_result.success_rate,
                "critical_issues": comprehensive_result.critical_issues,
                "recommendations": comprehensive_result.recommendations,
                "performance_metrics": comprehensive_result.performance_metrics,
                "overall_duration_seconds": comprehensive_result.overall_duration_seconds
            }
            
            # Generate and display report
            report = test_suite.generate_final_report(comprehensive_result)
            print("\n" + "="*80)
            print("COMPREHENSIVE WEBSOCKET INFRASTRUCTURE VALIDATION REPORT")
            print("="*80)
            print(report)
            
            # Save report to file if requested
            if args.output_file:
                with open(args.output_file, 'w') as f:
                    f.write(report)
                print(f"\nDetailed report saved to: {args.output_file}")
            
            # Log probe completion
            log_probe_completion(result_dict)
            
            # Exit with appropriate code
            if comprehensive_result.success_rate >= 95:
                print("\n✅ PROBE SUCCESS: WebSocket infrastructure validation PASSED")
                sys.exit(0)
            elif comprehensive_result.success_rate >= 80:
                print("\n⚠️  PROBE WARNING: WebSocket infrastructure validation PARTIAL")
                sys.exit(1)
            else:
                print("\n❌ PROBE FAILURE: WebSocket infrastructure validation FAILED")
                sys.exit(2)
    
    except Exception as e:
        # Log probe error
        error_log = {
            "timestamp": datetime.utcnow().isoformat(),
            "probe": "test_probe",
            "action": "probe_execution",
            "status": "error",
            "results": {
                "error": str(e),
                "error_type": type(e).__name__
            }
        }
        print(json.dumps(error_log))
        
        print(f"\n❌ PROBE ERROR: {str(e)}")
        sys.exit(3)


if __name__ == "__main__":
    asyncio.run(main())