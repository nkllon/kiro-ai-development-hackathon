"""
MakefileHealthManager - DAG-driven Makefile health monitoring
"""

import os
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from pathlib import Path

from .dag_analyzer import DAGAnalyzer, DAGAnalysisResult
from .health_scorer import HealthScorer, HealthReport
from .auto_fixer import AutoFixer, FixResult

# RM-DDD Integration - Using Unified Interface
import sys
sys.path.append(str(Path(__file__).parent.parent.parent))
from src.rm_ddd.core.unified_reflective_module import (
    ReflectiveModule,
    ModuleHealth,
    ModuleStatus,
    ModuleCapability,
    GracefulDegradationResult
)


@dataclass
class MakefileHealthResult:
    """Complete health analysis result for a Makefile"""
    makefile_path: str
    exists: bool
    dag_analysis: Optional[DAGAnalysisResult]
    health_report: Optional[HealthReport]
    fix_result: Optional[FixResult]
    overall_health_score: float
    status: str  # 'healthy', 'needs_attention', 'critical', 'error'


class MakefileHealthManager(ReflectiveModule):
    """
    DAG-driven Makefile health monitoring and repair system
    
    TRACE: REQ-RC1-RMDDD-001, REQ-RC1-RDI-001
    TEST: tests/rc1/test_makefile_health_manager.py
    IMPLEMENTATION: DAG-driven Makefile analysis and repair system
    """
    
    def __init__(self):
        super().__init__()  # CRITICAL: Call parent __init__ for Prometheus, logging, etc.
        self.module_id = "makefile_health_manager"
        self.version = "1.0.0"
        self.capabilities = [ModuleCapability.CORE_FUNCTIONALITY, ModuleCapability.MONITORING]
        # Dependencies not required in unified model
        self.dag_analyzer = DAGAnalyzer()
        self.health_scorer = HealthScorer()
        self.auto_fixer = AutoFixer()
        
    def get_module_info(self) -> Dict[str, Any]:
        """
        Get comprehensive module information for RM-DDD registry.
        
        TRACE: REQ-RC1-RMDDD-002, REQ-RC1-RDI-002
        TEST: Unit test validates method implementation and return format
        IMPLEMENTATION: Module metadata interface specification
        """
        return {
            'module_id': self.module_id,
            'version': self.version,
            'class_name': self.__class__.__name__,
            'file_path': self.__class__.__module__,
            'capabilities': [cap.value for cap in self.capabilities],
            'health_status': self.get_health_status().status.value,
            'last_updated': datetime.now().isoformat()
        }
    
    def get_capabilities(self) -> List[ModuleCapability]:
        """Get module capabilities for RM-DDD registry."""
        return self.capabilities
    
    def get_health_status(self) -> ModuleHealth:
        """Perform comprehensive health check for RM-DDD compliance."""
        try:
            # Test basic functionality
            test_result = self.diagnose_makefile("test", auto_fix=False)
            health_score = 100.0 if test_result.status != 'error' else 50.0
            
            return ModuleHealth(
                module_id=self.module_id,
                status=ModuleStatus.HEALTHY if health_score > 80 else ModuleStatus.DEGRADED,
                health_score=health_score,
                issues=[] if health_score > 80 else ["Module functionality test failed"],
                last_check=datetime.now()
            )
        except Exception as e:
            return ModuleHealth(
                module_id=self.module_id,
                status=ModuleStatus.ERROR,
                health_score=0.0,
                issues=[f"Health check failed: {str(e)}"],
                last_check=datetime.now()
            )
    
    def graceful_degradation(self) -> GracefulDegradationResult:
        """Perform graceful degradation for RM-DDD compliance."""
        return GracefulDegradationResult(
            success=True,
            degraded_capabilities=[],
            remaining_capabilities=self.capabilities,
            error_message=None
        )
    
    def register_module(self, registry):
        """Register module with registry."""
        metadata = self.get_interface_metadata()
        if hasattr(registry, "register"):
            registry.register(metadata)
    
    def get_interface_metadata(self):
        """Get interface metadata for registry."""
        return {
            "module_id": getattr(self, "module_id", self.__class__.__name__),
            "interface_type": self.__class__.__name__,
            "version": "1.0.0",
            "dependencies": [],
            "capabilities": [cap.value for cap in self.capabilities],
        }
    
    def health_check(self):
        """Perform health check."""
        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "module_id": getattr(self, "module_id", self.__class__.__name__),
        }
    
    def _should_enable_prometheus(self) -> bool:
        """Check if Prometheus metrics should be enabled."""
        return os.getenv("BEAST_MODE_PROMETHEUS_ENABLED", "true").lower() == "true"
    
    def _initialize_prometheus_metrics(self):
        """Initialize Prometheus metrics for this module."""
        try:
            from beast_mode.monitoring.prometheus_exporter import PrometheusExporter
            
            self._prometheus_exporter = PrometheusExporter(
                port=int(os.getenv("BEAST_MODE_PROMETHEUS_PORT", "8000")),
                enable_http_server=True,
            )
            self._logger.info(
                f"Prometheus metrics enabled for {self.__class__.__name__}"
            )
        except ImportError:
            self._logger.warning(
                "Prometheus client not available. Install with: pip install prometheus-client"
            )
            self._enable_prometheus = False
        except Exception as e:
            self._logger.error(f"Failed to initialize Prometheus metrics: {e}")
            self._enable_prometheus = False
    
    def _collect_prometheus_metrics(self):
        """Collect metrics for Prometheus export."""
        if not self._enable_prometheus or not self._prometheus_exporter:
            return
        
        try:
            # Get module info
            module_info = self.get_module_info()
            module_id = module_info.get("module_id", self.__class__.__name__)
            
            # Get health status
            health_status = self.get_health_status()
            
            # Record module health metrics
            self._prometheus_exporter.record_module_health(
                module_id=module_id,
                status=health_status.status.value,
                health_score=health_status.health_score,
                error_count=health_status.error_count,
                warning_count=health_status.warning_count,
                uptime_seconds=health_status.uptime_seconds,
            )
            
            # Record module performance metrics
            self._prometheus_exporter.record_module_performance(
                module_id=module_id,
                class_name=self.__class__.__name__,
                version=module_info.get("version", "1.0.0"),
                capabilities=[cap.value for cap in self.get_capabilities()],
                last_activity=self._last_activity,
            )
            
        except Exception as e:
            self._logger.error(f"Failed to collect Prometheus metrics: {e}")
    
    def _update_activity(self):
        """Update last activity timestamp and collect metrics."""
        self._last_activity = datetime.now()
        if self._enable_prometheus:
            self._collect_prometheus_metrics()
    
    def _increment_error_count(self):
        """Increment error count and collect metrics."""
        self._error_count += 1
        self._update_activity()
    
    def _increment_warning_count(self):
        """Increment warning count and collect metrics."""
        self._warning_count += 1
        self._update_activity()
    
    def get_prometheus_metrics(self) -> Dict[str, Any]:
        """Get Prometheus metrics for this module."""
        if not self._enable_prometheus or not self._prometheus_exporter:
            return {}
        
        try:
            return self._prometheus_exporter.get_module_metrics(
                module_id=getattr(self, "module_id", self.__class__.__name__)
            )
        except Exception as e:
            self._logger.error(f"Failed to get Prometheus metrics: {e}")
            return {}
    
    def enable_prometheus_metrics(self, enable: bool = True):
        """Enable or disable Prometheus metrics for this module."""
        self._enable_prometheus = enable
        if enable and not self._prometheus_exporter:
            self._initialize_prometheus_metrics()
        elif not enable:
            self._prometheus_exporter = None
        
    def diagnose_makefile(self, makefile_path: str, auto_fix: bool = False) -> MakefileHealthResult:
        """
        Diagnose Makefile health with comprehensive analysis
        
        Args:
            makefile_path: Path to the Makefile to analyze
            auto_fix: Whether to automatically apply fixes
            
        Returns:
            MakefileHealthResult with complete analysis
        """
        result = MakefileHealthResult(
            makefile_path=makefile_path,
            exists=os.path.exists(makefile_path),
            dag_analysis=None,
            health_report=None,
            fix_result=None,
            overall_health_score=0.0,
            status='error'
        )
        
        if not result.exists:
            result.status = 'error'
            return result
        
        try:
            # Perform DAG analysis
            result.dag_analysis = self.dag_analyzer.analyze_makefile(makefile_path)
            
            # Generate health report
            result.health_report = self.health_scorer.score_makefile_health(result.dag_analysis)
            result.overall_health_score = result.health_report.metrics.overall_health
            
            # Apply fixes if requested
            if auto_fix and result.health_report and result.health_report.issues:
                result.fix_result = self.auto_fixer.fix_makefile_issues(
                    makefile_path, result.dag_analysis, result.health_report
                )
                
                # Re-analyze after fixes
                if result.fix_result and result.fix_result.success:
                    result.dag_analysis = self.dag_analyzer.analyze_makefile(makefile_path)
                    result.health_report = self.health_scorer.score_makefile_health(result.dag_analysis)
                    result.overall_health_score = result.health_report.metrics.overall_health
            
            # Determine overall status
            if result.health_report:
                result.status = self._determine_status(result.overall_health_score, result.health_report)
            
        except Exception as e:
            result.status = 'error'
            print(f"Error analyzing Makefile {makefile_path}: {e}")
        
        return result
    
    def diagnose_multiple_makefiles(self, makefile_paths: List[str], 
                                  auto_fix: bool = False) -> List[MakefileHealthResult]:
        """
        Diagnose multiple Makefiles
        
        Args:
            makefile_paths: List of Makefile paths
            auto_fix: Whether to automatically apply fixes
            
        Returns:
            List of MakefileHealthResult objects
        """
        results = []
        
        for path in makefile_paths:
            result = self.diagnose_makefile(path, auto_fix)
            results.append(result)
            
        return results
    
    def discover_makefiles(self, directory: str) -> List[str]:
        """
        Discover all Makefiles in a directory tree
        
        Args:
            directory: Root directory to search
            
        Returns:
            List of discovered Makefile paths
        """
        makefiles: List[str] = []
        directory_path = Path(directory)
        
        if not directory_path.exists():
            return makefiles
        
        # Look for common Makefile names
        makefile_names = ['Makefile', 'makefile', 'GNUmakefile']
        
        for root, dirs, files in os.walk(directory):
            for file in files:
                if file in makefile_names:
                    makefiles.append(os.path.join(root, file))
        
        return makefiles
    
    def generate_health_summary(self, results: List[MakefileHealthResult]) -> Dict[str, Any]:
        """
        Generate summary of health analysis results
        
        Args:
            results: List of health analysis results
            
        Returns:
            Summary dictionary with statistics and insights
        """
        if not results:
            return {"error": "No results to summarize"}
        
        total_makefiles = len(results)
        healthy_count = sum(1 for r in results if r.status == 'healthy')
        needs_attention_count = sum(1 for r in results if r.status == 'needs_attention')
        critical_count = sum(1 for r in results if r.status == 'critical')
        error_count = sum(1 for r in results if r.status == 'error')
        
        avg_health_score = sum(r.overall_health_score for r in results if r.overall_health_score > 0) / max(1, total_makefiles - error_count)
        
        # Collect common issues
        all_issues = []
        for result in results:
            if result.health_report and result.health_report.issues:
                all_issues.extend(result.health_report.issues)
        
        issue_counts: Dict[str, int] = {}
        for issue in all_issues:
            issue_counts[issue] = issue_counts.get(issue, 0) + 1
        
        # Sort issues by frequency
        common_issues = sorted(issue_counts.items(), key=lambda x: x[1], reverse=True)
        
        return {
            "total_makefiles": total_makefiles,
            "healthy": healthy_count,
            "needs_attention": needs_attention_count,
            "critical": critical_count,
            "errors": error_count,
            "average_health_score": round(avg_health_score, 3),
            "common_issues": common_issues[:10],  # Top 10 most common issues
            "success_rate": round((healthy_count / total_makefiles) * 100, 1) if total_makefiles > 0 else 0
        }
    
    def _determine_status(self, health_score: float, health_report: HealthReport) -> str:
        """Determine overall status based on health score and issues"""
        if health_score >= 0.9:
            return 'healthy'
        elif health_score >= 0.7:
            return 'needs_attention'
        elif health_score >= 0.4:
            return 'critical'
        else:
            return 'critical'  # Very low health score
    
    def export_health_report(self, results: List[MakefileHealthResult], 
                           output_path: str) -> bool:
        """
        Export health report to file
        
        Args:
            results: Health analysis results
            output_path: Path to save the report
            
        Returns:
            True if successful, False otherwise
        """
        try:
            import json
            
            # Convert results to serializable format
            report_data = []
            for result in results:
                data = {
                    "makefile_path": result.makefile_path,
                    "exists": result.exists,
                    "overall_health_score": result.overall_health_score,
                    "status": result.status
                }
                
                if result.dag_analysis:
                    data["dag_analysis"] = {
                        "total_nodes": len(result.dag_analysis.nodes),
                        "cycles_count": len(result.dag_analysis.cycles),
                        "orphaned_nodes": result.dag_analysis.orphaned_nodes,
                        "health_score": result.dag_analysis.health_score
                    }
                
                if result.health_report:
                    data["health_metrics"] = {
                        "structural_health": result.health_report.metrics.structural_health,
                        "dependency_health": result.health_report.metrics.dependency_health,
                        "performance_health": result.health_report.metrics.performance_health,
                        "maintainability_health": result.health_report.metrics.maintainability_health,
                        "overall_health": result.health_report.metrics.overall_health,
                        "confidence_level": result.health_report.confidence_level
                    }
                    data["issues"] = result.health_report.issues
                    data["recommendations"] = result.health_report.recommendations
                
                if result.fix_result:
                    data["fix_result"] = {
                        "success": result.fix_result.success,
                        "fixes_applied": result.fix_result.fixes_applied,
                        "warnings": result.fix_result.warnings,
                        "errors": result.fix_result.errors,
                        "backup_created": result.fix_result.backup_created
                    }
                
                report_data.append(data)
            
            # Add summary
            summary = self.generate_health_summary(results)
            
            full_report = {
                "summary": summary,
                "detailed_results": report_data,
                "generated_at": str(Path().cwd()),
                "version": "1.0"
            }
            
            with open(output_path, 'w') as f:
                json.dump(full_report, f, indent=2)
            
            return True
            
        except Exception as e:
            print(f"Error exporting health report: {e}")
            return False
