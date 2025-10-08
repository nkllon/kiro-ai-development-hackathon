#!/usr/bin/env python3
"""
Orphaned Solution Scanner
========================

Background task to scan for implementations without corresponding specifications,
producing structured reports for independent agents to reverse engineer specs.

Implements the Ad-Hoc Solution to Specification Governance rule.
"""

import asyncio
import ast
import json
import logging
import re
import sys
from collections import defaultdict
from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional, Set, Tuple
import subprocess

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from src.rm_ddd.core.unified_reflective_module import ReflectiveModule


@dataclass
class ImplementationSignature:
    """Signature of a discovered implementation."""
    file_path: Path
    module_name: str
    class_names: List[str] = field(default_factory=list)
    function_names: List[str] = field(default_factory=list)
    imports: List[str] = field(default_factory=list)
    docstring: Optional[str] = None
    line_count: int = 0
    complexity_score: float = 0.0
    last_modified: Optional[datetime] = None
    git_history: List[str] = field(default_factory=list)


@dataclass
class SpecificationReference:
    """Reference to an existing specification."""
    spec_path: Path
    spec_name: str
    requirements_file: Optional[Path] = None
    design_file: Optional[Path] = None
    tasks_file: Optional[Path] = None
    coverage_keywords: List[str] = field(default_factory=list)


@dataclass
class OrphanedSolution:
    """An implementation without corresponding specification."""
    implementation: ImplementationSignature
    orphan_confidence: float  # 0.0 = definitely has spec, 1.0 = definitely orphaned
    potential_specs: List[SpecificationReference] = field(default_factory=list)
    suggested_spec_name: str = ""
    reverse_engineering_priority: int = 1  # 1=high, 2=medium, 3=low
    estimated_effort_hours: int = 0
    business_value_score: float = 0.0
    technical_complexity: str = "medium"
    dependencies: List[str] = field(default_factory=list)
    integration_points: List[str] = field(default_factory=list)
    usage_patterns: List[str] = field(default_factory=list)


@dataclass
class ScanReport:
    """Complete scan report for orphaned solutions."""
    scan_timestamp: datetime
    total_implementations: int
    total_specifications: int
    orphaned_solutions: List[OrphanedSolution]
    coverage_percentage: float
    high_priority_orphans: int
    recommendations: List[str] = field(default_factory=list)
    next_scan_suggested: datetime = None


class OrphanedSolutionScanner(ReflectiveModule):
    """
    Scans repository for implementations without corresponding specifications.
    Produces structured reports for independent agents to reverse engineer specs.
    """
    
    def __init__(self):
        super().__init__()
        self.module_id = "OrphanedSolutionScanner"
        self._logger = logging.getLogger(f"governance.{self.__class__.__name__}")
        
        # Scan configuration
        self.source_directories = [
            Path("src"),
            Path("scripts"),
            Path("tests")
        ]
        self.spec_directory = Path(".kiro/specs")
        self.exclude_patterns = [
            "__pycache__",
            ".git",
            ".pytest_cache",
            "node_modules",
            ".venv",
            "venv"
        ]
        
        # Analysis thresholds
        self.min_line_count = 10  # Minimum lines to consider significant (very low for testing)
        self.high_complexity_threshold = 0.7
        self.high_priority_line_threshold = 100  # Reduced threshold
        
        # Discovered data
        self.implementations: List[ImplementationSignature] = []
        self.specifications: List[SpecificationReference] = []
        self.orphaned_solutions: List[OrphanedSolution] = []
    
    def get_module_info(self) -> Dict[str, Any]:
        """Get module information."""
        return {
            "module_id": self.module_id,
            "version": "1.0.0",
            "description": "Scans for implementations without specifications",
            "capabilities": ["orphaned_solution_detection", "spec_matching", "priority_analysis"]
        }
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get health status."""
        return {
            "status": "healthy",
            "last_scan": getattr(self, '_last_scan_time', None),
            "implementations_found": len(getattr(self, 'implementations', [])),
            "orphaned_solutions": len(getattr(self, 'orphaned_solutions', []))
        }
    
    def get_capabilities(self) -> List[str]:
        """Get scanner capabilities."""
        return [
            "python_file_analysis",
            "ast_parsing", 
            "spec_matching",
            "priority_calculation",
            "report_generation"
        ]
    
    def graceful_degradation(self) -> Dict[str, Any]:
        """Handle graceful degradation."""
        return {
            "degraded_mode": False,
            "available_features": self.get_capabilities(),
            "limitations": []
        }
        self.implementations: List[ImplementationSignature] = []
        self.specifications: List[SpecificationReference] = []
        self.orphaned_solutions: List[OrphanedSolution] = []
    
    async def scan_repository(self) -> ScanReport:
        """Perform comprehensive repository scan for orphaned solutions."""
        self._logger.info("Starting orphaned solution scan...")
        
        scan_start = datetime.now()
        
        # Phase 1: Discover all implementations
        await self._discover_implementations()
        
        # Phase 2: Discover all specifications
        await self._discover_specifications()
        
        # Phase 3: Match implementations to specifications
        await self._match_implementations_to_specs()
        
        # Phase 4: Analyze orphaned solutions
        await self._analyze_orphaned_solutions()
        
        # Phase 5: Generate comprehensive report
        report = await self._generate_scan_report(scan_start)
        
        self._logger.info(f"Scan completed: {len(self.orphaned_solutions)} orphaned solutions found")
        return report
    
    async def _discover_implementations(self):
        """Discover all significant implementations in the repository."""
        self._logger.info("Discovering implementations...")
        
        total_files = 0
        excluded_files = 0
        analyzed_files = 0
        
        for source_dir in self.source_directories:
            if not source_dir.exists():
                self._logger.warning(f"Source directory {source_dir} does not exist")
                continue
                
            for py_file in source_dir.rglob("*.py"):
                total_files += 1
                
                if self._should_exclude_file(py_file):
                    excluded_files += 1
                    continue
                
                try:
                    signature = await self._analyze_python_file(py_file)
                    analyzed_files += 1
                    
                    if signature:
                        if self._is_significant_implementation(signature):
                            self.implementations.append(signature)
                            self._logger.info(f"Found significant implementation: {py_file} ({signature.line_count} lines, {len(signature.class_names)} classes, {len(signature.function_names)} functions)")
                        else:
                            # Log first few non-significant ones for debugging
                            if len(self.implementations) < 5:
                                self._logger.info(f"Implementation not significant: {py_file} ({signature.line_count} lines, {len(signature.class_names)} classes, {len(signature.function_names)} functions, complexity: {signature.complexity_score:.2f})")
                    else:
                        if analyzed_files < 5:  # Log first few parsing failures
                            self._logger.info(f"Failed to parse: {py_file}")
                except Exception as e:
                    self._logger.warning(f"Failed to analyze {py_file}: {e}")
        
        self._logger.info(f"File analysis: {total_files} total, {excluded_files} excluded, {analyzed_files} analyzed")
        
        self._logger.info(f"Discovered {len(self.implementations)} significant implementations")
    
    async def _discover_specifications(self):
        """Discover all existing specifications."""
        self._logger.info("Discovering specifications...")
        
        if not self.spec_directory.exists():
            self._logger.warning(f"Spec directory {self.spec_directory} does not exist")
            return
        
        for spec_dir in self.spec_directory.iterdir():
            if not spec_dir.is_dir():
                continue
            
            spec_ref = SpecificationReference(
                spec_path=spec_dir,
                spec_name=spec_dir.name
            )
            
            # Look for standard spec files
            requirements_file = spec_dir / "requirements.md"
            if requirements_file.exists():
                spec_ref.requirements_file = requirements_file
                spec_ref.coverage_keywords.extend(
                    await self._extract_keywords_from_file(requirements_file)
                )
            
            design_file = spec_dir / "design.md"
            if design_file.exists():
                spec_ref.design_file = design_file
                spec_ref.coverage_keywords.extend(
                    await self._extract_keywords_from_file(design_file)
                )
            
            tasks_file = spec_dir / "tasks.md"
            if tasks_file.exists():
                spec_ref.tasks_file = tasks_file
            
            self.specifications.append(spec_ref)
        
        self._logger.info(f"Discovered {len(self.specifications)} specifications")
    
    async def _analyze_python_file(self, file_path: Path) -> Optional[ImplementationSignature]:
        """Analyze a Python file to extract implementation signature."""
        try:
            content = file_path.read_text(encoding='utf-8', errors='ignore')
            tree = ast.parse(content, filename=str(file_path))
            
            signature = ImplementationSignature(
                file_path=file_path,
                module_name=self._path_to_module_name(file_path),
                line_count=len(content.splitlines())
            )
            
            # Extract classes and functions
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    signature.class_names.append(node.name)
                elif isinstance(node, ast.FunctionDef):
                    signature.function_names.append(node.name)
                elif isinstance(node, ast.Import):
                    for alias in node.names:
                        signature.imports.append(alias.name)
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        signature.imports.append(node.module)
            
            # Extract module docstring
            if (tree.body and isinstance(tree.body[0], ast.Expr) and 
                isinstance(tree.body[0].value, ast.Constant) and 
                isinstance(tree.body[0].value.value, str)):
                signature.docstring = tree.body[0].value.value
            
            # Calculate complexity score
            signature.complexity_score = self._calculate_complexity_score(tree)
            
            # Get file modification time
            signature.last_modified = datetime.fromtimestamp(file_path.stat().st_mtime)
            
            # Get git history (if available)
            signature.git_history = await self._get_git_history(file_path)
            
            return signature
            
        except Exception as e:
            self._logger.debug(f"Failed to parse {file_path}: {e}")
            return None
    
    def _path_to_module_name(self, file_path: Path) -> str:
        """Convert file path to Python module name."""
        # Remove .py extension and convert path separators to dots
        relative_path = file_path.relative_to(Path.cwd())
        module_parts = list(relative_path.parts[:-1]) + [relative_path.stem]
        return ".".join(module_parts)
    
    def _calculate_complexity_score(self, tree: ast.AST) -> float:
        """Calculate complexity score for AST tree."""
        complexity_indicators = 0
        total_nodes = 0
        
        for node in ast.walk(tree):
            total_nodes += 1
            
            # Count complexity indicators
            if isinstance(node, (ast.If, ast.While, ast.For, ast.Try, ast.With)):
                complexity_indicators += 1
            elif isinstance(node, ast.FunctionDef):
                complexity_indicators += len(node.args.args)  # Parameter count
            elif isinstance(node, ast.ClassDef):
                complexity_indicators += len(node.bases)  # Inheritance count
        
        return complexity_indicators / max(total_nodes, 1)
    
    async def _get_git_history(self, file_path: Path) -> List[str]:
        """Get recent git history for a file."""
        try:
            result = subprocess.run([
                "git", "log", "--oneline", "-5", str(file_path)
            ], capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                return result.stdout.strip().split('\n')
        except Exception:
            pass
        
        return []
    
    def _should_exclude_file(self, file_path: Path) -> bool:
        """Check if file should be excluded from analysis."""
        path_str = str(file_path)
        
        for pattern in self.exclude_patterns:
            if pattern in path_str:
                return True
        
        # Exclude test files from implementation analysis
        if "test_" in file_path.name or file_path.name.startswith("test"):
            return True
        
        # Exclude __init__.py files unless they have significant content
        if file_path.name == "__init__.py":
            try:
                content = file_path.read_text()
                if len(content.strip()) < 100:  # Minimal __init__.py
                    return True
            except Exception:
                return True
        
        return False
    
    def _is_significant_implementation(self, signature: ImplementationSignature) -> bool:
        """Determine if implementation is significant enough to require a spec."""
        # Must have minimum line count
        if signature.line_count < self.min_line_count:
            return False
        
        # Accept if it has any classes (classes usually indicate significant functionality)
        if signature.class_names:
            return True
        
        # Accept if it has many functions (indicates substantial functionality)
        if len(signature.function_names) >= 5:
            return True
        
        # Accept if it's complex enough
        if signature.complexity_score > 0.3:
            return True
        
        # Accept if it's reasonably long with some functions
        if signature.line_count > 50 and len(signature.function_names) >= 2:
            return True
        
        return False
    
    async def _extract_keywords_from_file(self, file_path: Path) -> List[str]:
        """Extract keywords from a specification file."""
        try:
            content = file_path.read_text(encoding='utf-8').lower()
            
            # Extract meaningful words (excluding common words)
            words = re.findall(r'\b[a-z]{3,}\b', content)
            
            # Filter out common words
            common_words = {
                'the', 'and', 'for', 'are', 'but', 'not', 'you', 'all', 'can', 'had', 
                'her', 'was', 'one', 'our', 'out', 'day', 'get', 'has', 'him', 'his', 
                'how', 'its', 'may', 'new', 'now', 'old', 'see', 'two', 'who', 'boy', 
                'did', 'she', 'use', 'way', 'will', 'when', 'that', 'this', 'with',
                'shall', 'should', 'must', 'will', 'then', 'when', 'user', 'story',
                'requirement', 'acceptance', 'criteria'
            }
            
            keywords = [word for word in set(words) if word not in common_words]
            return keywords[:20]  # Top 20 keywords
            
        except Exception:
            return []
    
    async def _match_implementations_to_specs(self):
        """Match implementations to existing specifications."""
        self._logger.info("Matching implementations to specifications...")
        
        for impl in self.implementations:
            orphan_confidence = 1.0  # Start assuming orphaned
            potential_specs = []
            
            # Check for direct matches
            for spec in self.specifications:
                match_score = self._calculate_spec_match_score(impl, spec)
                
                if match_score > 0.3:  # Potential match
                    potential_specs.append(spec)
                    orphan_confidence -= match_score
            
            # Ensure confidence is between 0 and 1
            orphan_confidence = max(0.0, min(1.0, orphan_confidence))
            
            # Only consider as orphaned if confidence > 0.7
            if orphan_confidence > 0.7:
                orphan = OrphanedSolution(
                    implementation=impl,
                    orphan_confidence=orphan_confidence,
                    potential_specs=potential_specs,
                    suggested_spec_name=self._suggest_spec_name(impl)
                )
                self.orphaned_solutions.append(orphan)
        
        self._logger.info(f"Found {len(self.orphaned_solutions)} orphaned solutions")
    
    def _calculate_spec_match_score(self, impl: ImplementationSignature, spec: SpecificationReference) -> float:
        """Calculate how well an implementation matches a specification."""
        score = 0.0
        
        # Check module name similarity
        impl_words = set(impl.module_name.lower().split('.'))
        spec_words = set(spec.spec_name.lower().replace('-', ' ').replace('_', ' ').split())
        
        if impl_words & spec_words:  # Common words
            score += 0.4
        
        # Check class name matches
        for class_name in impl.class_names:
            class_words = set(re.findall(r'[A-Z][a-z]*', class_name))
            if any(word.lower() in spec.coverage_keywords for word in class_words):
                score += 0.3
        
        # Check keyword overlap
        impl_keywords = set()
        if impl.docstring:
            impl_keywords.update(re.findall(r'\b[a-z]{3,}\b', impl.docstring.lower()))
        
        keyword_overlap = len(impl_keywords & set(spec.coverage_keywords))
        if keyword_overlap > 0:
            score += min(0.3, keyword_overlap * 0.1)
        
        return min(1.0, score)
    
    def _suggest_spec_name(self, impl: ImplementationSignature) -> str:
        """Suggest a specification name for an implementation."""
        # Use the main class name if available
        if impl.class_names:
            main_class = impl.class_names[0]
            # Convert CamelCase to kebab-case
            spec_name = re.sub(r'([A-Z])', r'-\1', main_class).lower().strip('-')
            return spec_name
        
        # Use module name
        module_parts = impl.module_name.split('.')
        if len(module_parts) > 1:
            return '-'.join(module_parts[-2:]).replace('_', '-')
        
        return module_parts[-1].replace('_', '-')
    
    async def _analyze_orphaned_solutions(self):
        """Analyze orphaned solutions to determine priority and effort."""
        self._logger.info("Analyzing orphaned solutions...")
        
        for orphan in self.orphaned_solutions:
            impl = orphan.implementation
            
            # Calculate reverse engineering priority
            priority_score = 0
            
            # High line count = higher priority
            if impl.line_count > self.high_priority_line_threshold:
                priority_score += 3
            elif impl.line_count > 100:
                priority_score += 2
            else:
                priority_score += 1
            
            # High complexity = higher priority
            if impl.complexity_score > self.high_complexity_threshold:
                priority_score += 2
            
            # Recent modifications = higher priority
            if impl.last_modified and (datetime.now() - impl.last_modified).days < 30:
                priority_score += 2
            
            # Multiple classes = higher priority
            if len(impl.class_names) > 2:
                priority_score += 1
            
            # Set priority (1=high, 2=medium, 3=low)
            if priority_score >= 6:
                orphan.reverse_engineering_priority = 1
            elif priority_score >= 4:
                orphan.reverse_engineering_priority = 2
            else:
                orphan.reverse_engineering_priority = 3
            
            # Estimate effort in hours
            base_effort = max(2, impl.line_count // 50)  # 2 hours minimum, 1 hour per 50 lines
            complexity_multiplier = 1 + impl.complexity_score
            orphan.estimated_effort_hours = int(base_effort * complexity_multiplier)
            
            # Calculate business value score
            orphan.business_value_score = self._calculate_business_value(impl)
            
            # Determine technical complexity
            if impl.complexity_score > 0.7:
                orphan.technical_complexity = "high"
            elif impl.complexity_score > 0.4:
                orphan.technical_complexity = "medium"
            else:
                orphan.technical_complexity = "low"
            
            # Analyze dependencies and integration points
            orphan.dependencies = self._extract_dependencies(impl)
            orphan.integration_points = self._identify_integration_points(impl)
            orphan.usage_patterns = await self._analyze_usage_patterns(impl)
    
    def _calculate_business_value(self, impl: ImplementationSignature) -> float:
        """Calculate business value score for an implementation."""
        value_score = 0.5  # Base score
        
        # Higher value for core system components
        if any(keyword in impl.module_name.lower() for keyword in 
               ['core', 'engine', 'manager', 'orchestrator', 'system']):
            value_score += 0.3
        
        # Higher value for user-facing components
        if any(keyword in impl.module_name.lower() for keyword in 
               ['api', 'cli', 'interface', 'service', 'handler']):
            value_score += 0.2
        
        # Higher value for recent activity
        if impl.git_history and len(impl.git_history) > 2:
            value_score += 0.2
        
        # Higher value for complex implementations
        if impl.complexity_score > 0.6:
            value_score += 0.1
        
        return min(1.0, value_score)
    
    def _extract_dependencies(self, impl: ImplementationSignature) -> List[str]:
        """Extract key dependencies from implementation."""
        dependencies = []
        
        # Add significant imports (exclude standard library)
        for imp in impl.imports:
            if not imp.startswith(('os', 'sys', 'json', 'datetime', 'pathlib', 're')):
                dependencies.append(imp)
        
        return dependencies[:10]  # Top 10 dependencies
    
    def _identify_integration_points(self, impl: ImplementationSignature) -> List[str]:
        """Identify integration points for an implementation."""
        integration_points = []
        
        # Check for common integration patterns
        if 'ReflectiveModule' in impl.imports or any('ReflectiveModule' in cls for cls in impl.class_names):
            integration_points.append("Beast Mode Framework")
        
        if any('test' in func.lower() for func in impl.function_names):
            integration_points.append("Testing Framework")
        
        if any('api' in name.lower() for name in impl.class_names + impl.function_names):
            integration_points.append("API Layer")
        
        if any('cli' in name.lower() for name in impl.class_names + impl.function_names):
            integration_points.append("Command Line Interface")
        
        return integration_points
    
    async def _analyze_usage_patterns(self, impl: ImplementationSignature) -> List[str]:
        """Analyze usage patterns for an implementation."""
        patterns = []
        
        # Check for common patterns based on class and function names
        if any('manager' in name.lower() for name in impl.class_names):
            patterns.append("Resource Management")
        
        if any('orchestrator' in name.lower() for name in impl.class_names):
            patterns.append("Workflow Orchestration")
        
        if any('validator' in name.lower() for name in impl.class_names):
            patterns.append("Data Validation")
        
        if any('generator' in name.lower() for name in impl.class_names):
            patterns.append("Code Generation")
        
        if any('analyzer' in name.lower() for name in impl.class_names):
            patterns.append("Data Analysis")
        
        return patterns
    
    async def _generate_scan_report(self, scan_start: datetime) -> ScanReport:
        """Generate comprehensive scan report."""
        self._logger.info("Generating scan report...")
        
        high_priority_count = sum(1 for o in self.orphaned_solutions if o.reverse_engineering_priority == 1)
        coverage_percentage = ((len(self.implementations) - len(self.orphaned_solutions)) / 
                              max(len(self.implementations), 1)) * 100
        
        recommendations = self._generate_recommendations()
        
        report = ScanReport(
            scan_timestamp=scan_start,
            total_implementations=len(self.implementations),
            total_specifications=len(self.specifications),
            orphaned_solutions=self.orphaned_solutions,
            coverage_percentage=coverage_percentage,
            high_priority_orphans=high_priority_count,
            recommendations=recommendations,
            next_scan_suggested=datetime.now() + timedelta(days=1)
        )
        
        return report
    
    def _generate_recommendations(self) -> List[str]:
        """Generate recommendations based on scan results."""
        recommendations = []
        
        high_priority = [o for o in self.orphaned_solutions if o.reverse_engineering_priority == 1]
        medium_priority = [o for o in self.orphaned_solutions if o.reverse_engineering_priority == 2]
        
        if high_priority:
            recommendations.append(
                f"URGENT: {len(high_priority)} high-priority implementations need immediate spec creation"
            )
        
        if medium_priority:
            recommendations.append(
                f"MEDIUM: {len(medium_priority)} medium-priority implementations should be spec'd within 2 weeks"
            )
        
        total_effort = sum(o.estimated_effort_hours for o in self.orphaned_solutions)
        if total_effort > 40:
            recommendations.append(
                f"Consider dedicating {total_effort // 8} developer-days to spec creation backlog"
            )
        
        if len(self.orphaned_solutions) > len(self.specifications):
            recommendations.append(
                "More implementations than specs detected - consider spec-first development approach"
            )
        
        return recommendations
    
    def save_report_json(self, report: ScanReport, output_path: Path):
        """Save report as JSON for independent agent consumption."""
        report_data = asdict(report)
        
        # Convert datetime objects to ISO strings
        def convert_datetime(obj):
            if isinstance(obj, datetime):
                return obj.isoformat()
            elif isinstance(obj, Path):
                return str(obj)
            elif isinstance(obj, dict):
                return {k: convert_datetime(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [convert_datetime(item) for item in obj]
            return obj
        
        report_data = convert_datetime(report_data)
        
        with open(output_path, 'w') as f:
            json.dump(report_data, f, indent=2)
        
        self._logger.info(f"Report saved to {output_path}")
    
    def save_report_markdown(self, report: ScanReport, output_path: Path):
        """Save report as Markdown for human consumption."""
        md_content = f"""# Orphaned Solution Scan Report

**Scan Date**: {report.scan_timestamp.strftime('%Y-%m-%d %H:%M:%S')}  
**Coverage**: {report.coverage_percentage:.1f}%  
**Total Implementations**: {report.total_implementations}  
**Total Specifications**: {report.total_specifications}  
**Orphaned Solutions**: {len(report.orphaned_solutions)}  
**High Priority**: {report.high_priority_orphans}  

## Executive Summary

{len(report.orphaned_solutions)} implementations were found without corresponding specifications, representing {100 - report.coverage_percentage:.1f}% of the codebase that lacks proper documentation.

## High Priority Orphaned Solutions

"""
        
        high_priority = [o for o in report.orphaned_solutions if o.reverse_engineering_priority == 1]
        for orphan in high_priority:
            impl = orphan.implementation
            md_content += f"""### {impl.module_name}

- **File**: `{impl.file_path}`
- **Classes**: {', '.join(impl.class_names) if impl.class_names else 'None'}
- **Lines**: {impl.line_count}
- **Complexity**: {impl.complexity_score:.2f}
- **Estimated Effort**: {orphan.estimated_effort_hours} hours
- **Business Value**: {orphan.business_value_score:.2f}
- **Suggested Spec**: `{orphan.suggested_spec_name}`

**Dependencies**: {', '.join(orphan.dependencies[:5])}  
**Integration Points**: {', '.join(orphan.integration_points)}  
**Usage Patterns**: {', '.join(orphan.usage_patterns)}  

"""
        
        md_content += f"""## Recommendations

"""
        for rec in report.recommendations:
            md_content += f"- {rec}\n"
        
        md_content += f"""
## All Orphaned Solutions

| Module | Priority | Lines | Effort (hrs) | Suggested Spec |
|--------|----------|-------|--------------|----------------|
"""
        
        for orphan in sorted(report.orphaned_solutions, key=lambda x: x.reverse_engineering_priority):
            priority_str = {1: "HIGH", 2: "MEDIUM", 3: "LOW"}[orphan.reverse_engineering_priority]
            md_content += f"| `{orphan.implementation.module_name}` | {priority_str} | {orphan.implementation.line_count} | {orphan.estimated_effort_hours} | `{orphan.suggested_spec_name}` |\n"
        
        with open(output_path, 'w') as f:
            f.write(md_content)
        
        self._logger.info(f"Markdown report saved to {output_path}")


async def main():
    """Main entry point for orphaned solution scanning."""
    # Enable debug logging
    logging.basicConfig(level=logging.INFO)
    
    scanner = OrphanedSolutionScanner()
    
    print("🔍 Starting Orphaned Solution Scan...")
    print("=" * 50)
    
    # Perform scan
    report = await scanner.scan_repository()
    
    # Save reports
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    json_path = Path(f"reports/orphaned_solutions_{timestamp}.json")
    md_path = Path(f"reports/orphaned_solutions_{timestamp}.md")
    
    # Ensure reports directory exists
    json_path.parent.mkdir(exist_ok=True)
    
    scanner.save_report_json(report, json_path)
    scanner.save_report_markdown(report, md_path)
    
    # Print summary
    print(f"\n📊 Scan Results:")
    print(f"   Total Implementations: {report.total_implementations}")
    print(f"   Total Specifications: {report.total_specifications}")
    print(f"   Orphaned Solutions: {len(report.orphaned_solutions)}")
    print(f"   Coverage: {report.coverage_percentage:.1f}%")
    print(f"   High Priority: {report.high_priority_orphans}")
    
    print(f"\n📁 Reports Generated:")
    print(f"   JSON: {json_path}")
    print(f"   Markdown: {md_path}")
    
    print(f"\n💡 Recommendations:")
    for rec in report.recommendations:
        print(f"   - {rec}")
    
    return report


if __name__ == "__main__":
    asyncio.run(main())