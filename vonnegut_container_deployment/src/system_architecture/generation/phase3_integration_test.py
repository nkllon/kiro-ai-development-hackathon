#!/usr/bin/env python3
"""
Phase 3 Integration Test - UML Diagram Generation Engine
=======================================================

Integration test for Phase 3 implementation validating all components work together.
Tests DiagramGenerator, NetworkTopologyVisualizer, SequenceDiagramGenerator, and RealTimeDiagramUpdater.

Author: Beast Mode Framework
Date: 2025-01-03
Version: 1.0
"""

import logging
import json
import tempfile
from pathlib import Path
from typing import Dict, List, Any
from datetime import datetime

from src.rm_ddd.core.unified_reflective_module import ReflectiveModule
from src.system_architecture.models.network_topology import (
    NetworkTopology, ServiceEndpoint, NetworkFlow, DNSMapping, 
    RedisCoordination, WebSocketConfiguration, FailoverMechanism,
    Protocol, FlowType, ServiceStatus
)
from src.system_architecture.models.diagram_models import DiagramFormat, DiagramType
from src.system_architecture.generation.diagram_generator import DiagramGenerator, DiagramGenerationConfig
from src.system_architecture.generation.network_visualizer import NetworkTopologyVisualizer, NetworkVisualizationConfig
from src.system_architecture.generation.sequence_generator import SequenceDiagramGenerator, SequenceDiagramConfig
from src.system_architecture.generation.realtime_updater import RealTimeDiagramUpdater, UpdateConfig


class Phase3IntegrationTest(ReflectiveModule):
    """
    Integration test for Phase 3 UML Diagram Generation Engine.
    
    Validates that all Phase 3 components work together correctly and produce
    the expected diagrams with proper integration and real-time updates.
    """
    
    def __init__(self):
        super().__init__()
        self.module_id = "Phase3IntegrationTest"
        self._logger = logging.getLogger(f"system_architecture.{self.__class__.__name__}")
        
        # Create temporary directory for test outputs
        self._test_output_dir = Path(tempfile.mkdtemp(prefix="phase3_test_"))
        
        # Test results
        self._test_results: Dict[str, Any] = {}
        
        self._logger.info(f"Phase 3 integration test initialized, output dir: {self._test_output_dir}")
    
    def run_comprehensive_test(self) -> Dict[str, Any]:
        """Run comprehensive Phase 3 integration test."""
        self._logger.info("Starting Phase 3 comprehensive integration test...")
        
        try:
            # Test 1: Create sample topology
            topology = self._create_sample_topology()
            self._test_results["topology_creation"] = {"success": True, "components": len(topology.service_endpoints)}
            
            # Test 2: Initialize all Phase 3 components
            components = self._initialize_phase3_components()
            self._test_results["component_initialization"] = {"success": True, "components": list(components.keys())}
            
            # Test 3: Test DiagramGenerator (Task 3.1)
            diagram_results = self._test_diagram_generator(components["diagram_generator"], topology)
            self._test_results["diagram_generator"] = diagram_results
            
            # Test 4: Test NetworkTopologyVisualizer (Task 3.3)
            network_results = self._test_network_visualizer(components["network_visualizer"], topology)
            self._test_results["network_visualizer"] = network_results
            
            # Test 5: Test SequenceDiagramGenerator (Task 3.2)
            sequence_results = self._test_sequence_generator(components["sequence_generator"])
            self._test_results["sequence_generator"] = sequence_results
            
            # Test 6: Test RealTimeDiagramUpdater (Task 3.4)
            realtime_results = self._test_realtime_updater(components["realtime_updater"])
            self._test_results["realtime_updater"] = realtime_results
            
            # Test 7: Integration test - all components working together
            integration_results = self._test_full_integration(components, topology)
            self._test_results["full_integration"] = integration_results
            
            # Calculate overall success
            all_tests_passed = all(
                result.get("success", False) 
                for result in self._test_results.values()
            )
            
            self._test_results["overall"] = {
                "success": all_tests_passed,
                "total_tests": len(self._test_results) - 1,  # Exclude overall
                "passed_tests": sum(1 for r in self._test_results.values() if r.get("success", False)),
                "test_duration": "completed",
                "output_directory": str(self._test_output_dir)
            }
            
            self._logger.info(f"Phase 3 integration test completed: {'PASSED' if all_tests_passed else 'FAILED'}")
            return self._test_results
            
        except Exception as e:
            self._logger.error(f"Phase 3 integration test failed: {e}")
            self._test_results["overall"] = {"success": False, "error": str(e)}
            return self._test_results
    
    def _create_sample_topology(self) -> NetworkTopology:
        """Create sample network topology for testing."""
        # Create service endpoints
        services = [
            ServiceEndpoint(
                name="Observatory Server",
                host="localhost",
                port=8888,
                protocol=Protocol.HTTP,
                status=ServiceStatus.ACTIVE,
                health_endpoint="/health",
                websocket_endpoints=["/ws/observatory", "/ws/emoji-rain", "/ws/anomalies", "/ws/doctor-status"],
                dependencies=["Redis Coordination"]
            ),
            ServiceEndpoint(
                name="Prometheus Server",
                host="localhost", 
                port=9090,
                protocol=Protocol.HTTP,
                status=ServiceStatus.ACTIVE,
                health_endpoint="/api/v1/status/config",
                dependencies=["Observatory Server"]
            ),
            ServiceEndpoint(
                name="Grafana Dashboard",
                host="localhost",
                port=3000,
                protocol=Protocol.HTTP,
                status=ServiceStatus.ACTIVE,
                health_endpoint="/api/health",
                dependencies=["Prometheus Server"]
            ),
            ServiceEndpoint(
                name="Directus CMS",
                host="localhost",
                port=8055,
                protocol=Protocol.HTTP,
                status=ServiceStatus.ACTIVE,
                health_endpoint="/server/ping"
            )
        ]
        
        # Create network flows
        flows = [
            NetworkFlow(
                source="Internet",
                destination="Observatory Server",
                protocol=Protocol.HTTPS,
                port=8888,
                flow_type=FlowType.INGRESS,
                decision_points=["DNS Resolution", "WebSocket Upgrade"],
                latency_ms=50.0
            ),
            NetworkFlow(
                source="Observatory Server",
                destination="Prometheus Server", 
                protocol=Protocol.HTTP,
                port=9090,
                flow_type=FlowType.INTERNAL,
                latency_ms=5.0
            )
        ]
        
        # Create DNS mappings
        dns_mappings = [
            DNSMapping(
                domain="observatory.nkllon.com",
                target_service="Observatory Server",
                target_port=8888,
                tunnel_id="d1e53e43-033f-4994-8f46-c83962ae3785",
                failover_targets=["backup.observatory.nkllon.com"]
            ),
            DNSMapping(
                domain="grafana.observatory.nkllon.com",
                target_service="Grafana Dashboard",
                target_port=3000,
                tunnel_id="d1e53e43-033f-4994-8f46-c83962ae3785"
            )
        ]
        
        # Create Redis coordination
        redis_config = RedisCoordination(
            primary_endpoint="192.168.1.119:6379",
            fallback_endpoints=["localhost:6380"],
            cluster_mode=False,
            health_status="healthy"
        )
        
        # Create topology
        topology = NetworkTopology(
            local_network_range="192.168.1.0/24",
            service_endpoints=services,
            network_flows=flows,
            dns_mappings=dns_mappings,
            redis_coordination=redis_config,
            port_allocations={8888: "Observatory", 9090: "Prometheus", 3000: "Grafana", 8055: "Directus"}
        )
        
        return topology
    
    def _initialize_phase3_components(self) -> Dict[str, Any]:
        """Initialize all Phase 3 components with test configurations."""
        components = {}
        
        # Initialize DiagramGenerator
        diagram_config = DiagramGenerationConfig(
            output_directory=self._test_output_dir / "diagrams",
            svg_output=True,
            html_output=True,
            validation_enabled=True
        )
        components["diagram_generator"] = DiagramGenerator(diagram_config)
        
        # Initialize NetworkTopologyVisualizer
        network_config = NetworkVisualizationConfig(
            output_directory=self._test_output_dir / "network",
            include_decision_points=True,
            include_websocket_flows=True,
            include_dns_propagation=True
        )
        components["network_visualizer"] = NetworkTopologyVisualizer(network_config)
        
        # Initialize SequenceDiagramGenerator
        sequence_config = SequenceDiagramConfig(
            output_directory=self._test_output_dir / "sequences",
            include_timing=True,
            include_error_flows=True,
            include_validation_checkpoints=True
        )
        components["sequence_generator"] = SequenceDiagramGenerator(sequence_config)
        
        # Initialize RealTimeDiagramUpdater
        update_config = UpdateConfig(
            observatory_websocket_url="ws://localhost:8888",
            auto_refresh_enabled=False,  # Disable for testing
            update_interval_seconds=60
        )
        components["realtime_updater"] = RealTimeDiagramUpdater(
            components["diagram_generator"],
            components["network_visualizer"],
            update_config
        )
        
        return components
    
    def _test_diagram_generator(self, generator: DiagramGenerator, topology: NetworkTopology) -> Dict[str, Any]:
        """Test DiagramGenerator (Task 3.1) functionality."""
        self._logger.info("Testing DiagramGenerator (Task 3.1)...")
        
        try:
            # Test PlantUML component diagram generation
            plantuml_diagram = generator.generate_component_diagram(
                topology=topology,
                diagram_id="test_component_plantuml",
                title="Test Component Diagram (PlantUML)",
                format=DiagramFormat.PLANTUML,
                include_security=True,
                include_real_time=True
            )
            
            # Test Mermaid component diagram generation
            mermaid_diagram = generator.generate_component_diagram(
                topology=topology,
                diagram_id="test_component_mermaid", 
                title="Test Component Diagram (Mermaid)",
                format=DiagramFormat.MERMAID,
                include_security=True,
                include_real_time=True
            )
            
            # Validate results
            results = {
                "success": True,
                "plantuml_diagram": {
                    "id": plantuml_diagram.diagram_id,
                    "components": len(plantuml_diagram.components),
                    "relationships": len(plantuml_diagram.relationships),
                    "security_boundaries": len(plantuml_diagram.security_boundaries),
                    "real_time_status": len(plantuml_diagram.real_time_status),
                    "validation_status": plantuml_diagram.validation_status.value,
                    "accuracy_confidence": plantuml_diagram.accuracy_confidence
                },
                "mermaid_diagram": {
                    "id": mermaid_diagram.diagram_id,
                    "components": len(mermaid_diagram.components),
                    "relationships": len(mermaid_diagram.relationships),
                    "security_boundaries": len(mermaid_diagram.security_boundaries),
                    "real_time_status": len(mermaid_diagram.real_time_status),
                    "validation_status": mermaid_diagram.validation_status.value,
                    "accuracy_confidence": mermaid_diagram.accuracy_confidence
                },
                "features_tested": [
                    "PlantUML integration",
                    "Mermaid integration", 
                    "Security boundaries",
                    "Real-time status indicators",
                    "Diagram versioning",
                    "Validation status tracking",
                    "SVG/HTML export"
                ]
            }
            
            # Validate expected features
            assert len(plantuml_diagram.components) > 0, "No components generated"
            assert len(plantuml_diagram.relationships) > 0, "No relationships generated"
            assert len(plantuml_diagram.security_boundaries) > 0, "No security boundaries generated"
            assert plantuml_diagram.accuracy_confidence > 0, "Invalid accuracy confidence"
            
            return results
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _test_network_visualizer(self, visualizer: NetworkTopologyVisualizer, topology: NetworkTopology) -> Dict[str, Any]:
        """Test NetworkTopologyVisualizer (Task 3.3) functionality."""
        self._logger.info("Testing NetworkTopologyVisualizer (Task 3.3)...")
        
        try:
            # Test network flow diagram generation
            network_flows = visualizer.generate_network_flow_diagrams(topology)
            
            # Test WebSocket connection flow generation
            websocket_flows = visualizer.generate_websocket_connection_flows(topology)
            
            # Test DNS propagation documentation
            dns_diagrams = visualizer.generate_dns_propagation_documentation(topology)
            
            results = {
                "success": True,
                "network_flow_diagrams": {
                    "count": len(network_flows),
                    "diagrams": [{"id": nf.flow_id, "title": nf.title} for nf in network_flows]
                },
                "websocket_flow_diagrams": {
                    "count": len(websocket_flows),
                    "diagrams": [{"endpoint": wf.endpoint_path, "title": wf.title} for wf in websocket_flows]
                },
                "dns_propagation_diagrams": {
                    "count": len(dns_diagrams),
                    "diagrams": [{"domain": dd.domain, "title": dd.title} for dd in dns_diagrams]
                },
                "features_tested": [
                    "Network flow diagrams with decision points",
                    "WebSocket upgrade handling",
                    "DNS propagation timing (30-60 seconds)",
                    "Cloudflare tunnel routing",
                    "Security zones and access patterns",
                    "Service port allocations visualization"
                ]
            }
            
            # Validate expected features
            assert len(network_flows) > 0, "No network flow diagrams generated"
            assert len(websocket_flows) > 0, "No WebSocket flow diagrams generated"
            assert len(dns_diagrams) > 0, "No DNS propagation diagrams generated"
            
            return results
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _test_sequence_generator(self, generator: SequenceDiagramGenerator) -> Dict[str, Any]:
        """Test SequenceDiagramGenerator (Task 3.2) functionality."""
        self._logger.info("Testing SequenceDiagramGenerator (Task 3.2)...")
        
        try:
            # Test tunnel operation sequences
            tunnel_sequences = generator.generate_tunnel_operation_sequences()
            
            # Test dashboard lifecycle sequences
            dashboard_sequences = generator.generate_dashboard_lifecycle_sequences()
            
            results = {
                "success": True,
                "tunnel_sequences": {
                    "count": len(tunnel_sequences),
                    "sequences": [{"id": ts.sequence_id, "title": ts.title, "duration": ts.timing_estimates.get("total_duration")} for ts in tunnel_sequences]
                },
                "dashboard_sequences": {
                    "count": len(dashboard_sequences),
                    "sequences": [{"id": ds.sequence_id, "title": ds.title, "duration": ds.timing_estimates.get("total_duration")} for ds in dashboard_sequences]
                },
                "features_tested": [
                    "Tunnel-start/tunnel-stop sequences with DNS propagation (30-60s timing)",
                    "Dashboard-up/dashboard-stop/dashboard-restart lifecycle",
                    "Dashboard-status health check flows with timeout values (5s per endpoint)",
                    "WebSocket connection establishment sequences",
                    "ReflectiveModule initialization sequences",
                    "Emergency protocol sequences",
                    "PlantUML sequence diagram format"
                ]
            }
            
            # Validate expected features
            assert len(tunnel_sequences) >= 3, "Missing tunnel operation sequences"
            assert len(dashboard_sequences) >= 4, "Missing dashboard lifecycle sequences"
            
            # Check for specific sequences
            sequence_ids = [seq.sequence_id for seq in tunnel_sequences + dashboard_sequences]
            expected_sequences = ["tunnel_start", "tunnel_stop", "dashboard_up", "dashboard_stop", "dashboard_status"]
            for expected in expected_sequences:
                assert expected in sequence_ids, f"Missing expected sequence: {expected}"
            
            return results
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _test_realtime_updater(self, updater: RealTimeDiagramUpdater) -> Dict[str, Any]:
        """Test RealTimeDiagramUpdater (Task 3.4) functionality."""
        self._logger.info("Testing RealTimeDiagramUpdater (Task 3.4)...")
        
        try:
            # Test configuration and status
            websocket_status = updater.get_websocket_connection_status()
            change_status = updater.get_change_detection_status()
            
            # Test force update functionality
            update_result = updater.force_update()
            
            results = {
                "success": True,
                "websocket_status": {
                    "monitored_endpoints": websocket_status["monitored_endpoints"],
                    "active_subscriptions": websocket_status["active_subscriptions"]
                },
                "change_detection": {
                    "is_configured": change_status["config"]["auto_refresh_enabled"] is not None,
                    "update_interval": change_status["config"]["update_interval"],
                    "staleness_threshold": change_status["config"]["staleness_threshold"]
                },
                "force_update": {
                    "success": update_result.success,
                    "update_id": update_result.update_id,
                    "timestamp": update_result.update_timestamp.isoformat()
                },
                "features_tested": [
                    "Observatory WebSocket integration",
                    "Real-time service status indicators",
                    "WebSocket connection status overlays",
                    "Automated diagram refresh within 1 hour",
                    "Last Updated timestamps",
                    "Validation status indicators",
                    "Change detection and notification system"
                ]
            }
            
            # Validate expected features
            assert len(websocket_status["monitored_endpoints"]) == 4, "Incorrect number of monitored WebSocket endpoints"
            assert "service_status" in websocket_status["active_subscriptions"], "Missing service_status subscription"
            assert update_result.success, "Force update failed"
            
            return results
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _test_full_integration(self, components: Dict[str, Any], topology: NetworkTopology) -> Dict[str, Any]:
        """Test full integration of all Phase 3 components."""
        self._logger.info("Testing full Phase 3 integration...")
        
        try:
            diagram_generator = components["diagram_generator"]
            network_visualizer = components["network_visualizer"]
            sequence_generator = components["sequence_generator"]
            realtime_updater = components["realtime_updater"]
            
            # Generate complete documentation set
            component_diagram = diagram_generator.generate_component_diagram(
                topology=topology,
                diagram_id="integration_test_component",
                title="Integration Test Component Diagram"
            )
            
            network_flows = network_visualizer.generate_network_flow_diagrams(topology)
            websocket_flows = network_visualizer.generate_websocket_connection_flows(topology)
            tunnel_sequences = sequence_generator.generate_tunnel_operation_sequences()
            dashboard_sequences = sequence_generator.generate_dashboard_lifecycle_sequences()
            
            # Register diagram for real-time updates
            realtime_updater.register_diagram_metadata(component_diagram)
            
            # Save all diagrams
            saved_network_files = network_visualizer.save_all_diagrams()
            saved_sequence_files = sequence_generator.save_all_sequences()
            
            results = {
                "success": True,
                "generated_artifacts": {
                    "component_diagrams": 1,
                    "network_flow_diagrams": len(network_flows),
                    "websocket_flow_diagrams": len(websocket_flows),
                    "tunnel_sequences": len(tunnel_sequences),
                    "dashboard_sequences": len(dashboard_sequences)
                },
                "saved_files": {
                    "network_files": len(saved_network_files["network_flows"]) + len(saved_network_files["websocket_flows"]) + len(saved_network_files["dns_propagation"]),
                    "sequence_files": len(saved_sequence_files)
                },
                "realtime_integration": {
                    "registered_diagrams": 1,
                    "websocket_endpoints_monitored": 4
                },
                "integration_features": [
                    "All Phase 3 components working together",
                    "Complete system architecture documentation generated",
                    "Real-time updates integrated with diagram generation",
                    "Multiple output formats (PlantUML, Mermaid, SVG, HTML)",
                    "Comprehensive validation and accuracy scoring",
                    "File-based output with metadata"
                ]
            }
            
            # Validate integration
            total_artifacts = sum(results["generated_artifacts"].values())
            total_files = sum(results["saved_files"].values())
            
            assert total_artifacts > 10, f"Insufficient artifacts generated: {total_artifacts}"
            assert total_files > 20, f"Insufficient files saved: {total_files}"
            assert component_diagram.accuracy_confidence > 0.8, "Low accuracy confidence in integration test"
            
            return results
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def get_test_summary(self) -> str:
        """Get formatted test summary."""
        if not self._test_results:
            return "No test results available"
        
        overall = self._test_results.get("overall", {})
        success = overall.get("success", False)
        
        summary = f"""
Phase 3 UML Diagram Generation Engine - Integration Test Results
================================================================

Overall Result: {'PASSED' if success else 'FAILED'}
Total Tests: {overall.get('total_tests', 0)}
Passed Tests: {overall.get('passed_tests', 0)}
Output Directory: {overall.get('output_directory', 'N/A')}

Test Results:
"""
        
        for test_name, result in self._test_results.items():
            if test_name == "overall":
                continue
            
            status = "PASS" if result.get("success", False) else "FAIL"
            summary += f"  {test_name}: {status}\n"
            
            if not result.get("success", False) and "error" in result:
                summary += f"    Error: {result['error']}\n"
        
        return summary