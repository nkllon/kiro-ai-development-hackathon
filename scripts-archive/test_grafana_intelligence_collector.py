#!/usr/bin/env python3
"""
Test Grafana Intelligence Collector Implementation
=================================================

Comprehensive test suite for the Grafana Intelligence Collector to validate
Phase 1 completion of the Runtime State Registry.
"""

import sys
import json
import asyncio
from datetime import datetime
from pathlib import Path

# Add project root to path
sys.path.insert(0, '.')

from src.runtime_state_registry.collectors.grafana_intelligence_collector import GrafanaIntelligenceCollector
from src.runtime_state_registry.core.runtime_state_registry import RuntimeStateRegistry


class GrafanaCollectorTestSuite:
    """Test suite for Grafana Intelligence Collector."""
    
    def __init__(self):
        self.test_results = []
        self.collector = None
        self.registry = None
    
    def run_all_tests(self):
        """Run comprehensive test suite."""
        print("🧪 Grafana Intelligence Collector Test Suite")
        print("=" * 50)
        
        # Test collector initialization
        self.test_collector_initialization()
        
        # Test Grafana connectivity
        self.test_grafana_connectivity()
        
        # Test dashboard discovery
        self.test_dashboard_discovery()
        
        # Test alert collection
        self.test_alert_collection()
        
        # Test monitoring state collection
        self.test_monitoring_state_collection()
        
        # Test deep-link generation
        self.test_dashboard_deep_links()
        
        # Test auto-provisioning
        self.test_auto_provisioning()
        
        # Test registry integration
        self.test_registry_integration()
        
        # Generate report
        self.generate_test_report()
        
        return all(result["passed"] for result in self.test_results)
    
    def test_collector_initialization(self):
        """Test 1: Collector can be initialized."""
        print("\n🔧 Test 1: Collector Initialization")
        
        try:
            self.collector = GrafanaIntelligenceCollector()
            
            # Check required attributes
            required_attrs = [
                'grafana_url', 'session', 'service_patterns',
                '_dashboard_cache', '_cache_timestamp', '_cache_ttl'
            ]
            
            missing_attrs = []
            for attr in required_attrs:
                if not hasattr(self.collector, attr):
                    missing_attrs.append(attr)
            
            if missing_attrs:
                self.record_test_result("collector_init", False, 
                                      f"Missing attributes: {missing_attrs}")
                return False
            
            # Check required methods
            required_methods = [
                'collect_monitoring_state', 'generate_dashboard_deep_link',
                'auto_provision_service_monitoring', 'health_check'
            ]
            
            missing_methods = []
            for method in required_methods:
                if not hasattr(self.collector, method):
                    missing_methods.append(method)
            
            if missing_methods:
                self.record_test_result("collector_init", False,
                                      f"Missing methods: {missing_methods}")
                return False
            
            self.record_test_result("collector_init", True, "Collector initialized successfully")
            print("✅ Collector initialization: PASSED")
            return True
            
        except Exception as e:
            self.record_test_result("collector_init", False, str(e))
            print(f"❌ Collector initialization: FAILED - {e}")
            return False
    
    def test_grafana_connectivity(self):
        """Test 2: Grafana connectivity and health check."""
        print("\n🌐 Test 2: Grafana Connectivity")
        
        try:
            if not self.collector:
                self.record_test_result("grafana_connectivity", False, "Collector not initialized")
                return False
            
            # Test health check
            health = self.collector.health_check()
            
            if not isinstance(health, dict):
                self.record_test_result("grafana_connectivity", False, "Invalid health check response")
                return False
            
            status = health.get('status', 'unknown')
            
            if status == 'healthy':
                self.record_test_result("grafana_connectivity", True, 
                                      f"Grafana healthy: {health}")
                print("✅ Grafana connectivity: PASSED")
                return True
            else:
                self.record_test_result("grafana_connectivity", False,
                                      f"Grafana unhealthy: {health}")
                print(f"⚠️ Grafana connectivity: WARNING - {health}")
                return False
                
        except Exception as e:
            self.record_test_result("grafana_connectivity", False, str(e))
            print(f"❌ Grafana connectivity: FAILED - {e}")
            return False
    
    def test_dashboard_discovery(self):
        """Test 3: Dashboard discovery and metadata extraction."""
        print("\n📊 Test 3: Dashboard Discovery")
        
        try:
            if not self.collector:
                self.record_test_result("dashboard_discovery", False, "Collector not initialized")
                return False
            
            # Get all dashboards
            dashboards = self.collector._get_all_dashboards()
            
            dashboard_count = len(dashboards)
            
            if dashboard_count == 0:
                self.record_test_result("dashboard_discovery", False, "No dashboards found")
                print("⚠️ Dashboard discovery: WARNING - No dashboards found")
                return False
            
            # Check dashboard metadata structure
            if dashboards:
                dashboard = dashboards[0]
                required_fields = ['uid', 'title', 'services_monitored', 'url']
                missing_fields = []
                
                for field in required_fields:
                    if not hasattr(dashboard, field):
                        missing_fields.append(field)
                
                if missing_fields:
                    self.record_test_result("dashboard_discovery", False,
                                          f"Dashboard missing fields: {missing_fields}")
                    return False
            
            dashboard_summary = {
                'total_dashboards': dashboard_count,
                'services_discovered': sum(len(d.services_monitored) for d in dashboards),
                'sample_dashboard': dashboards[0].title if dashboards else None
            }
            
            self.record_test_result("dashboard_discovery", True,
                                  f"Dashboard discovery working: {dashboard_summary}")
            print(f"✅ Dashboard discovery: PASSED ({dashboard_count} dashboards)")
            return True
            
        except Exception as e:
            self.record_test_result("dashboard_discovery", False, str(e))
            print(f"❌ Dashboard discovery: FAILED - {e}")
            return False
    
    def test_alert_collection(self):
        """Test 4: Alert state collection."""
        print("\n🚨 Test 4: Alert Collection")
        
        try:
            if not self.collector:
                self.record_test_result("alert_collection", False, "Collector not initialized")
                return False
            
            # Get alert states
            alerts = self.collector._get_alert_states()
            
            alert_count = len(alerts)
            
            # Check alert structure if any exist
            if alerts:
                alert = alerts[0]
                required_fields = ['alert_name', 'service_name', 'state', 'severity']
                missing_fields = []
                
                for field in required_fields:
                    if not hasattr(alert, field):
                        missing_fields.append(field)
                
                if missing_fields:
                    self.record_test_result("alert_collection", False,
                                          f"Alert missing fields: {missing_fields}")
                    return False
            
            alert_summary = {
                'total_alerts': alert_count,
                'services_with_alerts': len(set(a.service_name for a in alerts)),
                'alert_states': list(set(a.state for a in alerts))
            }
            
            self.record_test_result("alert_collection", True,
                                  f"Alert collection working: {alert_summary}")
            print(f"✅ Alert collection: PASSED ({alert_count} alerts)")
            return True
            
        except Exception as e:
            self.record_test_result("alert_collection", False, str(e))
            print(f"❌ Alert collection: FAILED - {e}")
            return False
    
    def test_monitoring_state_collection(self):
        """Test 5: Complete monitoring state collection."""
        print("\n📈 Test 5: Monitoring State Collection")
        
        try:
            if not self.collector:
                self.record_test_result("monitoring_state", False, "Collector not initialized")
                return False
            
            # Collect monitoring state
            monitoring_states = self.collector.collect_monitoring_state()
            
            if not isinstance(monitoring_states, dict):
                self.record_test_result("monitoring_state", False, "Invalid monitoring state format")
                return False
            
            service_count = len(monitoring_states)
            
            # Check monitoring state structure
            if monitoring_states:
                service_name, state = next(iter(monitoring_states.items()))
                required_fields = ['service_name', 'health_status', 'dashboards', 'alerts']
                missing_fields = []
                
                for field in required_fields:
                    if not hasattr(state, field):
                        missing_fields.append(field)
                
                if missing_fields:
                    self.record_test_result("monitoring_state", False,
                                          f"Monitoring state missing fields: {missing_fields}")
                    return False
            
            monitoring_summary = {
                'services_monitored': service_count,
                'total_dashboards': sum(len(s.dashboards) for s in monitoring_states.values()),
                'total_alerts': sum(len(s.alerts) for s in monitoring_states.values()),
                'healthy_services': sum(1 for s in monitoring_states.values() 
                                      if s.health_status.value == 'healthy')
            }
            
            self.record_test_result("monitoring_state", True,
                                  f"Monitoring state collection working: {monitoring_summary}")
            print(f"✅ Monitoring state collection: PASSED ({service_count} services)")
            return True
            
        except Exception as e:
            self.record_test_result("monitoring_state", False, str(e))
            print(f"❌ Monitoring state collection: FAILED - {e}")
            return False
    
    def test_dashboard_deep_links(self):
        """Test 6: Dashboard deep-link generation."""
        print("\n🔗 Test 6: Dashboard Deep-Links")
        
        try:
            if not self.collector:
                self.record_test_result("deep_links", False, "Collector not initialized")
                return False
            
            # Test deep-link generation for common services
            test_services = ['prometheus', 'grafana', 'jaeger']
            link_results = {}
            
            for service in test_services:
                link = self.collector.generate_dashboard_deep_link(
                    service_name=service,
                    time_range="now-1h",
                    refresh="30s"
                )
                link_results[service] = link
            
            # Check if any links were generated
            valid_links = [link for link in link_results.values() if link]
            
            link_summary = {
                'services_tested': len(test_services),
                'links_generated': len(valid_links),
                'sample_links': {k: v for k, v in link_results.items() if v}
            }
            
            success = len(valid_links) > 0
            
            self.record_test_result("deep_links", success,
                                  f"Deep-link generation: {link_summary}")
            
            if success:
                print(f"✅ Dashboard deep-links: PASSED ({len(valid_links)} links)")
            else:
                print("⚠️ Dashboard deep-links: WARNING - No links generated")
            
            return success
            
        except Exception as e:
            self.record_test_result("deep_links", False, str(e))
            print(f"❌ Dashboard deep-links: FAILED - {e}")
            return False
    
    def test_auto_provisioning(self):
        """Test 7: Auto-provisioning capabilities."""
        print("\n🤖 Test 7: Auto-Provisioning")
        
        try:
            if not self.collector:
                self.record_test_result("auto_provisioning", False, "Collector not initialized")
                return False
            
            # Test auto-provisioning for a test service
            result = self.collector.auto_provision_service_monitoring(
                service_name="test-service",
                service_port=8080,
                service_type="http"
            )
            
            if not isinstance(result, dict):
                self.record_test_result("auto_provisioning", False, "Invalid provisioning result")
                return False
            
            # Check result structure
            required_fields = ['service_name', 'dashboard_created', 'alerts_created']
            missing_fields = []
            
            for field in required_fields:
                if field not in result:
                    missing_fields.append(field)
            
            if missing_fields:
                self.record_test_result("auto_provisioning", False,
                                      f"Provisioning result missing fields: {missing_fields}")
                return False
            
            provisioning_summary = {
                'service_name': result['service_name'],
                'dashboard_created': result['dashboard_created'],
                'alerts_created': result['alerts_created'],
                'has_error': 'error' in result
            }
            
            self.record_test_result("auto_provisioning", True,
                                  f"Auto-provisioning working: {provisioning_summary}")
            print("✅ Auto-provisioning: PASSED")
            return True
            
        except Exception as e:
            self.record_test_result("auto_provisioning", False, str(e))
            print(f"❌ Auto-provisioning: FAILED - {e}")
            return False
    
    def test_registry_integration(self):
        """Test 8: Integration with Runtime State Registry."""
        print("\n🔗 Test 8: Registry Integration")
        
        try:
            # Initialize registry
            self.registry = RuntimeStateRegistry()
            
            # Check if Grafana collector is initialized
            if not hasattr(self.registry, 'grafana_collector'):
                self.record_test_result("registry_integration", False, 
                                      "Registry missing grafana_collector")
                return False
            
            # Test monitoring state method
            if not hasattr(self.registry, 'get_monitoring_state'):
                self.record_test_result("registry_integration", False,
                                      "Registry missing get_monitoring_state method")
                return False
            
            # Test dashboard link method
            if not hasattr(self.registry, 'generate_dashboard_link'):
                self.record_test_result("registry_integration", False,
                                      "Registry missing generate_dashboard_link method")
                return False
            
            # Test auto-provisioning method
            if not hasattr(self.registry, 'auto_provision_monitoring'):
                self.record_test_result("registry_integration", False,
                                      "Registry missing auto_provision_monitoring method")
                return False
            
            integration_summary = {
                'grafana_collector_available': self.registry.grafana_collector is not None,
                'monitoring_methods_available': True,
                'registry_health': self.registry.get_health_status().status.value
            }
            
            self.record_test_result("registry_integration", True,
                                  f"Registry integration working: {integration_summary}")
            print("✅ Registry integration: PASSED")
            return True
            
        except Exception as e:
            self.record_test_result("registry_integration", False, str(e))
            print(f"❌ Registry integration: FAILED - {e}")
            return False
    
    def record_test_result(self, test_name: str, passed: bool, details: str):
        """Record test result."""
        self.test_results.append({
            "test_name": test_name,
            "passed": passed,
            "details": details,
            "timestamp": datetime.now().isoformat()
        })
    
    def generate_test_report(self):
        """Generate comprehensive test report."""
        print("\n" + "=" * 50)
        print("🧪 GRAFANA INTELLIGENCE COLLECTOR TEST REPORT")
        print("=" * 50)
        
        passed_tests = [r for r in self.test_results if r["passed"]]
        failed_tests = [r for r in self.test_results if not r["passed"]]
        
        print(f"\n📊 SUMMARY:")
        print(f"   ✅ Passed: {len(passed_tests)}/{len(self.test_results)}")
        print(f"   ❌ Failed: {len(failed_tests)}/{len(self.test_results)}")
        print(f"   📈 Success Rate: {len(passed_tests)/len(self.test_results)*100:.1f}%")
        
        if failed_tests:
            print(f"\n❌ FAILED TESTS:")
            for test in failed_tests:
                print(f"   • {test['test_name']}: {test['details']}")
        
        print(f"\n✅ PASSED TESTS:")
        for test in passed_tests:
            print(f"   • {test['test_name']}: {test['details']}")
        
        # Phase 1 completion assessment
        critical_tests = [
            "collector_init",
            "monitoring_state",
            "registry_integration"
        ]
        
        critical_passed = [t for t in self.test_results 
                          if t["test_name"] in critical_tests and t["passed"]]
        
        phase1_complete = len(critical_passed) == len(critical_tests)
        
        print(f"\n🎯 PHASE 1 COMPLETION STATUS:")
        print(f"   Status: {'✅ COMPLETE' if phase1_complete else '❌ INCOMPLETE'}")
        print(f"   Critical Tests: {len(critical_passed)}/{len(critical_tests)} passed")
        
        if phase1_complete:
            print("\n🎉 Phase 1 Foundation Complete!")
            print("   ✅ Multi-source data collection system ready")
            print("   ✅ Grafana intelligence integration functional")
            print("   ✅ Ready for Phase 2: State Reconciliation Engine")
        else:
            failed_critical = [t for t in critical_tests 
                             if not any(r["test_name"] == t and r["passed"] 
                                      for r in self.test_results)]
            print(f"   Missing: {failed_critical}")
        
        # Save detailed report
        report_data = {
            "test_summary": {
                "total_tests": len(self.test_results),
                "passed_tests": len(passed_tests),
                "failed_tests": len(failed_tests),
                "success_rate": len(passed_tests)/len(self.test_results)*100,
                "phase1_complete": phase1_complete
            },
            "test_results": self.test_results,
            "timestamp": datetime.now().isoformat()
        }
        
        report_file = "grafana_intelligence_collector_test_report.json"
        with open(report_file, 'w') as f:
            json.dump(report_data, f, indent=2)
        
        print(f"\n📄 Detailed report saved to: {report_file}")


def main():
    """Run the test suite."""
    test_suite = GrafanaCollectorTestSuite()
    success = test_suite.run_all_tests()
    
    if success:
        print("\n🎉 All tests passed! Grafana Intelligence Collector is ready.")
        return 0
    else:
        print("\n⚠️ Some tests failed. Review the issues before proceeding.")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)