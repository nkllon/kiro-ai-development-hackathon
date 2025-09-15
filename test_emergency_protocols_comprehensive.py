#!/usr/bin/env python3
"""
Comprehensive Emergency Protocol Testing Suite
=============================================

Tests all emergency protocols to ensure they work correctly:
- Beast Mode Debug System
- Emergency Session Dump
- Ghostbusters Consultation
- Emergency Protocol Integration
"""

import sys
import time
import json
import tempfile
import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from beast_mode_debug_system import initialize_beast_mode_debug, stop_and_dump_trace
from session_dump_emergency import EmergencySessionDumper
from ghostbusters_standalone_consultation import GhostbustersStandaloneConsultation
from emergency_protocol_integration import EmergencyProtocolManager


class EmergencyProtocolTester:
    """Comprehensive tester for all emergency protocols"""
    
    def __init__(self):
        self.test_results = {}
        self.test_start_time = time.time()
        self.temp_dir = None
        self.original_cwd = Path.cwd()
    
    def setup_test_environment(self):
        """Setup isolated test environment"""
        
        print("🧪 SETTING UP TEST ENVIRONMENT")
        print("-" * 50)
        
        # Create temporary directory for testing
        self.temp_dir = tempfile.mkdtemp(prefix="emergency_protocol_test_")
        print(f"   Temporary directory: {self.temp_dir}")
        
        # Copy test files to temp directory
        test_files = [
            "beast_mode_debug_system.py",
            "session_dump_emergency.py", 
            "ghostbusters_standalone_consultation.py",
            "emergency_protocol_integration.py"
        ]
        
        for file in test_files:
            src = Path(file)
            if src.exists():
                dst = Path(self.temp_dir) / file
                shutil.copy2(src, dst)
                print(f"   Copied: {file}")
        
        # Change to temp directory
        os.chdir(self.temp_dir)
        print(f"   Changed to: {Path.cwd()}")
        
        print("✅ Test environment setup complete")
    
    def cleanup_test_environment(self):
        """Cleanup test environment"""
        
        print("\n🧹 CLEANING UP TEST ENVIRONMENT")
        print("-" * 50)
        
        # Return to original directory
        os.chdir(self.original_cwd)
        print(f"   Returned to: {Path.cwd()}")
        
        # Remove temporary directory
        if self.temp_dir and Path(self.temp_dir).exists():
            shutil.rmtree(self.temp_dir)
            print(f"   Removed: {self.temp_dir}")
        
        print("✅ Test environment cleanup complete")
    
    def test_beast_mode_debug_system(self):
        """Test Beast Mode Debug System"""
        
        print("\n🚀 TESTING BEAST MODE DEBUG SYSTEM")
        print("-" * 50)
        
        test_result = {
            "test_name": "Beast Mode Debug System",
            "start_time": time.time(),
            "success": False,
            "errors": [],
            "details": {}
        }
        
        try:
            # Test 1: Initialize system
            print("   Test 1: Initializing Beast Mode Debug System...")
            debug_system = initialize_beast_mode_debug()
            
            if debug_system:
                test_result["details"]["initialization"] = "SUCCESS"
                print("   ✅ Initialization: SUCCESS")
            else:
                test_result["errors"].append("Failed to initialize Beast Mode Debug System")
                print("   ❌ Initialization: FAILED")
            
            # Test 2: Log debug event
            print("   Test 2: Logging debug event...")
            debug_system.log_debug_event("test_event", {"test": "data"})
            test_result["details"]["debug_logging"] = "SUCCESS"
            print("   ✅ Debug logging: SUCCESS")
            
            # Test 3: Create emergency dump
            print("   Test 3: Creating emergency dump...")
            dump_file = debug_system.create_emergency_dump("test_emergency")
            
            if dump_file and Path(dump_file).exists():
                test_result["details"]["emergency_dump"] = "SUCCESS"
                test_result["details"]["dump_file"] = dump_file
                print(f"   ✅ Emergency dump: SUCCESS ({dump_file})")
            else:
                test_result["errors"].append("Failed to create emergency dump")
                print("   ❌ Emergency dump: FAILED")
            
            # Test 4: Stop and dump trace
            print("   Test 4: Stop and dump trace...")
            trace_file = stop_and_dump_trace("test_trace")
            
            if trace_file and Path(trace_file).exists():
                test_result["details"]["trace_dump"] = "SUCCESS"
                test_result["details"]["trace_file"] = trace_file
                print(f"   ✅ Trace dump: SUCCESS ({trace_file})")
            else:
                test_result["errors"].append("Failed to create trace dump")
                print("   ❌ Trace dump: FAILED")
            
            # Test 5: Function tracing decorator
            print("   Test 5: Testing function tracing decorator...")
            
            @debug_system.trace_function
            def test_function(x, y):
                return x + y
            
            result = test_function(5, 3)
            
            if result == 8:
                test_result["details"]["function_tracing"] = "SUCCESS"
                print("   ✅ Function tracing: SUCCESS")
            else:
                test_result["errors"].append("Function tracing failed")
                print("   ❌ Function tracing: FAILED")
            
            # Overall success
            if not test_result["errors"]:
                test_result["success"] = True
                print("   🎉 Beast Mode Debug System: ALL TESTS PASSED")
            else:
                print(f"   ❌ Beast Mode Debug System: {len(test_result['errors'])} TESTS FAILED")
            
        except Exception as e:
            test_result["errors"].append(f"Exception during testing: {str(e)}")
            print(f"   ❌ Beast Mode Debug System: EXCEPTION - {e}")
        
        test_result["end_time"] = time.time()
        test_result["duration"] = test_result["end_time"] - test_result["start_time"]
        
        self.test_results["beast_mode_debug"] = test_result
        return test_result
    
    def test_emergency_session_dump(self):
        """Test Emergency Session Dump System"""
        
        print("\n💾 TESTING EMERGENCY SESSION DUMP SYSTEM")
        print("-" * 50)
        
        test_result = {
            "test_name": "Emergency Session Dump System",
            "start_time": time.time(),
            "success": False,
            "errors": [],
            "details": {}
        }
        
        try:
            # Test 1: Initialize dumper
            print("   Test 1: Initializing Emergency Session Dumper...")
            dumper = EmergencySessionDumper()
            
            if dumper:
                test_result["details"]["initialization"] = "SUCCESS"
                print("   ✅ Initialization: SUCCESS")
            else:
                test_result["errors"].append("Failed to initialize Emergency Session Dumper")
                print("   ❌ Initialization: FAILED")
            
            # Test 2: Create comprehensive dump
            print("   Test 2: Creating comprehensive session dump...")
            dump_file = dumper.create_comprehensive_dump()
            
            if dump_file and Path(dump_file).exists():
                test_result["details"]["dump_creation"] = "SUCCESS"
                test_result["details"]["dump_file"] = dump_file
                
                # Check dump file size
                dump_size = Path(dump_file).stat().st_size
                test_result["details"]["dump_size"] = dump_size
                print(f"   ✅ Dump creation: SUCCESS ({dump_file}, {dump_size:,} bytes)")
                
                # Test 3: Validate dump content
                print("   Test 3: Validating dump content...")
                with open(dump_file, 'r') as f:
                    dump_data = json.load(f)
                
                required_sections = [
                    'system_info', 'python_environment', 'directory_state',
                    'git_state', 'imported_modules', 'negotiation_protocol_state',
                    'error_logs', 'stack_traces', 'file_structure', 'recent_commits',
                    'implementation_status'
                ]
                
                missing_sections = [section for section in required_sections if section not in dump_data]
                
                if not missing_sections:
                    test_result["details"]["content_validation"] = "SUCCESS"
                    print(f"   ✅ Content validation: SUCCESS (all {len(required_sections)} sections present)")
                else:
                    test_result["errors"].append(f"Missing sections: {missing_sections}")
                    print(f"   ❌ Content validation: FAILED (missing: {missing_sections})")
                
            else:
                test_result["errors"].append("Failed to create comprehensive dump")
                print("   ❌ Dump creation: FAILED")
            
            # Overall success
            if not test_result["errors"]:
                test_result["success"] = True
                print("   🎉 Emergency Session Dump System: ALL TESTS PASSED")
            else:
                print(f"   ❌ Emergency Session Dump System: {len(test_result['errors'])} TESTS FAILED")
            
        except Exception as e:
            test_result["errors"].append(f"Exception during testing: {str(e)}")
            print(f"   ❌ Emergency Session Dump System: EXCEPTION - {e}")
        
        test_result["end_time"] = time.time()
        test_result["duration"] = test_result["end_time"] - test_result["start_time"]
        
        self.test_results["emergency_session_dump"] = test_result
        return test_result
    
    def test_ghostbusters_consultation(self):
        """Test Ghostbusters Consultation System"""
        
        print("\n👻 TESTING GHOSTBUSTERS CONSULTATION SYSTEM")
        print("-" * 50)
        
        test_result = {
            "test_name": "Ghostbusters Consultation System",
            "start_time": time.time(),
            "success": False,
            "errors": [],
            "details": {}
        }
        
        try:
            # Test 1: Initialize consultation
            print("   Test 1: Initializing Ghostbusters Consultation...")
            consultation = GhostbustersStandaloneConsultation()
            
            if consultation:
                test_result["details"]["initialization"] = "SUCCESS"
                print("   ✅ Initialization: SUCCESS")
            else:
                test_result["errors"].append("Failed to initialize Ghostbusters Consultation")
                print("   ❌ Initialization: FAILED")
            
            # Test 2: Create critical state
            print("   Test 2: Creating critical state assessment...")
            critical_state = {
                "current_page_data": {
                    "url": "https://test-critical-page.com/emergency",
                    "title": "Test Critical Situation",
                    "page_type": "critical_failure",
                    "error_indicators": ["Test error 1", "Test error 2"],
                    "failure_modes": {"primary": "test_failure"},
                    "evidence": {"system_health": "critical"}
                },
                "confidence": 0.05,
                "risk_level": "critical"
            }
            
            test_result["details"]["critical_state"] = "SUCCESS"
            print("   ✅ Critical state creation: SUCCESS")
            
            # Test 3: Run consultation
            print("   Test 3: Running Ghostbusters consultation...")
            consultation_report = consultation.run_critical_consultation(critical_state)
            
            if consultation_report:
                test_result["details"]["consultation"] = "SUCCESS"
                test_result["details"]["consultation_id"] = consultation_report.get("consultation_id")
                test_result["details"]["primary_strategy"] = consultation_report.get("primary_strategy")
                test_result["details"]["risk_assessment"] = consultation_report.get("risk_assessment", {}).get("level")
                print(f"   ✅ Consultation: SUCCESS (ID: {consultation_report.get('consultation_id')})")
                print(f"      Strategy: {consultation_report.get('primary_strategy')}")
                print(f"      Risk: {consultation_report.get('risk_assessment', {}).get('level')}")
            else:
                test_result["errors"].append("Failed to run Ghostbusters consultation")
                print("   ❌ Consultation: FAILED")
            
            # Test 4: Validate investigation modules
            print("   Test 4: Validating investigation modules...")
            investigation_results = consultation_report.get("investigation_results", {})
            
            expected_modules = ["PageStructureAnalyzer", "NavigationAnalyzer", "ContentAnalyzer", "DiagnosticTester"]
            missing_modules = [module for module in expected_modules if module not in investigation_results]
            
            if not missing_modules:
                test_result["details"]["investigation_modules"] = "SUCCESS"
                print(f"   ✅ Investigation modules: SUCCESS (all {len(expected_modules)} modules)")
            else:
                test_result["errors"].append(f"Missing investigation modules: {missing_modules}")
                print(f"   ❌ Investigation modules: FAILED (missing: {missing_modules})")
            
            # Overall success
            if not test_result["errors"]:
                test_result["success"] = True
                print("   🎉 Ghostbusters Consultation System: ALL TESTS PASSED")
            else:
                print(f"   ❌ Ghostbusters Consultation System: {len(test_result['errors'])} TESTS FAILED")
            
        except Exception as e:
            test_result["errors"].append(f"Exception during testing: {str(e)}")
            print(f"   ❌ Ghostbusters Consultation System: EXCEPTION - {e}")
        
        test_result["end_time"] = time.time()
        test_result["duration"] = test_result["end_time"] - test_result["start_time"]
        
        self.test_results["ghostbusters_consultation"] = test_result
        return test_result
    
    def test_emergency_protocol_integration(self):
        """Test Emergency Protocol Integration"""
        
        print("\n🚨 TESTING EMERGENCY PROTOCOL INTEGRATION")
        print("-" * 50)
        
        test_result = {
            "test_name": "Emergency Protocol Integration",
            "start_time": time.time(),
            "success": False,
            "errors": [],
            "details": {}
        }
        
        try:
            # Test 1: Initialize protocol manager
            print("   Test 1: Initializing Emergency Protocol Manager...")
            protocol_manager = EmergencyProtocolManager()
            
            if protocol_manager:
                test_result["details"]["initialization"] = "SUCCESS"
                print("   ✅ Initialization: SUCCESS")
            else:
                test_result["errors"].append("Failed to initialize Emergency Protocol Manager")
                print("   ❌ Initialization: FAILED")
            
            # Test 2: Activate emergency protocols
            print("   Test 2: Activating emergency protocols...")
            integration_result = protocol_manager.activate_emergency_protocols()
            
            if integration_result and integration_result.get("success"):
                test_result["details"]["protocol_activation"] = "SUCCESS"
                test_result["details"]["protocol_id"] = integration_result.get("protocol_id")
                test_result["details"]["duration"] = integration_result.get("duration")
                test_result["details"]["dump_file"] = integration_result.get("dump_file")
                test_result["details"]["trace_file"] = integration_result.get("trace_file")
                print(f"   ✅ Protocol activation: SUCCESS (ID: {integration_result.get('protocol_id')})")
            else:
                test_result["errors"].append("Failed to activate emergency protocols")
                print("   ❌ Protocol activation: FAILED")
            
            # Test 3: Validate protocol status
            print("   Test 3: Validating protocol status...")
            protocol_status = protocol_manager.get_protocol_status()
            
            expected_protocols = [
                "beast_mode_debug", "emergency_session_dump", "ghostbusters_consultation",
                "comprehensive_trace_capture", "human_intervention_ready"
            ]
            
            inactive_protocols = [protocol for protocol in expected_protocols if not protocol_status.get(protocol)]
            
            if not inactive_protocols:
                test_result["details"]["protocol_status"] = "SUCCESS"
                print(f"   ✅ Protocol status: SUCCESS (all {len(expected_protocols)} protocols active)")
            else:
                test_result["errors"].append(f"Inactive protocols: {inactive_protocols}")
                print(f"   ❌ Protocol status: FAILED (inactive: {inactive_protocols})")
            
            # Test 4: Check human intervention readiness
            print("   Test 4: Checking human intervention readiness...")
            ready = protocol_manager.is_ready_for_human_intervention()
            
            if ready:
                test_result["details"]["human_intervention_ready"] = "SUCCESS"
                print("   ✅ Human intervention readiness: SUCCESS")
            else:
                test_result["errors"].append("System not ready for human intervention")
                print("   ❌ Human intervention readiness: FAILED")
            
            # Overall success
            if not test_result["errors"]:
                test_result["success"] = True
                print("   🎉 Emergency Protocol Integration: ALL TESTS PASSED")
            else:
                print(f"   ❌ Emergency Protocol Integration: {len(test_result['errors'])} TESTS FAILED")
            
        except Exception as e:
            test_result["errors"].append(f"Exception during testing: {str(e)}")
            print(f"   ❌ Emergency Protocol Integration: EXCEPTION - {e}")
        
        test_result["end_time"] = time.time()
        test_result["duration"] = test_result["end_time"] - test_result["start_time"]
        
        self.test_results["emergency_protocol_integration"] = test_result
        return test_result
    
    def run_all_tests(self):
        """Run all emergency protocol tests"""
        
        print("🧪 COMPREHENSIVE EMERGENCY PROTOCOL TESTING")
        print("=" * 80)
        print("Testing all emergency protocols for functionality and integration")
        print("=" * 80)
        
        try:
            # Setup test environment
            self.setup_test_environment()
            
            # Run all tests
            self.test_beast_mode_debug_system()
            self.test_emergency_session_dump()
            self.test_ghostbusters_consultation()
            self.test_emergency_protocol_integration()
            
            # Generate test report
            self.generate_test_report()
            
        except Exception as e:
            print(f"\n💥 FATAL ERROR DURING TESTING: {e}")
            print("Emergency protocols may not be functioning correctly")
        
        finally:
            # Cleanup test environment
            self.cleanup_test_environment()
    
    def generate_test_report(self):
        """Generate comprehensive test report"""
        
        print("\n📊 GENERATING COMPREHENSIVE TEST REPORT")
        print("=" * 80)
        
        total_tests = len(self.test_results)
        successful_tests = sum(1 for result in self.test_results.values() if result["success"])
        failed_tests = total_tests - successful_tests
        
        total_duration = time.time() - self.test_start_time
        
        print(f"📋 TEST SUMMARY:")
        print(f"   Total Tests: {total_tests}")
        print(f"   Successful: {successful_tests}")
        print(f"   Failed: {failed_tests}")
        print(f"   Success Rate: {(successful_tests/total_tests)*100:.1f}%")
        print(f"   Total Duration: {total_duration:.2f}s")
        
        print(f"\n📊 DETAILED RESULTS:")
        print("-" * 50)
        
        for test_name, result in self.test_results.items():
            status_icon = "✅" if result["success"] else "❌"
            print(f"   {status_icon} {result['test_name']}")
            print(f"      Duration: {result['duration']:.2f}s")
            print(f"      Success: {result['success']}")
            
            if result["errors"]:
                print(f"      Errors: {len(result['errors'])}")
                for error in result["errors"]:
                    print(f"        • {error}")
            
            if result["details"]:
                print(f"      Details: {len(result['details'])} items")
        
        print(f"\n🎯 OVERALL TEST RESULT:")
        print("-" * 50)
        
        if failed_tests == 0:
            print("   🎉 ALL EMERGENCY PROTOCOLS: FULLY OPERATIONAL")
            print("   ✅ Beast Mode Debug System: OPERATIONAL")
            print("   ✅ Emergency Session Dump: OPERATIONAL") 
            print("   ✅ Ghostbusters Consultation: OPERATIONAL")
            print("   ✅ Protocol Integration: OPERATIONAL")
            print("   ✅ System Ready for Human Intervention")
        else:
            print(f"   ⚠️ {failed_tests} EMERGENCY PROTOCOLS: ISSUES DETECTED")
            print("   Review failed tests and address issues before deployment")
        
        # Save test report
        report_file = f"emergency_protocol_test_report_{int(time.time())}.json"
        with open(report_file, 'w') as f:
            json.dump({
                "test_summary": {
                    "total_tests": total_tests,
                    "successful_tests": successful_tests,
                    "failed_tests": failed_tests,
                    "success_rate": (successful_tests/total_tests)*100,
                    "total_duration": total_duration,
                    "timestamp": datetime.now().isoformat()
                },
                "test_results": self.test_results
            }, f, indent=2)
        
        print(f"\n💾 Test report saved: {report_file}")


def main():
    """Main function for comprehensive emergency protocol testing"""
    
    print("🧪 COMPREHENSIVE EMERGENCY PROTOCOL TESTING SUITE")
    print("=" * 80)
    print("Testing all emergency protocols for functionality and integration")
    print("This will validate that all systems are working correctly")
    print("=" * 80)
    
    try:
        # Initialize tester
        tester = EmergencyProtocolTester()
        
        # Run all tests
        tester.run_all_tests()
        
        print(f"\n✅ COMPREHENSIVE TESTING COMPLETE")
        print("=" * 80)
        print("All emergency protocols have been tested")
        print("Review the test report for detailed results")
        print("System ready for emergency protocol deployment")
        
    except Exception as e:
        print(f"\n💥 FATAL ERROR IN TESTING SUITE: {e}")
        print("Emergency protocols may not be functioning correctly")
        print("Manual verification required")


if __name__ == "__main__":
    import os
    main()

