"""
Health Scorer - Score system health based on various metrics
"""

from typing import Dict, List, Any
from dataclasses import dataclass
from .dag_analyzer import DAGAnalysisResult


@dataclass
class HealthMetrics:
    """Health metrics for a system component"""
    structural_health: float
    dependency_health: float
    performance_health: float
    maintainability_health: float
    overall_health: float


@dataclass
class HealthReport:
    """Comprehensive health report"""
    metrics: HealthMetrics
    issues: List[str]
    recommendations: List[str]
    confidence_level: float


class HealthScorer:
    """Scores system health based on multiple dimensions"""
    
    def __init__(self):
        self.weights = {
            'structural': 0.3,
            'dependency': 0.25,
            'performance': 0.25,
            'maintainability': 0.2
        }
    
    def score_makefile_health(self, dag_result: DAGAnalysisResult) -> HealthReport:
        """
        Score Makefile health based on DAG analysis
        
        Args:
            dag_result: Result from DAG analysis
            
        Returns:
            HealthReport with comprehensive scoring
        """
        structural_health = self._score_structural_health(dag_result)
        dependency_health = self._score_dependency_health(dag_result)
        performance_health = self._score_performance_health(dag_result)
        maintainability_health = self._score_maintainability_health(dag_result)
        
        overall_health = (
            structural_health * self.weights['structural'] +
            dependency_health * self.weights['dependency'] +
            performance_health * self.weights['performance'] +
            maintainability_health * self.weights['maintainability']
        )
        
        metrics = HealthMetrics(
            structural_health=structural_health,
            dependency_health=dependency_health,
            performance_health=performance_health,
            maintainability_health=maintainability_health,
            overall_health=overall_health
        )
        
        issues = self._identify_issues(dag_result, metrics)
        recommendations = self._generate_recommendations(issues, dag_result)
        confidence_level = self._calculate_confidence_level(dag_result, metrics)
        
        return HealthReport(
            metrics=metrics,
            issues=issues,
            recommendations=recommendations,
            confidence_level=confidence_level
        )
    
    def _score_structural_health(self, dag_result: DAGAnalysisResult) -> float:
        """Score structural health based on DAG structure"""
        total_nodes = len(dag_result.nodes)
        if total_nodes == 0:
            return 0.0
            
        # Penalize cycles heavily
        cycle_penalty = min(0.8, len(dag_result.cycles) * 0.3)
        
        # Penalize orphaned nodes
        orphan_penalty = min(0.4, len(dag_result.orphaned_nodes) * 0.1)
        
        # Reward well-connected structure
        avg_dependencies = sum(len(node.dependencies) for node in dag_result.nodes.values()) / total_nodes
        connectivity_score = min(1.0, avg_dependencies / 3.0)  # Optimal around 3 dependencies
        
        base_score = 1.0 - cycle_penalty - orphan_penalty
        return max(0.0, min(1.0, base_score * 0.7 + connectivity_score * 0.3))
    
    def _score_dependency_health(self, dag_result: DAGAnalysisResult) -> float:
        """Score dependency health"""
        if len(dag_result.nodes) == 0:
            return 0.0
            
        # Check for circular dependencies
        if dag_result.cycles:
            return 0.1  # Very low score for cycles
            
        # Check for reasonable dependency depth
        max_depth = self._calculate_max_dependency_depth(dag_result)
        if max_depth > 10:
            depth_penalty = min(0.5, (max_depth - 10) * 0.05)
        else:
            depth_penalty = 0.0
            
        # Check for dependency balance
        dependency_counts = [len(node.dependencies) for node in dag_result.nodes.values()]
        if dependency_counts:
            avg_deps = sum(dependency_counts) / len(dependency_counts)
            std_deps = (sum((x - avg_deps) ** 2 for x in dependency_counts) / len(dependency_counts)) ** 0.5
            
            # Prefer moderate dependencies with low variance
            balance_score = 1.0 if 1 <= avg_deps <= 5 and std_deps <= 2 else 0.7
        else:
            balance_score = 1.0
            
        return max(0.0, min(1.0, (1.0 - depth_penalty) * balance_score))
    
    def _score_performance_health(self, dag_result: DAGAnalysisResult) -> float:
        """Score performance health"""
        if len(dag_result.nodes) == 0:
            return 0.0
            
        # Check command complexity
        total_commands = sum(len(node.commands) for node in dag_result.nodes.values())
        avg_commands = total_commands / len(dag_result.nodes)
        
        # Optimal is 1-3 commands per target
        if 1 <= avg_commands <= 3:
            command_score = 1.0
        elif avg_commands < 1:
            command_score = 0.5  # Too simple might indicate missing functionality
        else:
            command_score = max(0.3, 1.0 - (avg_commands - 3) * 0.1)
            
        # Check for parallel execution opportunities
        parallel_score = self._calculate_parallel_potential(dag_result)
        
        return (command_score * 0.6 + parallel_score * 0.4)
    
    def _score_maintainability_health(self, dag_result: DAGAnalysisResult) -> float:
        """Score maintainability health"""
        if len(dag_result.nodes) == 0:
            return 0.0
            
        # Check for consistent naming
        naming_score = self._score_naming_consistency(dag_result)
        
        # Check for modularity
        modularity_score = self._score_modularity(dag_result)
        
        # Check for documentation (via comments in commands)
        doc_score = self._score_documentation(dag_result)
        
        return (naming_score * 0.4 + modularity_score * 0.4 + doc_score * 0.2)
    
    def _calculate_max_dependency_depth(self, dag_result: DAGAnalysisResult) -> int:
        """Calculate maximum dependency depth"""
        def dfs_depth(node_name: str, visited: set, depth: int) -> int:
            if node_name in visited or node_name not in dag_result.nodes:
                return depth
                
            visited.add(node_name)
            max_child_depth = depth
            
            for dep in dag_result.nodes[node_name].dependencies:
                child_depth = dfs_depth(dep, visited.copy(), depth + 1)
                max_child_depth = max(max_child_depth, child_depth)
                
            return max_child_depth
        
        max_depth = 0
        for node_name in dag_result.nodes:
            depth = dfs_depth(node_name, set(), 0)
            max_depth = max(max_depth, depth)
            
        return max_depth
    
    def _calculate_parallel_potential(self, dag_result: DAGAnalysisResult) -> float:
        """Calculate potential for parallel execution"""
        if len(dag_result.nodes) == 0:
            return 0.0
            
        # Count nodes that can run in parallel (no dependencies between them)
        parallel_groups = 0
        processed = set()
        
        for node_name in dag_result.nodes:
            if node_name in processed:
                continue
                
            # Find all nodes that can run in parallel with this one
            parallel_set = {node_name}
            for other_name in dag_result.nodes:
                if other_name == node_name or other_name in processed:
                    continue
                    
                # Check if they can run in parallel
                if self._can_run_parallel(node_name, other_name, dag_result):
                    parallel_set.add(other_name)
                    
            parallel_groups += 1
            processed.update(parallel_set)
            
        # Score based on parallelization potential
        total_nodes = len(dag_result.nodes)
        optimal_parallel = min(total_nodes, 4)  # Assume 4 cores optimal
        parallel_score = min(1.0, parallel_groups / optimal_parallel)
        
        return parallel_score
    
    def _can_run_parallel(self, node1: str, node2: str, dag_result: DAGAnalysisResult) -> bool:
        """Check if two nodes can run in parallel"""
        def has_dependency_path(start: str, end: str, visited: set) -> bool:
            if start == end:
                return True
            if start in visited or start not in dag_result.nodes:
                return False
                
            visited.add(start)
            for dep in dag_result.nodes[start].dependencies:
                if has_dependency_path(dep, end, visited.copy()):
                    return True
            return False
            
        return not (has_dependency_path(node1, node2, set()) or 
                   has_dependency_path(node2, node1, set()))
    
    def _score_naming_consistency(self, dag_result: DAGAnalysisResult) -> float:
        """Score naming consistency"""
        if not dag_result.nodes:
            return 1.0
            
        names = list(dag_result.nodes.keys())
        
        # Check for consistent naming patterns
        has_hyphens = any('-' in name for name in names)
        has_underscores = any('_' in name for name in names)
        
        if has_hyphens and has_underscores:
            return 0.5  # Mixed conventions
        elif has_hyphens or has_underscores:
            return 0.8  # Consistent with one convention
        else:
            return 1.0  # Clean naming
    
    def _score_modularity(self, dag_result: DAGAnalysisResult) -> float:
        """Score modularity based on component separation"""
        if len(dag_result.disconnected_components) <= 1:
            return 0.3  # Everything connected - not modular
            
        # Prefer 2-4 well-separated components
        component_count = len(dag_result.disconnected_components)
        if 2 <= component_count <= 4:
            return 1.0
        elif component_count > 4:
            return max(0.5, 1.0 - (component_count - 4) * 0.1)
        else:
            return 0.3
    
    def _score_documentation(self, dag_result: DAGAnalysisResult) -> float:
        """Score documentation quality"""
        if not dag_result.nodes:
            return 1.0
            
        documented_targets = 0
        for node in dag_result.nodes.values():
            # Look for comment lines in commands
            has_comments = any(cmd.strip().startswith('#') for cmd in node.commands)
            if has_comments:
                documented_targets += 1
                
        return documented_targets / len(dag_result.nodes)
    
    def _identify_issues(self, dag_result: DAGAnalysisResult, metrics: HealthMetrics) -> List[str]:
        """Identify specific issues based on analysis"""
        issues = []
        
        if metrics.structural_health < 0.7:
            issues.append("Poor structural organization detected")
            
        if metrics.dependency_health < 0.7:
            issues.append("Dependency issues found")
            
        if metrics.performance_health < 0.7:
            issues.append("Performance optimization opportunities identified")
            
        if metrics.maintainability_health < 0.7:
            issues.append("Maintainability concerns detected")
            
        if dag_result.cycles:
            issues.append(f"Circular dependencies found: {len(dag_result.cycles)} cycles")
            
        if dag_result.orphaned_nodes:
            issues.append(f"Orphaned targets found: {len(dag_result.orphaned_nodes)} targets")
            
        return issues
    
    def _generate_recommendations(self, issues: List[str], dag_result: DAGAnalysisResult) -> List[str]:
        """Generate actionable recommendations"""
        recommendations = []
        
        if dag_result.cycles:
            recommendations.append("Break circular dependencies by introducing intermediate targets")
            
        if dag_result.orphaned_nodes:
            recommendations.append("Remove or integrate orphaned targets into dependency chain")
            
        if len(dag_result.disconnected_components) == 1:
            recommendations.append("Consider breaking into modular components")
            
        if any(len(node.commands) > 5 for node in dag_result.nodes.values()):
            recommendations.append("Break down complex targets into smaller, focused tasks")
            
        max_depth = self._calculate_max_dependency_depth(dag_result)
        if max_depth > 10:
            recommendations.append("Reduce dependency depth for better maintainability")
            
        return recommendations
    
    def _calculate_confidence_level(self, dag_result: DAGAnalysisResult, metrics: HealthMetrics) -> float:
        """Calculate confidence level in the health assessment"""
        # Base confidence on data quality and consistency
        data_points = len(dag_result.nodes)
        if data_points == 0:
            return 0.0
            
        # Higher confidence with more data
        data_confidence = min(1.0, data_points / 20.0)
        
        # Consistency confidence based on metric agreement
        metrics_list = [
            metrics.structural_health,
            metrics.dependency_health,
            metrics.performance_health,
            metrics.maintainability_health
        ]
        
        avg_metric = sum(metrics_list) / len(metrics_list)
        variance = sum((m - avg_metric) ** 2 for m in metrics_list) / len(metrics_list)
        consistency_confidence = max(0.0, 1.0 - variance)
        
        return (data_confidence * 0.6 + consistency_confidence * 0.4)
