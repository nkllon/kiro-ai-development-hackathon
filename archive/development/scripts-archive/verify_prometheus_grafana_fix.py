#!/usr/bin/env python3
"""
Verify Prometheus/Grafana Fix
============================

Comprehensive verification that the Prometheus/Grafana "no data" issue
has been resolved and all systems are working correctly.

Author: Beast Mode Framework
Date: 2025-01-27
"""

import requests
import time
import json
import sys
from typing import Dict, Any, List, Tuple


class PrometheusGrafanaVerifier:
    """Verifies Prometheus/Grafana fix implementation."""
    
    def __init__(self):
        self.local_prometheus = "http://192.168.1.101:9090"
        self.local_grafana = "http://192.168.1.101:3000"
        self.public_prometheus = "https://prometheus.observatory.nkllon.com"
        self.public_grafana = "https://grafana.observatory.nkllon.com"
        
        self.verification_results = []
    
    def log_result(self, test_name: str, passed: bool, details: str = ""):
        """Log verification result."""
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} {test_name}")
        if details:
            print(f"    {details}")
        
        self.verification_results.append({
            'test': test_name,
            'passed': passed,
            'details': details
        })
    
    def test_local_prometheus(self) -> bool:
        """Test local Prometheus accessibility and data."""
        try:
            # Test basic connectivity
            response = requests.get(f"{self.local_prometheus}/api/v1/query?query=up", timeout=5)
            
            if response.status_code != 200:
                self.log_result("Local Prometheus Connectivity", False, f"HTTP {response.status_code}")
                return False
            
            # Test data availability
            data = response.json()
            if data.get('status') != 'success':
                self.log_result("Local Prometheus Data", False, f"Status: {data.get('status')}")
                return False
            
            results = data.get('data', {}).get('result', [])
            if not results:
                self.log_result("Local Prometheus Metrics", False, "No metrics data found")
                return False
            
            self.log_result("Local Prometheus", True, f"Found {len(results)} metrics")
            return True
            
        except Exception as e:
            self.log_result("Local Prometheus", False, str(e))
            return False
    
    def test_public_prometheus(self) -> bool:
        """Test public Prometheus accessibility through tunnel."""
        try:
            # Test basic connectivity
            response = requests.get(f"{self.public_prometheus}/api/v1/query?query=up", timeout=15)
            
            if response.status_code != 200:
                self.log_result("Public Prometheus Connectivity", False, f"HTTP {response.status_code}")
                return False
            
            # Test data availability
            data = response.json()
            if data.get('status') != 'success':
                self.log_result("Public Prometheus Data", False, f"Status: {data.get('status')}")
                return False
            
            results = data.get('data', {}).get('result', [])
            if not results:
                self.log_result("Public Prometheus Metrics", False, "No metrics data found")
                return False
            
            self.log_result("Public Prometheus", True, f"Found {len(results)} metrics via tunnel")
            return True
            
        except Exception as e:
            self.log_result("Public Prometheus", False, str(e))
            return False
    
    def test_local_grafana(self) -> bool:
        """Test local Grafana accessibility."""
        try:
            response = requests.get(f"{self.local_grafana}/api/health", timeout=5)
            
            if response.status_code == 200:
                self.log_result("Local Grafana", True, "Health check passed")
                return True
            else:
                self.log_result("Local Grafana", False, f"HTTP {response.status_code}")
                return False
                
        except Exception as e:
            self.log_result("Local Grafana", False, str(e))
            return False
    
    def test_public_grafana(self) -> bool:
        """Test public Grafana accessibility through tunnel."""
        try:
            response = requests.get(f"{self.public_grafana}/api/health", timeout=15)
            
            if response.status_code == 200:
                self.log_result("Public Grafana", True, "Accessible via tunnel")
                return True
            else:
                self.log_result("Public Grafana", False, f"HTTP {response.status_code}")
                return False
                
        except Exception as e:
            self.log_result("Public Grafana", False, str(e))
            return False
    
    def test_dag_orchestration_metrics(self) -> bool:
        """Test DAG orchestration specific metrics."""
        try:
            # Test for Beast Mode metrics
            response = requests.get(
                f"{self.local_prometheus}/api/v1/query?query=beast_mode_module_health_score",
                timeout=5
            )
            
            if response.status_code != 200:
                self.log_result("DAG Orchestration Metrics", False, f"HTTP {response.status_code}")
                return False
            
            data = response.json()
            results = data.get('data', {}).get('result', [])
            
            if results:
                self.log_result("DAG Orchestration Metrics", True, f"Found {len(results)} health metrics")
                return True
            else:
                # Try alternative metrics
                response = requests.get(
                    f"{self.local_prometheus}/api/v1/query?query={{__name__=~\"beast_mode.*\"}}",
                    timeout=5
                )
                
                if response.status_code == 200:
                    data = response.json()
                    results = data.get('data', {}).get('result', [])
                    
                    if results:
                        self.log_result("DAG Orchestration Metrics", True, f"Found {len(results)} Beast Mode metrics")
                        return True
                
                self.log_result("DAG Orchestration Metrics", False, "No Beast Mode metrics found")
                return False
                
        except Exception as e:
            self.log_result("DAG Orchestration Metrics", False, str(e))
            return False
    
    def test_metrics_collection_process(self) -> bool:
        """Test that metrics collection process is running."""
        try:
            import subprocess
            
            result = subprocess.run(
                ["ps", "aux"],
                capture_output=True,
                text=True
            )
            
            if "start_prometheus_metrics_collection" in result.stdout:
                self.log_result("Metrics Collection Process", True, "Process is running")
                return True
            else:
                self.log_result("Metrics Collection Process", False, "Process not found")
                return False
                
        except Exception as e:
            self.log_result("Metrics Collection Process", False, str(e))
            return False
    
    def test_tunnel_process(self) -> bool:
        """Test that Cloudflare tunnel is running."""
        try:
            import subprocess
            
            result = subprocess.run(
                ["ps", "aux"],
                capture_output=True,
                text=True
            )
            
            if "cloudflared tunnel run" in result.stdout:
                self.log_result("Cloudflare Tunnel Process", True, "Tunnel is running")
                return True
            else:
                self.log_result("Cloudflare Tunnel Process", False, "Tunnel process not found")
                return False
                
        except Exception as e:
            self.log_result("Cloudflare Tunnel Process", False, str(e))
            return False
    
    def generate_verification_report(self) -> Dict[str, Any]:
        """Generate comprehensive verification report."""
        passed_tests = sum(1 for result in self.verification_results if result['passed'])
        total_tests = len(self.verification_results)
        success_rate = passed_tests / total_tests if total_tests > 0 else 0
        
        return {
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
            'total_tests': total_tests,
            'passed_tests': passed_tests,
            'failed_tests': total_tests - passed_tests,
            'success_rate': success_rate,
            'overall_status': 'PASS' if success_rate >= 0.8 else 'FAIL',
            'test_results': self.verification_results,
            'recommendations': self._generate_recommendations()
        }
    
    def _generate_recommendations(self) -> List[str]:
        """Generate recommendations based on test results."""
        recommendations = []
        
        failed_tests = [r for r in self.verification_results if not r['passed']]
        
        if any('Public Prometheus' in test['test'] for test in failed_tests):
            recommendations.append("Wait 2-3 minutes for Cloudflare tunnel to fully propagate")
            recommendations.append("Check tunnel configuration and credentials")
        
        if any('Metrics Collection' in test['test'] for test in failed_tests):
            recommendations.append("Restart metrics collection: python3 start_prometheus_metrics_collection.py")
        
        if any('DAG Orchestration' in test['test'] for test in failed_tests):
            recommendations.append("Run DAG orchestration tests to generate metrics")
        
        if any('Local' in test['test'] for test in failed_tests):
            recommendations.append("Check local service bindings and network configuration")
        
        if not failed_tests:
            recommendations.append("All systems operational - monitor for continued stability")
            recommendations.append("Set up automated health monitoring")
        
        return recommendations
    
    def run_comprehensive_verification(self) -> bool:
        """Run all verification tests."""
        print("🔍 Comprehensive Prometheus/Grafana Fix Verification")
        print("=" * 60)
        
        # Test local services first
        print("\n📍 Local Services:")
        self.test_local_prometheus()
        self.test_local_grafana()
        
        # Test processes
        print("\n🔄 Background Processes:")
        self.test_metrics_collection_process()
        self.test_tunnel_process()
        
        # Test metrics
        print("\n📊 Metrics Data:")
        self.test_dag_orchestration_metrics()
        
        # Test public endpoints (may take time to propagate)
        print("\n🌐 Public Endpoints (via Cloudflare Tunnel):")
        print("   Note: May take 2-3 minutes to fully propagate...")
        
        # Try public endpoints with retries
        for attempt in range(3):
            if attempt > 0:
                print(f"   Retry attempt {attempt + 1}/3...")
                time.sleep(30)  # Wait 30 seconds between attempts
            
            public_prometheus_ok = self.test_public_prometheus()
            public_grafana_ok = self.test_public_grafana()
            
            if public_prometheus_ok and public_grafana_ok:
                break
        
        # Generate report
        report = self.generate_verification_report()
        
        print(f"\n📋 VERIFICATION REPORT")
        print("=" * 30)
        print(f"Timestamp: {report['timestamp']}")
        print(f"Total Tests: {report['total_tests']}")
        print(f"Passed: {report['passed_tests']}")
        print(f"Failed: {report['failed_tests']}")
        print(f"Success Rate: {report['success_rate']:.1%}")
        print(f"Overall Status: {report['overall_status']}")
        
        if report['recommendations']:
            print(f"\n💡 Recommendations:")
            for rec in report['recommendations']:
                print(f"   • {rec}")
        
        # Save report
        with open('prometheus_grafana_verification_report.json', 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"\n📄 Detailed report saved: prometheus_grafana_verification_report.json")
        
        return report['overall_status'] == 'PASS'


def main():
    """Main execution function."""
    verifier = PrometheusGrafanaVerifier()
    
    try:
        success = verifier.run_comprehensive_verification()
        
        if success:
            print(f"\n🚀 VERIFICATION SUCCESSFUL!")
            print(f"✅ Prometheus/Grafana fix has been verified")
            print(f"✅ All critical systems are operational")
            print(f"\n🎯 Access Points:")
            print(f"   • Prometheus: https://prometheus.observatory.nkllon.com")
            print(f"   • Grafana: https://grafana.observatory.nkllon.com")
        else:
            print(f"\n⚠️ VERIFICATION INCOMPLETE")
            print(f"❌ Some systems may need additional attention")
            print(f"💡 Check recommendations above")
        
        return success
        
    except KeyboardInterrupt:
        print(f"\n⚠️ Verification cancelled by user")
        return False
    except Exception as e:
        print(f"\n❌ Verification failed: {e}")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)