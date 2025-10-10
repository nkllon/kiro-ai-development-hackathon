"""
Unit tests for OpenMetrics Discovery and Modeling System.
"""

import pytest
from datetime import datetime
from unittest.mock import Mock, patch

from src.beast_mode.observatory.openmetrics_discovery import (
    MonitoringDiscoveryEngine,
    OpenMetricsMetricFamily,
    OpenMetricsMetricType,
    OpenMetricsDiscoveryResult,
    DiscoveryAuditRecord
)
from src.beast_mode.observatory.language_modeling import (
    UbiquitousLanguageEngine,
    DomainType,
    MetricType
)


class TestOpenMetricsMetricFamily:
    """Test OpenMetricsMetricFamily dataclass."""
    
    def test_metric_family_creation(self):
        """Test creating an OpenMetrics metric family."""
        family = OpenMetricsMetricFamily(
            name="http_requests_total",
            metric_type=OpenMetricsMetricType.COUNTER,
            help_text="Total number of HTTP requests",
            unit="total",
            labels=["method", "status", "handler"]
        )
        
        assert family.name == "http_requests_total"
        assert family.metric_type == OpenMetricsMetricType.COUNTER
        assert family.help_text == "Total number of HTTP requests"
        assert family.unit == "total"
        assert "method" in family.labels
        assert len(family.samples) == 0


class TestDiscoveryAuditRecord:
    """Test DiscoveryAuditRecord dataclass."""
    
    def test_audit_record_creation(self):
        """Test creating a discovery audit record."""
        record = DiscoveryAuditRecord(
            discovery_source="OpenMetrics Specification",
            discovery_method="Specification Analysis",
            findings={"metric_families": 10, "terminology_terms": 25},
            decisions_made=["Mapped counters to business events"],
            rationale="Reference implementation for methodology",
            confidence_score=0.95
        )
        
        assert record.discovery_source == "OpenMetrics Specification"
        assert record.discovery_method == "Specification Analysis"
        assert record.findings["metric_families"] == 10
        assert len(record.decisions_made) == 1
        assert record.confidence_score == 0.95
        assert isinstance(record.timestamp, datetime)


class TestMonitoringDiscoveryEngine:
    """Test MonitoringDiscoveryEngine class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.language_engine = UbiquitousLanguageEngine()
        self.discovery_engine = MonitoringDiscoveryEngine(self.language_engine)
    
    def test_engine_initialization(self):
        """Test discovery engine initialization."""
        assert self.discovery_engine.language_engine == self.language_engine
        assert len(self.discovery_engine._audit_records) == 0
        assert "version" in self.discovery_engine._openmetrics_spec
        assert self.discovery_engine._openmetrics_spec["version"] == "1.0.0"
    
    def test_openmetrics_specification_loading(self):
        """Test OpenMetrics specification knowledge loading."""
        spec = self.discovery_engine._openmetrics_spec
        
        assert spec["content_type"] == "application/openmetrics-text"
        assert "counter" in spec["metric_types"]
        assert "gauge" in spec["metric_types"]
        assert "histogram" in spec["metric_types"]
        assert "summary" in spec["metric_types"]
        
        # Test counter specification
        counter_spec = spec["metric_types"]["counter"]
        assert counter_spec["suffix"] == "_total"
        assert "http_requests_total" in counter_spec["examples"]
        assert "Cumulative count" in counter_spec["business_meaning"]
    
    def test_unit_inference(self):
        """Test unit inference from metric names."""
        engine = self.discovery_engine
        
        assert engine._infer_unit_from_name("response_time_seconds") == "seconds"
        assert engine._infer_unit_from_name("memory_usage_bytes") == "bytes"
        assert engine._infer_unit_from_name("http_requests_total") == "total"
        assert engine._infer_unit_from_name("error_ratio") == "ratio"
        assert engine._infer_unit_from_name("cpu_usage_percent") == "percent"
        assert engine._infer_unit_from_name("temperature_celsius") == "celsius"
        assert engine._infer_unit_from_name("unknown_metric") is None
    
    def test_label_inference(self):
        """Test common label inference."""
        engine = self.discovery_engine
        
        # HTTP metrics should include HTTP-specific labels
        http_labels = engine._infer_common_labels("http_requests_total")
        assert "instance" in http_labels
        assert "job" in http_labels
        assert "method" in http_labels
        assert "status" in http_labels
        assert "handler" in http_labels
        
        # RPC metrics should include RPC-specific labels
        rpc_labels = engine._infer_common_labels("rpc_duration_seconds")
        assert "service" in rpc_labels
        assert "method" in rpc_labels
        
        # Database metrics should include DB-specific labels
        db_labels = engine._infer_common_labels("database_queries_total")
        assert "database" in db_labels
        assert "table" in db_labels
        assert "operation" in db_labels
        
        # Queue metrics should include queue-specific labels
        queue_labels = engine._infer_common_labels("queue_size")
        assert "queue_name" in queue_labels
        assert "priority" in queue_labels
    
    def test_metric_family_discovery(self):
        """Test discovery of metric families from specification."""
        families = self.discovery_engine._discover_metric_families()
        
        assert len(families) > 0
        
        # Check that we have families for each metric type
        counter_families = [f for f in families if f.metric_type == OpenMetricsMetricType.COUNTER]
        gauge_families = [f for f in families if f.metric_type == OpenMetricsMetricType.GAUGE]
        histogram_families = [f for f in families if f.metric_type == OpenMetricsMetricType.HISTOGRAM]
        
        assert len(counter_families) > 0
        assert len(gauge_families) > 0
        assert len(histogram_families) > 0
        
        # Check specific examples
        http_requests = next((f for f in families if f.name == "http_requests_total"), None)
        assert http_requests is not None
        assert http_requests.metric_type == OpenMetricsMetricType.COUNTER
        assert http_requests.unit == "total"
        assert "method" in http_requests.labels
    
    def test_naming_conventions_extraction(self):
        """Test extraction of naming conventions."""
        conventions = self.discovery_engine._extract_naming_conventions()
        
        assert "metric_naming" in conventions
        assert "label_naming" in conventions
        assert "unit_suffix" in conventions
        assert "type_suffix" in conventions
        
        assert "snake_case" in conventions["metric_naming"]
        assert "base SI units" in conventions["base_units"]
    
    def test_label_conventions_analysis(self):
        """Test analysis of label usage patterns."""
        label_conventions = self.discovery_engine._analyze_label_conventions()
        
        assert "standard_labels" in label_conventions
        assert "http_labels" in label_conventions
        assert "rpc_labels" in label_conventions
        
        assert "instance" in label_conventions["standard_labels"]
        assert "job" in label_conventions["standard_labels"]
        assert "method" in label_conventions["http_labels"]
        assert "status" in label_conventions["http_labels"]
    
    def test_terminology_extraction(self):
        """Test extraction of technical to business terminology."""
        terminology = self.discovery_engine._extract_terminology()
        
        assert len(terminology) > 0
        assert "counter_metric" in terminology
        assert "gauge_metric" in terminology
        assert "exposition_format" in terminology
        assert "metric_family" in terminology
        
        # Check business name generation
        assert "cumulative" in terminology["counter_metric"].lower()
        assert "Metric Export Format" == terminology["exposition_format"]
    
    def test_business_name_generation(self):
        """Test generation of business names from technical names."""
        engine = self.discovery_engine
        
        assert engine._generate_business_name("http_requests_total") == "HTTP Requests"
        assert engine._generate_business_name("memory_usage_bytes") == "Memory Usage"
        assert engine._generate_business_name("rpc_duration_seconds") == "RPC Duration"
        assert engine._generate_business_name("cpu_usage_percent") == "CPU Usage"
        assert engine._generate_business_name("db_connections") == "Database Connections"
    
    def test_business_concepts_identification(self):
        """Test identification of high-level business concepts."""
        concepts = self.discovery_engine._identify_business_concepts()
        
        assert len(concepts) > 0
        assert any("Performance" in concept for concept in concepts)
        assert any("Health" in concept for concept in concepts)
        assert any("Resource" in concept for concept in concepts)
        assert any("Error" in concept for concept in concepts)
    
    def test_pattern_identification(self):
        """Test identification of patterns and best practices."""
        patterns = self.discovery_engine._identify_patterns()
        
        assert len(patterns) > 0
        assert any("counter" in pattern.lower() for pattern in patterns)
        assert any("gauge" in pattern.lower() for pattern in patterns)
        assert any("histogram" in pattern.lower() for pattern in patterns)
        assert any("label" in pattern.lower() for pattern in patterns)
        assert any("unit" in pattern.lower() for pattern in patterns)
    
    @pytest.mark.asyncio
    async def test_openmetrics_discovery_complete(self):
        """Test complete OpenMetrics specification discovery."""
        result = await self.discovery_engine.discover_openmetrics_specification()
        
        assert isinstance(result, OpenMetricsDiscoveryResult)
        assert len(result.metric_families) > 0
        assert len(result.naming_conventions) > 0
        assert len(result.label_conventions) > 0
        assert len(result.terminology_extracted) > 0
        assert len(result.business_concepts) > 0
        assert len(result.discovered_patterns) > 0
        
        assert result.exposition_format == "text/plain; version=1.0.0; charset=utf-8"
        assert result.content_type == "application/openmetrics-text"
        assert isinstance(result.discovery_timestamp, datetime)
        
        # Check audit trail was created
        audit_records = self.discovery_engine.get_discovery_audit_trail()
        assert len(audit_records) == 1
        assert audit_records[0].confidence_score == 1.0
        assert len(audit_records[0].decisions_made) > 0
    
    @pytest.mark.asyncio
    async def test_language_model_generation(self):
        """Test generation of language model from discovery results."""
        # First perform discovery
        discovery_result = await self.discovery_engine.discover_openmetrics_specification()
        
        # Generate language model
        model = await self.discovery_engine.generate_language_model(discovery_result)
        
        assert model.domain == DomainType.DEVOPS
        assert model.name == "OpenMetrics Reference Implementation"
        assert len(model.terminology) > 0
        assert len(model.concepts) > 0
        assert len(model.aggregation_rules) > 0
        
        # Check specific terminology
        assert "counter_metric" in model.terminology
        assert "exposition_format" in model.terminology
        
        # Check aggregation rules
        assert "request_rate" in model.aggregation_rules
        assert "error_ratio" in model.aggregation_rules
        
        # Check display preferences
        assert len(model.display_preferences.chart_colors) > 0
        assert "counter" in model.display_preferences.chart_colors
        
        # Check metadata
        assert model.metadata["source"] == "OpenMetrics Specification 1.0.0"
        assert model.metadata["reference_implementation"] is True
    
    def test_openmetrics_to_metric_type_mapping(self):
        """Test mapping of OpenMetrics types to internal metric types."""
        engine = self.discovery_engine
        
        assert engine._map_openmetrics_to_metric_type(OpenMetricsMetricType.COUNTER) == MetricType.COUNTER
        assert engine._map_openmetrics_to_metric_type(OpenMetricsMetricType.GAUGE) == MetricType.GAUGE
        assert engine._map_openmetrics_to_metric_type(OpenMetricsMetricType.HISTOGRAM) == MetricType.HISTOGRAM
        assert engine._map_openmetrics_to_metric_type(OpenMetricsMetricType.SUMMARY) == MetricType.SUMMARY
        assert engine._map_openmetrics_to_metric_type(OpenMetricsMetricType.INFO) == MetricType.GAUGE
        assert engine._map_openmetrics_to_metric_type(OpenMetricsMetricType.UNKNOWN) == MetricType.GAUGE
    
    @pytest.mark.asyncio
    async def test_methodology_documentation_generation(self):
        """Test generation of methodology documentation."""
        # Perform discovery to create audit trail
        await self.discovery_engine.discover_openmetrics_specification()
        
        # Generate methodology documentation
        methodology = self.discovery_engine.generate_methodology_documentation()
        
        assert "methodology" in methodology
        assert "process_steps" in methodology
        assert "audit_trail" in methodology
        assert "replication_guide" in methodology
        
        # Check methodology details
        assert methodology["methodology"]["name"] == "OpenMetrics Discovery Methodology"
        assert methodology["methodology"]["version"] == "1.0.0"
        
        # Check process steps
        steps = methodology["process_steps"]
        assert len(steps) == 4
        assert steps[0]["name"] == "Specification Analysis"
        assert steps[1]["name"] == "Terminology Extraction"
        assert steps[2]["name"] == "Pattern Identification"
        assert steps[3]["name"] == "Language Model Generation"
        
        # Check audit trail
        audit = methodology["audit_trail"]
        assert "discovery_id" in audit
        assert "findings" in audit
        assert "decisions" in audit
        assert audit["confidence"] == 1.0
        
        # Check replication guide
        replication = methodology["replication_guide"]
        assert "steps" in replication
        assert "tools_required" in replication
        assert len(replication["steps"]) > 0
        assert "MonitoringDiscoveryEngine" in replication["tools_required"]
    
    @pytest.mark.asyncio
    async def test_discovery_error_handling(self):
        """Test error handling during discovery process."""
        # Mock a failure in metric family discovery
        with patch.object(self.discovery_engine, '_discover_metric_families', side_effect=Exception("Test error")):
            with pytest.raises(Exception, match="Test error"):
                await self.discovery_engine.discover_openmetrics_specification()
            
            # Check that audit record was created for the failure
            audit_records = self.discovery_engine.get_discovery_audit_trail()
            assert len(audit_records) == 1
            assert audit_records[0].confidence_score == 0.0
            assert "Test error" in audit_records[0].findings["error"]
    
    def test_audit_trail_tracking(self):
        """Test audit trail tracking functionality."""
        # Initially no records
        assert len(self.discovery_engine.get_discovery_audit_trail()) == 0
        
        # Create a test audit record
        record = DiscoveryAuditRecord(
            discovery_source="Test Source",
            discovery_method="Test Method",
            findings={"test": "data"},
            confidence_score=0.8
        )
        
        self.discovery_engine._audit_records.append(record)
        
        # Check audit trail retrieval
        trail = self.discovery_engine.get_discovery_audit_trail()
        assert len(trail) == 1
        assert trail[0].discovery_source == "Test Source"
        assert trail[0].confidence_score == 0.8
        
        # Ensure we get a copy, not the original
        trail[0].confidence_score = 0.5
        original_trail = self.discovery_engine.get_discovery_audit_trail()
        assert original_trail[0].confidence_score == 0.8


if __name__ == "__main__":
    pytest.main([__file__])