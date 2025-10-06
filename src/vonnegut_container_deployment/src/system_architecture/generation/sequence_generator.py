#!/usr/bin/env python3
"""
Sequence Diagram Generator - Task 3.2 Implementation
===================================================

Creates SequenceDiagramGenerator class for Observatory operational workflows.
Generates tunnel-start/tunnel-stop sequence diagrams with DNS propagation flows.
Includes WebSocket connection establishment in tunnel startup sequences.

Author: Beast Mode Framework
Date: 2025-01-03
Version: 1.0
"""

import logging
import json
from typing import Dict, List, Any, Optional, Set, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path

from src.rm_ddd.core.unified_reflective_module import ReflectiveModule, ModuleCapability, GracefulDegradationResult
from src.system_architecture.models.network_topology import NetworkTopology
from src.system_architecture.models.diagram_models import DiagramMetadata, DiagramFormat


@dataclass
class SequenceDiagramConfig:
    """Configuration for sequence diagram generation."""
    output_directory: Path = Path("generated_diagrams/sequences")
    include_timing: bool = True
    include_error_flows: bool = True
    include_validation_checkpoints: bool = True
    plantuml_format: bool = True
    detailed_annotations: bool = True


@dataclass
class OperationalSequence:
    """Operational sequence with timing and validation checkpoints."""
    sequence_id: str
    title: str
    description: str
    participants: List[str]
    steps: List[Dict[str, Any]]
    timing_estimates: Dict[str, str]
    validation_checkpoints: List[Dict[str, Any]]
    error_scenarios: List[Dict[str, Any]]
    plantuml_content: str
    metadata: Dict[str, Any] = field(default_factory=dict)


class SequenceDiagramGenerator(ReflectiveModule):
    """
    Creates sequence diagrams for Observatory operational workflows.
    
    Implements Task 3.2 from the system architecture wiring diagram specification.
    Generates detailed sequence diagrams for tunnel operations, dashboard lifecycle,
    and WebSocket connection establishment with timing estimates.
    """
    
    def __init__(self, config: Optional[SequenceDiagramConfig] = None):
        super().__init__()
        self.module_id = "SequenceDiagramGenerator"
        self._logger = logging.getLogger(f"system_architecture.{self.__class__.__name__}")
        
        # Configuration
        self._config = config or SequenceDiagramConfig()
        
        # Ensure output directory exists
        self._config.output_directory.mkdir(parents=True, exist_ok=True)
        
        # Generated sequences cache
        self._operational_sequences: Dict[str, OperationalSequence] = {}
        
        self._logger.info("SequenceDiagramGenerator initialized")
    
    def get_capabilities(self) -> List[ModuleCapability]:
        """Get module capabilities."""
        return [
            ModuleCapability.CORE_FUNCTIONALITY,
            ModuleCapability.DATA_PROCESSING,
            ModuleCapability.VALIDATION
        ]    

    def generate_tunnel_operation_sequences(self) -> List[OperationalSequence]:
        """
        Generate tunnel-start/tunnel-stop sequence diagrams with DNS propagation flows.
        
        Returns:
            List of operational sequences for tunnel operations with 30-60 second timing
        """
        self._logger.info("Generating tunnel operation sequence diagrams...")
        
        sequences = []
        
        # Generate tunnel-start sequence
        tunnel_start = self._generate_tunnel_start_sequence()
        sequences.append(tunnel_start)
        
        # Generate tunnel-stop sequence
        tunnel_stop = self._generate_tunnel_stop_sequence()
        sequences.append(tunnel_stop)
        
        # Generate tunnel-restart sequence
        tunnel_restart = self._generate_tunnel_restart_sequence()
        sequences.append(tunnel_restart)
        
        # Cache generated sequences
        for sequence in sequences:
            self._operational_sequences[sequence.sequence_id] = sequence
        
        self._logger.info(f"Generated {len(sequences)} tunnel operation sequences")
        return sequences
    
    def _generate_tunnel_start_sequence(self) -> OperationalSequence:
        """Generate tunnel-start sequence diagram with DNS propagation timing."""
        
        plantuml_content = """
@startuml tunnel_start_sequence
!theme plain
title Tunnel Start Sequence with DNS Propagation
note top : Cloudflare Tunnel ID: d1e53e43-033f-4994-8f46-c83962ae3785\\nEstimated Duration: 60-90 seconds

participant "Makefile" as Make
participant "Tunnel Script" as Script
participant "Cloudflare Daemon" as Daemon
participant "Cloudflare API" as API
participant "Edge Network" as Edge
participant "DNS System" as DNS
participant "Observatory Server" as Observatory
participant "WebSocket Handler" as WS

== Tunnel Startup Phase ==
Make -> Script : make tunnel-start
note right : Command: cloudflared tunnel run
Script -> Script : Validate credentials
note right : Check tunnel credentials file\\nValidate configuration
Script -> Daemon : Start cloudflared process
note right : Background process startup\\nPID tracking enabled

== Authentication Phase ==
Daemon -> API : Authenticate tunnel
note right : Tunnel ID: d1e53e43...\\nCredentials validation
API -> Daemon : Authentication success
note right : Tunnel registered\\nIngress rules loaded

== DNS Propagation Phase ==
API -> DNS : Update DNS records
note right : observatory.nkllon.com\\ngrafana.observatory.nkllon.com\\nprometheus.observatory.nkllon.com
DNS -> Edge : Propagate to edge servers
note right : Tier 1: 0-15 seconds\\nTier 2: 15-30 seconds\\nTier 3: 30-60 seconds

== Service Registration Phase ==
Daemon -> Observatory : Health check probe
note right : GET /health\\nValidate service availability
Observatory -> Daemon : Health response
note right : Status: healthy\\nWebSocket endpoints ready

== WebSocket Endpoint Registration ==
Observatory -> WS : Register WebSocket endpoints
note right : /ws/observatory\\n/ws/emoji-rain\\n/ws/anomalies\\n/ws/doctor-status
WS -> Observatory : Registration complete
note right : All endpoints active\\nConnection pooling ready

== Validation Phase ==
Script -> Daemon : Verify tunnel status
note right : Check process health\\nValidate connections
Daemon -> Script : Status: running
note right : Tunnel active\\nIngress rules applied
Script -> Make : Tunnel start complete
note right : Exit code: 0\\nDuration: ~60-90s

@enduml
"""
        
        steps = [
            {"step": 1, "actor": "Makefile", "action": "Execute make tunnel-start", "timing": "0s", "validation": "Command syntax"},
            {"step": 2, "actor": "Tunnel Script", "action": "Validate credentials and configuration", "timing": "1-2s", "validation": "Credentials file exists"},
            {"step": 3, "actor": "Cloudflare Daemon", "action": "Start cloudflared process", "timing": "2-5s", "validation": "Process starts successfully"},
            {"step": 4, "actor": "Cloudflare API", "action": "Authenticate tunnel", "timing": "5-10s", "validation": "Authentication success"},
            {"step": 5, "actor": "DNS System", "action": "Propagate DNS records", "timing": "10-60s", "validation": "DNS resolution works"},
            {"step": 6, "actor": "Observatory Server", "action": "Health check validation", "timing": "60-70s", "validation": "Health endpoint responds"},
            {"step": 7, "actor": "WebSocket Handler", "action": "Register WebSocket endpoints", "timing": "70-80s", "validation": "All endpoints active"},
            {"step": 8, "actor": "Tunnel Script", "action": "Final validation", "timing": "80-90s", "validation": "Tunnel fully operational"}
        ]
        
        timing_estimates = {
            "credential_validation": "1-2 seconds",
            "daemon_startup": "2-5 seconds", 
            "authentication": "5-10 seconds",
            "dns_propagation": "30-60 seconds",
            "service_validation": "10-20 seconds",
            "total_duration": "60-90 seconds"
        }
        
        validation_checkpoints = [
            {"checkpoint": "credentials_valid", "description": "Tunnel credentials file exists and is valid", "timing": "2s"},
            {"checkpoint": "daemon_running", "description": "Cloudflared process started successfully", "timing": "5s"},
            {"checkpoint": "tunnel_authenticated", "description": "Tunnel authenticated with Cloudflare API", "timing": "10s"},
            {"checkpoint": "dns_propagated", "description": "DNS records propagated to edge servers", "timing": "60s"},
            {"checkpoint": "services_healthy", "description": "All target services respond to health checks", "timing": "70s"},
            {"checkpoint": "websockets_active", "description": "WebSocket endpoints registered and active", "timing": "80s"}
        ]
        
        error_scenarios = [
            {"error": "invalid_credentials", "description": "Tunnel credentials invalid or missing", "recovery": "Check credentials file path"},
            {"error": "daemon_startup_failed", "description": "Cloudflared process failed to start", "recovery": "Check port availability and permissions"},
            {"error": "authentication_failed", "description": "Tunnel authentication with API failed", "recovery": "Verify tunnel ID and credentials"},
            {"error": "dns_propagation_timeout", "description": "DNS propagation taking longer than expected", "recovery": "Wait additional time or check DNS status"},
            {"error": "service_health_failed", "description": "Target services not responding to health checks", "recovery": "Start services before tunnel"},
            {"error": "websocket_registration_failed", "description": "WebSocket endpoints failed to register", "recovery": "Check Observatory server status"}
        ]
        
        return OperationalSequence(
            sequence_id="tunnel_start",
            title="Tunnel Start Sequence with DNS Propagation",
            description="Complete tunnel startup sequence including DNS propagation and WebSocket endpoint registration",
            participants=["Makefile", "Tunnel Script", "Cloudflare Daemon", "Cloudflare API", "Edge Network", "DNS System", "Observatory Server", "WebSocket Handler"],
            steps=steps,
            timing_estimates=timing_estimates,
            validation_checkpoints=validation_checkpoints,
            error_scenarios=error_scenarios,
            plantuml_content=plantuml_content,
            metadata={
                "tunnel_id": "d1e53e43-033f-4994-8f46-c83962ae3785",
                "domains": ["observatory.nkllon.com", "grafana.observatory.nkllon.com", "prometheus.observatory.nkllon.com"],
                "websocket_endpoints": ["/ws/observatory", "/ws/emoji-rain", "/ws/anomalies", "/ws/doctor-status"],
                "estimated_duration": "60-90 seconds"
            }
        )
    
    def _generate_tunnel_stop_sequence(self) -> OperationalSequence:
        """Generate tunnel-stop sequence diagram with graceful shutdown."""
        
        plantuml_content = """
@startuml tunnel_stop_sequence
!theme plain
title Tunnel Stop Sequence with Graceful Shutdown
note top : Graceful shutdown with connection cleanup\\nEstimated Duration: 30-45 seconds

participant "Makefile" as Make
participant "Tunnel Script" as Script
participant "Cloudflare Daemon" as Daemon
participant "WebSocket Handler" as WS
participant "Observatory Server" as Observatory
participant "Active Connections" as Connections
participant "Cloudflare API" as API

== Shutdown Initiation Phase ==
Make -> Script : make tunnel-stop
note right : Command: stop tunnel gracefully
Script -> Script : Find tunnel process
note right : Locate cloudflared PID\\nValidate process ownership

== Connection Cleanup Phase ==
Script -> WS : Signal shutdown
note right : Graceful WebSocket closure\\nNotify active connections
WS -> Connections : Send close frames
note right : WebSocket close code 1001\\nGoing away message
Connections -> WS : Acknowledge close
note right : Client connections closed\\nCleanup complete

== Service Deregistration Phase ==
WS -> Observatory : Deregister endpoints
note right : Remove /ws/* endpoints\\nStop accepting new connections
Observatory -> Observatory : Graceful shutdown
note right : Complete pending requests\\nClose health endpoints

== Tunnel Termination Phase ==
Script -> Daemon : Send SIGTERM
note right : Graceful shutdown signal\\nAllow connection cleanup
Daemon -> API : Deregister tunnel
note right : Remove tunnel registration\\nCleanup API resources
API -> Daemon : Deregistration complete
note right : Tunnel unregistered\\nResources released

== Process Cleanup Phase ==
Daemon -> Script : Process terminated
note right : Exit code: 0\\nCleanup complete
Script -> Script : Verify shutdown
note right : Check process stopped\\nValidate port released
Script -> Make : Tunnel stop complete
note right : All resources cleaned\\nDuration: ~30-45s

@enduml
"""
        
        steps = [
            {"step": 1, "actor": "Makefile", "action": "Execute make tunnel-stop", "timing": "0s", "validation": "Command executed"},
            {"step": 2, "actor": "Tunnel Script", "action": "Find and validate tunnel process", "timing": "1s", "validation": "Process found"},
            {"step": 3, "actor": "WebSocket Handler", "action": "Signal graceful shutdown", "timing": "2s", "validation": "Shutdown initiated"},
            {"step": 4, "actor": "Active Connections", "action": "Close WebSocket connections", "timing": "2-10s", "validation": "Connections closed"},
            {"step": 5, "actor": "Observatory Server", "action": "Deregister endpoints", "timing": "10-15s", "validation": "Endpoints removed"},
            {"step": 6, "actor": "Cloudflare Daemon", "action": "Deregister tunnel", "timing": "15-25s", "validation": "Tunnel unregistered"},
            {"step": 7, "actor": "Tunnel Script", "action": "Verify complete shutdown", "timing": "25-30s", "validation": "Process terminated"}
        ]
        
        return OperationalSequence(
            sequence_id="tunnel_stop",
            title="Tunnel Stop Sequence with Graceful Shutdown",
            description="Graceful tunnel shutdown with connection cleanup and resource deregistration",
            participants=["Makefile", "Tunnel Script", "Cloudflare Daemon", "WebSocket Handler", "Observatory Server", "Active Connections", "Cloudflare API"],
            steps=steps,
            timing_estimates={"total_duration": "30-45 seconds", "connection_cleanup": "10 seconds", "deregistration": "15 seconds"},
            validation_checkpoints=[
                {"checkpoint": "connections_closed", "description": "All WebSocket connections closed gracefully", "timing": "10s"},
                {"checkpoint": "endpoints_deregistered", "description": "WebSocket endpoints removed", "timing": "15s"},
                {"checkpoint": "tunnel_deregistered", "description": "Tunnel unregistered from API", "timing": "25s"},
                {"checkpoint": "process_terminated", "description": "Cloudflared process terminated", "timing": "30s"}
            ],
            error_scenarios=[
                {"error": "process_not_found", "description": "Tunnel process not running", "recovery": "Already stopped, no action needed"},
                {"error": "connections_timeout", "description": "WebSocket connections not closing", "recovery": "Force close after timeout"},
                {"error": "deregistration_failed", "description": "API deregistration failed", "recovery": "Continue with local cleanup"}
            ],
            plantuml_content=plantuml_content,
            metadata={"shutdown_type": "graceful", "estimated_duration": "30-45 seconds"}
        )
    
    def _generate_tunnel_restart_sequence(self) -> OperationalSequence:
        """Generate tunnel-restart sequence combining stop and start."""
        
        plantuml_content = """
@startuml tunnel_restart_sequence
!theme plain
title Tunnel Restart Sequence (Stop + Start)
note top : Combined stop and start operation\\nEstimated Duration: 90-135 seconds

participant "Makefile" as Make
participant "Tunnel Script" as Script
participant "Stop Process" as Stop
participant "Start Process" as Start
participant "Validation" as Validate

== Restart Initiation ==
Make -> Script : make tunnel-restart
note right : Combined stop/start operation
Script -> Stop : Execute tunnel stop
note right : Graceful shutdown first\\nClean state for restart

== Stop Phase ==
Stop -> Stop : Graceful shutdown
note right : 30-45 seconds\\nSee tunnel-stop sequence
Stop -> Script : Stop complete
note right : All resources cleaned\\nReady for restart

== Validation Phase ==
Script -> Validate : Verify clean state
note right : Check ports available\\nValidate no conflicts
Validate -> Script : State validated
note right : Safe to restart\\nNo resource conflicts

== Start Phase ==
Script -> Start : Execute tunnel start
note right : Fresh startup\\nSee tunnel-start sequence
Start -> Start : Complete startup
note right : 60-90 seconds\\nFull initialization
Start -> Script : Start complete
note right : Tunnel operational\\nAll endpoints active

== Final Validation ==
Script -> Validate : Verify restart success
note right : End-to-end validation\\nAll services healthy
Validate -> Script : Restart validated
note right : Full functionality confirmed
Script -> Make : Restart complete
note right : Total: 90-135 seconds

@enduml
"""
        
        return OperationalSequence(
            sequence_id="tunnel_restart",
            title="Tunnel Restart Sequence (Stop + Start)",
            description="Complete tunnel restart combining graceful stop and fresh start",
            participants=["Makefile", "Tunnel Script", "Stop Process", "Start Process", "Validation"],
            steps=[
                {"step": 1, "actor": "Makefile", "action": "Execute tunnel restart", "timing": "0s"},
                {"step": 2, "actor": "Stop Process", "action": "Graceful tunnel stop", "timing": "0-45s"},
                {"step": 3, "actor": "Validation", "action": "Verify clean state", "timing": "45-50s"},
                {"step": 4, "actor": "Start Process", "action": "Fresh tunnel start", "timing": "50-140s"},
                {"step": 5, "actor": "Validation", "action": "Verify restart success", "timing": "140-150s"}
            ],
            timing_estimates={"total_duration": "90-135 seconds", "stop_phase": "30-45 seconds", "start_phase": "60-90 seconds"},
            validation_checkpoints=[
                {"checkpoint": "stop_complete", "description": "Tunnel stopped and cleaned", "timing": "45s"},
                {"checkpoint": "state_validated", "description": "Clean state verified", "timing": "50s"},
                {"checkpoint": "start_complete", "description": "Tunnel started successfully", "timing": "140s"},
                {"checkpoint": "restart_validated", "description": "Full functionality confirmed", "timing": "150s"}
            ],
            error_scenarios=[
                {"error": "stop_failed", "description": "Graceful stop failed", "recovery": "Force kill and cleanup"},
                {"error": "state_conflict", "description": "Resources still in use", "recovery": "Wait and retry validation"},
                {"error": "start_failed", "description": "Restart failed", "recovery": "Check logs and retry"}
            ],
            plantuml_content=plantuml_content,
            metadata={"operation_type": "restart", "estimated_duration": "90-135 seconds"}
        )    

    def generate_dashboard_lifecycle_sequences(self) -> List[OperationalSequence]:
        """
        Generate dashboard-up/dashboard-stop/dashboard-restart lifecycle sequences.
        
        Returns:
            List of operational sequences for dashboard lifecycle with ReflectiveModule initialization
        """
        self._logger.info("Generating dashboard lifecycle sequence diagrams...")
        
        sequences = []
        
        # Generate dashboard-up sequence
        dashboard_up = self._generate_dashboard_up_sequence()
        sequences.append(dashboard_up)
        
        # Generate dashboard-stop sequence
        dashboard_stop = self._generate_dashboard_stop_sequence()
        sequences.append(dashboard_stop)
        
        # Generate dashboard-restart sequence
        dashboard_restart = self._generate_dashboard_restart_sequence()
        sequences.append(dashboard_restart)
        
        # Generate dashboard-status sequence
        dashboard_status = self._generate_dashboard_status_sequence()
        sequences.append(dashboard_status)
        
        # Cache generated sequences
        for sequence in sequences:
            self._operational_sequences[sequence.sequence_id] = sequence
        
        self._logger.info(f"Generated {len(sequences)} dashboard lifecycle sequences")
        return sequences
    
    def _generate_dashboard_up_sequence(self) -> OperationalSequence:
        """Generate dashboard-up sequence with ReflectiveModule initialization."""
        
        plantuml_content = """
@startuml dashboard_up_sequence
!theme plain
title Dashboard Up Sequence with ReflectiveModule Initialization
note top : Observatory Server startup with full observability\\nEstimated Duration: 45-60 seconds

participant "Makefile" as Make
participant "Dashboard Script" as Script
participant "Observatory Server" as Observatory
participant "ReflectiveModule" as RM
participant "WebSocket Handler" as WS
participant "Metrics Collector" as Metrics
participant "Health Monitor" as Health
participant "Redis Coordination" as Redis

== Initialization Phase ==
Make -> Script : make dashboard-up
note right : Start Observatory server
Script -> Observatory : Start observatory-daemon.py
note right : Python process startup\\nEnvironment validation

== ReflectiveModule Initialization ==
Observatory -> RM : Initialize ReflectiveModule
note right : Base class initialization\\nCapability registration
RM -> RM : Register capabilities
note right : CORE_FUNCTIONALITY\\nDATA_PROCESSING\\nMONITORING
RM -> Health : Initialize health endpoints
note right : /health, /ready, /metrics\\nHealth check framework

== Service Registration Phase ==
RM -> Metrics : Register metrics collectors
note right : Prometheus metrics\\nPerformance counters
Metrics -> RM : Collectors registered
note right : System metrics active\\nCustom metrics ready

== WebSocket Initialization ==
Observatory -> WS : Initialize WebSocket handler
note right : WebSocket server setup\\nEndpoint registration
WS -> WS : Register endpoints
note right : /ws/observatory\\n/ws/emoji-rain\\n/ws/anomalies\\n/ws/doctor-status
WS -> Observatory : WebSocket ready
note right : All endpoints active\\nConnection pooling enabled

== Coordination Setup ==
Observatory -> Redis : Connect to coordination
note right : Primary: 192.168.1.119:6379\\nFallback: localhost:6380
Redis -> Observatory : Connection established
note right : Coordination active\\nFailover configured

== Health Validation ==
Health -> Observatory : Validate all systems
note right : Component health checks\\nDependency validation
Observatory -> Health : All systems healthy
note right : Ready to serve traffic\\nFull functionality active

== Startup Complete ==
Observatory -> Script : Startup complete
note right : All systems operational\\nHealth endpoints active
Script -> Make : Dashboard up complete
note right : Exit code: 0\\nDuration: ~45-60s

@enduml
"""
        
        return OperationalSequence(
            sequence_id="dashboard_up",
            title="Dashboard Up Sequence with ReflectiveModule Initialization",
            description="Complete Observatory server startup with ReflectiveModule pattern and WebSocket endpoints",
            participants=["Makefile", "Dashboard Script", "Observatory Server", "ReflectiveModule", "WebSocket Handler", "Metrics Collector", "Health Monitor", "Redis Coordination"],
            steps=[
                {"step": 1, "actor": "Makefile", "action": "Execute dashboard-up", "timing": "0s", "validation": "Command executed"},
                {"step": 2, "actor": "Observatory Server", "action": "Process startup", "timing": "1-5s", "validation": "Process running"},
                {"step": 3, "actor": "ReflectiveModule", "action": "Initialize base framework", "timing": "5-10s", "validation": "Capabilities registered"},
                {"step": 4, "actor": "Health Monitor", "action": "Initialize health endpoints", "timing": "10-15s", "validation": "Endpoints active"},
                {"step": 5, "actor": "Metrics Collector", "action": "Register metrics", "timing": "15-20s", "validation": "Metrics collecting"},
                {"step": 6, "actor": "WebSocket Handler", "action": "Initialize WebSocket endpoints", "timing": "20-30s", "validation": "All endpoints ready"},
                {"step": 7, "actor": "Redis Coordination", "action": "Establish coordination", "timing": "30-40s", "validation": "Coordination active"},
                {"step": 8, "actor": "Health Monitor", "action": "Final validation", "timing": "40-45s", "validation": "All systems healthy"}
            ],
            timing_estimates={
                "process_startup": "1-5 seconds",
                "reflective_module_init": "5-10 seconds",
                "websocket_setup": "10-15 seconds",
                "coordination_setup": "10-15 seconds",
                "health_validation": "5-10 seconds",
                "total_duration": "45-60 seconds"
            },
            validation_checkpoints=[
                {"checkpoint": "process_running", "description": "Observatory process started", "timing": "5s"},
                {"checkpoint": "reflective_module_ready", "description": "ReflectiveModule initialized", "timing": "10s"},
                {"checkpoint": "health_endpoints_active", "description": "Health endpoints responding", "timing": "15s"},
                {"checkpoint": "metrics_collecting", "description": "Metrics collection active", "timing": "20s"},
                {"checkpoint": "websockets_ready", "description": "All WebSocket endpoints active", "timing": "30s"},
                {"checkpoint": "coordination_active", "description": "Redis coordination established", "timing": "40s"},
                {"checkpoint": "fully_operational", "description": "All systems healthy and ready", "timing": "45s"}
            ],
            error_scenarios=[
                {"error": "process_startup_failed", "description": "Observatory process failed to start", "recovery": "Check port availability and permissions"},
                {"error": "reflective_module_init_failed", "description": "ReflectiveModule initialization failed", "recovery": "Check dependencies and configuration"},
                {"error": "websocket_setup_failed", "description": "WebSocket endpoints failed to initialize", "recovery": "Check port conflicts and configuration"},
                {"error": "redis_connection_failed", "description": "Redis coordination failed", "recovery": "Check Redis availability and failover"},
                {"error": "health_check_failed", "description": "Health validation failed", "recovery": "Check component status and dependencies"}
            ],
            plantuml_content=plantuml_content,
            metadata={
                "server_type": "Observatory",
                "port": 8888,
                "websocket_endpoints": ["/ws/observatory", "/ws/emoji-rain", "/ws/anomalies", "/ws/doctor-status"],
                "health_endpoints": ["/health", "/ready", "/metrics"],
                "estimated_duration": "45-60 seconds"
            }
        )
    
    def _generate_dashboard_stop_sequence(self) -> OperationalSequence:
        """Generate dashboard-stop sequence with graceful shutdown."""
        
        plantuml_content = """
@startuml dashboard_stop_sequence
!theme plain
title Dashboard Stop Sequence with Graceful Shutdown
note top : Graceful Observatory shutdown with cleanup\\nEstimated Duration: 20-30 seconds

participant "Makefile" as Make
participant "Dashboard Script" as Script
participant "Observatory Server" as Observatory
participant "WebSocket Handler" as WS
participant "Active Connections" as Connections
participant "Metrics Collector" as Metrics
participant "Health Monitor" as Health
participant "Redis Coordination" as Redis

== Shutdown Initiation ==
Make -> Script : make dashboard-stop
note right : Graceful shutdown command
Script -> Observatory : Send SIGTERM
note right : Graceful shutdown signal\\nAllow cleanup time

== Connection Cleanup ==
Observatory -> WS : Signal shutdown
note right : Stop accepting new connections\\nClose existing gracefully
WS -> Connections : Send close frames
note right : WebSocket close code 1001\\nServer going away
Connections -> WS : Acknowledge close
note right : Client connections closed\\nCleanup complete

== Service Deregistration ==
Observatory -> Health : Deregister health endpoints
note right : /health returns 503\\n/ready returns false
Health -> Observatory : Endpoints deregistered
note right : No longer accepting health checks

Observatory -> Metrics : Stop metrics collection
note right : Flush pending metrics\\nClose Prometheus endpoint
Metrics -> Observatory : Collection stopped
note right : Final metrics sent\\nCollectors cleaned

== Coordination Cleanup ==
Observatory -> Redis : Disconnect coordination
note right : Clean disconnect\\nRelease coordination locks
Redis -> Observatory : Disconnection complete
note right : Coordination cleaned\\nResources released

== Process Termination ==
Observatory -> Observatory : Final cleanup
note right : Close file handles\\nRelease resources
Observatory -> Script : Process terminated
note right : Exit code: 0\\nCleanup complete
Script -> Make : Dashboard stop complete
note right : All resources cleaned\\nDuration: ~20-30s

@enduml
"""
        
        return OperationalSequence(
            sequence_id="dashboard_stop",
            title="Dashboard Stop Sequence with Graceful Shutdown",
            description="Graceful Observatory server shutdown with connection cleanup and resource deregistration",
            participants=["Makefile", "Dashboard Script", "Observatory Server", "WebSocket Handler", "Active Connections", "Metrics Collector", "Health Monitor", "Redis Coordination"],
            steps=[
                {"step": 1, "actor": "Makefile", "action": "Execute dashboard-stop", "timing": "0s"},
                {"step": 2, "actor": "Observatory Server", "action": "Receive shutdown signal", "timing": "1s"},
                {"step": 3, "actor": "WebSocket Handler", "action": "Close WebSocket connections", "timing": "1-10s"},
                {"step": 4, "actor": "Health Monitor", "action": "Deregister health endpoints", "timing": "10-15s"},
                {"step": 5, "actor": "Metrics Collector", "action": "Stop metrics collection", "timing": "15-20s"},
                {"step": 6, "actor": "Redis Coordination", "action": "Disconnect coordination", "timing": "20-25s"},
                {"step": 7, "actor": "Observatory Server", "action": "Final cleanup and termination", "timing": "25-30s"}
            ],
            timing_estimates={"total_duration": "20-30 seconds", "connection_cleanup": "10 seconds", "service_cleanup": "10 seconds"},
            validation_checkpoints=[
                {"checkpoint": "connections_closed", "description": "All WebSocket connections closed", "timing": "10s"},
                {"checkpoint": "health_deregistered", "description": "Health endpoints deregistered", "timing": "15s"},
                {"checkpoint": "metrics_stopped", "description": "Metrics collection stopped", "timing": "20s"},
                {"checkpoint": "coordination_disconnected", "description": "Redis coordination cleaned", "timing": "25s"},
                {"checkpoint": "process_terminated", "description": "Process terminated cleanly", "timing": "30s"}
            ],
            error_scenarios=[
                {"error": "connections_timeout", "description": "WebSocket connections not closing", "recovery": "Force close after timeout"},
                {"error": "metrics_flush_failed", "description": "Failed to flush final metrics", "recovery": "Continue shutdown, log error"},
                {"error": "redis_disconnect_failed", "description": "Redis disconnect failed", "recovery": "Force disconnect, continue shutdown"}
            ],
            plantuml_content=plantuml_content,
            metadata={"shutdown_type": "graceful", "estimated_duration": "20-30 seconds"}
        )
    
    def _generate_dashboard_restart_sequence(self) -> OperationalSequence:
        """Generate dashboard-restart sequence combining stop and start."""
        
        plantuml_content = """
@startuml dashboard_restart_sequence
!theme plain
title Dashboard Restart Sequence (Stop + Start)
note top : Combined stop and start with validation\\nEstimated Duration: 65-90 seconds

participant "Makefile" as Make
participant "Dashboard Script" as Script
participant "Stop Process" as Stop
participant "Validation" as Validate
participant "Start Process" as Start

== Restart Initiation ==
Make -> Script : make dashboard-restart
note right : Combined stop/start operation
Script -> Stop : Execute dashboard stop
note right : Graceful shutdown first\\nSee dashboard-stop sequence

== Stop Phase ==
Stop -> Stop : Graceful shutdown
note right : 20-30 seconds\\nClean resource cleanup
Stop -> Script : Stop complete
note right : Process terminated\\nResources released

== Validation Phase ==
Script -> Validate : Verify clean state
note right : Check port 8888 available\\nValidate no conflicts
Validate -> Script : State validated
note right : Safe to restart\\nNo resource conflicts

== Start Phase ==
Script -> Start : Execute dashboard start
note right : Fresh startup\\nSee dashboard-up sequence
Start -> Start : Complete initialization
note right : 45-60 seconds\\nFull ReflectiveModule init
Start -> Script : Start complete
note right : All systems operational\\nWebSocket endpoints active

== Final Validation ==
Script -> Validate : Verify restart success
note right : End-to-end health check\\nAll endpoints responding
Validate -> Script : Restart validated
note right : Full functionality confirmed
Script -> Make : Restart complete
note right : Total: 65-90 seconds

@enduml
"""
        
        return OperationalSequence(
            sequence_id="dashboard_restart",
            title="Dashboard Restart Sequence (Stop + Start)",
            description="Complete Observatory server restart with validation checkpoints",
            participants=["Makefile", "Dashboard Script", "Stop Process", "Validation", "Start Process"],
            steps=[
                {"step": 1, "actor": "Makefile", "action": "Execute dashboard restart", "timing": "0s"},
                {"step": 2, "actor": "Stop Process", "action": "Graceful dashboard stop", "timing": "0-30s"},
                {"step": 3, "actor": "Validation", "action": "Verify clean state", "timing": "30-35s"},
                {"step": 4, "actor": "Start Process", "action": "Fresh dashboard start", "timing": "35-95s"},
                {"step": 5, "actor": "Validation", "action": "Verify restart success", "timing": "95-100s"}
            ],
            timing_estimates={"total_duration": "65-90 seconds", "stop_phase": "20-30 seconds", "start_phase": "45-60 seconds"},
            validation_checkpoints=[
                {"checkpoint": "stop_complete", "description": "Dashboard stopped cleanly", "timing": "30s"},
                {"checkpoint": "state_validated", "description": "Clean state verified", "timing": "35s"},
                {"checkpoint": "start_complete", "description": "Dashboard started successfully", "timing": "95s"},
                {"checkpoint": "restart_validated", "description": "Full functionality confirmed", "timing": "100s"}
            ],
            error_scenarios=[
                {"error": "stop_failed", "description": "Graceful stop failed", "recovery": "Force kill and cleanup"},
                {"error": "port_conflict", "description": "Port 8888 still in use", "recovery": "Wait and retry or force cleanup"},
                {"error": "start_failed", "description": "Restart failed", "recovery": "Check logs and configuration"}
            ],
            plantuml_content=plantuml_content,
            metadata={"operation_type": "restart", "estimated_duration": "65-90 seconds"}
        ) 
   
    def _generate_dashboard_status_sequence(self) -> OperationalSequence:
        """Generate dashboard-status comprehensive health check flow."""
        
        plantuml_content = """
@startuml dashboard_status_sequence
!theme plain
title Dashboard Status Comprehensive Health Check Flow
note top : Complete health validation with timeout values\\nEstimated Duration: 10-15 seconds

participant "Makefile" as Make
participant "Status Script" as Script
participant "Observatory Server" as Observatory
participant "Health Endpoints" as Health
participant "WebSocket Handler" as WS
participant "Metrics Collector" as Metrics
participant "Redis Coordination" as Redis
participant "External Services" as External

== Status Check Initiation ==
Make -> Script : make dashboard-status
note right : Comprehensive health check
Script -> Observatory : Check process status
note right : Verify process running\\nCheck PID and port

== Health Endpoint Validation ==
Script -> Health : GET /health
note right : Timeout: 5 seconds\\nExpected: 200 OK
Health -> Observatory : Query component health
note right : Check all subsystems\\nValidate dependencies
Observatory -> Health : Health response
note right : Status: healthy/degraded/down\\nComponent details
Health -> Script : Health status
note right : JSON response with details

Script -> Health : GET /ready
note right : Timeout: 5 seconds\\nReadiness check
Health -> Script : Readiness status
note right : Ready: true/false\\nDependency status

Script -> Health : GET /metrics
note right : Timeout: 5 seconds\\nPrometheus metrics
Health -> Script : Metrics data
note right : Performance counters\\nSystem metrics

== WebSocket Endpoint Validation ==
Script -> WS : Check /ws/observatory
note right : WebSocket connectivity test\\nTimeout: 3 seconds
WS -> Script : Connection status
note right : Active/Inactive\\nConnection count

Script -> WS : Check /ws/emoji-rain
note right : Endpoint availability\\nTimeout: 3 seconds
WS -> Script : Endpoint status

Script -> WS : Check /ws/anomalies
note right : Alert endpoint status\\nTimeout: 3 seconds
WS -> Script : Status response

Script -> WS : Check /ws/doctor-status
note right : Health monitoring endpoint\\nTimeout: 3 seconds
WS -> Script : Health endpoint status

== Coordination Validation ==
Script -> Redis : Check coordination
note right : Primary: 192.168.1.119:6379\\nTimeout: 3 seconds
Redis -> Script : Connection status
note right : Connected/Disconnected\\nFailover status

== External Dependencies ==
Script -> External : Check tunnel connectivity
note right : Cloudflare tunnel status\\nTimeout: 5 seconds
External -> Script : Tunnel status
note right : Active/Inactive\\nLatency info

== Status Compilation ==
Script -> Script : Compile status report
note right : Aggregate all checks\\nDetermine overall status
Script -> Make : Status report
note right : Overall: healthy/degraded/down\\nComponent breakdown\\nDuration: ~10-15s

@enduml
"""
        
        return OperationalSequence(
            sequence_id="dashboard_status",
            title="Dashboard Status Comprehensive Health Check Flow",
            description="Complete health validation with specific success/failure criteria and timeout values",
            participants=["Makefile", "Status Script", "Observatory Server", "Health Endpoints", "WebSocket Handler", "Metrics Collector", "Redis Coordination", "External Services"],
            steps=[
                {"step": 1, "actor": "Makefile", "action": "Execute dashboard-status", "timing": "0s", "validation": "Command executed"},
                {"step": 2, "actor": "Status Script", "action": "Check process status", "timing": "0-1s", "validation": "Process running on port 8888"},
                {"step": 3, "actor": "Health Endpoints", "action": "Validate /health endpoint", "timing": "1-6s", "validation": "200 OK response within 5s"},
                {"step": 4, "actor": "Health Endpoints", "action": "Validate /ready endpoint", "timing": "6-11s", "validation": "Ready: true within 5s"},
                {"step": 5, "actor": "Health Endpoints", "action": "Validate /metrics endpoint", "timing": "11-16s", "validation": "Metrics data within 5s"},
                {"step": 6, "actor": "WebSocket Handler", "action": "Check all WebSocket endpoints", "timing": "16-28s", "validation": "All endpoints responsive within 3s each"},
                {"step": 7, "actor": "Redis Coordination", "action": "Check coordination status", "timing": "28-31s", "validation": "Connection active within 3s"},
                {"step": 8, "actor": "External Services", "action": "Check external dependencies", "timing": "31-36s", "validation": "Tunnel active within 5s"},
                {"step": 9, "actor": "Status Script", "action": "Compile and report status", "timing": "36-40s", "validation": "Complete status report generated"}
            ],
            timing_estimates={
                "process_check": "1 second",
                "health_endpoints": "15 seconds (3 endpoints × 5s timeout)",
                "websocket_endpoints": "12 seconds (4 endpoints × 3s timeout)",
                "coordination_check": "3 seconds",
                "external_checks": "5 seconds",
                "total_duration": "10-15 seconds"
            },
            validation_checkpoints=[
                {"checkpoint": "process_running", "description": "Observatory process active on port 8888", "timing": "1s", "timeout": "1s"},
                {"checkpoint": "health_responding", "description": "/health returns 200 OK", "timing": "6s", "timeout": "5s"},
                {"checkpoint": "ready_confirmed", "description": "/ready returns ready: true", "timing": "11s", "timeout": "5s"},
                {"checkpoint": "metrics_available", "description": "/metrics returns Prometheus data", "timing": "16s", "timeout": "5s"},
                {"checkpoint": "websockets_active", "description": "All 4 WebSocket endpoints responsive", "timing": "28s", "timeout": "3s each"},
                {"checkpoint": "coordination_active", "description": "Redis coordination connected", "timing": "31s", "timeout": "3s"},
                {"checkpoint": "tunnel_active", "description": "Cloudflare tunnel operational", "timing": "36s", "timeout": "5s"}
            ],
            error_scenarios=[
                {"error": "process_not_running", "description": "Observatory process not found", "recovery": "Start dashboard with make dashboard-up"},
                {"error": "health_timeout", "description": "Health endpoint timeout (>5s)", "recovery": "Check server load and restart if needed"},
                {"error": "websocket_unavailable", "description": "WebSocket endpoint not responding", "recovery": "Check WebSocket handler status"},
                {"error": "redis_disconnected", "description": "Redis coordination failed", "recovery": "Check Redis status and failover"},
                {"error": "tunnel_down", "description": "Cloudflare tunnel not responding", "recovery": "Check tunnel status and restart if needed"}
            ],
            plantuml_content=plantuml_content,
            metadata={
                "check_type": "comprehensive",
                "timeout_values": {
                    "health_endpoints": "5 seconds",
                    "websocket_endpoints": "3 seconds",
                    "redis_coordination": "3 seconds",
                    "external_services": "5 seconds"
                },
                "success_criteria": {
                    "overall_healthy": "All checks pass within timeout",
                    "degraded": "Some checks fail but core functionality works",
                    "down": "Critical checks fail or timeout"
                },
                "estimated_duration": "10-15 seconds"
            }
        )
    
    def save_all_sequences(self) -> List[str]:
        """Save all generated sequences to files."""
        self._logger.info("Saving all generated sequence diagrams...")
        
        saved_files = []
        
        for sequence in self._operational_sequences.values():
            files = self._save_sequence_diagram(sequence)
            saved_files.extend(files)
        
        self._logger.info(f"Saved {len(saved_files)} sequence diagram files")
        return saved_files
    
    def _save_sequence_diagram(self, sequence: OperationalSequence) -> List[str]:
        """Save sequence diagram to files."""
        files = []
        
        # Save PlantUML source
        plantuml_file = self._config.output_directory / f"{sequence.sequence_id}.puml"
        with open(plantuml_file, 'w', encoding='utf-8') as f:
            f.write(sequence.plantuml_content)
        files.append(str(plantuml_file))
        
        # Save metadata
        metadata_file = self._config.output_directory / f"{sequence.sequence_id}_metadata.json"
        with open(metadata_file, 'w', encoding='utf-8') as f:
            json.dump({
                "sequence_id": sequence.sequence_id,
                "title": sequence.title,
                "description": sequence.description,
                "participants": sequence.participants,
                "steps": sequence.steps,
                "timing_estimates": sequence.timing_estimates,
                "validation_checkpoints": sequence.validation_checkpoints,
                "error_scenarios": sequence.error_scenarios,
                "metadata": sequence.metadata,
                "generated_at": datetime.now().isoformat()
            }, f, indent=2)
        files.append(str(metadata_file))
        
        return files
    
    def get_all_sequences(self) -> Dict[str, OperationalSequence]:
        """Get all generated sequences."""
        return self._operational_sequences.copy()
    
    def graceful_degradation(self, error: Exception) -> GracefulDegradationResult:
        """Handle graceful degradation on errors."""
        self._logger.warning(f"Graceful degradation triggered: {error}")
        
        return GracefulDegradationResult(
            success=True,
            message=f"SequenceDiagramGenerator degraded due to: {str(error)}",
            fallback_data={
                "operational_sequences": len(self._operational_sequences),
                "available_sequences": list(self._operational_sequences.keys())
            }
        )