"""
Comprehensive Dependency Analysis System

This module provides advanced dependency analysis capabilities including:
- Circular dependency detection with detailed path analysis
- Orphaned file detection using pattern coverage analysis
- Dependency impact analysis for change assessment
- Performance-optimized algorithms for large domain sets
"""

import os
import ast
import time
from pathlib import Path
from typing import Dict, List, Optional, Any, Set, Tuple, Union
from datetime import datetime
from collections import defaultdict, deque
from concurrent.futures import ThreadPoolExecutor, as_completed

from .base import DomainSystemComponent
from .models import (
    Domain, DomainCollection, DependencyGraph, HealthIssue, 
    IssueSeverity, IssueCategory, ValidationResult
)
from .exceptions import DependencyAnalysisError
from .config import get_config


class CircularDependencyDetector:
    """
    Advanced circular dependency detection using multiple algorithms
    """
    
    def __init__(self, domains: DomainCollection):
        self.domains = domains
        self.dependency_graph = self._build_dependency_graph()
    
    def _build_dependency_graph(self) -> Dict[str, Set[str]]:
        """Build adjacency list representation of dependency graph"""
        graph = defaultdict(set)
        for domain_name, domain in self.domains.items():
            for dep in domain.dependencies:
                if dep in self.domains:  # Only include valid dependencies
                    graph[domain_name].add(dep)
        return dict(graph)
    
    def detect_cycles_dfs(self) -> List[List[str]]:
        """Detect cycles using Depth-First Search with path tracking"""
        cycles = []
        visited = set()
        rec_stack = set()
        
        def dfs(node: str, path: List[str]) -> None:
            if node in rec_stack:
                # Found cycle - extract the cycle path
                cycle_start = path.index(node)
                cycle = path[cycle_start:] + [node]
                cycles.append(cycle)
                return
            
            if node in visited:
                return
            
            visited.add(node)
            rec_stack.add(node)
            
            # Visit all dependencies
            for neighbor in self.dependency_graph.get(node, set()):
                dfs(neighbor, path + [node])
            
            rec_stack.remove(node)
        
        # Check each domain as potential cycle start
        for domain_name in self.domains:
            if domain_name not in visited:
                dfs(domain_name, [])
        
        return cycles
    
    def detect_cycles_tarjan(self) -> List[List[str]]:
        """Detect strongly connected components using Tarjan's algorithm"""
        index_counter = [0]
        stack = []
        lowlinks = {}
        index = {}
        on_stack = {}
        sccs = []
        
        def strongconnect(node: str) -> None:
            index[node] = index_counter[0]
            lowlinks[node] = index_counter[0]
            index_counter[0] += 1
            stack.append(node)
            on_stack[node] = True
            
            # Consider successors
            for successor in self.dependency_graph.get(node, set()):
                if successor not in index:
                    strongconnect(successor)
                    lowlinks[node] = min(lowlinks[node], lowlinks[successor])
                elif on_stack.get(successor, False):
                    lowlinks[node] = min(lowlinks[node], index[successor])
            
            # If node is a root node, pop the stack and create SCC
            if lowlinks[node] == index[node]:
                component = []
                while True:
                    w = stack.pop()
                    on_stack[w] = False
                    component.append(w)
                    if w == node:
                        break
                
                # Only include SCCs with more than one node (actual cycles)
                if len(component) > 1:
                    sccs.append(component)
        
        # Find all SCCs
        for node in self.domains:
            if node not in index:
                strongconnect(node)
        
        return sccs
    
    def analyze_cycle_impact(self, cycle: List[str]) -> Dict[str, Any]:
        """Analyze the impact and characteristics of a dependency cycle"""
        cycle_domains = [self.domains[name] for name in cycle if name in self.domains]
        
        # Calculate cycle metrics
        total_files = sum(domain.file_count for domain in cycle_domains)
        total_lines = sum(domain.line_count for domain in cycle_domains)
        
        # Analyze cycle complexity
        cycle_length = len(cycle)
        complexity_score = min(1.0, cycle_length / 10.0)  # Normalize to 0-1
        
        # Find external dependencies (dependencies outside the cycle)
        external_deps = set()
        for domain_name in cycle:
            if domain_name in self.domains:
                domain = self.domains[domain_name]
                for dep in domain.dependencies:
                    if dep not in cycle and dep in self.domains:
                        external_deps.add(dep)
        
        # Find dependents (domains that depend on cycle members)
        dependents = set()
        for domain_name, domain in self.domains.items():
            if domain_name not in cycle:
                for dep in domain.dependencies:
                    if dep in cycle:
                        dependents.add(domain_name)
        
        return {
            "cycle_path": cycle,
            "cycle_length": cycle_length,
            "complexity_score": complexity_score,
            "total_files_affected": total_files,
            "total_lines_affected": total_lines,
            "external_dependencies": list(external_deps),
            "external_dependents": list(dependents),
            "breaking_suggestions": self._suggest_cycle_breaking_points(cycle)
        }
    
    def _suggest_cycle_breaking_points(self, cycle: List[str]) -> List[Dict[str, Any]]:
        """Suggest potential points to break the dependency cycle"""
        suggestions = []
        
        for i in range(len(cycle) - 1):
            current = cycle[i]
            next_domain = cycle[i + 1]
            
            if current in self.domains and next_domain in self.domains:
                current_domain = self.domains[current]
                
                # Suggest breaking this dependency
                suggestion = {
                    "break_dependency": f"{current} -> {next_domain}",
                    "impact_score": 0.5,  # Default impact
                    "suggested_approach": "Extract common interface or use dependency injection",
                    "alternative_patterns": [
                        "Observer pattern",
                        "Event-driven architecture",
                        "Dependency inversion"
                    ]
                }
                suggestions.append(suggestion)
        
        return suggestions


class OrphanedFileDetector:
    """
    Advanced orphaned file detection using pattern analysis
    """
    
    def __init__(self, domains: DomainCollection, project_root: Path):
        self.domains = domains
        self.project_root = project_root
        self.file_extensions = {'.py', '.js', '.ts', '.java', '.cpp', '.c', '.h', '.hpp'}
    
    def detect_orphaned_files(self, include_tests: bool = True) -> Dict[str, Any]:
        """Detect files not covered by any domain pattern"""
        # Get all relevant files in the project
        all_files = self._get_all_project_files(include_tests)
        
        # Get all domain patterns
        domain_patterns = self._collect_domain_patterns()
        
        # Find uncovered files
        orphaned_files = []
        coverage_map = {}
        
        for file_path in all_files:
            covering_domains = self._find_covering_domains(file_path, domain_patterns)
            
            if not covering_domains:
                orphaned_files.append(str(file_path))
            else:
                coverage_map[str(file_path)] = covering_domains
        
        # Analyze orphaned files
        analysis = self._analyze_orphaned_files(orphaned_files)
        
        return {
            "orphaned_files": orphaned_files,
            "total_files_checked": len(all_files),
            "coverage_percentage": ((len(all_files) - len(orphaned_files)) / max(len(all_files), 1)) * 100,
            "coverage_map": coverage_map,
            "analysis": analysis,
            "suggestions": self._suggest_domain_assignments(orphaned_files)
        }
    
    def _get_all_project_files(self, include_tests: bool) -> List[Path]:
        """Get all relevant files in the project"""
        files = []
        
        for ext in self.file_extensions:
            pattern = f"**/*{ext}"
            found_files = list(self.project_root.glob(pattern))
            
            # Filter out common exclusions
            filtered_files = []
            for file_path in found_files:
                relative_path = file_path.relative_to(self.project_root)
                path_str = str(relative_path)
                
                # Skip common exclusions
                if any(exclude in path_str for exclude in [
                    '__pycache__', '.git', 'node_modules', '.venv', 'venv',
                    '.pytest_cache', '.mypy_cache', 'build', 'dist'
                ]):
                    continue
                
                # Skip test files if not including tests
                if not include_tests and ('test' in path_str.lower() or 'spec' in path_str.lower()):
                    continue
                
                filtered_files.append(file_path)
            
            files.extend(filtered_files)
        
        return files
    
    def _collect_domain_patterns(self) -> Dict[str, List[str]]:
        """Collect all domain patterns"""
        patterns = {}
        for domain_name, domain in self.domains.items():
            patterns[domain_name] = domain.patterns
        return patterns
    
    def _find_covering_domains(self, file_path: Path, domain_patterns: Dict[str, List[str]]) -> List[str]:
        """Find which domains cover a specific file"""
        relative_path = file_path.relative_to(self.project_root)
        covering_domains = []
        
        for domain_name, patterns in domain_patterns.items():
            for pattern in patterns:
                if self._file_matches_pattern(relative_path, pattern):
                    covering_domains.append(domain_name)
                    break  # One match per domain is enough
        
        return covering_domains
    
    def _file_matches_pattern(self, file_path: Path, pattern: str) -> bool:
        """Check if a file matches a domain pattern using glob-like matching"""
        try:
            # Convert pattern to Path and use match
            pattern_path = Path(pattern)
            
            # Handle different pattern types
            if "**" in pattern:
                # Recursive pattern - use glob matching
                return file_path.match(pattern) or any(
                    file_path.match(part) for part in pattern.split("**") if part.strip()
                )
            else:
                # Simple pattern matching
                return file_path.match(pattern)
        except Exception:
            # Fallback to string matching
            return pattern.replace("**", "") in str(file_path)
    
    def _analyze_orphaned_files(self, orphaned_files: List[str]) -> Dict[str, Any]:
        """Analyze characteristics of orphaned files"""
        if not orphaned_files:
            return {"file_types": {}, "directories": {}, "size_analysis": {}}
        
        # Analyze by file type
        file_types = defaultdict(int)
        directories = defaultdict(int)
        total_size = 0
        
        for file_path_str in orphaned_files:
            file_path = Path(file_path_str)
            
            # File type analysis
            extension = file_path.suffix
            file_types[extension] += 1
            
            # Directory analysis
            parent_dir = str(file_path.parent)
            directories[parent_dir] += 1
            
            # Size analysis
            try:
                full_path = self.project_root / file_path
                if full_path.exists():
                    total_size += full_path.stat().st_size
            except Exception:
                pass
        
        return {
            "file_types": dict(file_types),
            "directories": dict(directories),
            "size_analysis": {
                "total_size_bytes": total_size,
                "average_size_bytes": total_size / max(len(orphaned_files), 1)
            }
        }
    
    def _suggest_domain_assignments(self, orphaned_files: List[str]) -> List[Dict[str, Any]]:
        """Suggest potential domain assignments for orphaned files"""
        suggestions = []
        
        # Group files by directory for better suggestions
        dir_groups = defaultdict(list)
        for file_path_str in orphaned_files:
            file_path = Path(file_path_str)
            dir_groups[str(file_path.parent)].append(file_path_str)
        
        # Generate suggestions for each directory group
        for directory, files in dir_groups.items():
            suggestion = {
                "directory": directory,
                "files": files,
                "suggested_actions": self._generate_assignment_suggestions(directory, files)
            }
            suggestions.append(suggestion)
        
        return suggestions
    
    def _generate_assignment_suggestions(self, directory: str, files: List[str]) -> List[str]:
        """Generate specific assignment suggestions for a directory"""
        suggestions = []
        
        # Analyze directory name for clues
        dir_parts = directory.lower().split('/')
        
        # Look for existing domains with similar patterns
        for domain_name, domain in self.domains.items():
            domain_name_lower = domain_name.lower()
            
            # Check if directory matches domain name
            if any(part in domain_name_lower or domain_name_lower in part for part in dir_parts):
                suggestions.append(f"Extend '{domain_name}' domain to include {directory}")
        
        # Generic suggestions
        if not suggestions:
            suggestions.extend([
                f"Create new domain for {directory}",
                f"Add pattern to existing domain that logically includes {directory}",
                f"Consider if files in {directory} should be moved to existing domain directories"
            ])
        
        return suggestions


class DependencyImpactAnalyzer:
    """
    Analyze the impact of potential changes to domain dependencies
    """
    
    def __init__(self, domains: DomainCollection):
        self.domains = domains
        self.dependency_graph = self._build_dependency_graph()
        self.reverse_graph = self._build_reverse_graph()
    
    def _build_dependency_graph(self) -> Dict[str, Set[str]]:
        """Build forward dependency graph"""
        graph = defaultdict(set)
        for domain_name, domain in self.domains.items():
            for dep in domain.dependencies:
                if dep in self.domains:
                    graph[domain_name].add(dep)
        return dict(graph)
    
    def _build_reverse_graph(self) -> Dict[str, Set[str]]:
        """Build reverse dependency graph (who depends on whom)"""
        reverse_graph = defaultdict(set)
        for domain_name, dependencies in self.dependency_graph.items():
            for dep in dependencies:
                reverse_graph[dep].add(domain_name)
        return dict(reverse_graph)
    
    def analyze_change_impact(self, domain_name: str, change_type: str) -> Dict[str, Any]:
        """Analyze impact of changes to a domain"""
        if domain_name not in self.domains:
            return {"error": f"Domain '{domain_name}' not found"}
        
        # Find all domains that would be affected
        affected_domains = self._find_affected_domains(domain_name, change_type)
        
        # Calculate impact metrics
        impact_metrics = self._calculate_impact_metrics(domain_name, affected_domains)
        
        # Generate recommendations
        recommendations = self._generate_change_recommendations(domain_name, change_type, affected_domains)
        
        return {
            "target_domain": domain_name,
            "change_type": change_type,
            "directly_affected": list(self.reverse_graph.get(domain_name, set())),
            "transitively_affected": affected_domains,
            "impact_metrics": impact_metrics,
            "recommendations": recommendations,
            "risk_assessment": self._assess_change_risk(domain_name, affected_domains)
        }
    
    def _find_affected_domains(self, domain_name: str, change_type: str) -> Set[str]:
        """Find all domains affected by a change"""
        affected = set()
        
        if change_type in ["modify", "delete"]:
            # Find all domains that depend on this domain (transitively)
            visited = set()
            queue = deque([domain_name])
            
            while queue:
                current = queue.popleft()
                if current in visited:
                    continue
                
                visited.add(current)
                dependents = self.reverse_graph.get(current, set())
                
                for dependent in dependents:
                    if dependent not in visited:
                        affected.add(dependent)
                        queue.append(dependent)
        
        return affected
    
    def _calculate_impact_metrics(self, domain_name: str, affected_domains: Set[str]) -> Dict[str, Any]:
        """Calculate quantitative impact metrics"""
        target_domain = self.domains[domain_name]
        
        # Calculate affected file and line counts
        total_affected_files = target_domain.file_count
        total_affected_lines = target_domain.line_count
        
        for affected_domain_name in affected_domains:
            if affected_domain_name in self.domains:
                affected_domain = self.domains[affected_domain_name]
                total_affected_files += affected_domain.file_count
                total_affected_lines += affected_domain.line_count
        
        # Calculate dependency depth impact
        max_dependency_depth = self._calculate_max_dependency_depth(domain_name)
        
        # Calculate coupling impact
        coupling_score = len(self.reverse_graph.get(domain_name, set())) / max(len(self.domains), 1)
        
        return {
            "affected_domain_count": len(affected_domains),
            "total_affected_files": total_affected_files,
            "total_affected_lines": total_affected_lines,
            "max_dependency_depth": max_dependency_depth,
            "coupling_score": coupling_score,
            "impact_severity": self._calculate_impact_severity(len(affected_domains), coupling_score)
        }
    
    def _calculate_max_dependency_depth(self, domain_name: str) -> int:
        """Calculate maximum dependency depth from this domain"""
        max_depth = 0
        visited = set()
        
        def dfs(current: str, depth: int) -> int:
            if current in visited:
                return depth
            
            visited.add(current)
            current_max = depth
            
            for dependent in self.reverse_graph.get(current, set()):
                dependent_depth = dfs(dependent, depth + 1)
                current_max = max(current_max, dependent_depth)
            
            return current_max
        
        return dfs(domain_name, 0)
    
    def _calculate_impact_severity(self, affected_count: int, coupling_score: float) -> str:
        """Calculate overall impact severity"""
        if affected_count == 0:
            return "low"
        elif affected_count <= 2 and coupling_score < 0.3:
            return "low"
        elif affected_count <= 5 and coupling_score < 0.6:
            return "medium"
        else:
            return "high"
    
    def _generate_change_recommendations(self, domain_name: str, change_type: str, affected_domains: Set[str]) -> List[str]:
        """Generate recommendations for managing change impact"""
        recommendations = []
        
        if not affected_domains:
            recommendations.append("Change has minimal impact - safe to proceed")
            return recommendations
        
        # General recommendations based on impact
        if len(affected_domains) > 5:
            recommendations.append("High impact change - consider phased rollout")
            recommendations.append("Implement comprehensive testing strategy")
        
        if change_type == "delete":
            recommendations.extend([
                "Ensure all dependent domains have alternative implementations",
                "Consider deprecation period before deletion",
                "Update documentation and migration guides"
            ])
        elif change_type == "modify":
            recommendations.extend([
                "Maintain backward compatibility where possible",
                "Version the interface changes",
                "Coordinate with dependent domain maintainers"
            ])
        
        # Specific recommendations for highly coupled domains
        coupling_score = len(self.reverse_graph.get(domain_name, set())) / max(len(self.domains), 1)
        if coupling_score > 0.5:
            recommendations.append("Consider refactoring to reduce coupling before making changes")
        
        return recommendations
    
    def _assess_change_risk(self, domain_name: str, affected_domains: Set[str]) -> Dict[str, Any]:
        """Assess the risk level of the proposed change"""
        risk_factors = []
        risk_score = 0.0
        
        # Factor 1: Number of affected domains
        affected_count = len(affected_domains)
        if affected_count > 10:
            risk_factors.append("Very high number of affected domains")
            risk_score += 0.4
        elif affected_count > 5:
            risk_factors.append("High number of affected domains")
            risk_score += 0.3
        elif affected_count > 2:
            risk_factors.append("Moderate number of affected domains")
            risk_score += 0.2
        
        # Factor 2: Coupling level
        coupling_score = len(self.reverse_graph.get(domain_name, set())) / max(len(self.domains), 1)
        if coupling_score > 0.7:
            risk_factors.append("Very high coupling")
            risk_score += 0.3
        elif coupling_score > 0.4:
            risk_factors.append("High coupling")
            risk_score += 0.2
        
        # Factor 3: Circular dependencies involving this domain
        if self._is_in_circular_dependency(domain_name):
            risk_factors.append("Part of circular dependency")
            risk_score += 0.3
        
        # Determine risk level
        if risk_score >= 0.7:
            risk_level = "high"
        elif risk_score >= 0.4:
            risk_level = "medium"
        else:
            risk_level = "low"
        
        return {
            "risk_level": risk_level,
            "risk_score": min(1.0, risk_score),
            "risk_factors": risk_factors,
            "mitigation_strategies": self._suggest_risk_mitigation(risk_level, risk_factors)
        }
    
    def _is_in_circular_dependency(self, domain_name: str) -> bool:
        """Check if domain is part of any circular dependency"""
        detector = CircularDependencyDetector(self.domains)
        cycles = detector.detect_cycles_dfs()
        
        return any(domain_name in cycle for cycle in cycles)
    
    def _suggest_risk_mitigation(self, risk_level: str, risk_factors: List[str]) -> List[str]:
        """Suggest risk mitigation strategies"""
        strategies = []
        
        if risk_level == "high":
            strategies.extend([
                "Implement comprehensive integration testing",
                "Create detailed rollback plan",
                "Consider feature flags for gradual rollout",
                "Coordinate with all affected domain maintainers"
            ])
        elif risk_level == "medium":
            strategies.extend([
                "Implement targeted testing for affected domains",
                "Create rollback plan",
                "Notify affected domain maintainers"
            ])
        else:
            strategies.append("Standard testing and review process should be sufficient")
        
        # Specific strategies based on risk factors
        if "circular dependency" in " ".join(risk_factors).lower():
            strategies.append("Resolve circular dependencies before making changes")
        
        if "high coupling" in " ".join(risk_factors).lower():
            strategies.append("Consider refactoring to reduce coupling")
        
        return strategies


class ComprehensiveDependencyAnalyzer(DomainSystemComponent):
    """
    Main dependency analysis component that orchestrates all analysis types
    """
    
    def __init__(self, registry_manager=None, config: Optional[Dict[str, Any]] = None):
        super().__init__("dependency_analyzer", config)
        
        self.registry_manager = registry_manager
        self.project_root = Path.cwd()
        
        # Analysis components
        self.circular_detector = None
        self.orphaned_detector = None
        self.impact_analyzer = None
        
        # Configuration
        self.config_obj = get_config()
        self.parallel_analysis = self.config_obj.get("parallel_dependency_analysis", True)
        self.max_workers = self.config_obj.get("dependency_analysis_workers", 4)
        
        self.logger.info("Initialized ComprehensiveDependencyAnalyzer")
    
    def set_registry_manager(self, registry_manager):
        """Set the registry manager (dependency injection)"""
        self.registry_manager = registry_manager
    
    def set_project_root(self, project_root: str):
        """Set the project root directory"""
        self.project_root = Path(project_root)
        self.logger.info(f"Set project root to: {self.project_root}")
    
    def perform_comprehensive_analysis(self) -> Dict[str, Any]:
        """Perform all types of dependency analysis"""
        with self._time_operation("comprehensive_analysis"):
            try:
                if not self.registry_manager:
                    raise DependencyAnalysisError("Registry manager not set")
                
                # Get all domains
                domains = self.registry_manager.get_all_domains()
                if not domains:
                    return {"error": "No domains found for analysis"}
                
                # Initialize analysis components
                self._initialize_analyzers(domains)
                
                # Perform analyses
                if self.parallel_analysis:
                    results = self._parallel_comprehensive_analysis()
                else:
                    results = self._sequential_comprehensive_analysis()
                
                # Add summary and recommendations
                results["summary"] = self._generate_analysis_summary(results)
                results["recommendations"] = self._generate_comprehensive_recommendations(results)
                
                return results
                
            except Exception as e:
                self._handle_error(e, "comprehensive_analysis")
                return {"error": str(e)}
    
    def _initialize_analyzers(self, domains: DomainCollection):
        """Initialize all analyzer components"""
        self.circular_detector = CircularDependencyDetector(domains)
        self.orphaned_detector = OrphanedFileDetector(domains, self.project_root)
        self.impact_analyzer = DependencyImpactAnalyzer(domains)
    
    def _parallel_comprehensive_analysis(self) -> Dict[str, Any]:
        """Perform analysis in parallel"""
        results = {}
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit analysis tasks
            futures = {
                executor.submit(self._analyze_circular_dependencies): "circular_dependencies",
                executor.submit(self._analyze_orphaned_files): "orphaned_files",
                executor.submit(self._analyze_dependency_health): "dependency_health"
            }
            
            # Collect results
            for future in as_completed(futures):
                analysis_type = futures[future]
                try:
                    results[analysis_type] = future.result()
                except Exception as e:
                    self.logger.error(f"Parallel analysis failed for {analysis_type}: {e}")
                    results[analysis_type] = {"error": str(e)}
        
        return results
    
    def _sequential_comprehensive_analysis(self) -> Dict[str, Any]:
        """Perform analysis sequentially"""
        return {
            "circular_dependencies": self._analyze_circular_dependencies(),
            "orphaned_files": self._analyze_orphaned_files(),
            "dependency_health": self._analyze_dependency_health()
        }
    
    def _analyze_circular_dependencies(self) -> Dict[str, Any]:
        """Analyze circular dependencies"""
        try:
            # Detect cycles using multiple algorithms
            dfs_cycles = self.circular_detector.detect_cycles_dfs()
            tarjan_cycles = self.circular_detector.detect_cycles_tarjan()
            
            # Analyze each cycle
            cycle_analyses = []
            for cycle in dfs_cycles:
                analysis = self.circular_detector.analyze_cycle_impact(cycle)
                cycle_analyses.append(analysis)
            
            return {
                "cycles_found": len(dfs_cycles),
                "dfs_cycles": dfs_cycles,
                "tarjan_sccs": tarjan_cycles,
                "cycle_analyses": cycle_analyses,
                "has_circular_dependencies": len(dfs_cycles) > 0
            }
            
        except Exception as e:
            return {"error": f"Circular dependency analysis failed: {str(e)}"}
    
    def _analyze_orphaned_files(self) -> Dict[str, Any]:
        """Analyze orphaned files"""
        try:
            return self.orphaned_detector.detect_orphaned_files(include_tests=True)
        except Exception as e:
            return {"error": f"Orphaned file analysis failed: {str(e)}"}
    
    def _analyze_dependency_health(self) -> Dict[str, Any]:
        """Analyze overall dependency health"""
        try:
            domains = self.registry_manager.get_all_domains()
            health_metrics = {
                "total_domains": len(domains),
                "domains_with_dependencies": 0,
                "domains_without_dependencies": 0,
                "average_dependency_count": 0.0,
                "max_dependency_depth": 0,
                "highly_coupled_domains": [],
                "isolated_domains": []
            }
            
            total_deps = 0
            for domain_name, domain in domains.items():
                dep_count = len(domain.dependencies)
                total_deps += dep_count
                
                if dep_count > 0:
                    health_metrics["domains_with_dependencies"] += 1
                else:
                    health_metrics["domains_without_dependencies"] += 1
                    health_metrics["isolated_domains"].append(domain_name)
                
                # Check for high coupling (many dependents)
                dependents = len(self.impact_analyzer.reverse_graph.get(domain_name, set()))
                if dependents > 5:
                    health_metrics["highly_coupled_domains"].append({
                        "domain": domain_name,
                        "dependent_count": dependents
                    })
                
                # Calculate dependency depth
                depth = self.impact_analyzer._calculate_max_dependency_depth(domain_name)
                health_metrics["max_dependency_depth"] = max(health_metrics["max_dependency_depth"], depth)
            
            health_metrics["average_dependency_count"] = total_deps / max(len(domains), 1)
            
            return health_metrics
            
        except Exception as e:
            return {"error": f"Dependency health analysis failed: {str(e)}"}
    
    def _generate_analysis_summary(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate high-level summary of all analyses"""
        summary = {
            "overall_health": "unknown",
            "critical_issues": [],
            "warnings": [],
            "recommendations_count": 0
        }
        
        # Analyze circular dependencies
        circular_deps = results.get("circular_dependencies", {})
        if circular_deps.get("has_circular_dependencies", False):
            cycle_count = circular_deps.get("cycles_found", 0)
            summary["critical_issues"].append(f"Found {cycle_count} circular dependency cycles")
        
        # Analyze orphaned files
        orphaned = results.get("orphaned_files", {})
        orphaned_count = len(orphaned.get("orphaned_files", []))
        if orphaned_count > 0:
            coverage = orphaned.get("coverage_percentage", 0)
            if coverage < 80:
                summary["critical_issues"].append(f"Low pattern coverage: {coverage:.1f}%")
            else:
                summary["warnings"].append(f"{orphaned_count} orphaned files found")
        
        # Analyze dependency health
        dep_health = results.get("dependency_health", {})
        highly_coupled = len(dep_health.get("highly_coupled_domains", []))
        if highly_coupled > 0:
            summary["warnings"].append(f"{highly_coupled} highly coupled domains detected")
        
        # Determine overall health
        if summary["critical_issues"]:
            summary["overall_health"] = "critical"
        elif summary["warnings"]:
            summary["overall_health"] = "warning"
        else:
            summary["overall_health"] = "healthy"
        
        return summary
    
    def _generate_comprehensive_recommendations(self, results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate comprehensive recommendations based on all analyses"""
        recommendations = []
        
        # Circular dependency recommendations
        circular_deps = results.get("circular_dependencies", {})
        if circular_deps.get("has_circular_dependencies", False):
            for cycle_analysis in circular_deps.get("cycle_analyses", []):
                for suggestion in cycle_analysis.get("breaking_suggestions", []):
                    recommendations.append({
                        "type": "circular_dependency",
                        "priority": "high",
                        "description": f"Break circular dependency: {suggestion['break_dependency']}",
                        "approach": suggestion["suggested_approach"],
                        "alternatives": suggestion["alternative_patterns"]
                    })
        
        # Orphaned file recommendations
        orphaned = results.get("orphaned_files", {})
        for suggestion in orphaned.get("suggestions", []):
            for action in suggestion.get("suggested_actions", []):
                recommendations.append({
                    "type": "orphaned_files",
                    "priority": "medium",
                    "description": action,
                    "directory": suggestion["directory"],
                    "affected_files": len(suggestion["files"])
                })
        
        # Dependency health recommendations
        dep_health = results.get("dependency_health", {})
        for coupled_domain in dep_health.get("highly_coupled_domains", []):
            recommendations.append({
                "type": "high_coupling",
                "priority": "medium",
                "description": f"Reduce coupling for domain '{coupled_domain['domain']}'",
                "dependent_count": coupled_domain["dependent_count"],
                "approaches": [
                    "Extract common interfaces",
                    "Use dependency injection",
                    "Implement observer pattern"
                ]
            })
        
        return recommendations
    
    def analyze_domain_impact(self, domain_name: str, change_type: str = "modify") -> Dict[str, Any]:
        """Analyze impact of changes to a specific domain"""
        with self._time_operation("analyze_domain_impact"):
            try:
                if not self.registry_manager:
                    raise DependencyAnalysisError("Registry manager not set")
                
                domains = self.registry_manager.get_all_domains()
                if domain_name not in domains:
                    return {"error": f"Domain '{domain_name}' not found"}
                
                # Initialize impact analyzer if needed
                if not self.impact_analyzer:
                    self.impact_analyzer = DependencyImpactAnalyzer(domains)
                
                return self.impact_analyzer.analyze_change_impact(domain_name, change_type)
                
            except Exception as e:
                self._handle_error(e, "analyze_domain_impact")
                return {"error": str(e)}
    
    def get_analyzer_stats(self) -> Dict[str, Any]:
        """Get dependency analyzer statistics"""
        return {
            "component_stats": self.get_module_status(),
            "project_root": str(self.project_root),
            "parallel_analysis_enabled": self.parallel_analysis,
            "max_workers": self.max_workers,
            "analyzers_initialized": {
                "circular_detector": self.circular_detector is not None,
                "orphaned_detector": self.orphaned_detector is not None,
                "impact_analyzer": self.impact_analyzer is not None
            },
            "performance_metrics": self.performance_metrics
        }