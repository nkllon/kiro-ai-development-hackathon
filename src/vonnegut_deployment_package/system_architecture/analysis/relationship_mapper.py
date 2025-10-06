#!/usr/bin/env python3
"""
Relationship Mapper - DAG-Compliant Dependency Analysis
======================================================

Implements Task 2.1 from the System Architecture Wiring Diagram specification.
Creates RelationshipMapper class with mathematical validation, dependency graph
analysis with cycle detection, DAG Registry integration, and ReflectiveModule
initialization sequence mapping.

Author: Kiro AI Assistant
Created: 2025-01-30
Task: 2.1 - DAG-compliant dependency analysis
Requirements: 2.1, 2.4, 9.1
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional, Set, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import networkx as nx
from collections import defaultdict, deque

from src.rm_ddd.core.unified_reflective_module import (
    ReflectiveModule, 
    ModuleHealth, 
    ModuleStatus, 
    ModuleCapability,
    GracefulDegradationResult
)
from src.rm_ddd.core.dag_registry import DAGRegistry


class DependencyType(Enum):
    """Types of dependencies in the system architecture."""
    INITIALIZATION = "initialization"
    DATA_FLOW = "data_flow"
    SERVICE = "service"
    CONFIGURATION = "configuration"
    NETWORK = "network"
    INTEGRATION = "integration"


class ValidationStatus(Enum):
    """Validation status for dependency relationships."""
    VALID = "valid"
    INVALID = "invalid"
    CIRCULAR = "circular"
    MISSING = "missing"
    DEGRADED = "degraded"


@dataclass
class DependencyRelationship:
    """Represents a dependency relationship between components."""
    source_component: str
    target_component: str
    dependency_type: DependencyType
    required: bool = True
    validation_status: ValidationStatus = ValidationStatus.VALID
    initialization_order: Optional[int] = None
    error_message: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class ComponentNode:
    """Represents a component in the dependency graph."""
    component_id: str
    component_name: str
    component_type: str  # ReflectiveModule, Service, Integration, etc.
    dependencies: Set[str] = field(default_factory=set)
    dependents: Set[str] = field(default_factory=set)
    initialization_sequence: Optional[int] = None
    health_status: str = "unknown"
    reflective_module: bool = False


@dataclass
class DependencyGraph:
    """Complete dependency graph with mathematical validation."""
    nodes: Dict[str, ComponentNode] = field(default_factory=dict)
    edges: List[DependencyRelationship] = field(default_factory=list)
    is_dag: bool = True
    cycles: List[List[str]] = field(default_factory=list)
    topological_order: List[str] = field(default_factory=list)
    validation_errors: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)


class RelationshipMapper(ReflectiveModule):
    """
    RelationshipMapper class with mathematical validation for DAG-compliant
    dependency analysis in the Beast Mode framework.
    
    Implements:
    - Dependency graph analysis with cycle detection
    - DAG Registry integration for dependency validation
    - ReflectiveModule initialization sequence mapping
    - Dependency visualization with validation status
    """
    
    def __init__(self):
        super().__init__()
        self.module_id = "RelationshipMapper"
        self._logger = logging.getLogger(f"system_architecture.{self.__class__.__name__}")
        
        # Core components
        self._dependency_graph: Optional[DependencyGraph] = None
        self._dag_registry = DAGRegistry()
        self._networkx_graph = nx.DiGraph()
        
        # Component registry
        self._components: Dict[str, ComponentNode] = {}
        self._relationships: List[DependencyRelationship] = []
        
        # Mathematical validation state
        self._validation_cache: Dict[str, Any] = {}
        self._last_validation: Optional[datetime] = None
        
        self._logger.info("RelationshipMapper initialized with mathematical validation")
    
    def get_module_info(self) -> Dict[str, Any]:
        """Get module information - RDI Compliant."""
        return {
            "module_id": self.module_id,
            "name": "RelationshipMapper",
            "version": "1.0.0",
            "description": "DAG-compliant dependency analysis with mathematical validation",
            "task": "2.1 - DAG-compliant dependency analysis",
            "capabilities": [cap.value for cap in self.get_capabilities()],
            "components_registered": len(self._components),
            "relationships_mapped": len(self._relationships),
            "last_validation": self._last_validation.isoformat() if self._last_validation else None
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
            # Determine health based on dependency graph state
            if self._dependency_graph is None:
                status = ModuleStatus.WARNING
                health_score = 0.5
                issues = ["No dependency analysis performed yet"]
            elif not self._dependency_graph.is_dag:
                status = ModuleStatus.ERROR
                health_score = 0.2
                issues = [f"Circular dependencies detected: {len(self._dependency_graph.cycles)} cycles"]
            elif len(self._dependency_graph.validation_errors) > 0:
                status = ModuleStatus.WARNING
                health_score = 0.7
                issues = self._dependency_graph.validation_errors[:3]  # First 3 errors
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
                error_count=len(self._dependency_graph.validation_errors) if self._dependency_graph else 0,
                warning_count=0
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
            # In degraded mode, we can still provide basic dependency information
            # but without advanced mathematical validation
            remaining_capabilities = [
                ModuleCapability.CORE_FUNCTIONALITY,
                ModuleCapability.DATA_PROCESSING
            ]
            
            degraded_capabilities = [
                ModuleCapability.VALIDATION,
                ModuleCapability.MONITORING,
                ModuleCapability.API_INTEGRATION
            ]
            
            self._logger.warning("Entering graceful degradation mode")
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
    
    def register_component(self, component_id: str, component_name: str, 
                          component_type: str, reflective_module: bool = False) -> None:
        """Register a component in the dependency graph."""
        
        component = ComponentNode(
            component_id=component_id,
            component_name=component_name,
            component_type=component_type,
            reflective_module=reflective_module
        )
        
        self._components[component_id] = component
        self._networkx_graph.add_node(component_id, **{
            'name': component_name,
            'type': component_type,
            'reflective_module': reflective_module
        })
        
        self._logger.debug(f"Registered component: {component_id} ({component_type})")
    
    def add_dependency(self, source: str, target: str, 
                      dependency_type: DependencyType, required: bool = True) -> bool:
        """
        Add a dependency relationship with mathematical validation.
        
        Returns True if dependency is valid (doesn't create cycles), False otherwise.
        """
        
        # Check if components exist
        if source not in self._components:
            self._logger.error(f"Source component not found: {source}")
            return False
        
        if target not in self._components:
            self._logger.error(f"Target component not found: {target}")
            return False
        
        # Create relationship
        relationship = DependencyRelationship(
            source_component=source,
            target_component=target,
            dependency_type=dependency_type,
            required=required
        )
        
        # Add edge to NetworkX graph for cycle detection
        self._networkx_graph.add_edge(source, target, **{
            'type': dependency_type.value,
            'required': required
        })
        
        # Check for cycles (mathematical validation)
        if not nx.is_directed_acyclic_graph(self._networkx_graph):
            # Cycle detected - remove the edge and mark as invalid
            self._networkx_graph.remove_edge(source, target)
            relationship.validation_status = ValidationStatus.CIRCULAR
            
            # Find the cycle for reporting
            try:
                cycles = list(nx.simple_cycles(self._networkx_graph))
                if cycles:
                    relationship.error_message = f"Would create cycle: {cycles[0]}"
            except Exception:
                relationship.error_message = "Circular dependency detected"
            
            self._logger.warning(f"Circular dependency detected: {source} -> {target}")
            return False
        
        # Valid dependency - update component relationships
        self._components[source].dependencies.add(target)
        self._components[target].dependents.add(source)
        
        # Store relationship
        self._relationships.append(relationship)
        
        # Integrate with DAG Registry
        self._integrate_with_dag_registry(relationship)
        
        self._logger.info(f"Added dependency: {source} -> {target} ({dependency_type.value})")
        return True
    
    def _integrate_with_dag_registry(self, relationship: DependencyRelationship) -> None:
        """Integrate dependency with DAG Registry for validation."""
        try:
            # Register the dependency in the DAG Registry
            self._dag_registry.register_dependency(
                source=relationship.source_component,
                target=relationship.target_component,
                dependency_type=relationship.dependency_type.value
            )
            
            # Validate against DAG Registry constraints
            validation_result = self._dag_registry.validate_dependency(
                relationship.source_component,
                relationship.target_component
            )
            
            if not validation_result.get('valid', True):
                relationship.validation_status = ValidationStatus.INVALID
                relationship.error_message = validation_result.get('error', 'DAG Registry validation failed')
                
        except Exception as e:
            self._logger.warning(f"DAG Registry integration failed: {e}")
            # Continue without DAG Registry integration
    
    def analyze_dependency_graph(self) -> DependencyGraph:
        """
        Perform comprehensive dependency graph analysis with mathematical validation.
        """
        self._logger.info("Starting dependency graph analysis...")
        
        # Create dependency graph
        graph = DependencyGraph(
            nodes=self._components.copy(),
            edges=self._relationships.copy()
        )
        
        # Mathematical validation: Check if graph is a DAG
        graph.is_dag = nx.is_directed_acyclic_graph(self._networkx_graph)
        
        if not graph.is_dag:
            # Find all cycles
            try:
                graph.cycles = list(nx.simple_cycles(self._networkx_graph))
                graph.validation_errors.append(f"Circular dependencies detected: {len(graph.cycles)} cycles")
            except Exception as e:
                graph.validation_errors.append(f"Cycle detection failed: {e}")
        
        # Generate topological ordering (initialization sequence)
        if graph.is_dag:
            try:
                graph.topological_order = list(nx.topological_sort(self._networkx_graph))
                
                # Assign initialization sequence numbers
                for i, component_id in enumerate(graph.topological_order):
                    if component_id in graph.nodes:
                        graph.nodes[component_id].initialization_sequence = i
                        
            except Exception as e:
                graph.validation_errors.append(f"Topological sort failed: {e}")
        
        # Validate ReflectiveModule initialization sequences
        self._validate_reflective_module_sequences(graph)
        
        # Store the graph
        self._dependency_graph = graph
        self._last_validation = datetime.now()
        
        self._logger.info(f"Dependency graph analysis completed: DAG={graph.is_dag}, "
                         f"Nodes={len(graph.nodes)}, Edges={len(graph.edges)}")
        
        return graph
    
    def _validate_reflective_module_sequences(self, graph: DependencyGraph) -> None:
        """Validate ReflectiveModule initialization sequences."""
        
        reflective_modules = [
            (node_id, node) for node_id, node in graph.nodes.items()
            if node.reflective_module
        ]
        
        if not reflective_modules:
            return
        
        # Check that ReflectiveModules have proper initialization order
        for node_id, node in reflective_modules:
            if node.initialization_sequence is None:
                graph.validation_errors.append(
                    f"ReflectiveModule {node_id} missing initialization sequence"
                )
            
            # Validate dependencies are initialized first
            for dep_id in node.dependencies:
                if dep_id in graph.nodes:
                    dep_node = graph.nodes[dep_id]
                    if (dep_node.initialization_sequence is not None and 
                        node.initialization_sequence is not None and
                        dep_node.initialization_sequence >= node.initialization_sequence):
                        
                        graph.validation_errors.append(
                            f"ReflectiveModule {node_id} initialization order conflict with {dep_id}"
                        )
    
    def map_reflective_module_initialization_sequences(self) -> Dict[str, int]:
        """
        Map ReflectiveModule initialization sequences based on dependency analysis.
        
        Returns a dictionary mapping component IDs to initialization order.
        """
        
        if not self._dependency_graph:
            self.analyze_dependency_graph()
        
        sequences = {}
        
        for component_id, component in self._dependency_graph.nodes.items():
            if component.reflective_module and component.initialization_sequence is not None:
                sequences[component_id] = component.initialization_sequence
        
        self._logger.info(f"Mapped {len(sequences)} ReflectiveModule initialization sequences")
        return sequences
    
    def detect_cycles(self) -> List[List[str]]:
        """Detect cycles in the dependency graph using mathematical algorithms."""
        
        try:
            cycles = list(nx.simple_cycles(self._networkx_graph))
            
            if cycles:
                self._logger.warning(f"Detected {len(cycles)} cycles in dependency graph")
                for i, cycle in enumerate(cycles):
                    self._logger.warning(f"Cycle {i+1}: {' -> '.join(cycle + [cycle[0]])}")
            
            return cycles
            
        except Exception as e:
            self._logger.error(f"Cycle detection failed: {e}")
            return []
    
    def get_dependency_visualization_data(self) -> Dict[str, Any]:
        """
        Generate data for dependency visualization with validation status.
        """
        
        if not self._dependency_graph:
            self.analyze_dependency_graph()
        
        # Prepare nodes for visualization
        nodes = []
        for component_id, component in self._dependency_graph.nodes.items():
            node_data = {
                'id': component_id,
                'name': component.component_name,
                'type': component.component_type,
                'reflective_module': component.reflective_module,
                'initialization_sequence': component.initialization_sequence,
                'health_status': component.health_status,
                'dependencies_count': len(component.dependencies),
                'dependents_count': len(component.dependents)
            }
            nodes.append(node_data)
        
        # Prepare edges for visualization
        edges = []
        for relationship in self._dependency_graph.edges:
            edge_data = {
                'source': relationship.source_component,
                'target': relationship.target_component,
                'type': relationship.dependency_type.value,
                'required': relationship.required,
                'status': relationship.validation_status.value,
                'error': relationship.error_message
            }
            edges.append(edge_data)
        
        # Graph statistics
        stats = {
            'total_nodes': len(nodes),
            'total_edges': len(edges),
            'is_dag': self._dependency_graph.is_dag,
            'cycles_count': len(self._dependency_graph.cycles),
            'reflective_modules_count': len([n for n in nodes if n['reflective_module']]),
            'validation_errors': self._dependency_graph.validation_errors
        }
        
        visualization_data = {
            'nodes': nodes,
            'edges': edges,
            'statistics': stats,
            'topological_order': self._dependency_graph.topological_order,
            'cycles': self._dependency_graph.cycles,
            'generated_at': datetime.now().isoformat()
        }
        
        self._logger.info("Generated dependency visualization data")
        return visualization_data
    
    def validate_system_dependencies(self) -> Dict[str, Any]:
        """
        Comprehensive validation of system dependencies with mathematical guarantees.
        """
        
        validation_report = {
            'validation_timestamp': datetime.now().isoformat(),
            'overall_status': 'unknown',
            'mathematical_validation': {},
            'dag_compliance': {},
            'reflective_module_validation': {},
            'recommendations': []
        }
        
        # Perform dependency analysis if not done
        if not self._dependency_graph:
            self.analyze_dependency_graph()
        
        # Mathematical validation
        validation_report['mathematical_validation'] = {
            'is_dag': self._dependency_graph.is_dag,
            'node_count': len(self._dependency_graph.nodes),
            'edge_count': len(self._dependency_graph.edges),
            'cycles_detected': len(self._dependency_graph.cycles),
            'topological_sort_possible': bool(self._dependency_graph.topological_order),
            'validation_errors': self._dependency_graph.validation_errors
        }
        
        # DAG compliance validation
        validation_report['dag_compliance'] = {
            'compliant': self._dependency_graph.is_dag and len(self._dependency_graph.validation_errors) == 0,
            'cycles': self._dependency_graph.cycles,
            'initialization_order_valid': len(self._dependency_graph.topological_order) > 0
        }
        
        # ReflectiveModule validation
        reflective_modules = [
            node for node in self._dependency_graph.nodes.values()
            if node.reflective_module
        ]
        
        validation_report['reflective_module_validation'] = {
            'total_reflective_modules': len(reflective_modules),
            'properly_sequenced': len([rm for rm in reflective_modules if rm.initialization_sequence is not None]),
            'sequence_conflicts': len([
                error for error in self._dependency_graph.validation_errors
                if 'ReflectiveModule' in error and 'initialization order conflict' in error
            ])
        }
        
        # Determine overall status
        if (validation_report['dag_compliance']['compliant'] and 
            validation_report['reflective_module_validation']['sequence_conflicts'] == 0):
            validation_report['overall_status'] = 'valid'
        elif self._dependency_graph.is_dag:
            validation_report['overall_status'] = 'warning'
        else:
            validation_report['overall_status'] = 'invalid'
        
        # Generate recommendations
        if not self._dependency_graph.is_dag:
            validation_report['recommendations'].append(
                "Resolve circular dependencies to ensure proper initialization order"
            )
        
        if validation_report['reflective_module_validation']['sequence_conflicts'] > 0:
            validation_report['recommendations'].append(
                "Fix ReflectiveModule initialization sequence conflicts"
            )
        
        if len(reflective_modules) == 0:
            validation_report['recommendations'].append(
                "Consider using ReflectiveModule pattern for systematic observability"
            )
        
        self._logger.info(f"System dependency validation completed: {validation_report['overall_status']}")
        return validation_report
    
    def get_initialization_plan(self) -> List[Dict[str, Any]]:
        """
        Generate a systematic initialization plan based on dependency analysis.
        """
        
        if not self._dependency_graph or not self._dependency_graph.topological_order:
            self.analyze_dependency_graph()
        
        if not self._dependency_graph.topological_order:
            self._logger.error("Cannot generate initialization plan: graph contains cycles")
            return []
        
        initialization_plan = []
        
        for i, component_id in enumerate(self._dependency_graph.topological_order):
            if component_id in self._dependency_graph.nodes:
                component = self._dependency_graph.nodes[component_id]
                
                step = {
                    'sequence': i,
                    'component_id': component_id,
                    'component_name': component.component_name,
                    'component_type': component.component_type,
                    'reflective_module': component.reflective_module,
                    'dependencies': list(component.dependencies),
                    'initialization_method': self._get_initialization_method(component),
                    'validation_checks': self._get_validation_checks(component),
                    'rollback_procedure': self._get_rollback_procedure(component)
                }
                
                initialization_plan.append(step)
        
        self._logger.info(f"Generated initialization plan with {len(initialization_plan)} steps")
        return initialization_plan
    
    def _get_initialization_method(self, component: ComponentNode) -> str:
        """Get the appropriate initialization method for a component."""
        
        if component.reflective_module:
            return "ReflectiveModule.__init__() with health endpoint registration"
        elif component.component_type == "Service":
            return "Service startup with health check validation"
        elif component.component_type == "Integration":
            return "Integration point establishment with connectivity validation"
        else:
            return "Standard component initialization"
    
    def _get_validation_checks(self, component: ComponentNode) -> List[str]:
        """Get validation checks for component initialization."""
        
        checks = ["Component startup successful"]
        
        if component.reflective_module:
            checks.extend([
                "Health endpoint responding",
                "Metrics registration completed",
                "ReflectiveModule capabilities available"
            ])
        
        if component.dependencies:
            checks.append("All dependencies available and healthy")
        
        return checks
    
    def _get_rollback_procedure(self, component: ComponentNode) -> List[str]:
        """Get rollback procedure for component initialization failure."""
        
        procedures = ["Stop component gracefully"]
        
        if component.reflective_module:
            procedures.extend([
                "Unregister health endpoints",
                "Clean up metrics registration",
                "Release ReflectiveModule resources"
            ])
        
        if component.dependents:
            procedures.append("Notify dependent components of unavailability")
        
        return procedures


# Factory function for easy instantiation
def create_relationship_mapper() -> RelationshipMapper:
    """Create and return a configured RelationshipMapper instance."""
    return RelationshipMapper()


# Example usage and testing
async def demonstrate_relationship_mapper():
    """Demonstrate RelationshipMapper capabilities."""
    
    mapper = create_relationship_mapper()
    
    # Register Beast Mode framework components
    mapper.register_component("observatory", "Observatory Server", "ReflectiveModule", reflective_module=True)
    mapper.register_component("prometheus", "Prometheus Metrics", "Service")
    mapper.register_component("grafana", "Grafana Dashboard", "Service")
    mapper.register_component("redis", "Redis Coordination", "Service")
    mapper.register_component("dag_registry", "DAG Registry", "ReflectiveModule", reflective_module=True)
    
    # Add dependencies
    mapper.add_dependency("observatory", "redis", DependencyType.SERVICE)
    mapper.add_dependency("prometheus", "observatory", DependencyType.DATA_FLOW)
    mapper.add_dependency("grafana", "prometheus", DependencyType.DATA_FLOW)
    mapper.add_dependency("dag_registry", "redis", DependencyType.SERVICE)
    
    # Analyze dependencies
    graph = mapper.analyze_dependency_graph()
    
    # Generate reports
    validation_report = mapper.validate_system_dependencies()
    initialization_plan = mapper.get_initialization_plan()
    visualization_data = mapper.get_dependency_visualization_data()
    
    print("🐺 RelationshipMapper Demonstration Complete!")
    print(f"DAG Compliant: {graph.is_dag}")
    print(f"Components: {len(graph.nodes)}")
    print(f"Dependencies: {len(graph.edges)}")
    print(f"Initialization Steps: {len(initialization_plan)}")
    
    return {
        'graph': graph,
        'validation': validation_report,
        'initialization_plan': initialization_plan,
        'visualization': visualization_data
    }


if __name__ == "__main__":
    # Run demonstration
    asyncio.run(demonstrate_relationship_mapper())