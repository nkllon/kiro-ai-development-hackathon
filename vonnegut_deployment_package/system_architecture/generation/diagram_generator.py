#!/usr/bin/env python3
"""
Diagram Generator - Task 3.1 Implementation
==========================================

Comprehensive diagram generation system with PlantUML and Mermaid integration.
Builds component diagrams with security boundaries, access control, versioning,
validation status tracking, and real-time service status indicators.

Author: Beast Mode Framework
Date: 2025-01-03
Version: 1.0
"""

import logging
import json
import yaml
from typing import Dict, List, Any, Optional, Set, Tuple, Union
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
import subprocess
import tempfile
import base64

from src.rm_ddd.core.unified_reflective_module import ReflectiveModule, ModuleCapability, GracefulDegradationResult
from src.system_architecture.models.diagram_models import (
    DiagramMetadata, DiagramComponent, DiagramRelationship, SecurityBoundary,
    DiagramType, DiagramFormat, ValidationStatus, SecurityLevel, ServiceStatus,
    DiagramVersion, RealTimeStatus
)
from src.system_architecture.models.network_topology import NetworkTopology, ServiceEndpoint
from src.system_architecture.discovery.service_scanner import ServiceScanner
from src.system_architecture.discovery.system_constraint_validator import SystemConstraintValidator


@dataclass
class DiagramGenerationConfig:
    """Configuration for diagram generation."""
    output_directory: Path = Path("generated_diagrams")
    plantuml_jar_path: Optional[Path] = None
    include_security_boundaries: bool = True
    include_real_time_status: bool = True
    svg_output: bool = True
    html_output: bool = True
    png_output: bool = False
    pdf_output: bool = False
    validation_enabled: bool = True
    accuracy_threshold: float = 0.95


@dataclass
class DiagramTemplate:
    """Template for diagram generation."""
    template_id: str
    name: str
    description: str
    diagram_type: DiagramType
    format: DiagramFormat
    template_content: str
    variables: List[str] = field(default_factory=list)
    security_level: SecurityLevel = SecurityLevel.INTERNAL


class DiagramGenerator(ReflectiveModule):
    """
    Comprehensive diagram generation system with PlantUML and Mermaid integration.
    
    Implements Task 3.1 from the system architecture wiring diagram specification.
    Provides component diagram generation with security boundaries, access control,
    versioning, validation status tracking, and real-time service status indicators.
    """
    
    def __init__(self, config: Optional[DiagramGenerationConfig] = None):
        super().__init__()
        self.module_id = "DiagramGenerator"
        self._logger = logging.getLogger(f"system_architecture.{self.__class__.__name__}")
        
        # Configuration
        self._config = config or DiagramGenerationConfig()
        
        # Ensure output directory exists
        self._config.output_directory.mkdir(parents=True, exist_ok=True)
        
        # Initialize dependencies
        self._service_scanner = ServiceScanner()
        self._constraint_validator = SystemConstraintValidator()
        
        # Templates storage
        self._templates: Dict[str, DiagramTemplate] = {}
        
        # Generated diagrams cache
        self._generated_diagrams: Dict[str, DiagramMetadata] = {}
        
        # Real-time status cache
        self._status_cache: Dict[str, RealTimeStatus] = {}
        
        # Initialize default templates
        self._initialize_default_templates()
        
        self._logger.info("DiagramGenerator initialized")
    
    def get_capabilities(self) -> List[ModuleCapability]:
        """Get module capabilities."""
        return [
            ModuleCapability.CORE_FUNCTIONALITY,
            ModuleCapability.DATA_PROCESSING,
            ModuleCapability.VALIDATION
        ]
    
    def _initialize_default_templates(self) -> None:
        """Initialize default diagram templates."""
        # PlantUML Component Diagram Template
        plantuml_component_template = DiagramTemplate(
            template_id="plantuml_component",
            name="PlantUML Component Diagram",
            description="Component diagram with security boundaries and real-time status",
            diagram_type=DiagramType.COMPONENT,
            format=DiagramFormat.PLANTUML,
            template_content="""
@startuml {diagram_title}
!theme plain
skinparam componentStyle rectangle
skinparam backgroundColor #FFFFFF
skinparam componentBackgroundColor #E1F5FE
skinparam componentBorderColor #0277BD

title {diagram_title}
note top : Generated: {generated_at}\\nVersion: {version}\\nAccuracy: {accuracy_confidence}%

{security_boundaries}

{components}

{relationships}

{real_time_status}

@enduml
""",
            variables=["diagram_title", "generated_at", "version", "accuracy_confidence", 
                      "security_boundaries", "components", "relationships", "real_time_status"]
        )
        
        # Mermaid Component Diagram Template
        mermaid_component_template = DiagramTemplate(
            template_id="mermaid_component",
            name="Mermaid Component Diagram",
            description="Interactive component diagram with real-time updates",
            diagram_type=DiagramType.COMPONENT,
            format=DiagramFormat.MERMAID,
            template_content="""
graph TD
    %% {diagram_title}
    %% Generated: {generated_at}
    %% Version: {version}
    %% Accuracy: {accuracy_confidence}%
    
    {components}
    
    {relationships}
    
    {styling}
""",
            variables=["diagram_title", "generated_at", "version", "accuracy_confidence",
                      "components", "relationships", "styling"]
        )
        
        self._templates["plantuml_component"] = plantuml_component_template
        self._templates["mermaid_component"] = mermaid_component_template
        
        self._logger.info(f"Initialized {len(self._templates)} default templates")
    
    def generate_component_diagram(self, 
                                 topology: NetworkTopology,
                                 diagram_id: str,
                                 title: str,
                                 format: DiagramFormat = DiagramFormat.PLANTUML,
                                 include_security: bool = True,
                                 include_real_time: bool = True) -> DiagramMetadata:
        """
        Generate component diagram with security boundaries and real-time status.
        
        Args:
            topology: Network topology data
            diagram_id: Unique diagram identifier
            title: Diagram title
            format: Output format (PlantUML or Mermaid)
            include_security: Include security boundaries
            include_real_time: Include real-time status indicators
            
        Returns:
            DiagramMetadata with generated diagram information
        """
        self._logger.info(f"Generating component diagram: {diagram_id}")
        
        try:
            # Create diagram metadata
            diagram_metadata = DiagramMetadata(
                diagram_id=diagram_id,
                title=title,
                diagram_type=DiagramType.COMPONENT,
                format=format,
                security_level=SecurityLevel.INTERNAL
            )
            
            # Convert topology to diagram components
            components = self._convert_topology_to_components(topology)
            relationships = self._extract_component_relationships(topology)
            
            # Add security boundaries if requested
            security_boundaries = []
            if include_security:
                security_boundaries = self._create_security_boundaries(components)
            
            # Add real-time status if requested
            real_time_status = {}
            if include_real_time:
                real_time_status = self._collect_real_time_status(components)
            
            # Update diagram metadata
            diagram_metadata.components = components
            diagram_metadata.relationships = relationships
            diagram_metadata.security_boundaries = security_boundaries
            diagram_metadata.real_time_status = real_time_status
            
            # Generate diagram content
            diagram_content = self._generate_diagram_content(diagram_metadata)
            
            # Validate diagram
            validation_result = self._validate_diagram(diagram_metadata)
            diagram_metadata.validation_status = validation_result["status"]
            diagram_metadata.accuracy_confidence = validation_result["confidence"]
            
            # Save diagram files
            output_files = self._save_diagram_files(diagram_metadata, diagram_content)
            diagram_metadata.metadata["output_files"] = output_files
            
            # Cache generated diagram
            self._generated_diagrams[diagram_id] = diagram_metadata
            
            self._logger.info(f"Generated component diagram: {diagram_id} with {len(components)} components")
            return diagram_metadata
            
        except Exception as e:
            self._logger.error(f"Failed to generate component diagram {diagram_id}: {e}")
            raise
    
    def _convert_topology_to_components(self, topology: NetworkTopology) -> List[DiagramComponent]:
        """Convert network topology to diagram components."""
        components = []
        
        for service in topology.service_endpoints:
            # Determine component type based on service
            component_type = self._determine_component_type(service)
            
            # Determine security level
            security_level = self._determine_security_level(service)
            
            # Create component
            component = DiagramComponent(
                id=f"component_{service.name.lower().replace(' ', '_')}",
                name=service.name,
                type=component_type,
                description=f"Service running on {service.host}:{service.port}",
                security_level=security_level,
                dependencies=service.dependencies,
                interfaces=[f"{service.protocol.value}:{service.port}"],
                status=self._convert_service_status(service.status),
                health_score=self._calculate_health_score(service),
                metadata={
                    "host": service.host,
                    "port": service.port,
                    "protocol": service.protocol.value,
                    "websocket_endpoints": service.websocket_endpoints,
                    "health_endpoint": service.health_endpoint,
                    "response_time_ms": service.response_time_ms,
                    "error_count": service.error_count
                }
            )
            
            components.append(component)
        
        # Add infrastructure components
        infrastructure_components = self._create_infrastructure_components(topology)
        components.extend(infrastructure_components)
        
        return components
    
    def _determine_component_type(self, service: ServiceEndpoint) -> str:
        """Determine component type based on service characteristics."""
        service_name = service.name.lower()
        
        if "observatory" in service_name:
            return "observatory_server"
        elif "prometheus" in service_name:
            return "metrics_collector"
        elif "grafana" in service_name:
            return "visualization_dashboard"
        elif "redis" in service_name:
            return "coordination_service"
        elif "directus" in service_name:
            return "cms_service"
        elif service.websocket_endpoints:
            return "websocket_service"
        elif service.health_endpoint:
            return "monitored_service"
        else:
            return "generic_service"
    
    def _determine_security_level(self, service: ServiceEndpoint) -> SecurityLevel:
        """Determine security level based on service characteristics."""
        service_name = service.name.lower()
        
        if "admin" in service_name or "management" in service_name:
            return SecurityLevel.RESTRICTED
        elif "internal" in service_name or "redis" in service_name:
            return SecurityLevel.CONFIDENTIAL
        elif "public" in service_name or "api" in service_name:
            return SecurityLevel.PUBLIC
        else:
            return SecurityLevel.INTERNAL
    
    def _convert_service_status(self, status) -> ServiceStatus:
        """Convert service status to diagram service status."""
        status_mapping = {
            "active": ServiceStatus.HEALTHY,
            "inactive": ServiceStatus.DOWN,
            "degraded": ServiceStatus.DEGRADED,
            "maintenance": ServiceStatus.MAINTENANCE,
            "unknown": ServiceStatus.UNKNOWN
        }
        
        if hasattr(status, 'value'):
            return status_mapping.get(status.value, ServiceStatus.UNKNOWN)
        else:
            return status_mapping.get(str(status).lower(), ServiceStatus.UNKNOWN)
    
    def _calculate_health_score(self, service: ServiceEndpoint) -> float:
        """Calculate health score based on service metrics."""
        score = 1.0
        
        # Reduce score based on error count
        if service.error_count > 0:
            score -= min(0.5, service.error_count * 0.1)
        
        # Reduce score based on response time
        if service.response_time_ms:
            if service.response_time_ms > 1000:  # > 1 second
                score -= 0.3
            elif service.response_time_ms > 500:  # > 500ms
                score -= 0.1
        
        # Reduce score if no health endpoint
        if not service.health_endpoint:
            score -= 0.2
        
        return max(0.0, min(1.0, score))
    
    def _create_infrastructure_components(self, topology: NetworkTopology) -> List[DiagramComponent]:
        """Create infrastructure components from topology."""
        components = []
        
        # Cloudflare Tunnel component
        tunnel_component = DiagramComponent(
            id="cloudflare_tunnel",
            name="Cloudflare Tunnel",
            type="tunnel_service",
            description="Cloudflare tunnel for secure external access",
            security_level=SecurityLevel.PUBLIC,
            interfaces=["https:443", "websocket:443"],
            status=ServiceStatus.HEALTHY,
            health_score=0.95,
            metadata={
                "tunnel_id": "d1e53e43-033f-4994-8f46-c83962ae3785",
                "domains": ["observatory.nkllon.com", "grafana.observatory.nkllon.com", "prometheus.observatory.nkllon.com"]
            }
        )
        components.append(tunnel_component)
        
        # Redis Coordination component
        if topology.redis_coordination:
            redis_component = DiagramComponent(
                id="redis_coordination",
                name="Redis Coordination",
                type="coordination_service",
                description="Redis coordination with failover support",
                security_level=SecurityLevel.CONFIDENTIAL,
                interfaces=["redis:6379", "redis:6380"],
                status=ServiceStatus.HEALTHY if topology.redis_coordination.health_status == "healthy" else ServiceStatus.UNKNOWN,
                health_score=0.9,
                metadata={
                    "primary_endpoint": topology.redis_coordination.primary_endpoint,
                    "fallback_endpoints": topology.redis_coordination.fallback_endpoints,
                    "cluster_mode": topology.redis_coordination.cluster_mode
                }
            )
            components.append(redis_component)
        
        # Network Infrastructure component
        network_component = DiagramComponent(
            id="network_infrastructure",
            name="Network Infrastructure",
            type="network_layer",
            description=f"Local network infrastructure ({topology.local_network_range})",
            security_level=SecurityLevel.INTERNAL,
            interfaces=["tcp", "udp", "http", "https"],
            status=ServiceStatus.HEALTHY,
            health_score=0.98,
            metadata={
                "network_range": topology.local_network_range,
                "port_allocations": topology.port_allocations
            }
        )
        components.append(network_component)
        
        return components
    
    def _extract_component_relationships(self, topology: NetworkTopology) -> List[DiagramRelationship]:
        """Extract relationships between components."""
        relationships = []
        
        # Create relationships from network flows
        for flow in topology.network_flows:
            relationship = DiagramRelationship(
                source_id=f"component_{flow.source.lower().replace(' ', '_')}",
                target_id=f"component_{flow.destination.lower().replace(' ', '_')}",
                relationship_type=flow.flow_type.value,
                description=f"{flow.protocol.value} connection on port {flow.port}",
                protocol=flow.protocol.value,
                port=flow.port,
                encryption=flow.protocol.value in ["https", "wss"],
                bandwidth_limit=flow.bandwidth_limit,
                latency_ms=flow.latency_ms,
                reliability_score=1.0 - (flow.packet_loss_percent or 0) / 100,
                metadata={
                    "decision_points": flow.decision_points,
                    "routing_rules": flow.routing_rules,
                    "security_policies": flow.security_policies
                }
            )
            relationships.append(relationship)
        
        # Create relationships from service dependencies
        for service in topology.service_endpoints:
            source_id = f"component_{service.name.lower().replace(' ', '_')}"
            
            for dependency in service.dependencies:
                target_id = f"component_{dependency.lower().replace(' ', '_')}"
                
                relationship = DiagramRelationship(
                    source_id=source_id,
                    target_id=target_id,
                    relationship_type="depends_on",
                    description=f"{service.name} depends on {dependency}",
                    authentication_required=True,
                    metadata={
                        "dependency_type": "service_dependency"
                    }
                )
                relationships.append(relationship)
        
        # Create relationships from DNS mappings
        for dns_mapping in topology.dns_mappings:
            relationship = DiagramRelationship(
                source_id="cloudflare_tunnel",
                target_id=f"component_{dns_mapping.target_service.lower().replace(' ', '_')}",
                relationship_type="routes_to",
                description=f"DNS routing: {dns_mapping.domain} -> {dns_mapping.target_service}",
                protocol="https",
                port=dns_mapping.target_port,
                encryption=True,
                metadata={
                    "domain": dns_mapping.domain,
                    "tunnel_id": dns_mapping.tunnel_id,
                    "failover_targets": dns_mapping.failover_targets
                }
            )
            relationships.append(relationship)
        
        return relationships
    
    def _create_security_boundaries(self, components: List[DiagramComponent]) -> List[SecurityBoundary]:
        """Create security boundaries for components."""
        boundaries = []
        
        # Group components by security level
        security_groups = {}
        for component in components:
            level = component.security_level
            if level not in security_groups:
                security_groups[level] = []
            security_groups[level].append(component.id)
        
        # Create boundaries for each security level
        for security_level, component_ids in security_groups.items():
            boundary = SecurityBoundary(
                id=f"boundary_{security_level.value}",
                name=f"{security_level.value.title()} Security Zone",
                description=f"Security boundary for {security_level.value} components",
                security_level=security_level,
                components=component_ids,
                encryption_required=security_level in [SecurityLevel.CONFIDENTIAL, SecurityLevel.RESTRICTED],
                authentication_required=security_level != SecurityLevel.PUBLIC,
                audit_logging=True,
                network_segmentation=security_level == SecurityLevel.RESTRICTED,
                metadata={
                    "component_count": len(component_ids),
                    "access_policies": self._generate_access_policies(security_level)
                }
            )
            boundaries.append(boundary)
        
        return boundaries
    
    def _generate_access_policies(self, security_level: SecurityLevel) -> List[Dict[str, Any]]:
        """Generate access policies for security level."""
        policies = []
        
        if security_level == SecurityLevel.PUBLIC:
            policies.append({
                "policy": "allow_public_access",
                "description": "Allow public access with rate limiting",
                "rules": ["rate_limit: 1000/hour", "ddos_protection: enabled"]
            })
        elif security_level == SecurityLevel.INTERNAL:
            policies.append({
                "policy": "internal_network_only",
                "description": "Allow access from internal network only",
                "rules": ["source_ip: 192.168.1.0/24", "authentication: required"]
            })
        elif security_level == SecurityLevel.CONFIDENTIAL:
            policies.append({
                "policy": "authenticated_access_only",
                "description": "Require authentication and encryption",
                "rules": ["authentication: required", "encryption: tls1.3", "audit_logging: enabled"]
            })
        elif security_level == SecurityLevel.RESTRICTED:
            policies.append({
                "policy": "admin_access_only",
                "description": "Require admin privileges and MFA",
                "rules": ["role: admin", "mfa: required", "session_timeout: 30min", "audit_logging: full"]
            })
        
        return policies
    
    def _collect_real_time_status(self, components: List[DiagramComponent]) -> Dict[str, RealTimeStatus]:
        """Collect real-time status for components."""
        status_map = {}
        
        for component in components:
            # Check if we have cached status
            if component.id in self._status_cache:
                cached_status = self._status_cache[component.id]
                # Use cached if recent (< 5 minutes)
                if (datetime.now() - cached_status.last_check).total_seconds() < 300:
                    status_map[component.id] = cached_status
                    continue
            
            # Collect fresh status
            status = self._collect_component_status(component)
            status_map[component.id] = status
            self._status_cache[component.id] = status
        
        return status_map
    
    def _collect_component_status(self, component: DiagramComponent) -> RealTimeStatus:
        """Collect real-time status for a single component."""
        try:
            # Try to get status from health endpoint if available
            if "health_endpoint" in component.metadata and component.metadata["health_endpoint"]:
                # This would normally make an HTTP request to the health endpoint
                # For now, we'll simulate based on component metadata
                pass
            
            # Calculate status based on available metadata
            status = component.status
            health_score = component.health_score
            
            # Simulate response time based on component type
            response_time = None
            if component.type in ["observatory_server", "metrics_collector", "visualization_dashboard"]:
                response_time = 50.0 + (1.0 - health_score) * 200.0  # 50-250ms based on health
            
            # Calculate error rate based on error count
            error_rate = 0.0
            if "error_count" in component.metadata:
                error_count = component.metadata["error_count"]
                error_rate = min(0.1, error_count * 0.01)  # Max 10% error rate
            
            # Simulate resource usage
            resource_usage = {
                "cpu_percent": 20.0 + (1.0 - health_score) * 30.0,  # 20-50% based on health
                "memory_percent": 30.0 + (1.0 - health_score) * 40.0,  # 30-70% based on health
                "disk_percent": 15.0,
                "network_mbps": 5.0
            }
            
            # Generate alerts based on status
            alerts = []
            if status == ServiceStatus.DEGRADED:
                alerts.append("Service performance degraded")
            elif status == ServiceStatus.DOWN:
                alerts.append("Service unavailable")
            elif error_rate > 0.05:
                alerts.append(f"High error rate: {error_rate:.1%}")
            
            return RealTimeStatus(
                component_id=component.id,
                status=status,
                health_score=health_score,
                response_time_ms=response_time,
                error_rate=error_rate,
                uptime_percentage=95.0 + health_score * 5.0,  # 95-100% based on health
                active_connections=10 if status == ServiceStatus.HEALTHY else 0,
                resource_usage=resource_usage,
                alerts=alerts,
                metadata={
                    "last_restart": (datetime.now().replace(hour=0, minute=0, second=0)).isoformat(),
                    "version": "1.0.0",
                    "build": "latest"
                }
            )
            
        except Exception as e:
            self._logger.warning(f"Failed to collect status for {component.id}: {e}")
            return RealTimeStatus(
                component_id=component.id,
                status=ServiceStatus.UNKNOWN,
                health_score=0.0,
                alerts=[f"Status collection failed: {str(e)}"]
            )
    
    def _generate_diagram_content(self, diagram_metadata: DiagramMetadata) -> str:
        """Generate diagram content based on format and template."""
        template_id = f"{diagram_metadata.format.value}_{diagram_metadata.diagram_type.value}"
        
        if template_id not in self._templates:
            raise ValueError(f"Template not found: {template_id}")
        
        template = self._templates[template_id]
        
        # Prepare template variables
        variables = {
            "diagram_title": diagram_metadata.title,
            "generated_at": diagram_metadata.generated_at.strftime("%Y-%m-%d %H:%M:%S"),
            "version": diagram_metadata.version.version,
            "accuracy_confidence": f"{diagram_metadata.accuracy_confidence * 100:.1f}"
        }
        
        # Generate format-specific content
        if diagram_metadata.format == DiagramFormat.PLANTUML:
            variables.update(self._generate_plantuml_content(diagram_metadata))
        elif diagram_metadata.format == DiagramFormat.MERMAID:
            variables.update(self._generate_mermaid_content(diagram_metadata))
        
        # Replace template variables
        content = template.template_content
        for var_name, var_value in variables.items():
            content = content.replace(f"{{{var_name}}}", str(var_value))
        
        return content
    
    def _generate_plantuml_content(self, diagram_metadata: DiagramMetadata) -> Dict[str, str]:
        """Generate PlantUML-specific content."""
        content = {}
        
        # Generate security boundaries
        boundaries_content = []
        for boundary in diagram_metadata.security_boundaries:
            boundary_color = self._get_security_color(boundary.security_level)
            boundaries_content.append(f"rectangle \"{boundary.name}\" as {boundary.id} {boundary_color} {{")
            boundaries_content.append("}")
        content["security_boundaries"] = "\n".join(boundaries_content)
        
        # Generate components
        components_content = []
        for component in diagram_metadata.components:
            status_icon = self._get_status_icon(component.status)
            component_color = self._get_component_color(component.type)
            
            components_content.append(f"component \"{status_icon} {component.name}\" as {component.id} {component_color}")
            
            # Add component details as notes
            if component.description:
                components_content.append(f"note right of {component.id} : {component.description}")
        
        content["components"] = "\n".join(components_content)
        
        # Generate relationships
        relationships_content = []
        for relationship in diagram_metadata.relationships:
            arrow_style = self._get_relationship_arrow(relationship.relationship_type)
            label = f"{relationship.protocol}:{relationship.port}" if relationship.protocol and relationship.port else relationship.relationship_type
            
            relationships_content.append(f"{relationship.source_id} {arrow_style} {relationship.target_id} : {label}")
        
        content["relationships"] = "\n".join(relationships_content)
        
        # Generate real-time status
        status_content = []
        for component_id, status in diagram_metadata.real_time_status.items():
            if status.alerts:
                status_content.append(f"note bottom of {component_id} : Health: {status.health_score:.1%}\\nAlerts: {len(status.alerts)}")
        
        content["real_time_status"] = "\n".join(status_content)
        
        return content
    
    def _generate_mermaid_content(self, diagram_metadata: DiagramMetadata) -> Dict[str, str]:
        """Generate Mermaid-specific content."""
        content = {}
        
        # Generate components
        components_content = []
        for component in diagram_metadata.components:
            status_icon = self._get_mermaid_status_icon(component.status)
            components_content.append(f"    {component.id}[\"{status_icon} {component.name}\"]")
        
        content["components"] = "\n".join(components_content)
        
        # Generate relationships
        relationships_content = []
        for relationship in diagram_metadata.relationships:
            arrow_style = self._get_mermaid_arrow(relationship.relationship_type)
            label = f"{relationship.protocol}:{relationship.port}" if relationship.protocol and relationship.port else relationship.relationship_type
            
            relationships_content.append(f"    {relationship.source_id} {arrow_style} {relationship.target_id}")
        
        content["relationships"] = "\n".join(relationships_content)
        
        # Generate styling
        styling_content = []
        for component in diagram_metadata.components:
            color_class = self._get_mermaid_color_class(component.status)
            styling_content.append(f"    class {component.id} {color_class}")
        
        content["styling"] = "\n".join(styling_content)
        
        return content
    
    def _get_security_color(self, security_level: SecurityLevel) -> str:
        """Get PlantUML color for security level."""
        colors = {
            SecurityLevel.PUBLIC: "#E8F5E8",
            SecurityLevel.INTERNAL: "#E3F2FD",
            SecurityLevel.CONFIDENTIAL: "#FFF3E0",
            SecurityLevel.RESTRICTED: "#FFEBEE"
        }
        return colors.get(security_level, "#F5F5F5")
    
    def _get_status_icon(self, status: ServiceStatus) -> str:
        """Get status icon for PlantUML."""
        icons = {
            ServiceStatus.HEALTHY: "✅",
            ServiceStatus.DEGRADED: "⚠️",
            ServiceStatus.DOWN: "❌",
            ServiceStatus.MAINTENANCE: "🔧",
            ServiceStatus.UNKNOWN: "❓",
            ServiceStatus.STARTING: "🔄",
            ServiceStatus.STOPPING: "⏹️"
        }
        return icons.get(status, "❓")
    
    def _get_mermaid_status_icon(self, status: ServiceStatus) -> str:
        """Get status icon for Mermaid."""
        icons = {
            ServiceStatus.HEALTHY: "✓",
            ServiceStatus.DEGRADED: "⚠",
            ServiceStatus.DOWN: "✗",
            ServiceStatus.MAINTENANCE: "🔧",
            ServiceStatus.UNKNOWN: "?",
            ServiceStatus.STARTING: "↻",
            ServiceStatus.STOPPING: "⏹"
        }
        return icons.get(status, "?")
    
    def _get_component_color(self, component_type: str) -> str:
        """Get PlantUML color for component type."""
        colors = {
            "observatory_server": "#4CAF50",
            "metrics_collector": "#FF9800",
            "visualization_dashboard": "#2196F3",
            "coordination_service": "#9C27B0",
            "cms_service": "#607D8B",
            "websocket_service": "#00BCD4",
            "tunnel_service": "#795548",
            "network_layer": "#9E9E9E"
        }
        return colors.get(component_type, "#757575")
    
    def _get_relationship_arrow(self, relationship_type: str) -> str:
        """Get PlantUML arrow style for relationship type."""
        arrows = {
            "depends_on": "..>",
            "routes_to": "-->",
            "connects_to": "->",
            "ingress": "==>",
            "egress": "<==",
            "internal": "<->",
            "cross_region": "<=>"
        }
        return arrows.get(relationship_type, "->")
    
    def _get_mermaid_arrow(self, relationship_type: str) -> str:
        """Get Mermaid arrow style for relationship type."""
        arrows = {
            "depends_on": "-.->",
            "routes_to": "-->",
            "connects_to": "->",
            "ingress": "==>",
            "egress": "<==",
            "internal": "<-->",
            "cross_region": "<=>"
        }
        return arrows.get(relationship_type, "-->")
    
    def _get_mermaid_color_class(self, status: ServiceStatus) -> str:
        """Get Mermaid color class for status."""
        classes = {
            ServiceStatus.HEALTHY: "healthy",
            ServiceStatus.DEGRADED: "degraded",
            ServiceStatus.DOWN: "down",
            ServiceStatus.MAINTENANCE: "maintenance",
            ServiceStatus.UNKNOWN: "unknown"
        }
        return classes.get(status, "unknown")
    
    def _validate_diagram(self, diagram_metadata: DiagramMetadata) -> Dict[str, Any]:
        """Validate diagram and calculate accuracy confidence."""
        validation_issues = diagram_metadata.validate_diagram()
        
        # Calculate confidence based on validation and data freshness
        confidence = diagram_metadata.calculate_accuracy_confidence()
        
        # Determine validation status
        if len(validation_issues) == 0 and confidence >= self._config.accuracy_threshold:
            status = ValidationStatus.VALID
        elif len(validation_issues) > 0:
            status = ValidationStatus.INVALID
        elif confidence < self._config.accuracy_threshold:
            status = ValidationStatus.WARNING
        else:
            status = ValidationStatus.PENDING
        
        return {
            "status": status,
            "confidence": confidence,
            "issues": validation_issues,
            "validation_timestamp": datetime.now()
        }
    
    def _save_diagram_files(self, diagram_metadata: DiagramMetadata, content: str) -> List[str]:
        """Save diagram files in requested formats."""
        output_files = []
        
        # Base filename
        base_filename = f"{diagram_metadata.diagram_id}_{diagram_metadata.version.version}"
        
        # Save source content
        source_ext = "puml" if diagram_metadata.format == DiagramFormat.PLANTUML else "mmd"
        source_file = self._config.output_directory / f"{base_filename}.{source_ext}"
        
        with open(source_file, 'w', encoding='utf-8') as f:
            f.write(content)
        output_files.append(str(source_file))
        
        # Save metadata
        metadata_file = self._config.output_directory / f"{base_filename}_metadata.json"
        with open(metadata_file, 'w', encoding='utf-8') as f:
            f.write(diagram_metadata.to_json())
        output_files.append(str(metadata_file))
        
        # Generate additional formats if requested
        if self._config.svg_output:
            svg_file = self._generate_svg_output(source_file, diagram_metadata.format)
            if svg_file:
                output_files.append(str(svg_file))
        
        if self._config.html_output:
            html_file = self._generate_html_output(source_file, diagram_metadata)
            if html_file:
                output_files.append(str(html_file))
        
        if self._config.png_output:
            png_file = self._generate_png_output(source_file, diagram_metadata.format)
            if png_file:
                output_files.append(str(png_file))
        
        return output_files
    
    def _generate_svg_output(self, source_file: Path, format: DiagramFormat) -> Optional[Path]:
        """Generate SVG output from source file."""
        try:
            svg_file = source_file.with_suffix('.svg')
            
            if format == DiagramFormat.PLANTUML:
                # Use PlantUML to generate SVG
                if self._config.plantuml_jar_path and self._config.plantuml_jar_path.exists():
                    cmd = [
                        'java', '-jar', str(self._config.plantuml_jar_path),
                        '-tsvg', str(source_file)
                    ]
                    subprocess.run(cmd, check=True, capture_output=True)
                    return svg_file
                else:
                    self._logger.warning("PlantUML JAR not found, skipping SVG generation")
            
            elif format == DiagramFormat.MERMAID:
                # For Mermaid, we'd need mermaid-cli (mmdc)
                # This is a placeholder - would need actual mermaid-cli installation
                self._logger.info("Mermaid SVG generation would require mermaid-cli")
            
            return None
            
        except Exception as e:
            self._logger.error(f"Failed to generate SVG: {e}")
            return None
    
    def _generate_html_output(self, source_file: Path, diagram_metadata: DiagramMetadata) -> Optional[Path]:
        """Generate HTML output with embedded diagram."""
        try:
            html_file = source_file.with_suffix('.html')
            
            # Read source content
            with open(source_file, 'r', encoding='utf-8') as f:
                source_content = f.read()
            
            # Generate HTML template
            html_template = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{diagram_metadata.title}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        .header {{ background: #f5f5f5; padding: 15px; border-radius: 5px; margin-bottom: 20px; }}
        .diagram {{ border: 1px solid #ddd; padding: 20px; border-radius: 5px; }}
        .metadata {{ background: #f9f9f9; padding: 10px; border-radius: 5px; margin-top: 20px; }}
        .status {{ display: inline-block; padding: 3px 8px; border-radius: 3px; font-size: 12px; }}
        .status.valid {{ background: #d4edda; color: #155724; }}
        .status.warning {{ background: #fff3cd; color: #856404; }}
        .status.invalid {{ background: #f8d7da; color: #721c24; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>{diagram_metadata.title}</h1>
        <p><strong>Type:</strong> {diagram_metadata.diagram_type.value.title()}</p>
        <p><strong>Generated:</strong> {diagram_metadata.generated_at.strftime("%Y-%m-%d %H:%M:%S")}</p>
        <p><strong>Version:</strong> {diagram_metadata.version.version}</p>
        <p><strong>Status:</strong> <span class="status {diagram_metadata.validation_status.value}">{diagram_metadata.validation_status.value.title()}</span></p>
        <p><strong>Accuracy:</strong> {diagram_metadata.accuracy_confidence * 100:.1f}%</p>
    </div>
    
    <div class="diagram">
        <h2>Diagram Source</h2>
        <pre><code>{source_content}</code></pre>
    </div>
    
    <div class="metadata">
        <h3>Components ({len(diagram_metadata.components)})</h3>
        <ul>
"""
            
            for component in diagram_metadata.components:
                html_template += f"<li><strong>{component.name}</strong> ({component.type}) - {component.status.value}</li>\n"
            
            html_template += f"""
        </ul>
        
        <h3>Relationships ({len(diagram_metadata.relationships)})</h3>
        <ul>
"""
            
            for relationship in diagram_metadata.relationships:
                html_template += f"<li>{relationship.source_id} → {relationship.target_id} ({relationship.relationship_type})</li>\n"
            
            html_template += """
        </ul>
    </div>
</body>
</html>
"""
            
            with open(html_file, 'w', encoding='utf-8') as f:
                f.write(html_template)
            
            return html_file
            
        except Exception as e:
            self._logger.error(f"Failed to generate HTML: {e}")
            return None
    
    def _generate_png_output(self, source_file: Path, format: DiagramFormat) -> Optional[Path]:
        """Generate PNG output from source file."""
        try:
            png_file = source_file.with_suffix('.png')
            
            if format == DiagramFormat.PLANTUML:
                # Use PlantUML to generate PNG
                if self._config.plantuml_jar_path and self._config.plantuml_jar_path.exists():
                    cmd = [
                        'java', '-jar', str(self._config.plantuml_jar_path),
                        '-tpng', str(source_file)
                    ]
                    subprocess.run(cmd, check=True, capture_output=True)
                    return png_file
                else:
                    self._logger.warning("PlantUML JAR not found, skipping PNG generation")
            
            return None
            
        except Exception as e:
            self._logger.error(f"Failed to generate PNG: {e}")
            return None
    
    def get_generated_diagrams(self) -> Dict[str, DiagramMetadata]:
        """Get all generated diagrams."""
        return self._generated_diagrams.copy()
    
    def get_diagram_by_id(self, diagram_id: str) -> Optional[DiagramMetadata]:
        """Get diagram by ID."""
        return self._generated_diagrams.get(diagram_id)
    
    def update_real_time_status(self, component_id: str, status: RealTimeStatus) -> None:
        """Update real-time status for a component."""
        self._status_cache[component_id] = status
        
        # Update any diagrams that contain this component
        for diagram in self._generated_diagrams.values():
            if component_id in diagram.real_time_status:
                diagram.real_time_status[component_id] = status
    
    def graceful_degradation(self, error: Exception) -> GracefulDegradationResult:
        """Handle graceful degradation on errors."""
        self._logger.warning(f"Graceful degradation triggered: {error}")
        
        return GracefulDegradationResult(
            success=True,
            message=f"DiagramGenerator degraded due to: {str(error)}",
            fallback_data={
                "generated_diagrams_count": len(self._generated_diagrams),
                "cached_status_count": len(self._status_cache),
                "available_templates": list(self._templates.keys())
            }
        )