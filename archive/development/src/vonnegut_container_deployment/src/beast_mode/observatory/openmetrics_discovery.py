"""
OpenMetrics Discovery and Modeling System - Reference implementation of monitoring system discovery.

This module demonstrates the complete discovery → modeling → generation methodology by
analyzing the OpenMetrics specification as if it were a customer's monitoring system.
This serves as both a reference implementation and a proof of concept for the approach.
"""

import json
import logging
import re
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Any, Set, Tuple
from urllib.parse import urlparse

from .language_modeling import (
    UbiquitousLanguageEngine,
    DomainLanguageModel,
    TermDefinition,
    ConceptModel,
    ConceptRelationship,
    AggregationRule,
    DisplayPreferences,
    DomainType,
    MetricType,
    AggregationFunction
)


logger = logging.getLogger(__name__)


class OpenMetricsMetricType(Enum):
    """OpenMetrics standard metric types."""
    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    SUMMARY = "summary"
    GAUGE_HISTOGRAM = "gaugehistogram"
    INFO = "info"
    STATE_SET = "stateset"
    UNKNOWN = "unknown"


@dataclass
class OpenMetricsMetricFamily:
    """Represents an OpenMetrics metric family."""
    name: str
    metric_type: OpenMetricsMetricType
    help_text: str
    unit: Optional[str] = None
    labels: List[str] = field(default_factory=list)
    samples: List[Dict[str, Any]] = field(default_factory=list)


@dataclass
class OpenMetricsDiscoveryResult:
    """Result of OpenMetrics specification discovery."""
    metric_families: List[OpenMetricsMetricFamily]
    naming_conventions: Dict[str, str]
    label_conventions: Dict[str, List[str]]
    exposition_format: str
    content_type: str
    discovered_patterns: List[str]
    terminology_extracted: Dict[str, str]
    business_concepts: List[str]
    discovery_timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class DiscoveryAuditRecord:
    """Audit record for discovery process."""
    discovery_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = field(default_factory=datetime.now)
    discovery_source: str = ""
    discovery_method: str = ""
    findings: Dict[str, Any] = field(default_factory=dict)
    decisions_made: List[str] = field(default_factory=list)
    rationale: str = ""
    confidence_score: float = 1.0
    next_steps: List[str] = field(default_factory=list)


class MonitoringDiscoveryEngine:
    """
    Engine for discovering and analyzing monitoring systems to extract their models.
    
    This implementation focuses on OpenMetrics as a reference case, but the methodology
    can be applied to any monitoring system (Prometheus, Grafana, custom systems, etc.).
    """
    
    def __init__(self, language_engine: UbiquitousLanguageEngine):
        self.language_engine = language_engine
        self._audit_records: List[DiscoveryAuditRecord] = []
        
        # OpenMetrics specification knowledge base
        self._openmetrics_spec = self._load_openmetrics_specification()
        
        logger.info("🔍 MonitoringDiscoveryEngine initialized for OpenMetrics discovery")
    
    def _load_openmetrics_specification(self) -> Dict[str, Any]:
        """Load OpenMetrics specification knowledge for discovery."""
        return {
            "version": "1.0.0",
            "content_type": "application/openmetrics-text",
            "metric_types": {
                "counter": {
                    "description": "Monotonically increasing counter",
                    "suffix": "_total",
                    "business_meaning": "Cumulative count of events or operations",
                    "examples": ["http_requests_total", "errors_total", "bytes_processed_total"]
                },
                "gauge": {
                    "description": "Value that can go up and down",
                    "suffix": None,
                    "business_meaning": "Current state or level measurement",
                    "examples": ["memory_usage_bytes", "temperature_celsius", "queue_size"]
                },
                "histogram": {
                    "description": "Cumulative frequency of observations in buckets",
                    "suffix": "_bucket",
                    "business_meaning": "Distribution of measurements over time",
                    "examples": ["http_request_duration_seconds", "response_size_bytes"]
                },
                "summary": {
                    "description": "Quantiles of observations over sliding time window",
                    "suffix": "_quantile",
                    "business_meaning": "Statistical summary of measurements",
                    "examples": ["rpc_duration_seconds", "request_size_bytes"]
                }
            },
            "naming_conventions": {
                "base_unit": "Use base units (seconds, bytes, etc.)",
                "suffix_pattern": "Metric type determines suffix",
                "label_naming": "Snake case for label names",
                "reserved_labels": ["__name__", "__value__", "__timestamp__"]
            },
            "exposition_format": {
                "help_line": "# HELP metric_name Description of the metric",
                "type_line": "# TYPE metric_name metric_type",
                "sample_line": "metric_name{label1=\"value1\"} value timestamp",
                "eof_marker": "# EOF"
            }
        }
    
    async def discover_openmetrics_specification(self) -> OpenMetricsDiscoveryResult:
        """
        Discover and analyze the OpenMetrics specification as a reference monitoring system.
        
        This method treats the OpenMetrics spec as if it were a customer's monitoring system,
        demonstrating the complete discovery methodology.
        """
        logger.info("🔍 Starting OpenMetrics specification discovery...")
        
        audit_record = DiscoveryAuditRecord(
            discovery_source="OpenMetrics Specification 1.0.0",
            discovery_method="Specification Analysis",
            rationale="Reference implementation to demonstrate discovery methodology"
        )
        
        try:
            # Step 1: Discover metric families and types
            metric_families = self._discover_metric_families()
            audit_record.findings["metric_families"] = len(metric_families)
            
            # Step 2: Extract naming conventions
            naming_conventions = self._extract_naming_conventions()
            audit_record.findings["naming_conventions"] = len(naming_conventions)
            
            # Step 3: Analyze label conventions
            label_conventions = self._analyze_label_conventions()
            audit_record.findings["label_conventions"] = len(label_conventions)
            
            # Step 4: Extract terminology and business concepts
            terminology = self._extract_terminology()
            business_concepts = self._identify_business_concepts()
            audit_record.findings["terminology_terms"] = len(terminology)
            audit_record.findings["business_concepts"] = len(business_concepts)
            
            # Step 5: Identify patterns and best practices
            patterns = self._identify_patterns()
            audit_record.findings["patterns_discovered"] = len(patterns)
            
            # Create discovery result
            result = OpenMetricsDiscoveryResult(
                metric_families=metric_families,
                naming_conventions=naming_conventions,
                label_conventions=label_conventions,
                exposition_format="text/plain; version=1.0.0; charset=utf-8",
                content_type="application/openmetrics-text",
                discovered_patterns=patterns,
                terminology_extracted=terminology,
                business_concepts=business_concepts
            )
            
            # Record successful discovery
            audit_record.confidence_score = 1.0
            audit_record.decisions_made = [
                "Identified 4 core metric types with distinct business meanings",
                "Extracted naming conventions for enterprise consistency",
                "Mapped technical terms to business concepts",
                "Documented exposition format for integration generation"
            ]
            audit_record.next_steps = [
                "Generate domain language model from discovered terminology",
                "Create aggregation rules for metric processing",
                "Build integration generation templates"
            ]
            
            self._audit_records.append(audit_record)
            
            logger.info(f"✅ OpenMetrics discovery complete: {len(metric_families)} metric families, {len(terminology)} terms")
            return result
            
        except Exception as e:
            audit_record.confidence_score = 0.0
            audit_record.findings["error"] = str(e)
            self._audit_records.append(audit_record)
            logger.error(f"❌ OpenMetrics discovery failed: {e}")
            raise
    
    def _discover_metric_families(self) -> List[OpenMetricsMetricFamily]:
        """Discover OpenMetrics metric families from specification."""
        metric_families = []
        
        for metric_type, spec in self._openmetrics_spec["metric_types"].items():
            # Create representative metric families for each type
            for example in spec["examples"]:
                family = OpenMetricsMetricFamily(
                    name=example,
                    metric_type=OpenMetricsMetricType(metric_type),
                    help_text=f"{spec['business_meaning']} - {spec['description']}",
                    unit=self._infer_unit_from_name(example),
                    labels=self._infer_common_labels(example)
                )
                metric_families.append(family)
        
        return metric_families
    
    def _infer_unit_from_name(self, metric_name: str) -> Optional[str]:
        """Infer unit from metric name following OpenMetrics conventions."""
        unit_patterns = {
            r".*_seconds$": "seconds",
            r".*_bytes$": "bytes", 
            r".*_total$": "total",
            r".*_ratio$": "ratio",
            r".*_percent$": "percent",
            r".*_celsius$": "celsius",
            r".*_requests$": "requests",
            r".*_errors$": "errors"
        }
        
        for pattern, unit in unit_patterns.items():
            if re.match(pattern, metric_name):
                return unit
        
        return None
    
    def _infer_common_labels(self, metric_name: str) -> List[str]:
        """Infer common labels based on metric name and OpenMetrics patterns."""
        common_labels = ["instance", "job"]  # Standard Prometheus labels
        
        # Add domain-specific labels based on metric name
        if "http" in metric_name:
            common_labels.extend(["method", "status", "handler"])
        elif "rpc" in metric_name:
            common_labels.extend(["service", "method", "status"])
        elif "database" in metric_name or "db" in metric_name:
            common_labels.extend(["database", "table", "operation"])
        elif "queue" in metric_name:
            common_labels.extend(["queue_name", "priority"])
        
        return common_labels
    
    def _extract_naming_conventions(self) -> Dict[str, str]:
        """Extract naming conventions from OpenMetrics specification."""
        return {
            "metric_naming": "snake_case with descriptive names",
            "label_naming": "snake_case for consistency",
            "unit_suffix": "Include unit in metric name (e.g., _seconds, _bytes)",
            "type_suffix": "Add type-specific suffix (e.g., _total for counters)",
            "reserved_prefixes": "Avoid __ prefix (reserved for internal use)",
            "base_units": "Use base SI units (seconds not milliseconds, bytes not KB)",
            "descriptive_names": "Metric names should be self-documenting"
        }
    
    def _analyze_label_conventions(self) -> Dict[str, List[str]]:
        """Analyze label usage patterns in OpenMetrics."""
        return {
            "standard_labels": ["instance", "job"],
            "http_labels": ["method", "status", "handler", "path"],
            "rpc_labels": ["service", "method", "status", "client"],
            "database_labels": ["database", "table", "operation", "result"],
            "queue_labels": ["queue_name", "priority", "consumer"],
            "system_labels": ["cpu", "device", "filesystem", "mode"],
            "application_labels": ["version", "environment", "component", "team"]
        }
    
    def _extract_terminology(self) -> Dict[str, str]:
        """Extract technical to business terminology mapping."""
        terminology = {}
        
        for metric_type, spec in self._openmetrics_spec["metric_types"].items():
            # Map technical metric type to business meaning
            terminology[f"{metric_type}_metric"] = spec["business_meaning"]
            
            # Map example metrics to business terms
            for example in spec["examples"]:
                business_name = self._generate_business_name(example)
                terminology[example] = business_name
        
        # Add OpenMetrics concepts
        terminology.update({
            "exposition_format": "Metric Export Format",
            "metric_family": "Related Metric Group",
            "sample": "Metric Data Point",
            "timestamp": "Measurement Time",
            "label": "Metric Dimension",
            "help_text": "Metric Description",
            "quantile": "Statistical Percentile",
            "bucket": "Distribution Range",
            "le": "Less Than or Equal To"
        })
        
        return terminology
    
    def _generate_business_name(self, technical_name: str) -> str:
        """Generate business-friendly name from technical metric name."""
        # Remove common suffixes
        name = re.sub(r"_(total|seconds|bytes|ratio|percent)$", "", technical_name)
        
        # Split on underscores and capitalize
        words = name.split("_")
        business_words = []
        
        for word in words:
            # Handle common abbreviations
            if word == "http":
                business_words.append("HTTP")
            elif word == "rpc":
                business_words.append("RPC")
            elif word == "cpu":
                business_words.append("CPU")
            elif word == "db":
                business_words.append("Database")
            else:
                business_words.append(word.capitalize())
        
        return " ".join(business_words)
    
    def _identify_business_concepts(self) -> List[str]:
        """Identify high-level business concepts from OpenMetrics."""
        return [
            "System Performance Monitoring",
            "Application Health Tracking",
            "Resource Utilization Measurement",
            "Error Rate Monitoring",
            "Latency Distribution Analysis",
            "Throughput Measurement",
            "Capacity Planning Metrics",
            "Service Level Indicators",
            "Operational Metrics",
            "Business Metrics"
        ]
    
    def _identify_patterns(self) -> List[str]:
        """Identify patterns and best practices from OpenMetrics."""
        return [
            "Use counters for monotonically increasing values",
            "Use gauges for values that can go up and down",
            "Include units in metric names for clarity",
            "Use consistent label naming across metrics",
            "Provide meaningful help text for all metrics",
            "Follow base unit conventions (seconds, bytes)",
            "Use histograms for latency and size distributions",
            "Include standard labels (instance, job) for infrastructure metrics",
            "Avoid high cardinality labels to prevent performance issues",
            "Use summary metrics for pre-calculated quantiles"
        ]
    
    async def generate_language_model(self, discovery_result: OpenMetricsDiscoveryResult) -> DomainLanguageModel:
        """
        Generate a domain language model from OpenMetrics discovery results.
        
        This demonstrates the discovery → modeling transformation.
        """
        logger.info("📝 Generating language model from OpenMetrics discovery...")
        
        # Create the domain model
        model = self.language_engine.create_domain_model(
            domain=DomainType.DEVOPS,
            name="OpenMetrics Reference Implementation",
            description="Language model generated from OpenMetrics specification analysis"
        )
        
        # Add terminology from discovery
        for technical_name, business_name in discovery_result.terminology_extracted.items():
            term = TermDefinition(
                technical_name=technical_name,
                business_name=business_name,
                description=f"OpenMetrics concept: {business_name}",
                context="Monitoring and observability",
                domain=DomainType.DEVOPS,
                examples=[f"Used in OpenMetrics exposition format"]
            )
            model.add_term(term)
        
        # Add concepts for each metric type
        for metric_family in discovery_result.metric_families:
            concept = ConceptModel(
                name=metric_family.name,
                definition=metric_family.help_text,
                domain=DomainType.DEVOPS,
                metric_type=self._map_openmetrics_to_metric_type(metric_family.metric_type),
                unit=metric_family.unit or "unknown",
                properties={
                    "openmetrics_type": metric_family.metric_type.value,
                    "labels": metric_family.labels,
                    "exposition_format": "OpenMetrics text format"
                }
            )
            model.add_concept(concept)
        
        # Add aggregation rules for common patterns
        rate_rule = AggregationRule(
            metric_name="request_rate",
            source_metrics=["http_requests_total"],
            aggregation_function=AggregationFunction.CALCULATED,
            window_size_seconds=300,
            calculation_logic="rate(http_requests_total[5m])",
            business_context="Calculate per-second rate of HTTP requests"
        )
        model.add_aggregation_rule(rate_rule)
        
        error_ratio_rule = AggregationRule(
            metric_name="error_ratio",
            source_metrics=["http_requests_total", "http_errors_total"],
            aggregation_function=AggregationFunction.CALCULATED,
            window_size_seconds=300,
            calculation_logic="http_errors_total / http_requests_total",
            business_context="Calculate error rate as ratio of failed to total requests"
        )
        model.add_aggregation_rule(error_ratio_rule)
        
        # Set display preferences
        model.display_preferences = DisplayPreferences(
            chart_colors={
                "counter": "#1f77b4",
                "gauge": "#ff7f0e", 
                "histogram": "#2ca02c",
                "summary": "#d62728"
            },
            label_formats={
                "counter": "{metric_name}_total",
                "gauge": "{metric_name}",
                "histogram": "{metric_name}_bucket",
                "summary": "{metric_name}_quantile"
            },
            unit_displays={
                "seconds": "s",
                "bytes": "B",
                "total": "total",
                "ratio": "ratio"
            }
        )
        
        # Add metadata
        model.metadata = {
            "source": "OpenMetrics Specification 1.0.0",
            "discovery_method": "Specification Analysis",
            "discovery_timestamp": discovery_result.discovery_timestamp.isoformat(),
            "patterns_identified": discovery_result.discovered_patterns,
            "business_concepts": discovery_result.business_concepts,
            "reference_implementation": True
        }
        
        logger.info(f"✅ Generated language model with {len(model.terminology)} terms and {len(model.concepts)} concepts")
        return model
    
    def _map_openmetrics_to_metric_type(self, openmetrics_type: OpenMetricsMetricType) -> MetricType:
        """Map OpenMetrics metric type to our internal metric type."""
        mapping = {
            OpenMetricsMetricType.COUNTER: MetricType.COUNTER,
            OpenMetricsMetricType.GAUGE: MetricType.GAUGE,
            OpenMetricsMetricType.HISTOGRAM: MetricType.HISTOGRAM,
            OpenMetricsMetricType.SUMMARY: MetricType.SUMMARY,
            OpenMetricsMetricType.INFO: MetricType.GAUGE,
            OpenMetricsMetricType.STATE_SET: MetricType.GAUGE,
            OpenMetricsMetricType.UNKNOWN: MetricType.GAUGE
        }
        return mapping.get(openmetrics_type, MetricType.GAUGE)
    
    def get_discovery_audit_trail(self) -> List[DiscoveryAuditRecord]:
        """Get complete audit trail of discovery process."""
        import copy
        return copy.deepcopy(self._audit_records)
    
    def generate_methodology_documentation(self) -> Dict[str, Any]:
        """Generate methodology documentation from audit trail."""
        if not self._audit_records:
            return {"error": "No discovery records available"}
        
        latest_record = self._audit_records[-1]
        
        return {
            "methodology": {
                "name": "OpenMetrics Discovery Methodology",
                "description": "Reference implementation of monitoring system discovery process",
                "version": "1.0.0"
            },
            "process_steps": [
                {
                    "step": 1,
                    "name": "Specification Analysis",
                    "description": "Analyze monitoring system specification or documentation",
                    "inputs": ["OpenMetrics Specification 1.0.0"],
                    "outputs": ["Metric families", "Naming conventions", "Label patterns"]
                },
                {
                    "step": 2,
                    "name": "Terminology Extraction",
                    "description": "Extract technical terms and map to business concepts",
                    "inputs": ["Metric definitions", "Documentation"],
                    "outputs": ["Technical-to-business mapping", "Business concepts"]
                },
                {
                    "step": 3,
                    "name": "Pattern Identification",
                    "description": "Identify usage patterns and best practices",
                    "inputs": ["Metric examples", "Convention analysis"],
                    "outputs": ["Usage patterns", "Best practices", "Anti-patterns"]
                },
                {
                    "step": 4,
                    "name": "Language Model Generation",
                    "description": "Generate domain language model from discoveries",
                    "inputs": ["Terminology", "Concepts", "Patterns"],
                    "outputs": ["Domain language model", "Aggregation rules"]
                }
            ],
            "audit_trail": {
                "discovery_id": latest_record.discovery_id,
                "timestamp": latest_record.timestamp.isoformat(),
                "findings": latest_record.findings,
                "decisions": latest_record.decisions_made,
                "confidence": latest_record.confidence_score,
                "next_steps": latest_record.next_steps
            },
            "replication_guide": {
                "description": "How to apply this methodology to other monitoring systems",
                "steps": [
                    "Replace OpenMetrics specification with target system documentation",
                    "Adapt terminology extraction to target system's naming conventions",
                    "Identify system-specific patterns and best practices",
                    "Generate domain-specific language model",
                    "Validate model with system stakeholders"
                ],
                "tools_required": [
                    "MonitoringDiscoveryEngine",
                    "UbiquitousLanguageEngine",
                    "Target system access or documentation"
                ]
            }
        }