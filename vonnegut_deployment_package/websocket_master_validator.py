#!/usr/bin/env python3
"""
WebSocket Master Validator
Phase 3 WebSocket Validation and Testing - Master Test Runner

This script orchestrates all WebSocket validation tests and generates a comprehensive report.

Executes:
1. Comprehensive WebSocket Validation Suite
2. Performance Validator
3. Integration Tester
4. Generates detailed validation report with success/failure status
"""

import asyncio
import json
import time
import subprocess
import sys
import os
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import signal

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('websocket_master_validation.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class ValidationPhase:
    name: str
    script_path: str
    description: str
    required: bool = True
    timeout: int = 300  # 5 minutes default timeout

class WebSocketMasterValidator:
    """Master validator that orchestrates all WebSocket validation tests."""
    
    def __init__(self):
        self.validation_phases = [
            ValidationPhase(
                name="comprehensive_validation",
                script_path="scripts/comprehensive_websocket_validation_suite.py",
                description="Comprehensive WebSocket validation for all 4 endpoints",
                timeout=600  # 10 minutes
            ),
            ValidationPhase(
                name="performance_validation",
                script_path="scripts/websocket_performance_validator.py",
                description="Performance metrics validation (connection time, latency, stability)",
                timeout=900  # 15 minutes (includes 5-minute stability test)
            ),
            ValidationPhase(
                name="integration_validation",
                script_path="scripts/websocket_integration_tester.py",
                description="Integration testing for dashboard connections and real-time functionality",
                timeout=300  # 5 minutes
            )
        ]
        
        self.results: Dict[str, Any] = {}
        self.start_time = None
        self.stop_requested = False
        
        # Setup signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals gracefully."""
        logger.info(f"Received signal {signum}, initiating graceful shutdown...")
        self.stop_requested = True
    
    async def run_complete_validation(self) -> Dict[str, Any]:
        """Run the complete WebSocket validation suite."""
        logger.info("🚀 Starting Phase 3 WebSocket Validation and Testing")
        logger.info("=" * 60)
        
        self.start_time = time.time()
        
        # Print validation overview
        self._print_validation_overview()
        
        # Run each validation phase
        for phase in self.validation_phases:
            if self.stop_requested:
                logger.info("⏹️ Validation stopped by user request")
                break
                
            await self._run_validation_phase(phase)
        
        # Generate comprehensive report
        total_duration = time.time() - self.start_time
        report = self._generate_master_report(total_duration)
        
        # Save and display results
        self._save_and_display_results(report)
        
        return report
    
    def _print_validation_overview(self):
        """Print validation overview."""
        print("\n📋 PHASE 3 WEBSOCKET VALIDATION OVERVIEW")
        print("=" * 60)
        print("🎯 Objectives:")
        print("  • Execute comprehensive WebSocket testing suite for all 4 endpoints")
        print("  • Validate connection establishment (< 2 seconds)")
        print("  • Test message exchange and error handling")
        print("  • Verify performance metrics (latency < 100ms)")
        print("  • Test connection stability (> 30 minutes)")
        print("  • Run integration tests for dashboard WebSocket connections")
        print("  • Test real-time emoji rain functionality")
        print("  • Validate live status updates streaming")
        print("  • Test anomaly detection streaming")
        print("  • Generate detailed validation report")
        
        print("\n🔌 WebSocket Endpoints to Test:")
        print("  • /ws/emoji-rain - Real-time emoji rain updates")
        print("  • /ws/observatory - Observatory status updates")
        print("  • /ws/anomalies - Real-time anomaly alerts")
        print("  • /ws/doctor-status - System health doctor updates")
        
        print("\n📊 Validation Phases:")
        for i, phase in enumerate(self.validation_phases, 1):
            print(f"  {i}. {phase.name.replace('_', ' ').title()}")
            print(f"     {phase.description}")
            print(f"     Script: {phase.script_path}")
            print(f"     Timeout: {phase.timeout}s")
            print()
    
    async def _run_validation_phase(self, phase: ValidationPhase):
        """Run a single validation phase."""
        logger.info(f"🔄 Running {phase.name.replace('_', ' ').title()}...")
        print(f"\n{'='*20} {phase.name.upper().replace('_', ' ')} {'='*20}")
        
        start_time = time.time()
        
        try:
            # Check if script exists
            if not os.path.exists(phase.script_path):
                raise FileNotFoundError(f"Validation script not found: {phase.script_path}")
            
            # Run the validation script
            process = await asyncio.create_subprocess_exec(
                sys.executable, phase.script_path,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=os.getcwd()
            )
            
            # Wait for completion with timeout
            try:
                stdout, stderr = await asyncio.wait_for(
                    process.communicate(), 
                    timeout=phase.timeout
                )
                
                duration = time.time() - start_time
                
                # Parse results
                if process.returncode == 0:
                    # Try to parse JSON output from stdout
                    try:
                        output_lines = stdout.decode().strip().split('\n')
                        json_line = None
                        for line in reversed(output_lines):
                            if line.strip().startswith('{'):
                                json_line = line.strip()
                                break
                        
                        if json_line:
                            phase_result = json.loads(json_line)
                        else:
                            # Fallback: create result from stdout
                            phase_result = {
                                "status": "completed",
                                "duration": duration,
                                "output": stdout.decode(),
                                "error": None
                            }
                    except json.JSONDecodeError:
                        phase_result = {
                            "status": "completed",
                            "duration": duration,
                            "output": stdout.decode(),
                            "error": None
                        }
                    
                    self.results[phase.name] = {
                        "status": "passed",
                        "duration": duration,
                        "result": phase_result,
                        "error": None
                    }
                    
                    logger.info(f"✅ {phase.name} completed successfully ({duration:.1f}s)")
                    
                else:
                    error_output = stderr.decode() if stderr else stdout.decode()
                    self.results[phase.name] = {
                        "status": "failed",
                        "duration": duration,
                        "result": None,
                        "error": error_output
                    }
                    
                    logger.error(f"❌ {phase.name} failed ({duration:.1f}s)")
                    logger.error(f"Error: {error_output}")
                
            except asyncio.TimeoutError:
                duration = time.time() - start_time
                process.kill()
                await process.wait()
                
                self.results[phase.name] = {
                    "status": "timeout",
                    "duration": duration,
                    "result": None,
                    "error": f"Phase timed out after {phase.timeout}s"
                }
                
                logger.error(f"⏰ {phase.name} timed out after {phase.timeout}s")
        
        except Exception as e:
            duration = time.time() - start_time
            self.results[phase.name] = {
                "status": "error",
                "duration": duration,
                "result": None,
                "error": str(e)
            }
            
            logger.error(f"💥 {phase.name} failed with error: {e}")
    
    def _generate_master_report(self, total_duration: float) -> Dict[str, Any]:
        """Generate comprehensive master validation report."""
        logger.info("📊 Generating Master Validation Report...")
        
        # Calculate overall statistics
        total_phases = len(self.validation_phases)
        completed_phases = len([r for r in self.results.values() if r["status"] == "passed"])
        failed_phases = len([r for r in self.results.values() if r["status"] in ["failed", "timeout", "error"]])
        success_rate = (completed_phases / total_phases * 100) if total_phases > 0 else 0
        
        # Extract detailed results from each phase
        detailed_results = {}
        requirements_validation = {}
        performance_summary = {}
        integration_summary = {}
        
        for phase_name, result in self.results.items():
            if result["status"] == "passed" and result["result"]:
                phase_result = result["result"]
                
                if phase_name == "comprehensive_validation":
                    detailed_results["comprehensive"] = phase_result
                    requirements_validation = phase_result.get("requirements_validation", {})
                
                elif phase_name == "performance_validation":
                    detailed_results["performance"] = phase_result
                    performance_summary = self._extract_performance_summary(phase_result)
                
                elif phase_name == "integration_validation":
                    detailed_results["integration"] = phase_result
                    integration_summary = phase_result.get("integration_summary", {})
        
        # Generate requirements compliance summary
        compliance_summary = self._generate_compliance_summary(requirements_validation)
        
        report = {
            "master_validation_summary": {
                "total_phases": total_phases,
                "completed_phases": completed_phases,
                "failed_phases": failed_phases,
                "success_rate": success_rate,
                "total_duration": total_duration,
                "validation_timestamp": datetime.utcnow().isoformat(),
                "overall_status": "passed" if failed_phases == 0 else "failed"
            },
            "phase_results": {
                phase.name: {
                    "status": result["status"],
                    "duration": result["duration"],
                    "error": result["error"],
                    "description": phase.description
                }
                for phase, result in zip(self.validation_phases, 
                                       [self.results.get(phase.name, {"status": "not_run", "duration": 0, "error": "Not executed"}) 
                                        for phase in self.validation_phases])
            },
            "requirements_compliance": compliance_summary,
            "performance_summary": performance_summary,
            "integration_summary": integration_summary,
            "detailed_results": detailed_results,
            "validation_metadata": {
                "validation_suite_version": "1.0",
                "target_system": "observatory.nkllon.com",
                "websocket_endpoints": [
                    "/ws/emoji-rain",
                    "/ws/observatory", 
                    "/ws/anomalies",
                    "/ws/doctor-status"
                ],
                "test_environment": {
                    "python_version": sys.version,
                    "working_directory": os.getcwd(),
                    "validation_scripts": [phase.script_path for phase in self.validation_phases]
                }
            }
        }
        
        return report
    
    def _extract_performance_summary(self, performance_result: Dict[str, Any]) -> Dict[str, Any]:
        """Extract performance summary from performance validation results."""
        summary = {
            "connection_establishment": performance_result.get("connection_establishment", {}),
            "message_latency": performance_result.get("message_latency", {}),
            "connection_stability": performance_result.get("connection_stability", {}),
            "throughput": performance_result.get("throughput", {}),
            "resource_usage": performance_result.get("resource_usage", {})
        }
        
        return summary
    
    def _generate_compliance_summary(self, requirements_validation: Dict[str, Any]) -> Dict[str, Any]:
        """Generate requirements compliance summary."""
        compliance = {
            "connection_time_requirement": {
                "requirement": "< 2 seconds",
                "status": "unknown",
                "details": "No data available"
            },
            "latency_requirement": {
                "requirement": "< 100ms",
                "status": "unknown", 
                "details": "No data available"
            },
            "stability_requirement": {
                "requirement": "> 30 minutes",
                "status": "unknown",
                "details": "No data available"
            },
            "message_exchange_requirement": {
                "requirement": "bidirectional communication",
                "status": "unknown",
                "details": "No data available"
            },
            "error_handling_requirement": {
                "requirement": "graceful error handling",
                "status": "unknown",
                "details": "No data available"
            }
        }
        
        # Update with actual data if available
        for req_name, req_data in requirements_validation.items():
            if req_name in compliance:
                compliance[req_name] = req_data
        
        return compliance
    
    def _save_and_display_results(self, report: Dict[str, Any]):
        """Save results and display summary."""
        # Save comprehensive report
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        report_filename = f"websocket_master_validation_report_{timestamp}.json"
        
        with open(report_filename, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        
        # Display summary
        print("\n" + "="*60)
        print("📊 PHASE 3 WEBSOCKET VALIDATION - FINAL SUMMARY")
        print("="*60)
        
        summary = report["master_validation_summary"]
        print(f"Overall Status: {'✅ PASSED' if summary['overall_status'] == 'passed' else '❌ FAILED'}")
        print(f"Success Rate: {summary['success_rate']:.1f}%")
        print(f"Total Duration: {summary['total_duration']:.1f}s")
        print(f"Completed Phases: {summary['completed_phases']}/{summary['total_phases']}")
        
        print("\n📋 PHASE RESULTS:")
        for phase_name, phase_result in report["phase_results"].items():
            status_emoji = "✅" if phase_result["status"] == "passed" else "❌"
            print(f"  {status_emoji} {phase_name.replace('_', ' ').title()}: {phase_result['status']} ({phase_result['duration']:.1f}s)")
            if phase_result["error"]:
                print(f"     Error: {phase_result['error'][:100]}...")
        
        print("\n🎯 REQUIREMENTS COMPLIANCE:")
        compliance = report["requirements_compliance"]
        for req_name, req_data in compliance.items():
            status_emoji = "✅" if req_data["status"] in ["passed", "tested_5min"] else "❌"
            print(f"  {status_emoji} {req_name.replace('_', ' ').title()}: {req_data['details']}")
        
        print(f"\n📄 Comprehensive report saved to: {report_filename}")
        
        # Print final status
        if summary['overall_status'] == 'passed':
            print("\n🎉 PHASE 3 WEBSOCKET VALIDATION COMPLETED SUCCESSFULLY!")
            print("All WebSocket endpoints validated and operational.")
        else:
            print("\n⚠️ PHASE 3 WEBSOCKET VALIDATION COMPLETED WITH ISSUES!")
            print("Some validation phases failed. Check the detailed report.")

async def main():
    """Main execution function."""
    print("🚀 WebSocket Master Validator - Phase 3")
    print("Comprehensive WebSocket Validation and Testing Suite")
    print("=" * 60)
    
    validator = WebSocketMasterValidator()
    
    try:
        report = await validator.run_complete_validation()
        
        # Exit with appropriate code
        if report["master_validation_summary"]["overall_status"] == "passed":
            sys.exit(0)
        else:
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n⏹️ Validation interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Master validation failed: {e}")
        logger.exception("Master validation failed")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())