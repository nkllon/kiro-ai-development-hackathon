#!/usr/bin/env python3
"""
Automation Chain Models - Task 2.3 Implementation
==================================================

Data models and structures for automation chain analysis and dependency mapping.
Provides comprehensive models for Makefile targets, Python scripts, WebSocket
endpoints, metrics collection pipelines, and integration point coordination.

Author: Beast Mode Framework
Date: 2024-12-19
Version: 1.0
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Dict, List, Any, Optional, Set, Tuple
import json
import yaml
from pathlib import Path


class DependencyType(Enum):
    """Types of automation dependencies."""
    MAKEFILE_TARGET = "makefile_target"
    PYTHON_SCRIPT = "python_script"
    WEBSOCKET_ENDPOINT = "websocket_endpoint"
    METRICS_PIPELINE = "metrics_pipeline"
    INTEGRATION_POINT = "integration_point"
    ENVIRONMENT_VARIABLE = "environment_variable"
    CONFIGURATION_FILE = "configuration_file"
    SERVICE_DEPENDENCY = "service_dependency"


class ExecutionStatus(Enum):
    """Execution status for automation components."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"
    CANCELLED = "cancelled"


class ParameterType(Enum):
    """Types of parameters passed between automation components."""
    STRING = "string"
    INTEGER = "integer"
    BOOLEAN = "boolean"
    LIST = "list"
    DICT = "dict"
    FILE_PATH = "file_path"
    URL = "url"
    ENVIRONMENT_VARIABLE = "environment_variable"


class IntegrationType(Enum):
    """Types of integration points."""
    ACE_REPORTER = "ace_reporter"
    AI_MEMORY_PALACE = "ai_memory_palace"
    DAG_REGISTRY = "dag_registry"
    DIRECTUS_CMS = "directus_cms"
    PROMETHEUS = "prometheus"
    GRAFANA = "grafana"
    REDIS = "redis"
    WEBSOCKET = "websocket"


@dataclass
class ParameterDefinition:
    """
    Parameter definition for automation components.
    
    Represents a parameter that can be passed between automation
    components with type validation and default values.
    """
    name: str
    param_type: ParameterType
    description: str
    required: bool = True
    default_value: Optional[Any] = None
    validation_rules: List[str] = field(default_factory=list)
    environment_variable: Optional[str] = None
    examples: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "name": self.name,
            "type": self.param_type.value,
            "description": self.description,
            "required": self.required,
            "default_value": self.default_value,
            "validation_rules": self.validation_rules,
            "environment_variable": self.environment_variable,
            "examples": self.examples
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ParameterDefinition':
        """Create from dictionary representation."""
        return cls(
            name=data["name"],
            param_type=ParameterType(data.get("type", "string")),
            description=data["description"],
            required=data.get("required", True),
            default_value=data.get("default_value"),
            validation_rules=data.get("validation_rules", []),
            environment_variable=data.get("environment_variable"),
            examples=data.get("examples", [])
        )


@dataclass
class EnvironmentRequirement:
    """
    Environment requirement for automation components.
    
    Represents environment variables, configuration files,
    or system requirements needed for automation execution.
    """
    name: str
    requirement_type: str  # "env_var", "config_file", "service", "port", "network"
    description: str
    required: bool = True
    default_value: Optional[str] = None
    validation_pattern: Optional[str] = None
    examples: List[str] = field(default_factory=list)
    related_components: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "name": self.name,
            "requirement_type": self.requirement_type,
            "description": self.description,
            "required": self.required,
            "default_value": self.default_value,
            "validation_pattern": self.validation_pattern,
            "examples": self.examples,
            "related_components": self.related_components
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'EnvironmentRequirement':
        """Create from dictionary representation."""
        return cls(
            name=data["name"],
            requirement_type=data["requirement_type"],
            description=data["description"],
            required=data.get("required", True),
            default_value=data.get("default_value"),
            validation_pattern=data.get("validation_pattern"),
            examples=data.get("examples", []),
            related_components=data.get("related_components", [])
        )


@dataclass
class MakefileTarget:
    """
    Makefile target with dependency analysis.
    
    Represents a Makefile target with its dependencies,
    parameters, and execution effects.
    """
    name: str
    description: str
    dependencies: List[str] = field(default_factory=list)
    parameters: List[ParameterDefinition] = field(default_factory=list)
    environment_requirements: List[EnvironmentRequirement] = field(default_factory=list)
    execution_effects: List[str] = field(default_factory=list)
    estimated_duration: Optional[str] = None
    success_criteria: List[str] = field(default_factory=list)
    failure_handling: List[str] = field(default_factory=list)
    related_scripts: List[str] = field(default_factory=list)
    infrastructure_impact: List[str] = field(default_factory=list)
    last_executed: Optional[datetime] = None
    execution_count: int = 0
    success_rate: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "name": self.name,
            "description": self.description,
            "dependencies": self.dependencies,
            "parameters": [param.to_dict() for param in self.parameters],
            "environment_requirements": [req.to_dict() for req in self.environment_requirements],
            "execution_effects": self.execution_effects,
            "estimated_duration": self.estimated_duration,
            "success_criteria": self.success_criteria,
            "failure_handling": self.failure_handling,
            "related_scripts": self.related_scripts,
            "infrastructure_impact": self.infrastructure_impact,
            "last_executed": self.last_executed.isoformat() if self.last_executed else None,
            "execution_count": self.execution_count,
            "success_rate": self.success_rate
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'MakefileTarget':
        """Create from dictionary representation."""
        return cls(
            name=data["name"],
            description=data["description"],
            dependencies=data.get("dependencies", []),
            parameters=[ParameterDefinition.from_dict(param) for param in data.get("parameters", [])],
            environment_requirements=[EnvironmentRequirement.from_dict(req) for req in data.get("environment_requirements", [])],
            execution_effects=data.get("execution_effects", []),
            estimated_duration=data.get("estimated_duration"),
            success_criteria=data.get("success_criteria", []),
            failure_handling=data.get("failure_handling", []),
            related_scripts=data.get("related_scripts", []),
            infrastructure_impact=data.get("infrastructure_impact", []),
            last_executed=datetime.fromisoformat(data["last_executed"]) if data.get("last_executed") else None,
            execution_count=data.get("execution_count", 0),
            success_rate=data.get("success_rate", 0.0)
        )


@dataclass
class PythonScript:
    """
    Python script with parameter passing and environment requirements.
    
    Represents a Python automation script with its input/output
    parameters, environment requirements, and integration points.
    """
    script_path: str
    script_name: str
    description: str
    input_parameters: List[ParameterDefinition] = field(default_factory=list)
    output_parameters: List[ParameterDefinition] = field(default_factory=list)
    environment_requirements: List[EnvironmentRequirement] = field(default_factory=list)
    integration_points: List[IntegrationType] = field(default_factory=list)
    websocket_endpoints: List[str] = field(default_factory=list)
    metrics_collection: List[str] = field(default_factory=list)
    error_handling: List[str] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)
    execution_frequency: Optional[str] = None
    last_executed: Optional[datetime] = None
    execution_count: int = 0
    success_rate: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "script_path": self.script_path,
            "script_name": self.script_name,
            "description": self.description,
            "input_parameters": [param.to_dict() for param in self.input_parameters],
            "output_parameters": [param.to_dict() for param in self.output_parameters],
            "environment_requirements": [req.to_dict() for req in self.environment_requirements],
            "integration_points": [point.value for point in self.integration_points],
            "websocket_endpoints": self.websocket_endpoints,
            "metrics_collection": self.metrics_collection,
            "error_handling": self.error_handling,
            "dependencies": self.dependencies,
            "execution_frequency": self.execution_frequency,
            "last_executed": self.last_executed.isoformat() if self.last_executed else None,
            "execution_count": self.execution_count,
            "success_rate": self.success_rate
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'PythonScript':
        """Create from dictionary representation."""
        return cls(
            script_path=data["script_path"],
            script_name=data["script_name"],
            description=data["description"],
            input_parameters=[ParameterDefinition.from_dict(param) for param in data.get("input_parameters", [])],
            output_parameters=[ParameterDefinition.from_dict(param) for param in data.get("output_parameters", [])],
            environment_requirements=[EnvironmentRequirement.from_dict(req) for req in data.get("environment_requirements", [])],
            integration_points=[IntegrationType(point) for point in data.get("integration_points", [])],
            websocket_endpoints=data.get("websocket_endpoints", []),
            metrics_collection=data.get("metrics_collection", []),
            error_handling=data.get("error_handling", []),
            dependencies=data.get("dependencies", []),
            execution_frequency=data.get("execution_frequency"),
            last_executed=datetime.fromisoformat(data["last_executed"]) if data.get("last_executed") else None,
            execution_count=data.get("execution_count", 0),
            success_rate=data.get("success_rate", 0.0)
        )


@dataclass
class WebSocketEndpoint:
    """
    WebSocket endpoint with registration dependencies.
    
    Represents a WebSocket endpoint with its registration
    dependencies, message types, and integration requirements.
    """
    endpoint_path: str
    endpoint_name: str
    description: str
    registration_dependencies: List[str] = field(default_factory=list)
    message_types: List[str] = field(default_factory=list)
    authentication_required: bool = False
    rate_limiting: Optional[Dict[str, Any]] = None
    connection_requirements: List[EnvironmentRequirement] = field(default_factory=list)
    integration_points: List[IntegrationType] = field(default_factory=list)
    health_check_endpoint: Optional[str] = None
    error_handling: List[str] = field(default_factory=list)
    last_registered: Optional[datetime] = None
    active_connections: int = 0
    total_connections: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "endpoint_path": self.endpoint_path,
            "endpoint_name": self.endpoint_name,
            "description": self.description,
            "registration_dependencies": self.registration_dependencies,
            "message_types": self.message_types,
            "authentication_required": self.authentication_required,
            "rate_limiting": self.rate_limiting,
            "connection_requirements": [req.to_dict() for req in self.connection_requirements],
            "integration_points": [point.value for point in self.integration_points],
            "health_check_endpoint": self.health_check_endpoint,
            "error_handling": self.error_handling,
            "last_registered": self.last_registered.isoformat() if self.last_registered else None,
            "active_connections": self.active_connections,
            "total_connections": self.total_connections
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'WebSocketEndpoint':
        """Create from dictionary representation."""
        return cls(
            endpoint_path=data["endpoint_path"],
            endpoint_name=data["endpoint_name"],
            description=data["description"],
            registration_dependencies=data.get("registration_dependencies", []),
            message_types=data.get("message_types", []),
            authentication_required=data.get("authentication_required", False),
            rate_limiting=data.get("rate_limiting"),
            connection_requirements=[EnvironmentRequirement.from_dict(req) for req in data.get("connection_requirements", [])],
            integration_points=[IntegrationType(point) for point in data.get("integration_points", [])],
            health_check_endpoint=data.get("health_check_endpoint"),
            error_handling=data.get("error_handling", []),
            last_registered=datetime.fromisoformat(data["last_registered"]) if data.get("last_registered") else None,
            active_connections=data.get("active_connections", 0),
            total_connections=data.get("total_connections", 0)
        )


@dataclass
class MetricsCollectionPipeline:
    """
    Metrics collection pipeline with dependency mapping.
    
    Represents a metrics collection pipeline with its
    dependencies, data flow, and integration points.
    """
    pipeline_name: str
    description: str
    data_sources: List[str] = field(default_factory=list)
    data_flow: List[str] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)
    integration_points: List[IntegrationType] = field(default_factory=list)
    collection_interval: Optional[str] = None
    retention_policy: Optional[str] = None
    aggregation_rules: List[str] = field(default_factory=list)
    alert_rules: List[str] = field(default_factory=list)
    error_handling: List[str] = field(default_factory=list)
    last_collection: Optional[datetime] = None
    collection_count: int = 0
    success_rate: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "pipeline_name": self.pipeline_name,
            "description": self.description,
            "data_sources": self.data_sources,
            "data_flow": self.data_flow,
            "dependencies": self.dependencies,
            "integration_points": [point.value for point in self.integration_points],
            "collection_interval": self.collection_interval,
            "retention_policy": self.retention_policy,
            "aggregation_rules": self.aggregation_rules,
            "alert_rules": self.alert_rules,
            "error_handling": self.error_handling,
            "last_collection": self.last_collection.isoformat() if self.last_collection else None,
            "collection_count": self.collection_count,
            "success_rate": self.success_rate
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'MetricsCollectionPipeline':
        """Create from dictionary representation."""
        return cls(
            pipeline_name=data["pipeline_name"],
            description=data["description"],
            data_sources=data.get("data_sources", []),
            data_flow=data.get("data_flow", []),
            dependencies=data.get("dependencies", []),
            integration_points=[IntegrationType(point) for point in data.get("integration_points", [])],
            collection_interval=data.get("collection_interval"),
            retention_policy=data.get("retention_policy"),
            aggregation_rules=data.get("aggregation_rules", []),
            alert_rules=data.get("alert_rules", []),
            error_handling=data.get("error_handling", []),
            last_collection=datetime.fromisoformat(data["last_collection"]) if data.get("last_collection") else None,
            collection_count=data.get("collection_count", 0),
            success_rate=data.get("success_rate", 0.0)
        )


@dataclass
class IntegrationPoint:
    """
    Integration point coordination workflow.
    
    Represents an integration point with its coordination
    workflows, dependencies, and health monitoring.
    """
    integration_name: str
    integration_type: IntegrationType
    description: str
    coordination_workflows: List[str] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)
    health_endpoints: List[str] = field(default_factory=list)
    error_handling: List[str] = field(default_factory=list)
    configuration_requirements: List[EnvironmentRequirement] = field(default_factory=list)
    performance_metrics: List[str] = field(default_factory=list)
    last_health_check: Optional[datetime] = None
    health_status: str = "unknown"
    error_count: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "integration_name": self.integration_name,
            "integration_type": self.integration_type.value,
            "description": self.description,
            "coordination_workflows": self.coordination_workflows,
            "dependencies": self.dependencies,
            "health_endpoints": self.health_endpoints,
            "error_handling": self.error_handling,
            "configuration_requirements": [req.to_dict() for req in self.configuration_requirements],
            "performance_metrics": self.performance_metrics,
            "last_health_check": self.last_health_check.isoformat() if self.last_health_check else None,
            "health_status": self.health_status,
            "error_count": self.error_count
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'IntegrationPoint':
        """Create from dictionary representation."""
        return cls(
            integration_name=data["integration_name"],
            integration_type=IntegrationType(data.get("integration_type", "websocket")),
            description=data["description"],
            coordination_workflows=data.get("coordination_workflows", []),
            dependencies=data.get("dependencies", []),
            health_endpoints=data.get("health_endpoints", []),
            error_handling=data.get("error_handling", []),
            configuration_requirements=[EnvironmentRequirement.from_dict(req) for req in data.get("configuration_requirements", [])],
            performance_metrics=data.get("performance_metrics", []),
            last_health_check=datetime.fromisoformat(data["last_health_check"]) if data.get("last_health_check") else None,
            health_status=data.get("health_status", "unknown"),
            error_count=data.get("error_count", 0)
        )


@dataclass
class AutomationDependency:
    """
    Automation dependency relationship.
    
    Represents a dependency relationship between automation
    components with execution order and validation.
    """
    source_component: str
    target_component: str
    dependency_type: DependencyType
    description: str
    execution_order: int
    validation_required: bool = True
    timeout_seconds: Optional[int] = None
    retry_attempts: int = 3
    failure_handling: List[str] = field(default_factory=list)
    success_criteria: List[str] = field(default_factory=list)
    last_validated: Optional[datetime] = None
    validation_status: str = "unknown"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "source_component": self.source_component,
            "target_component": self.target_component,
            "dependency_type": self.dependency_type.value,
            "description": self.description,
            "execution_order": self.execution_order,
            "validation_required": self.validation_required,
            "timeout_seconds": self.timeout_seconds,
            "retry_attempts": self.retry_attempts,
            "failure_handling": self.failure_handling,
            "success_criteria": self.success_criteria,
            "last_validated": self.last_validated.isoformat() if self.last_validated else None,
            "validation_status": self.validation_status
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AutomationDependency':
        """Create from dictionary representation."""
        return cls(
            source_component=data["source_component"],
            target_component=data["target_component"],
            dependency_type=DependencyType(data.get("dependency_type", "makefile_target")),
            description=data["description"],
            execution_order=data["execution_order"],
            validation_required=data.get("validation_required", True),
            timeout_seconds=data.get("timeout_seconds"),
            retry_attempts=data.get("retry_attempts", 3),
            failure_handling=data.get("failure_handling", []),
            success_criteria=data.get("success_criteria", []),
            last_validated=datetime.fromisoformat(data["last_validated"]) if data.get("last_validated") else None,
            validation_status=data.get("validation_status", "unknown")
        )


@dataclass
class AutomationChain:
    """
    Complete automation chain with dependency graph.
    
    Comprehensive automation chain representation including
    all components, dependencies, execution order, and validation.
    """
    chain_name: str
    description: str
    makefile_targets: List[MakefileTarget] = field(default_factory=list)
    python_scripts: List[PythonScript] = field(default_factory=list)
    websocket_endpoints: List[WebSocketEndpoint] = field(default_factory=list)
    metrics_pipelines: List[MetricsCollectionPipeline] = field(default_factory=list)
    integration_points: List[IntegrationPoint] = field(default_factory=list)
    dependencies: List[AutomationDependency] = field(default_factory=list)
    execution_order: List[str] = field(default_factory=list)
    validation_rules: List[str] = field(default_factory=list)
    analysis_timestamp: datetime = field(default_factory=datetime.now)
    chain_version: str = "1.0"
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "chain_name": self.chain_name,
            "description": self.description,
            "makefile_targets": [target.to_dict() for target in self.makefile_targets],
            "python_scripts": [script.to_dict() for script in self.python_scripts],
            "websocket_endpoints": [endpoint.to_dict() for endpoint in self.websocket_endpoints],
            "metrics_pipelines": [pipeline.to_dict() for pipeline in self.metrics_pipelines],
            "integration_points": [point.to_dict() for point in self.integration_points],
            "dependencies": [dep.to_dict() for dep in self.dependencies],
            "execution_order": self.execution_order,
            "validation_rules": self.validation_rules,
            "analysis_timestamp": self.analysis_timestamp.isoformat(),
            "chain_version": self.chain_version,
            "metadata": self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AutomationChain':
        """Create from dictionary representation."""
        return cls(
            chain_name=data["chain_name"],
            description=data["description"],
            makefile_targets=[MakefileTarget.from_dict(target) for target in data.get("makefile_targets", [])],
            python_scripts=[PythonScript.from_dict(script) for script in data.get("python_scripts", [])],
            websocket_endpoints=[WebSocketEndpoint.from_dict(endpoint) for endpoint in data.get("websocket_endpoints", [])],
            metrics_pipelines=[MetricsCollectionPipeline.from_dict(pipeline) for pipeline in data.get("metrics_pipelines", [])],
            integration_points=[IntegrationPoint.from_dict(point) for point in data.get("integration_points", [])],
            dependencies=[AutomationDependency.from_dict(dep) for dep in data.get("dependencies", [])],
            execution_order=data.get("execution_order", []),
            validation_rules=data.get("validation_rules", []),
            analysis_timestamp=datetime.fromisoformat(data.get("analysis_timestamp", datetime.now().isoformat())),
            chain_version=data.get("chain_version", "1.0"),
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
    def from_json(cls, json_data: str) -> 'AutomationChain':
        """Import from JSON format."""
        data = json.loads(json_data)
        return cls.from_dict(data)
    
    @classmethod
    def from_yaml(cls, yaml_data: str) -> 'AutomationChain':
        """Import from YAML format."""
        data = yaml.safe_load(yaml_data)
        return cls.from_dict(data)
    
    @classmethod
    def from_file(cls, file_path: Path) -> 'AutomationChain':
        """Import from file (auto-detect format)."""
        with open(file_path, 'r') as f:
            content = f.read()
        
        if file_path.suffix.lower() == '.json':
            return cls.from_json(content)
        elif file_path.suffix.lower() in ['.yml', '.yaml']:
            return cls.from_yaml(content)
        else:
            raise ValueError(f"Unsupported file format: {file_path.suffix}")
    
    def get_component_by_name(self, name: str) -> Optional[Any]:
        """Get automation component by name."""
        # Check makefile targets
        for target in self.makefile_targets:
            if target.name == name:
                return target
        
        # Check python scripts
        for script in self.python_scripts:
            if script.script_name == name:
                return script
        
        # Check websocket endpoints
        for endpoint in self.websocket_endpoints:
            if endpoint.endpoint_name == name:
                return endpoint
        
        # Check metrics pipelines
        for pipeline in self.metrics_pipelines:
            if pipeline.pipeline_name == name:
                return pipeline
        
        # Check integration points
        for point in self.integration_points:
            if point.integration_name == name:
                return point
        
        return None
    
    def get_dependencies_for_component(self, component_name: str) -> List[AutomationDependency]:
        """Get dependencies for a specific component."""
        return [dep for dep in self.dependencies if dep.target_component == component_name]
    
    def get_dependents_for_component(self, component_name: str) -> List[AutomationDependency]:
        """Get components that depend on a specific component."""
        return [dep for dep in self.dependencies if dep.source_component == component_name]
    
    def validate_execution_order(self) -> List[str]:
        """Validate execution order and return any issues."""
        issues = []
        
        # Check for circular dependencies
        visited = set()
        rec_stack = set()
        
        def has_cycle(component):
            visited.add(component)
            rec_stack.add(component)
            
            for dep in self.get_dependencies_for_component(component):
                target = dep.target_component
                if target not in visited:
                    if has_cycle(target):
                        return True
                elif target in rec_stack:
                    return True
            
            rec_stack.remove(component)
            return False
        
        for target in self.makefile_targets:
            if target.name not in visited:
                if has_cycle(target.name):
                    issues.append(f"Circular dependency detected involving {target.name}")
        
        # Check execution order completeness
        all_components = set()
        for target in self.makefile_targets:
            all_components.add(target.name)
        for script in self.python_scripts:
            all_components.add(script.script_name)
        
        execution_components = set(self.execution_order)
        missing_components = all_components - execution_components
        if missing_components:
            issues.append(f"Components missing from execution order: {missing_components}")
        
        return issues
    
    def get_chain_summary(self) -> Dict[str, Any]:
        """Get comprehensive chain summary."""
        return {
            "chain_name": self.chain_name,
            "analysis_timestamp": self.analysis_timestamp.isoformat(),
            "chain_version": self.chain_version,
            "total_makefile_targets": len(self.makefile_targets),
            "total_python_scripts": len(self.python_scripts),
            "total_websocket_endpoints": len(self.websocket_endpoints),
            "total_metrics_pipelines": len(self.metrics_pipelines),
            "total_integration_points": len(self.integration_points),
            "total_dependencies": len(self.dependencies),
            "execution_order_length": len(self.execution_order),
            "validation_issues": len(self.validate_execution_order()),
            "chain_complexity_score": self._calculate_complexity_score()
        }
    
    def _calculate_complexity_score(self) -> float:
        """Calculate automation chain complexity score."""
        # Simple complexity scoring based on component count and dependencies
        component_count = (
            len(self.makefile_targets) +
            len(self.python_scripts) +
            len(self.websocket_endpoints) +
            len(self.metrics_pipelines) +
            len(self.integration_points)
        )
        
        dependency_count = len(self.dependencies)
        
        # Normalize to 0-100 scale
        complexity = min(100, (component_count * 2) + (dependency_count * 3))
        return complexity