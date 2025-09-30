"""
Comprehensive test suite for System Architecture Wiring Diagram components.

This module implements comprehensive unit tests, integration tests, and end-to-end
validation testing for all components of the system architecture documentation system.
"""

import asyncio
import json
import pytest
import tempfile
from datetime import datetime
from pathlib import Path
from unittest.mock import Mock, patch, AsyncMock

from src.beast_mode.observatory.infrastructure_discovery import (
    InfrastructureDiscoverer, ObservatoryWebSocketClient, ServiceInfo, NetworkTopology
)
from src.beast_mode.observatory.makefile_analyzer import (
    MakefileAnalyzer, MakefileAnalysis, MakefileTarget, TargetCategory, InfrastructureEffect
)
from src.beast_mode.observatory.cloudflare_tunnel_discovery import (
    CloudflareTunnelDiscoverer, CloudflareTunnel, TunnelDiscoveryResult, TunnelStatus
)
from src.beast_mode.observatory.network_topology_discovery import (
    NetworkTopologyDiscoverer, NetworkTopology as NetTopology, ServiceEndpoint, ServiceStatus
)
from src.beast_mode.observatory.diagram_generator import (
    DiagramGenerator, DiagramGenerationResult, DiagramType, GeneratedDiagram
)
from src.beast_mode.observatory.documentation_orchestrator import (
    DocumentationOrchestrator, DocumentationPackage, ValidationStatus, DocumentationType
)


class TestInfrastructureDiscovery:
    """Test suite for Infrastructure Discovery Engine."""
    
    @pytest.fixture
    def infrastructure_discoverer(self):
        """Create InfrastructureDiscoverer instance for testing."""
        return InfrastructureDiscoverer(None)
    
    @pytest.fixture
    def websocket_client(self):
        """Create ObservatoryWebSocketClient instance for testing."""
        return ObservatoryWebSocketClient("ws://localhost:8888")
    
    def test_service_info_creation(self):
        """Test ServiceInfo creation and validation."""
        service = ServiceInfo(
            name="test_service",
            process_id=12345,
            port=8080,
            health_endpoint="/health"
        )
        
        assert service.name == "test_service"
        assert service.process_id == 12345
        assert service.port == 8080
        assert service.health_endpoint == "/health"
        assert service.validation_status.value == "pending"
    
    def test_network_topology_creation(self):
        """Test NetworkTopology creation."""
        topology = NetworkTopology()
        
        assert len(topology.services) == 0
        assert len(topology.connections) == 0
        assert topology.validation_status.value == "pending"
        assert topology.accuracy_score == 0.0
    
    @pytest.mark.asyncio
    async def test_websocket_client_initialization(self, websocket_client):
        """Test ObservatoryWebSocketClient initialization."""
        assert websocket_client.base_url == "ws://localhost:8888"
        assert len(websocket_client.endpoints) == 4
        assert "/ws/observatory" in websocket_client.endpoints
        assert "/ws/anomalies" in websocket_client.endpoints
        assert "/ws/emoji-rain" in websocket_client.endpoints
        assert "/ws/doctor-status" in websocket_client.endpoints
    
    @pytest.mark.asyncio
    async def test_infrastructure_discoverer_initialization(self, infrastructure_discoverer):
        """Test InfrastructureDiscoverer initialization."""
        assert infrastructure_discoverer.module_id == "infrastructure_discoverer"
        assert infrastructure_discoverer._websocket_client is not None
        assert infrastructure_discoverer._discovered_services == {}
    
    @pytest.mark.asyncio
    @patch('src.beast_mode.observatory.infrastructure_discovery.psutil.process_iter')
    async def test_discover_running_services(self, mock_process_iter, infrastructure_discoverer):
        """Test discovery of running services."""
        # Mock process information
        mock_process = Mock()
        mock_process.info = {
            'pid': 12345,
            'name': 'observatory-server',
            'cmdline': ['python', 'observatory-daemon.py'],
            'connections': [Mock(status='LISTEN', laddr=Mock(port=8888))]
        }
        mock_process_iter.return_value = [mock_process]
        
        services = await infrastructure_discoverer._discover_running_services()
        
        assert len(services) > 0
        assert any('observatory' in service_name for service_name in services.keys())
    
    @pytest.mark.asyncio
    @patch('src.beast_mode.observatory.infrastructure_discovery.psutil.net_connections')
    async def test_discover_network_topology(self, mock_net_connections, infrastructure_discoverer):
        """Test network topology discovery."""
        # Mock network connections
        mock_conn = Mock()
        mock_conn.status = 'LISTEN'
        mock_conn.laddr = Mock()
        mock_conn.laddr.ip = '127.0.0.1'
        mock_conn.laddr.port = 8888
        mock_conn.raddr = None
        mock_net_connections.return_value = [mock_conn]
        
        topology = await infrastructure_discoverer._discover_network_topology()
        
        assert topology is not None
        assert len(topology.connections) > 0
        assert topology.validation_status.value == "valid"


class TestMakefileAnalyzer:
    """Test suite for Makefile Analyzer."""
    
    @pytest.fixture
    def makefile_analyzer(self):
        """Create MakefileAnalyzer instance for testing."""
        return MakefileAnalyzer()
    
    @pytest.fixture
    def sample_makefile_content(self):
        """Sample Makefile content for testing."""
        return """
# Test Makefile
.PHONY: help install deploy verify test clean

help:
	@echo "Available commands:"
	@echo "  make install     - Install dependencies"
	@echo "  make deploy      - Deploy application"
	@echo "  make verify      - Verify deployment"
	@echo "  make test        - Run tests"
	@echo "  make clean       - Clean up"

install:
	@echo "Installing dependencies..."
	pip install -r requirements.txt

deploy:
	@echo "Deploying application..."
	python deploy.py

verify:
	@echo "Verifying deployment..."
	python verify.py

test:
	@echo "Running tests..."
	pytest tests/

clean:
	@echo "Cleaning up..."
	rm -rf __pycache__/
	rm -rf .pytest_cache/
"""
    
    def test_makefile_target_creation(self):
        """Test MakefileTarget creation."""
        target = MakefileTarget(
            name="deploy",
            dependencies=["install"],
            commands=["python deploy.py"],
            category=TargetCategory.DEPLOYMENT,
            affected_components=[InfrastructureEffect.OBSERVATORY_SERVER]
        )
        
        assert target.name == "deploy"
        assert "install" in target.dependencies
        assert "python deploy.py" in target.commands
        assert target.category == TargetCategory.DEPLOYMENT
        assert InfrastructureEffect.OBSERVATORY_SERVER in target.affected_components
    
    def test_makefile_analysis_creation(self):
        """Test MakefileAnalysis creation."""
        analysis = MakefileAnalysis()
        
        assert len(analysis.targets) == 0
        assert len(analysis.dependency_graph) == 0
        assert len(analysis.execution_chains) == 0
        assert analysis.total_targets == 0
        assert analysis.complexity_score == 0.0
    
    @pytest.mark.asyncio
    async def test_makefile_analyzer_initialization(self, makefile_analyzer):
        """Test MakefileAnalyzer initialization."""
        assert makefile_analyzer.module_id == "makefile_analyzer"
        assert len(makefile_analyzer._category_patterns) > 0
        assert len(makefile_analyzer._infrastructure_patterns) > 0
    
    @pytest.mark.asyncio
    async def test_extract_targets(self, makefile_analyzer, sample_makefile_content):
        """Test Makefile target extraction."""
        targets = await makefile_analyzer._extract_targets(sample_makefile_content)
        
        assert len(targets) > 0
        assert "help" in targets
        assert "install" in targets
        assert "deploy" in targets
        assert "verify" in targets
        assert "test" in targets
        assert "clean" in targets
        
        # Check target properties
        deploy_target = targets["deploy"]
        assert len(deploy_target.commands) > 0
        assert deploy_target.category == TargetCategory.DEPLOYMENT
    
    def test_categorize_target(self, makefile_analyzer):
        """Test target categorization."""
        assert makefile_analyzer._categorize_target("deploy") == TargetCategory.DEPLOYMENT
        assert makefile_analyzer._categorize_target("test") == TargetCategory.TESTING
        assert makefile_analyzer._categorize_target("clean") == TargetCategory.CLEANUP
        assert makefile_analyzer._categorize_target("help") == TargetCategory.INFO
    
    def test_map_target_infrastructure_effects(self, makefile_analyzer):
        """Test infrastructure effect mapping."""
        commands = ["python observatory-daemon.py"]
        effects = makefile_analyzer._map_target_infrastructure_effects("dashboard-up", commands)
        
        assert InfrastructureEffect.OBSERVATORY_SERVER in effects
        assert InfrastructureEffect.WEBSOCKET_ENDPOINTS in effects
    
    def test_assess_target_risk(self, makefile_analyzer):
        """Test target risk assessment."""
        assert makefile_analyzer._assess_target_risk("clean", ["rm -rf /"]) == "high"
        assert makefile_analyzer._assess_target_risk("deploy", ["python deploy.py"]) == "medium"
        assert makefile_analyzer._assess_target_risk("help", ["echo 'help'"]) == "low"


class TestCloudflareTunnelDiscovery:
    """Test suite for Cloudflare Tunnel Discovery."""
    
    @pytest.fixture
    def tunnel_discoverer(self):
        """Create CloudflareTunnelDiscoverer instance for testing."""
        return CloudflareTunnelDiscoverer()
    
    def test_cloudflare_tunnel_creation(self):
        """Test CloudflareTunnel creation."""
        tunnel = CloudflareTunnel(
            tunnel_id="test-tunnel-id",
            name="test_tunnel",
            status=TunnelStatus.ACTIVE
        )
        
        assert tunnel.tunnel_id == "test-tunnel-id"
        assert tunnel.name == "test_tunnel"
        assert tunnel.status == TunnelStatus.ACTIVE
        assert tunnel.is_valid is True
    
    def test_tunnel_discovery_result_creation(self):
        """Test TunnelDiscoveryResult creation."""
        result = TunnelDiscoveryResult()
        
        assert len(result.tunnels) == 0
        assert len(result.dns_records) == 0
        assert len(result.routing_rules) == 0
        assert result.total_tunnels == 0
        assert result.active_tunnels == 0
    
    @pytest.mark.asyncio
    async def test_tunnel_discoverer_initialization(self, tunnel_discoverer):
        """Test CloudflareTunnelDiscoverer initialization."""
        assert tunnel_discoverer.module_id == "cloudflare_tunnel_discoverer"
        assert tunnel_discoverer._known_tunnel_id == "d1e53e43-033f-4994-8f46-c83962ae3785"
        assert len(tunnel_discoverer._known_domains) == 3
        assert len(tunnel_discoverer._websocket_endpoints) == 4
    
    @pytest.mark.asyncio
    async def test_create_known_tunnel_entry(self, tunnel_discoverer):
        """Test creation of known tunnel entry."""
        tunnel_discoverer._discovery_result = TunnelDiscoveryResult()
        await tunnel_discoverer._create_known_tunnel_entry()
        
        assert tunnel_discoverer._known_tunnel_id in tunnel_discoverer._discovery_result.tunnels
        tunnel = tunnel_discoverer._discovery_result.tunnels[tunnel_discoverer._known_tunnel_id]
        assert tunnel.name == "observatory_tunnel"
        assert tunnel.status == TunnelStatus.ACTIVE
        assert len(tunnel.ingress_rules) == 3  # One for each known domain
    
    @pytest.mark.asyncio
    async def test_discover_dns_records(self, tunnel_discoverer):
        """Test DNS record discovery."""
        tunnel_discoverer._discovery_result = TunnelDiscoveryResult()
        await tunnel_discoverer._discover_dns_records()
        
        assert len(tunnel_discoverer._discovery_result.dns_records) == 3
        domains = [record.domain for record in tunnel_discoverer._discovery_result.dns_records]
        assert "observatory.nkllon.com" in domains
        assert "grafana.observatory.nkllon.com" in domains
        assert "prometheus.observatory.nkllon.com" in domains


class TestNetworkTopologyDiscovery:
    """Test suite for Network Topology Discovery."""
    
    @pytest.fixture
    def network_discoverer(self):
        """Create NetworkTopologyDiscoverer instance for testing."""
        return NetworkTopologyDiscoverer()
    
    def test_service_endpoint_creation(self):
        """Test ServiceEndpoint creation."""
        endpoint = ServiceEndpoint(
            service_name="test_service",
            host="localhost",
            port=8080,
            protocol="tcp"
        )
        
        assert endpoint.service_name == "test_service"
        assert endpoint.host == "localhost"
        assert endpoint.port == 8080
        assert endpoint.status == ServiceStatus.UNKNOWN
    
    def test_network_topology_creation(self):
        """Test NetworkTopology creation."""
        topology = NetTopology()
        
        assert len(topology.interfaces) == 0
        assert len(topology.service_endpoints) == 0
        assert len(topology.network_connections) == 0
        assert topology.total_services == 0
        assert topology.active_connections == 0
    
    @pytest.mark.asyncio
    async def test_network_discoverer_initialization(self, network_discoverer):
        """Test NetworkTopologyDiscoverer initialization."""
        assert network_discoverer.module_id == "network_topology_discoverer"
        assert len(network_discoverer._known_endpoints) == 3
        assert len(network_discoverer._known_redis_endpoints) == 2
        assert len(network_discoverer._websocket_endpoints) == 4
    
    def test_identify_service_by_port(self, network_discoverer):
        """Test service identification by port."""
        assert network_discoverer._identify_service_by_port(22) == "ssh"
        assert network_discoverer._identify_service_by_port(80) == "http"
        assert network_discoverer._identify_service_by_port(443) == "https"
        assert network_discoverer._identify_service_by_port(3000) == "grafana"
        assert network_discoverer._identify_service_by_port(8888) == "observatory"
        assert network_discoverer._identify_service_by_port(9090) == "prometheus"
        assert network_discoverer._identify_service_by_port(9999) == "service-9999"
    
    def test_determine_interface_type(self, network_discoverer):
        """Test interface type determination."""
        assert network_discoverer._determine_interface_type("lo0") == "loopback"
        assert network_discoverer._determine_interface_type("eth0") == "ethernet"
        assert network_discoverer._determine_interface_type("wlan0") == "wifi"
        assert network_discoverer._determine_interface_type("docker0") == "docker"
        assert network_discoverer._determine_interface_type("unknown0") == "unknown"


class TestDiagramGenerator:
    """Test suite for Diagram Generator."""
    
    @pytest.fixture
    def diagram_generator(self):
        """Create DiagramGenerator instance for testing."""
        return DiagramGenerator()
    
    def test_generated_diagram_creation(self):
        """Test GeneratedDiagram creation."""
        from src.beast_mode.observatory.diagram_generator import DiagramMetadata
        
        metadata = DiagramMetadata(
            diagram_id="test_diagram",
            diagram_type=DiagramType.COMPONENT,
            title="Test Diagram",
            description="Test diagram description"
        )
        
        diagram = GeneratedDiagram(
            metadata=metadata,
            plantuml_source="@startuml\ntest\n@enduml",
            mermaid_source="graph TB\nA[Test]\n"
        )
        
        assert diagram.metadata.diagram_id == "test_diagram"
        assert diagram.metadata.diagram_type == DiagramType.COMPONENT
        assert diagram.plantuml_source == "@startuml\ntest\n@enduml"
        assert diagram.mermaid_source == "graph TB\nA[Test]\n"
    
    def test_diagram_generation_result_creation(self):
        """Test DiagramGenerationResult creation."""
        result = DiagramGenerationResult()
        
        assert len(result.diagrams) == 0
        assert result.total_diagrams == 0
        assert result.successful_generations == 0
        assert result.failed_generations == 0
        assert result.validation_success_rate == 0.0
    
    @pytest.mark.asyncio
    async def test_diagram_generator_initialization(self, diagram_generator):
        """Test DiagramGenerator initialization."""
        assert diagram_generator.module_id == "diagram_generator"
        assert diagram_generator._output_directory.exists()
        assert diagram_generator._component_template is not None
        assert diagram_generator._sequence_template is not None
        assert diagram_generator._network_template is not None
    
    @pytest.mark.asyncio
    async def test_create_diagram(self, diagram_generator):
        """Test diagram creation."""
        diagram = await diagram_generator._create_diagram(
            diagram_id="test_diagram",
            diagram_type=DiagramType.COMPONENT,
            title="Test Diagram",
            description="Test diagram description",
            plantuml_source="@startuml\ntest\n@enduml",
            mermaid_source="graph TB\nA[Test]\n"
        )
        
        assert diagram.metadata.diagram_id == "test_diagram"
        assert diagram.metadata.diagram_type == DiagramType.COMPONENT
        assert diagram.plantuml_file is not None
        assert diagram.mermaid_file is not None
        
        # Check that files were created
        assert Path(diagram.plantuml_file).exists()
        assert Path(diagram.mermaid_file).exists()


class TestDocumentationOrchestrator:
    """Test suite for Documentation Orchestrator."""
    
    @pytest.fixture
    def documentation_orchestrator(self):
        """Create DocumentationOrchestrator instance for testing."""
        return DocumentationOrchestrator()
    
    def test_documentation_package_creation(self):
        """Test DocumentationPackage creation."""
        package = DocumentationPackage(package_id="test_package")
        
        assert package.package_id == "test_package"
        assert package.version == "1.0.0"
        assert len(package.validation_results) == 0
        assert package.overall_accuracy_score == 0.0
        assert package.validation_success_rate == 0.0
    
    def test_validation_result_creation(self):
        """Test ValidationResult creation."""
        result = ValidationResult(
            documentation_type=DocumentationType.INFRASTRUCTURE_DISCOVERY,
            validation_status=ValidationStatus.VALID,
            accuracy_score=0.95
        )
        
        assert result.documentation_type == DocumentationType.INFRASTRUCTURE_DISCOVERY
        assert result.validation_status == ValidationStatus.VALID
        assert result.accuracy_score == 0.95
        assert result.requires_manual_verification is False
    
    @pytest.mark.asyncio
    async def test_documentation_orchestrator_initialization(self, documentation_orchestrator):
        """Test DocumentationOrchestrator initialization."""
        assert documentation_orchestrator.module_id == "documentation_orchestrator"
        assert documentation_orchestrator._validation_interval_hours == 24
        assert documentation_orchestrator._staleness_threshold_hours == 24
        assert documentation_orchestrator._accuracy_threshold == 0.95
        assert len(documentation_orchestrator._validation_checklists) > 0
    
    def test_get_validation_checklist(self, documentation_orchestrator):
        """Test getting validation checklist."""
        checklist = documentation_orchestrator.get_validation_checklist(DocumentationType.INFRASTRUCTURE_DISCOVERY)
        
        assert checklist is not None
        assert checklist.documentation_type == DocumentationType.INFRASTRUCTURE_DISCOVERY
        assert len(checklist.checklist_items) > 0
        assert len(checklist.automated_tests) > 0
        assert len(checklist.manual_verification_steps) > 0
        assert len(checklist.success_criteria) > 0
    
    @pytest.mark.asyncio
    async def test_validate_documentation_accuracy(self, documentation_orchestrator):
        """Test documentation accuracy validation."""
        # Create mock documentation package
        package = DocumentationPackage(package_id="test_package")
        package.validation_results = {
            DocumentationType.INFRASTRUCTURE_DISCOVERY: ValidationResult(
                documentation_type=DocumentationType.INFRASTRUCTURE_DISCOVERY,
                validation_status=ValidationStatus.VALID,
                accuracy_score=0.95
            )
        }
        package.overall_accuracy_score = 0.95
        package.validation_success_rate = 1.0
        
        documentation_orchestrator._documentation_package = package
        
        validation_result = await documentation_orchestrator.validate_documentation_accuracy()
        
        assert "validation_results" in validation_result
        assert "overall_accuracy_score" in validation_result
        assert "validation_success_rate" in validation_result
        assert validation_result["overall_accuracy_score"] == 0.95
        assert validation_result["validation_success_rate"] == 1.0


class TestIntegrationTests:
    """Integration tests for the complete system."""
    
    @pytest.mark.asyncio
    async def test_end_to_end_documentation_generation(self):
        """Test end-to-end documentation generation."""
        orchestrator = DocumentationOrchestrator()
        
        # Mock the discovery components to avoid external dependencies
        with patch('src.beast_mode.observatory.documentation_orchestrator.InfrastructureDiscoverer') as mock_infra, \
             patch('src.beast_mode.observatory.documentation_orchestrator.MakefileAnalyzer') as mock_makefile, \
             patch('src.beast_mode.observatory.documentation_orchestrator.CloudflareTunnelDiscoverer') as mock_tunnel, \
             patch('src.beast_mode.observatory.documentation_orchestrator.NetworkTopologyDiscoverer') as mock_network, \
             patch('src.beast_mode.observatory.documentation_orchestrator.DiagramGenerator') as mock_diagram:
            
            # Setup mocks
            mock_infra_instance = AsyncMock()
            mock_infra_instance.start_discovery.return_value = True
            mock_infra_instance.get_discovered_services.return_value = {"test_service": Mock()}
            mock_infra_instance.get_network_topology.return_value = Mock()
            mock_infra_instance.get_configuration_map.return_value = Mock()
            mock_infra_instance.get_script_registry.return_value = Mock()
            mock_infra.return_value = mock_infra_instance
            
            mock_makefile_instance = AsyncMock()
            mock_makefile_instance.analyze_makefile.return_value = Mock()
            mock_makefile.return_value = mock_makefile_instance
            
            mock_tunnel_instance = AsyncMock()
            mock_tunnel_instance.discover_tunnels.return_value = Mock()
            mock_tunnel.return_value = mock_tunnel_instance
            
            mock_network_instance = AsyncMock()
            mock_network_instance.discover_topology.return_value = Mock()
            mock_network.return_value = mock_network_instance
            
            mock_diagram_instance = AsyncMock()
            mock_diagram_instance.generate_all_diagrams.return_value = Mock()
            mock_diagram.return_value = mock_diagram_instance
            
            # Run the test
            package = await orchestrator.generate_complete_documentation()
            
            assert package is not None
            assert package.package_id is not None
            assert package.generation_time_seconds > 0
            assert len(package.validation_results) > 0
    
    @pytest.mark.asyncio
    async def test_makefile_analysis_integration(self):
        """Test Makefile analysis integration."""
        analyzer = MakefileAnalyzer()
        
        # Create a temporary Makefile for testing
        with tempfile.NamedTemporaryFile(mode='w', suffix='.mk', delete=False) as f:
            f.write("""
help:
	@echo "Help message"

deploy:
	@echo "Deploying..."
	python deploy.py

test:
	@echo "Testing..."
	pytest tests/
""")
            temp_makefile = Path(f.name)
        
        try:
            analysis = await analyzer.analyze_makefile(temp_makefile)
            
            assert analysis is not None
            assert analysis.total_targets > 0
            assert "help" in analysis.targets
            assert "deploy" in analysis.targets
            assert "test" in analysis.targets
            
            # Check target categorization
            assert analysis.targets["deploy"].category == TargetCategory.DEPLOYMENT
            assert analysis.targets["test"].category == TargetCategory.TESTING
            
        finally:
            temp_makefile.unlink()


class TestPerformanceTests:
    """Performance tests for the system."""
    
    @pytest.mark.asyncio
    async def test_documentation_generation_performance(self):
        """Test documentation generation performance."""
        orchestrator = DocumentationOrchestrator()
        
        start_time = datetime.now()
        
        # Mock all external dependencies for performance testing
        with patch('src.beast_mode.observatory.documentation_orchestrator.InfrastructureDiscoverer') as mock_infra, \
             patch('src.beast_mode.observatory.documentation_orchestrator.MakefileAnalyzer') as mock_makefile, \
             patch('src.beast_mode.observatory.documentation_orchestrator.CloudflareTunnelDiscoverer') as mock_tunnel, \
             patch('src.beast_mode.observatory.documentation_orchestrator.NetworkTopologyDiscoverer') as mock_network, \
             patch('src.beast_mode.observatory.documentation_orchestrator.DiagramGenerator') as mock_diagram:
            
            # Setup fast mocks
            for mock_class in [mock_infra, mock_makefile, mock_tunnel, mock_network, mock_diagram]:
                mock_instance = AsyncMock()
                mock_instance.start_discovery.return_value = True
                mock_instance.analyze_makefile.return_value = Mock()
                mock_instance.discover_tunnels.return_value = Mock()
                mock_instance.discover_topology.return_value = Mock()
                mock_instance.generate_all_diagrams.return_value = Mock()
                mock_class.return_value = mock_instance
            
            package = await orchestrator.generate_complete_documentation()
            
            end_time = datetime.now()
            generation_time = (end_time - start_time).total_seconds()
            
            # Performance assertions
            assert generation_time < 10.0  # Should complete within 10 seconds
            assert package.generation_time_seconds < 10.0
            assert package is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])