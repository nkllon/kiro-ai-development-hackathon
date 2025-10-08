#!/usr/bin/env python3
"""
Diagram Models - Task 3.1 Implementation
========================================

Data models and structures for comprehensive diagram generation system.
Provides models for PlantUML and Mermaid diagrams with security boundaries,
access control, versioning, validation status, and real-time service indicators.

Author: Beast Mode Framework
Date: 2024-12-19
Version: 1.0
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Dict, List, Any, Optional, Set, Tuple, Union
import json
import yaml
from pathlib import Path


class DiagramType(Enum):
    """Types of diagrams that can be generated."""
    COMPONENT = "component"
    SEQUENCE = "sequence"
    NETWORK_TOPOLOGY = "network_topology"
    DATA_FLOW = "data_flow"
    USE_CASE = "use_case"
    DEPLOYMENT = "deployment"
    SECURITY_BOUNDARY = "security_boundary"
    ACCESS_CONTROL = "access_control"


class DiagramFormat(Enum):
    """Output formats for diagrams."""
    PLANTUML = "plantuml"
    MERMAID = "mermaid"
    SVG = "svg"
    PNG = "png"
    PDF = "pdf"
    JSON = "json"
    YAML = "yaml"


class ValidationStatus(Enum):
    """Diagram validation status."""
    VALID = "valid"
    INVALID = "invalid"
    PENDING = "pending"
    STALE = "stale"
    ERROR = "error"
    WARNING = "warning"


class SecurityLevel(Enum):
    """Security classification levels."""
    PUBLIC = "public"
    INTERNAL = "internal"
    CONFIDENTIAL = "confidential"
    RESTRICTED = "restricted"


class ServiceStatus(Enum):
    """Real-time service status indicators."""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    DOWN = "down"
    MAINTENANCE = "maintenance"
    UNKNOWN = "unknown"
    STARTING = "starting"
    STOPPING = "stopping"


@dataclass
class DiagramComponent:
    """
    Individual component in a diagram with comprehensive metadata.
    
    Represents a system component with security boundaries,
    access control, and real-time status indicators.
    """
    id: str
    name: str
    type: str
    description: Optional[str] = None
    security_level: SecurityLevel = SecurityLevel.INTERNAL
    access_control: List[str] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)
    interfaces: List[str] = field(default_factory=list)
    status: ServiceStatus = ServiceStatus.UNKNOWN
    health_score: float = 0.0
    last_updated: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)
    tags: Set[str] = field(default_factory=set)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "id": self.id,
            "name": self.name,
            "type": self.type,
            "description": self.description,
            "security_level": self.security_level.value,
            "access_control": self.access_control,
            "dependencies": self.dependencies,
            "interfaces": self.interfaces,
            "status": self.status.value,
            "health_score": self.health_score,
            "last_updated": self.last_updated.isoformat(),
            "metadata": self.metadata,
            "tags": list(self.tags)
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'DiagramComponent':
        """Create from dictionary representation."""
        return cls(
            id=data["id"],
            name=data["name"],
            type=data["type"],
            description=data.get("description"),
            security_level=SecurityLevel(data.get("security_level", "internal")),
            access_control=data.get("access_control", []),
            dependencies=data.get("dependencies", []),
            interfaces=data.get("interfaces", []),
            status=ServiceStatus(data.get("status", "unknown")),
            health_score=data.get("health_score", 0.0),
            last_updated=datetime.fromisoformat(data.get("last_updated", datetime.now().isoformat())),
            metadata=data.get("metadata", {}),
            tags=set(data.get("tags", []))
        )


@dataclass
class DiagramRelationship:
    """
    Relationship between diagram components.
    
    Represents connections, dependencies, and data flows
    between system components with security and access control.
    """
    source_id: str
    target_id: str
    relationship_type: str
    description: Optional[str] = None
    security_level: SecurityLevel = SecurityLevel.INTERNAL
    access_control: List[str] = field(default_factory=list)
    protocol: Optional[str] = None
    port: Optional[int] = None
    encryption: bool = False
    authentication_required: bool = False
    bandwidth_limit: Optional[int] = None
    latency_ms: Optional[float] = None
    reliability_score: float = 1.0
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "source_id": self.source_id,
            "target_id": self.target_id,
            "relationship_type": self.relationship_type,
            "description": self.description,
            "security_level": self.security_level.value,
            "access_control": self.access_control,
            "protocol": self.protocol,
            "port": self.port,
            "encryption": self.encryption,
            "authentication_required": self.authentication_required,
            "bandwidth_limit": self.bandwidth_limit,
            "latency_ms": self.latency_ms,
            "reliability_score": self.reliability_score,
            "metadata": self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'DiagramRelationship':
        """Create from dictionary representation."""
        return cls(
            source_id=data["source_id"],
            target_id=data["target_id"],
            relationship_type=data["relationship_type"],
            description=data.get("description"),
            security_level=SecurityLevel(data.get("security_level", "internal")),
            access_control=data.get("access_control", []),
            protocol=data.get("protocol"),
            port=data.get("port"),
            encryption=data.get("encryption", False),
            authentication_required=data.get("authentication_required", False),
            bandwidth_limit=data.get("bandwidth_limit"),
            latency_ms=data.get("latency_ms"),
            reliability_score=data.get("reliability_score", 1.0),
            metadata=data.get("metadata", {})
        )


@dataclass
class SecurityBoundary:
    """
    Security boundary definition for diagram components.
    
    Represents security zones, trust boundaries, and
    access control policies within the system architecture.
    """
    id: str
    name: str
    description: Optional[str] = None
    security_level: SecurityLevel = SecurityLevel.INTERNAL
    components: List[str] = field(default_factory=list)
    access_policies: List[Dict[str, Any]] = field(default_factory=list)
    encryption_required: bool = False
    authentication_required: bool = False
    audit_logging: bool = True
    network_segmentation: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "security_level": self.security_level.value,
            "components": self.components,
            "access_policies": self.access_policies,
            "encryption_required": self.encryption_required,
            "authentication_required": self.authentication_required,
            "audit_logging": self.audit_logging,
            "network_segmentation": self.network_segmentation,
            "metadata": self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SecurityBoundary':
        """Create from dictionary representation."""
        return cls(
            id=data["id"],
            name=data["name"],
            description=data.get("description"),
            security_level=SecurityLevel(data.get("security_level", "internal")),
            components=data.get("components", []),
            access_policies=data.get("access_policies", []),
            encryption_required=data.get("encryption_required", False),
            authentication_required=data.get("authentication_required", False),
            audit_logging=data.get("audit_logging", True),
            network_segmentation=data.get("network_segmentation", False),
            metadata=data.get("metadata", {})
        )


@dataclass
class DiagramVersion:
    """
    Version information for diagram generation and tracking.
    
    Tracks diagram versions, changes, validation status,
    and accuracy confidence scoring.
    """
    version: str
    created_at: datetime
    created_by: str
    description: Optional[str] = None
    validation_status: ValidationStatus = ValidationStatus.PENDING
    accuracy_confidence: float = 0.0
    validation_errors: List[str] = field(default_factory=list)
    validation_warnings: List[str] = field(default_factory=list)
    last_validated: Optional[datetime] = None
    validation_duration_ms: Optional[float] = None
    change_summary: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "version": self.version,
            "created_at": self.created_at.isoformat(),
            "created_by": self.created_by,
            "description": self.description,
            "validation_status": self.validation_status.value,
            "accuracy_confidence": self.accuracy_confidence,
            "validation_errors": self.validation_errors,
            "validation_warnings": self.validation_warnings,
            "last_validated": self.last_validated.isoformat() if self.last_validated else None,
            "validation_duration_ms": self.validation_duration_ms,
            "change_summary": self.change_summary,
            "metadata": self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'DiagramVersion':
        """Create from dictionary representation."""
        return cls(
            version=data["version"],
            created_at=datetime.fromisoformat(data["created_at"]),
            created_by=data["created_by"],
            description=data.get("description"),
            validation_status=ValidationStatus(data.get("validation_status", "pending")),
            accuracy_confidence=data.get("accuracy_confidence", 0.0),
            validation_errors=data.get("validation_errors", []),
            validation_warnings=data.get("validation_warnings", []),
            last_validated=datetime.fromisoformat(data["last_validated"]) if data.get("last_validated") else None,
            validation_duration_ms=data.get("validation_duration_ms"),
            change_summary=data.get("change_summary"),
            metadata=data.get("metadata", {})
        )


@dataclass
class RealTimeStatus:
    """
    Real-time service status information for diagram components.
    
    Provides live status indicators, health scores, and
    performance metrics for diagram components.
    """
    component_id: str
    status: ServiceStatus
    health_score: float
    response_time_ms: Optional[float] = None
    error_rate: float = 0.0
    last_check: datetime = field(default_factory=datetime.now)
    uptime_percentage: float = 100.0
    active_connections: int = 0
    resource_usage: Dict[str, float] = field(default_factory=dict)
    alerts: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "component_id": self.component_id,
            "status": self.status.value,
            "health_score": self.health_score,
            "response_time_ms": self.response_time_ms,
            "error_rate": self.error_rate,
            "last_check": self.last_check.isoformat(),
            "uptime_percentage": self.uptime_percentage,
            "active_connections": self.active_connections,
            "resource_usage": self.resource_usage,
            "alerts": self.alerts,
            "metadata": self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'RealTimeStatus':
        """Create from dictionary representation."""
        return cls(
            component_id=data["component_id"],
            status=ServiceStatus(data.get("status", "unknown")),
            health_score=data.get("health_score", 0.0),
            response_time_ms=data.get("response_time_ms"),
            error_rate=data.get("error_rate", 0.0),
            last_check=datetime.fromisoformat(data.get("last_check", datetime.now().isoformat())),
            uptime_percentage=data.get("uptime_percentage", 100.0),
            active_connections=data.get("active_connections", 0),
            resource_usage=data.get("resource_usage", {}),
            alerts=data.get("alerts", []),
            metadata=data.get("metadata", {})
        )


@dataclass
class DiagramMetadata:
    """
    Comprehensive metadata for diagram generation and management.
    
    Contains all metadata needed for diagram versioning,
    validation, security, and real-time status tracking.
    """
    diagram_id: str
    title: str
    description: Optional[str] = None
    diagram_type: DiagramType = DiagramType.COMPONENT
    format: DiagramFormat = DiagramFormat.PLANTUML
    security_level: SecurityLevel = SecurityLevel.INTERNAL
    version: DiagramVersion = field(default_factory=lambda: DiagramVersion(
        version="1.0.0",
        created_at=datetime.now(),
        created_by="system"
    ))
    components: List[DiagramComponent] = field(default_factory=list)
    relationships: List[DiagramRelationship] = field(default_factory=list)
    security_boundaries: List[SecurityBoundary] = field(default_factory=list)
    real_time_status: Dict[str, RealTimeStatus] = field(default_factory=dict)
    generated_at: datetime = field(default_factory=datetime.now)
    generated_by: str = "diagram_generator"
    template_version: str = "1.0"
    validation_status: ValidationStatus = ValidationStatus.PENDING
    accuracy_confidence: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "diagram_id": self.diagram_id,
            "title": self.title,
            "description": self.description,
            "diagram_type": self.diagram_type.value,
            "format": self.format.value,
            "security_level": self.security_level.value,
            "version": self.version.to_dict(),
            "components": [comp.to_dict() for comp in self.components],
            "relationships": [rel.to_dict() for rel in self.relationships],
            "security_boundaries": [boundary.to_dict() for boundary in self.security_boundaries],
            "real_time_status": {k: v.to_dict() for k, v in self.real_time_status.items()},
            "generated_at": self.generated_at.isoformat(),
            "generated_by": self.generated_by,
            "template_version": self.template_version,
            "validation_status": self.validation_status.value,
            "accuracy_confidence": self.accuracy_confidence,
            "metadata": self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'DiagramMetadata':
        """Create from dictionary representation."""
        return cls(
            diagram_id=data["diagram_id"],
            title=data["title"],
            description=data.get("description"),
            diagram_type=DiagramType(data.get("diagram_type", "component")),
            format=DiagramFormat(data.get("format", "plantuml")),
            security_level=SecurityLevel(data.get("security_level", "internal")),
            version=DiagramVersion.from_dict(data.get("version", {
                "version": "1.0.0",
                "created_at": datetime.now().isoformat(),
                "created_by": "system"
            })),
            components=[DiagramComponent.from_dict(comp) for comp in data.get("components", [])],
            relationships=[DiagramRelationship.from_dict(rel) for rel in data.get("relationships", [])],
            security_boundaries=[SecurityBoundary.from_dict(boundary) for boundary in data.get("security_boundaries", [])],
            real_time_status={k: RealTimeStatus.from_dict(v) for k, v in data.get("real_time_status", {}).items()},
            generated_at=datetime.fromisoformat(data.get("generated_at", datetime.now().isoformat())),
            generated_by=data.get("generated_by", "diagram_generator"),
            template_version=data.get("template_version", "1.0"),
            validation_status=ValidationStatus(data.get("validation_status", "pending")),
            accuracy_confidence=data.get("accuracy_confidence", 0.0),
            metadata=data.get("metadata", {})
        )
    
    def to_json(self, file_path: Optional[Path] = None) -> str:
        """Export to JSON format."""
        json_data = json.dumps(self.to_dict(), indent=2, default=str)
        
        if file_path:
            with open(file_path, 'w') as f:
                f.write(json_data)
        
        return json_data
    
    def to_yaml(self, file_path: Optional[Path] = None) -> str:
        """Export to YAML format."""
        yaml_data = yaml.dump(self.to_dict(), default_flow_style=False, sort_keys=False)
        
        if file_path:
            with open(file_path, 'w') as f:
                f.write(yaml_data)
        
        return yaml_data
    
    @classmethod
    def from_json(cls, json_data: str) -> 'DiagramMetadata':
        """Import from JSON format."""
        data = json.loads(json_data)
        return cls.from_dict(data)
    
    @classmethod
    def from_yaml(cls, yaml_data: str) -> 'DiagramMetadata':
        """Import from YAML format."""
        data = yaml.safe_load(yaml_data)
        return cls.from_dict(data)
    
    @classmethod
    def from_file(cls, file_path: Path) -> 'DiagramMetadata':
        """Import from file (auto-detect format)."""
        with open(file_path, 'r') as f:
            content = f.read()
        
        if file_path.suffix.lower() == '.json':
            return cls.from_json(content)
        elif file_path.suffix.lower() in ['.yml', '.yaml']:
            return cls.from_yaml(content)
        else:
            raise ValueError(f"Unsupported file format: {file_path.suffix}")
    
    def get_component_by_id(self, component_id: str) -> Optional[DiagramComponent]:
        """Get component by ID."""
        for component in self.components:
            if component.id == component_id:
                return component
        return None
    
    def get_components_by_type(self, component_type: str) -> List[DiagramComponent]:
        """Get components by type."""
        return [comp for comp in self.components if comp.type == component_type]
    
    def get_components_by_security_level(self, security_level: SecurityLevel) -> List[DiagramComponent]:
        """Get components by security level."""
        return [comp for comp in self.components if comp.security_level == security_level]
    
    def get_relationships_by_source(self, source_id: str) -> List[DiagramRelationship]:
        """Get relationships by source component."""
        return [rel for rel in self.relationships if rel.source_id == source_id]
    
    def get_relationships_by_target(self, target_id: str) -> List[DiagramRelationship]:
        """Get relationships by target component."""
        return [rel for rel in self.relationships if rel.target_id == target_id]
    
    def get_security_boundary_by_id(self, boundary_id: str) -> Optional[SecurityBoundary]:
        """Get security boundary by ID."""
        for boundary in self.security_boundaries:
            if boundary.id == boundary_id:
                return boundary
        return None
    
    def validate_diagram(self) -> List[str]:
        """Validate diagram configuration and return any issues."""
        issues = []
        
        # Check for duplicate component IDs
        component_ids = [comp.id for comp in self.components]
        if len(component_ids) != len(set(component_ids)):
            issues.append("Duplicate component IDs found")
        
        # Check for missing components in relationships
        for relationship in self.relationships:
            if relationship.source_id not in component_ids:
                issues.append(f"Relationship source component {relationship.source_id} not found")
            if relationship.target_id not in component_ids:
                issues.append(f"Relationship target component {relationship.target_id} not found")
        
        # Check security boundaries
        for boundary in self.security_boundaries:
            for component_id in boundary.components:
                if component_id not in component_ids:
                    issues.append(f"Security boundary {boundary.id} references unknown component {component_id}")
        
        # Check real-time status
        for status_id, status in self.real_time_status.items():
            if status_id not in component_ids:
                issues.append(f"Real-time status for unknown component {status_id}")
        
        return issues
    
    def calculate_accuracy_confidence(self) -> float:
        """Calculate accuracy confidence score based on validation and data freshness."""
        confidence = 1.0
        
        # Reduce confidence for validation issues
        validation_issues = len(self.validate_diagram())
        if validation_issues > 0:
            confidence -= min(0.5, validation_issues * 0.1)
        
        # Reduce confidence for stale data
        now = datetime.now()
        for component in self.components:
            age_hours = (now - component.last_updated).total_seconds() / 3600
            if age_hours > 24:  # Data older than 24 hours
                confidence -= 0.1
        
        # Reduce confidence for unknown status components
        unknown_count = sum(1 for comp in self.components if comp.status == ServiceStatus.UNKNOWN)
        if unknown_count > 0:
            confidence -= min(0.3, unknown_count * 0.05)
        
        return max(0.0, min(1.0, confidence))
    
    def get_diagram_summary(self) -> Dict[str, Any]:
        """Get comprehensive diagram summary."""
        validation_issues = self.validate_diagram()
        
        return {
            "diagram_id": self.diagram_id,
            "title": self.title,
            "diagram_type": self.diagram_type.value,
            "format": self.format.value,
            "security_level": self.security_level.value,
            "version": self.version.version,
            "total_components": len(self.components),
            "total_relationships": len(self.relationships),
            "security_boundaries": len(self.security_boundaries),
            "real_time_status_count": len(self.real_time_status),
            "validation_status": self.validation_status.value,
            "accuracy_confidence": self.accuracy_confidence,
            "validation_issues_count": len(validation_issues),
            "generated_at": self.generated_at.isoformat(),
            "generated_by": self.generated_by,
            "template_version": self.template_version
        }