#!/usr/bin/env python3
"""
Repository-Wide Refactoring Engine

This script implements the systematic refactoring approach we used for models.py
and applies it to the entire repository to achieve RM-DDD compliance.

Key Features:
- Analyzes all Python files for size violations
- Groups related classes into domain-specific modules
- Maintains interface consistency
- Preserves functionality while improving maintainability
- Generates comprehensive refactoring reports
"""

import os
import ast
import json
import shutil
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class FileAnalysis:
    """Analysis result for a single Python file"""
    file_path: str
    line_count: int
    class_count: int
    function_count: int
    import_count: int
    is_large: bool
    classes: List[str]
    functions: List[str]
    imports: List[str]
    dependencies: List[str]
    domain: Optional[str] = None
    refactoring_priority: int = 0
    suggested_modules: List[str] = None

@dataclass
class RefactoringPlan:
    """Plan for refactoring a large file"""
    source_file: str
    target_modules: List[str]
    class_assignments: Dict[str, str]  # class_name -> target_module
    function_assignments: Dict[str, str]  # function_name -> target_module
    dependencies: List[str]
    estimated_effort: int  # 1-5 scale
    risk_level: str  # low, medium, high

class RepositoryRefactoringEngine:
    """Main engine for repository-wide refactoring"""
    
    def __init__(self, src_dir: str = "src"):
        self.src_dir = Path(src_dir)
        self.analysis_results: List[FileAnalysis] = []
        self.refactoring_plans: List[RefactoringPlan] = []
        self.domain_patterns = self._load_domain_patterns()
        
    def _load_domain_patterns(self) -> Dict[str, List[str]]:
        """Load domain patterns for automatic classification"""
        return {
            "core": ["base", "core", "foundation", "common", "utils"],
            "models": ["model", "data", "entity", "schema", "dto"],
            "services": ["service", "manager", "handler", "processor", "engine"],
            "api": ["api", "client", "endpoint", "controller", "route"],
            "validation": ["validator", "validation", "checker", "verifier"],
            "testing": ["test", "spec", "mock", "fixture", "stub"],
            "integration": ["integration", "adapter", "bridge", "connector"],
            "monitoring": ["monitor", "metrics", "logging", "health", "status"],
            "configuration": ["config", "settings", "options", "preferences"],
            "storage": ["storage", "repository", "dao", "persistence", "database"],
            "communication": ["message", "event", "notification", "pubsub"],
            "security": ["auth", "security", "permission", "access", "encryption"],
            "ui": ["ui", "view", "component", "widget", "interface"],
            "workflow": ["workflow", "pipeline", "orchestration", "coordination"],
            "analysis": ["analysis", "analytics", "reporting", "insights"]
        }
    
    def analyze_repository(self) -> Dict[str, Any]:
        """Analyze entire repository for refactoring opportunities"""
        logger.info("🔍 Starting repository analysis...")
        
        all_files = []
        for root, dirs, files in os.walk(self.src_dir):
            for file in files:
                if file.endswith('.py'):
                    file_path = os.path.join(root, file)
                    analysis = self._analyze_file(file_path)
                    if analysis:
                        all_files.append(analysis)
        
        self.analysis_results = all_files
        
        # Generate comprehensive report
        report = self._generate_analysis_report()
        
        logger.info(f"✅ Analysis complete: {len(all_files)} files analyzed")
        return report
    
    def _analyze_file(self, file_path: str) -> Optional[FileAnalysis]:
        """Analyze a single Python file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                lines = content.split('\n')
                line_count = len(lines)
                
                # Parse AST
                try:
                    tree = ast.parse(content)
                    
                    # Extract classes
                    classes = []
                    for node in ast.walk(tree):
                        if isinstance(node, ast.ClassDef):
                            classes.append(node.name)
                    
                    # Extract functions
                    functions = []
                    for node in ast.walk(tree):
                        if isinstance(node, ast.FunctionDef):
                            functions.append(node.name)
                    
                    # Extract imports
                    imports = []
                    dependencies = []
                    for node in ast.walk(tree):
                        if isinstance(node, ast.Import):
                            for alias in node.names:
                                imports.append(alias.name)
                                dependencies.append(alias.name.split('.')[0])
                        elif isinstance(node, ast.ImportFrom):
                            if node.module:
                                imports.append(node.module)
                                dependencies.append(node.module.split('.')[0])
                    
                    # Determine domain
                    domain = self._classify_domain(file_path, classes, functions)
                    
                    # Calculate refactoring priority
                    priority = self._calculate_priority(line_count, len(classes), len(functions))
                    
                    return FileAnalysis(
                        file_path=file_path,
                        line_count=line_count,
                        class_count=len(classes),
                        function_count=len(functions),
                        import_count=len(imports),
                        is_large=line_count > 300,
                        classes=classes,
                        functions=functions,
                        imports=imports,
                        dependencies=list(set(dependencies)),
                        domain=domain,
                        refactoring_priority=priority
                    )
                    
                except SyntaxError as e:
                    logger.warning(f"Syntax error in {file_path}: {e}")
                    return None
                    
        except Exception as e:
            logger.error(f"Error analyzing {file_path}: {e}")
            return None
    
    def _classify_domain(self, file_path: str, classes: List[str], functions: List[str]) -> str:
        """Classify file domain based on path, classes, and functions"""
        path_lower = file_path.lower()
        all_names = classes + functions
        all_names_lower = [name.lower() for name in all_names]
        
        # Score each domain
        domain_scores = {}
        for domain, patterns in self.domain_patterns.items():
            score = 0
            for pattern in patterns:
                if pattern in path_lower:
                    score += 2  # Path matches are stronger
                for name in all_names_lower:
                    if pattern in name:
                        score += 1
            domain_scores[domain] = score
        
        # Return highest scoring domain
        if domain_scores:
            return max(domain_scores, key=domain_scores.get)
        return "core"
    
    def _calculate_priority(self, line_count: int, class_count: int, function_count: int) -> int:
        """Calculate refactoring priority (1-5, 5 being highest)"""
        priority = 1
        
        # Size-based priority
        if line_count > 1000:
            priority += 2
        elif line_count > 500:
            priority += 1
        
        # Complexity-based priority
        if class_count > 10:
            priority += 1
        if function_count > 50:
            priority += 1
        
        return min(priority, 5)
    
    def _generate_analysis_report(self) -> Dict[str, Any]:
        """Generate comprehensive analysis report"""
        valid_files = [f for f in self.analysis_results if f is not None]
        large_files = [f for f in valid_files if f.is_large]
        
        # Group by domain
        domain_stats = {}
        for file in valid_files:
            domain = file.domain or "unknown"
            if domain not in domain_stats:
                domain_stats[domain] = {"total": 0, "large": 0, "lines": 0}
            domain_stats[domain]["total"] += 1
            if file.is_large:
                domain_stats[domain]["large"] += 1
            domain_stats[domain]["lines"] += file.line_count
        
        # Calculate metrics
        total_lines = sum(f.line_count for f in valid_files)
        total_classes = sum(f.class_count for f in valid_files)
        total_functions = sum(f.function_count for f in valid_files)
        compliance_rate = ((len(valid_files) - len(large_files)) / len(valid_files)) * 100 if valid_files else 0
        
        return {
            "summary": {
                "total_files": len(valid_files),
                "large_files": len(large_files),
                "compliance_rate": compliance_rate,
                "total_lines": total_lines,
                "total_classes": total_classes,
                "total_functions": total_functions,
                "average_file_size": total_lines // len(valid_files) if valid_files else 0
            },
            "domain_breakdown": domain_stats,
            "largest_files": sorted(large_files, key=lambda x: x.line_count, reverse=True)[:20],
            "priority_files": sorted([f for f in large_files if f.refactoring_priority >= 4], 
                                   key=lambda x: x.refactoring_priority, reverse=True)[:10],
            "analysis_timestamp": datetime.now().isoformat()
        }
    
    def generate_refactoring_plans(self) -> List[RefactoringPlan]:
        """Generate refactoring plans for large files"""
        logger.info("📋 Generating refactoring plans...")
        
        large_files = [f for f in self.analysis_results if f.is_large]
        plans = []
        
        for file_analysis in large_files:
            plan = self._create_refactoring_plan(file_analysis)
            if plan:
                plans.append(plan)
        
        self.refactoring_plans = plans
        logger.info(f"✅ Generated {len(plans)} refactoring plans")
        return plans
    
    def _create_refactoring_plan(self, file_analysis: FileAnalysis) -> Optional[RefactoringPlan]:
        """Create refactoring plan for a single file"""
        if not file_analysis.classes and not file_analysis.functions:
            return None
        
        # Determine target modules based on domain and content
        domain = file_analysis.domain or "core"
        base_name = Path(file_analysis.file_path).stem
        
        # Create module suggestions
        suggested_modules = []
        class_assignments = {}
        function_assignments = {}
        
        # Group classes by functionality
        class_groups = self._group_classes_by_functionality(file_analysis.classes)
        
        for group_name, classes in class_groups.items():
            module_name = f"{base_name}_{group_name}.py"
            suggested_modules.append(module_name)
            for class_name in classes:
                class_assignments[class_name] = module_name
        
        # Group functions by functionality
        function_groups = self._group_functions_by_functionality(file_analysis.functions)
        
        for group_name, functions in function_groups.items():
            module_name = f"{base_name}_{group_name}.py"
            if module_name not in suggested_modules:
                suggested_modules.append(module_name)
            for function_name in functions:
                function_assignments[function_name] = module_name
        
        # Calculate effort and risk
        effort = self._calculate_effort(file_analysis)
        risk = self._calculate_risk(file_analysis)
        
        return RefactoringPlan(
            source_file=file_analysis.file_path,
            target_modules=suggested_modules,
            class_assignments=class_assignments,
            function_assignments=function_assignments,
            dependencies=file_analysis.dependencies,
            estimated_effort=effort,
            risk_level=risk
        )
    
    def _group_classes_by_functionality(self, classes: List[str]) -> Dict[str, List[str]]:
        """Group classes by functionality patterns"""
        groups = {
            "models": [],
            "services": [],
            "handlers": [],
            "utils": [],
            "core": []
        }
        
        for class_name in classes:
            class_lower = class_name.lower()
            if any(pattern in class_lower for pattern in ["model", "data", "entity", "schema"]):
                groups["models"].append(class_name)
            elif any(pattern in class_lower for pattern in ["service", "manager", "processor", "engine"]):
                groups["services"].append(class_name)
            elif any(pattern in class_lower for pattern in ["handler", "controller", "adapter"]):
                groups["handlers"].append(class_name)
            elif any(pattern in class_lower for pattern in ["util", "helper", "tool"]):
                groups["utils"].append(class_name)
            else:
                groups["core"].append(class_name)
        
        # Remove empty groups
        return {k: v for k, v in groups.items() if v}
    
    def _group_functions_by_functionality(self, functions: List[str]) -> Dict[str, List[str]]:
        """Group functions by functionality patterns"""
        groups = {
            "validation": [],
            "processing": [],
            "utils": [],
            "core": []
        }
        
        for function_name in functions:
            func_lower = function_name.lower()
            if any(pattern in func_lower for pattern in ["validate", "check", "verify", "test"]):
                groups["validation"].append(function_name)
            elif any(pattern in func_lower for pattern in ["process", "transform", "convert", "parse"]):
                groups["processing"].append(function_name)
            elif any(pattern in func_lower for pattern in ["util", "helper", "tool", "format"]):
                groups["utils"].append(function_name)
            else:
                groups["core"].append(function_name)
        
        # Remove empty groups
        return {k: v for k, v in groups.items() if v}
    
    def _calculate_effort(self, file_analysis: FileAnalysis) -> int:
        """Calculate refactoring effort (1-5 scale)"""
        effort = 1
        
        if file_analysis.line_count > 2000:
            effort += 2
        elif file_analysis.line_count > 1000:
            effort += 1
        
        if file_analysis.class_count > 20:
            effort += 1
        if file_analysis.function_count > 100:
            effort += 1
        
        return min(effort, 5)
    
    def _calculate_risk(self, file_analysis: FileAnalysis) -> str:
        """Calculate refactoring risk level"""
        if file_analysis.line_count > 2000 or file_analysis.class_count > 20:
            return "high"
        elif file_analysis.line_count > 1000 or file_analysis.class_count > 10:
            return "medium"
        else:
            return "low"
    
    def export_analysis_report(self, output_file: str = "repository_analysis_report.json"):
        """Export analysis report to JSON file"""
        report = self._generate_analysis_report()
        
        with open(output_file, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        
        logger.info(f"📊 Analysis report exported to {output_file}")
    
    def export_refactoring_plans(self, output_file: str = "refactoring_plans.json"):
        """Export refactoring plans to JSON file"""
        plans_data = []
        for plan in self.refactoring_plans:
            plans_data.append({
                "source_file": plan.source_file,
                "target_modules": plan.target_modules,
                "class_assignments": plan.class_assignments,
                "function_assignments": plan.function_assignments,
                "dependencies": plan.dependencies,
                "estimated_effort": plan.estimated_effort,
                "risk_level": plan.risk_level
            })
        
        with open(output_file, 'w') as f:
            json.dump(plans_data, f, indent=2)
        
        logger.info(f"📋 Refactoring plans exported to {output_file}")

def main():
    """Main execution function"""
    print("🚀 Repository-Wide Refactoring Engine")
    print("=" * 50)
    
    # Initialize engine
    engine = RepositoryRefactoringEngine()
    
    # Analyze repository
    print("\n1. Analyzing repository...")
    report = engine.analyze_repository()
    
    # Print summary
    summary = report["summary"]
    print(f"\n📊 Analysis Summary:")
    print(f"   Total files: {summary['total_files']}")
    print(f"   Large files (>300 lines): {summary['large_files']}")
    print(f"   Compliance rate: {summary['compliance_rate']:.1f}%")
    print(f"   Total lines: {summary['total_lines']:,}")
    print(f"   Average file size: {summary['average_file_size']} lines")
    
    # Generate refactoring plans
    print("\n2. Generating refactoring plans...")
    plans = engine.generate_refactoring_plans()
    
    # Export reports
    print("\n3. Exporting reports...")
    engine.export_analysis_report()
    engine.export_refactoring_plans()
    
    # Show top priority files
    print("\n🎯 Top Priority Files for Refactoring:")
    priority_files = report["priority_files"]
    for i, file in enumerate(priority_files[:5], 1):
        print(f"   {i}. {file.file_path}")
        print(f"      Lines: {file.line_count}, Classes: {file.class_count}, Priority: {file.refactoring_priority}")
    
    print(f"\n✅ Analysis complete! Generated {len(plans)} refactoring plans.")
    print("📁 Check repository_analysis_report.json and refactoring_plans.json for details.")

if __name__ == "__main__":
    main()









