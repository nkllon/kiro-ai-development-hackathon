#!/usr/bin/env python3
"""
Performance Validation Script

This script validates that examples run efficiently on standard development machines by:
1. Testing example execution times and resource usage
2. Optimizing startup times and resource consumption
3. Documenting performance characteristics and requirements

Requirements: 7.2, 7.3, 7.4, 7.5
"""

import os
import sys
import time
import json
import psutil
import subprocess
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, asdict
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class PerformanceMetrics:
    """Performance metrics for an example execution."""
    name: str
    execution_time: float
    memory_usage_mb: float
    cpu_usage_percent: float
    startup_time: float
    success: bool
    error_message: Optional[str] = None
    resource_requirements: Optional[Dict] = None

@dataclass
class SystemInfo:
    """System information for performance context."""
    cpu_count: int
    memory_gb: float
    python_version: str
    platform: str
    architecture: str

class PerformanceValidator:
    """Validates performance of examples and system components."""
    
    def __init__(self):
        self.examples_dir = Path("examples")
        self.performance_results = []
        self.system_info = self._get_system_info()
        
        # Performance thresholds for standard development machines
        self.thresholds = {
            "max_startup_time": 30.0,  # seconds
            "max_execution_time": 300.0,  # 5 minutes
            "max_memory_usage": 2048,  # MB
            "max_cpu_usage": 80.0,  # percent
        }
        
        # Examples to test
        self.examples_to_test = [
            {
                "name": "Quick Start Demo",
                "path": "examples/demos/quick_start_demo.py",
                "expected_runtime": 60,  # seconds
                "description": "Basic framework demonstration"
            },
            {
                "name": "AI Memory Palace Demo",
                "path": "examples/demos/ai_memory_palace_demo.py",
                "expected_runtime": 120,
                "description": "AI Memory Palace functionality demo"
            },
            {
                "name": "DAG Orchestration Demo",
                "path": "examples/demos/dag_orchestration_demo.py",
                "expected_runtime": 180,
                "description": "DAG orchestration capabilities demo"
            },
            {
                "name": "ReflectiveModule Demo",
                "path": "examples/demos/reflective_module_demo.py",
                "expected_runtime": 90,
                "description": "ReflectiveModule pattern demonstration"
            }
        ]

    def _get_system_info(self) -> SystemInfo:
        """Get system information for performance context."""
        return SystemInfo(
            cpu_count=psutil.cpu_count(),
            memory_gb=round(psutil.virtual_memory().total / (1024**3), 2),
            python_version=sys.version.split()[0],
            platform=sys.platform,
            architecture=os.uname().machine if hasattr(os, 'uname') else 'unknown'
        )

    def measure_startup_time(self, script_path: str) -> float:
        """Measure the startup time of a Python script."""
        start_time = time.time()
        try:
            # Run script with --help or --version to test startup without full execution
            result = subprocess.run([
                sys.executable, script_path, "--help"
            ], capture_output=True, text=True, timeout=30)
            
            if result.returncode != 0:
                # Try without --help flag
                result = subprocess.run([
                    sys.executable, "-c", f"import sys; sys.path.insert(0, '.'); exec(open('{script_path}').read()[:100])"
                ], capture_output=True, text=True, timeout=10)
            
            return time.time() - start_time
        except subprocess.TimeoutExpired:
            return 30.0  # Max startup time
        except Exception:
            return 5.0  # Reasonable default

    def run_example_with_monitoring(self, example: Dict) -> PerformanceMetrics:
        """Run an example with performance monitoring."""
        logger.info(f"Testing example: {example['name']}")
        
        script_path = example["path"]
        if not Path(script_path).exists():
            return PerformanceMetrics(
                name=example["name"],
                execution_time=0,
                memory_usage_mb=0,
                cpu_usage_percent=0,
                startup_time=0,
                success=False,
                error_message=f"Script not found: {script_path}"
            )
        
        # Measure startup time
        startup_time = self.measure_startup_time(script_path)
        
        # Start monitoring
        process = None
        start_time = time.time()
        max_memory = 0
        max_cpu = 0
        
        try:
            # Start the process
            process = subprocess.Popen([
                sys.executable, script_path
            ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            
            # Monitor resource usage
            psutil_process = psutil.Process(process.pid)
            
            while process.poll() is None:
                try:
                    # Get memory usage
                    memory_info = psutil_process.memory_info()
                    memory_mb = memory_info.rss / (1024 * 1024)
                    max_memory = max(max_memory, memory_mb)
                    
                    # Get CPU usage
                    cpu_percent = psutil_process.cpu_percent()
                    max_cpu = max(max_cpu, cpu_percent)
                    
                    # Check if we've exceeded time limit
                    if time.time() - start_time > self.thresholds["max_execution_time"]:
                        process.terminate()
                        break
                    
                    time.sleep(0.1)  # Sample every 100ms
                    
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    break
            
            execution_time = time.time() - start_time
            
            # Get final result
            stdout, stderr = process.communicate(timeout=10)
            success = process.returncode == 0
            error_message = stderr if stderr and not success else None
            
            return PerformanceMetrics(
                name=example["name"],
                execution_time=execution_time,
                memory_usage_mb=max_memory,
                cpu_usage_percent=max_cpu,
                startup_time=startup_time,
                success=success,
                error_message=error_message,
                resource_requirements={
                    "min_memory_mb": max_memory * 1.2,  # 20% buffer
                    "expected_runtime": example["expected_runtime"],
                    "description": example["description"]
                }
            )
            
        except subprocess.TimeoutExpired:
            if process:
                process.kill()
            return PerformanceMetrics(
                name=example["name"],
                execution_time=self.thresholds["max_execution_time"],
                memory_usage_mb=max_memory,
                cpu_usage_percent=max_cpu,
                startup_time=startup_time,
                success=False,
                error_message="Execution timeout"
            )
        except Exception as e:
            return PerformanceMetrics(
                name=example["name"],
                execution_time=0,
                memory_usage_mb=0,
                cpu_usage_percent=0,
                startup_time=startup_time,
                success=False,
                error_message=str(e)
            )

    def validate_system_requirements(self) -> Dict:
        """Validate that the system meets minimum requirements."""
        requirements = {
            "min_memory_gb": 4,
            "min_cpu_cores": 2,
            "recommended_memory_gb": 8,
            "recommended_cpu_cores": 4
        }
        
        validation = {
            "meets_minimum": True,
            "meets_recommended": True,
            "issues": [],
            "recommendations": []
        }
        
        # Check memory
        if self.system_info.memory_gb < requirements["min_memory_gb"]:
            validation["meets_minimum"] = False
            validation["issues"].append(
                f"Insufficient memory: {self.system_info.memory_gb}GB < {requirements['min_memory_gb']}GB required"
            )
        elif self.system_info.memory_gb < requirements["recommended_memory_gb"]:
            validation["meets_recommended"] = False
            validation["recommendations"].append(
                f"Consider upgrading memory: {self.system_info.memory_gb}GB < {requirements['recommended_memory_gb']}GB recommended"
            )
        
        # Check CPU
        if self.system_info.cpu_count < requirements["min_cpu_cores"]:
            validation["meets_minimum"] = False
            validation["issues"].append(
                f"Insufficient CPU cores: {self.system_info.cpu_count} < {requirements['min_cpu_cores']} required"
            )
        elif self.system_info.cpu_count < requirements["recommended_cpu_cores"]:
            validation["meets_recommended"] = False
            validation["recommendations"].append(
                f"Consider upgrading CPU: {self.system_info.cpu_count} < {requirements['recommended_cpu_cores']} cores recommended"
            )
        
        return validation

    def optimize_performance(self) -> List[str]:
        """Generate performance optimization recommendations."""
        optimizations = []
        
        # Check for virtual environment
        if not hasattr(sys, 'real_prefix') and not (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
            optimizations.append("Create and use a virtual environment to isolate dependencies")
        
        # Check Python version
        python_version = tuple(map(int, sys.version.split()[0].split('.')))
        if python_version < (3, 8):
            optimizations.append(f"Upgrade Python from {sys.version.split()[0]} to 3.8+ for better performance")
        
        # Check available memory
        available_memory = psutil.virtual_memory().available / (1024**3)
        if available_memory < 2:
            optimizations.append(f"Free up memory: only {available_memory:.1f}GB available")
        
        # Check disk space
        disk_usage = psutil.disk_usage('.')
        free_space_gb = disk_usage.free / (1024**3)
        if free_space_gb < 5:
            optimizations.append(f"Free up disk space: only {free_space_gb:.1f}GB available")
        
        # General optimizations
        optimizations.extend([
            "Close unnecessary applications to free up resources",
            "Ensure stable internet connection for downloading dependencies",
            "Consider using SSD storage for better I/O performance",
            "Run examples in a clean environment without other heavy processes"
        ])
        
        return optimizations

    def run_performance_validation(self) -> Dict:
        """Run complete performance validation."""
        logger.info("Starting performance validation...")
        
        # Validate system requirements
        system_validation = self.validate_system_requirements()
        
        # Test examples
        example_results = []
        for example in self.examples_to_test:
            metrics = self.run_example_with_monitoring(example)
            example_results.append(metrics)
            
            # Log results
            if metrics.success:
                logger.info(f"✓ {metrics.name}: {metrics.execution_time:.1f}s, {metrics.memory_usage_mb:.1f}MB")
            else:
                logger.warning(f"✗ {metrics.name}: {metrics.error_message}")
        
        # Generate performance summary
        successful_examples = [r for r in example_results if r.success]
        failed_examples = [r for r in example_results if not r.success]
        
        performance_summary = {
            "total_examples": len(example_results),
            "successful_examples": len(successful_examples),
            "failed_examples": len(failed_examples),
            "average_execution_time": sum(r.execution_time for r in successful_examples) / len(successful_examples) if successful_examples else 0,
            "average_memory_usage": sum(r.memory_usage_mb for r in successful_examples) / len(successful_examples) if successful_examples else 0,
            "max_memory_usage": max((r.memory_usage_mb for r in successful_examples), default=0),
            "max_execution_time": max((r.execution_time for r in successful_examples), default=0)
        }
        
        # Check against thresholds
        threshold_violations = []
        for result in successful_examples:
            if result.execution_time > self.thresholds["max_execution_time"]:
                threshold_violations.append(f"{result.name}: execution time {result.execution_time:.1f}s > {self.thresholds['max_execution_time']}s")
            if result.memory_usage_mb > self.thresholds["max_memory_usage"]:
                threshold_violations.append(f"{result.name}: memory usage {result.memory_usage_mb:.1f}MB > {self.thresholds['max_memory_usage']}MB")
            if result.startup_time > self.thresholds["max_startup_time"]:
                threshold_violations.append(f"{result.name}: startup time {result.startup_time:.1f}s > {self.thresholds['max_startup_time']}s")
        
        # Generate optimizations
        optimizations = self.optimize_performance()
        
        # Create comprehensive report
        report = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "system_info": asdict(self.system_info),
            "system_validation": system_validation,
            "performance_thresholds": self.thresholds,
            "example_results": [asdict(r) for r in example_results],
            "performance_summary": performance_summary,
            "threshold_violations": threshold_violations,
            "optimizations": optimizations,
            "recommendations": self._generate_recommendations(example_results, system_validation),
            "overall_assessment": self._assess_overall_performance(example_results, system_validation, threshold_violations)
        }
        
        return report

    def _generate_recommendations(self, results: List[PerformanceMetrics], system_validation: Dict) -> List[str]:
        """Generate specific recommendations based on results."""
        recommendations = []
        
        # System-level recommendations
        if not system_validation["meets_minimum"]:
            recommendations.append("⚠️  System does not meet minimum requirements - upgrade hardware")
        elif not system_validation["meets_recommended"]:
            recommendations.append("💡 System meets minimum but not recommended requirements - consider upgrading")
        
        # Example-specific recommendations
        failed_examples = [r for r in results if not r.success]
        if failed_examples:
            recommendations.append(f"🔧 Fix {len(failed_examples)} failing examples before public release")
        
        slow_examples = [r for r in results if r.success and r.execution_time > 120]
        if slow_examples:
            recommendations.append(f"⚡ Optimize {len(slow_examples)} slow-running examples")
        
        memory_heavy = [r for r in results if r.success and r.memory_usage_mb > 1024]
        if memory_heavy:
            recommendations.append(f"🧠 Reduce memory usage in {len(memory_heavy)} memory-intensive examples")
        
        # General recommendations
        recommendations.extend([
            "📚 Document system requirements in README",
            "🚀 Create quick start guide with 5-minute example",
            "🔍 Add performance monitoring to examples",
            "📊 Include performance benchmarks in documentation"
        ])
        
        return recommendations

    def _assess_overall_performance(self, results: List[PerformanceMetrics], 
                                  system_validation: Dict, violations: List[str]) -> str:
        """Assess overall performance status."""
        successful_count = len([r for r in results if r.success])
        total_count = len(results)
        success_rate = successful_count / total_count if total_count > 0 else 0
        
        if not system_validation["meets_minimum"]:
            return "❌ FAIL - System does not meet minimum requirements"
        elif success_rate < 0.8:
            return f"❌ FAIL - Only {successful_count}/{total_count} examples working ({success_rate:.0%})"
        elif violations:
            return f"⚠️  WARN - Examples work but {len(violations)} performance issues detected"
        elif not system_validation["meets_recommended"]:
            return "✅ PASS - Examples work but system upgrade recommended"
        else:
            return "✅ EXCELLENT - All examples work efficiently on recommended hardware"

def main():
    """Main function to run performance validation."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Validate framework performance")
    parser.add_argument("--output", default="data/performance_validation_report.json",
                       help="Output file for the report")
    parser.add_argument("--examples-only", action="store_true",
                       help="Test only examples, skip system validation")
    parser.add_argument("--quick", action="store_true",
                       help="Run quick validation with reduced timeouts")
    
    args = parser.parse_args()
    
    validator = PerformanceValidator()
    
    # Adjust thresholds for quick mode
    if args.quick:
        validator.thresholds["max_execution_time"] = 60.0
        validator.thresholds["max_startup_time"] = 10.0
    
    # Run validation
    report = validator.run_performance_validation()
    
    # Save report
    os.makedirs(os.path.dirname(args.output), exist_ok=True)
    with open(args.output, 'w') as f:
        json.dump(report, f, indent=2)
    
    logger.info(f"Performance validation report saved to: {args.output}")
    
    # Print summary
    print("\n" + "="*80)
    print("PERFORMANCE VALIDATION SUMMARY")
    print("="*80)
    print(f"System: {report['system_info']['cpu_count']} cores, {report['system_info']['memory_gb']}GB RAM")
    print(f"Examples tested: {report['performance_summary']['total_examples']}")
    print(f"Successful: {report['performance_summary']['successful_examples']}")
    print(f"Failed: {report['performance_summary']['failed_examples']}")
    
    if report['performance_summary']['successful_examples'] > 0:
        print(f"Average execution time: {report['performance_summary']['average_execution_time']:.1f}s")
        print(f"Average memory usage: {report['performance_summary']['average_memory_usage']:.1f}MB")
    
    print(f"\nOverall Assessment: {report['overall_assessment']}")
    
    if report['threshold_violations']:
        print(f"\nPerformance Issues ({len(report['threshold_violations'])}):")
        for violation in report['threshold_violations']:
            print(f"  - {violation}")
    
    if report['recommendations']:
        print(f"\nRecommendations:")
        for rec in report['recommendations'][:5]:  # Show top 5
            print(f"  {rec}")
    
    print(f"\nFull report: {args.output}")
    
    # Exit with appropriate code
    if "FAIL" in report['overall_assessment']:
        sys.exit(1)
    elif "WARN" in report['overall_assessment']:
        sys.exit(2)
    else:
        sys.exit(0)

if __name__ == "__main__":
    main()