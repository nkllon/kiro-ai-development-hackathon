"""
Data Flow Mapper - Comprehensive Data Flow Mapping Implementation.

This module implements Task 2.2: Comprehensive Data Flow Mapping for the 
system-architecture-wiring-diagram specification. It traces metrics flow from 
ReflectiveModule components through Observatory to Prometheus and Grafana, maps 
WebSocket real-time metrics streaming, documents systematic error handling with 
correlation ID tracking, and creates integration flow mapping.
"""

import asyncio
import json
import logging
import time
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Set, Tuple
from uuid import uuid4

from src.rm_ddd.core.unified_reflective_module import ReflectiveModule
from ..models.data_flow import (
    DataFlowGraph, DataFlowNode, DataFlowEdge, MetricsFlow, WebSocketFlow,
    ErrorFlow, IntegrationFlow, WebSocketMessageFlow, EmojiRainFlow,
    DataFlowType, FlowDirection, FlowPriority, ErrorSeverity
)
from ..discovery.infrastructure_discoverer import InfrastructureDiscoverer
from ..discovery.observatory_websocket_client import ObservatoryWebSocketClient

logger = logging.getLogger(__name__)


@dataclass
class DataFlowMappingConfig:
    """Configuration for data flow mapping."""
    enable_real_time_mapping: bool = True
    enable_error_tracking: bool = True
    enable_performance_monitoring: bool = True
    mapping_interval_seconds: int = 30
    correlation_id_tracking: bool = True
    websocket_endpoints: List[str] = None
    prometheus_endpoint: str = "http://localhost:9090"
    grafana_endpoint: str = "http://localhost:3000"
    observatory_endpoint: str = "http://localhost:8888"
    
    def __post_init__(self):
        if self.websocket_endpoints is None:
            self.websocket_endpoints = [
                "/ws/observatory",
                "/ws/anomalies", 
                "/ws/emoji-rain",
                "/ws/doctor-status"
            ]


class DataFlowMapper(ReflectiveModule):
    """
    Comprehensive Data Flow Mapper for System Architecture Wiring Diagram.
    
    Implements Task 2.2 requirements:
    - Trace metrics flow: ReflectiveModule components → Observatory → Prometheus → Grafana
    - Map WebSocket real-time metrics streaming parallel to batch collection
    - Document systematic error handling with correlation ID tracking
    - Create integration flow mapping (ACE Reporter → AI Memory Palace → DAG Registry)
    - Map WebSocket message flows (/ws/anomalies → Grafana alerts)
    - Document emoji rain data flow (achievement → WebSocket → frontend)
    """
    
    def __init__(self, config: Optional[DataFlowMappingConfig] = None):
        super().__init__()
        self.module_id = "data_flow_mapper"
        self._config = config or DataFlowMappingConfig()
        
        # Core components
        self._infrastructure_discoverer: Optional[InfrastructureDiscoverer] = None
        self._websocket_client: Optional[ObservatoryWebSocketClient] = None
        
        # Data flow graph
        self._data_flow_graph: Optional[DataFlowGraph] = None
        
        # Mapping state
        self._mapping_active = False
        self._mapping_task: Optional[asyncio.Task] = None
        self._last_mapping_time: Optional[datetime] = None
        
        # Performance tracking
        self._mapping_start_time = time.time()
        self._flows_mapped = 0
        self._mapping_errors = 0
        self._last_mapping_duration = 0.0
        
        # Error tracking with correlation IDs
        self._error_correlation_map: Dict[str, str] = {}
        self._active_error_flows: Dict[str, ErrorFlow] = {}
        
        logger.info("🔍 DataFlowMapper initialized - Ready to map comprehensive data flows")
    
    async def start_mapping(self) -> bool:
        """Start comprehensive data flow mapping."""
        try:
            if self._mapping_active:
                logger.warning("DataFlowMapper is already active")
                return True
            
            # Initialize infrastructure discoverer
            self._infrastructure_discoverer = InfrastructureDiscoverer()
            await self._infrastructure_discoverer.start_discovery()
            
            # Initialize WebSocket client
            self._websocket_client = ObservatoryWebSocketClient(
                base_url=f"ws://localhost:8888"
            )
            await self._websocket_client.connect_to_endpoints()
            
            # Initialize data flow graph
            self._data_flow_graph = DataFlowGraph(
                graph_id=str(uuid4()),
                graph_name="Beast Mode Framework Data Flow Graph"
            )
            
            # Start mapping task
            self._mapping_active = True
            self._mapping_task = asyncio.create_task(self._mapping_loop())
            
            logger.info("🚀 DataFlowMapper started - mapping comprehensive data flows")
            return True
            
        except Exception as e:
            logger.error(f"Failed to start DataFlowMapper: {e}")
            return False
    
    async def stop_mapping(self) -> None:
        """Stop data flow mapping gracefully."""
        logger.info("🛑 Stopping DataFlowMapper...")
        
        self._mapping_active = False
        
        # Cancel mapping task
        if self._mapping_task and not self._mapping_task.done():
            self._mapping_task.cancel()
        
        # Wait for task to complete
        if self._mapping_task:
            await asyncio.gather(self._mapping_task, return_exceptions=True)
        
        # Stop infrastructure discoverer
        if self._infrastructure_discoverer:
            await self._infrastructure_discoverer.stop_discovery()
        
        # Disconnect WebSocket client
        if self._websocket_client:
            await self._websocket_client.disconnect()
        
        logger.info("✅ DataFlowMapper stopped gracefully")
    
    async def _mapping_loop(self) -> None:
        """Main loop for comprehensive data flow mapping."""
        logger.info("📊 Starting comprehensive data flow mapping loop")
        
        while self._mapping_active:
            mapping_start = time.time()
            
            try:
                # Perform comprehensive mapping
                await self._perform_comprehensive_mapping()
                
                # Track performance
                self._last_mapping_duration = time.time() - mapping_start
                self._last_mapping_time = datetime.now()
                
                # Sleep for mapping interval
                await asyncio.sleep(self._config.mapping_interval_seconds)
                
            except asyncio.CancelledError:
                logger.info("Data flow mapping loop cancelled")
                break
            except Exception as e:
                logger.error(f"Error in mapping loop: {e}")
                self._mapping_errors += 1
                await asyncio.sleep(5)  # Brief pause on error
        
        logger.info("Data flow mapping loop stopped")
    
    async def _perform_comprehensive_mapping(self) -> None:
        """Perform comprehensive data flow mapping."""
        try:
            # Map infrastructure nodes
            await self._map_infrastructure_nodes()
            
            # Map metrics flows
            await self._map_metrics_flows()
            
            # Map WebSocket flows
            await self._map_websocket_flows()
            
            # Map error flows
            await self._map_error_flows()
            
            # Map integration flows
            await self._map_integration_flows()
            
            # Map WebSocket message flows
            await self._map_websocket_message_flows()
            
            # Map emoji rain flows
            await self._map_emoji_rain_flows()
            
            # Update graph metadata
            self._update_graph_metadata()
            
            self._flows_mapped += 1
            
        except Exception as e:
            logger.error(f"Error during comprehensive mapping: {e}")
            raise
    
    async def _map_infrastructure_nodes(self) -> None:
        """Map infrastructure nodes from discovery results."""
        if not self._infrastructure_discoverer:
            return
        
        # Get discovered services
        discovered_services = self._infrastructure_discoverer.get_discovered_services()
        
        for service_name, service_info in discovered_services.items():
            node = DataFlowNode(
                node_id=service_name,
                node_name=service_info.name,
                node_type=service_info.name,
                endpoint=f"http://localhost:{service_info.port}" if service_info.port else None,
                port=service_info.port,
                health_endpoint=service_info.health_endpoint,
                websocket_endpoints=self._get_websocket_endpoints_for_service(service_info.name),
                capabilities=self._get_capabilities_for_service(service_info.name),
                dependencies=service_info.dependencies,
                metadata={
                    "process_id": service_info.process_id,
                    "config_files": service_info.config_files,
                    "validation_status": service_info.validation_status,
                    "last_validated": service_info.last_validated.isoformat() if service_info.last_validated else None
                },
                validation_status=service_info.validation_status,
                accuracy_score=0.9 if service_info.validation_status == "active" else 0.5
            )
            
            self._data_flow_graph.add_node(node)
        
        logger.debug(f"Mapped {len(discovered_services)} infrastructure nodes")
    
    async def _map_metrics_flows(self) -> None:
        """Map metrics flow: ReflectiveModule components → Observatory → Prometheus → Grafana."""
        try:
            # Create metrics flow
            metrics_flow = MetricsFlow(
                flow_id=f"metrics_flow_{uuid4()}",
                source_component="ReflectiveModule Components",
                target_systems=["Observatory", "Prometheus", "Grafana"],
                metrics_types=[
                    "health_score", "uptime_seconds", "error_count", "warning_count",
                    "memory_usage_mb", "cpu_usage_percent", "operation_count",
                    "performance_metrics", "usage_tracking"
                ],
                collection_interval_seconds=15.0,
                retention_period_days=30,
                flow_path=[
                    "ReflectiveModule Components",
                    "Observatory Server",
                    "Prometheus Server", 
                    "Grafana Dashboard"
                ],
                parallel_streams=[
                    "/ws/observatory",
                    "/ws/doctor-status"
                ],
                batch_collection_enabled=True,
                real_time_streaming_enabled=True,
                compression_enabled=True,
                error_correlation_id=str(uuid4()),
                error_propagation_path=[
                    "ReflectiveModule → Observatory",
                    "Observatory → Prometheus",
                    "Prometheus → Grafana"
                ],
                fallback_mechanisms=[
                    "Redis failover",
                    "WebSocket reconnection",
                    "Batch collection fallback"
                ]
            )
            
            self._data_flow_graph.add_metrics_flow(metrics_flow)
            
            # Create edges for metrics flow
            await self._create_metrics_flow_edges(metrics_flow)
            
            logger.debug("Mapped metrics flow: ReflectiveModule → Observatory → Prometheus → Grafana")
            
        except Exception as e:
            logger.error(f"Error mapping metrics flows: {e}")
    
    async def _map_websocket_flows(self) -> None:
        """Map WebSocket real-time metrics streaming parallel to batch collection."""
        try:
            for endpoint in self._config.websocket_endpoints:
                websocket_flow = WebSocketFlow(
                    flow_id=f"websocket_flow_{endpoint.replace('/', '_')}_{uuid4()}",
                    endpoint=endpoint,
                    message_types=self._get_message_types_for_endpoint(endpoint),
                    streaming_frequency_ms=1000,
                    message_format="json",
                    compression_enabled=True,
                    parallel_to_batch=True,
                    batch_collection_endpoint=f"http://localhost:8888/api/metrics",
                    real_time_endpoint=f"ws://localhost:8888{endpoint}",
                    connection_pool_size=5,
                    retry_policy={
                        "max_attempts": 10,
                        "base_delay": 1.0,
                        "max_delay": 60.0,
                        "multiplier": 2.0
                    },
                    heartbeat_interval_seconds=30,
                    error_correlation_id=str(uuid4()),
                    reconnection_strategy="exponential_backoff",
                    fallback_to_batch=True
                )
                
                self._data_flow_graph.add_websocket_flow(websocket_flow)
            
            logger.debug(f"Mapped {len(self._config.websocket_endpoints)} WebSocket flows")
            
        except Exception as e:
            logger.error(f"Error mapping WebSocket flows: {e}")
    
    async def _map_error_flows(self) -> None:
        """Map systematic error handling with correlation ID tracking."""
        try:
            # Create error flow for systematic error handling
            error_flow = ErrorFlow(
                error_id=f"systematic_error_flow_{uuid4()}",
                correlation_id=str(uuid4()),
                error_type="systematic_error_handling",
                severity=ErrorSeverity.ERROR,
                source_component="ReflectiveModule",
                propagation_path=[
                    "ReflectiveModule",
                    "Observatory Error Handler",
                    "Prometheus Alert Manager",
                    "Grafana Alerting"
                ],
                affected_components=[
                    "Observatory Server",
                    "Prometheus Server",
                    "Grafana Dashboard",
                    "WebSocket Connections"
                ],
                error_message="Systematic error handling with correlation ID tracking",
                error_code="SYS_ERROR_001",
                context_data={
                    "error_tracking_enabled": True,
                    "correlation_id_tracking": True,
                    "error_propagation_enabled": True,
                    "fallback_mechanisms": [
                        "Redis failover",
                        "WebSocket reconnection",
                        "Service isolation"
                    ]
                },
                recovery_actions=[
                    "Automatic retry with exponential backoff",
                    "Fallback to batch collection",
                    "Service isolation and recovery",
                    "Manual intervention if required"
                ],
                fallback_activated=False,
                manual_intervention_required=False,
                impact_score=0.3,  # Moderate impact
                affected_users=0,
                service_degradation=False,
                tags=["systematic", "error_handling", "correlation_id"],
                metadata={
                    "tracking_enabled": True,
                    "correlation_map_size": len(self._error_correlation_map),
                    "active_error_flows": len(self._active_error_flows)
                }
            )
            
            self._data_flow_graph.add_error_flow(error_flow)
            
            logger.debug("Mapped systematic error handling flow with correlation ID tracking")
            
        except Exception as e:
            logger.error(f"Error mapping error flows: {e}")
    
    async def _map_integration_flows(self) -> None:
        """Map integration flow: ACE Reporter → AI Memory Palace → DAG Registry."""
        try:
            integration_flow = IntegrationFlow(
                flow_id=f"integration_flow_{uuid4()}",
                integration_name="ACE Reporter to AI Memory Palace to DAG Registry",
                source_system="ACE Reporter",
                target_systems=["AI Memory Palace", "DAG Registry"],
                integration_type="data_sync",
                data_format="json",
                transport_protocol="http",
                flow_sequence=[
                    "ACE Reporter",
                    "AI Memory Palace",
                    "DAG Registry"
                ],
                dependencies=[
                    "ACE Reporter must be active",
                    "AI Memory Palace must be accessible",
                    "DAG Registry must be available"
                ],
                processing_mode="sequential",
                batch_processing_enabled=True,
                real_time_processing_enabled=True,
                error_correlation_id=str(uuid4()),
                retry_policy={
                    "max_attempts": 5,
                    "base_delay": 2.0,
                    "max_delay": 30.0,
                    "multiplier": 1.5
                },
                circuit_breaker_enabled=True
            )
            
            self._data_flow_graph.add_integration_flow(integration_flow)
            
            logger.debug("Mapped integration flow: ACE Reporter → AI Memory Palace → DAG Registry")
            
        except Exception as e:
            logger.error(f"Error mapping integration flows: {e}")
    
    async def _map_websocket_message_flows(self) -> None:
        """Map WebSocket message flows: /ws/anomalies → Grafana alerts."""
        try:
            websocket_message_flow = WebSocketMessageFlow(
                flow_id=f"websocket_message_flow_{uuid4()}",
                source_endpoint="/ws/anomalies",
                target_system="Grafana",
                message_type="anomaly_alert",
                message_format="json",
                priority=FlowPriority.HIGH,
                real_time_enabled=True,
                batch_processing_enabled=False,
                compression_enabled=True,
                alert_rules=[
                    {
                        "rule_name": "anomaly_detection",
                        "condition": "anomaly_score > 0.8",
                        "severity": "warning"
                    },
                    {
                        "rule_name": "critical_anomaly",
                        "condition": "anomaly_score > 0.95",
                        "severity": "critical"
                    }
                ],
                notification_channels=[
                    "grafana_alerts",
                    "websocket_broadcast",
                    "email_notifications"
                ],
                escalation_policy={
                    "immediate": ["websocket_broadcast"],
                    "5_minutes": ["email_notifications"],
                    "15_minutes": ["pager_duty"]
                },
                error_correlation_id=str(uuid4()),
                fallback_notification="email_alert_system"
            )
            
            self._data_flow_graph.add_websocket_message_flow(websocket_message_flow)
            
            logger.debug("Mapped WebSocket message flow: /ws/anomalies → Grafana alerts")
            
        except Exception as e:
            logger.error(f"Error mapping WebSocket message flows: {e}")
    
    async def _map_emoji_rain_flows(self) -> None:
        """Map emoji rain data flow: achievement → WebSocket → frontend."""
        try:
            emoji_rain_flow = EmojiRainFlow(
                flow_id=f"emoji_rain_flow_{uuid4()}",
                achievement_type="task_completion",
                trigger_event="task_success",
                flow_path=[
                    "Achievement Detection",
                    "WebSocket Broadcast",
                    "Frontend Rendering"
                ],
                websocket_endpoint="/ws/emoji-rain",
                emoji_type="celebration",
                emoji_sequence=["🎉", "✨", "🚀", "💫", "🌟"],
                animation_duration_ms=3000,
                broadcast_scope="global",
                target_users=[],
                broadcast_channels=[
                    "/ws/emoji-rain",
                    "frontend_notifications"
                ],
                error_correlation_id=str(uuid4()),
                fallback_celebration="static_emoji_display"
            )
            
            self._data_flow_graph.add_emoji_rain_flow(emoji_rain_flow)
            
            logger.debug("Mapped emoji rain data flow: achievement → WebSocket → frontend")
            
        except Exception as e:
            logger.error(f"Error mapping emoji rain flows: {e}")
    
    async def _create_metrics_flow_edges(self, metrics_flow: MetricsFlow) -> None:
        """Create edges for metrics flow."""
        try:
            # ReflectiveModule → Observatory
            edge1 = DataFlowEdge(
                edge_id=f"edge_reflective_observatory_{uuid4()}",
                source_node_id="ReflectiveModule Components",
                target_node_id="Observatory Server",
                flow_type=DataFlowType.METRICS,
                direction=FlowDirection.OUTBOUND,
                priority=FlowPriority.HIGH,
                data_format="json",
                transport_protocol="http",
                compression_enabled=True,
                correlation_id_tracking=True,
                description="Metrics collection from ReflectiveModule components to Observatory",
                tags=["metrics", "collection", "reflective_module"]
            )
            
            # Observatory → Prometheus
            edge2 = DataFlowEdge(
                edge_id=f"edge_observatory_prometheus_{uuid4()}",
                source_node_id="Observatory Server",
                target_node_id="Prometheus Server",
                flow_type=DataFlowType.METRICS,
                direction=FlowDirection.OUTBOUND,
                priority=FlowPriority.HIGH,
                data_format="prometheus",
                transport_protocol="http",
                compression_enabled=False,
                correlation_id_tracking=True,
                description="Metrics scraping from Observatory to Prometheus",
                tags=["metrics", "scraping", "prometheus"]
            )
            
            # Prometheus → Grafana
            edge3 = DataFlowEdge(
                edge_id=f"edge_prometheus_grafana_{uuid4()}",
                source_node_id="Prometheus Server",
                target_node_id="Grafana Dashboard",
                flow_type=DataFlowType.METRICS,
                direction=FlowDirection.OUTBOUND,
                priority=FlowPriority.HIGH,
                data_format="promql",
                transport_protocol="http",
                compression_enabled=False,
                correlation_id_tracking=True,
                description="Metrics querying from Prometheus to Grafana",
                tags=["metrics", "querying", "grafana"]
            )
            
            self._data_flow_graph.add_edge(edge1)
            self._data_flow_graph.add_edge(edge2)
            self._data_flow_graph.add_edge(edge3)
            
        except Exception as e:
            logger.error(f"Error creating metrics flow edges: {e}")
    
    def _get_websocket_endpoints_for_service(self, service_name: str) -> List[str]:
        """Get WebSocket endpoints for a service."""
        if service_name.lower() == "observatory":
            return self._config.websocket_endpoints
        return []
    
    def _get_capabilities_for_service(self, service_name: str) -> List[str]:
        """Get capabilities for a service."""
        capabilities_map = {
            "Observatory": ["metrics_collection", "websocket_server", "real_time_streaming"],
            "Prometheus": ["metrics_storage", "querying", "alerting"],
            "Grafana": ["visualization", "dashboard", "alerting"],
            "Redis": ["data_storage", "caching", "pub_sub"]
        }
        return capabilities_map.get(service_name, [])
    
    def _get_message_types_for_endpoint(self, endpoint: str) -> List[str]:
        """Get message types for a WebSocket endpoint."""
        message_types_map = {
            "/ws/observatory": ["metrics", "status", "health_check"],
            "/ws/anomalies": ["anomaly_alert", "anomaly_detection"],
            "/ws/emoji-rain": ["achievement", "celebration", "emoji_sequence"],
            "/ws/doctor-status": ["health_status", "diagnostic", "recovery"]
        }
        return message_types_map.get(endpoint, ["generic"])
    
    def _update_graph_metadata(self) -> None:
        """Update graph metadata and validation."""
        if not self._data_flow_graph:
            return
        
        # Update complexity score
        self._data_flow_graph.complexity_score = (
            self._data_flow_graph.total_nodes * 0.3 +
            self._data_flow_graph.total_edges * 0.4 +
            self._data_flow_graph.total_flows * 0.3
        )
        
        # Update accuracy score
        if self._data_flow_graph.nodes:
            total_accuracy = sum(node.accuracy_score for node in self._data_flow_graph.nodes.values())
            self._data_flow_graph.accuracy_score = total_accuracy / len(self._data_flow_graph.nodes)
        
        # Validate graph
        validation_results = self._data_flow_graph.validate_graph()
        self._data_flow_graph.validation_status = "valid" if validation_results["is_valid"] else "invalid"
    
    def get_data_flow_graph(self) -> Optional[DataFlowGraph]:
        """Get the current data flow graph."""
        return self._data_flow_graph
    
    def get_flow_summary(self) -> Dict[str, Any]:
        """Get a summary of all mapped flows."""
        if not self._data_flow_graph:
            return {"error": "No data flow graph available"}
        
        return self._data_flow_graph.get_flow_summary()
    
    def get_mapping_stats(self) -> Dict[str, Any]:
        """Get data flow mapping performance statistics."""
        uptime = time.time() - self._mapping_start_time
        
        return {
            "uptime_seconds": uptime,
            "mapping_active": self._mapping_active,
            "flows_mapped": self._flows_mapped,
            "mapping_errors": self._mapping_errors,
            "last_mapping_duration_ms": self._last_mapping_duration * 1000,
            "last_mapping_time": self._last_mapping_time.isoformat() if self._last_mapping_time else None,
            "mapping_rate_per_hour": (self._flows_mapped / uptime) * 3600 if uptime > 0 else 0,
            "error_rate_percent": (self._mapping_errors / max(1, self._flows_mapped)) * 100,
            "graph_stats": self.get_flow_summary() if self._data_flow_graph else None
        }
    
    def export_data_flow_report(self, format: str = "json") -> str:
        """Export comprehensive data flow report."""
        if not self._data_flow_graph:
            return json.dumps({"error": "No data flow graph available"})
        
        if format.lower() == "json":
            return json.dumps(self._data_flow_graph.to_dict(), indent=2)
        else:
            return str(self._data_flow_graph.to_dict())
    
    # ReflectiveModule implementation
    
    def get_capabilities(self) -> List['ModuleCapability']:
        """Get DataFlowMapper capabilities."""
        from src.rm_ddd.core.unified_reflective_module import ModuleCapability
        return [
            ModuleCapability.MONITORING,
            ModuleCapability.DATA_PROCESSING,
            ModuleCapability.API_INTEGRATION,
        ]
    
    def get_module_info(self) -> Dict[str, Any]:
        """Get module information."""
        return {
            "module_id": self.module_id,
            "name": "Comprehensive Data Flow Mapper",
            "version": "1.0.0",
            "description": "Maps comprehensive data flows across Beast Mode framework ecosystem",
            "config": {
                "real_time_mapping": self._config.enable_real_time_mapping,
                "error_tracking": self._config.enable_error_tracking,
                "performance_monitoring": self._config.enable_performance_monitoring,
                "mapping_interval": self._config.mapping_interval_seconds,
                "websocket_endpoints": self._config.websocket_endpoints
            }
        }
    
    def get_health_status(self) -> 'ModuleHealth':
        """Get health status of the DataFlowMapper."""
        from src.rm_ddd.core.unified_reflective_module import ModuleHealth, ModuleStatus
        
        # Determine status based on mapping state and error rate
        if not self._mapping_active:
            status = ModuleStatus.ERROR
            health_score = 0.0
            issues = ["DataFlowMapper is not active"]
        else:
            error_rate = (self._mapping_errors / max(1, self._flows_mapped)) * 100
            
            if error_rate > 10:
                status = ModuleStatus.ERROR
                health_score = 0.3
                issues = [f"High error rate: {error_rate:.1f}%"]
            elif error_rate > 5:
                status = ModuleStatus.WARNING
                health_score = 0.7
                issues = [f"Elevated error rate: {error_rate:.1f}%"]
            else:
                status = ModuleStatus.HEALTHY
                health_score = 1.0
                issues = []
        
        uptime = time.time() - self._mapping_start_time
        
        return ModuleHealth(
            module_id=self.module_id,
            status=status,
            health_score=health_score,
            issues=issues,
            last_check=datetime.now(),
            uptime_seconds=uptime,
            error_count=self._mapping_errors,
            warning_count=0
        )
    
    async def graceful_degradation(self, error: Exception) -> bool:
        """Handle graceful degradation on errors."""
        logger.warning(f"DataFlowMapper entering graceful degradation due to: {error}")
        
        # Continue running but with reduced functionality
        if "websocket" in str(error).lower():
            logger.info("WebSocket connection issue - continuing without real-time mapping")
            return True
        elif "infrastructure" in str(error).lower():
            logger.info("Infrastructure discovery issue - continuing with cached data")
            return True
        
        return False
    
    async def get_metrics(self) -> Dict[str, Any]:
        """Get current metrics for this mapper."""
        return {
            "mapping_stats": self.get_mapping_stats(),
            "data_flow_graph_available": self._data_flow_graph is not None,
            "infrastructure_discoverer_active": self._infrastructure_discoverer is not None,
            "websocket_client_connected": self._websocket_client is not None,
            "mapping_active": self._mapping_active
        }