#!/usr/bin/env python3
"""
Redis Execution Tracking Validator
==================================

Validates that claimed DAG executions actually have corresponding Redis tracking records.
Generated as corrective action for missing Redis state persistence.
"""

import redis
import json
import sys
import os
from datetime import datetime
from typing import Dict, List, Optional, Any
from pathlib import Path


class RedisExecutionValidator:
    """Validates Redis execution tracking records."""
    
    def __init__(self, redis_host: str = "192.168.1.119", redis_port: int = 6379, redis_password: str = None):
        """Initialize Redis connection."""
        # Load environment variables from ~/.env
        self.load_env_vars()
        
        # Get password from environment if not provided
        if redis_password is None:
            redis_password = os.getenv('REDIS_PASSWORD', os.getenv('BEAST_MODE_REDIS_PASSWORD', ''))
        
        try:
            self.redis_client = redis.Redis(host=redis_host, port=redis_port, password=redis_password, decode_responses=True)
            self.redis_client.ping()
            print(f"✅ Connected to Redis at {redis_host}:{redis_port}")
        except Exception as e:
            print(f"❌ Failed to connect to Redis: {e}")
            if not redis_password:
                print("💡 Tip: Add REDIS_PASSWORD to ~/.env file")
            sys.exit(1)
    
    def load_env_vars(self):
        """Load environment variables from ~/.env if it exists."""
        home_env = Path.home() / ".env"
        if home_env.exists():
            with open(home_env, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        os.environ[key.strip()] = value.strip().strip('"').strip("'")
    
    def validate_execution_id(self, execution_id: str) -> Dict[str, Any]:
        """Validate that an execution ID has proper Redis tracking records."""
        print(f"\n🔍 Validating execution: {execution_id}")
        
        results = {
            "execution_id": execution_id,
            "redis_records_found": False,
            "tracking_keys": [],
            "validation_status": "FAILED",
            "issues": []
        }
        
        # Check for exact execution ID key
        if self.redis_client.exists(execution_id):
            results["redis_records_found"] = True
            results["tracking_keys"].append(execution_id)
            print(f"✅ Found exact execution record: {execution_id}")
        else:
            results["issues"].append(f"Missing exact execution record: {execution_id}")
            print(f"❌ Missing exact execution record: {execution_id}")
        
        # Check for pattern-based keys
        pattern_keys = self.redis_client.keys(f"*{execution_id}*")
        if pattern_keys:
            results["tracking_keys"].extend(pattern_keys)
            print(f"✅ Found pattern-based keys: {pattern_keys}")
        else:
            results["issues"].append(f"No pattern-based keys found for: {execution_id}")
            print(f"❌ No pattern-based keys found for: {execution_id}")
        
        # Check for spec-based keys
        if "_" in execution_id:
            spec_name = execution_id.split("_")[0]
            spec_keys = self.redis_client.keys(f"*{spec_name}*")
            if spec_keys:
                results["tracking_keys"].extend(spec_keys)
                print(f"✅ Found spec-based keys: {spec_keys}")
            else:
                results["issues"].append(f"No spec-based keys found for: {spec_name}")
                print(f"❌ No spec-based keys found for: {spec_name}")
        
        # Determine validation status
        if results["redis_records_found"] or results["tracking_keys"]:
            results["validation_status"] = "VERIFIED"
        else:
            results["validation_status"] = "UNVERIFIED"
        
        return results
    
    def validate_recent_executions(self, hours: int = 24) -> List[Dict[str, Any]]:
        """Validate all Redis keys that look like recent executions."""
        print(f"\n🔍 Scanning for execution-like keys from last {hours} hours...")
        
        all_keys = self.redis_client.keys("*")
        execution_like_keys = []
        
        for key in all_keys:
            # Look for keys that match execution ID patterns
            if any(pattern in key.lower() for pattern in ["execution", "launch", "task", "20251002"]):
                execution_like_keys.append(key)
        
        print(f"📊 Found {len(execution_like_keys)} execution-like keys: {execution_like_keys}")
        return execution_like_keys
    
    def generate_verification_report(self, execution_ids: List[str]) -> Dict[str, Any]:
        """Generate comprehensive verification report."""
        report = {
            "timestamp": datetime.now().isoformat(),
            "total_executions_checked": len(execution_ids),
            "verified_executions": 0,
            "unverified_executions": 0,
            "execution_results": [],
            "redis_health": self.check_redis_health(),
            "recommendations": []
        }
        
        for execution_id in execution_ids:
            result = self.validate_execution_id(execution_id)
            report["execution_results"].append(result)
            
            if result["validation_status"] == "VERIFIED":
                report["verified_executions"] += 1
            else:
                report["unverified_executions"] += 1
        
        # Generate recommendations
        if report["unverified_executions"] > 0:
            report["recommendations"].append("CRITICAL: Unverified executions detected - investigate Redis persistence implementation")
            report["recommendations"].append("Update execution system to ensure Redis tracking records are actually created")
            report["recommendations"].append("Add mandatory post-execution Redis verification to prevent false completion claims")
        
        if report["verified_executions"] == 0 and len(execution_ids) > 0:
            report["recommendations"].append("URGENT: Zero verified executions - Redis tracking system may be completely non-functional")
        
        return report
    
    def check_redis_health(self) -> Dict[str, Any]:
        """Check Redis health and configuration."""
        health = {
            "connection_status": "connected",
            "total_keys": len(self.redis_client.keys("*")),
            "memory_usage": "unknown",
            "redis_version": "unknown"
        }
        
        try:
            info = self.redis_client.info()
            health["redis_version"] = info.get("redis_version", "unknown")
            health["memory_usage"] = info.get("used_memory_human", "unknown")
        except Exception as e:
            health["info_error"] = str(e)
        
        return health


def main():
    """Main validation function."""
    print("🚀 Redis Execution Tracking Validator")
    print("=" * 50)
    
    validator = RedisExecutionValidator()
    
    # Check for recent execution IDs from command line or logs
    execution_ids = []
    
    if len(sys.argv) > 1:
        execution_ids = sys.argv[1:]
        print(f"📋 Validating provided execution IDs: {execution_ids}")
    else:
        # Try to find recent execution IDs from logs
        print("📋 No execution IDs provided, scanning for recent executions...")
        recent_keys = validator.validate_recent_executions()
        
        # Add known recent execution ID from our analysis
        execution_ids = ["live-dashboard-engagement-system_20251002_075945_c3fd43"]
        print(f"📋 Using known recent execution ID: {execution_ids}")
    
    # Generate verification report
    report = validator.generate_verification_report(execution_ids)
    
    # Print summary
    print("\n" + "=" * 50)
    print("📊 VERIFICATION SUMMARY")
    print("=" * 50)
    print(f"Total Executions Checked: {report['total_executions_checked']}")
    print(f"Verified Executions: {report['verified_executions']}")
    print(f"Unverified Executions: {report['unverified_executions']}")
    print(f"Redis Health: {report['redis_health']['connection_status']}")
    print(f"Total Redis Keys: {report['redis_health']['total_keys']}")
    
    if report['recommendations']:
        print("\n🚨 RECOMMENDATIONS:")
        for rec in report['recommendations']:
            print(f"  • {rec}")
    
    # Save detailed report
    report_file = f"redis_validation_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(report_file, 'w') as f:
        json.dump(report, f, indent=2)
    print(f"\n📄 Detailed report saved to: {report_file}")
    
    # Exit with appropriate code
    if report['unverified_executions'] > 0:
        print("\n❌ VALIDATION FAILED: Unverified executions detected")
        sys.exit(1)
    else:
        print("\n✅ VALIDATION PASSED: All executions verified")
        sys.exit(0)


if __name__ == "__main__":
    main()