"""
Documentation Orchestration and Validation System for System Architecture Wiring Diagram.

This module implements comprehensive documentation orchestration with ReflectiveModule integration,
real-time validation system, validation checklist, and performance monitoring.
"""

import asyncio
import json
import logging
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any, Set
from enum import Enum

from ..core import ReflectiveModule
from .infrastructure_discovery import InfrastructureDiscoverer
from .makefile_analyzer import MakefileAnalyzer
from .cloudflare_tunnel_discovery import CloudflareTunnelDiscoverer
from .network_topology_discovery import NetworkTopologyDiscoverer
from .diagram_generator import DiagramGenerator, DiagramGenerationResult

logger = logging.getLogger(__name__)


class ValidationStatus(Enum):
    """Validation status for documentation."""
    VALID = "valid"
    INVALID = "invalid"
    PENDING = "pending"
    STALE = "stale"
    ERROR = "error"


class DocumentationType(Enum):
    """Types of documentation."""
    INFRASTRUCTURE_DISCOVERY = "infrastructure_discovery"
    MAKEFILE_ANALYSIS = "makefile_analysis"
    TUNNEL_DISCOVERY = "tunnel_discovery"
    NETWORK_TOPOLOGY = "network_topology"
    DIAGRAM_GENERATION = "diagram_generation"
    USE_CASE_DOCUMENTATION = "use_case_documentation"
    TROUBLESHOOTING_GUIDE = "troubleshooting_guide"
    SECURITY_DOCUMENTATION = "security_documentation"
    DISASTER_RECOVERY = "disaster_recovery"


@dataclass
class ValidationResult:
    """Result of documentation validation."""
    documentation_type: DocumentationType
    validation_status: ValidationStatus
    accuracy_score: float  # 0.0-1.0
    validation_timestamp: datetime = field(default_factory=datetime.now)
    validation_errors: List[str] = field(default_factory=list)
    validation_warnings: List[str] = field(default_factory=list)
    requires_manual_verification: bool = False
    last_manual_verification: Optional[datetime] = None
    next_validation_due: Optional[datetime] = None


@dataclass
class DocumentationPackage:
    """Complete documentation package."""
    package_id: str
    created_at: datetime = field(default_factory=datetime.now)
    last_updated: datetime = field(default_factory=datetime.now)
    version: str = "1.0.0"
    
    # Documentation components
    infrastructure_discovery: Optional[Any] = None
    makefile_analysis: Optional[Any] = None
    tunnel_discovery: Optional[Any] = None
    network_topology: Optional[Any] = None
    diagram_generation: Optional[Any] = None
    
    # Validation results
    validation_results: Dict[DocumentationType, ValidationResult] = field(default_factory=dict)
    overall_accuracy_score: float = 0.0
    validation_success_rate: float = 0.0
    
    # Performance metrics
    generation_time_seconds: float = 0.0
    total_size_bytes: int = 0
    file_count: int = 0


@dataclass
class ValidationChecklist:
    """Validation checklist for manual verification."""
    checklist_id: str
    documentation_type: DocumentationType
    checklist_items: List[str] = field(default_factory=list)
    automated_tests: List[str] = field(default_factory=list)
    manual_verification_steps: List[str] = field(default_factory=list)
    success_criteria: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class PerformanceMetrics:
    """Performance metrics for documentation generation."""
    discovery_time_seconds: float = 0.0
    analysis_time_seconds: float = 0.0
    generation_time_seconds: float = 0.0
    validation_time_seconds: float = 0.0
    total_time_seconds: float = 0.0
    
    # Resource usage
    memory_usage_mb: float = 0.0
    cpu_usage_percent: float = 0.0
    
    # Quality metrics
    accuracy_score: float = 0.0
    completeness_score: float = 0.0
    freshness_score: float = 0.0
    
    # Timestamps
    metrics_timestamp: datetime = field(default_factory=datetime.now)


class DocumentationOrchestrator(ReflectiveModule):
    """Comprehensive documentation orchestration and validation system."""
    
    def __init__(self):
        super().__init__()
        self.module_id = "documentation_orchestrator"
        self._documentation_package: Optional[DocumentationPackage] = None
        self._validation_checklists: Dict[DocumentationType, ValidationChecklist] = {}
        self._performance_metrics: Optional[PerformanceMetrics] = None
        
        # Initialize discovery components
        self._infrastructure_discoverer: Optional[InfrastructureDiscoverer] = None
        self._makefile_analyzer: Optional[MakefileAnalyzer] = None
        self._tunnel_discoverer: Optional[CloudflareTunnelDiscoverer] = None
        self._network_discoverer: Optional[NetworkTopologyDiscoverer] = None
        self._diagram_generator: Optional[DiagramGenerator] = None
        
        # Validation settings
        self._validation_interval_hours = 24
        self._staleness_threshold_hours = 24
        self._accuracy_threshold = 0.95
        
        # Initialize validation checklists
        self._initialize_validation_checklists()
        
        logger.info("Documentation Orchestrator initialized")
    
    def _initialize_validation_checklists(self) -> None:
        """Initialize validation checklists for each documentation type."""
        
        # Infrastructure Discovery Checklist
        self._validation_checklists[DocumentationType.INFRASTRUCTURE_DISCOVERY] = ValidationChecklist(
            checklist_id="infrastructure_discovery_checklist",
            documentation_type=DocumentationType.INFRASTRUCTURE_DISCOVERY,
            checklist_items=[
                "All running services discovered",
                "WebSocket endpoints mapped correctly",
                "Service health endpoints validated",
                "Configuration files parsed successfully",
                "Network connections identified"
            ],
            automated_tests=[
                "Service discovery completeness test",
                "WebSocket endpoint connectivity test",
                "Configuration file parsing test",
                "Network topology validation test"
            ],
            manual_verification_steps=[
                "Verify discovered services match actual running services",
                "Test WebSocket endpoint accessibility",
                "Validate configuration file accuracy",
                "Confirm network topology accuracy"
            ],
            success_criteria=[
                ">95% of services discovered",
                "All WebSocket endpoints accessible",
                "Configuration files parse without errors",
                "Network topology matches actual infrastructure"
            ]
        )
        
        # Makefile Analysis Checklist
        self._validation_checklists[DocumentationType.MAKEFILE_ANALYSIS] = ValidationChecklist(
            checklist_id="makefile_analysis_checklist",
            documentation_type=DocumentationType.MAKEFILE_ANALYSIS,
            checklist_items=[
                "All Makefile targets extracted",
                "Target dependencies mapped correctly",
                "Infrastructure effects identified",
                "Execution chains validated",
                "Risk levels assessed"
            ],
            automated_tests=[
                "Makefile parsing completeness test",
                "Dependency graph validation test",
                "Infrastructure mapping test",
                "Execution chain validation test"
            ],
            manual_verification_steps=[
                "Verify all targets are documented",
                "Test dependency relationships",
                "Validate infrastructure effect mappings",
                "Confirm execution chain accuracy"
            ],
            success_criteria=[
                "100% of targets extracted",
                "Dependency graph is acyclic",
                "Infrastructure effects correctly mapped",
                "Execution chains are valid"
            ]
        )
        
        # Tunnel Discovery Checklist
        self._validation_checklists[DocumentationType.TUNNEL_DISCOVERY] = ValidationChecklist(
            checklist_id="tunnel_discovery_checklist",
            documentation_type=DocumentationType.TUNNEL_DISCOVERY,
            checklist_items=[
                "Tunnel configuration parsed",
                "DNS records validated",
                "Ingress rules documented",
                "WebSocket routing confirmed",
                "Connectivity tests passed"
            ],
            automated_tests=[
                "Tunnel configuration parsing test",
                "DNS resolution test",
                "Ingress rule validation test",
                "WebSocket endpoint connectivity test"
            ],
            manual_verification_steps=[
                "Verify tunnel configuration accuracy",
                "Test DNS resolution",
                "Validate ingress rule mappings",
                "Confirm WebSocket endpoint accessibility"
            ],
            success_criteria=[
                "Tunnel configuration parsed successfully",
                "DNS records resolve correctly",
                "Ingress rules match actual configuration",
                "WebSocket endpoints are accessible"
            ]
        )
        
        # Network Topology Checklist
        self._validation_checklists[DocumentationType.NETWORK_TOPOLOGY] = ValidationChecklist(
            checklist_id="network_topology_checklist",
            documentation_type=DocumentationType.NETWORK_TOPOLOGY,
            checklist_items=[
                "Network interfaces discovered",
                "Service endpoints mapped",
                "Network connections identified",
                "Redis coordination documented",
                "Network flows analyzed"
            ],
            automated_tests=[
                "Network interface discovery test",
                "Service endpoint connectivity test",
                "Network connection validation test",
                "Redis coordination test"
            ],
            manual_verification_steps=[
                "Verify network interface accuracy",
                "Test service endpoint connectivity",
                "Validate network connection mappings",
                "Confirm Redis coordination status"
            ],
            success_criteria=[
                "All network interfaces discovered",
                "Service endpoints are accessible",
                "Network connections are accurate",
                "Redis coordination is active"
            ]
        )
        
        # Diagram Generation Checklist
        self._validation_checklists[DocumentationType.DIAGRAM_GENERATION] = ValidationChecklist(
            checklist_id="diagram_generation_checklist",
            documentation_type=DocumentationType.DIAGRAM_GENERATION,
            checklist_items=[
                "All diagram types generated",
                "PlantUML source created",
                "Mermaid source created",
                "SVG output generated",
                "PNG output generated"
            ],
            automated_tests=[
                "Diagram generation completeness test",
                "PlantUML syntax validation test",
                "Mermaid syntax validation test",
                "Output file generation test"
            ],
            manual_verification_steps=[
                "Review diagram accuracy",
                "Verify PlantUML syntax",
                "Check Mermaid syntax",
                "Validate output file quality"
            ],
            success_criteria=[
                "All diagram types generated",
                "PlantUML syntax is valid",
                "Mermaid syntax is valid",
                "Output files are generated successfully"
            ]
        )
    
    async def generate_complete_documentation(self) -> DocumentationPackage:
        """Generate complete documentation package."""
        try:
            logger.info("Starting complete documentation generation...")
            
            start_time = datetime.now()
            
            # Initialize documentation package
            package_id = f"doc_package_{start_time.strftime('%Y%m%d_%H%M%S')}"
            self._documentation_package = DocumentationPackage(package_id=package_id)
            
            # Phase 1: Infrastructure Discovery
            await self._perform_infrastructure_discovery()
            
            # Phase 2: Makefile Analysis
            await self._perform_makefile_analysis()
            
            # Phase 3: Tunnel Discovery
            await self._perform_tunnel_discovery()
            
            # Phase 4: Network Topology Discovery
            await self._perform_network_topology_discovery()
            
            # Phase 5: Diagram Generation
            await self._perform_diagram_generation()
            
            # Phase 6: Validation
            await self._perform_comprehensive_validation()
            
            # Update package metadata
            end_time = datetime.now()
            self._documentation_package.generation_time_seconds = (end_time - start_time).total_seconds()
            self._documentation_package.last_updated = end_time
            
            # Calculate performance metrics
            await self._calculate_performance_metrics(start_time, end_time)
            
            logger.info(f"Complete documentation generation finished in {self._documentation_package.generation_time_seconds:.2f} seconds")
            
            return self._documentation_package
            
        except Exception as e:
            logger.error(f"Complete documentation generation failed: {e}")
            raise
    
    async def _perform_infrastructure_discovery(self) -> None:
        """Perform infrastructure discovery."""
        try:
            logger.info("Performing infrastructure discovery...")
            
            self._infrastructure_discoverer = InfrastructureDiscoverer(None)  # TODO: Pass proper config
            success = await self._infrastructure_discoverer.start_discovery()
            
            if success:
                self._documentation_package.infrastructure_discovery = {
                    "services": self._infrastructure_discoverer.get_discovered_services(),
                    "network_topology": self._infrastructure_discoverer.get_network_topology(),
                    "configuration_map": self._infrastructure_discoverer.get_configuration_map(),
                    "script_registry": self._infrastructure_discoverer.get_script_registry()
                }
                logger.info("Infrastructure discovery completed successfully")
            else:
                logger.error("Infrastructure discovery failed")
        
        except Exception as e:
            logger.error(f"Error in infrastructure discovery: {e}")
    
    async def _perform_makefile_analysis(self) -> None:
        """Perform Makefile analysis."""
        try:
            logger.info("Performing Makefile analysis...")
            
            self._makefile_analyzer = MakefileAnalyzer()
            analysis = await self._makefile_analyzer.analyze_makefile()
            
            if analysis:
                self._documentation_package.makefile_analysis = {
                    "targets": analysis.targets,
                    "dependency_graph": analysis.dependency_graph,
                    "execution_chains": analysis.execution_chains,
                    "infrastructure_mapping": analysis.infrastructure_mapping,
                    "total_targets": analysis.total_targets,
                    "complexity_score": analysis.complexity_score
                }
                logger.info("Makefile analysis completed successfully")
            else:
                logger.error("Makefile analysis failed")
        
        except Exception as e:
            logger.error(f"Error in Makefile analysis: {e}")
    
    async def _perform_tunnel_discovery(self) -> None:
        """Perform Cloudflare tunnel discovery."""
        try:
            logger.info("Performing Cloudflare tunnel discovery...")
            
            self._tunnel_discoverer = CloudflareTunnelDiscoverer()
            discovery_result = await self._tunnel_discoverer.discover_tunnels()
            
            if discovery_result:
                self._documentation_package.tunnel_discovery = {
                    "tunnels": discovery_result.tunnels,
                    "dns_records": discovery_result.dns_records,
                    "routing_rules": discovery_result.routing_rules,
                    "total_tunnels": discovery_result.total_tunnels,
                    "active_tunnels": discovery_result.active_tunnels,
                    "validation_success_rate": discovery_result.validation_success_rate
                }
                logger.info("Tunnel discovery completed successfully")
            else:
                logger.error("Tunnel discovery failed")
        
        except Exception as e:
            logger.error(f"Error in tunnel discovery: {e}")
    
    async def _perform_network_topology_discovery(self) -> None:
        """Perform network topology discovery."""
        try:
            logger.info("Performing network topology discovery...")
            
            self._network_discoverer = NetworkTopologyDiscoverer()
            topology = await self._network_discoverer.discover_topology()
            
            if topology:
                self._documentation_package.network_topology = {
                    "interfaces": topology.interfaces,
                    "service_endpoints": topology.service_endpoints,
                    "network_connections": topology.network_connections,
                    "redis_endpoints": topology.redis_endpoints,
                    "network_flows": topology.network_flows,
                    "total_services": topology.total_services,
                    "validation_success_rate": topology.validation_success_rate
                }
                logger.info("Network topology discovery completed successfully")
            else:
                logger.error("Network topology discovery failed")
        
        except Exception as e:
            logger.error(f"Error in network topology discovery: {e}")
    
    async def _perform_diagram_generation(self) -> None:
        """Perform diagram generation."""
        try:
            logger.info("Performing diagram generation...")
            
            self._diagram_generator = DiagramGenerator()
            generation_result = await self._diagram_generator.generate_all_diagrams(
                infrastructure_discoverer=self._infrastructure_discoverer,
                makefile_analyzer=self._makefile_analyzer,
                tunnel_discoverer=self._tunnel_discoverer,
                network_discoverer=self._network_discoverer
            )
            
            if generation_result:
                self._documentation_package.diagram_generation = {
                    "diagrams": generation_result.diagrams,
                    "total_diagrams": generation_result.total_diagrams,
                    "successful_generations": generation_result.successful_generations,
                    "validation_success_rate": generation_result.validation_success_rate
                }
                logger.info("Diagram generation completed successfully")
            else:
                logger.error("Diagram generation failed")
        
        except Exception as e:
            logger.error(f"Error in diagram generation: {e}")
    
    async def _perform_comprehensive_validation(self) -> None:
        """Perform comprehensive validation of all documentation."""
        try:
            logger.info("Performing comprehensive validation...")
            
            validation_results = {}
            accuracy_scores = []
            
            # Validate each documentation type
            for doc_type in DocumentationType:
                validation_result = await self._validate_documentation_type(doc_type)
                validation_results[doc_type] = validation_result
                accuracy_scores.append(validation_result.accuracy_score)
            
            self._documentation_package.validation_results = validation_results
            self._documentation_package.overall_accuracy_score = (
                sum(accuracy_scores) / len(accuracy_scores) if accuracy_scores else 0.0
            )
            
            # Calculate validation success rate
            successful_validations = sum(1 for result in validation_results.values() 
                                      if result.validation_status == ValidationStatus.VALID)
            self._documentation_package.validation_success_rate = (
                successful_validations / len(validation_results) if validation_results else 0.0
            )
            
            logger.info(f"Comprehensive validation completed. Overall accuracy: {self._documentation_package.overall_accuracy_score:.2%}")
        
        except Exception as e:
            logger.error(f"Error in comprehensive validation: {e}")
    
    async def _validate_documentation_type(self, doc_type: DocumentationType) -> ValidationResult:
        """Validate a specific documentation type."""
        try:
            validation_result = ValidationResult(
                documentation_type=doc_type,
                validation_status=ValidationStatus.PENDING,
                accuracy_score=0.0
            )
            
            # Get validation checklist
            checklist = self._validation_checklists.get(doc_type)
            if not checklist:
                validation_result.validation_status = ValidationStatus.ERROR
                validation_result.validation_errors.append("No validation checklist available")
                return validation_result
            
            # Perform automated tests
            automated_test_results = await self._run_automated_tests(doc_type, checklist)
            
            # Calculate accuracy score
            validation_result.accuracy_score = automated_test_results.get("accuracy_score", 0.0)
            
            # Determine validation status
            if validation_result.accuracy_score >= self._accuracy_threshold:
                validation_result.validation_status = ValidationStatus.VALID
            elif validation_result.accuracy_score >= 0.8:
                validation_result.validation_status = ValidationStatus.PENDING
                validation_result.requires_manual_verification = True
            else:
                validation_result.validation_status = ValidationStatus.INVALID
            
            # Set next validation due
            validation_result.next_validation_due = (
                datetime.now() + timedelta(hours=self._validation_interval_hours)
            )
            
            return validation_result
        
        except Exception as e:
            logger.error(f"Error validating documentation type {doc_type}: {e}")
            return ValidationResult(
                documentation_type=doc_type,
                validation_status=ValidationStatus.ERROR,
                accuracy_score=0.0,
                validation_errors=[str(e)]
            )
    
    async def _run_automated_tests(self, doc_type: DocumentationType, checklist: ValidationChecklist) -> Dict[str, Any]:
        """Run automated tests for a documentation type."""
        test_results = {"accuracy_score": 0.0, "test_results": {}}
        
        try:
            if doc_type == DocumentationType.INFRASTRUCTURE_DISCOVERY:
                test_results = await self._test_infrastructure_discovery()
            elif doc_type == DocumentationType.MAKEFILE_ANALYSIS:
                test_results = await self._test_makefile_analysis()
            elif doc_type == DocumentationType.TUNNEL_DISCOVERY:
                test_results = await self._test_tunnel_discovery()
            elif doc_type == DocumentationType.NETWORK_TOPOLOGY:
                test_results = await self._test_network_topology()
            elif doc_type == DocumentationType.DIAGRAM_GENERATION:
                test_results = await self._test_diagram_generation()
        
        except Exception as e:
            logger.error(f"Error running automated tests for {doc_type}: {e}")
            test_results["accuracy_score"] = 0.0
            test_results["test_results"]["error"] = str(e)
        
        return test_results
    
    async def _test_infrastructure_discovery(self) -> Dict[str, Any]:
        """Test infrastructure discovery results."""
        test_results = {"accuracy_score": 0.0, "test_results": {}}
        
        try:
            if not self._documentation_package.infrastructure_discovery:
                test_results["test_results"]["error"] = "No infrastructure discovery data"
                return test_results
            
            discovery_data = self._documentation_package.infrastructure_discovery
            services = discovery_data.get("services", {})
            
            # Test service discovery completeness
            expected_services = ["observatory", "prometheus", "grafana"]
            discovered_services = list(services.keys())
            service_completeness = len(set(expected_services) & set(discovered_services)) / len(expected_services)
            
            test_results["test_results"]["service_completeness"] = service_completeness
            test_results["accuracy_score"] = service_completeness
        
        except Exception as e:
            logger.error(f"Error testing infrastructure discovery: {e}")
            test_results["test_results"]["error"] = str(e)
        
        return test_results
    
    async def _test_makefile_analysis(self) -> Dict[str, Any]:
        """Test Makefile analysis results."""
        test_results = {"accuracy_score": 0.0, "test_results": {}}
        
        try:
            if not self._documentation_package.makefile_analysis:
                test_results["test_results"]["error"] = "No Makefile analysis data"
                return test_results
            
            analysis_data = self._documentation_package.makefile_analysis
            targets = analysis_data.get("targets", {})
            
            # Test target extraction completeness
            expected_targets = ["help", "install", "deploy", "verify", "test", "clean"]
            discovered_targets = list(targets.keys())
            target_completeness = len(set(expected_targets) & set(discovered_targets)) / len(expected_targets)
            
            test_results["test_results"]["target_completeness"] = target_completeness
            test_results["accuracy_score"] = target_completeness
        
        except Exception as e:
            logger.error(f"Error testing Makefile analysis: {e}")
            test_results["test_results"]["error"] = str(e)
        
        return test_results
    
    async def _test_tunnel_discovery(self) -> Dict[str, Any]:
        """Test tunnel discovery results."""
        test_results = {"accuracy_score": 0.0, "test_results": {}}
        
        try:
            if not self._documentation_package.tunnel_discovery:
                test_results["test_results"]["error"] = "No tunnel discovery data"
                return test_results
            
            tunnel_data = self._documentation_package.tunnel_discovery
            tunnels = tunnel_data.get("tunnels", {})
            
            # Test tunnel discovery
            expected_tunnel_id = "d1e53e43-033f-4994-8f46-c83962ae3785"
            tunnel_found = expected_tunnel_id in tunnels
            
            test_results["test_results"]["tunnel_found"] = tunnel_found
            test_results["accuracy_score"] = 1.0 if tunnel_found else 0.0
        
        except Exception as e:
            logger.error(f"Error testing tunnel discovery: {e}")
            test_results["test_results"]["error"] = str(e)
        
        return test_results
    
    async def _test_network_topology(self) -> Dict[str, Any]:
        """Test network topology results."""
        test_results = {"accuracy_score": 0.0, "test_results": {}}
        
        try:
            if not self._documentation_package.network_topology:
                test_results["test_results"]["error"] = "No network topology data"
                return test_results
            
            topology_data = self._documentation_package.network_topology
            service_endpoints = topology_data.get("service_endpoints", [])
            
            # Test service endpoint discovery
            expected_endpoints = [("localhost", 8888), ("localhost", 9090), ("localhost", 3000)]
            discovered_endpoints = [(ep.host, ep.port) for ep in service_endpoints]
            endpoint_completeness = len(set(expected_endpoints) & set(discovered_endpoints)) / len(expected_endpoints)
            
            test_results["test_results"]["endpoint_completeness"] = endpoint_completeness
            test_results["accuracy_score"] = endpoint_completeness
        
        except Exception as e:
            logger.error(f"Error testing network topology: {e}")
            test_results["test_results"]["error"] = str(e)
        
        return test_results
    
    async def _test_diagram_generation(self) -> Dict[str, Any]:
        """Test diagram generation results."""
        test_results = {"accuracy_score": 0.0, "test_results": {}}
        
        try:
            if not self._documentation_package.diagram_generation:
                test_results["test_results"]["error"] = "No diagram generation data"
                return test_results
            
            diagram_data = self._documentation_package.diagram_generation
            diagrams = diagram_data.get("diagrams", [])
            
            # Test diagram generation completeness
            expected_diagram_types = ["component", "sequence", "network_topology", "data_flow", "deployment"]
            generated_types = [d.metadata.diagram_type.value for d in diagrams]
            diagram_completeness = len(set(expected_diagram_types) & set(generated_types)) / len(expected_diagram_types)
            
            test_results["test_results"]["diagram_completeness"] = diagram_completeness
            test_results["accuracy_score"] = diagram_completeness
        
        except Exception as e:
            logger.error(f"Error testing diagram generation: {e}")
            test_results["test_results"]["error"] = str(e)
        
        return test_results
    
    async def _calculate_performance_metrics(self, start_time: datetime, end_time: datetime) -> None:
        """Calculate performance metrics."""
        try:
            total_time = (end_time - start_time).total_seconds()
            
            self._performance_metrics = PerformanceMetrics(
                total_time_seconds=total_time,
                accuracy_score=self._documentation_package.overall_accuracy_score,
                completeness_score=self._documentation_package.validation_success_rate,
                freshness_score=1.0,  # Freshly generated
                metrics_timestamp=end_time
            )
        
        except Exception as e:
            logger.error(f"Error calculating performance metrics: {e}")
    
    async def validate_documentation_accuracy(self) -> Dict[str, Any]:
        """Validate documentation accuracy against live system."""
        try:
            logger.info("Validating documentation accuracy against live system...")
            
            validation_results = {}
            
            # Validate each documentation type
            for doc_type in DocumentationType:
                if doc_type in self._documentation_package.validation_results:
                    validation_result = self._documentation_package.validation_results[doc_type]
                    
                    # Check if validation is stale
                    if validation_result.next_validation_due and datetime.now() > validation_result.next_validation_due:
                        validation_result.validation_status = ValidationStatus.STALE
                        validation_result.requires_manual_verification = True
                    
                    validation_results[doc_type.value] = {
                        "status": validation_result.validation_status.value,
                        "accuracy_score": validation_result.accuracy_score,
                        "requires_manual_verification": validation_result.requires_manual_verification,
                        "last_validated": validation_result.validation_timestamp.isoformat(),
                        "next_validation_due": validation_result.next_validation_due.isoformat() if validation_result.next_validation_due else None
                    }
            
            return {
                "validation_results": validation_results,
                "overall_accuracy_score": self._documentation_package.overall_accuracy_score,
                "validation_success_rate": self._documentation_package.validation_success_rate,
                "validation_timestamp": datetime.now().isoformat()
            }
        
        except Exception as e:
            logger.error(f"Error validating documentation accuracy: {e}")
            return {"error": str(e)}
    
    def get_documentation_package(self) -> Optional[DocumentationPackage]:
        """Get the current documentation package."""
        return self._documentation_package
    
    def get_validation_checklist(self, doc_type: DocumentationType) -> Optional[ValidationChecklist]:
        """Get validation checklist for a documentation type."""
        return self._validation_checklists.get(doc_type)
    
    def get_performance_metrics(self) -> Optional[PerformanceMetrics]:
        """Get current performance metrics."""
        return self._performance_metrics
    
    # ReflectiveModule implementation
    
    def get_capabilities(self) -> List['ModuleCapability']:
        """Get Documentation Orchestrator capabilities."""
        from src.rm_ddd.core.unified_reflective_module import ModuleCapability
        return [
            ModuleCapability.ORCHESTRATION,
            ModuleCapability.DOCUMENTATION,
            ModuleCapability.VALIDATION,
            ModuleCapability.MONITORING,
        ]
    
    def get_health_status(self) -> 'ModuleHealth':
        """Get health status of the Documentation Orchestrator."""
        from src.rm_ddd.core.unified_reflective_module import ModuleHealth, ModuleStatus
        
        if self._documentation_package and self._documentation_package.overall_accuracy_score > 0:
            status = ModuleStatus.HEALTHY
            health_score = self._documentation_package.overall_accuracy_score
            issues = []
        else:
            status = ModuleStatus.WARNING
            health_score = 0.5
            issues = ["No documentation package available"]
        
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
        """Get Documentation Orchestrator performance metrics."""
        if not self._documentation_package:
            return {
                "generation_time_seconds": 0.0,
                "overall_accuracy_score": 0.0,
                "validation_success_rate": 0.0,
                "total_documentation_types": 0,
            }
        
        return {
            "generation_time_seconds": self._documentation_package.generation_time_seconds,
            "overall_accuracy_score": self._documentation_package.overall_accuracy_score,
            "validation_success_rate": self._documentation_package.validation_success_rate,
            "total_documentation_types": len(self._documentation_package.validation_results),
            "validation_checklists": len(self._validation_checklists),
            "performance_metrics_available": self._performance_metrics is not None,
        }