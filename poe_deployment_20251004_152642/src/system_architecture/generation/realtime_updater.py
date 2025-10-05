#!/usr/bin/env python3
"""
Real-Time Diagram Updater - Task 3.4 Implementation
===================================================

Creates RealTimeDiagramUpdater class integrating with Observatory WebSocket feeds.
Generates live component diagrams with real-time service status indicators.
Implements automated diagram refresh within 1 hour of infrastructure changes.

Author: Beast Mode Framework
Date: 2025-01-03
Version: 1.0
"""

import logging
import json
import asyncio
import websockets
from typing import Dict, List, Any, Optional, Set, Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
import threading
import time

from src.rm_ddd.core.unified_reflective_module import ReflectiveModule, ModuleCapability, GracefulDegradationResult
from src.system_architecture.models.diagram_models import DiagramMetadata, RealTimeStatus, ServiceStatus, ValidationStatus
from src.system_architecture.generation.diagram_generator import DiagramGenerator
from src.system_architecture.generation.network_visualizer import NetworkTopologyVisualizer


@dataclass
class UpdateConfig:
    """Configuration for real-time diagram updates."""
    observatory_websocket_url: str = "ws://localhost:8888"
    update_interval_seconds: int = 300  # 5 minutes
    change_detection_threshold: float = 0.1  # 10% change threshold
    max_update_frequency_seconds: int = 60  # Max 1 update per minute
    staleness_threshold_hours: int = 1  # Mark stale after 1 hour
    auto_refresh_enabled: bool = True
    websocket_reconnect_delay: int = 5  # seconds
    max_reconnect_attempts: int = 10


@dataclass
class ChangeEvent:
    """Infrastructure change event."""
    event_id: str
    event_type: str
    component_id: str
    change_description: str
    timestamp: datetime
    severity: str  # "low", "medium", "high", "critical"
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class UpdateResult:
    """Result of diagram update operation."""
    update_id: str
    diagram_ids: List[str]
    changes_detected: List[ChangeEvent]
    update_timestamp: datetime
    success: bool
    error_message: Optional[str] = None
    files_updated: List[str] = field(default_factory=list)
    validation_results: Dict[str, Any] = field(default_factory=dict)


class RealTimeDiagramUpdater(ReflectiveModule):
    """
    Real-time diagram updater integrating with Observatory WebSocket feeds.
    
    Implements Task 3.4 from the system architecture wiring diagram specification.
    Provides live component diagrams with real-time service status indicators,
    WebSocket connection status overlays, and automated refresh mechanisms.
    """
    
    def __init__(self, 
                 diagram_generator: DiagramGenerator,
                 network_visualizer: NetworkTopologyVisualizer,
                 config: Optional[UpdateConfig] = None):
        super().__init__()
        self.module_id = "RealTimeDiagramUpdater"
        self._logger = logging.getLogger(f"system_architecture.{self.__class__.__name__}")
        
        # Configuration
        self._config = config or UpdateConfig()
        
        # Dependencies
        self._diagram_generator = diagram_generator
        self._network_visualizer = network_visualizer
        
        # State management
        self._websocket_connection: Optional[websockets.WebSocketServerProtocol] = None
        self._is_running = False
        self._update_thread: Optional[threading.Thread] = None
        self._websocket_thread: Optional[threading.Thread] = None
        
        # Change tracking
        self._change_events: List[ChangeEvent] = []
        self._last_update_time: Optional[datetime] = None
        self._component_status_cache: Dict[str, RealTimeStatus] = {}
        self._diagram_metadata_cache: Dict[str, DiagramMetadata] = {}
        
        # Update callbacks
        self._update_callbacks: List[Callable[[UpdateResult], None]] = []
        
        # WebSocket endpoints to monitor
        self._websocket_endpoints = [
            "/ws/observatory",
            "/ws/emoji-rain", 
            "/ws/anomalies",
            "/ws/doctor-status"
        ]
        
        self._logger.info("RealTimeDiagramUpdater initialized")
    
    def get_capabilities(self) -> List[ModuleCapability]:
        """Get module capabilities."""
        return [
            ModuleCapability.CORE_FUNCTIONALITY,
            ModuleCapability.DATA_PROCESSING,
            ModuleCapability.MONITORING
        ]
    
    def start_real_time_updates(self) -> None:
        """Start real-time diagram update system."""
        self._logger.info("Starting real-time diagram update system...")
        
        if self._is_running:
            self._logger.warning("Real-time updates already running")
            return
        
        self._is_running = True
        
        # Start WebSocket monitoring thread
        self._websocket_thread = threading.Thread(
            target=self._websocket_monitor_loop,
            name="WebSocketMonitor",
            daemon=True
        )
        self._websocket_thread.start()
        
        # Start update processing thread
        self._update_thread = threading.Thread(
            target=self._update_processing_loop,
            name="UpdateProcessor", 
            daemon=True
        )
        self._update_thread.start()
        
        self._logger.info("Real-time update system started")
    
    def stop_real_time_updates(self) -> None:
        """Stop real-time diagram update system."""
        self._logger.info("Stopping real-time diagram update system...")
        
        self._is_running = False
        
        # Close WebSocket connection
        if self._websocket_connection:
            asyncio.create_task(self._websocket_connection.close())
        
        # Wait for threads to finish
        if self._websocket_thread and self._websocket_thread.is_alive():
            self._websocket_thread.join(timeout=5)
        
        if self._update_thread and self._update_thread.is_alive():
            self._update_thread.join(timeout=5)
        
        self._logger.info("Real-time update system stopped")
    
    def _websocket_monitor_loop(self) -> None:
        """WebSocket monitoring loop running in separate thread."""
        reconnect_attempts = 0
        
        while self._is_running and reconnect_attempts < self._config.max_reconnect_attempts:
            try:
                # Run WebSocket client
                asyncio.run(self._websocket_client())
                reconnect_attempts = 0  # Reset on successful connection
                
            except Exception as e:
                reconnect_attempts += 1
                self._logger.error(f"WebSocket connection failed (attempt {reconnect_attempts}): {e}")
                
                if reconnect_attempts < self._config.max_reconnect_attempts:
                    self._logger.info(f"Reconnecting in {self._config.websocket_reconnect_delay} seconds...")
                    time.sleep(self._config.websocket_reconnect_delay)
                else:
                    self._logger.error("Max reconnection attempts reached, stopping WebSocket monitoring")
                    break
    
    async def _websocket_client(self) -> None:
        """WebSocket client for monitoring Observatory events."""
        websocket_url = f"{self._config.observatory_websocket_url}/ws/observatory"
        
        try:
            self._logger.info(f"Connecting to WebSocket: {websocket_url}")
            
            async with websockets.connect(websocket_url) as websocket:
                self._websocket_connection = websocket
                self._logger.info("WebSocket connection established")
                
                # Send subscription message
                subscription = {
                    "type": "subscribe",
                    "events": ["service_status", "component_health", "infrastructure_change"],
                    "client_id": "diagram_updater"
                }
                await websocket.send(json.dumps(subscription))
                
                # Listen for messages
                async for message in websocket:
                    if not self._is_running:
                        break
                    
                    try:
                        await self._handle_websocket_message(message)
                    except Exception as e:
                        self._logger.error(f"Error handling WebSocket message: {e}")
                        
        except Exception as e:
            self._logger.error(f"WebSocket client error: {e}")
            raise
    
    async def _handle_websocket_message(self, message: str) -> None:
        """Handle incoming WebSocket message."""
        try:
            data = json.loads(message)
            event_type = data.get("type", "unknown")
            
            if event_type == "service_status":
                await self._handle_service_status_event(data)
            elif event_type == "component_health":
                await self._handle_component_health_event(data)
            elif event_type == "infrastructure_change":
                await self._handle_infrastructure_change_event(data)
            else:
                self._logger.debug(f"Unhandled WebSocket event type: {event_type}")
                
        except json.JSONDecodeError as e:
            self._logger.error(f"Invalid JSON in WebSocket message: {e}")
        except Exception as e:
            self._logger.error(f"Error processing WebSocket message: {e}")
    
    async def _handle_service_status_event(self, data: Dict[str, Any]) -> None:
        """Handle service status change event."""
        component_id = data.get("component_id")
        status = data.get("status")
        
        if not component_id or not status:
            return
        
        # Update status cache
        real_time_status = RealTimeStatus(
            component_id=component_id,
            status=ServiceStatus(status),
            health_score=data.get("health_score", 0.0),
            response_time_ms=data.get("response_time_ms"),
            error_rate=data.get("error_rate", 0.0),
            uptime_percentage=data.get("uptime_percentage", 100.0),
            active_connections=data.get("active_connections", 0),
            resource_usage=data.get("resource_usage", {}),
            alerts=data.get("alerts", []),
            metadata=data.get("metadata", {})
        )
        
        # Check for significant changes
        old_status = self._component_status_cache.get(component_id)
        if self._is_significant_change(old_status, real_time_status):
            change_event = ChangeEvent(
                event_id=f"status_{component_id}_{int(time.time())}",
                event_type="service_status_change",
                component_id=component_id,
                change_description=f"Status changed from {old_status.status.value if old_status else 'unknown'} to {status}",
                timestamp=datetime.now(),
                severity=self._determine_change_severity(old_status, real_time_status),
                metadata={"old_status": old_status.to_dict() if old_status else None, "new_status": real_time_status.to_dict()}
            )
            self._change_events.append(change_event)
        
        # Update cache
        self._component_status_cache[component_id] = real_time_status
        
        # Update diagram generator cache
        self._diagram_generator.update_real_time_status(component_id, real_time_status)
    
    async def _handle_component_health_event(self, data: Dict[str, Any]) -> None:
        """Handle component health change event."""
        component_id = data.get("component_id")
        health_score = data.get("health_score", 0.0)
        
        if not component_id:
            return
        
        # Create change event for significant health changes
        old_status = self._component_status_cache.get(component_id)
        if old_status and abs(old_status.health_score - health_score) > self._config.change_detection_threshold:
            change_event = ChangeEvent(
                event_id=f"health_{component_id}_{int(time.time())}",
                event_type="component_health_change",
                component_id=component_id,
                change_description=f"Health score changed from {old_status.health_score:.2f} to {health_score:.2f}",
                timestamp=datetime.now(),
                severity="medium" if abs(old_status.health_score - health_score) > 0.3 else "low",
                metadata={"old_health": old_status.health_score, "new_health": health_score}
            )
            self._change_events.append(change_event)
    
    async def _handle_infrastructure_change_event(self, data: Dict[str, Any]) -> None:
        """Handle infrastructure change event."""
        change_event = ChangeEvent(
            event_id=data.get("event_id", f"infra_{int(time.time())}"),
            event_type="infrastructure_change",
            component_id=data.get("component_id", "unknown"),
            change_description=data.get("description", "Infrastructure change detected"),
            timestamp=datetime.fromisoformat(data.get("timestamp", datetime.now().isoformat())),
            severity=data.get("severity", "medium"),
            metadata=data.get("metadata", {})
        )
        self._change_events.append(change_event)
    
    def _is_significant_change(self, old_status: Optional[RealTimeStatus], new_status: RealTimeStatus) -> bool:
        """Determine if status change is significant enough to trigger update."""
        if not old_status:
            return True  # First status is always significant
        
        # Status change is always significant
        if old_status.status != new_status.status:
            return True
        
        # Health score change > threshold
        if abs(old_status.health_score - new_status.health_score) > self._config.change_detection_threshold:
            return True
        
        # Error rate change > threshold
        if abs(old_status.error_rate - new_status.error_rate) > self._config.change_detection_threshold:
            return True
        
        # New alerts
        if len(new_status.alerts) > len(old_status.alerts):
            return True
        
        return False
    
    def _determine_change_severity(self, old_status: Optional[RealTimeStatus], new_status: RealTimeStatus) -> str:
        """Determine severity of status change."""
        if not old_status:
            return "low"
        
        # Service going down is critical
        if old_status.status in [ServiceStatus.HEALTHY, ServiceStatus.DEGRADED] and new_status.status == ServiceStatus.DOWN:
            return "critical"
        
        # Service recovering is medium
        if old_status.status == ServiceStatus.DOWN and new_status.status in [ServiceStatus.HEALTHY, ServiceStatus.DEGRADED]:
            return "medium"
        
        # Health score dropping significantly is high
        if old_status.health_score - new_status.health_score > 0.5:
            return "high"
        
        # Error rate increasing significantly is medium
        if new_status.error_rate - old_status.error_rate > 0.1:
            return "medium"
        
        return "low"    

    def _update_processing_loop(self) -> None:
        """Update processing loop running in separate thread."""
        while self._is_running:
            try:
                # Check if update is needed
                if self._should_trigger_update():
                    self._logger.info("Triggering diagram update due to changes")
                    update_result = self._perform_diagram_update()
                    
                    # Notify callbacks
                    for callback in self._update_callbacks:
                        try:
                            callback(update_result)
                        except Exception as e:
                            self._logger.error(f"Error in update callback: {e}")
                
                # Check for stale diagrams
                self._check_for_stale_diagrams()
                
                # Sleep until next check
                time.sleep(self._config.update_interval_seconds)
                
            except Exception as e:
                self._logger.error(f"Error in update processing loop: {e}")
                time.sleep(self._config.update_interval_seconds)
    
    def _should_trigger_update(self) -> bool:
        """Determine if diagram update should be triggered."""
        # Check if we have pending changes
        if not self._change_events:
            return False
        
        # Check minimum update frequency
        if self._last_update_time:
            time_since_last = datetime.now() - self._last_update_time
            if time_since_last.total_seconds() < self._config.max_update_frequency_seconds:
                return False
        
        # Check for high/critical severity changes (immediate update)
        for event in self._change_events:
            if event.severity in ["high", "critical"]:
                return True
        
        # Check for accumulated medium/low changes (batch update)
        medium_low_changes = [e for e in self._change_events if e.severity in ["medium", "low"]]
        if len(medium_low_changes) >= 5:  # Batch threshold
            return True
        
        # Check for changes older than staleness threshold
        staleness_threshold = datetime.now() - timedelta(hours=self._config.staleness_threshold_hours)
        for event in self._change_events:
            if event.timestamp < staleness_threshold:
                return True
        
        return False
    
    def _perform_diagram_update(self) -> UpdateResult:
        """Perform diagram update based on accumulated changes."""
        update_id = f"update_{int(time.time())}"
        self._logger.info(f"Performing diagram update: {update_id}")
        
        try:
            # Get current changes to process
            changes_to_process = self._change_events.copy()
            self._change_events.clear()  # Clear processed changes
            
            # Update diagrams
            updated_diagrams = []
            updated_files = []
            validation_results = {}
            
            # Update component diagrams
            component_diagrams = self._update_component_diagrams(changes_to_process)
            updated_diagrams.extend(component_diagrams)
            
            # Update network topology diagrams
            network_diagrams = self._update_network_diagrams(changes_to_process)
            updated_diagrams.extend(network_diagrams)
            
            # Save updated diagrams
            for diagram_id in updated_diagrams:
                diagram_metadata = self._diagram_metadata_cache.get(diagram_id)
                if diagram_metadata:
                    # Add "Last Updated" timestamp
                    diagram_metadata.generated_at = datetime.now()
                    diagram_metadata.metadata["last_updated"] = datetime.now().isoformat()
                    diagram_metadata.metadata["update_trigger"] = "real_time_change"
                    diagram_metadata.metadata["changes_processed"] = len(changes_to_process)
                    
                    # Validate diagram
                    validation_result = self._validate_updated_diagram(diagram_metadata)
                    validation_results[diagram_id] = validation_result
                    
                    # Save files if validation passes
                    if validation_result.get("status") == ValidationStatus.VALID:
                        files = self._save_updated_diagram(diagram_metadata)
                        updated_files.extend(files)
            
            # Update timestamp
            self._last_update_time = datetime.now()
            
            return UpdateResult(
                update_id=update_id,
                diagram_ids=updated_diagrams,
                changes_detected=changes_to_process,
                update_timestamp=datetime.now(),
                success=True,
                files_updated=updated_files,
                validation_results=validation_results
            )
            
        except Exception as e:
            self._logger.error(f"Error performing diagram update: {e}")
            return UpdateResult(
                update_id=update_id,
                diagram_ids=[],
                changes_detected=changes_to_process if 'changes_to_process' in locals() else [],
                update_timestamp=datetime.now(),
                success=False,
                error_message=str(e)
            )
    
    def _update_component_diagrams(self, changes: List[ChangeEvent]) -> List[str]:
        """Update component diagrams based on changes."""
        updated_diagrams = []
        
        # Get affected components
        affected_components = set(change.component_id for change in changes)
        
        # Update diagrams containing affected components
        for diagram_id, diagram_metadata in self._diagram_metadata_cache.items():
            if diagram_metadata.diagram_type.value == "component":
                # Check if any components in this diagram are affected
                diagram_component_ids = {comp.id for comp in diagram_metadata.components}
                if diagram_component_ids.intersection(affected_components):
                    # Update real-time status for affected components
                    for component_id in affected_components:
                        if component_id in self._component_status_cache:
                            status = self._component_status_cache[component_id]
                            diagram_metadata.real_time_status[component_id] = status
                            
                            # Update component status in metadata
                            for component in diagram_metadata.components:
                                if component.id == component_id:
                                    component.status = status.status
                                    component.health_score = status.health_score
                                    component.last_updated = datetime.now()
                    
                    # Recalculate accuracy confidence
                    diagram_metadata.accuracy_confidence = diagram_metadata.calculate_accuracy_confidence()
                    
                    updated_diagrams.append(diagram_id)
        
        return updated_diagrams
    
    def _update_network_diagrams(self, changes: List[ChangeEvent]) -> List[str]:
        """Update network topology diagrams based on changes."""
        updated_diagrams = []
        
        # Check for network-related changes
        network_changes = [
            change for change in changes 
            if change.event_type in ["infrastructure_change", "service_status_change"]
            and any(keyword in change.change_description.lower() 
                   for keyword in ["network", "connection", "tunnel", "dns", "websocket"])
        ]
        
        if network_changes:
            # Update network topology visualizations
            # This would trigger regeneration of network flow diagrams
            updated_diagrams.append("network_topology_main")
            updated_diagrams.append("websocket_flows")
        
        return updated_diagrams
    
    def _validate_updated_diagram(self, diagram_metadata: DiagramMetadata) -> Dict[str, Any]:
        """Validate updated diagram and calculate accuracy confidence."""
        validation_issues = diagram_metadata.validate_diagram()
        confidence = diagram_metadata.calculate_accuracy_confidence()
        
        # Determine validation status
        if len(validation_issues) == 0 and confidence >= 0.95:
            status = ValidationStatus.VALID
        elif len(validation_issues) > 0:
            status = ValidationStatus.INVALID
        elif confidence < 0.95:
            status = ValidationStatus.WARNING
        else:
            status = ValidationStatus.PENDING
        
        return {
            "status": status,
            "confidence": confidence,
            "issues": validation_issues,
            "validation_timestamp": datetime.now().isoformat()
        }
    
    def _save_updated_diagram(self, diagram_metadata: DiagramMetadata) -> List[str]:
        """Save updated diagram to files."""
        # This would use the diagram generator to save updated files
        # For now, return placeholder file paths
        base_path = f"generated_diagrams/{diagram_metadata.diagram_id}"
        return [
            f"{base_path}.svg",
            f"{base_path}.html", 
            f"{base_path}_metadata.json"
        ]
    
    def _check_for_stale_diagrams(self) -> None:
        """Check for stale diagrams and mark them for update."""
        staleness_threshold = datetime.now() - timedelta(hours=self._config.staleness_threshold_hours)
        
        for diagram_id, diagram_metadata in self._diagram_metadata_cache.items():
            if diagram_metadata.generated_at < staleness_threshold:
                if diagram_metadata.validation_status != ValidationStatus.STALE:
                    self._logger.warning(f"Diagram {diagram_id} is stale (last updated: {diagram_metadata.generated_at})")
                    diagram_metadata.validation_status = ValidationStatus.STALE
                    
                    # Create staleness change event
                    change_event = ChangeEvent(
                        event_id=f"stale_{diagram_id}_{int(time.time())}",
                        event_type="diagram_staleness",
                        component_id=diagram_id,
                        change_description=f"Diagram {diagram_id} is stale (>{self._config.staleness_threshold_hours}h old)",
                        timestamp=datetime.now(),
                        severity="medium",
                        metadata={"last_updated": diagram_metadata.generated_at.isoformat()}
                    )
                    self._change_events.append(change_event)
    
    def add_update_callback(self, callback: Callable[[UpdateResult], None]) -> None:
        """Add callback to be notified of diagram updates."""
        self._update_callbacks.append(callback)
    
    def remove_update_callback(self, callback: Callable[[UpdateResult], None]) -> None:
        """Remove update callback."""
        if callback in self._update_callbacks:
            self._update_callbacks.remove(callback)
    
    def force_update(self, diagram_ids: Optional[List[str]] = None) -> UpdateResult:
        """Force immediate update of specified diagrams or all diagrams."""
        self._logger.info(f"Forcing diagram update for: {diagram_ids or 'all diagrams'}")
        
        # Create force update change event
        change_event = ChangeEvent(
            event_id=f"force_update_{int(time.time())}",
            event_type="force_update",
            component_id="system",
            change_description="Manual diagram update requested",
            timestamp=datetime.now(),
            severity="high",
            metadata={"diagram_ids": diagram_ids}
        )
        self._change_events.append(change_event)
        
        # Trigger immediate update
        return self._perform_diagram_update()
    
    def get_websocket_connection_status(self) -> Dict[str, Any]:
        """Get WebSocket connection status overlay information."""
        status = {
            "connected": self._websocket_connection is not None and not self._websocket_connection.closed,
            "last_message_time": None,
            "reconnect_attempts": 0,
            "monitored_endpoints": self._websocket_endpoints,
            "active_subscriptions": ["service_status", "component_health", "infrastructure_change"]
        }
        
        if self._websocket_connection:
            status["connection_state"] = "connected"
            status["remote_address"] = str(self._websocket_connection.remote_address)
        else:
            status["connection_state"] = "disconnected"
        
        return status
    
    def get_change_detection_status(self) -> Dict[str, Any]:
        """Get change detection and notification system status."""
        return {
            "is_running": self._is_running,
            "pending_changes": len(self._change_events),
            "last_update_time": self._last_update_time.isoformat() if self._last_update_time else None,
            "cached_components": len(self._component_status_cache),
            "cached_diagrams": len(self._diagram_metadata_cache),
            "update_callbacks": len(self._update_callbacks),
            "config": {
                "update_interval": self._config.update_interval_seconds,
                "staleness_threshold": self._config.staleness_threshold_hours,
                "auto_refresh_enabled": self._config.auto_refresh_enabled
            }
        }
    
    def get_recent_changes(self, limit: int = 10) -> List[ChangeEvent]:
        """Get recent change events."""
        return sorted(self._change_events, key=lambda x: x.timestamp, reverse=True)[:limit]
    
    def register_diagram_metadata(self, diagram_metadata: DiagramMetadata) -> None:
        """Register diagram metadata for real-time updates."""
        self._diagram_metadata_cache[diagram_metadata.diagram_id] = diagram_metadata
        self._logger.info(f"Registered diagram for real-time updates: {diagram_metadata.diagram_id}")
    
    def unregister_diagram_metadata(self, diagram_id: str) -> None:
        """Unregister diagram metadata from real-time updates."""
        if diagram_id in self._diagram_metadata_cache:
            del self._diagram_metadata_cache[diagram_id]
            self._logger.info(f"Unregistered diagram from real-time updates: {diagram_id}")
    
    def graceful_degradation(self, error: Exception) -> GracefulDegradationResult:
        """Handle graceful degradation on errors."""
        self._logger.warning(f"Graceful degradation triggered: {error}")
        
        # Stop real-time updates if running
        if self._is_running:
            self.stop_real_time_updates()
        
        return GracefulDegradationResult(
            success=True,
            message=f"RealTimeDiagramUpdater degraded due to: {str(error)}",
            fallback_data={
                "pending_changes": len(self._change_events),
                "cached_components": len(self._component_status_cache),
                "cached_diagrams": len(self._diagram_metadata_cache),
                "websocket_status": "disconnected",
                "last_update": self._last_update_time.isoformat() if self._last_update_time else None
            }
        )