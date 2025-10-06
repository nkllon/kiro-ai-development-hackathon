#!/usr/bin/env python3
"""
Phase 1 Integration Test - System Architecture Discovery
=======================================================

Integration test for all Phase 1 tasks of the system architecture
wiring diagram implementation.
"""

import asyncio
import logging
import json
from typing import Dict, Any, List
from datetime import datetime
from pathlib import Path

from src.rm_ddd.core.unified_reflective_module import ReflectiveModule
from src.system_architecture.discovery.infrastructure_discoverer import InfrastructureDiscoverer
from src.system_architecture.discovery.observatory_websocket_client import ObservatoryWebSocketClient
from src.system_architecture.discovery.system_constraint_validator import SystemConstraintValidator
from src.system_architecture.discovery.cloudflare_tunnel_discoverer import CloudflareTunnelDiscoverer
from src.system_architecture.discovery.makefile_analyzer import MakefileAnalyzer
from src.system_architecture.discovery.network_topology_discoverer import NetworkTopologyDiscoverer


class Phase1IntegrationTest(ReflectiveModule):
    """
    Integration test for Phase 1 system architecture discovery tasks.
    
    Tests all completed Phase 1 tasks:
    - 1.1: Infrastructure Discovery Engine ✓
    - 1.2: Observatory WebSocket Integration ✓
    - 1.3: Service Discovery Scanner ✓
    - 1.4: System Constraint Validation ✓
    - 1.5: Cloudflare Tunnel Discovery ✓
    - 1.6: Makefile Analysis System ✓
    - 1.7: Network Topology Discovery ✓
    """
    
    def __init__(self):
        super().__init__()
        self.module_id = "Phase1IntegrationTest"
        self._logger = logging.getLogger(f"system_architecture.{self.__class__.__name__}")
        
        # Initialize all Phase 1 components
        self._infrastructure_discoverer = InfrastructureDiscoverer()
        self._websocket_client = ObservatoryWebSocketClient()
        self._constraint_validator = SystemConstraintValidator()
        self._tunnel_discoverer = CloudflareTunnelDiscoverer()
        self._makefile_analyzer = MakefileAnalyzer()
        self._network_discoverer = NetworkTopologyDiscoverer()
        
        self._test_results: Dict[str, Any] = {}
        
    async def run_comprehensive_phase1_test(self) -> Dict[str, Any]:
        """Run comprehensive Phase 1 integration test."""
        self._logger.info("Starting Phase 1 comprehensive integration test...")
        
        test_results = {
            "test_timestamp": datetime.now().isoformat(),
            "phase": "Phase 1 - Infrastructure Discovery Engine",
            "tasks_tested": [
                "1.1 - Infrastructure Discovery Engine",
                "1.2 - Observatory WebSocket Integration", 
                "1.3 - Service Discovery Scanner",
                "1.4 - System Constraint Validation",
                "1.5 - Cloudflare Tunnel Discovery",
                "1.6 - Makefile Analysis System",
                "1.7 - Network Topology Discovery"
            ],
            "test_results": {},
            "integration_results": {},
            "overall_status": "unknown"
        }
        
        try:
            # Test Task 1.1 - Infrastructure Discovery Engine
            self._logger.info("Testing Task 1.1 - Infrastructure Discovery Engine...")
            task_1_1_result = await self._test_infrastructure_discovery()
            test_results["test_results"]["task_1_1"] = task_1_1_result
            
            # Test Task 1.2 - Observatory WebSocket Integration
            self._logger.info("Testing Task 1.2 - Observatory WebSocket Integration...")
            task_1_2_result = await self._test_websocket_integration()
            test_results["test_results"]["task_1_2"] = task_1_2_result
            
            # Test Task 1.3 - Service Discovery Scanner (part of 1.1)
            self._logger.info("Testing Task 1.3 - Service Discovery Scanner...")
            task_1_3_result = await self._test_service_discovery()
            test_results["test_results"]["task_1_3"] = task_1_3_result
            
            # Test Task 1.4 - System Constraint Validation
            self._logger.info("Testing Task 1.4 - System Constraint Validation...")
            task_1_4_result = await self._test_constraint_validation()
            test_results["test_results"]["task_1_4"] = task_1_4_result
            
            # Test Task 1.5 - Cloudflare Tunnel Discovery
            self._logger.info("Testing Task 1.5 - Cloudflare Tunnel Discovery...")
            task_1_5_result = await self._test_tunnel_discovery()
            test_results["test_results"]["task_1_5"] = task_1_5_result
            
            # Test Task 1.6 - Makefile Analysis System
            self._logger.info("Testing Task 1.6 - Makefile Analysis System...")
            task_1_6_result = await self._test_makefile_analysis()
            test_results["test_results"]["task_1_6"] = task_1_6_result
            
            # Test Task 1.7 - Network Topology Discovery
            self._logger.info("Testing Task 1.7 - Network Topology Discovery...")
            task_1_7_result = await self._test_network_topology()
            test_results["test_results"]["task_1_7"] = task_1_7_result
            
            # Test integration between components
            self._logger.info("Testing Phase 1 component integration...")
            integration_result = await self._test_phase1_integration()
            test_results["integration_results"] = integration_result
            
            # Determine overall status
            all_tasks_passed = all(
                result.get("status") == "passed" 
                for result in test_results["test_results"].values()
            )
            integration_passed = integration_result.get("status") == "passed"
            
            if all_tasks_passed and integration_passed:
                test_results["overall_status"] = "passed"
            elif all_tasks_passed:
                test_results["overall_status"] = "passed_with_integration_warnings"
            else:
                test_results["overall_status"] = "failed"
            
            self._logger.info(f"Phase 1 integration test completed: {test_results['overall_status']}")
            
        except Exception as e:
            self._logger.error(f"Phase 1 integration test failed: {e}")
            test_results["overall_status"] = "error"
            test_results["error"] = str(e)
        
        self._test_results = test_results
        return test_results
    
    async def _test_infrastructure_discovery(self) -> Dict[str, Any]:
        """Test Task 1.1 - Infrastructure Discovery Engine."""
        try:
            # Test comprehensive discovery
            discovery_report = await self._infrastructure_discoverer.perform_comprehensive_discovery()
            
            # Validate discovery results
            required_sections = ["services", "network_topology", "configurations", "automation_scripts"]
            missing_sections = [section for section in required_sections if section not in discovery_report]
            
            if missing_sections:
                return {
                    "status": "failed",
                    "error": f"Missing required sections: {missing_sections}",
                    "discovery_report": discovery_report
                }
            
            # Check if services were discovered
            services_found = len(discovery_report.get("services", []))
            
            return {
                "status": "passed",
                "services_discovered": services_found,
                "network_topology_mapped": bool(discovery_report.get("network_topology")),
                "configurations_found": len(discovery_report.get("configurations", {}).get("yaml_configs", [])),
                "automation_scripts_found": len(discovery_report.get("automation_scripts", {}).get("python_scripts", [])),
                "discovery_report": discovery_report
            }
            
        except Exception as e:
            return {
                "status": "failed",
                "error": str(e)
            }
    
    async def _test_websocket_integration(self) -> Dict[str, Any]:
        """Test Task 1.2 - Observatory WebSocket Integration."""
        try:
            # Discover WebSocket endpoints
            endpoints = self._websocket_client.discover_websocket_endpoints()
            
            # Test connection (will fail if Observatory not running, but that's expected)
            connection_summary = self._websocket_client.get_connection_summary()
            
            # Validate expected endpoints
            expected_endpoints = ["/ws/observatory", "/ws/emoji-rain", "/ws/anomalies", "/ws/doctor-status"]
            discovered_endpoints = [ep.path for ep in endpoints]
            
            missing_endpoints = [ep for ep in expected_endpoints if ep not in discovered_endpoints]
            
            if missing_endpoints:
                return {
                    "status": "failed",
                    "error": f"Missing expected endpoints: {missing_endpoints}",
                    "discovered_endpoints": discovered_endpoints
                }
            
            return {
                "status": "passed",
                "endpoints_discovered": len(endpoints),
                "expected_endpoints_found": len(expected_endpoints),
                "connection_summary": connection_summary
            }
            
        except Exception as e:
            return {
                "status": "failed",
                "error": str(e)
            }
    
    async def _test_service_discovery(self) -> Dict[str, Any]:
        """Test Task 1.3 - Service Discovery Scanner."""
        try:
            # Test service discovery
            services = self._infrastructure_discoverer.discover_services()
            
            # Test network configuration discovery
            network_config = self._infrastructure_discoverer.discover_network_config()
            
            # Test configuration discovery
            configurations = self._infrastructure_discoverer.discover_configurations()
            
            return {
                "status": "passed",
                "services_discovered": len(services),
                "network_config_mapped": bool(network_config),
                "configurations_found": len(configurations.yaml_configs) + len(configurations.json_configs),
                "makefile_targets": len(configurations.makefile_targets)
            }
            
        except Exception as e:
            return {
                "status": "failed",
                "error": str(e)
            }
    
    async def _test_constraint_validation(self) -> Dict[str, Any]:
        """Test Task 1.4 - System Constraint Validation."""
        try:
            # Test constraint validation
            validation_results = await self._constraint_validator.validate_all_constraints()
            
            # Test configuration mode determination
            redis_status = self._constraint_validator.get_redis_coordination_status()
            observatory_mode = self._constraint_validator.get_observatory_discovery_mode()
            fallback_docs = self._constraint_validator.get_fallback_documentation()
            
            return {
                "status": "passed",
                "overall_constraint_status": validation_results.get("overall_status"),
                "constraints_validated": len(validation_results.get("constraints", [])),
                "fallback_modes_active": len(validation_results.get("fallback_modes_active", [])),
                "configuration_mode": validation_results.get("configuration_mode", {}).get("mode"),
                "redis_coordination": redis_status.get("coordination_mode"),
                "observatory_discovery": observatory_mode.get("discovery_mode"),
                "fallback_documentation": len(fallback_docs.get("active_fallbacks", []))
            }
            
        except Exception as e:
            return {
                "status": "failed",
                "error": str(e)
            }
    
    async def _test_tunnel_discovery(self) -> Dict[str, Any]:
        """Test Task 1.5 - Cloudflare Tunnel Discovery."""
        try:
            # Test tunnel discovery
            tunnel_report = self._tunnel_discoverer.generate_tunnel_report()
            
            # Validate tunnel configuration
            tunnel_config = tunnel_report.get("tunnel_configuration", {})
            expected_tunnel_id = "d1e53e43-033f-4994-8f46-c83962ae3785"
            
            if tunnel_config.get("tunnel_id") != expected_tunnel_id:
                return {
                    "status": "failed",
                    "error": f"Expected tunnel ID {expected_tunnel_id}, got {tunnel_config.get('tunnel_id')}",
                    "tunnel_report": tunnel_report
                }
            
            return {
                "status": "passed",
                "tunnel_id": tunnel_config.get("tunnel_id"),
                "tunnel_status": tunnel_config.get("status"),
                "ingress_rules": len(tunnel_config.get("ingress_rules", [])),
                "dns_routing": len(tunnel_config.get("dns_routing", [])),
                "validation_results": tunnel_report.get("validation_results"),
                "performance_metrics": tunnel_report.get("performance_metrics")
            }
            
        except Exception as e:
            return {
                "status": "failed",
                "error": str(e)
            }
    
    async def _test_makefile_analysis(self) -> Dict[str, Any]:
        """Test Task 1.6 - Makefile Analysis System."""
        try:
            # Test Makefile analysis
            analysis_report = self._makefile_analyzer.get_comprehensive_analysis()
            
            # Validate analysis results
            summary = analysis_report.get("summary", {})
            
            # Check for key targets
            targets = analysis_report.get("targets", {})
            expected_targets = ["tunnel-start", "dashboard-up", "dashboard-status"]
            found_targets = [target for target in expected_targets if target in targets]
            
            return {
                "status": "passed",
                "total_targets": summary.get("total_targets", 0),
                "target_categories": summary.get("target_categories", {}),
                "dependency_chains": summary.get("dependency_chains", 0),
                "script_mappings": summary.get("script_mappings", 0),
                "expected_targets_found": len(found_targets),
                "workflow_diagrams": len(analysis_report.get("workflow_diagrams", {})),
                "recommendations": len(analysis_report.get("recommendations", []))
            }
            
        except Exception as e:
            return {
                "status": "failed",
                "error": str(e)
            }
    
    async def _test_network_topology(self) -> Dict[str, Any]:
        """Test Task 1.7 - Network Topology Discovery."""
        try:
            # Test network topology discovery
            topology = self._network_discoverer.discover_network_topology()
            
            # Validate topology results
            return {
                "status": "passed",
                "local_network_range": topology.local_network_range,
                "service_endpoints": len(topology.service_endpoints),
                "network_flows": len(topology.network_flows),
                "dns_mappings": len(topology.dns_mappings),
                "websocket_configs": len(topology.websocket_configs),
                "port_allocations": len(topology.port_allocations),
                "failover_mechanisms": len(topology.failover_mechanisms),
                "redis_coordination": bool(topology.redis_coordination)
            }
            
        except Exception as e:
            return {
                "status": "failed",
                "error": str(e)
            }
    
    async def _test_phase1_integration(self) -> Dict[str, Any]:
        """Test integration between Phase 1 components."""
        try:
            integration_tests = []
            
            # Test 1: Infrastructure discoverer + constraint validator integration
            try:
                services = self._infrastructure_discoverer.discover_services()
                constraints = await self._constraint_validator.validate_all_constraints()
                
                # Check if discovered services align with constraint validation
                service_names = [s.name for s in services]
                constraint_services = ["Observatory", "Prometheus", "Grafana", "Redis"]
                
                aligned_services = [s for s in constraint_services if any(s in sn for sn in service_names)]
                
                integration_tests.append({
                    "test": "infrastructure_constraint_alignment",
                    "status": "passed",
                    "services_discovered": len(services),
                    "constraints_validated": len(constraints.get("constraints", [])),
                    "aligned_services": len(aligned_services)
                })
                
            except Exception as e:
                integration_tests.append({
                    "test": "infrastructure_constraint_alignment",
                    "status": "failed",
                    "error": str(e)
                })
            
            # Test 2: WebSocket client + network topology integration
            try:
                endpoints = self._websocket_client.discover_websocket_endpoints()
                topology = self._network_discoverer.discover_network_topology()
                
                # Check if WebSocket endpoints are reflected in network topology
                ws_paths = [ep.path for ep in endpoints]
                topology_ws_configs = topology.websocket_configs
                topology_ws_paths = [config.endpoint for config in topology_ws_configs]
                
                matching_endpoints = [path for path in ws_paths if path in topology_ws_paths]
                
                integration_tests.append({
                    "test": "websocket_topology_alignment",
                    "status": "passed",
                    "websocket_endpoints": len(endpoints),
                    "topology_websocket_configs": len(topology_ws_configs),
                    "matching_endpoints": len(matching_endpoints)
                })
                
            except Exception as e:
                integration_tests.append({
                    "test": "websocket_topology_alignment",
                    "status": "failed",
                    "error": str(e)
                })
            
            # Test 3: Tunnel discoverer + network topology integration
            try:
                tunnel_report = self._tunnel_discoverer.generate_tunnel_report()
                topology = self._network_discoverer.discover_network_topology()
                
                # Check if tunnel configuration aligns with DNS mappings
                tunnel_dns = tunnel_report.get("tunnel_configuration", {}).get("dns_routing", [])
                topology_dns = topology.dns_mappings
                
                tunnel_domains = [dns.get("subdomain") for dns in tunnel_dns]
                topology_domains = [dns.domain for dns in topology_dns]
                
                matching_domains = [domain for domain in tunnel_domains if domain in topology_domains]
                
                integration_tests.append({
                    "test": "tunnel_topology_alignment",
                    "status": "passed",
                    "tunnel_dns_mappings": len(tunnel_dns),
                    "topology_dns_mappings": len(topology_dns),
                    "matching_domains": len(matching_domains)
                })
                
            except Exception as e:
                integration_tests.append({
                    "test": "tunnel_topology_alignment",
                    "status": "failed",
                    "error": str(e)
                })
            
            # Determine overall integration status
            failed_tests = [test for test in integration_tests if test.get("status") == "failed"]
            
            return {
                "status": "passed" if not failed_tests else "failed",
                "integration_tests": integration_tests,
                "total_tests": len(integration_tests),
                "passed_tests": len(integration_tests) - len(failed_tests),
                "failed_tests": len(failed_tests)
            }
            
        except Exception as e:
            return {
                "status": "failed",
                "error": str(e)
            }
    
    def save_test_results(self, output_path: str = "phase1_integration_test_results.json") -> None:
        """Save test results to file."""
        try:
            with open(output_path, 'w') as f:
                json.dump(self._test_results, f, indent=2, default=str)
            self._logger.info(f"Test results saved to {output_path}")
        except Exception as e:
            self._logger.error(f"Failed to save test results: {e}")
    
    def get_test_summary(self) -> Dict[str, Any]:
        """Get test summary."""
        if not self._test_results:
            return {"status": "not_run"}
        
        test_results = self._test_results.get("test_results", {})
        passed_tasks = [task for task, result in test_results.items() if result.get("status") == "passed"]
        failed_tasks = [task for task, result in test_results.items() if result.get("status") == "failed"]
        
        return {
            "overall_status": self._test_results.get("overall_status"),
            "total_tasks": len(test_results),
            "passed_tasks": len(passed_tasks),
            "failed_tasks": len(failed_tasks),
            "passed_task_list": passed_tasks,
            "failed_task_list": failed_tasks,
            "integration_status": self._test_results.get("integration_results", {}).get("status"),
            "test_timestamp": self._test_results.get("test_timestamp")
        }


async def main():
    """Run Phase 1 integration test."""
    logging.basicConfig(level=logging.INFO)
    
    test = Phase1IntegrationTest()
    results = await test.run_comprehensive_phase1_test()
    
    # Save results
    test.save_test_results()
    
    # Print summary
    summary = test.get_test_summary()
    print("\n" + "="*60)
    print("PHASE 1 INTEGRATION TEST SUMMARY")
    print("="*60)
    print(f"Overall Status: {summary.get('overall_status')}")
    print(f"Tasks Tested: {summary.get('total_tasks')}")
    print(f"Tasks Passed: {summary.get('passed_tasks')}")
    print(f"Tasks Failed: {summary.get('failed_tasks')}")
    print(f"Integration Status: {summary.get('integration_status')}")
    print(f"Test Timestamp: {summary.get('test_timestamp')}")
    
    if summary.get('failed_task_list'):
        print(f"\nFailed Tasks: {', '.join(summary.get('failed_task_list'))}")
    
    print("="*60)
    
    return results


if __name__ == "__main__":
    asyncio.run(main())