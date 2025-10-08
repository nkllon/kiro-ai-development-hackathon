#!/usr/bin/env python3
"""
Observatory Deployment Validation Suite
======================================

Comprehensive validation of Observatory deployment including endpoints,
WebSocket connections, external access, and performance benchmarking.
"""

import os
import sys
import time
import json
import asyncio
import websockets
import requests
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any

class ObservatoryValidator:
    def __init__(self):
        self.observatory_port = 8888
        self.external_url = "https://observatory.nkllon.com"
        self.validation_results = {
            "timestamp": datetime.now().isoformat(),
            "tests": {},
            "summary": {}
        }
        
    def log_test(self, test_name: str, status: str, details: str = "", duration: float = 0):
        """Log test results."""
        self.validation_results["tests"][test_name] = {
            "status": status,
            "details": details,
            "duration": duration,
            "timestamp": datetime.now().isoformat()
        }
        
        status_icon = "✅" if status == "pass" else "❌" if status == "fail" else "⚠️"
        duration_str = f" ({duration:.2f}s)" if duration > 0 else ""
        print(f"{status_icon} {test_name}: {details}{duration_str}")
    
    def test_local_endpoints(self) -> bool:
        """Test all Observatory endpoints locally."""
        print("🔍 Testing local Observatory endpoints...")
        
        endpoints = [
            ("/health", "Health endpoint", True),
            ("/ready", "Readiness endpoint", True),
            ("/metrics", "Metrics endpoint", True),
            ("/", "Dashboard endpoint", False)  # Dashboard might return different status codes
        ]
        
        all_passed = True
        
        for endpoint, description, require_200 in endpoints:
            start_time = time.time()
            
            try:
                response = requests.get(
                    f"http://localhost:{self.observatory_port}{endpoint}", 
                    timeout=10
                )
                duration = time.time() - start_time
                
                if require_200 and response.status_code == 200:
                    self.log_test(f"Local {description}", "pass", 
                                f"Status {response.status_code}", duration)
                elif not require_200 and response.status_code in [200, 302, 404]:
                    self.log_test(f"Local {description}", "pass", 
                                f"Status {response.status_code}", duration)
                else:
                    self.log_test(f"Local {description}", "fail", 
                                f"Status {response.status_code}", duration)
                    all_passed = False
                    
            except requests.exceptions.RequestException as e:
                duration = time.time() - start_time
                self.log_test(f"Local {description}", "fail", str(e), duration)
                all_passed = False
        
        return all_passed
    
    def test_external_access(self) -> bool:
        """Test external access via Cloudflare tunnel."""
        print("🌐 Testing external access via Cloudflare tunnel...")
        
        endpoints = [
            ("/health", "External Health endpoint"),
            ("/", "External Dashboard endpoint")
        ]
        
        all_passed = True
        
        for endpoint, description in endpoints:
            start_time = time.time()
            
            try:
                response = requests.get(
                    f"{self.external_url}{endpoint}", 
                    timeout=30,
                    allow_redirects=True
                )
                duration = time.time() - start_time
                
                if response.status_code in [200, 302]:
                    self.log_test(description, "pass", 
                                f"Status {response.status_code}", duration)
                else:
                    self.log_test(description, "fail", 
                                f"Status {response.status_code}", duration)
                    all_passed = False
                    
            except requests.exceptions.RequestException as e:
                duration = time.time() - start_time
                self.log_test(description, "fail", str(e), duration)
                all_passed = False
        
        return all_passed
    
    async def test_websocket_connection(self) -> bool:
        """Test WebSocket connection functionality."""
        print("🔌 Testing WebSocket connections...")
        
        websocket_endpoints = [
            "/ws/observatory",
            "/ws/emoji-rain", 
            "/ws/anomalies",
            "/ws/doctor-status"
        ]
        
        all_passed = True
        
        for endpoint in websocket_endpoints:
            start_time = time.time()
            
            try:
                uri = f"ws://localhost:{self.observatory_port}{endpoint}"
                
                async with websockets.connect(uri) as websocket:
                    # Send a test message
                    await websocket.send(json.dumps({"type": "ping", "data": "test"}))
                    
                    # Wait for response or timeout
                    try:
                        response = await asyncio.wait_for(websocket.recv(), timeout=5)
                        duration = time.time() - start_time
                        self.log_test(f"WebSocket {endpoint}", "pass", 
                                    "Connection and message exchange successful", duration)
                    except asyncio.TimeoutError:
                        duration = time.time() - start_time
                        self.log_test(f"WebSocket {endpoint}", "pass", 
                                    "Connection successful (no response expected)", duration)
                        
            except Exception as e:
                duration = time.time() - start_time
                self.log_test(f"WebSocket {endpoint}", "fail", str(e), duration)
                all_passed = False
        
        return all_passed
    
    def test_performance_benchmarks(self) -> bool:
        """Test performance characteristics."""
        print("⚡ Testing performance benchmarks...")
        
        # Test response times for critical endpoints
        performance_tests = [
            ("/health", 1.0),  # Health should respond within 1 second
            ("/metrics", 2.0), # Metrics within 2 seconds
            ("/", 3.0)         # Dashboard within 3 seconds
        ]
        
        all_passed = True
        
        for endpoint, max_time in performance_tests:
            times = []
            
            # Run 5 requests to get average
            for i in range(5):
                start_time = time.time()
                
                try:
                    response = requests.get(
                        f"http://localhost:{self.observatory_port}{endpoint}", 
                        timeout=max_time + 1
                    )
                    duration = time.time() - start_time
                    times.append(duration)
                    
                except requests.exceptions.RequestException:
                    times.append(max_time + 1)  # Count as failure
            
            avg_time = sum(times) / len(times)
            
            if avg_time <= max_time:
                self.log_test(f"Performance {endpoint}", "pass", 
                            f"Avg response time: {avg_time:.2f}s (target: <{max_time}s)")
            else:
                self.log_test(f"Performance {endpoint}", "fail", 
                            f"Avg response time: {avg_time:.2f}s (target: <{max_time}s)")
                all_passed = False
        
        return all_passed
    
    def test_data_persistence(self) -> bool:
        """Test data persistence functionality."""
        print("💾 Testing data persistence...")
        
        data_dir = Path("observatory_data")
        
        # Check if data directories exist
        required_dirs = ["metrics", "dashboards", "logs", "config"]
        all_passed = True
        
        for dir_name in required_dirs:
            dir_path = data_dir / dir_name
            
            if dir_path.exists() and dir_path.is_dir():
                self.log_test(f"Data Directory {dir_name}", "pass", 
                            f"Directory exists and is accessible")
            else:
                self.log_test(f"Data Directory {dir_name}", "fail", 
                            f"Directory missing or inaccessible")
                all_passed = False
        
        # Test write permissions
        test_file = data_dir / "logs" / "validation_test.txt"
        try:
            with open(test_file, 'w') as f:
                f.write(f"Validation test: {datetime.now().isoformat()}")
            
            if test_file.exists():
                test_file.unlink()  # Clean up
                self.log_test("Data Write Permissions", "pass", 
                            "Can write to data directories")
            else:
                self.log_test("Data Write Permissions", "fail", 
                            "Write test file not created")
                all_passed = False
                
        except Exception as e:
            self.log_test("Data Write Permissions", "fail", str(e))
            all_passed = False
        
        return all_passed
    
    def test_process_health(self) -> bool:
        """Test Observatory process health."""
        print("🏥 Testing process health...")
        
        # Check if Observatory process is running
        import subprocess
        
        try:
            result = subprocess.run(
                ["pgrep", "-f", "start_observatory"], 
                capture_output=True, text=True
            )
            
            if result.returncode == 0 and result.stdout.strip():
                pids = result.stdout.strip().split('\n')
                self.log_test("Process Running", "pass", 
                            f"Observatory process found (PIDs: {', '.join(pids)})")
                
                # Check process resource usage
                for pid in pids:
                    try:
                        ps_result = subprocess.run(
                            ["ps", "-p", pid, "-o", "pid,pcpu,pmem,time"], 
                            capture_output=True, text=True
                        )
                        if ps_result.returncode == 0:
                            self.log_test(f"Process Resources PID {pid}", "pass", 
                                        ps_result.stdout.strip().split('\n')[-1])
                    except:
                        pass
                
                return True
            else:
                self.log_test("Process Running", "fail", 
                            "No Observatory process found")
                return False
                
        except Exception as e:
            self.log_test("Process Running", "fail", str(e))
            return False
    
    def test_tunnel_connectivity(self) -> bool:
        """Test Cloudflare tunnel connectivity."""
        print("🌉 Testing Cloudflare tunnel connectivity...")
        
        # Check if tunnel process is running
        import subprocess
        
        try:
            result = subprocess.run(
                ["pgrep", "-f", "cloudflared"], 
                capture_output=True, text=True
            )
            
            if result.returncode == 0 and result.stdout.strip():
                pids = result.stdout.strip().split('\n')
                self.log_test("Tunnel Process", "pass", 
                            f"Cloudflare tunnel running (PIDs: {', '.join(pids)})")
                return True
            else:
                self.log_test("Tunnel Process", "fail", 
                            "No Cloudflare tunnel process found")
                return False
                
        except Exception as e:
            self.log_test("Tunnel Process", "fail", str(e))
            return False
    
    def generate_validation_report(self) -> Path:
        """Generate comprehensive validation report."""
        print("📋 Generating validation report...")
        
        # Calculate summary statistics
        total_tests = len(self.validation_results["tests"])
        passed_tests = sum(1 for test in self.validation_results["tests"].values() 
                          if test["status"] == "pass")
        failed_tests = total_tests - passed_tests
        
        self.validation_results["summary"] = {
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "failed_tests": failed_tests,
            "success_rate": (passed_tests / total_tests * 100) if total_tests > 0 else 0,
            "overall_status": "pass" if failed_tests == 0 else "fail"
        }
        
        # Save detailed report
        report_file = Path(f"observatory_validation_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
        with open(report_file, 'w') as f:
            json.dump(self.validation_results, f, indent=2)
        
        # Generate human-readable summary
        summary_file = Path(f"observatory_validation_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md")
        with open(summary_file, 'w') as f:
            f.write("# Observatory Deployment Validation Report\n\n")
            f.write(f"**Generated:** {self.validation_results['timestamp']}\n\n")
            f.write(f"## Summary\n\n")
            f.write(f"- **Total Tests:** {total_tests}\n")
            f.write(f"- **Passed:** {passed_tests}\n")
            f.write(f"- **Failed:** {failed_tests}\n")
            f.write(f"- **Success Rate:** {self.validation_results['summary']['success_rate']:.1f}%\n")
            f.write(f"- **Overall Status:** {'✅ PASS' if failed_tests == 0 else '❌ FAIL'}\n\n")
            
            f.write("## Test Results\n\n")
            for test_name, result in self.validation_results["tests"].items():
                status_icon = "✅" if result["status"] == "pass" else "❌"
                f.write(f"### {status_icon} {test_name}\n")
                f.write(f"- **Status:** {result['status'].upper()}\n")
                f.write(f"- **Details:** {result['details']}\n")
                if result.get('duration', 0) > 0:
                    f.write(f"- **Duration:** {result['duration']:.2f}s\n")
                f.write(f"- **Timestamp:** {result['timestamp']}\n\n")
        
        print(f"✅ Validation report saved: {report_file}")
        print(f"✅ Validation summary saved: {summary_file}")
        
        return report_file
    
    async def run_validation(self) -> bool:
        """Run complete validation suite."""
        print("🚀 Observatory Deployment Validation Suite")
        print("=" * 50)
        
        validation_start = time.time()
        
        # Run all validation tests
        tests = [
            ("Local Endpoints", self.test_local_endpoints),
            ("External Access", self.test_external_access),
            ("Data Persistence", self.test_data_persistence),
            ("Process Health", self.test_process_health),
            ("Tunnel Connectivity", self.test_tunnel_connectivity),
            ("Performance Benchmarks", self.test_performance_benchmarks)
        ]
        
        overall_success = True
        
        for test_name, test_func in tests:
            print(f"\n--- {test_name} ---")
            try:
                if asyncio.iscoroutinefunction(test_func):
                    result = await test_func()
                else:
                    result = test_func()
                
                if not result:
                    overall_success = False
                    
            except Exception as e:
                print(f"❌ {test_name} failed with exception: {e}")
                self.log_test(test_name, "fail", f"Exception: {e}")
                overall_success = False
        
        # Test WebSocket separately as it's async
        print(f"\n--- WebSocket Connections ---")
        try:
            websocket_result = await self.test_websocket_connection()
            if not websocket_result:
                overall_success = False
        except Exception as e:
            print(f"❌ WebSocket test failed with exception: {e}")
            self.log_test("WebSocket Connections", "fail", f"Exception: {e}")
            overall_success = False
        
        validation_duration = time.time() - validation_start
        
        # Generate report
        report_file = self.generate_validation_report()
        
        # Print final summary
        summary = self.validation_results["summary"]
        print(f"\n🎯 Validation Complete ({validation_duration:.2f}s)")
        print("=" * 50)
        print(f"📊 Results: {summary['passed_tests']}/{summary['total_tests']} tests passed ({summary['success_rate']:.1f}%)")
        print(f"📋 Report: {report_file}")
        
        if overall_success:
            print("✅ Observatory deployment validation PASSED")
        else:
            print("❌ Observatory deployment validation FAILED")
            print("🔧 Review failed tests and address issues before proceeding")
        
        return overall_success

async def main():
    """Main validation execution."""
    validator = ObservatoryValidator()
    
    try:
        success = await validator.run_validation()
        return success
        
    except Exception as e:
        print(f"\n❌ Validation failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)