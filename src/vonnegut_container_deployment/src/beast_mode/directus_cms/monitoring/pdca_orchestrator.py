"""
Directus CMS PDCA Methodology Integration

Single Responsibility: Implement systematic PDCA cycles for all major operations.
Maintains <250 lines through focused PDCA implementation.

Requirements Addressed:
- 9.2, 9.4: PDCA methodology integration for systematic operations
- Continuous improvement tracking and reporting
"""

import time
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass, field
from enum import Enum

from src.rm_ddd.core.unified_reflective_module import (
    ReflectiveModule,
    ModuleCapability,
)
from .structured_logger import StructuredLogger


class PDCAPhase(Enum):
    """PDCA cycle phases"""
    PLAN = "plan"
    DO = "do"
    CHECK = "check"
    ACT = "act"


@dataclass
class PDCAResult:
    """Result of a PDCA phase execution"""
    phase: PDCAPhase
    success: bool
    duration_seconds: float
    data: Dict[str, Any] = field(default_factory=dict)
    error: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class PDCACycle:
    """Complete PDCA cycle tracking"""
    operation: str
    correlation_id: str
    start_time: datetime
    end_time: Optional[datetime] = None
    phases: Dict[PDCAPhase, PDCAResult] = field(default_factory=dict)
    overall_success: bool = False
    improvement_actions: List[str] = field(default_factory=list)


class PDCAOrchestrator(ReflectiveModule):
    """
    PDCA methodology orchestrator for systematic operations
    
    Implements Plan-Do-Check-Act cycles with tracking and improvement.
    Maintains <250 lines through focused PDCA implementation.
    """
    
    def __init__(self, logger: StructuredLogger = None):
        """Initialize PDCA orchestrator with logging"""
        super().__init__()
        
        self.module_id = "pdca_orchestrator"
        self.logger = logger or StructuredLogger("pdca_orchestrator")
        
        self._active_cycles = {}
        self._completed_cycles = []
        self._improvement_patterns = {}
    
    def get_module_info(self) -> Dict[str, Any]:
        """Get module information - ReflectiveModule implementation"""
        return {
            "module_id": self.module_id,
            "module_name": "PDCAOrchestrator",
            "version": "1.0.0",
            "pattern": "pdca_orchestrator",
            "methodology": "plan_do_check_act",
            "beast_mode_compliance": "full"
        }
    
    def get_capabilities(self) -> List[ModuleCapability]:
        """Get module capabilities - ReflectiveModule implementation"""
        return [
            ModuleCapability.CORE_FUNCTIONALITY,
            ModuleCapability.MONITORING,
            ModuleCapability.VALIDATION
        ]
    
    def execute_pdca_cycle(self, 
                          operation: str,
                          plan_func: Callable[[], Dict[str, Any]],
                          do_func: Callable[[Dict[str, Any]], Dict[str, Any]],
                          check_func: Callable[[Dict[str, Any]], Dict[str, Any]],
                          act_func: Callable[[Dict[str, Any]], Dict[str, Any]]) -> PDCACycle:
        """
        Execute complete PDCA cycle for an operation
        
        Args:
            operation: Name of the operation
            plan_func: Function to execute PLAN phase
            do_func: Function to execute DO phase
            check_func: Function to execute CHECK phase
            act_func: Function to execute ACT phase
            
        Returns:
            Complete PDCA cycle results
        """
        with self.trace_operation("execute_pdca_cycle", operation=operation) as trace:
            with self.logger.correlation_context_manager() as correlation_id:
                
                # Initialize cycle
                cycle = PDCACycle(
                    operation=operation,
                    correlation_id=correlation_id,
                    start_time=datetime.now()
                )
                
                self._active_cycles[correlation_id] = cycle
                
                self.logger.operation_start(operation, pdca_cycle="started")
                
                try:
                    # PLAN Phase
                    plan_result = self._execute_phase(
                        PDCAPhase.PLAN, plan_func, operation, correlation_id
                    )
                    cycle.phases[PDCAPhase.PLAN] = plan_result
                    
                    if not plan_result.success:
                        cycle.overall_success = False
                        self._complete_cycle(cycle)
                        return cycle
                    
                    # DO Phase
                    do_result = self._execute_phase(
                        PDCAPhase.DO, 
                        lambda: do_func(plan_result.data),
                        operation, 
                        correlation_id
                    )
                    cycle.phases[PDCAPhase.DO] = do_result
                    
                    # CHECK Phase
                    check_result = self._execute_phase(
                        PDCAPhase.CHECK,
                        lambda: check_func(do_result.data),
                        operation,
                        correlation_id
                    )
                    cycle.phases[PDCAPhase.CHECK] = check_result
                    
                    # ACT Phase
                    act_result = self._execute_phase(
                        PDCAPhase.ACT,
                        lambda: act_func(check_result.data),
                        operation,
                        correlation_id
                    )
                    cycle.phases[PDCAPhase.ACT] = act_result
                    
                    # Determine overall success
                    cycle.overall_success = all(
                        result.success for result in cycle.phases.values()
                    )
                    
                    # Extract improvement actions
                    if act_result.success and "improvements" in act_result.data:
                        cycle.improvement_actions = act_result.data["improvements"]
                    
                    self.logger.operation_end(operation, cycle.overall_success, 
                                            pdca_cycle="completed",
                                            phases_completed=len(cycle.phases))
                    
                    trace.output_result = {
                        "success": cycle.overall_success,
                        "phases_completed": len(cycle.phases)
                    }
                    
                except Exception as e:
                    self._increment_error_count()
                    cycle.overall_success = False
                    
                    self.logger.error(f"PDCA cycle failed for {operation}: {e}",
                                    operation=operation,
                                    pdca_cycle="failed",
                                    error=str(e))
                    
                    trace.error_info = {"error": str(e)}
                
                finally:
                    self._complete_cycle(cycle)
                
                return cycle
    
    def _execute_phase(self, 
                      phase: PDCAPhase, 
                      phase_func: Callable[[], Dict[str, Any]],
                      operation: str,
                      correlation_id: str) -> PDCAResult:
        """Execute a single PDCA phase"""
        start_time = time.time()
        
        self.logger.operation_checkpoint(operation, f"pdca_{phase.value}_start")
        
        try:
            result_data = phase_func()
            duration = time.time() - start_time
            
            result = PDCAResult(
                phase=phase,
                success=True,
                duration_seconds=duration,
                data=result_data or {}
            )
            
            self.logger.operation_checkpoint(operation, f"pdca_{phase.value}_success",
                                           duration_seconds=duration)
            
            return result
            
        except Exception as e:
            duration = time.time() - start_time
            
            result = PDCAResult(
                phase=phase,
                success=False,
                duration_seconds=duration,
                error=str(e)
            )
            
            self.logger.error(f"PDCA {phase.value} phase failed for {operation}: {e}",
                            operation=operation,
                            pdca_phase=phase.value,
                            duration_seconds=duration)
            
            return result
    
    def _complete_cycle(self, cycle: PDCACycle):
        """Complete and store PDCA cycle"""
        cycle.end_time = datetime.now()
        
        # Move from active to completed
        if cycle.correlation_id in self._active_cycles:
            del self._active_cycles[cycle.correlation_id]
        
        self._completed_cycles.append(cycle)
        
        # Keep only last 100 cycles
        if len(self._completed_cycles) > 100:
            self._completed_cycles.pop(0)
        
        # Update improvement patterns
        self._update_improvement_patterns(cycle)
    
    def _update_improvement_patterns(self, cycle: PDCACycle):
        """Update improvement patterns based on cycle results"""
        operation = cycle.operation
        
        if operation not in self._improvement_patterns:
            self._improvement_patterns[operation] = {
                "total_cycles": 0,
                "successful_cycles": 0,
                "common_failures": {},
                "improvement_actions": [],
                "avg_duration_seconds": 0
            }
        
        pattern = self._improvement_patterns[operation]
        pattern["total_cycles"] += 1
        
        if cycle.overall_success:
            pattern["successful_cycles"] += 1
        
        # Track common failures
        for phase, result in cycle.phases.items():
            if not result.success and result.error:
                error_key = f"{phase.value}_{result.error[:50]}"  # Truncate for grouping
                pattern["common_failures"][error_key] = pattern["common_failures"].get(error_key, 0) + 1
        
        # Collect improvement actions
        pattern["improvement_actions"].extend(cycle.improvement_actions)
        
        # Update average duration
        total_duration = sum(
            (cycle.end_time - cycle.start_time).total_seconds()
            for cycle in self._completed_cycles
            if cycle.operation == operation and cycle.end_time
        )
        operation_cycles = [c for c in self._completed_cycles if c.operation == operation and c.end_time]
        if operation_cycles:
            pattern["avg_duration_seconds"] = total_duration / len(operation_cycles)
    
    def get_operation_analysis(self, operation: str) -> Dict[str, Any]:
        """
        Get PDCA analysis for a specific operation
        
        Args:
            operation: Operation name to analyze
            
        Returns:
            Analysis of PDCA cycles for the operation
        """
        with self.trace_operation("get_operation_analysis", operation=operation) as trace:
            try:
                if operation not in self._improvement_patterns:
                    return {
                        "operation": operation,
                        "status": "no_data",
                        "message": "No PDCA cycles recorded for this operation"
                    }
                
                pattern = self._improvement_patterns[operation]
                
                # Calculate success rate
                success_rate = 0
                if pattern["total_cycles"] > 0:
                    success_rate = (pattern["successful_cycles"] / pattern["total_cycles"]) * 100
                
                # Get recent cycles
                recent_cycles = [
                    cycle for cycle in self._completed_cycles[-10:]
                    if cycle.operation == operation
                ]
                
                analysis = {
                    "operation": operation,
                    "total_cycles": pattern["total_cycles"],
                    "success_rate_percent": success_rate,
                    "avg_duration_seconds": pattern["avg_duration_seconds"],
                    "common_failures": pattern["common_failures"],
                    "improvement_actions_count": len(pattern["improvement_actions"]),
                    "recent_cycles_count": len(recent_cycles),
                    "recommendations": self._generate_recommendations(pattern)
                }
                
                trace.output_result = analysis
                return analysis
                
            except Exception as e:
                self._increment_error_count()
                error_analysis = {
                    "operation": operation,
                    "status": "error",
                    "error": str(e)
                }
                
                trace.error_info = {"error": str(e)}
                return error_analysis
    
    def _generate_recommendations(self, pattern: Dict[str, Any]) -> List[str]:
        """Generate improvement recommendations based on patterns"""
        recommendations = []
        
        # Success rate recommendations
        success_rate = 0
        if pattern["total_cycles"] > 0:
            success_rate = (pattern["successful_cycles"] / pattern["total_cycles"]) * 100
        
        if success_rate < 80:
            recommendations.append("Success rate below 80% - review common failure patterns")
        
        # Duration recommendations
        if pattern["avg_duration_seconds"] > 300:  # 5 minutes
            recommendations.append("Average duration exceeds 5 minutes - consider optimization")
        
        # Failure pattern recommendations
        if pattern["common_failures"]:
            most_common_failure = max(pattern["common_failures"].items(), key=lambda x: x[1])
            if most_common_failure[1] > 2:
                recommendations.append(f"Address recurring failure: {most_common_failure[0]}")
        
        # Improvement action recommendations
        if len(pattern["improvement_actions"]) > 10:
            recommendations.append("Many improvement actions identified - prioritize implementation")
        
        return recommendations
    
    def get_continuous_improvement_report(self) -> Dict[str, Any]:
        """
        Generate comprehensive continuous improvement report
        
        Returns:
            Report on PDCA effectiveness and improvement opportunities
        """
        with self.trace_operation("get_continuous_improvement_report") as trace:
            try:
                # Overall statistics
                total_cycles = len(self._completed_cycles)
                successful_cycles = sum(1 for cycle in self._completed_cycles if cycle.overall_success)
                
                overall_success_rate = 0
                if total_cycles > 0:
                    overall_success_rate = (successful_cycles / total_cycles) * 100
                
                # Operation breakdown
                operation_stats = {}
                for operation, pattern in self._improvement_patterns.items():
                    operation_stats[operation] = {
                        "cycles": pattern["total_cycles"],
                        "success_rate": (pattern["successful_cycles"] / pattern["total_cycles"]) * 100 if pattern["total_cycles"] > 0 else 0,
                        "avg_duration": pattern["avg_duration_seconds"]
                    }
                
                report = {
                    "report_timestamp": datetime.now().isoformat(),
                    "overall_statistics": {
                        "total_cycles": total_cycles,
                        "overall_success_rate_percent": overall_success_rate,
                        "operations_tracked": len(self._improvement_patterns)
                    },
                    "operation_breakdown": operation_stats,
                    "top_improvement_opportunities": self._identify_top_improvements(),
                    "pdca_effectiveness": self._assess_pdca_effectiveness()
                }
                
                trace.output_result = {"operations_analyzed": len(operation_stats)}
                return report
                
            except Exception as e:
                self._increment_error_count()
                error_report = {
                    "report_timestamp": datetime.now().isoformat(),
                    "status": "error",
                    "error": str(e)
                }
                
                trace.error_info = {"error": str(e)}
                return error_report
    
    def _identify_top_improvements(self) -> List[Dict[str, Any]]:
        """Identify top improvement opportunities across all operations"""
        improvements = []
        
        for operation, pattern in self._improvement_patterns.items():
            success_rate = (pattern["successful_cycles"] / pattern["total_cycles"]) * 100 if pattern["total_cycles"] > 0 else 0
            
            if success_rate < 90:  # Operations with room for improvement
                improvements.append({
                    "operation": operation,
                    "success_rate_percent": success_rate,
                    "total_cycles": pattern["total_cycles"],
                    "priority": "high" if success_rate < 70 else "medium"
                })
        
        # Sort by success rate (lowest first)
        improvements.sort(key=lambda x: x["success_rate_percent"])
        
        return improvements[:5]  # Top 5 improvement opportunities
    
    def _assess_pdca_effectiveness(self) -> Dict[str, Any]:
        """Assess overall effectiveness of PDCA methodology"""
        if not self._completed_cycles:
            return {"status": "insufficient_data"}
        
        # Calculate trends over time
        recent_cycles = self._completed_cycles[-20:]  # Last 20 cycles
        older_cycles = self._completed_cycles[-40:-20] if len(self._completed_cycles) >= 40 else []
        
        recent_success_rate = sum(1 for c in recent_cycles if c.overall_success) / len(recent_cycles) * 100
        older_success_rate = sum(1 for c in older_cycles if c.overall_success) / len(older_cycles) * 100 if older_cycles else recent_success_rate
        
        trend = "improving" if recent_success_rate > older_success_rate else "declining" if recent_success_rate < older_success_rate else "stable"
        
        return {
            "trend": trend,
            "recent_success_rate_percent": recent_success_rate,
            "improvement_delta_percent": recent_success_rate - older_success_rate,
            "effectiveness": "high" if recent_success_rate > 85 else "medium" if recent_success_rate > 70 else "low"
        }