"""
Makefile Analysis System for System Architecture Wiring Diagram.

This module implements comprehensive Makefile analysis to extract all targets,
dependencies, and their effects on infrastructure components.
"""

import logging
import re
import subprocess
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any, Set, Tuple
from enum import Enum

from ..core import ReflectiveModule

logger = logging.getLogger(__name__)


class TargetCategory(Enum):
    """Categories of Makefile targets."""
    DEPLOYMENT = "deployment"
    DEVELOPMENT = "development"
    TESTING = "testing"
    MONITORING = "monitoring"
    MAINTENANCE = "maintenance"
    DOCKER = "docker"
    CI_CD = "ci_cd"
    SETUP = "setup"
    CLEANUP = "cleanup"
    INFO = "info"


class InfrastructureEffect(Enum):
    """Infrastructure components affected by targets."""
    CLOUDFLARE_TUNNEL = "cloudflare_tunnel"
    DNS_ROUTING = "dns_routing"
    OBSERVATORY_SERVER = "observatory_server"
    WEBSOCKET_ENDPOINTS = "websocket_endpoints"
    PROMETHEUS_SERVER = "prometheus_server"
    GRAFANA_SERVER = "grafana_server"
    BEAST_MODE_COMPONENTS = "beast_mode_components"
    DAG_REGISTRY = "dag_registry"
    REDIS_COORDINATION = "redis_coordination"
    FILE_SYSTEM = "file_system"
    DOCKER_CONTAINERS = "docker_containers"
    GITHUB_ACTIONS = "github_actions"


@dataclass
class MakefileTarget:
    """Information about a Makefile target."""
    name: str
    dependencies: List[str] = field(default_factory=list)
    commands: List[str] = field(default_factory=list)
    category: TargetCategory = TargetCategory.SETUP
    affected_components: List[InfrastructureEffect] = field(default_factory=list)
    expected_outcomes: List[str] = field(default_factory=list)
    execution_time_estimate: Optional[float] = None  # seconds
    requires_environment: List[str] = field(default_factory=list)
    risk_level: str = "low"  # low, medium, high, critical
    
    # Versioning and validation fields
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    version: str = "1.0.0"
    last_validated: Optional[datetime] = None
    validation_status: str = "pending"


@dataclass
class MakefileAnalysis:
    """Complete analysis of a Makefile."""
    targets: Dict[str, MakefileTarget] = field(default_factory=dict)
    dependency_graph: Dict[str, List[str]] = field(default_factory=dict)
    execution_chains: List[List[str]] = field(default_factory=list)
    infrastructure_mapping: Dict[str, List[InfrastructureEffect]] = field(default_factory=dict)
    
    # Analysis metadata
    total_targets: int = 0
    categories_found: Set[TargetCategory] = field(default_factory=set)
    complexity_score: float = 0.0  # 0.0-1.0
    analysis_timestamp: datetime = field(default_factory=datetime.now)


class MakefileAnalyzer(ReflectiveModule):
    """Comprehensive Makefile analysis system."""
    
    def __init__(self):
        super().__init__()
        self.module_id = "makefile_analyzer"
        self._makefile_path: Optional[Path] = None
        self._analysis: Optional[MakefileAnalysis] = None
        
        # Target categorization patterns
        self._category_patterns = {
            TargetCategory.DEPLOYMENT: [
                r'deploy', r'tunnel-start', r'tunnel-stop', r'dashboard-up', 
                r'dashboard-stop', r'dashboard-restart'
            ],
            TargetCategory.DEVELOPMENT: [
                r'dev-', r'build', r'compile', r'install'
            ],
            TargetCategory.TESTING: [
                r'test', r'verify', r'validate', r'check'
            ],
            TargetCategory.MONITORING: [
                r'monitor', r'status', r'logs', r'analytics', r'health'
            ],
            TargetCategory.MAINTENANCE: [
                r'backup', r'update', r'clean', r'maintenance'
            ],
            TargetCategory.DOCKER: [
                r'docker-', r'container'
            ],
            TargetCategory.CI_CD: [
                r'ci-', r'cd-', r'github', r'workflow'
            ],
            TargetCategory.SETUP: [
                r'setup', r'init', r'configure', r'env'
            ],
            TargetCategory.CLEANUP: [
                r'clean', r'remove', r'delete', r'purge'
            ],
            TargetCategory.INFO: [
                r'help', r'info', r'version', r'status'
            ]
        }
        
        # Infrastructure effect mapping patterns
        self._infrastructure_patterns = {
            InfrastructureEffect.CLOUDFLARE_TUNNEL: [
                r'tunnel', r'cloudflare', r'd1e53e43-033f-4994-8f46-c83962ae3785'
            ],
            InfrastructureEffect.DNS_ROUTING: [
                r'dns', r'domain', r'nkllon\.com', r'routing'
            ],
            InfrastructureEffect.OBSERVATORY_SERVER: [
                r'observatory', r'dashboard', r'localhost:8888'
            ],
            InfrastructureEffect.WEBSOCKET_ENDPOINTS: [
                r'websocket', r'/ws/', r'ws/observatory', r'ws/anomalies', 
                r'ws/emoji-rain', r'ws/doctor-status'
            ],
            InfrastructureEffect.PROMETHEUS_SERVER: [
                r'prometheus', r'localhost:9090', r'metrics'
            ],
            InfrastructureEffect.GRAFANA_SERVER: [
                r'grafana', r'localhost:3000', r'dashboard'
            ],
            InfrastructureEffect.BEAST_MODE_COMPONENTS: [
                r'beast', r'task-', r'phase-', r'component'
            ],
            InfrastructureEffect.DAG_REGISTRY: [
                r'dag', r'registry', r'orchestration'
            ],
            InfrastructureEffect.REDIS_COORDINATION: [
                r'redis', r'192\.168\.1\.119:6379', r'coordination'
            ],
            InfrastructureEffect.FILE_SYSTEM: [
                r'file', r'path', r'directory', r'backup'
            ],
            InfrastructureEffect.DOCKER_CONTAINERS: [
                r'docker', r'container', r'image'
            ],
            InfrastructureEffect.GITHUB_ACTIONS: [
                r'github', r'workflow', r'actions'
            ]
        }
        
        logger.info("Makefile Analyzer initialized")
    
    async def analyze_makefile(self, makefile_path: Optional[Path] = None) -> MakefileAnalysis:
        """Perform comprehensive analysis of a Makefile."""
        try:
            self._makefile_path = makefile_path or Path("Makefile")
            
            if not self._makefile_path.exists():
                raise FileNotFoundError(f"Makefile not found at {self._makefile_path}")
            
            logger.info(f"Analyzing Makefile: {self._makefile_path}")
            
            # Initialize analysis
            self._analysis = MakefileAnalysis()
            
            # Parse Makefile content
            content = await self._read_makefile_content()
            
            # Extract targets and dependencies
            targets = await self._extract_targets(content)
            self._analysis.targets = targets
            self._analysis.total_targets = len(targets)
            
            # Build dependency graph
            dependency_graph = await self._build_dependency_graph(targets)
            self._analysis.dependency_graph = dependency_graph
            
            # Find execution chains
            execution_chains = await self._find_execution_chains(dependency_graph)
            self._analysis.execution_chains = execution_chains
            
            # Map infrastructure effects
            infrastructure_mapping = await self._map_infrastructure_effects(targets)
            self._analysis.infrastructure_mapping = infrastructure_mapping
            
            # Calculate complexity score
            complexity_score = await self._calculate_complexity_score(targets, dependency_graph)
            self._analysis.complexity_score = complexity_score
            
            # Identify categories
            categories = set()
            for target in targets.values():
                categories.add(target.category)
            self._analysis.categories_found = categories
            
            logger.info(f"Makefile analysis completed: {len(targets)} targets, {len(execution_chains)} chains")
            return self._analysis
            
        except Exception as e:
            logger.error(f"Makefile analysis failed: {e}")
            raise
    
    async def _read_makefile_content(self) -> str:
        """Read Makefile content."""
        try:
            with open(self._makefile_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            logger.error(f"Error reading Makefile: {e}")
            raise
    
    async def _extract_targets(self, content: str) -> Dict[str, MakefileTarget]:
        """Extract all targets from Makefile content."""
        targets = {}
        lines = content.split('\n')
        
        current_target = None
        current_commands = []
        
        for line_num, line in enumerate(lines, 1):
            line = line.rstrip()
            
            # Skip empty lines and comments
            if not line or line.startswith('#'):
                continue
            
            # Check if this is a target line (contains : and doesn't start with tab)
            if ':' in line and not line.startswith('\t') and not line.startswith(' '):
                # Save previous target if exists
                if current_target:
                    targets[current_target.name] = current_target
                
                # Parse new target
                target_parts = line.split(':', 1)
                target_name = target_parts[0].strip()
                dependencies_str = target_parts[1].strip() if len(target_parts) > 1 else ""
                
                # Parse dependencies
                dependencies = [dep.strip() for dep in dependencies_str.split() if dep.strip()]
                
                # Create new target
                current_target = MakefileTarget(
                    name=target_name,
                    dependencies=dependencies
                )
                
                # Categorize target
                current_target.category = await self._categorize_target(target_name)
                
                # Map infrastructure effects
                current_target.affected_components = await self._map_target_infrastructure_effects(
                    target_name, current_target.commands
                )
                
                # Set risk level
                current_target.risk_level = await self._assess_target_risk(target_name, current_target.commands)
                
                # Reset commands for new target
                current_commands = []
            
            # Check if this is a command line (starts with tab)
            elif line.startswith('\t') and current_target:
                command = line[1:].strip()  # Remove leading tab
                current_commands.append(command)
                current_target.commands.append(command)
            
            # Handle multi-line commands (continuation with backslash)
            elif line.endswith('\\') and current_target and current_commands:
                # Remove backslash and add to last command
                continuation = line[:-1].strip()
                if current_target.commands:
                    current_target.commands[-1] += ' ' + continuation
        
        # Save last target
        if current_target:
            targets[current_target.name] = current_target
        
        # Post-process targets to extract additional information
        for target in targets.values():
            await self._extract_target_metadata(target)
        
        return targets
    
    async def _categorize_target(self, target_name: str) -> TargetCategory:
        """Categorize a target based on its name."""
        target_lower = target_name.lower()
        
        for category, patterns in self._category_patterns.items():
            for pattern in patterns:
                if re.search(pattern, target_lower):
                    return category
        
        return TargetCategory.SETUP  # Default category
    
    async def _map_target_infrastructure_effects(self, target_name: str, commands: List[str]) -> List[InfrastructureEffect]:
        """Map infrastructure effects for a target."""
        effects = []
        target_lower = target_name.lower()
        commands_text = ' '.join(commands).lower()
        
        for effect, patterns in self._infrastructure_patterns.items():
            for pattern in patterns:
                if (re.search(pattern, target_lower) or 
                    re.search(pattern, commands_text)):
                    if effect not in effects:
                        effects.append(effect)
        
        return effects
    
    async def _assess_target_risk(self, target_name: str, commands: List[str]) -> str:
        """Assess risk level of a target."""
        target_lower = target_name.lower()
        commands_text = ' '.join(commands).lower()
        
        # High risk patterns
        high_risk_patterns = [
            r'delete', r'remove', r'destroy', r'purge', r'rollback',
            r'rm -rf', r'docker rm', r'docker rmi'
        ]
        
        # Medium risk patterns
        medium_risk_patterns = [
            r'deploy', r'update', r'modify', r'change', r'restart',
            r'docker stop', r'docker start'
        ]
        
        # Check for high risk
        for pattern in high_risk_patterns:
            if re.search(pattern, target_lower) or re.search(pattern, commands_text):
                return "high"
        
        # Check for medium risk
        for pattern in medium_risk_patterns:
            if re.search(pattern, target_lower) or re.search(pattern, commands_text):
                return "medium"
        
        return "low"  # Default to low risk
    
    async def _extract_target_metadata(self, target: MakefileTarget) -> None:
        """Extract additional metadata for a target."""
        # Estimate execution time based on commands
        target.execution_time_estimate = await self._estimate_execution_time(target.commands)
        
        # Extract environment requirements
        target.requires_environment = await self._extract_environment_requirements(target.commands)
        
        # Generate expected outcomes
        target.expected_outcomes = await self._generate_expected_outcomes(target)
        
        # Update validation timestamp
        target.last_validated = datetime.now()
        target.validation_status = "validated"
    
    async def _estimate_execution_time(self, commands: List[str]) -> float:
        """Estimate execution time for commands in seconds."""
        total_time = 0.0
        
        for command in commands:
            command_lower = command.lower()
            
            # Quick commands (< 1 second)
            if any(pattern in command_lower for pattern in ['echo', 'mkdir', 'cp', 'mv', 'ln']):
                total_time += 0.1
            
            # Network operations (1-10 seconds)
            elif any(pattern in command_lower for pattern in ['curl', 'wget', 'ping', 'ssh']):
                total_time += 5.0
            
            # Docker operations (5-30 seconds)
            elif any(pattern in command_lower for pattern in ['docker build', 'docker run', 'docker pull']):
                total_time += 15.0
            
            # File operations (0.1-2 seconds)
            elif any(pattern in command_lower for pattern in ['python', 'pip', 'npm', 'yarn']):
                total_time += 2.0
            
            # Default estimate
            else:
                total_time += 1.0
        
        return total_time
    
    async def _extract_environment_requirements(self, commands: List[str]) -> List[str]:
        """Extract environment requirements from commands."""
        requirements = []
        
        for command in commands:
            # Look for environment variable references
            env_vars = re.findall(r'\$\(([^)]+)\)', command)
            requirements.extend(env_vars)
            
            # Look for direct environment variable usage
            env_vars = re.findall(r'\$([A-Z_][A-Z0-9_]*)', command)
            requirements.extend(env_vars)
        
        return list(set(requirements))  # Remove duplicates
    
    async def _generate_expected_outcomes(self, target: MakefileTarget) -> List[str]:
        """Generate expected outcomes for a target."""
        outcomes = []
        
        # Based on target category
        if target.category == TargetCategory.DEPLOYMENT:
            outcomes.extend([
                "Service successfully deployed",
                "Health checks passing",
                "Endpoints accessible"
            ])
        elif target.category == TargetCategory.TESTING:
            outcomes.extend([
                "All tests passing",
                "Validation successful",
                "No errors detected"
            ])
        elif target.category == TargetCategory.MONITORING:
            outcomes.extend([
                "Status information displayed",
                "Metrics collected",
                "Health status reported"
            ])
        elif target.category == TargetCategory.CLEANUP:
            outcomes.extend([
                "Temporary files removed",
                "Cache cleared",
                "Cleanup completed"
            ])
        
        # Based on infrastructure effects
        if InfrastructureEffect.CLOUDFLARE_TUNNEL in target.affected_components:
            outcomes.append("Tunnel connectivity established")
        
        if InfrastructureEffect.OBSERVATORY_SERVER in target.affected_components:
            outcomes.append("Observatory server operational")
        
        if InfrastructureEffect.WEBSOCKET_ENDPOINTS in target.affected_components:
            outcomes.append("WebSocket connections established")
        
        return outcomes
    
    async def _build_dependency_graph(self, targets: Dict[str, MakefileTarget]) -> Dict[str, List[str]]:
        """Build dependency graph from targets."""
        graph = {}
        
        for target_name, target in targets.items():
            graph[target_name] = target.dependencies.copy()
        
        return graph
    
    async def _find_execution_chains(self, dependency_graph: Dict[str, List[str]]) -> List[List[str]]:
        """Find execution chains in the dependency graph."""
        chains = []
        visited = set()
        
        def find_chain(target: str, current_chain: List[str]) -> None:
            if target in visited:
                return
            
            visited.add(target)
            current_chain.append(target)
            
            # If this target has no dependencies, it's a leaf
            if not dependency_graph.get(target, []):
                chains.append(current_chain.copy())
            else:
                # Continue with dependencies
                for dep in dependency_graph.get(target, []):
                    find_chain(dep, current_chain.copy())
        
        # Start from targets with no dependencies (root targets)
        root_targets = [target for target, deps in dependency_graph.items() if not deps]
        
        for root in root_targets:
            find_chain(root, [])
        
        return chains
    
    async def _map_infrastructure_effects(self, targets: Dict[str, MakefileTarget]) -> Dict[str, List[InfrastructureEffect]]:
        """Map infrastructure effects for all targets."""
        mapping = {}
        
        for target_name, target in targets.items():
            mapping[target_name] = target.affected_components
        
        return mapping
    
    async def _calculate_complexity_score(self, targets: Dict[str, MakefileTarget], 
                                        dependency_graph: Dict[str, List[str]]) -> float:
        """Calculate complexity score for the Makefile."""
        if not targets:
            return 0.0
        
        # Factors contributing to complexity
        target_count = len(targets)
        avg_dependencies = sum(len(deps) for deps in dependency_graph.values()) / len(dependency_graph)
        avg_commands = sum(len(target.commands) for target in targets.values()) / len(targets)
        
        # Calculate complexity score (0.0-1.0)
        complexity = min(1.0, (target_count * 0.01 + avg_dependencies * 0.1 + avg_commands * 0.05))
        
        return complexity
    
    def get_analysis(self) -> Optional[MakefileAnalysis]:
        """Get the current analysis."""
        return self._analysis
    
    def get_target_by_name(self, target_name: str) -> Optional[MakefileTarget]:
        """Get a specific target by name."""
        if self._analysis and target_name in self._analysis.targets:
            return self._analysis.targets[target_name]
        return None
    
    def get_targets_by_category(self, category: TargetCategory) -> List[MakefileTarget]:
        """Get all targets in a specific category."""
        if not self._analysis:
            return []
        
        return [target for target in self._analysis.targets.values() 
                if target.category == category]
    
    def get_targets_affecting_component(self, component: InfrastructureEffect) -> List[MakefileTarget]:
        """Get all targets that affect a specific infrastructure component."""
        if not self._analysis:
            return []
        
        return [target for target in self._analysis.targets.values() 
                if component in target.affected_components]
    
    def get_execution_chain_for_target(self, target_name: str) -> List[str]:
        """Get the execution chain for a specific target."""
        if not self._analysis:
            return []
        
        # Find chains that end with this target
        for chain in self._analysis.execution_chains:
            if chain and chain[-1] == target_name:
                return chain
        
        return [target_name]  # Return just the target if no chain found
    
    # ReflectiveModule implementation
    
    def get_capabilities(self) -> List['ModuleCapability']:
        """Get Makefile Analyzer capabilities."""
        from src.rm_ddd.core.unified_reflective_module import ModuleCapability
        return [
            ModuleCapability.DATA_PROCESSING,
            ModuleCapability.ANALYSIS,
        ]
    
    def get_health_status(self) -> 'ModuleHealth':
        """Get health status of the Makefile Analyzer."""
        from src.rm_ddd.core.unified_reflective_module import ModuleHealth, ModuleStatus
        
        if self._analysis and self._analysis.total_targets > 0:
            status = ModuleStatus.HEALTHY
            health_score = min(1.0, self._analysis.total_targets / 50.0)  # Scale based on targets found
            issues = []
        else:
            status = ModuleStatus.WARNING
            health_score = 0.5
            issues = ["No Makefile analysis available"]
        
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
        """Get Makefile Analyzer performance metrics."""
        if not self._analysis:
            return {
                "total_targets": 0,
                "complexity_score": 0.0,
                "categories_found": 0,
                "execution_chains": 0,
            }
        
        return {
            "total_targets": self._analysis.total_targets,
            "complexity_score": self._analysis.complexity_score,
            "categories_found": len(self._analysis.categories_found),
            "execution_chains": len(self._analysis.execution_chains),
            "infrastructure_components": len(set().union(*self._analysis.infrastructure_mapping.values())),
            "high_risk_targets": len([t for t in self._analysis.targets.values() if t.risk_level == "high"]),
            "medium_risk_targets": len([t for t in self._analysis.targets.values() if t.risk_level == "medium"]),
            "low_risk_targets": len([t for t in self._analysis.targets.values() if t.risk_level == "low"]),
        }