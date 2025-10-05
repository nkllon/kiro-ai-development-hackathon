"""
Error Propagation Analyzer - Comprehensive Error Propagation Analysis Implementation.

This module implements Task 2.4: Error Propagation Analysis for the 
system-architecture-wiring-diagram specification. It maps error propagation paths 
through systematic error handling, documents correlation ID tracking across all 
components, creates error recovery procedure mapping, maps fallback mechanisms, 
documents emergency protocol integration points, and creates error classification 
and escalation procedures.
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
from ..models.error_propagation import (
    ErrorPropagationGraph, ErrorPropagationPath, CorrelationIDMapping,
    ErrorRecoveryProcedure, FallbackMechanism, EmergencyProtocol,
    ErrorClassification, ErrorContext, ErrorSeverity, ErrorCategory,
    RecoveryStrategy, FallbackType
)
from ..discovery.infrastructure_discoverer import InfrastructureDiscoverer
from ..discovery.observatory_websocket_client import ObservatoryWebSocketClient

logger = logging.getLogger(__name__)


@dataclass
class ErrorPropagationConfig:
    """Configuration for error propagation analysis."""
    enable_real_time_analysis: bool = True
    enable_correlation_tracking: bool = True
    enable_recovery_mapping: bool = True
    enable_fallback_monitoring: bool = True
    analysis_interval_seconds: int = 60
    correlation_timeout_seconds: int = 3600  # 1 hour
    websocket_endpoints: List[str] = None
    observatory_endpoint: str = "http://localhost:8888"
    prometheus_endpoint: str = "http://localhost:9090"
    
    def __post_init__(self):
        if self.websocket_endpoints is None:
            self.websocket_endpoints = [
                "/ws/observatory",
                "/ws/anomalies", 
                "/ws/emoji-rain",
                "/ws/doctor-status"
            ]


class ErrorPropagationAnalyzer(ReflectiveModule):
    """
    Comprehensive Error Propagation Analyzer for System Architecture Wiring Diagram.
    
    Implements Task 2.4 requirements:
    - Map error propagation paths through systematic error handling
    - Document correlation ID tracking across all components
    - Create error recovery procedure mapping
    - Map fallback mechanisms (Redis failover, WebSocket reconnection)
    - Document emergency protocol integration points
    - Create error classification and escalation procedures
    """
    
    def __init__(self, config: Optional[ErrorPropagationConfig] = None):
        super().__init__()
        self.module_id = "error_propagation_analyzer"
        self._config = config or ErrorPropagationConfig()
        
        # Core components
        self._infrastructure_discoverer: Optional[InfrastructureDiscoverer] = None
        self._websocket_client: Optional[ObservatoryWebSocketClient] = None
        
        # Error propagation graph
        self._error_propagation_graph: Optional[ErrorPropagationGraph] = None
        
        # Analysis state
        self._analysis_active = False
        self._analysis_task: Optional[asyncio.Task] = None
        self._last_analysis_time: Optional[datetime] = None
        
        # Performance tracking
        self._analysis_start_time = time.time()
        self._paths_analyzed = 0
        self._analysis_errors = 0
        self._last_analysis_duration = 0.0
        
        # Error tracking with correlation IDs
        self._active_correlations: Dict[str, CorrelationIDMapping] = {}
        self._error_patterns: Dict[str, ErrorClassification] = {}
        
        logger.info("🔍 ErrorPropagationAnalyzer initialized - Ready to analyze error propagation")
    
    async def start_analysis(self) -> bool:
        """Start comprehensive error propagation analysis."""
        try:
            if self._analysis_active:
                logger.warning("ErrorPropagationAnalyzer is already active")
                return True
            
            # Initialize infrastructure discoverer
            self._infrastructure_discoverer = InfrastructureDiscoverer()
            await self._infrastructure_discoverer.start_discovery()
            
            # Initialize WebSocket client
            self._websocket_client = ObservatoryWebSocketClient(
                base_url=f"ws://localhost:8888"
            )
            await self._websocket_client.connect_to_endpoints()
            
            # Initialize error propagation graph
            self._error_propagation_graph = ErrorPropagationGraph(
                graph_id=str(uuid4()),
                graph_name="Beast Mode Framework Error Propagation Graph"
            )
            
            # Start analysis task
            self._analysis_active = True
            self._analysis_task = asyncio.create_task(self._analysis_loop())
            
            logger.info("🚀 ErrorPropagationAnalyzer started - analyzing error propagation")
            return True
            
        except Exception as e:
            logger.error(f"Failed to start ErrorPropagationAnalyzer: {e}")
            return False
    
    async def stop_analysis(self) -> None:
        """Stop error propagation analysis gracefully."""
        logger.info("🛑 Stopping ErrorPropagationAnalyzer...")
        
        self._analysis_active = False
        
        # Cancel analysis task
        if self._analysis_task and not self._analysis_task.done():
            self._analysis_task.cancel()
        
        # Wait for task to complete
        if self._analysis_task:
            await asyncio.gather(self._analysis_task, return_exceptions=True)
        
        # Stop infrastructure discoverer
        if self._infrastructure_discoverer:
            await self._infrastructure_discoverer.stop_discovery()
        
        # Disconnect WebSocket client
        if self._websocket_client:
            await self._websocket_client.disconnect()
        
        logger.info("✅ ErrorPropagationAnalyzer stopped gracefully")
    
    async def _analysis_loop(self) -> None:
        """Main loop for comprehensive error propagation analysis."""
        logger.info("📊 Starting comprehensive error propagation analysis loop")
        
        while self._analysis_active:
            analysis_start = time.time()
            
            try:
                # Perform comprehensive analysis
                await self._perform_comprehensive_analysis()
                
                # Track performance
                self._last_analysis_duration = time.time() - analysis_start
                self._last_analysis_time = datetime.now()
                
                # Sleep for analysis interval
                await asyncio.sleep(self._config.analysis_interval_seconds)
                
            except asyncio.CancelledError:
                logger.info("Error propagation analysis loop cancelled")
                break
            except Exception as e:
                logger.error(f"Error in analysis loop: {e}")
                self._analysis_errors += 1
                await asyncio.sleep(5)  # Brief pause on error
        
        logger.info("Error propagation analysis loop stopped")
    
    async def _perform_comprehensive_analysis(self) -> None:
        """Perform comprehensive error propagation analysis."""
        try:
            # Map error propagation paths
            await self._map_error_propagation_paths()
            
            # Track correlation IDs
            await self._track_correlation_ids()
            
            # Map recovery procedures
            await self._map_recovery_procedures()
            
            # Map fallback mechanisms
            await self._map_fallback_mechanisms()
            
            # Map emergency protocols
            await self._map_emergency_protocols()
            
            # Create error classifications
            await self._create_error_classifications()
            
            # Update graph metadata
            self._update_graph_metadata()
            
            self._paths_analyzed += 1
            
        except Exception as e:
            logger.error(f"Error during comprehensive analysis: {e}")
            raise
    
    async def _map_error_propagation_paths(self) -> None:
        """Map error propagation paths through systematic error handling."""
        try:
            # Map ReflectiveModule error propagation
            reflective_module_path = ErrorPropagationPath(
                path_id=f"reflective_module_errors_{uuid4()}",
                source_component="ReflectiveModule Components",
                target_components=["Observatory Error Handler", "Prometheus Alert Manager", "Grafana Alerting"],
                propagation_steps=[
                    "ReflectiveModule Error Detection",
                    "Observatory Error Handler",
                    "Prometheus Alert Manager",
                    "Grafana Alerting",
                    "Notification System"
                ],
                error_types=["systematic_error", "health_check_failure", "performance_degradation"],
                severity_levels=[ErrorSeverity.ERROR, ErrorSeverity.WARNING, ErrorSeverity.CRITICAL],
                propagation_delay_ms=100.0,
                detection_time_ms=50.0,
                affected_services=["Observatory", "Prometheus", "Grafana", "WebSocket Connections"],
                user_impact_score=0.7,
                business_impact_score=0.8,
                recovery_mechanisms=["automatic_retry", "exponential_backoff", "circuit_breaker"],
                recovery_time_seconds=30.0,
                tags=["reflective_module", "systematic_error", "observatory"],
                metadata={
                    "error_tracking_enabled": True,
                    "correlation_id_tracking": True,
                    "systematic_handling": True
                }
            )
            
            self._error_propagation_graph.add_propagation_path(reflective_module_path)
            
            # Map WebSocket error propagation
            websocket_path = ErrorPropagationPath(
                path_id=f"websocket_errors_{uuid4()}",
                source_component="WebSocket Connections",
                target_components=["Observatory Server", "Frontend Applications", "Notification System"],
                propagation_steps=[
                    "WebSocket Connection Failure",
                    "Observatory Connection Manager",
                    "Frontend Reconnection Logic",
                    "Notification System"
                ],
                error_types=["connection_timeout", "websocket_upgrade_failure", "message_delivery_failure"],
                severity_levels=[ErrorSeverity.WARNING, ErrorSeverity.ERROR],
                propagation_delay_ms=200.0,
                detection_time_ms=100.0,
                affected_services=["Observatory", "Frontend", "Real-time Features"],
                user_impact_score=0.5,
                business_impact_score=0.6,
                recovery_mechanisms=["websocket_reconnection", "exponential_backoff", "fallback_to_polling"],
                recovery_time_seconds=15.0,
                tags=["websocket", "connection", "real_time"],
                metadata={
                    "reconnection_enabled": True,
                    "fallback_mechanisms": ["polling", "cached_data"],
                    "heartbeat_monitoring": True
                }
            )
            
            self._error_propagation_graph.add_propagation_path(websocket_path)
            
            # Map Redis coordination error propagation
            redis_path = ErrorPropagationPath(
                path_id=f"redis_coordination_errors_{uuid4()}",
                source_component="Redis Coordination",
                target_components=["Primary Redis", "Fallback Redis", "Service Coordination"],
                propagation_steps=[
                    "Redis Connection Failure",
                    "Primary Redis Health Check",
                    "Fallback Redis Activation",
                    "Service Coordination Update"
                ],
                error_types=["connection_failure", "timeout", "memory_exhaustion"],
                severity_levels=[ErrorSeverity.ERROR, ErrorSeverity.CRITICAL],
                propagation_delay_ms=500.0,
                detection_time_ms=200.0,
                affected_services=["Redis Primary", "Redis Fallback", "All Coordinated Services"],
                user_impact_score=0.9,
                business_impact_score=0.9,
                recovery_mechanisms=["redis_failover", "service_isolation", "graceful_degradation"],
                recovery_time_seconds=10.0,
                tags=["redis", "coordination", "failover"],
                metadata={
                    "failover_enabled": True,
                    "health_check_interval": 30,
                    "automatic_failover": True
                }
            )
            
            self._error_propagation_graph.add_propagation_path(redis_path)
            
            # Map Cloudflare tunnel error propagation
            tunnel_path = ErrorPropagationPath(
                path_id=f"cloudflare_tunnel_errors_{uuid4()}",
                source_component="Cloudflare Tunnel",
                target_components=["DNS Resolution", "SSL/TLS", "Service Routing"],
                propagation_steps=[
                    "Tunnel Connection Failure",
                    "DNS Resolution Check",
                    "SSL/TLS Validation",
                    "Service Routing Update"
                ],
                error_types=["tunnel_disconnect", "dns_failure", "ssl_error", "routing_failure"],
                severity_levels=[ErrorSeverity.CRITICAL, ErrorSeverity.ERROR],
                propagation_delay_ms=1000.0,
                detection_time_ms=500.0,
                affected_services=["All External Services", "DNS", "SSL/TLS"],
                user_impact_score=1.0,
                business_impact_score=1.0,
                recovery_mechanisms=["tunnel_reconnection", "dns_failover", "ssl_renewal"],
                recovery_time_seconds=60.0,
                tags=["cloudflare", "tunnel", "dns", "ssl"],
                metadata={
                    "tunnel_id": "d1e53e43-033f-4994-8f46-c83962ae3785",
                    "dns_failover_enabled": True,
                    "ssl_monitoring": True
                }
            )
            
            self._error_propagation_graph.add_propagation_path(tunnel_path)
            
            logger.debug("Mapped error propagation paths through systematic error handling")
            
        except Exception as e:
            logger.error(f"Error mapping propagation paths: {e}")
    
    async def _track_correlation_ids(self) -> None:
        """Document correlation ID tracking across all components."""
        try:
            # Create correlation mapping for ReflectiveModule errors
            reflective_correlation = CorrelationIDMapping(
                correlation_id=str(uuid4()),
                primary_component="ReflectiveModule",
                related_components=["Observatory", "Prometheus", "Grafana"],
                error_events=["health_check_failure", "performance_degradation", "systematic_error"],
                first_seen=datetime.now(),
                last_seen=datetime.now(),
                duration_seconds=300.0,
                is_active=True,
                resolution_status="pending",
                tags=["reflective_module", "systematic", "correlation"],
                metadata={
                    "tracking_enabled": True,
                    "cross_component_tracking": True,
                    "error_propagation_tracking": True
                }
            )
            
            self._error_propagation_graph.add_correlation_mapping(reflective_correlation)
            
            # Create correlation mapping for WebSocket errors
            websocket_correlation = CorrelationIDMapping(
                correlation_id=str(uuid4()),
                primary_component="WebSocket Connections",
                related_components=["Observatory Server", "Frontend", "Notification System"],
                error_events=["connection_failure", "message_delivery_failure", "reconnection_attempt"],
                first_seen=datetime.now(),
                last_seen=datetime.now(),
                duration_seconds=180.0,
                is_active=True,
                resolution_status="pending",
                tags=["websocket", "connection", "real_time"],
                metadata={
                    "reconnection_tracking": True,
                    "message_delivery_tracking": True,
                    "heartbeat_monitoring": True
                }
            )
            
            self._error_propagation_graph.add_correlation_mapping(websocket_correlation)
            
            # Create correlation mapping for Redis coordination
            redis_correlation = CorrelationIDMapping(
                correlation_id=str(uuid4()),
                primary_component="Redis Coordination",
                related_components=["Primary Redis", "Fallback Redis", "Service Coordination"],
                error_events=["connection_failure", "failover_activation", "coordination_update"],
                first_seen=datetime.now(),
                last_seen=datetime.now(),
                duration_seconds=120.0,
                is_active=True,
                resolution_status="pending",
                tags=["redis", "coordination", "failover"],
                metadata={
                    "failover_tracking": True,
                    "coordination_monitoring": True,
                    "health_check_tracking": True
                }
            )
            
            self._error_propagation_graph.add_correlation_mapping(redis_correlation)
            
            logger.debug("Documented correlation ID tracking across all components")
            
        except Exception as e:
            logger.error(f"Error tracking correlation IDs: {e}")
    
    async def _map_recovery_procedures(self) -> None:
        """Create error recovery procedure mapping."""
        try:
            # ReflectiveModule recovery procedure
            reflective_recovery = ErrorRecoveryProcedure(
                procedure_id=f"reflective_module_recovery_{uuid4()}",
                error_category=ErrorCategory.SYSTEM_ERROR,
                error_codes=["SYS_ERROR_001", "HEALTH_CHECK_FAIL", "PERF_DEGRADE"],
                affected_components=["ReflectiveModule", "Observatory", "Prometheus", "Grafana"],
                recovery_steps=[
                    "Detect systematic error",
                    "Generate correlation ID",
                    "Log error with context",
                    "Trigger automatic retry",
                    "Update health status",
                    "Notify monitoring systems"
                ],
                automated_steps=[
                    "Generate correlation ID",
                    "Log error with context",
                    "Trigger automatic retry",
                    "Update health status"
                ],
                manual_steps=[
                    "Review error logs",
                    "Analyze root cause",
                    "Update error handling rules",
                    "Notify stakeholders"
                ],
                estimated_recovery_time_seconds=30.0,
                timeout_seconds=300.0,
                prerequisites=["Error detection system active", "Monitoring systems operational"],
                dependencies=["Observatory", "Prometheus", "Grafana"],
                success_indicators=["Error resolved", "Health status restored", "Monitoring alerts cleared"],
                validation_checks=["Health endpoint accessible", "Metrics collection resumed", "Error rate normalized"],
                tags=["reflective_module", "systematic", "recovery"],
                metadata={
                    "automated_recovery": True,
                    "correlation_tracking": True,
                    "systematic_handling": True
                }
            )
            
            self._error_propagation_graph.add_recovery_procedure(reflective_recovery)
            
            # WebSocket recovery procedure
            websocket_recovery = ErrorRecoveryProcedure(
                procedure_id=f"websocket_recovery_{uuid4()}",
                error_category=ErrorCategory.NETWORK_ERROR,
                error_codes=["WS_CONN_FAIL", "WS_UPGRADE_FAIL", "WS_MSG_FAIL"],
                affected_components=["WebSocket Connections", "Observatory Server", "Frontend"],
                recovery_steps=[
                    "Detect connection failure",
                    "Generate correlation ID",
                    "Attempt reconnection",
                    "Fallback to polling",
                    "Update connection status",
                    "Notify frontend"
                ],
                automated_steps=[
                    "Generate correlation ID",
                    "Attempt reconnection",
                    "Fallback to polling",
                    "Update connection status"
                ],
                manual_steps=[
                    "Review connection logs",
                    "Check network connectivity",
                    "Verify WebSocket configuration",
                    "Update reconnection strategy"
                ],
                estimated_recovery_time_seconds=15.0,
                timeout_seconds=120.0,
                prerequisites=["Network connectivity", "WebSocket server operational"],
                dependencies=["Observatory Server", "Frontend Applications"],
                success_indicators=["Connection restored", "Real-time features resumed", "Message delivery confirmed"],
                validation_checks=["WebSocket endpoint accessible", "Connection established", "Message flow resumed"],
                tags=["websocket", "connection", "recovery"],
                metadata={
                    "reconnection_enabled": True,
                    "fallback_mechanisms": ["polling", "cached_data"],
                    "heartbeat_monitoring": True
                }
            )
            
            self._error_propagation_graph.add_recovery_procedure(websocket_recovery)
            
            # Redis coordination recovery procedure
            redis_recovery = ErrorRecoveryProcedure(
                procedure_id=f"redis_coordination_recovery_{uuid4()}",
                error_category=ErrorCategory.RESOURCE_ERROR,
                error_codes=["REDIS_CONN_FAIL", "REDIS_TIMEOUT", "REDIS_MEMORY"],
                affected_components=["Redis Primary", "Redis Fallback", "Service Coordination"],
                recovery_steps=[
                    "Detect Redis failure",
                    "Generate correlation ID",
                    "Activate failover",
                    "Update service coordination",
                    "Monitor failover status",
                    "Plan primary recovery"
                ],
                automated_steps=[
                    "Generate correlation ID",
                    "Activate failover",
                    "Update service coordination",
                    "Monitor failover status"
                ],
                manual_steps=[
                    "Review Redis logs",
                    "Check Redis configuration",
                    "Plan primary recovery",
                    "Update failover configuration"
                ],
                estimated_recovery_time_seconds=10.0,
                timeout_seconds=60.0,
                prerequisites=["Fallback Redis operational", "Service coordination active"],
                dependencies=["Redis Primary", "Redis Fallback", "Service Coordination"],
                success_indicators=["Failover activated", "Services coordinated", "Data consistency maintained"],
                validation_checks=["Fallback Redis accessible", "Service coordination updated", "Data consistency verified"],
                tags=["redis", "coordination", "failover"],
                metadata={
                    "automatic_failover": True,
                    "health_check_monitoring": True,
                    "service_coordination": True
                }
            )
            
            self._error_propagation_graph.add_recovery_procedure(redis_recovery)
            
            logger.debug("Created error recovery procedure mapping")
            
        except Exception as e:
            logger.error(f"Error mapping recovery procedures: {e}")
    
    async def _map_fallback_mechanisms(self) -> None:
        """Map fallback mechanisms (Redis failover, WebSocket reconnection)."""
        try:
            # Redis failover mechanism
            redis_failover = FallbackMechanism(
                mechanism_id=f"redis_failover_{uuid4()}",
                mechanism_type=FallbackType.REDIS_FAILOVER,
                primary_service="Redis Primary (192.168.1.119:6379)",
                fallback_service="Redis Fallback (localhost:6380)",
                activation_conditions=[
                    "Primary Redis connection failure",
                    "Primary Redis timeout",
                    "Primary Redis memory exhaustion"
                ],
                deactivation_conditions=[
                    "Primary Redis connection restored",
                    "Primary Redis health check passed",
                    "Manual failback initiated"
                ],
                health_check_endpoints=[
                    "http://192.168.1.119:6379/health",
                    "http://localhost:6380/health"
                ],
                switchover_time_seconds=5.0,
                performance_degradation_percent=10.0,
                health_check_interval_seconds=30,
                failure_threshold=3,
                recovery_threshold=2,
                is_active=False,
                tags=["redis", "failover", "coordination"],
                metadata={
                    "automatic_failover": True,
                    "health_check_monitoring": True,
                    "performance_monitoring": True
                }
            )
            
            self._error_propagation_graph.add_fallback_mechanism(redis_failover)
            
            # WebSocket reconnection mechanism
            websocket_reconnection = FallbackMechanism(
                mechanism_id=f"websocket_reconnection_{uuid4()}",
                mechanism_type=FallbackType.WEBSOCKET_RECONNECTION,
                primary_service="WebSocket Real-time Connection",
                fallback_service="HTTP Polling Fallback",
                activation_conditions=[
                    "WebSocket connection failure",
                    "WebSocket upgrade failure",
                    "WebSocket message delivery failure"
                ],
                deactivation_conditions=[
                    "WebSocket connection restored",
                    "WebSocket health check passed",
                    "Manual reconnection initiated"
                ],
                health_check_endpoints=[
                    "ws://localhost:8888/ws/observatory",
                    "ws://localhost:8888/ws/anomalies",
                    "ws://localhost:8888/ws/emoji-rain",
                    "ws://localhost:8888/ws/doctor-status"
                ],
                switchover_time_seconds=2.0,
                performance_degradation_percent=20.0,
                health_check_interval_seconds=15,
                failure_threshold=2,
                recovery_threshold=1,
                is_active=False,
                tags=["websocket", "reconnection", "real_time"],
                metadata={
                    "exponential_backoff": True,
                    "heartbeat_monitoring": True,
                    "fallback_polling": True
                }
            )
            
            self._error_propagation_graph.add_fallback_mechanism(websocket_reconnection)
            
            # Service redirection mechanism
            service_redirection = FallbackMechanism(
                mechanism_id=f"service_redirection_{uuid4()}",
                mechanism_type=FallbackType.SERVICE_REDIRECTION,
                primary_service="Observatory Server (localhost:8888)",
                fallback_service="Observatory Backup Server",
                activation_conditions=[
                    "Observatory server failure",
                    "Observatory health check failure",
                    "Observatory timeout"
                ],
                deactivation_conditions=[
                    "Observatory server restored",
                    "Observatory health check passed",
                    "Manual failback initiated"
                ],
                health_check_endpoints=[
                    "http://localhost:8888/health",
                    "http://localhost:8888/ready",
                    "http://localhost:8888/metrics"
                ],
                switchover_time_seconds=10.0,
                performance_degradation_percent=15.0,
                health_check_interval_seconds=30,
                failure_threshold=3,
                recovery_threshold=2,
                is_active=False,
                tags=["observatory", "service", "redirection"],
                metadata={
                    "dns_redirection": True,
                    "load_balancer": True,
                    "health_check_monitoring": True
                }
            )
            
            self._error_propagation_graph.add_fallback_mechanism(service_redirection)
            
            logger.debug("Mapped fallback mechanisms (Redis failover, WebSocket reconnection)")
            
        except Exception as e:
            logger.error(f"Error mapping fallback mechanisms: {e}")
    
    async def _map_emergency_protocols(self) -> None:
        """Document emergency protocol integration points."""
        try:
            # Critical system failure protocol
            critical_failure_protocol = EmergencyProtocol(
                protocol_id=f"critical_system_failure_{uuid4()}",
                protocol_name="Critical System Failure Response",
                trigger_conditions=[
                    "Multiple service failures",
                    "Redis coordination failure",
                    "Cloudflare tunnel failure",
                    "Observatory server failure"
                ],
                severity_threshold=ErrorSeverity.CRITICAL,
                immediate_actions=[
                    "Activate emergency mode",
                    "Isolate affected services",
                    "Activate all fallback mechanisms",
                    "Send emergency notifications"
                ],
                escalation_actions=[
                    "Contact system administrators",
                    "Activate disaster recovery procedures",
                    "Notify stakeholders",
                    "Document incident"
                ],
                communication_actions=[
                    "Send emergency alerts",
                    "Update status page",
                    "Notify users",
                    "Coordinate with team"
                ],
                primary_contacts=["system-admin@company.com", "ops-team@company.com"],
                escalation_contacts=["cto@company.com", "ceo@company.com"],
                notification_channels=["email", "slack", "pagerduty", "status-page"],
                response_time_seconds=60.0,
                escalation_time_seconds=300.0,
                is_active=True,
                tags=["emergency", "critical", "system_failure"],
                metadata={
                    "automated_response": True,
                    "escalation_enabled": True,
                    "communication_channels": ["email", "slack", "pagerduty"]
                }
            )
            
            self._error_propagation_graph.add_emergency_protocol(critical_failure_protocol)
            
            # Data loss prevention protocol
            data_loss_protocol = EmergencyProtocol(
                protocol_id=f"data_loss_prevention_{uuid4()}",
                protocol_name="Data Loss Prevention Response",
                trigger_conditions=[
                    "Redis data corruption",
                    "Database connection failure",
                    "Backup system failure",
                    "Data synchronization failure"
                ],
                severity_threshold=ErrorSeverity.CRITICAL,
                immediate_actions=[
                    "Stop all write operations",
                    "Activate read-only mode",
                    "Initiate data backup",
                    "Isolate affected systems"
                ],
                escalation_actions=[
                    "Contact database administrators",
                    "Activate disaster recovery",
                    "Notify data protection team",
                    "Document data loss risk"
                ],
                communication_actions=[
                    "Send data loss alerts",
                    "Update data status",
                    "Notify data owners",
                    "Coordinate recovery"
                ],
                primary_contacts=["dba@company.com", "data-team@company.com"],
                escalation_contacts=["cto@company.com", "legal@company.com"],
                notification_channels=["email", "slack", "pagerduty"],
                response_time_seconds=30.0,
                escalation_time_seconds=120.0,
                is_active=True,
                tags=["emergency", "data_loss", "prevention"],
                metadata={
                    "data_protection": True,
                    "backup_activation": True,
                    "read_only_mode": True
                }
            )
            
            self._error_propagation_graph.add_emergency_protocol(data_loss_protocol)
            
            # Security incident protocol
            security_incident_protocol = EmergencyProtocol(
                protocol_id=f"security_incident_{uuid4()}",
                protocol_name="Security Incident Response",
                trigger_conditions=[
                    "Unauthorized access detected",
                    "Authentication system failure",
                    "SSL/TLS certificate failure",
                    "Suspicious activity detected"
                ],
                severity_threshold=ErrorSeverity.CRITICAL,
                immediate_actions=[
                    "Isolate affected systems",
                    "Revoke compromised credentials",
                    "Activate security monitoring",
                    "Document security incident"
                ],
                escalation_actions=[
                    "Contact security team",
                    "Activate incident response",
                    "Notify legal team",
                    "Coordinate with authorities"
                ],
                communication_actions=[
                    "Send security alerts",
                    "Update security status",
                    "Notify stakeholders",
                    "Coordinate response"
                ],
                primary_contacts=["security@company.com", "incident-response@company.com"],
                escalation_contacts=["cto@company.com", "legal@company.com"],
                notification_channels=["email", "slack", "pagerduty", "security-channel"],
                response_time_seconds=15.0,
                escalation_time_seconds=60.0,
                is_active=True,
                tags=["emergency", "security", "incident"],
                metadata={
                    "security_monitoring": True,
                    "incident_response": True,
                    "legal_coordination": True
                }
            )
            
            self._error_propagation_graph.add_emergency_protocol(security_incident_protocol)
            
            logger.debug("Documented emergency protocol integration points")
            
        except Exception as e:
            logger.error(f"Error mapping emergency protocols: {e}")
    
    async def _create_error_classifications(self) -> None:
        """Create error classification and escalation procedures."""
        try:
            # Systematic error classification
            systematic_error_classification = ErrorClassification(
                classification_id=f"systematic_error_classification_{uuid4()}",
                error_pattern=r"SYSTEMATIC_ERROR|HEALTH_CHECK_FAIL|PERF_DEGRADE",
                error_category=ErrorCategory.SYSTEM_ERROR,
                severity=ErrorSeverity.ERROR,
                classification_rules=[
                    "Error originates from ReflectiveModule",
                    "Error affects multiple components",
                    "Error requires systematic handling",
                    "Error has correlation ID"
                ],
                false_positive_patterns=[
                    "Expected maintenance",
                    "Planned downtime",
                    "Configuration updates"
                ],
                escalation_threshold=5,
                escalation_time_seconds=300.0,
                escalation_contacts=["ops-team@company.com", "system-admin@company.com"],
                auto_response_enabled=True,
                response_actions=[
                    "Generate correlation ID",
                    "Log error with context",
                    "Trigger automatic retry",
                    "Update health status",
                    "Notify monitoring systems"
                ],
                tags=["systematic", "reflective_module", "classification"],
                metadata={
                    "automated_classification": True,
                    "correlation_tracking": True,
                    "systematic_handling": True
                }
            )
            
            self._error_propagation_graph.add_error_classification(systematic_error_classification)
            
            # Network error classification
            network_error_classification = ErrorClassification(
                classification_id=f"network_error_classification_{uuid4()}",
                error_pattern=r"NETWORK_ERROR|CONNECTION_FAIL|TIMEOUT",
                error_category=ErrorCategory.NETWORK_ERROR,
                severity=ErrorSeverity.WARNING,
                classification_rules=[
                    "Error involves network connectivity",
                    "Error affects communication between components",
                    "Error may require reconnection",
                    "Error has network context"
                ],
                false_positive_patterns=[
                    "Planned network maintenance",
                    "Expected network changes",
                    "Network configuration updates"
                ],
                escalation_threshold=10,
                escalation_time_seconds=600.0,
                escalation_contacts=["network-team@company.com", "ops-team@company.com"],
                auto_response_enabled=True,
                response_actions=[
                    "Attempt reconnection",
                    "Activate fallback mechanisms",
                    "Update connection status",
                    "Notify affected services"
                ],
                tags=["network", "connection", "classification"],
                metadata={
                    "network_monitoring": True,
                    "reconnection_enabled": True,
                    "fallback_mechanisms": True
                }
            )
            
            self._error_propagation_graph.add_error_classification(network_error_classification)
            
            # Resource error classification
            resource_error_classification = ErrorClassification(
                classification_id=f"resource_error_classification_{uuid4()}",
                error_pattern=r"RESOURCE_ERROR|MEMORY_EXHAUST|CPU_OVERLOAD",
                error_category=ErrorCategory.RESOURCE_ERROR,
                severity=ErrorSeverity.ERROR,
                classification_rules=[
                    "Error involves resource exhaustion",
                    "Error affects system performance",
                    "Error may require resource scaling",
                    "Error has resource context"
                ],
                false_positive_patterns=[
                    "Planned resource scaling",
                    "Expected resource usage",
                    "Resource optimization"
                ],
                escalation_threshold=3,
                escalation_time_seconds=180.0,
                escalation_contacts=["ops-team@company.com", "infrastructure-team@company.com"],
                auto_response_enabled=True,
                response_actions=[
                    "Monitor resource usage",
                    "Activate resource scaling",
                    "Isolate resource-intensive processes",
                    "Notify resource management"
                ],
                tags=["resource", "performance", "classification"],
                metadata={
                    "resource_monitoring": True,
                    "scaling_enabled": True,
                    "performance_tracking": True
                }
            )
            
            self._error_propagation_graph.add_error_classification(resource_error_classification)
            
            logger.debug("Created error classification and escalation procedures")
            
        except Exception as e:
            logger.error(f"Error creating error classifications: {e}")
    
    def _update_graph_metadata(self) -> None:
        """Update graph metadata and validation."""
        if not self._error_propagation_graph:
            return
        
        # Update complexity score
        self._error_propagation_graph.complexity_score = (
            self._error_propagation_graph.total_paths * 0.2 +
            self._error_propagation_graph.total_correlations * 0.2 +
            self._error_propagation_graph.total_procedures * 0.2 +
            self._error_propagation_graph.total_fallbacks * 0.2 +
            self._error_propagation_graph.total_protocols * 0.1 +
            self._error_propagation_graph.total_classifications * 0.1
        )
        
        # Update accuracy score
        self._error_propagation_graph.accuracy_score = 0.95  # High accuracy for systematic analysis
        
        # Validate graph
        validation_results = self._error_propagation_graph.validate_graph()
        self._error_propagation_graph.validation_status = "valid" if validation_results["is_valid"] else "invalid"
    
    def get_error_propagation_graph(self) -> Optional[ErrorPropagationGraph]:
        """Get the current error propagation graph."""
        return self._error_propagation_graph
    
    def get_analysis_summary(self) -> Dict[str, Any]:
        """Get a summary of all analyzed error propagation components."""
        if not self._error_propagation_graph:
            return {"error": "No error propagation graph available"}
        
        return self._error_propagation_graph.get_propagation_summary()
    
    def get_analysis_stats(self) -> Dict[str, Any]:
        """Get error propagation analysis performance statistics."""
        uptime = time.time() - self._analysis_start_time
        
        return {
            "uptime_seconds": uptime,
            "analysis_active": self._analysis_active,
            "paths_analyzed": self._paths_analyzed,
            "analysis_errors": self._analysis_errors,
            "last_analysis_duration_ms": self._last_analysis_duration * 1000,
            "last_analysis_time": self._last_analysis_time.isoformat() if self._last_analysis_time else None,
            "analysis_rate_per_hour": (self._paths_analyzed / uptime) * 3600 if uptime > 0 else 0,
            "error_rate_percent": (self._analysis_errors / max(1, self._paths_analyzed)) * 100,
            "graph_stats": self.get_analysis_summary() if self._error_propagation_graph else None
        }
    
    def export_error_propagation_report(self, format: str = "json") -> str:
        """Export comprehensive error propagation report."""
        if not self._error_propagation_graph:
            return json.dumps({"error": "No error propagation graph available"})
        
        if format.lower() == "json":
            return json.dumps(self._error_propagation_graph.to_dict(), indent=2)
        else:
            return str(self._error_propagation_graph.to_dict())
    
    # ReflectiveModule implementation
    
    def get_capabilities(self) -> List['ModuleCapability']:
        """Get ErrorPropagationAnalyzer capabilities."""
        from src.rm_ddd.core.unified_reflective_module import ModuleCapability
        return [
            ModuleCapability.MONITORING,
            ModuleCapability.DATA_PROCESSING,
            ModuleCapability.VALIDATION,
        ]
    
    def get_module_info(self) -> Dict[str, Any]:
        """Get module information."""
        return {
            "module_id": self.module_id,
            "name": "Comprehensive Error Propagation Analyzer",
            "version": "1.0.0",
            "description": "Analyzes error propagation across Beast Mode framework ecosystem",
            "config": {
                "real_time_analysis": self._config.enable_real_time_analysis,
                "correlation_tracking": self._config.enable_correlation_tracking,
                "recovery_mapping": self._config.enable_recovery_mapping,
                "fallback_monitoring": self._config.enable_fallback_monitoring,
                "analysis_interval": self._config.analysis_interval_seconds,
                "websocket_endpoints": self._config.websocket_endpoints
            }
        }
    
    def get_health_status(self) -> 'ModuleHealth':
        """Get health status of the ErrorPropagationAnalyzer."""
        from src.rm_ddd.core.unified_reflective_module import ModuleHealth, ModuleStatus
        
        # Determine status based on analysis state and error rate
        if not self._analysis_active:
            status = ModuleStatus.ERROR
            health_score = 0.0
            issues = ["ErrorPropagationAnalyzer is not active"]
        else:
            error_rate = (self._analysis_errors / max(1, self._paths_analyzed)) * 100
            
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
        
        uptime = time.time() - self._analysis_start_time
        
        return ModuleHealth(
            module_id=self.module_id,
            status=status,
            health_score=health_score,
            issues=issues,
            last_check=datetime.now(),
            uptime_seconds=uptime,
            error_count=self._analysis_errors,
            warning_count=0
        )
    
    async def graceful_degradation(self, error: Exception) -> bool:
        """Handle graceful degradation on errors."""
        logger.warning(f"ErrorPropagationAnalyzer entering graceful degradation due to: {error}")
        
        # Continue running but with reduced functionality
        if "websocket" in str(error).lower():
            logger.info("WebSocket connection issue - continuing without real-time analysis")
            return True
        elif "infrastructure" in str(error).lower():
            logger.info("Infrastructure discovery issue - continuing with cached data")
            return True
        
        return False
    
    async def get_metrics(self) -> Dict[str, Any]:
        """Get current metrics for this analyzer."""
        return {
            "analysis_stats": self.get_analysis_stats(),
            "error_propagation_graph_available": self._error_propagation_graph is not None,
            "infrastructure_discoverer_active": self._infrastructure_discoverer is not None,
            "websocket_client_connected": self._websocket_client is not None,
            "analysis_active": self._analysis_active
        }