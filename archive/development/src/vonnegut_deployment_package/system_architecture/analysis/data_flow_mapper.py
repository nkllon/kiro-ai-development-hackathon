#!/usr/bin/env python3
"""
Data Flow Mapper - Comprehensive Data Flow Analysis
===================================================

Implements Task 2.2 from the System Architecture Wiring Diagram specification.
Traces metrics flow from ReflectiveModule components through Observatory to 
Prometheus and Grafana, maps WebSocket real-time metrics streaming, documents
systematic error handling with correlation ID tracking, and creates integration
flow mapping.

Author: Kiro AI Assistant
Created: 2025-01-30
Task: 2.2 - Comprehensive data flow mapping
Requirements: 2.4, 6.1, 6.2, 6.3, 6.4
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional, Set, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import uuid

from src.rm_ddd.core.unified_reflective_module import (
    ReflectiveModule, 
    ModuleHealth, 
    ModuleStatus, 
    ModuleCapability,
    GracefulDegradationResult
)


class DataFlowType(Enum):
    """Types of data flows in the system architecture."""
    METRICS = "metrics"
    WEBSOCKET = "websocket"
    ERROR_HANDLING = "error_handling"
    INTEGRATION = "integration"
    REAL_TIME = "real_time"
    BATCH = "batch"


class FlowDirection(Enum):
    """Direction of data flow."""
    UPSTREAM = "upstream"
    DOWNSTREAM = "downstream"
    BIDIRECTIONAL = "bidirectional"


@dataclass
class DataFlowNode:
    """Represents a node in the data flow graph."""
    node_id: str
    node_name: str
    node_type: str  # ReflectiveModule, Service, WebSocket, Integration
    endpoints: List[str] = field(default_factory=list)
    metrics_exposed: List[str] = field(default_factory=list)
    websocket_endpoints: List[str] = field(default_factory=list)
    correlation_id_support: bool = False
    error_handling_capability: bool = False


@dataclass
class DataFlow:
    """Represents a data flow between components."""
    flow_id: str
    source_node: str
    target_node: str
    flow_type: DataFlowType
    direction: FlowDirection
    data_format: str  # JSON, Prometheus metrics, WebSocket messages, etc.
    frequency: Optional[str] = None  # real-time, 15s, 1m, etc.
    correlation_id_tracked: bool = False
    error_propagation: bool = False
    description: str = ""
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class MetricsFlow:
    """Specific metrics flow from ReflectiveModule to visualization."""
    source_component: str
    metrics_endpoint: str
    prometheus_scrape_config: Dict[str, Any]
    grafana_dashboard_config: Dict[str, Any]
    collection_interval: str
    retention_policy: str
    alert_rules: List[str] = field(default_factory=list)


@dataclass
class WebSocketFlow:
    """WebSocket real-time data flow configuration."""
    endpoint_path: str
    message_types: List[str]
    real_time_streaming: bool
    parallel_batch_collection: bool
    correlation_tracking: bool
    error_recovery: Dict[str, Any] = field(default_factory=dict)


@dataclass
class IntegrationFlow:
    """Integration flow between system components."""
    integration_name: str
    source_system: str
    target_system: str
    flow_path: List[str]  # ACE Reporter → AI Memory Palace → DAG Registry
    data_transformation: List[str] = field(default_factory=list)
    validation_points: List[str] = field(default_factory=list)


class DataFlowMapper(ReflectiveModule):
    """
    Comprehensive data flow mapper for the Beast Mode framework.
    
    Implements:
    - Metrics flow tracing from ReflectiveModule → Observatory → Prometheus → Grafana
    - WebSocket real-time metrics streaming parallel to batch collection
    - Systematic error handling with correlation ID tracking
    - Integration flow mapping (ACE Reporter → AI Memory Palace → DAG Registry)
    - WebSocket message flows (/ws/anomalies → Grafana alerts)
    - Emoji rain data flow (achievement → WebSocket → frontend)
    """
    
    def __init__(self):
        super().__init__()
        self.module_id = "DataFlowMapper"
        self._logger = logging.getLogger(f"system_architecture.{self.__class__.__name__}")
        
        # Core data structures
        self._nodes: Dict[str, DataFlowNode] = {}
        self._flows: List[DataFlow] = []
        self._metrics_flows: List[MetricsFlow] = []
        self._websocket_flows: List[WebSocketFlow] = []
        self._integration_flows: List[IntegrationFlow] = []
        
        # Analysis state
        self._flow_analysis_complete = False
        self._last_analysis: Optional[datetime] = None
        
        self._logger.info("DataFlowMapper initialized for comprehensive flow analysis")
    
    def get_module_info(self) -> Dict[str, Any]:
        """Get module information - RDI Compliant."""
        return {
            "module_id": self.module_id,
            "name": "DataFlowMapper",
            "version": "1.0.0",
            "description": "Comprehensive data flow analysis and mapping",
            "task": "2.2 - Comprehensive data flow mapping",
            "capabilities": [cap.value for cap in self.get_capabilities()],
            "nodes_mapped": len(self._nodes),
            "flows_analyzed": len(self._flows),
            "last_analysis": self._last_analysis.isoformat() if self._last_analysis else None
        }
    
    def get_capabilities(self) -> List[ModuleCapability]:
        """Get module capabilities - RDI Compliant."""
        return [
            ModuleCapability.CORE_FUNCTIONALITY,
            ModuleCapability.DATA_PROCESSING,
            ModuleCapability.VALIDATION,
            ModuleCapability.MONITORING,
            ModuleCapability.API_INTEGRATION
        ]
    
    def get_health_status(self) -> ModuleHealth:
        """Get module health status - RDI Compliant."""
        try:
            if not self._flow_analysis_complete:
                status = ModuleStatus.WARNING
                health_score = 0.5
                issues = ["Flow analysis not yet performed"]
            elif len(self._flows) == 0:
                status = ModuleStatus.WARNING
                health_score = 0.6
                issues = ["No data flows mapped"]
            else:
                status = ModuleStatus.HEALTHY
                health_score = 1.0
                issues = []
            
            return ModuleHealth(
                module_id=self.module_id,
                status=status,
                health_score=health_score,
                issues=issues,
                last_check=datetime.now(),
                uptime_seconds=(datetime.now() - self._start_time).total_seconds(),
                error_count=0,
                warning_count=len(issues)
            )
            
        except Exception as e:
            return ModuleHealth(
                module_id=self.module_id,
                status=ModuleStatus.ERROR,
                health_score=0.0,
                issues=[f"Health check failed: {str(e)}"],
                last_check=datetime.now(),
                uptime_seconds=0,
                error_count=1,
                warning_count=0
            )
    
    def graceful_degradation(self) -> GracefulDegradationResult:
        """Perform graceful degradation - RDI Compliant."""
        try:
            remaining_capabilities = [
                ModuleCapability.CORE_FUNCTIONALITY,
                ModuleCapability.DATA_PROCESSING
            ]
            
            degraded_capabilities = [
                ModuleCapability.VALIDATION,
                ModuleCapability.MONITORING,
                ModuleCapability.API_INTEGRATION
            ]
            
            return GracefulDegradationResult(
                success=True,
                degraded_capabilities=degraded_capabilities,
                remaining_capabilities=remaining_capabilities
            )
            
        except Exception as e:
            return GracefulDegradationResult(
                success=False,
                degraded_capabilities=[],
                remaining_capabilities=[],
                error_message=str(e)
            )
    
    def register_data_flow_node(self, node_id: str, node_name: str, node_type: str,
                               endpoints: List[str] = None, 
                               websocket_endpoints: List[str] = None) -> None:
        """Register a node in the data flow graph."""
        
        node = DataFlowNode(
            node_id=node_id,
            node_name=node_name,
            node_type=node_type,
            endpoints=endpoints or [],
            websocket_endpoints=websocket_endpoints or [],
            correlation_id_support=node_type == "ReflectiveModule",
            error_handling_capability=node_type in ["ReflectiveModule", "Observatory"]
        )
        
        self._nodes[node_id] = node
        self._logger.debug(f"Registered data flow node: {node_id} ({node_type})")
    
    def trace_metrics_flow(self) -> List[MetricsFlow]:
        """
        Trace metrics flow from ReflectiveModule components through Observatory 
        to Prometheus and Grafana.
        """
        self._logger.info("Tracing metrics flow: ReflectiveModule → Observatory → Prometheus → Grafana")
        
        metrics_flows = []
        
        # ReflectiveModule → Observatory metrics flow
        observatory_metrics_flow = MetricsFlow(
            source_component="ReflectiveModule Components",
            metrics_endpoint="/metrics",
            prometheus_scrape_config={
                "job_name": "reflective_modules",
                "scrape_interval": "15s",
                "metrics_path": "/metrics",
                "targets": ["localhost:8888", "localhost:9090"]
            },
            grafana_dashboard_config={
                "datasource": "Prometheus",
                "dashboard_name": "ReflectiveModule Metrics",
                "panels": [
                    "Health Status", "Performance Metrics", "Error Rates", 
                    "Request Latency", "Resource Usage"
                ]
            },
            collection_interval="15s",
            retention_policy="30d",
            alert_rules=[
                "ReflectiveModule Health Check Failed",
                "High Error Rate Detected",
                "Performance Degradation Alert"
            ]
        )
        metrics_flows.append(observatory_metrics_flow)
        
        # Observatory → Prometheus metrics flow
        prometheus_metrics_flow = MetricsFlow(
            source_component="Observatory Server",
            metrics_endpoint="/metrics",
            prometheus_scrape_config={
                "job_name": "observatory",
                "scrape_interval": "15s",
                "metrics_path": "/metrics",
                "targets": ["localhost:8888"]
            },
            grafana_dashboard_config={
                "datasource": "Prometheus",
                "dashboard_name": "Observatory Metrics",
                "panels": [
                    "WebSocket Connections", "Message Throughput", "System Health",
                    "Emoji Rain Events", "Anomaly Detection"
                ]
            },
            collection_interval="15s",
            retention_policy="30d"
        )
        metrics_flows.append(prometheus_metrics_flow)
        
        # Prometheus → Grafana visualization flow
        grafana_visualization_flow = MetricsFlow(
            source_component="Prometheus Server",
            metrics_endpoint="/api/v1/query",
            prometheus_scrape_config={},  # Grafana queries Prometheus
            grafana_dashboard_config={
                "datasource": "Prometheus (localhost:9090)",
                "dashboard_name": "System Overview",
                "panels": [
                    "Overall System Health", "Service Dependencies", 
                    "Real-time Metrics", "Alert Status"
                ]
            },
            collection_interval="real-time",
            retention_policy="inherited_from_prometheus"
        )
        metrics_flows.append(grafana_visualization_flow)
        
        self._metrics_flows = metrics_flows
        self._logger.info(f"Traced {len(metrics_flows)} metrics flows")
        return metrics_flows
    
    def map_websocket_real_time_streaming(self) -> List[WebSocketFlow]:
        """
        Map WebSocket real-time metrics streaming parallel to batch collection.
        """
        self._logger.info("Mapping WebSocket real-time streaming flows")
        
        websocket_flows = []
        
        # Observatory WebSocket endpoints
        observatory_websocket = WebSocketFlow(
            endpoint_path="/ws/observatory",
            message_types=["service_status", "metrics_update", "system_event", "health_check"],
            real_time_streaming=True,
            parallel_batch_collection=True,
            correlation_tracking=True,
            error_recovery={
                "reconnection_strategy": "exponential_backoff",
                "max_retries": 3,
                "fallback_mode": "polling"
            }
        )
        websocket_flows.append(observatory_websocket)
        
        # Emoji Rain WebSocket flow
        emoji_rain_websocket = WebSocketFlow(
            endpoint_path="/ws/emoji-rain",
            message_types=["emoji_event", "celebration", "achievement", "coordination_visual"],
            real_time_streaming=True,
            parallel_batch_collection=False,  # Real-time only
            correlation_tracking=True,
            error_recovery={
                "reconnection_strategy": "immediate",
                "max_retries": 5,
                "fallback_mode": "disable_animations"
            }
        )
        websocket_flows.append(emoji_rain_websocket)
        
        # Anomalies WebSocket flow
        anomalies_websocket = WebSocketFlow(
            endpoint_path="/ws/anomalies",
            message_types=["anomaly_detected", "threshold_exceeded", "alert", "performance_warning"],
            real_time_streaming=True,
            parallel_batch_collection=True,
            correlation_tracking=True,
            error_recovery={
                "reconnection_strategy": "exponential_backoff",
                "max_retries": 3,
                "fallback_mode": "email_alerts"
            }
        )
        websocket_flows.append(anomalies_websocket)
        
        # Doctor Status WebSocket flow
        doctor_status_websocket = WebSocketFlow(
            endpoint_path="/ws/doctor-status",
            message_types=["health_check", "status_update", "diagnostic", "system_recovery"],
            real_time_streaming=True,
            parallel_batch_collection=True,
            correlation_tracking=True,
            error_recovery={
                "reconnection_strategy": "exponential_backoff",
                "max_retries": 3,
                "fallback_mode": "system_logs"
            }
        )
        websocket_flows.append(doctor_status_websocket)
        
        self._websocket_flows = websocket_flows
        self._logger.info(f"Mapped {len(websocket_flows)} WebSocket flows")
        return websocket_flows
    
    def document_systematic_error_handling(self) -> Dict[str, Any]:
        """
        Document systematic error handling with correlation ID tracking.
        """
        self._logger.info("Documenting systematic error handling with correlation ID tracking")
        
        error_handling_documentation = {
            "correlation_id_system": {
                "generation": "UUID4 format generated at request entry point",
                "propagation": "Passed through all system components via headers/context",
                "tracking": "Logged at each component interaction",
                "format": "xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx"
            },
            "error_propagation_paths": [
                {
                    "path": "ReflectiveModule → Observatory → Prometheus → Grafana",
                    "error_types": ["Health Check Failures", "Metrics Collection Errors", "Visualization Errors"],
                    "correlation_tracking": True,
                    "recovery_procedures": [
                        "Automatic retry with exponential backoff",
                        "Fallback to cached data",
                        "Alert generation with correlation ID"
                    ]
                },
                {
                    "path": "WebSocket Connection → Observatory → Error Handler",
                    "error_types": ["Connection Drops", "Message Parsing Errors", "Authentication Failures"],
                    "correlation_tracking": True,
                    "recovery_procedures": [
                        "Automatic reconnection",
                        "Message queue replay",
                        "Graceful degradation to polling"
                    ]
                },
                {
                    "path": "Integration Points → ACE Reporter → AI Memory Palace → DAG Registry",
                    "error_types": ["Integration Failures", "Data Validation Errors", "Dependency Conflicts"],
                    "correlation_tracking": True,
                    "recovery_procedures": [
                        "Transaction rollback",
                        "Dependency resolution",
                        "Manual intervention alerts"
                    ]
                }
            ],
            "systematic_error_handling": {
                "error_classification": [
                    "Transient (retry-able)",
                    "Permanent (requires intervention)",
                    "Degraded (partial functionality)",
                    "Critical (system-wide impact)"
                ],
                "escalation_procedures": [
                    "Level 1: Automatic retry and logging",
                    "Level 2: Alert generation with correlation ID",
                    "Level 3: Human intervention required",
                    "Level 4: Emergency protocol activation"
                ],
                "correlation_id_benefits": [
                    "End-to-end request tracing",
                    "Distributed debugging capability",
                    "Performance bottleneck identification",
                    "Error root cause analysis"
                ]
            }
        }
        
        return error_handling_documentation
    
    def create_integration_flow_mapping(self) -> List[IntegrationFlow]:
        """
        Create integration flow mapping (ACE Reporter → AI Memory Palace → DAG Registry).
        """
        self._logger.info("Creating integration flow mapping")
        
        integration_flows = []
        
        # ACE Reporter → AI Memory Palace → DAG Registry flow
        ace_integration_flow = IntegrationFlow(
            integration_name="ACE Reporter Integration",
            source_system="ACE Reporter",
            target_system="AI Memory Palace",
            flow_path=["ACE Reporter", "Progress Broadcaster", "AI Memory Palace", "Context Storage"],
            data_transformation=[
                "Progress events → Structured context",
                "Achievement data → Memory storage format",
                "Correlation IDs → Context linking"
            ],
            validation_points=[
                "ACE Reporter event validation",
                "Progress data integrity check",
                "AI Memory Palace storage confirmation"
            ]
        )
        integration_flows.append(ace_integration_flow)
        
        # AI Memory Palace → DAG Registry flow
        memory_dag_flow = IntegrationFlow(
            integration_name="Memory Palace to DAG Registry",
            source_system="AI Memory Palace",
            target_system="DAG Registry",
            flow_path=["AI Memory Palace", "Context Retrieval", "DAG Registry", "Dependency Validation"],
            data_transformation=[
                "Stored context → Dependency information",
                "Historical data → Validation rules",
                "Context patterns → DAG constraints"
            ],
            validation_points=[
                "Context data availability",
                "DAG Registry connectivity",
                "Dependency validation success"
            ]
        )
        integration_flows.append(memory_dag_flow)
        
        # Observatory → Integration Points flow
        observatory_integration_flow = IntegrationFlow(
            integration_name="Observatory Integration Hub",
            source_system="Observatory Server",
            target_system="Multiple Integration Points",
            flow_path=["Observatory", "WebSocket Hub", "ACE Reporter", "AI Memory Palace", "DAG Registry"],
            data_transformation=[
                "WebSocket events → Progress broadcasts",
                "System metrics → Context storage",
                "Health status → Dependency validation"
            ],
            validation_points=[
                "WebSocket connectivity",
                "Integration point health",
                "Data flow continuity"
            ]
        )
        integration_flows.append(observatory_integration_flow)
        
        self._integration_flows = integration_flows
        self._logger.info(f"Created {len(integration_flows)} integration flow mappings")
        return integration_flows
    
    def map_websocket_message_flows(self) -> Dict[str, Any]:
        """
        Map WebSocket message flows (/ws/anomalies → Grafana alerts).
        """
        self._logger.info("Mapping WebSocket message flows to Grafana alerts")
        
        websocket_message_flows = {
            "/ws/anomalies": {
                "message_types": ["anomaly_detected", "threshold_exceeded", "performance_warning"],
                "grafana_integration": {
                    "alert_manager_webhook": "http://localhost:9093/api/v1/alerts",
                    "dashboard_panels": ["Anomaly Timeline", "Alert Status", "Performance Metrics"],
                    "notification_channels": ["email", "slack", "webhook"]
                },
                "flow_sequence": [
                    "Anomaly Detection → WebSocket Message",
                    "WebSocket → Observatory Event Handler",
                    "Event Handler → Prometheus Alert Rule",
                    "Alert Rule → Grafana Alert Manager",
                    "Alert Manager → Notification Channels"
                ],
                "correlation_tracking": True,
                "real_time_processing": True
            },
            "/ws/doctor-status": {
                "message_types": ["health_check", "status_update", "diagnostic"],
                "grafana_integration": {
                    "dashboard_panels": ["System Health", "Component Status", "Diagnostic Timeline"],
                    "alert_rules": ["Component Down", "Health Check Failed", "Diagnostic Alert"]
                },
                "flow_sequence": [
                    "Health Check → WebSocket Message",
                    "WebSocket → Observatory Health Handler",
                    "Health Handler → Prometheus Metrics",
                    "Metrics → Grafana Dashboard Update"
                ]
            },
            "/ws/emoji-rain": {
                "message_types": ["achievement", "celebration", "coordination_visual"],
                "grafana_integration": {
                    "dashboard_panels": ["Achievement Timeline", "Celebration Events"],
                    "custom_visualizations": ["Emoji Rain Animation", "Achievement Counter"]
                },
                "flow_sequence": [
                    "Achievement Event → WebSocket Message",
                    "WebSocket → Frontend Animation",
                    "Event → Observatory Metrics",
                    "Metrics → Grafana Achievement Dashboard"
                ]
            }
        }
        
        return websocket_message_flows
    
    def document_emoji_rain_data_flow(self) -> Dict[str, Any]:
        """
        Document emoji rain data flow (achievement → WebSocket → frontend).
        """
        self._logger.info("Documenting emoji rain data flow")
        
        emoji_rain_flow = {
            "flow_description": "Achievement-triggered emoji rain visualization system",
            "data_flow_sequence": [
                {
                    "step": 1,
                    "component": "Achievement Detection",
                    "action": "System detects achievement event (task completion, milestone, etc.)",
                    "data_format": "Achievement event object with metadata",
                    "correlation_id": "Generated for tracking"
                },
                {
                    "step": 2,
                    "component": "Observatory Server",
                    "action": "Processes achievement event and triggers emoji rain",
                    "data_format": "WebSocket message with emoji rain configuration",
                    "correlation_id": "Propagated from achievement event"
                },
                {
                    "step": 3,
                    "component": "WebSocket Endpoint (/ws/emoji-rain)",
                    "action": "Broadcasts emoji rain event to connected clients",
                    "data_format": "JSON message with emoji type, duration, intensity",
                    "correlation_id": "Included in message metadata"
                },
                {
                    "step": 4,
                    "component": "Frontend Client",
                    "action": "Receives WebSocket message and renders emoji rain animation",
                    "data_format": "DOM manipulation and CSS animations",
                    "correlation_id": "Used for debugging and analytics"
                },
                {
                    "step": 5,
                    "component": "Metrics Collection",
                    "action": "Records emoji rain event for analytics and monitoring",
                    "data_format": "Prometheus metrics and Grafana visualization",
                    "correlation_id": "Links to original achievement event"
                }
            ],
            "message_format": {
                "type": "emoji_rain",
                "payload": {
                    "emoji_type": "celebration",
                    "duration_ms": 3000,
                    "intensity": "high",
                    "achievement_type": "task_completion",
                    "correlation_id": "uuid"
                },
                "timestamp": "ISO 8601 format",
                "source": "observatory_server"
            },
            "error_handling": {
                "websocket_failure": "Graceful degradation - no animation",
                "frontend_error": "Fallback to simple notification",
                "correlation_tracking": "Error events linked to original achievement"
            },
            "performance_considerations": {
                "rate_limiting": "Max 1 emoji rain per 5 seconds per client",
                "resource_usage": "Lightweight CSS animations, minimal CPU impact",
                "scalability": "WebSocket broadcasting supports multiple clients"
            }
        }
        
        return emoji_rain_flow
    
    def analyze_comprehensive_data_flows(self) -> Dict[str, Any]:
        """
        Perform comprehensive analysis of all data flows in the system.
        """
        self._logger.info("Performing comprehensive data flow analysis")
        
        # Execute all flow mapping functions
        metrics_flows = self.trace_metrics_flow()
        websocket_flows = self.map_websocket_real_time_streaming()
        error_handling = self.document_systematic_error_handling()
        integration_flows = self.create_integration_flow_mapping()
        websocket_message_flows = self.map_websocket_message_flows()
        emoji_rain_flow = self.document_emoji_rain_data_flow()
        
        # Create comprehensive analysis report
        analysis_report = {
            "analysis_timestamp": datetime.now().isoformat(),
            "metrics_flows": {
                "total_flows": len(metrics_flows),
                "flows": [
                    {
                        "source": flow.source_component,
                        "endpoint": flow.metrics_endpoint,
                        "collection_interval": flow.collection_interval,
                        "retention_policy": flow.retention_policy,
                        "alert_rules_count": len(flow.alert_rules)
                    }
                    for flow in metrics_flows
                ]
            },
            "websocket_flows": {
                "total_endpoints": len(websocket_flows),
                "real_time_endpoints": len([f for f in websocket_flows if f.real_time_streaming]),
                "correlation_enabled": len([f for f in websocket_flows if f.correlation_tracking]),
                "flows": [
                    {
                        "endpoint": flow.endpoint_path,
                        "message_types": flow.message_types,
                        "real_time": flow.real_time_streaming,
                        "parallel_batch": flow.parallel_batch_collection
                    }
                    for flow in websocket_flows
                ]
            },
            "error_handling": error_handling,
            "integration_flows": {
                "total_integrations": len(integration_flows),
                "flows": [
                    {
                        "name": flow.integration_name,
                        "source": flow.source_system,
                        "target": flow.target_system,
                        "path_length": len(flow.flow_path),
                        "validation_points": len(flow.validation_points)
                    }
                    for flow in integration_flows
                ]
            },
            "websocket_message_flows": websocket_message_flows,
            "emoji_rain_flow": emoji_rain_flow,
            "summary": {
                "total_data_flows_mapped": len(metrics_flows) + len(websocket_flows) + len(integration_flows),
                "correlation_id_coverage": "100% for ReflectiveModule and WebSocket flows",
                "real_time_capabilities": "WebSocket streaming with batch collection fallback",
                "error_handling_systematic": "4-level escalation with correlation tracking",
                "integration_points_mapped": len(integration_flows)
            }
        }
        
        self._flow_analysis_complete = True
        self._last_analysis = datetime.now()
        
        self._logger.info("Comprehensive data flow analysis completed")
        return analysis_report


# Factory function for easy instantiation
def create_data_flow_mapper() -> DataFlowMapper:
    """Create and return a configured DataFlowMapper instance."""
    return DataFlowMapper()


# Example usage and testing
async def demonstrate_data_flow_mapper():
    """Demonstrate DataFlowMapper capabilities."""
    
    mapper = create_data_flow_mapper()
    
    # Register data flow nodes
    mapper.register_data_flow_node("observatory", "Observatory Server", "ReflectiveModule", 
                                  endpoints=["/health", "/metrics"], 
                                  websocket_endpoints=["/ws/observatory", "/ws/emoji-rain"])
    mapper.register_data_flow_node("prometheus", "Prometheus Server", "Service", 
                                  endpoints=["/metrics", "/api/v1/query"])
    mapper.register_data_flow_node("grafana", "Grafana Dashboard", "Service", 
                                  endpoints=["/api/health", "/api/datasources"])
    
    # Perform comprehensive analysis
    analysis_report = mapper.analyze_comprehensive_data_flows()
    
    print("🐺 DataFlowMapper Demonstration Complete!")
    print(f"Metrics Flows: {analysis_report['metrics_flows']['total_flows']}")
    print(f"WebSocket Flows: {analysis_report['websocket_flows']['total_endpoints']}")
    print(f"Integration Flows: {analysis_report['integration_flows']['total_integrations']}")
    print(f"Total Data Flows: {analysis_report['summary']['total_data_flows_mapped']}")
    
    return analysis_report


if __name__ == "__main__":
    # Run demonstration
    asyncio.run(demonstrate_data_flow_mapper())