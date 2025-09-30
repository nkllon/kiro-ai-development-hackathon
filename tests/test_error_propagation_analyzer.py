"""
Comprehensive Unit Tests for Error Propagation Analyzer.

This module provides comprehensive unit tests for the ErrorPropagationAnalyzer
with >90% test coverage, testing all error propagation analysis functionality,
correlation ID tracking, recovery procedures, fallback mechanisms, emergency
protocols, and error classifications.
"""

import asyncio
import json
import pytest
import time
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

from src.system_architecture.analysis.error_propagation_analyzer import (
    ErrorPropagationAnalyzer, ErrorPropagationConfig
)
from src.system_architecture.models.error_propagation import (
    ErrorPropagationGraph, ErrorPropagationPath, CorrelationIDMapping,
    ErrorRecoveryProcedure, FallbackMechanism, EmergencyProtocol,
    ErrorClassification, ErrorSeverity, ErrorCategory, FallbackType
)


class TestErrorPropagationConfig:
    """Test ErrorPropagationConfig functionality."""
    
    def test_config_default_values(self):
        """Test default configuration values."""
        config = ErrorPropagationConfig()
        
        assert config.enable_real_time_analysis is True
        assert config.enable_correlation_tracking is True
        assert config.enable_recovery_mapping is True
        assert config.enable_fallback_monitoring is True
        assert config.analysis_interval_seconds == 60
        assert config.correlation_timeout_seconds == 3600
        assert config.observatory_endpoint == "http://localhost:8888"
        assert config.prometheus_endpoint == "http://localhost:9090"
        assert len(config.websocket_endpoints) == 4
        assert "/ws/observatory" in config.websocket_endpoints
        assert "/ws/anomalies" in config.websocket_endpoints
        assert "/ws/emoji-rain" in config.websocket_endpoints
        assert "/ws/doctor-status" in config.websocket_endpoints
    
    def test_config_custom_values(self):
        """Test custom configuration values."""
        config = ErrorPropagationConfig(
            enable_real_time_analysis=False,
            analysis_interval_seconds=120,
            websocket_endpoints=["/ws/custom"]
        )
        
        assert config.enable_real_time_analysis is False
        assert config.analysis_interval_seconds == 120
        assert config.websocket_endpoints == ["/ws/custom"]


class TestErrorPropagationAnalyzer:
    """Test ErrorPropagationAnalyzer functionality."""
    
    @pytest.fixture
    def analyzer(self):
        """Create ErrorPropagationAnalyzer instance for testing."""
        config = ErrorPropagationConfig(
            enable_real_time_analysis=False,  # Disable for testing
            analysis_interval_seconds=1
        )
        return ErrorPropagationAnalyzer(config)
    
    @pytest.fixture
    def mock_infrastructure_discoverer(self):
        """Create mock infrastructure discoverer."""
        discoverer = AsyncMock()
        discoverer.start_discovery = AsyncMock(return_value=True)
        discoverer.stop_discovery = AsyncMock()
        discoverer.get_discovered_services = MagicMock(return_value={
            "observatory": MagicMock(name="Observatory", port=8888),
            "prometheus": MagicMock(name="Prometheus", port=9090),
            "grafana": MagicMock(name="Grafana", port=3000)
        })
        return discoverer
    
    @pytest.fixture
    def mock_websocket_client(self):
        """Create mock WebSocket client."""
        client = AsyncMock()
        client.connect_to_endpoints = AsyncMock()
        client.disconnect = AsyncMock()
        return client
    
    def test_analyzer_initialization(self, analyzer):
        """Test analyzer initialization."""
        assert analyzer.module_id == "error_propagation_analyzer"
        assert analyzer._config is not None
        assert analyzer._analysis_active is False
        assert analyzer._error_propagation_graph is None
        assert analyzer._paths_analyzed == 0
        assert analyzer._analysis_errors == 0
    
    def test_analyzer_capabilities(self, analyzer):
        """Test analyzer capabilities."""
        capabilities = analyzer.get_capabilities()
        assert len(capabilities) == 3
        assert any(cap.value == "monitoring" for cap in capabilities)
        assert any(cap.value == "data_processing" for cap in capabilities)
        assert any(cap.value == "validation" for cap in capabilities)
    
    def test_analyzer_module_info(self, analyzer):
        """Test analyzer module information."""
        info = analyzer.get_module_info()
        
        assert info["module_id"] == "error_propagation_analyzer"
        assert info["name"] == "Comprehensive Error Propagation Analyzer"
        assert info["version"] == "1.0.0"
        assert "Error Propagation" in info["description"]
        assert "config" in info
        assert info["config"]["real_time_analysis"] is False
    
    def test_analyzer_health_status_inactive(self, analyzer):
        """Test analyzer health status when inactive."""
        health = analyzer.get_health_status()
        
        assert health.module_id == "error_propagation_analyzer"
        assert health.status.value == "error"
        assert health.health_score == 0.0
        assert "not active" in health.issues[0]
        assert health.error_count == 0
        assert health.warning_count == 0
    
    @pytest.mark.asyncio
    async def test_start_analysis_success(self, analyzer, mock_infrastructure_discoverer, mock_websocket_client):
        """Test successful analysis start."""
        with patch('src.system_architecture.analysis.error_propagation_analyzer.InfrastructureDiscoverer', return_value=mock_infrastructure_discoverer), \
             patch('src.system_architecture.analysis.error_propagation_analyzer.ObservatoryWebSocketClient', return_value=mock_websocket_client):
            
            result = await analyzer.start_analysis()
            
            assert result is True
            assert analyzer._analysis_active is True
            assert analyzer._error_propagation_graph is not None
            assert analyzer._infrastructure_discoverer is not None
            assert analyzer._websocket_client is not None
            assert analyzer._analysis_task is not None
    
    @pytest.mark.asyncio
    async def test_start_analysis_already_active(self, analyzer):
        """Test starting analysis when already active."""
        analyzer._analysis_active = True
        
        result = await analyzer.start_analysis()
        
        assert result is True
    
    @pytest.mark.asyncio
    async def test_start_analysis_failure(self, analyzer):
        """Test analysis start failure."""
        with patch('src.system_architecture.analysis.error_propagation_analyzer.InfrastructureDiscoverer', side_effect=Exception("Test error")):
            result = await analyzer.start_analysis()
            
            assert result is False
            assert analyzer._analysis_active is False
    
    @pytest.mark.asyncio
    async def test_stop_analysis(self, analyzer):
        """Test analysis stop."""
        analyzer._analysis_active = True
        analyzer._analysis_task = AsyncMock()
        analyzer._infrastructure_discoverer = AsyncMock()
        analyzer._websocket_client = AsyncMock()
        
        await analyzer.stop_analysis()
        
        assert analyzer._analysis_active is False
        analyzer._analysis_task.cancel.assert_called_once()
        analyzer._infrastructure_discoverer.stop_discovery.assert_called_once()
        analyzer._websocket_client.disconnect.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_perform_comprehensive_analysis(self, analyzer):
        """Test comprehensive analysis performance."""
        analyzer._error_propagation_graph = ErrorPropagationGraph(
            graph_id=str(uuid4()),
            graph_name="Test Graph"
        )
        
        # Mock the individual analysis methods
        analyzer._map_error_propagation_paths = AsyncMock()
        analyzer._track_correlation_ids = AsyncMock()
        analyzer._map_recovery_procedures = AsyncMock()
        analyzer._map_fallback_mechanisms = AsyncMock()
        analyzer._map_emergency_protocols = AsyncMock()
        analyzer._create_error_classifications = AsyncMock()
        analyzer._update_graph_metadata = MagicMock()
        
        await analyzer._perform_comprehensive_analysis()
        
        assert analyzer._paths_analyzed == 1
        analyzer._map_error_propagation_paths.assert_called_once()
        analyzer._track_correlation_ids.assert_called_once()
        analyzer._map_recovery_procedures.assert_called_once()
        analyzer._map_fallback_mechanisms.assert_called_once()
        analyzer._map_emergency_protocols.assert_called_once()
        analyzer._create_error_classifications.assert_called_once()
        analyzer._update_graph_metadata.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_map_error_propagation_paths(self, analyzer):
        """Test error propagation path mapping."""
        analyzer._error_propagation_graph = ErrorPropagationGraph(
            graph_id=str(uuid4()),
            graph_name="Test Graph"
        )
        
        await analyzer._map_error_propagation_paths()
        
        assert len(analyzer._error_propagation_graph.propagation_paths) == 4
        assert analyzer._error_propagation_graph.total_paths == 4
        
        # Check specific paths
        paths = analyzer._error_propagation_graph.propagation_paths
        assert any("reflective_module" in path_id for path_id in paths.keys())
        assert any("websocket" in path_id for path_id in paths.keys())
        assert any("redis" in path_id for path_id in paths.keys())
        assert any("cloudflare" in path_id for path_id in paths.keys())
    
    @pytest.mark.asyncio
    async def test_track_correlation_ids(self, analyzer):
        """Test correlation ID tracking."""
        analyzer._error_propagation_graph = ErrorPropagationGraph(
            graph_id=str(uuid4()),
            graph_name="Test Graph"
        )
        
        await analyzer._track_correlation_ids()
        
        assert len(analyzer._error_propagation_graph.correlation_mappings) == 3
        assert analyzer._error_propagation_graph.total_correlations == 3
        
        # Check specific correlations
        correlations = analyzer._error_propagation_graph.correlation_mappings
        assert any("ReflectiveModule" in mapping.primary_component for mapping in correlations.values())
        assert any("WebSocket" in mapping.primary_component for mapping in correlations.values())
        assert any("Redis" in mapping.primary_component for mapping in correlations.values())
    
    @pytest.mark.asyncio
    async def test_map_recovery_procedures(self, analyzer):
        """Test recovery procedure mapping."""
        analyzer._error_propagation_graph = ErrorPropagationGraph(
            graph_id=str(uuid4()),
            graph_name="Test Graph"
        )
        
        await analyzer._map_recovery_procedures()
        
        assert len(analyzer._error_propagation_graph.recovery_procedures) == 3
        assert analyzer._error_propagation_graph.total_procedures == 3
        
        # Check specific procedures
        procedures = analyzer._error_propagation_graph.recovery_procedures
        assert any("reflective_module" in proc_id for proc_id in procedures.keys())
        assert any("websocket" in proc_id for proc_id in procedures.keys())
        assert any("redis" in proc_id for proc_id in procedures.keys())
    
    @pytest.mark.asyncio
    async def test_map_fallback_mechanisms(self, analyzer):
        """Test fallback mechanism mapping."""
        analyzer._error_propagation_graph = ErrorPropagationGraph(
            graph_id=str(uuid4()),
            graph_name="Test Graph"
        )
        
        await analyzer._map_fallback_mechanisms()
        
        assert len(analyzer._error_propagation_graph.fallback_mechanisms) == 3
        assert analyzer._error_propagation_graph.total_fallbacks == 3
        
        # Check specific mechanisms
        mechanisms = analyzer._error_propagation_graph.fallback_mechanisms
        assert any("redis" in mech_id for mech_id in mechanisms.keys())
        assert any("websocket" in mech_id for mech_id in mechanisms.keys())
        assert any("service" in mech_id for mech_id in mechanisms.keys())
    
    @pytest.mark.asyncio
    async def test_map_emergency_protocols(self, analyzer):
        """Test emergency protocol mapping."""
        analyzer._error_propagation_graph = ErrorPropagationGraph(
            graph_id=str(uuid4()),
            graph_name="Test Graph"
        )
        
        await analyzer._map_emergency_protocols()
        
        assert len(analyzer._error_propagation_graph.emergency_protocols) == 3
        assert analyzer._error_propagation_graph.total_protocols == 3
        
        # Check specific protocols
        protocols = analyzer._error_propagation_graph.emergency_protocols
        assert any("critical_system" in proto_id for proto_id in protocols.keys())
        assert any("data_loss" in proto_id for proto_id in protocols.keys())
        assert any("security" in proto_id for proto_id in protocols.keys())
    
    @pytest.mark.asyncio
    async def test_create_error_classifications(self, analyzer):
        """Test error classification creation."""
        analyzer._error_propagation_graph = ErrorPropagationGraph(
            graph_id=str(uuid4()),
            graph_name="Test Graph"
        )
        
        await analyzer._create_error_classifications()
        
        assert len(analyzer._error_propagation_graph.error_classifications) == 3
        assert analyzer._error_propagation_graph.total_classifications == 3
        
        # Check specific classifications
        classifications = analyzer._error_propagation_graph.error_classifications
        assert any("systematic" in class_id for class_id in classifications.keys())
        assert any("network" in class_id for class_id in classifications.keys())
        assert any("resource" in class_id for class_id in classifications.keys())
    
    def test_update_graph_metadata(self, analyzer):
        """Test graph metadata update."""
        analyzer._error_propagation_graph = ErrorPropagationGraph(
            graph_id=str(uuid4()),
            graph_name="Test Graph"
        )
        
        # Add some test data
        analyzer._error_propagation_graph.add_propagation_path(
            ErrorPropagationPath(
                path_id="test_path",
                source_component="test_source",
                target_components=["test_target"],
                propagation_steps=["step1", "step2"],
                error_types=["test_error"],
                severity_levels=[ErrorSeverity.ERROR]
            )
        )
        
        analyzer._update_graph_metadata()
        
        assert analyzer._error_propagation_graph.complexity_score > 0
        assert analyzer._error_propagation_graph.accuracy_score == 0.95
        assert analyzer._error_propagation_graph.validation_status == "valid"
    
    def test_get_error_propagation_graph(self, analyzer):
        """Test getting error propagation graph."""
        assert analyzer.get_error_propagation_graph() is None
        
        analyzer._error_propagation_graph = ErrorPropagationGraph(
            graph_id=str(uuid4()),
            graph_name="Test Graph"
        )
        
        graph = analyzer.get_error_propagation_graph()
        assert graph is not None
        assert graph.graph_name == "Test Graph"
    
    def test_get_analysis_summary_no_graph(self, analyzer):
        """Test getting analysis summary when no graph exists."""
        summary = analyzer.get_analysis_summary()
        assert "error" in summary
        assert "No error propagation graph available" in summary["error"]
    
    def test_get_analysis_summary_with_graph(self, analyzer):
        """Test getting analysis summary with graph."""
        analyzer._error_propagation_graph = ErrorPropagationGraph(
            graph_id=str(uuid4()),
            graph_name="Test Graph"
        )
        
        summary = analyzer.get_analysis_summary()
        assert "graph_id" in summary
        assert "graph_name" in summary
        assert "total_paths" in summary
        assert "component_breakdown" in summary
    
    def test_get_analysis_stats(self, analyzer):
        """Test getting analysis statistics."""
        stats = analyzer.get_analysis_stats()
        
        assert "uptime_seconds" in stats
        assert "analysis_active" in stats
        assert "paths_analyzed" in stats
        assert "analysis_errors" in stats
        assert "last_analysis_duration_ms" in stats
        assert "analysis_rate_per_hour" in stats
        assert "error_rate_percent" in stats
        
        assert stats["analysis_active"] is False
        assert stats["paths_analyzed"] == 0
        assert stats["analysis_errors"] == 0
    
    def test_export_error_propagation_report_no_graph(self, analyzer):
        """Test exporting report when no graph exists."""
        report = analyzer.export_error_propagation_report()
        data = json.loads(report)
        assert "error" in data
        assert "No error propagation graph available" in data["error"]
    
    def test_export_error_propagation_report_with_graph(self, analyzer):
        """Test exporting report with graph."""
        analyzer._error_propagation_graph = ErrorPropagationGraph(
            graph_id=str(uuid4()),
            graph_name="Test Graph"
        )
        
        report = analyzer.export_error_propagation_report()
        data = json.loads(report)
        
        assert "graph_id" in data
        assert "graph_name" in data
        assert "propagation_paths" in data
        assert "correlation_mappings" in data
        assert "recovery_procedures" in data
        assert "fallback_mechanisms" in data
        assert "emergency_protocols" in data
        assert "error_classifications" in data
    
    def test_export_error_propagation_report_text_format(self, analyzer):
        """Test exporting report in text format."""
        analyzer._error_propagation_graph = ErrorPropagationGraph(
            graph_id=str(uuid4()),
            graph_name="Test Graph"
        )
        
        report = analyzer.export_error_propagation_report(format="text")
        assert isinstance(report, str)
        assert "graph_id" in report
    
    @pytest.mark.asyncio
    async def test_graceful_degradation_websocket_error(self, analyzer):
        """Test graceful degradation for WebSocket errors."""
        result = await analyzer.graceful_degradation(Exception("WebSocket connection failed"))
        assert result is True
    
    @pytest.mark.asyncio
    async def test_graceful_degradation_infrastructure_error(self, analyzer):
        """Test graceful degradation for infrastructure errors."""
        result = await analyzer.graceful_degradation(Exception("Infrastructure discovery failed"))
        assert result is True
    
    @pytest.mark.asyncio
    async def test_graceful_degradation_other_error(self, analyzer):
        """Test graceful degradation for other errors."""
        result = await analyzer.graceful_degradation(Exception("Unknown error"))
        assert result is False
    
    @pytest.mark.asyncio
    async def test_get_metrics(self, analyzer):
        """Test getting metrics."""
        metrics = await analyzer.get_metrics()
        
        assert "analysis_stats" in metrics
        assert "error_propagation_graph_available" in metrics
        assert "infrastructure_discoverer_active" in metrics
        assert "websocket_client_connected" in metrics
        assert "analysis_active" in metrics
        
        assert metrics["error_propagation_graph_available"] is False
        assert metrics["infrastructure_discoverer_active"] is None
        assert metrics["websocket_client_connected"] is None
        assert metrics["analysis_active"] is False


class TestErrorPropagationModels:
    """Test error propagation models functionality."""
    
    def test_error_propagation_path_creation(self):
        """Test ErrorPropagationPath creation."""
        path = ErrorPropagationPath(
            path_id="test_path",
            source_component="test_source",
            target_components=["target1", "target2"],
            propagation_steps=["step1", "step2", "step3"],
            error_types=["error1", "error2"],
            severity_levels=[ErrorSeverity.ERROR, ErrorSeverity.WARNING]
        )
        
        assert path.path_id == "test_path"
        assert path.source_component == "test_source"
        assert len(path.target_components) == 2
        assert len(path.propagation_steps) == 3
        assert len(path.error_types) == 2
        assert len(path.severity_levels) == 2
        assert path.user_impact_score == 0.0
        assert path.business_impact_score == 0.0
    
    def test_correlation_id_mapping_creation(self):
        """Test CorrelationIDMapping creation."""
        mapping = CorrelationIDMapping(
            correlation_id="test_correlation",
            primary_component="test_component",
            related_components=["related1", "related2"],
            error_events=["event1", "event2"]
        )
        
        assert mapping.correlation_id == "test_correlation"
        assert mapping.primary_component == "test_component"
        assert len(mapping.related_components) == 2
        assert len(mapping.error_events) == 2
        assert mapping.is_active is True
        assert mapping.resolution_status == "pending"
    
    def test_error_recovery_procedure_creation(self):
        """Test ErrorRecoveryProcedure creation."""
        procedure = ErrorRecoveryProcedure(
            procedure_id="test_procedure",
            error_category=ErrorCategory.SYSTEM_ERROR,
            error_codes=["ERROR_001", "ERROR_002"],
            affected_components=["comp1", "comp2"],
            recovery_steps=["step1", "step2"],
            automated_steps=["auto1"],
            manual_steps=["manual1"],
            estimated_recovery_time_seconds=30.0,
            timeout_seconds=300.0
        )
        
        assert procedure.procedure_id == "test_procedure"
        assert procedure.error_category == ErrorCategory.SYSTEM_ERROR
        assert len(procedure.error_codes) == 2
        assert len(procedure.affected_components) == 2
        assert len(procedure.recovery_steps) == 2
        assert len(procedure.automated_steps) == 1
        assert len(procedure.manual_steps) == 1
        assert procedure.estimated_recovery_time_seconds == 30.0
        assert procedure.timeout_seconds == 300.0
    
    def test_fallback_mechanism_creation(self):
        """Test FallbackMechanism creation."""
        mechanism = FallbackMechanism(
            mechanism_id="test_mechanism",
            mechanism_type=FallbackType.REDIS_FAILOVER,
            primary_service="primary_service",
            fallback_service="fallback_service",
            activation_conditions=["condition1", "condition2"],
            deactivation_conditions=["deactivation1"],
            health_check_endpoints=["endpoint1", "endpoint2"],
            switchover_time_seconds=5.0,
            performance_degradation_percent=10.0
        )
        
        assert mechanism.mechanism_id == "test_mechanism"
        assert mechanism.mechanism_type == FallbackType.REDIS_FAILOVER
        assert mechanism.primary_service == "primary_service"
        assert mechanism.fallback_service == "fallback_service"
        assert len(mechanism.activation_conditions) == 2
        assert len(mechanism.deactivation_conditions) == 1
        assert len(mechanism.health_check_endpoints) == 2
        assert mechanism.switchover_time_seconds == 5.0
        assert mechanism.performance_degradation_percent == 10.0
        assert mechanism.is_active is False
    
    def test_emergency_protocol_creation(self):
        """Test EmergencyProtocol creation."""
        protocol = EmergencyProtocol(
            protocol_id="test_protocol",
            protocol_name="Test Emergency Protocol",
            trigger_conditions=["condition1", "condition2"],
            severity_threshold=ErrorSeverity.CRITICAL,
            immediate_actions=["action1", "action2"],
            escalation_actions=["escalation1"],
            communication_actions=["comm1", "comm2"],
            primary_contacts=["contact1@example.com"],
            escalation_contacts=["escalation@example.com"],
            notification_channels=["email", "slack"],
            response_time_seconds=60.0,
            escalation_time_seconds=300.0
        )
        
        assert protocol.protocol_id == "test_protocol"
        assert protocol.protocol_name == "Test Emergency Protocol"
        assert len(protocol.trigger_conditions) == 2
        assert protocol.severity_threshold == ErrorSeverity.CRITICAL
        assert len(protocol.immediate_actions) == 2
        assert len(protocol.escalation_actions) == 1
        assert len(protocol.communication_actions) == 2
        assert len(protocol.primary_contacts) == 1
        assert len(protocol.escalation_contacts) == 1
        assert len(protocol.notification_channels) == 2
        assert protocol.response_time_seconds == 60.0
        assert protocol.escalation_time_seconds == 300.0
        assert protocol.is_active is True
    
    def test_error_classification_creation(self):
        """Test ErrorClassification creation."""
        classification = ErrorClassification(
            classification_id="test_classification",
            error_pattern="TEST_ERROR|ERROR_TEST",
            error_category=ErrorCategory.SYSTEM_ERROR,
            severity=ErrorSeverity.ERROR,
            classification_rules=["rule1", "rule2"],
            false_positive_patterns=["false1"],
            escalation_threshold=5,
            escalation_time_seconds=300.0,
            escalation_contacts=["contact@example.com"]
        )
        
        assert classification.classification_id == "test_classification"
        assert classification.error_pattern == "TEST_ERROR|ERROR_TEST"
        assert classification.error_category == ErrorCategory.SYSTEM_ERROR
        assert classification.severity == ErrorSeverity.ERROR
        assert len(classification.classification_rules) == 2
        assert len(classification.false_positive_patterns) == 1
        assert classification.escalation_threshold == 5
        assert classification.escalation_time_seconds == 300.0
        assert len(classification.escalation_contacts) == 1
        assert classification.auto_response_enabled is True


class TestErrorPropagationGraph:
    """Test ErrorPropagationGraph functionality."""
    
    @pytest.fixture
    def graph(self):
        """Create ErrorPropagationGraph instance for testing."""
        return ErrorPropagationGraph(
            graph_id=str(uuid4()),
            graph_name="Test Error Propagation Graph"
        )
    
    def test_graph_initialization(self, graph):
        """Test graph initialization."""
        assert graph.graph_name == "Test Error Propagation Graph"
        assert len(graph.propagation_paths) == 0
        assert len(graph.correlation_mappings) == 0
        assert len(graph.recovery_procedures) == 0
        assert len(graph.fallback_mechanisms) == 0
        assert len(graph.emergency_protocols) == 0
        assert len(graph.error_classifications) == 0
        assert graph.total_paths == 0
        assert graph.total_correlations == 0
        assert graph.total_procedures == 0
        assert graph.total_fallbacks == 0
        assert graph.total_protocols == 0
        assert graph.total_classifications == 0
    
    def test_add_propagation_path(self, graph):
        """Test adding propagation path."""
        path = ErrorPropagationPath(
            path_id="test_path",
            source_component="test_source",
            target_components=["target1"],
            propagation_steps=["step1"],
            error_types=["error1"],
            severity_levels=[ErrorSeverity.ERROR]
        )
        
        graph.add_propagation_path(path)
        
        assert len(graph.propagation_paths) == 1
        assert graph.total_paths == 1
        assert "test_path" in graph.propagation_paths
        assert graph.updated_at is not None
    
    def test_add_correlation_mapping(self, graph):
        """Test adding correlation mapping."""
        mapping = CorrelationIDMapping(
            correlation_id="test_correlation",
            primary_component="test_component",
            related_components=["related1"],
            error_events=["event1"]
        )
        
        graph.add_correlation_mapping(mapping)
        
        assert len(graph.correlation_mappings) == 1
        assert graph.total_correlations == 1
        assert "test_correlation" in graph.correlation_mappings
        assert graph.updated_at is not None
    
    def test_add_recovery_procedure(self, graph):
        """Test adding recovery procedure."""
        procedure = ErrorRecoveryProcedure(
            procedure_id="test_procedure",
            error_category=ErrorCategory.SYSTEM_ERROR,
            error_codes=["ERROR_001"],
            affected_components=["comp1"],
            recovery_steps=["step1"],
            automated_steps=["auto1"],
            manual_steps=["manual1"],
            estimated_recovery_time_seconds=30.0,
            timeout_seconds=300.0
        )
        
        graph.add_recovery_procedure(procedure)
        
        assert len(graph.recovery_procedures) == 1
        assert graph.total_procedures == 1
        assert "test_procedure" in graph.recovery_procedures
        assert graph.updated_at is not None
    
    def test_add_fallback_mechanism(self, graph):
        """Test adding fallback mechanism."""
        mechanism = FallbackMechanism(
            mechanism_id="test_mechanism",
            mechanism_type=FallbackType.REDIS_FAILOVER,
            primary_service="primary_service",
            fallback_service="fallback_service",
            activation_conditions=["condition1"],
            deactivation_conditions=["deactivation1"],
            health_check_endpoints=["endpoint1"],
            switchover_time_seconds=5.0,
            performance_degradation_percent=10.0
        )
        
        graph.add_fallback_mechanism(mechanism)
        
        assert len(graph.fallback_mechanisms) == 1
        assert graph.total_fallbacks == 1
        assert "test_mechanism" in graph.fallback_mechanisms
        assert graph.updated_at is not None
    
    def test_add_emergency_protocol(self, graph):
        """Test adding emergency protocol."""
        protocol = EmergencyProtocol(
            protocol_id="test_protocol",
            protocol_name="Test Protocol",
            trigger_conditions=["condition1"],
            severity_threshold=ErrorSeverity.CRITICAL,
            immediate_actions=["action1"],
            escalation_actions=["escalation1"],
            communication_actions=["comm1"],
            primary_contacts=["contact@example.com"],
            escalation_contacts=["escalation@example.com"],
            notification_channels=["email"],
            response_time_seconds=60.0,
            escalation_time_seconds=300.0
        )
        
        graph.add_emergency_protocol(protocol)
        
        assert len(graph.emergency_protocols) == 1
        assert graph.total_protocols == 1
        assert "test_protocol" in graph.emergency_protocols
        assert graph.updated_at is not None
    
    def test_add_error_classification(self, graph):
        """Test adding error classification."""
        classification = ErrorClassification(
            classification_id="test_classification",
            error_pattern="TEST_ERROR",
            error_category=ErrorCategory.SYSTEM_ERROR,
            severity=ErrorSeverity.ERROR,
            classification_rules=["rule1"],
            false_positive_patterns=["false1"],
            escalation_threshold=5,
            escalation_time_seconds=300.0,
            escalation_contacts=["contact@example.com"]
        )
        
        graph.add_error_classification(classification)
        
        assert len(graph.error_classifications) == 1
        assert graph.total_classifications == 1
        assert "test_classification" in graph.error_classifications
        assert graph.updated_at is not None
    
    def test_get_propagation_summary(self, graph):
        """Test getting propagation summary."""
        summary = graph.get_propagation_summary()
        
        assert "graph_id" in summary
        assert "graph_name" in summary
        assert "total_paths" in summary
        assert "total_correlations" in summary
        assert "total_procedures" in summary
        assert "total_fallbacks" in summary
        assert "total_protocols" in summary
        assert "total_classifications" in summary
        assert "component_breakdown" in summary
        assert "accuracy_score" in summary
        assert "validation_status" in summary
    
    def test_validate_graph_empty(self, graph):
        """Test validating empty graph."""
        validation = graph.validate_graph()
        
        assert validation["is_valid"] is True
        assert len(validation["errors"]) == 0
        assert len(validation["warnings"]) == 0
        assert validation["accuracy_score"] == 0.0
    
    def test_validate_graph_with_data(self, graph):
        """Test validating graph with data."""
        # Add valid data
        path = ErrorPropagationPath(
            path_id="test_path",
            source_component="test_source",
            target_components=["target1"],
            propagation_steps=["step1"],
            error_types=["error1"],
            severity_levels=[ErrorSeverity.ERROR]
        )
        graph.add_propagation_path(path)
        
        procedure = ErrorRecoveryProcedure(
            procedure_id="test_procedure",
            error_category=ErrorCategory.SYSTEM_ERROR,
            error_codes=["ERROR_001"],
            affected_components=["comp1"],
            recovery_steps=["step1"],
            automated_steps=["auto1"],
            manual_steps=["manual1"],
            estimated_recovery_time_seconds=30.0,
            timeout_seconds=300.0
        )
        graph.add_recovery_procedure(procedure)
        
        validation = graph.validate_graph()
        
        assert validation["is_valid"] is True
        assert len(validation["errors"]) == 0
        assert validation["accuracy_score"] == 0.9
    
    def test_validate_graph_with_invalid_data(self, graph):
        """Test validating graph with invalid data."""
        # Add invalid data
        path = ErrorPropagationPath(
            path_id="test_path",
            source_component="",  # Invalid: empty source
            target_components=["target1"],
            propagation_steps=["step1"],
            error_types=["error1"],
            severity_levels=[ErrorSeverity.ERROR]
        )
        graph.add_propagation_path(path)
        
        procedure = ErrorRecoveryProcedure(
            procedure_id="test_procedure",
            error_category=ErrorCategory.SYSTEM_ERROR,
            error_codes=["ERROR_001"],
            affected_components=["comp1"],
            recovery_steps=[],  # Invalid: empty recovery steps
            automated_steps=["auto1"],
            manual_steps=["manual1"],
            estimated_recovery_time_seconds=30.0,
            timeout_seconds=300.0
        )
        graph.add_recovery_procedure(procedure)
        
        validation = graph.validate_graph()
        
        assert validation["is_valid"] is False
        assert len(validation["errors"]) > 0
        assert any("missing source component" in error for error in validation["errors"])
        assert any("no recovery steps" in error for error in validation["errors"])
    
    def test_to_dict(self, graph):
        """Test converting graph to dictionary."""
        # Add some test data
        path = ErrorPropagationPath(
            path_id="test_path",
            source_component="test_source",
            target_components=["target1"],
            propagation_steps=["step1"],
            error_types=["error1"],
            severity_levels=[ErrorSeverity.ERROR]
        )
        graph.add_propagation_path(path)
        
        mapping = CorrelationIDMapping(
            correlation_id="test_correlation",
            primary_component="test_component",
            related_components=["related1"],
            error_events=["event1"]
        )
        graph.add_correlation_mapping(mapping)
        
        data = graph.to_dict()
        
        assert "graph_id" in data
        assert "graph_name" in data
        assert "propagation_paths" in data
        assert "correlation_mappings" in data
        assert "recovery_procedures" in data
        assert "fallback_mechanisms" in data
        assert "emergency_protocols" in data
        assert "error_classifications" in data
        assert "metadata" in data
        
        assert len(data["propagation_paths"]) == 1
        assert len(data["correlation_mappings"]) == 1
        assert "test_path" in data["propagation_paths"]
        assert "test_correlation" in data["correlation_mappings"]


class TestErrorPropagationIntegration:
    """Test error propagation analysis integration."""
    
    @pytest.mark.asyncio
    async def test_full_analysis_workflow(self):
        """Test complete analysis workflow."""
        config = ErrorPropagationConfig(
            enable_real_time_analysis=False,
            analysis_interval_seconds=1
        )
        analyzer = ErrorPropagationAnalyzer(config)
        
        # Mock infrastructure discoverer
        mock_discoverer = AsyncMock()
        mock_discoverer.start_discovery = AsyncMock(return_value=True)
        mock_discoverer.stop_discovery = AsyncMock()
        mock_discoverer.get_discovered_services = MagicMock(return_value={
            "observatory": MagicMock(name="Observatory", port=8888),
            "prometheus": MagicMock(name="Prometheus", port=9090),
            "grafana": MagicMock(name="Grafana", port=3000)
        })
        
        # Mock WebSocket client
        mock_client = AsyncMock()
        mock_client.connect_to_endpoints = AsyncMock()
        mock_client.disconnect = AsyncMock()
        
        with patch('src.system_architecture.analysis.error_propagation_analyzer.InfrastructureDiscoverer', return_value=mock_discoverer), \
             patch('src.system_architecture.analysis.error_propagation_analyzer.ObservatoryWebSocketClient', return_value=mock_client):
            
            # Start analysis
            result = await analyzer.start_analysis()
            assert result is True
            
            # Wait for analysis to complete
            await asyncio.sleep(0.1)
            
            # Check results
            graph = analyzer.get_error_propagation_graph()
            assert graph is not None
            
            summary = analyzer.get_analysis_summary()
            assert "total_paths" in summary
            assert summary["total_paths"] >= 4  # Should have at least 4 paths
            
            # Stop analysis
            await analyzer.stop_analysis()
            assert analyzer._analysis_active is False
    
    @pytest.mark.asyncio
    async def test_error_handling_during_analysis(self):
        """Test error handling during analysis."""
        config = ErrorPropagationConfig(
            enable_real_time_analysis=False,
            analysis_interval_seconds=1
        )
        analyzer = ErrorPropagationAnalyzer(config)
        
        # Mock infrastructure discoverer that fails
        mock_discoverer = AsyncMock()
        mock_discoverer.start_discovery = AsyncMock(side_effect=Exception("Discovery failed"))
        
        with patch('src.system_architecture.analysis.error_propagation_analyzer.InfrastructureDiscoverer', return_value=mock_discoverer):
            result = await analyzer.start_analysis()
            assert result is False
            assert analyzer._analysis_active is False
    
    def test_health_status_during_analysis(self):
        """Test health status during analysis."""
        config = ErrorPropagationConfig(
            enable_real_time_analysis=False,
            analysis_interval_seconds=1
        )
        analyzer = ErrorPropagationAnalyzer(config)
        
        # Test inactive state
        health = analyzer.get_health_status()
        assert health.status.value == "error"
        assert health.health_score == 0.0
        
        # Simulate active state with errors
        analyzer._analysis_active = True
        analyzer._paths_analyzed = 10
        analyzer._analysis_errors = 2  # 20% error rate
        
        health = analyzer.get_health_status()
        assert health.status.value == "error"
        assert health.health_score == 0.3
        
        # Simulate active state with warnings
        analyzer._analysis_errors = 1  # 10% error rate
        
        health = analyzer.get_health_status()
        assert health.status.value == "warning"
        assert health.health_score == 0.7
        
        # Simulate healthy state
        analyzer._analysis_errors = 0  # 0% error rate
        
        health = analyzer.get_health_status()
        assert health.status.value == "healthy"
        assert health.health_score == 1.0


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--cov=src.system_architecture.analysis.error_propagation_analyzer", "--cov-report=html"])