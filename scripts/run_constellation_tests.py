#!/usr/bin/env python3
"""
Constellation Elaboration Test Suite
Runs comprehensive tests to validate system readiness
"""

import asyncio
import subprocess
import sys
import time
from pathlib import Path
from typing import Dict, Any

class ConstellationTestRunner:
    """Comprehensive test runner for constellation elaboration system"""
    
    def __init__(self):
        self.test_results = {}
        self.start_time = time.time()
    
    def log(self, message: str, level: str = "INFO"):
        """Log message with timestamp"""
        elapsed = time.time() - self.start_time
        print(f"[{elapsed:6.1f}s] {level:5s}: {message}")
    
    async def run_test(self, test_name: str, test_script: str, *args) -> Dict[str, Any]:
        """Run a single test script and capture results"""
        
        self.log(f"Starting {test_name}", "TEST")
        
        script_path = Path(__file__).parent / test_script
        if not script_path.exists():
            result = {
                "status": "failed",
                "error": f"Test script not found: {test_script}",
                "duration": 0
            }
            self.test_results[test_name] = result
            self.log(f"❌ {test_name} - Script not found", "FAIL")
            return result
        
        start_time = time.time()
        
        try:
            # Run the test script
            cmd = [sys.executable, str(script_path)] + list(args)
            
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            end_time = time.time()
            duration = end_time - start_time
            
            result = {
                "status": "passed" if process.returncode == 0 else "failed",
                "return_code": process.returncode,
                "duration": duration,
                "stdout": stdout.decode('utf-8'),
                "stderr": stderr.decode('utf-8')
            }
            
            if process.returncode == 0:
                self.log(f"✅ {test_name} - Passed in {duration:.1f}s", "PASS")
            else:
                self.log(f"❌ {test_name} - Failed (rc={process.returncode}) in {duration:.1f}s", "FAIL")
                if stderr:
                    self.log(f"   Error: {stderr.decode('utf-8')[:200]}...", "FAIL")
            
        except Exception as e:
            end_time = time.time()
            duration = end_time - start_time
            
            result = {
                "status": "error",
                "error": str(e),
                "duration": duration
            }
            
            self.log(f"💥 {test_name} - Exception: {e}", "ERROR")
        
        self.test_results[test_name] = result
        return result
    
    async def run_all_tests(self) -> Dict[str, Any]:
        """Run complete test suite"""
        
        self.log("🧪 Starting Constellation Elaboration Test Suite", "START")
        self.log("=" * 60, "START")
        
        # Test 1: Dry Run (Quick validation)
        await self.run_test(
            "Orchestrator Dry Run",
            "test_orchestrator_dry_run.py"
        )
        
        # Check if dry run passed before proceeding
        if self.test_results["Orchestrator Dry Run"]["status"] != "passed":
            self.log("❌ Dry run failed - stopping test suite", "STOP")
            return self.generate_summary()
        
        # Test 2: Single Prompt Execution
        await self.run_test(
            "Single Prompt Execution",
            "test_single_prompt.py",
            "prompts/staging/phase-1b1-stakeholder-extraction.md"
        )
        
        # Check if single prompt passed before parallel test
        if self.test_results["Single Prompt Execution"]["status"] != "passed":
            self.log("⚠️  Single prompt failed - skipping parallel test", "WARN")
        else:
            # Test 3: Parallel Execution
            await self.run_test(
                "Parallel Execution",
                "test_parallel_minimal.py"
            )
        
        return self.generate_summary()
    
    def generate_summary(self) -> Dict[str, Any]:
        """Generate comprehensive test summary"""
        
        total_time = time.time() - self.start_time
        
        passed = sum(1 for r in self.test_results.values() if r["status"] == "passed")
        failed = sum(1 for r in self.test_results.values() if r["status"] in ["failed", "error"])
        total = len(self.test_results)
        
        self.log("=" * 60, "SUMMARY")
        self.log("🏁 TEST SUITE COMPLETE", "SUMMARY")
        self.log("=" * 60, "SUMMARY")
        
        self.log(f"📊 Results: {passed}/{total} tests passed", "SUMMARY")
        self.log(f"⏱️  Total time: {total_time:.1f}s", "SUMMARY")
        
        # Detailed results
        for test_name, result in self.test_results.items():
            status_icon = "✅" if result["status"] == "passed" else "❌"
            duration = result.get("duration", 0)
            self.log(f"   {status_icon} {test_name}: {result['status']} ({duration:.1f}s)", "SUMMARY")
        
        # Recommendations
        self.log("", "SUMMARY")
        if failed == 0:
            self.log("🚀 RECOMMENDATION: System is ready for constellation execution", "SUMMARY")
            self.log("   Next steps:", "SUMMARY")
            self.log("   1. Execute with original 20 prompts (safe approach)", "SUMMARY")
            self.log("   2. Or generate all breakdown prompts and execute optimized", "SUMMARY")
        elif passed > 0:
            self.log("⚠️  RECOMMENDATION: Partial success - investigate failures", "SUMMARY")
            self.log("   Fix failing tests before full execution", "SUMMARY")
        else:
            self.log("❌ RECOMMENDATION: System not ready - fix all issues", "SUMMARY")
            self.log("   Do not attempt constellation execution yet", "SUMMARY")
        
        return {
            "total_tests": total,
            "passed": passed,
            "failed": failed,
            "total_time": total_time,
            "results": self.test_results,
            "ready_for_execution": failed == 0
        }

async def main():
    """Main test runner"""
    
    runner = ConstellationTestRunner()
    summary = await runner.run_all_tests()
    
    # Return appropriate exit code
    if summary["ready_for_execution"]:
        return 0  # All tests passed
    elif summary["passed"] > 0:
        return 1  # Partial success
    else:
        return 2  # All tests failed

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)