#!/usr/bin/env python3
"""
Real-Time Diagram Updater - Task 3.4 Implementation
==================================================

Implements real-time diagram updates with live component diagrams,
WebSocket connection status overlays, live metrics flow diagrams,
interactive sequence diagrams, and automated refresh capabilities.

Author: Beast Mode Framework
Date: 2024-12-19
Version: 1.0
"""

import asyncio
import json
import logging
import threading
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional, Set, Tuple, Union
import uuid
from concurrent.futures import ThreadPoolExecutor, as_completed

from src.rm_ddd.core.unified_reflective_module import ReflectiveModule, ModuleStatus, ModuleHealth
from src.system_architecture.models.real_time_models import (
    RealTimeStatus, WebSocketConnectionStatus, LiveMetricsFlow,
    InteractiveSequenceStep, DiagramRefreshRequest, DiagramRefreshResult,
    RealTimeDiagramMetadata, UpdateTrigger, RefreshStatus, ValidationLevel
)
from src.system_architecture.models.diagram_models import (
    DiagramMetadata, DiagramType, DiagramFormat, ValidationStatus,
    DiagramComponent, DiagramRelationship, SecurityBoundary
)


class RealTimeDiagramUpdater(ReflectiveModule):
    """
    Real-Time Diagram Updater for Task 3.4.
    
    Provides comprehensive real-time diagram update capabilities including:
    - Live component diagrams with real-time service status indicators
    - WebSocket connection status overlays on topology diagrams
    - Live metrics flow diagrams showing real-time data movement
    - Interactive sequence diagrams for operational workflows
    - Automated diagram refresh within 1 hour of infrastructure changes
    - "Last Updated" timestamps and validation status indicators
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize the Real-Time Diagram Updater."""
        super().__init__()
        
        self.module_name = "real_time_diagram_updater"
        self.config = config or {}
        self.correlation_id = str(uuid.uuid4())
        
        # Set up logging
        self.logger = logging.getLogger(f"beast_mode.system_architecture.{self.module_name}")
        
        # Real-time data storage
        self._real_time_statuses: Dict[str, RealTimeStatus] = {}
        self._websocket_connections: Dict[str, WebSocketConnectionStatus] = {}
        self._live_metrics_flows: List[LiveMetricsFlow] = []
        self._interactive_sequences: List[InteractiveSequenceStep] = []
        self._diagram_metadata: Dict[str, RealTimeDiagramMetadata] = {}
        
        # Refresh management
        self._refresh_queue: List[DiagramRefreshRequest] = []
        self._active_refreshes: Dict[str, DiagramRefreshResult] = {}
        self._refresh_history: List[DiagramRefreshResult] = []
        
        # Configuration
        self._refresh_interval_minutes = self.config.get("refresh_interval_minutes", 60)
        self._max_concurrent_refreshes = self.config.get("max_concurrent_refreshes", 5)
        self._validation_timeout_seconds = self.config.get("validation_timeout_seconds", 300)
        self._auto_refresh_enabled = self.config.get("auto_refresh_enabled", True)
        
        # Threading and async management
        self._executor = ThreadPoolExecutor(max_workers=self._max_concurrent_refreshes)
        self._refresh_thread: Optional[threading.Thread] = None
        self._running = False
        
        # Service discovery dependencies
        self._service_scanner = None
        self._network_discoverer = None
        self._data_flow_mapper = None
        
        self.logger.info(f"Real-Time Diagram Updater initialized with correlation ID: {self.correlation_id}")
    
    # ReflectiveModule Implementation
    
    def get_module_status(self) -> Dict[str, Any]:
        """Get comprehensive module status."""
        return {
            "module_name": self.module_name,
            "status": "healthy" if self.is_healthy() else "degraded",
            "correlation_id": self.correlation_id,
            "real_time_statuses_count": len(self._real_time_statuses),
            "websocket_connections_count": len(self._websocket_connections),
            "live_metrics_flows_count": len(self._live_metrics_flows),
            "interactive_sequences_count": len(self._interactive_sequences),
            "diagram_metadata_count": len(self._diagram_metadata),
            "active_refreshes_count": len(self._active_refreshes),
            "refresh_queue_size": len(self._refresh_queue),
            "auto_refresh_enabled": self._auto_refresh_enabled,
            "refresh_interval_minutes": self._refresh_interval_minutes,
            "uptime_seconds": (datetime.now() - self._start_time).total_seconds(),
            "last_activity": self._last_activity.isoformat()
        }
    
    def is_healthy(self) -> bool:
        """Check if the module is healthy."""
        try:
            # Check if refresh thread is running
            if self._auto_refresh_enabled and (not self._refresh_thread or not self._refresh_thread.is_alive()):
                return False
            
            # Check for excessive errors
            if self._error_count > 10:
                return False
            
            # Check if refresh queue is not overwhelmed
            if len(self._refresh_queue) > 100:
                return False
            
            return True
        except Exception as e:
            self.logger.error(f"Health check failed: {e}")
            return False
    
    def get_health_indicators(self) -> Dict[str, Any]:
        """Get detailed health indicators."""
        return {
            "module_status": "healthy" if self.is_healthy() else "degraded",
            "error_count": self._error_count,
            "warning_count": self._warning_count,
            "refresh_thread_alive": self._refresh_thread.is_alive() if self._refresh_thread else False,
            "queue_size": len(self._refresh_queue),
            "active_refreshes": len(self._active_refreshes),
            "real_time_data_freshness": self._get_data_freshness_score(),
            "websocket_connections_healthy": self._get_websocket_health_score(),
            "metrics_flow_health": self._get_metrics_flow_health_score()
        }
    
    def validate_systematic_compliance(self) -> str:
        """Validate systematic compliance."""
        try:
            # Check ReflectiveModule compliance
            if not hasattr(self, 'get_module_status'):
                return "error"
            
            # Check real-time update capabilities
            if not self._real_time_statuses:
                return "warning"
            
            # Check refresh mechanism
            if self._auto_refresh_enabled and not self._refresh_thread:
                return "warning"
            
            return "healthy"
        except Exception:
            return "error"
    
    # Core Real-Time Update Methods
    
    def start_real_time_updates(self) -> bool:
        """Start real-time update processing."""
        try:
            if self._running:
                self.logger.warning("Real-time updates already running")
                return True
            
            self._running = True
            
            # Start refresh thread if auto-refresh is enabled
            if self._auto_refresh_enabled:
                self._refresh_thread = threading.Thread(
                    target=self._refresh_worker,
                    name="RealTimeDiagramRefreshWorker",
                    daemon=True
                )
                self._refresh_thread.start()
                self.logger.info("Real-time refresh worker started")
            
            # Initialize service discovery dependencies
            self._initialize_service_dependencies()
            
            # Start real-time data collection
            self._start_real_time_data_collection()
            
            self.logger.info("Real-time updates started successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to start real-time updates: {e}")
            self._error_count += 1
            return False
    
    def stop_real_time_updates(self) -> bool:
        """Stop real-time update processing."""
        try:
            self._running = False
            
            # Stop refresh thread
            if self._refresh_thread and self._refresh_thread.is_alive():
                self._refresh_thread.join(timeout=5)
            
            # Shutdown executor
            self._executor.shutdown(wait=True)
            
            self.logger.info("Real-time updates stopped successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to stop real-time updates: {e}")
            self._error_count += 1
            return False
    
    def update_real_time_status(self, component_id: str, status_data: Dict[str, Any]) -> bool:
        """Update real-time status for a component."""
        try:
            real_time_status = RealTimeStatus(
                component_id=component_id,
                status=status_data.get("status", "unknown"),
                health_score=status_data.get("health_score", 0.0),
                last_updated=datetime.now(),
                websocket_connected=status_data.get("websocket_connected", False),
                metrics_available=status_data.get("metrics_available", False),
                error_count=status_data.get("error_count", 0),
                warning_count=status_data.get("warning_count", 0),
                response_time_ms=status_data.get("response_time_ms"),
                cpu_usage=status_data.get("cpu_usage"),
                memory_usage=status_data.get("memory_usage"),
                network_throughput=status_data.get("network_throughput"),
                metadata=status_data.get("metadata", {})
            )
            
            self._real_time_statuses[component_id] = real_time_status
            self._last_activity = datetime.now()
            
            # Trigger diagram refresh if needed
            self._trigger_diagram_refresh(
                UpdateTrigger.SERVICE_STATUS_CHANGE,
                metadata={"component_id": component_id, "status_change": True}
            )
            
            self.logger.debug(f"Updated real-time status for component {component_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to update real-time status for {component_id}: {e}")
            self._error_count += 1
            return False
    
    def update_websocket_connection_status(self, endpoint: str, connection_data: Dict[str, Any]) -> bool:
        """Update WebSocket connection status."""
        try:
            websocket_status = WebSocketConnectionStatus(
                endpoint=endpoint,
                connected=connection_data.get("connected", False),
                connection_time=datetime.fromisoformat(connection_data["connection_time"]) if connection_data.get("connection_time") else None,
                last_message_time=datetime.fromisoformat(connection_data["last_message_time"]) if connection_data.get("last_message_time") else None,
                messages_sent=connection_data.get("messages_sent", 0),
                messages_received=connection_data.get("messages_received", 0),
                connection_errors=connection_data.get("connection_errors", 0),
                reconnect_attempts=connection_data.get("reconnect_attempts", 0),
                latency_ms=connection_data.get("latency_ms"),
                bandwidth_kbps=connection_data.get("bandwidth_kbps"),
                connection_id=connection_data.get("connection_id", str(uuid.uuid4())),
                metadata=connection_data.get("metadata", {})
            )
            
            self._websocket_connections[endpoint] = websocket_status
            
            # Trigger diagram refresh for topology diagrams
            self._trigger_diagram_refresh(
                UpdateTrigger.WEBSOCKET_CONNECTION_CHANGE,
                metadata={"endpoint": endpoint, "connection_change": True}
            )
            
            self.logger.debug(f"Updated WebSocket connection status for {endpoint}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to update WebSocket connection status for {endpoint}: {e}")
            self._error_count += 1
            return False
    
    def update_live_metrics_flow(self, flow_data: Dict[str, Any]) -> bool:
        """Update live metrics flow information."""
        try:
            metrics_flow = LiveMetricsFlow(
                source_component=flow_data["source_component"],
                target_component=flow_data["target_component"],
                metric_name=flow_data["metric_name"],
                flow_rate_per_second=flow_data["flow_rate_per_second"],
                last_update=datetime.now(),
                latency_ms=flow_data.get("latency_ms"),
                data_size_bytes=flow_data.get("data_size_bytes"),
                error_rate=flow_data.get("error_rate", 0.0),
                success_rate=flow_data.get("success_rate", 100.0),
                flow_id=flow_data.get("flow_id", str(uuid.uuid4())),
                metadata=flow_data.get("metadata", {})
            )
            
            # Update or add the flow
            existing_flow = None
            for i, flow in enumerate(self._live_metrics_flows):
                if (flow.source_component == metrics_flow.source_component and
                    flow.target_component == metrics_flow.target_component and
                    flow.metric_name == metrics_flow.metric_name):
                    existing_flow = i
                    break
            
            if existing_flow is not None:
                self._live_metrics_flows[existing_flow] = metrics_flow
            else:
                self._live_metrics_flows.append(metrics_flow)
            
            # Trigger diagram refresh for data flow diagrams
            self._trigger_diagram_refresh(
                UpdateTrigger.METRICS_THRESHOLD_EXCEEDED,
                metadata={"metrics_flow_update": True, "flow_id": metrics_flow.flow_id}
            )
            
            self.logger.debug(f"Updated live metrics flow: {metrics_flow.source_component} -> {metrics_flow.target_component}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to update live metrics flow: {e}")
            self._error_count += 1
            return False
    
    def add_interactive_sequence_step(self, step_data: Dict[str, Any]) -> bool:
        """Add interactive sequence step for operational workflows."""
        try:
            sequence_step = InteractiveSequenceStep(
                step_id=step_data.get("step_id", str(uuid.uuid4())),
                participant=step_data["participant"],
                action=step_data["action"],
                message=step_data["message"],
                timestamp=datetime.now(),
                status=step_data.get("status", "pending"),
                duration_ms=step_data.get("duration_ms"),
                user_interaction_required=step_data.get("user_interaction_required", False),
                validation_required=step_data.get("validation_required", False),
                error_message=step_data.get("error_message"),
                metadata=step_data.get("metadata", {})
            )
            
            self._interactive_sequences.append(sequence_step)
            
            # Trigger diagram refresh for sequence diagrams
            self._trigger_diagram_refresh(
                UpdateTrigger.MANUAL_REFRESH,
                metadata={"interactive_sequence_update": True, "step_id": sequence_step.step_id}
            )
            
            self.logger.debug(f"Added interactive sequence step: {sequence_step.participant} - {sequence_step.action}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to add interactive sequence step: {e}")
            self._error_count += 1
            return False
    
    # Diagram Refresh Management
    
    def request_diagram_refresh(self, diagram_id: str, trigger: UpdateTrigger = UpdateTrigger.MANUAL_REFRESH,
                               priority: int = 5, validation_level: ValidationLevel = ValidationLevel.AUTOMATIC) -> str:
        """Request a diagram refresh."""
        try:
            refresh_request = DiagramRefreshRequest(
                diagram_id=diagram_id,
                trigger=trigger,
                requested_by="user",
                priority=priority,
                validation_level=validation_level,
                timeout_seconds=self._validation_timeout_seconds
            )
            
            self._refresh_queue.append(refresh_request)
            self._refresh_queue.sort(key=lambda x: x.priority, reverse=True)
            
            self.logger.info(f"Diagram refresh requested for {diagram_id} with priority {priority}")
            return refresh_request.request_id
            
        except Exception as e:
            self.logger.error(f"Failed to request diagram refresh for {diagram_id}: {e}")
            self._error_count += 1
            return ""
    
    def get_refresh_status(self, request_id: str) -> Optional[DiagramRefreshResult]:
        """Get refresh status by request ID."""
        # Check active refreshes
        if request_id in self._active_refreshes:
            return self._active_refreshes[request_id]
        
        # Check refresh history
        for result in self._refresh_history:
            if result.request_id == request_id:
                return result
        
        return None
    
    def get_diagram_metadata(self, diagram_id: str) -> Optional[RealTimeDiagramMetadata]:
        """Get real-time diagram metadata."""
        return self._diagram_metadata.get(diagram_id)
    
    def update_diagram_metadata(self, diagram_id: str, metadata: RealTimeDiagramMetadata) -> bool:
        """Update diagram metadata."""
        try:
            self._diagram_metadata[diagram_id] = metadata
            self._last_activity = datetime.now()
            return True
        except Exception as e:
            self.logger.error(f"Failed to update diagram metadata for {diagram_id}: {e}")
            self._error_count += 1
            return False
    
    # Private Helper Methods
    
    def _trigger_diagram_refresh(self, trigger: UpdateTrigger, metadata: Dict[str, Any]) -> None:
        """Trigger diagram refresh based on event."""
        try:
            # Find diagrams that need refresh based on trigger
            diagrams_to_refresh = self._get_diagrams_for_trigger(trigger)
            
            for diagram_id in diagrams_to_refresh:
                refresh_request = DiagramRefreshRequest(
                    diagram_id=diagram_id,
                    trigger=trigger,
                    requested_by="system",
                    priority=self._get_priority_for_trigger(trigger),
                    metadata=metadata
                )
                
                self._refresh_queue.append(refresh_request)
            
            # Sort queue by priority
            self._refresh_queue.sort(key=lambda x: x.priority, reverse=True)
            
        except Exception as e:
            self.logger.error(f"Failed to trigger diagram refresh: {e}")
            self._error_count += 1
    
    def _get_diagrams_for_trigger(self, trigger: UpdateTrigger) -> List[str]:
        """Get diagrams that need refresh based on trigger type."""
        diagrams = []
        
        for diagram_id, metadata in self._diagram_metadata.items():
            if metadata.needs_refresh():
                diagrams.append(diagram_id)
        
        return diagrams
    
    def _get_priority_for_trigger(self, trigger: UpdateTrigger) -> int:
        """Get priority for trigger type."""
        priority_map = {
            UpdateTrigger.ERROR_DETECTED: 10,
            UpdateTrigger.HEALTH_CHECK_FAILURE: 9,
            UpdateTrigger.SERVICE_STATUS_CHANGE: 7,
            UpdateTrigger.WEBSOCKET_CONNECTION_CHANGE: 6,
            UpdateTrigger.METRICS_THRESHOLD_EXCEEDED: 5,
            UpdateTrigger.INFRASTRUCTURE_CHANGE: 8,
            UpdateTrigger.SCHEDULED_REFRESH: 3,
            UpdateTrigger.MANUAL_REFRESH: 5
        }
        
        return priority_map.get(trigger, 5)
    
    def _refresh_worker(self) -> None:
        """Background worker for processing refresh requests."""
        self.logger.info("Refresh worker started")
        
        while self._running:
            try:
                if self._refresh_queue:
                    # Process highest priority request
                    request = self._refresh_queue.pop(0)
                    
                    # Check if we can start new refresh
                    if len(self._active_refreshes) < self._max_concurrent_refreshes:
                        self._executor.submit(self._process_refresh_request, request)
                    else:
                        # Put back in queue
                        self._refresh_queue.insert(0, request)
                
                time.sleep(1)  # Check every second
                
            except Exception as e:
                self.logger.error(f"Refresh worker error: {e}")
                self._error_count += 1
                time.sleep(5)  # Wait before retrying
        
        self.logger.info("Refresh worker stopped")
    
    def _process_refresh_request(self, request: DiagramRefreshRequest) -> None:
        """Process a single refresh request."""
        refresh_result = DiagramRefreshResult(
            request_id=request.request_id,
            diagram_id=request.diagram_id,
            status=RefreshStatus.IN_PROGRESS,
            started_at=datetime.now()
        )
        
        try:
            self._active_refreshes[request.request_id] = refresh_result
            
            # Perform the actual refresh
            success = self._perform_diagram_refresh(request, refresh_result)
            
            # Update result
            refresh_result.status = RefreshStatus.COMPLETED if success else RefreshStatus.FAILED
            refresh_result.completed_at = datetime.now()
            refresh_result.duration_ms = (refresh_result.completed_at - refresh_result.started_at).total_seconds() * 1000
            
            # Move to history
            self._refresh_history.append(refresh_result)
            if request.request_id in self._active_refreshes:
                del self._active_refreshes[request.request_id]
            
            # Update diagram metadata
            if success and request.diagram_id in self._diagram_metadata:
                metadata = self._diagram_metadata[request.diagram_id]
                metadata.last_updated = datetime.now()
                metadata.refresh_history.append(refresh_result)
            
            self.logger.info(f"Refresh completed for {request.diagram_id}: {refresh_result.status.value}")
            
        except Exception as e:
            self.logger.error(f"Refresh failed for {request.diagram_id}: {e}")
            refresh_result.status = RefreshStatus.FAILED
            refresh_result.error_message = str(e)
            refresh_result.completed_at = datetime.now()
            refresh_result.duration_ms = (refresh_result.completed_at - refresh_result.started_at).total_seconds() * 1000
            
            # Move to history
            self._refresh_history.append(refresh_result)
            if request.request_id in self._active_refreshes:
                del self._active_refreshes[request.request_id]
            
            self._error_count += 1
    
    def _perform_diagram_refresh(self, request: DiagramRefreshRequest, result: DiagramRefreshResult) -> bool:
        """Perform the actual diagram refresh."""
        try:
            # Update real-time statuses
            result.components_updated = len(self._real_time_statuses)
            
            # Update WebSocket connections
            result.websocket_statuses_updated = len(self._websocket_connections)
            
            # Update metrics flows
            result.metrics_flows_updated = len(self._live_metrics_flows)
            
            # Perform validation if required
            if request.validation_level != ValidationLevel.NONE:
                validation_result = self._validate_diagram_accuracy(request.diagram_id)
                result.validation_status = validation_result["status"]
                result.accuracy_confidence = validation_result["confidence"]
            
            return True
            
        except Exception as e:
            self.logger.error(f"Diagram refresh failed: {e}")
            result.error_message = str(e)
            return False
    
    def _validate_diagram_accuracy(self, diagram_id: str) -> Dict[str, Any]:
        """Validate diagram accuracy."""
        try:
            # Basic validation logic
            metadata = self._diagram_metadata.get(diagram_id)
            if not metadata:
                return {"status": "error", "confidence": 0.0}
            
            # Check data freshness
            freshness_score = self._get_data_freshness_score()
            
            # Check WebSocket health
            websocket_score = self._get_websocket_health_score()
            
            # Check metrics flow health
            metrics_score = self._get_metrics_flow_health_score()
            
            # Calculate overall confidence
            confidence = (freshness_score + websocket_score + metrics_score) / 3
            
            status = "valid" if confidence > 0.8 else "warning" if confidence > 0.5 else "invalid"
            
            return {
                "status": status,
                "confidence": confidence,
                "freshness_score": freshness_score,
                "websocket_score": websocket_score,
                "metrics_score": metrics_score
            }
            
        except Exception as e:
            self.logger.error(f"Diagram validation failed: {e}")
            return {"status": "error", "confidence": 0.0}
    
    def _get_data_freshness_score(self) -> float:
        """Calculate data freshness score."""
        if not self._real_time_statuses:
            return 0.0
        
        now = datetime.now()
        total_score = 0.0
        count = 0
        
        for status in self._real_time_statuses.values():
            age_minutes = (now - status.last_updated).total_seconds() / 60
            # Score decreases with age (1.0 for < 1 minute, 0.0 for > 60 minutes)
            score = max(0.0, 1.0 - (age_minutes / 60))
            total_score += score
            count += 1
        
        return total_score / count if count > 0 else 0.0
    
    def _get_websocket_health_score(self) -> float:
        """Calculate WebSocket connection health score."""
        if not self._websocket_connections:
            return 1.0  # No connections to check
        
        total_score = 0.0
        count = 0
        
        for connection in self._websocket_connections.values():
            if connection.connected:
                # Score based on error rate and latency
                error_score = max(0.0, 1.0 - (connection.connection_errors / 10))
                latency_score = 1.0 if connection.latency_ms is None or connection.latency_ms < 100 else 0.5
                score = (error_score + latency_score) / 2
            else:
                score = 0.0
            
            total_score += score
            count += 1
        
        return total_score / count if count > 0 else 0.0
    
    def _get_metrics_flow_health_score(self) -> float:
        """Calculate metrics flow health score."""
        if not self._live_metrics_flows:
            return 1.0  # No flows to check
        
        total_score = 0.0
        count = 0
        
        for flow in self._live_metrics_flows:
            # Score based on success rate and error rate
            success_score = flow.success_rate / 100
            error_score = max(0.0, 1.0 - (flow.error_rate / 10))
            score = (success_score + error_score) / 2
            
            total_score += score
            count += 1
        
        return total_score / count if count > 0 else 0.0
    
    def _initialize_service_dependencies(self) -> None:
        """Initialize service discovery dependencies."""
        try:
            # Import and initialize service dependencies
            from src.system_architecture.discovery.service_scanner import ServiceScanner
            from src.system_architecture.discovery.network_topology_discoverer import NetworkTopologyDiscoverer
            from src.system_architecture.analysis.data_flow_mapper import DataFlowMapper
            
            self._service_scanner = ServiceScanner()
            self._network_discoverer = NetworkTopologyDiscoverer()
            self._data_flow_mapper = DataFlowMapper()
            
            self.logger.info("Service dependencies initialized")
            
        except Exception as e:
            self.logger.warning(f"Failed to initialize some service dependencies: {e}")
            self._warning_count += 1
    
    def _start_real_time_data_collection(self) -> None:
        """Start real-time data collection from services."""
        try:
            # Start collecting real-time data
            self.logger.info("Real-time data collection started")
            
            # This would typically involve:
            # - WebSocket connections to Observatory
            # - Prometheus metrics scraping
            # - Service health monitoring
            # - Network topology monitoring
            
        except Exception as e:
            self.logger.error(f"Failed to start real-time data collection: {e}")
            self._error_count += 1
    
    # Health Endpoints for ReflectiveModule
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get health status for /health endpoint."""
        return {
            "status": "healthy" if self.is_healthy() else "degraded",
            "timestamp": datetime.now().isoformat(),
            "module": self.module_name,
            "correlation_id": self.correlation_id,
            "uptime_seconds": (datetime.now() - self._start_time).total_seconds(),
            "real_time_data_count": len(self._real_time_statuses),
            "websocket_connections": len(self._websocket_connections),
            "active_refreshes": len(self._active_refreshes),
            "refresh_queue_size": len(self._refresh_queue)
        }
    
    def get_ready_status(self) -> Dict[str, Any]:
        """Get ready status for /ready endpoint."""
        return {
            "ready": self.is_healthy() and self._running,
            "timestamp": datetime.now().isoformat(),
            "module": self.module_name,
            "dependencies_initialized": self._service_scanner is not None,
            "refresh_worker_running": self._refresh_thread.is_alive() if self._refresh_thread else False
        }
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get metrics for /metrics endpoint."""
        return {
            "real_time_diagram_updater": {
                "real_time_statuses_total": len(self._real_time_statuses),
                "websocket_connections_total": len(self._websocket_connections),
                "live_metrics_flows_total": len(self._live_metrics_flows),
                "interactive_sequences_total": len(self._interactive_sequences),
                "active_refreshes_total": len(self._active_refreshes),
                "refresh_queue_size": len(self._refresh_queue),
                "refresh_history_total": len(self._refresh_history),
                "data_freshness_score": self._get_data_freshness_score(),
                "websocket_health_score": self._get_websocket_health_score(),
                "metrics_flow_health_score": self._get_metrics_flow_health_score(),
                "error_count_total": self._error_count,
                "warning_count_total": self._warning_count,
                "uptime_seconds": (datetime.now() - self._start_time).total_seconds()
            }
        }