"""
UML Diagram Generation Engine for System Architecture Wiring Diagram.

This module implements comprehensive diagram generation using PlantUML and Mermaid
to create component diagrams, sequence diagrams, network topology maps, and data flow diagrams.
"""

import asyncio
import json
import logging
import subprocess
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any, Set
from enum import Enum

from ..core import ReflectiveModule
from .infrastructure_discovery import InfrastructureDiscoverer, NetworkTopology, ServiceInfo
from .makefile_analyzer import MakefileAnalyzer, MakefileAnalysis, MakefileTarget
from .cloudflare_tunnel_discovery import CloudflareTunnelDiscoverer, CloudflareTunnel, TunnelDiscoveryResult
from .network_topology_discovery import NetworkTopologyDiscoverer, NetworkTopology as NetTopology

logger = logging.getLogger(__name__)


class DiagramType(Enum):
    """Types of diagrams that can be generated."""
    COMPONENT = "component"
    SEQUENCE = "sequence"
    NETWORK_TOPOLOGY = "network_topology"
    DATA_FLOW = "data_flow"
    USE_CASE = "use_case"
    DEPLOYMENT = "deployment"


class DiagramFormat(Enum):
    """Output formats for diagrams."""
    PLANTUML = "plantuml"
    MERMAID = "mermaid"
    SVG = "svg"
    PNG = "png"
    PDF = "pdf"


@dataclass
class DiagramMetadata:
    """Metadata for generated diagrams."""
    diagram_id: str
    diagram_type: DiagramType
    title: str
    description: str
    created_at: datetime = field(default_factory=datetime.now)
    last_updated: datetime = field(default_factory=datetime.now)
    version: str = "1.0.0"
    
    # Source data information
    source_components: List[str] = field(default_factory=list)
    source_services: List[str] = field(default_factory=list)
    source_tunnels: List[str] = field(default_factory=list)
    
    # Validation information
    is_valid: bool = True
    validation_errors: List[str] = field(default_factory=list)
    accuracy_score: float = 1.0  # 0.0-1.0


@dataclass
class GeneratedDiagram:
    """Generated diagram with metadata."""
    metadata: DiagramMetadata
    plantuml_source: str
    mermaid_source: str
    svg_output: Optional[str] = None
    png_output: Optional[str] = None
    pdf_output: Optional[str] = None
    
    # File paths
    plantuml_file: Optional[str] = None
    mermaid_file: Optional[str] = None
    svg_file: Optional[str] = None
    png_file: Optional[str] = None
    pdf_file: Optional[str] = None


@dataclass
class DiagramGenerationResult:
    """Result of diagram generation process."""
    diagrams: List[GeneratedDiagram] = field(default_factory=list)
    generation_timestamp: datetime = field(default_factory=datetime.now)
    total_diagrams: int = 0
    successful_generations: int = 0
    failed_generations: int = 0
    
    # Generation statistics
    plantuml_diagrams: int = 0
    mermaid_diagrams: int = 0
    svg_outputs: int = 0
    png_outputs: int = 0
    
    # Validation results
    validation_success_rate: float = 0.0
    accuracy_scores: List[float] = field(default_factory=list)


class DiagramGenerator(ReflectiveModule):
    """Comprehensive diagram generation system."""
    
    def __init__(self):
        super().__init__()
        self.module_id = "diagram_generator"
        self._generation_result: Optional[DiagramGenerationResult] = None
        self._output_directory = Path("generated_diagrams")
        
        # Ensure output directory exists
        self._output_directory.mkdir(exist_ok=True)
        
        # Diagram templates
        self._component_template = self._load_component_template()
        self._sequence_template = self._load_sequence_template()
        self._network_template = self._load_network_template()
        
        logger.info("Diagram Generator initialized")
    
    def _load_component_template(self) -> str:
        """Load PlantUML component diagram template."""
        return """
@startuml {title}
!theme plain
title {title}

package "Infrastructure Layer" {{
    component [Cloudflare Tunnel\\n{d1e53e43-033f-4994-8f46-c83962ae3785}] as Tunnel
    component [DNS Routing\\nobservatory.nkllon.com] as DNS
    component [Local Network\\n192.168.1.x] as Network
}}

package "Observability Stack" {{
    component [Observatory Server\\nlocalhost:8888] as Observatory
    component [Prometheus\\nlocalhost:9090] as Prometheus
    component [Grafana\\nlocalhost:3000] as Grafana
    component [ReflectiveModule Pattern] as ReflectiveModule
}}

package "Automation Layer" {{
    component [Makefile\\n50+ targets] as Makefile
    component [Python Scripts] as Scripts
    component [Deployment Workflows] as Deployment
}}

package "Integration Points" {{
    component [ACE Reporter] as ACE
    component [AI Memory Palace] as Memory
    component [DAG Registry] as DAG
    component [Directus CMS] as CMS
}}

package "WebSocket Endpoints" {{
    component [/ws/observatory] as WS1
    component [/ws/anomalies] as WS2
    component [/ws/emoji-rain] as WS3
    component [/ws/doctor-status] as WS4
}}

package "Redis Coordination" {{
    component [Primary\\n192.168.1.119:6379] as RedisPrimary
    component [Fallback\\nlocalhost:6380] as RedisFallback
}}

' Connections
Tunnel --> DNS
DNS --> Network
Network --> Observatory
Network --> Prometheus
Network --> Grafana

Observatory --> WS1
Observatory --> WS2
Observatory --> WS3
Observatory --> WS4

Observatory --> ReflectiveModule
Prometheus --> ReflectiveModule
Grafana --> ReflectiveModule

Makefile --> Observatory
Makefile --> Prometheus
Makefile --> Grafana
Scripts --> Observatory
Scripts --> Prometheus
Scripts --> Grafana

Observatory --> ACE
Observatory --> Memory
Observatory --> DAG
Observatory --> CMS

RedisPrimary --> Observatory
RedisFallback --> Observatory
RedisPrimary --> RedisFallback : failover

@enduml
"""
    
    def _load_sequence_template(self) -> str:
        """Load PlantUML sequence diagram template."""
        return """
@startuml {title}
!theme plain
title {title}

actor User
participant "Makefile" as Makefile
participant "Python Script" as Script
participant "Observatory Server" as Observatory
participant "WebSocket Endpoints" as WebSocket
participant "Prometheus" as Prometheus
participant "Grafana" as Grafana
participant "Redis Coordination" as Redis
participant "Cloudflare Tunnel" as Tunnel

{sequence_steps}

@enduml
"""
    
    def _load_network_template(self) -> str:
        """Load Mermaid network topology template."""
        return """
graph TB
    subgraph "Internet"
        Internet[Internet]
    end
    
    subgraph "Cloudflare Edge"
        Edge[Cloudflare Edge<br/>observatory.nkllon.com]
    end
    
    subgraph "Cloudflare Tunnel"
        Tunnel[Cloudflare Tunnel<br/>d1e53e43-033f-4994-8f46-c83962ae3785]
    end
    
    subgraph "Local Network (192.168.1.x)"
        subgraph "Observatory Services"
            Observatory[Observatory Server<br/>localhost:8888]
            Prometheus[Prometheus<br/>localhost:9090]
            Grafana[Grafana<br/>localhost:3000]
        end
        
        subgraph "WebSocket Endpoints"
            WS1[/ws/observatory]
            WS2[/ws/anomalies]
            WS3[/ws/emoji-rain]
            WS4[/ws/doctor-status]
        end
        
        subgraph "Redis Coordination"
            RedisPrimary[Redis Primary<br/>192.168.1.119:6379]
            RedisFallback[Redis Fallback<br/>localhost:6380]
        end
    end
    
    Internet --> Edge
    Edge --> Tunnel
    Tunnel --> Observatory
    Tunnel --> Prometheus
    Tunnel --> Grafana
    
    Observatory --> WS1
    Observatory --> WS2
    Observatory --> WS3
    Observatory --> WS4
    
    Observatory --> RedisPrimary
    RedisPrimary --> RedisFallback
    
    Observatory --> Prometheus
    Prometheus --> Grafana
"""
    
    async def generate_all_diagrams(self, 
                                   infrastructure_discoverer: Optional[InfrastructureDiscoverer] = None,
                                   makefile_analyzer: Optional[MakefileAnalyzer] = None,
                                   tunnel_discoverer: Optional[CloudflareTunnelDiscoverer] = None,
                                   network_discoverer: Optional[NetworkTopologyDiscoverer] = None) -> DiagramGenerationResult:
        """Generate all types of diagrams."""
        try:
            logger.info("Starting comprehensive diagram generation...")
            
            self._generation_result = DiagramGenerationResult()
            
            # Generate component diagram
            await self._generate_component_diagram(infrastructure_discoverer)
            
            # Generate sequence diagrams
            await self._generate_sequence_diagrams(makefile_analyzer)
            
            # Generate network topology diagram
            await self._generate_network_topology_diagram(network_discoverer)
            
            # Generate data flow diagram
            await self._generate_data_flow_diagram(infrastructure_discoverer, tunnel_discoverer)
            
            # Generate deployment diagram
            await self._generate_deployment_diagram(makefile_analyzer, tunnel_discoverer)
            
            # Update generation metadata
            self._update_generation_metadata()
            
            logger.info(f"Diagram generation completed: {self._generation_result.total_diagrams} diagrams generated")
            
            return self._generation_result
            
        except Exception as e:
            logger.error(f"Diagram generation failed: {e}")
            raise
    
    async def _generate_component_diagram(self, infrastructure_discoverer: Optional[InfrastructureDiscoverer] = None) -> None:
        """Generate component diagram."""
        try:
            diagram_id = "system_architecture_component"
            title = "Beast Mode Framework System Architecture"
            
            # Create PlantUML source
            plantuml_source = self._component_template.format(
                title=title,
                d1e53e43_033f_4994_8f46_c83962ae3785="d1e53e43-033f-4994-8f46-c83962ae3785"
            )
            
            # Create Mermaid source (simplified)
            mermaid_source = """
graph TB
    subgraph "Infrastructure Layer"
        Tunnel[Cloudflare Tunnel]
        DNS[DNS Routing]
        Network[Local Network]
    end
    
    subgraph "Observability Stack"
        Observatory[Observatory Server]
        Prometheus[Prometheus]
        Grafana[Grafana]
        ReflectiveModule[ReflectiveModule Pattern]
    end
    
    subgraph "Automation Layer"
        Makefile[Makefile 50+ targets]
        Scripts[Python Scripts]
        Deployment[Deployment Workflows]
    end
    
    subgraph "Integration Points"
        ACE[ACE Reporter]
        Memory[AI Memory Palace]
        DAG[DAG Registry]
        CMS[Directus CMS]
    end
    
    Tunnel --> DNS
    DNS --> Network
    Network --> Observatory
    Observatory --> Prometheus
    Prometheus --> Grafana
    Observatory --> ReflectiveModule
    Makefile --> Observatory
    Observatory --> ACE
    Observatory --> Memory
    Observatory --> DAG
"""
            
            # Generate diagram
            diagram = await self._create_diagram(
                diagram_id=diagram_id,
                diagram_type=DiagramType.COMPONENT,
                title=title,
                description="Complete system architecture showing all components and their relationships",
                plantuml_source=plantuml_source,
                mermaid_source=mermaid_source
            )
            
            self._generation_result.diagrams.append(diagram)
            
        except Exception as e:
            logger.error(f"Error generating component diagram: {e}")
    
    async def _generate_sequence_diagrams(self, makefile_analyzer: Optional[MakefileAnalyzer] = None) -> None:
        """Generate sequence diagrams for operational workflows."""
        try:
            # Generate tunnel-start sequence diagram
            await self._generate_tunnel_start_sequence()
            
            # Generate dashboard-up sequence diagram
            await self._generate_dashboard_up_sequence()
            
            # Generate dashboard-status sequence diagram
            await self._generate_dashboard_status_sequence()
            
            # Generate emergency protocol sequence diagram
            await self._generate_emergency_protocol_sequence()
            
        except Exception as e:
            logger.error(f"Error generating sequence diagrams: {e}")
    
    async def _generate_tunnel_start_sequence(self) -> None:
        """Generate tunnel-start sequence diagram."""
        sequence_steps = """
User -> Makefile: make tunnel-start
Makefile -> Script: Execute tunnel management script
Script -> Tunnel: Start Cloudflare tunnel
Tunnel -> DNS: Register DNS records
DNS -> Edge: Propagate DNS changes
Edge -> Tunnel: Establish tunnel connection
Tunnel -> Observatory: Verify Observatory connectivity
Observatory -> WebSocket: Register WebSocket endpoints
WebSocket -> Observatory: Confirm endpoint registration
Observatory -> Redis: Update coordination status
Redis -> Observatory: Confirm status update
Observatory -> Script: Report success
Script -> Makefile: Return success status
Makefile -> User: Tunnel started successfully
"""
        
        plantuml_source = self._sequence_template.format(
            title="Tunnel Start Operation Sequence",
            sequence_steps=sequence_steps
        )
        
        mermaid_source = """
sequenceDiagram
    participant User
    participant Makefile
    participant Script
    participant Tunnel
    participant DNS
    participant Edge
    participant Observatory
    participant WebSocket
    participant Redis
    
    User->>Makefile: make tunnel-start
    Makefile->>Script: Execute tunnel management script
    Script->>Tunnel: Start Cloudflare tunnel
    Tunnel->>DNS: Register DNS records
    DNS->>Edge: Propagate DNS changes
    Edge->>Tunnel: Establish tunnel connection
    Tunnel->>Observatory: Verify Observatory connectivity
    Observatory->>WebSocket: Register WebSocket endpoints
    WebSocket->>Observatory: Confirm endpoint registration
    Observatory->>Redis: Update coordination status
    Redis->>Observatory: Confirm status update
    Observatory->>Script: Report success
    Script->>Makefile: Return success status
    Makefile->>User: Tunnel started successfully
"""
        
        diagram = await self._create_diagram(
            diagram_id="tunnel_start_sequence",
            diagram_type=DiagramType.SEQUENCE,
            title="Tunnel Start Operation Sequence",
            description="Complete sequence for starting Cloudflare tunnel with DNS propagation and service verification",
            plantuml_source=plantuml_source,
            mermaid_source=mermaid_source
        )
        
        self._generation_result.diagrams.append(diagram)
    
    async def _generate_dashboard_up_sequence(self) -> None:
        """Generate dashboard-up sequence diagram."""
        sequence_steps = """
User -> Makefile: make dashboard-up
Makefile -> Script: Execute observatory-daemon.py
Script -> Observatory: Start Observatory server
Observatory -> ReflectiveModule: Initialize ReflectiveModule
ReflectiveModule -> Observatory: Register health endpoints
Observatory -> Prometheus: Register scrape targets
Prometheus -> Observatory: Confirm target registration
Observatory -> Grafana: Configure datasource
Grafana -> Prometheus: Test datasource connection
Prometheus -> Grafana: Confirm connection
Observatory -> WebSocket: Establish WebSocket endpoints
WebSocket -> Observatory: Confirm endpoint establishment
Observatory -> Redis: Update coordination status
Redis -> Observatory: Confirm status update
Observatory -> Script: Report success
Script -> Makefile: Return success status
Makefile -> User: Dashboard started successfully
"""
        
        plantuml_source = self._sequence_template.format(
            title="Dashboard Up Operation Sequence",
            sequence_steps=sequence_steps
        )
        
        mermaid_source = """
sequenceDiagram
    participant User
    participant Makefile
    participant Script
    participant Observatory
    participant ReflectiveModule
    participant Prometheus
    participant Grafana
    participant WebSocket
    participant Redis
    
    User->>Makefile: make dashboard-up
    Makefile->>Script: Execute observatory-daemon.py
    Script->>Observatory: Start Observatory server
    Observatory->>ReflectiveModule: Initialize ReflectiveModule
    ReflectiveModule->>Observatory: Register health endpoints
    Observatory->>Prometheus: Register scrape targets
    Prometheus->>Observatory: Confirm target registration
    Observatory->>Grafana: Configure datasource
    Grafana->>Prometheus: Test datasource connection
    Prometheus->>Grafana: Confirm connection
    Observatory->>WebSocket: Establish WebSocket endpoints
    WebSocket->>Observatory: Confirm endpoint establishment
    Observatory->>Redis: Update coordination status
    Redis->>Observatory: Confirm status update
    Observatory->>Script: Report success
    Script->>Makefile: Return success status
    Makefile->>User: Dashboard started successfully
"""
        
        diagram = await self._create_diagram(
            diagram_id="dashboard_up_sequence",
            diagram_type=DiagramType.SEQUENCE,
            title="Dashboard Up Operation Sequence",
            description="Complete sequence for starting Observatory dashboard with health checks and WebSocket setup",
            plantuml_source=plantuml_source,
            mermaid_source=mermaid_source
        )
        
        self._generation_result.diagrams.append(diagram)
    
    async def _generate_dashboard_status_sequence(self) -> None:
        """Generate dashboard-status sequence diagram."""
        sequence_steps = """
User -> Makefile: make dashboard-status
Makefile -> Script: Execute health check script
Script -> Observatory: Check Observatory health
Observatory -> ReflectiveModule: Query health endpoints
ReflectiveModule -> Observatory: Return health status
Observatory -> Prometheus: Check target status
Prometheus -> Observatory: Return target status
Observatory -> Grafana: Test datasource connectivity
Grafana -> Observatory: Return connectivity status
Observatory -> WebSocket: Check WebSocket connections
WebSocket -> Observatory: Return connection status
Observatory -> Redis: Check coordination status
Redis -> Observatory: Return coordination status
Observatory -> Script: Compile health report
Script -> Makefile: Return health report
Makefile -> User: Display comprehensive health status
"""
        
        plantuml_source = self._sequence_template.format(
            title="Dashboard Status Health Check Sequence",
            sequence_steps=sequence_steps
        )
        
        mermaid_source = """
sequenceDiagram
    participant User
    participant Makefile
    participant Script
    participant Observatory
    participant ReflectiveModule
    participant Prometheus
    participant Grafana
    participant WebSocket
    participant Redis
    
    User->>Makefile: make dashboard-status
    Makefile->>Script: Execute health check script
    Script->>Observatory: Check Observatory health
    Observatory->>ReflectiveModule: Query health endpoints
    ReflectiveModule->>Observatory: Return health status
    Observatory->>Prometheus: Check target status
    Prometheus->>Observatory: Return target status
    Observatory->>Grafana: Test datasource connectivity
    Grafana->>Observatory: Return connectivity status
    Observatory->>WebSocket: Check WebSocket connections
    WebSocket->>Observatory: Return connection status
    Observatory->>Redis: Check coordination status
    Redis->>Observatory: Return coordination status
    Observatory->>Script: Compile health report
    Script->>Makefile: Return health report
    Makefile->>User: Display comprehensive health status
"""
        
        diagram = await self._create_diagram(
            diagram_id="dashboard_status_sequence",
            diagram_type=DiagramType.SEQUENCE,
            title="Dashboard Status Health Check Sequence",
            description="Comprehensive health check sequence for all Observatory components",
            plantuml_source=plantuml_source,
            mermaid_source=mermaid_source
        )
        
        self._generation_result.diagrams.append(diagram)
    
    async def _generate_emergency_protocol_sequence(self) -> None:
        """Generate emergency protocol sequence diagram."""
        sequence_steps = """
Anomaly -> Observatory: Detect system anomaly
Observatory -> ReflectiveModule: Capture error with correlation ID
ReflectiveModule -> Observatory: Return structured error data
Observatory -> ACE: Broadcast emergency status
ACE -> Observatory: Confirm broadcast
Observatory -> Memory: Store context for analysis
Memory -> Observatory: Confirm storage
Observatory -> DAG: Activate emergency protocols
DAG -> Observatory: Confirm protocol activation
Observatory -> Redis: Initiate failover procedures
Redis -> Observatory: Confirm failover initiation
Observatory -> WebSocket: Broadcast emergency alerts
WebSocket -> Observatory: Confirm alert broadcast
Observatory -> Script: Execute recovery procedures
Script -> Observatory: Report recovery status
Observatory -> User: Display emergency status and recovery progress
"""
        
        plantuml_source = self._sequence_template.format(
            title="Emergency Protocol Activation Sequence",
            sequence_steps=sequence_steps
        )
        
        mermaid_source = """
sequenceDiagram
    participant Anomaly
    participant Observatory
    participant ReflectiveModule
    participant ACE
    participant Memory
    participant DAG
    participant Redis
    participant WebSocket
    participant Script
    participant User
    
    Anomaly->>Observatory: Detect system anomaly
    Observatory->>ReflectiveModule: Capture error with correlation ID
    ReflectiveModule->>Observatory: Return structured error data
    Observatory->>ACE: Broadcast emergency status
    ACE->>Observatory: Confirm broadcast
    Observatory->>Memory: Store context for analysis
    Memory->>Observatory: Confirm storage
    Observatory->>DAG: Activate emergency protocols
    DAG->>Observatory: Confirm protocol activation
    Observatory->>Redis: Initiate failover procedures
    Redis->>Observatory: Confirm failover initiation
    Observatory->>WebSocket: Broadcast emergency alerts
    WebSocket->>Observatory: Confirm alert broadcast
    Observatory->>Script: Execute recovery procedures
    Script->>Observatory: Report recovery status
    Observatory->>User: Display emergency status and recovery progress
"""
        
        diagram = await self._create_diagram(
            diagram_id="emergency_protocol_sequence",
            diagram_type=DiagramType.SEQUENCE,
            title="Emergency Protocol Activation Sequence",
            description="Emergency protocol activation with systematic error handling and recovery procedures",
            plantuml_source=plantuml_source,
            mermaid_source=mermaid_source
        )
        
        self._generation_result.diagrams.append(diagram)
    
    async def _generate_network_topology_diagram(self, network_discoverer: Optional[NetworkTopologyDiscoverer] = None) -> None:
        """Generate network topology diagram."""
        try:
            # Use the network template
            mermaid_source = self._network_template
            
            # Create PlantUML version
            plantuml_source = """
@startuml Network Topology
!theme plain
title Network Topology - Beast Mode Framework

package "Internet" {
    [Internet] as Internet
}

package "Cloudflare Edge" {
    [Cloudflare Edge\\nobservatory.nkllon.com] as Edge
}

package "Cloudflare Tunnel" {
    [Cloudflare Tunnel\\nd1e53e43-033f-4994-8f46-c83962ae3785] as Tunnel
}

package "Local Network (192.168.1.x)" {
    package "Observatory Services" {
        [Observatory Server\\nlocalhost:8888] as Observatory
        [Prometheus\\nlocalhost:9090] as Prometheus
        [Grafana\\nlocalhost:3000] as Grafana
    }
    
    package "WebSocket Endpoints" {
        [/ws/observatory] as WS1
        [/ws/anomalies] as WS2
        [/ws/emoji-rain] as WS3
        [/ws/doctor-status] as WS4
    }
    
    package "Redis Coordination" {
        [Redis Primary\\n192.168.1.119:6379] as RedisPrimary
        [Redis Fallback\\nlocalhost:6380] as RedisFallback
    }
}

Internet --> Edge
Edge --> Tunnel
Tunnel --> Observatory
Tunnel --> Prometheus
Tunnel --> Grafana

Observatory --> WS1
Observatory --> WS2
Observatory --> WS3
Observatory --> WS4

Observatory --> RedisPrimary
RedisPrimary --> RedisFallback

Observatory --> Prometheus
Prometheus --> Grafana

@enduml
"""
            
            diagram = await self._create_diagram(
                diagram_id="network_topology",
                diagram_type=DiagramType.NETWORK_TOPOLOGY,
                title="Network Topology - Beast Mode Framework",
                description="Complete network topology showing Internet to local network routing with WebSocket endpoints and Redis coordination",
                plantuml_source=plantuml_source,
                mermaid_source=mermaid_source
            )
            
            self._generation_result.diagrams.append(diagram)
            
        except Exception as e:
            logger.error(f"Error generating network topology diagram: {e}")
    
    async def _generate_data_flow_diagram(self, 
                                        infrastructure_discoverer: Optional[InfrastructureDiscoverer] = None,
                                        tunnel_discoverer: Optional[CloudflareTunnelDiscoverer] = None) -> None:
        """Generate data flow diagram."""
        try:
            mermaid_source = """
graph LR
    subgraph "Data Sources"
        ReflectiveModule[ReflectiveModule Components]
        Observatory[Observatory Server]
        SystemMetrics[System Metrics]
    end
    
    subgraph "Collection Layer"
        MetricsCollector[Metrics Collector]
        WebSocketStream[WebSocket Stream]
        BatchCollector[Batch Collector]
    end
    
    subgraph "Processing Layer"
        Prometheus[Prometheus Server]
        AnomalyDetector[Anomaly Detector]
        CorrelationEngine[Correlation Engine]
    end
    
    subgraph "Visualization Layer"
        Grafana[Grafana Dashboards]
        RealTimeUI[Real-time UI]
        Alerts[Alert System]
    end
    
    subgraph "Integration Points"
        ACE[ACE Reporter]
        Memory[AI Memory Palace]
        DAG[DAG Registry]
    end
    
    ReflectiveModule --> MetricsCollector
    Observatory --> MetricsCollector
    SystemMetrics --> MetricsCollector
    
    MetricsCollector --> Prometheus
    MetricsCollector --> WebSocketStream
    MetricsCollector --> BatchCollector
    
    Prometheus --> Grafana
    WebSocketStream --> RealTimeUI
    BatchCollector --> Prometheus
    
    Prometheus --> AnomalyDetector
    AnomalyDetector --> CorrelationEngine
    CorrelationEngine --> Alerts
    
    Observatory --> ACE
    Observatory --> Memory
    Observatory --> DAG
"""
            
            plantuml_source = """
@startuml Data Flow
!theme plain
title Data Flow - Beast Mode Observability Pipeline

package "Data Sources" {
    [ReflectiveModule Components] as ReflectiveModule
    [Observatory Server] as Observatory
    [System Metrics] as SystemMetrics
}

package "Collection Layer" {
    [Metrics Collector] as MetricsCollector
    [WebSocket Stream] as WebSocketStream
    [Batch Collector] as BatchCollector
}

package "Processing Layer" {
    [Prometheus Server] as Prometheus
    [Anomaly Detector] as AnomalyDetector
    [Correlation Engine] as CorrelationEngine
}

package "Visualization Layer" {
    [Grafana Dashboards] as Grafana
    [Real-time UI] as RealTimeUI
    [Alert System] as Alerts
}

package "Integration Points" {
    [ACE Reporter] as ACE
    [AI Memory Palace] as Memory
    [DAG Registry] as DAG
}

ReflectiveModule --> MetricsCollector
Observatory --> MetricsCollector
SystemMetrics --> MetricsCollector

MetricsCollector --> Prometheus
MetricsCollector --> WebSocketStream
MetricsCollector --> BatchCollector

Prometheus --> Grafana
WebSocketStream --> RealTimeUI
BatchCollector --> Prometheus

Prometheus --> AnomalyDetector
AnomalyDetector --> CorrelationEngine
CorrelationEngine --> Alerts

Observatory --> ACE
Observatory --> Memory
Observatory --> DAG

@enduml
"""
            
            diagram = await self._create_diagram(
                diagram_id="data_flow",
                diagram_type=DiagramType.DATA_FLOW,
                title="Data Flow - Beast Mode Observability Pipeline",
                description="Complete data flow from ReflectiveModule components through Observatory to Prometheus and Grafana with real-time streaming",
                plantuml_source=plantuml_source,
                mermaid_source=mermaid_source
            )
            
            self._generation_result.diagrams.append(diagram)
            
        except Exception as e:
            logger.error(f"Error generating data flow diagram: {e}")
    
    async def _generate_deployment_diagram(self, 
                                         makefile_analyzer: Optional[MakefileAnalyzer] = None,
                                         tunnel_discoverer: Optional[CloudflareTunnelDiscoverer] = None) -> None:
        """Generate deployment diagram."""
        try:
            mermaid_source = """
graph TB
    subgraph "Deployment Orchestration"
        Makefile[Makefile 50+ targets]
        PythonScripts[Python Automation Scripts]
        DockerContainers[Docker Containers]
    end
    
    subgraph "Infrastructure Deployment"
        TunnelDeploy[Tunnel Deployment]
        DNSDeploy[DNS Configuration]
        ServiceDeploy[Service Deployment]
    end
    
    subgraph "Service Deployment"
        ObservatoryDeploy[Observatory Deployment]
        PrometheusDeploy[Prometheus Deployment]
        GrafanaDeploy[Grafana Deployment]
    end
    
    subgraph "Configuration Management"
        ConfigDeploy[Configuration Deployment]
        SecretDeploy[Secrets Management]
        HealthCheckDeploy[Health Check Setup]
    end
    
    subgraph "Validation & Testing"
        HealthValidation[Health Validation]
        ConnectivityTest[Connectivity Testing]
        IntegrationTest[Integration Testing]
    end
    
    Makefile --> TunnelDeploy
    Makefile --> DNSDeploy
    Makefile --> ServiceDeploy
    
    PythonScripts --> ObservatoryDeploy
    PythonScripts --> PrometheusDeploy
    PythonScripts --> GrafanaDeploy
    
    DockerContainers --> ConfigDeploy
    DockerContainers --> SecretDeploy
    
    ServiceDeploy --> HealthCheckDeploy
    HealthCheckDeploy --> HealthValidation
    HealthValidation --> ConnectivityTest
    ConnectivityTest --> IntegrationTest
"""
            
            plantuml_source = """
@startuml Deployment
!theme plain
title Deployment Diagram - Beast Mode Framework

package "Deployment Orchestration" {
    [Makefile 50+ targets] as Makefile
    [Python Automation Scripts] as PythonScripts
    [Docker Containers] as DockerContainers
}

package "Infrastructure Deployment" {
    [Tunnel Deployment] as TunnelDeploy
    [DNS Configuration] as DNSDeploy
    [Service Deployment] as ServiceDeploy
}

package "Service Deployment" {
    [Observatory Deployment] as ObservatoryDeploy
    [Prometheus Deployment] as PrometheusDeploy
    [Grafana Deployment] as GrafanaDeploy
}

package "Configuration Management" {
    [Configuration Deployment] as ConfigDeploy
    [Secrets Management] as SecretDeploy
    [Health Check Setup] as HealthCheckDeploy
}

package "Validation & Testing" {
    [Health Validation] as HealthValidation
    [Connectivity Testing] as ConnectivityTest
    [Integration Testing] as IntegrationTest
}

Makefile --> TunnelDeploy
Makefile --> DNSDeploy
Makefile --> ServiceDeploy

PythonScripts --> ObservatoryDeploy
PythonScripts --> PrometheusDeploy
PythonScripts --> GrafanaDeploy

DockerContainers --> ConfigDeploy
DockerContainers --> SecretDeploy

ServiceDeploy --> HealthCheckDeploy
HealthCheckDeploy --> HealthValidation
HealthValidation --> ConnectivityTest
ConnectivityTest --> IntegrationTest

@enduml
"""
            
            diagram = await self._create_diagram(
                diagram_id="deployment",
                diagram_type=DiagramType.DEPLOYMENT,
                title="Deployment Diagram - Beast Mode Framework",
                description="Complete deployment orchestration from Makefile targets through infrastructure and service deployment to validation",
                plantuml_source=plantuml_source,
                mermaid_source=mermaid_source
            )
            
            self._generation_result.diagrams.append(diagram)
            
        except Exception as e:
            logger.error(f"Error generating deployment diagram: {e}")
    
    async def _create_diagram(self, 
                            diagram_id: str,
                            diagram_type: DiagramType,
                            title: str,
                            description: str,
                            plantuml_source: str,
                            mermaid_source: str) -> GeneratedDiagram:
        """Create a diagram with all formats."""
        try:
            # Create metadata
            metadata = DiagramMetadata(
                diagram_id=diagram_id,
                diagram_type=diagram_type,
                title=title,
                description=description
            )
            
            # Create diagram object
            diagram = GeneratedDiagram(
                metadata=metadata,
                plantuml_source=plantuml_source,
                mermaid_source=mermaid_source
            )
            
            # Save source files
            await self._save_diagram_files(diagram)
            
            # Generate output formats
            await self._generate_output_formats(diagram)
            
            return diagram
            
        except Exception as e:
            logger.error(f"Error creating diagram {diagram_id}: {e}")
            raise
    
    async def _save_diagram_files(self, diagram: GeneratedDiagram) -> None:
        """Save diagram source files."""
        try:
            # Save PlantUML file
            plantuml_file = self._output_directory / f"{diagram.metadata.diagram_id}.puml"
            with open(plantuml_file, 'w') as f:
                f.write(diagram.plantuml_source)
            diagram.plantuml_file = str(plantuml_file)
            
            # Save Mermaid file
            mermaid_file = self._output_directory / f"{diagram.metadata.diagram_id}.mmd"
            with open(mermaid_file, 'w') as f:
                f.write(diagram.mermaid_source)
            diagram.mermaid_file = str(mermaid_file)
            
        except Exception as e:
            logger.error(f"Error saving diagram files: {e}")
    
    async def _generate_output_formats(self, diagram: GeneratedDiagram) -> None:
        """Generate output formats (SVG, PNG, PDF)."""
        try:
            # Generate SVG from PlantUML
            await self._generate_svg(diagram)
            
            # Generate PNG from PlantUML
            await self._generate_png(diagram)
            
        except Exception as e:
            logger.error(f"Error generating output formats: {e}")
    
    async def _generate_svg(self, diagram: GeneratedDiagram) -> None:
        """Generate SVG from PlantUML."""
        try:
            svg_file = self._output_directory / f"{diagram.metadata.diagram_id}.svg"
            
            # Use PlantUML to generate SVG
            result = await asyncio.create_subprocess_exec(
                "plantuml", "-tsvg", "-o", str(self._output_directory), 
                str(diagram.plantuml_file),
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await result.communicate()
            
            if result.returncode == 0 and svg_file.exists():
                diagram.svg_file = str(svg_file)
                with open(svg_file, 'r') as f:
                    diagram.svg_output = f.read()
            else:
                logger.warning(f"SVG generation failed for {diagram.metadata.diagram_id}: {stderr.decode()}")
        
        except Exception as e:
            logger.debug(f"Error generating SVG: {e}")
    
    async def _generate_png(self, diagram: GeneratedDiagram) -> None:
        """Generate PNG from PlantUML."""
        try:
            png_file = self._output_directory / f"{diagram.metadata.diagram_id}.png"
            
            # Use PlantUML to generate PNG
            result = await asyncio.create_subprocess_exec(
                "plantuml", "-tpng", "-o", str(self._output_directory), 
                str(diagram.plantuml_file),
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await result.communicate()
            
            if result.returncode == 0 and png_file.exists():
                diagram.png_file = str(png_file)
            else:
                logger.warning(f"PNG generation failed for {diagram.metadata.diagram_id}: {stderr.decode()}")
        
        except Exception as e:
            logger.debug(f"Error generating PNG: {e}")
    
    def _update_generation_metadata(self) -> None:
        """Update generation result metadata."""
        if not self._generation_result:
            return
        
        self._generation_result.total_diagrams = len(self._generation_result.diagrams)
        self._generation_result.successful_generations = len([
            d for d in self._generation_result.diagrams if d.svg_file or d.png_file
        ])
        self._generation_result.failed_generations = (
            self._generation_result.total_diagrams - self._generation_result.successful_generations
        )
        
        self._generation_result.plantuml_diagrams = len([
            d for d in self._generation_result.diagrams if d.plantuml_file
        ])
        self._generation_result.mermaid_diagrams = len([
            d for d in self._generation_result.diagrams if d.mermaid_file
        ])
        self._generation_result.svg_outputs = len([
            d for d in self._generation_result.diagrams if d.svg_file
        ])
        self._generation_result.png_outputs = len([
            d for d in self._generation_result.diagrams if d.png_file
        ])
        
        # Calculate validation success rate
        accuracy_scores = [d.metadata.accuracy_score for d in self._generation_result.diagrams]
        self._generation_result.accuracy_scores = accuracy_scores
        self._generation_result.validation_success_rate = (
            sum(accuracy_scores) / len(accuracy_scores) if accuracy_scores else 0.0
        )
    
    def get_generation_result(self) -> Optional[DiagramGenerationResult]:
        """Get the current generation result."""
        return self._generation_result
    
    def get_diagram_by_id(self, diagram_id: str) -> Optional[GeneratedDiagram]:
        """Get a specific diagram by ID."""
        if self._generation_result:
            for diagram in self._generation_result.diagrams:
                if diagram.metadata.diagram_id == diagram_id:
                    return diagram
        return None
    
    def get_diagrams_by_type(self, diagram_type: DiagramType) -> List[GeneratedDiagram]:
        """Get all diagrams of a specific type."""
        if not self._generation_result:
            return []
        
        return [diagram for diagram in self._generation_result.diagrams 
                if diagram.metadata.diagram_type == diagram_type]
    
    # ReflectiveModule implementation
    
    def get_capabilities(self) -> List['ModuleCapability']:
        """Get Diagram Generator capabilities."""
        from src.rm_ddd.core.unified_reflective_module import ModuleCapability
        return [
            ModuleCapability.DATA_PROCESSING,
            ModuleCapability.VISUALIZATION,
            ModuleCapability.DOCUMENTATION,
        ]
    
    def get_health_status(self) -> 'ModuleHealth':
        """Get health status of the Diagram Generator."""
        from src.rm_ddd.core.unified_reflective_module import ModuleHealth, ModuleStatus
        
        if self._generation_result and self._generation_result.total_diagrams > 0:
            status = ModuleStatus.HEALTHY
            health_score = min(1.0, self._generation_result.validation_success_rate)
            issues = []
        else:
            status = ModuleStatus.WARNING
            health_score = 0.5
            issues = ["No diagrams generated yet"]
        
        uptime = (datetime.now() - self._start_time).total_seconds()
        
        return ModuleHealth(
            module_id=self.module_id,
            status=status,
            health_score=health_score,
            issues=issues,
            last_check=datetime.now(),
            uptime_seconds=uptime,
            error_count=self._error_count,
            warning_count=self._warning_count
        )
    
    async def get_metrics(self) -> Dict[str, any]:
        """Get Diagram Generator performance metrics."""
        if not self._generation_result:
            return {
                "total_diagrams": 0,
                "successful_generations": 0,
                "failed_generations": 0,
                "validation_success_rate": 0.0,
            }
        
        return {
            "total_diagrams": self._generation_result.total_diagrams,
            "successful_generations": self._generation_result.successful_generations,
            "failed_generations": self._generation_result.failed_generations,
            "validation_success_rate": self._generation_result.validation_success_rate,
            "plantuml_diagrams": self._generation_result.plantuml_diagrams,
            "mermaid_diagrams": self._generation_result.mermaid_diagrams,
            "svg_outputs": self._generation_result.svg_outputs,
            "png_outputs": self._generation_result.png_outputs,
            "average_accuracy_score": sum(self._generation_result.accuracy_scores) / len(self._generation_result.accuracy_scores) if self._generation_result.accuracy_scores else 0.0,
        }