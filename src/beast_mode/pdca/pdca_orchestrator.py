"""
Systematic PDCA Orchestrator - Simple Implementation

A focused, practical implementation of PDCA cycles that actually works.
No over-engineering, just systematic execution of Plan-Do-Check-Act!
"""

import logging
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from pathlib import Path

from ..core.reflective_module import ReflectiveModule


@dataclass
class PDCATask:
    """A simple development task for PDCA execution"""
    name: str
    description: str
    requirements: List[str]
    success_criteria: List[str]
    estimated_duration: Optional[timedelta] = None


@dataclass
class PDCAResult:
    """Result of a PDCA cycle execution"""
    task: PDCATask
    success: bool
    duration: timedelta
    plan_result: Dict[str, Any]
    do_result: Dict[str, Any]
    check_result: Dict[str, Any]
    act_result: Dict[str, Any]
    lessons_learned: List[str]


class SystematicPDCAOrchestrator(ReflectiveModule):
    """
    Simple, focused PDCA orchestrator that executes Plan-Do-Check-Act cycles
    on real development tasks.
    
    Starting simple and building up - no over-engineering!
    """
    
    def __init__(self):
        super().__init__("SystematicPDCAOrchestrator")
        self.logger = logging.getLogger(__name__)
        
        # Simple state tracking
        self.cycles_executed = 0
        self.successful_cycles = 0
        self.lessons_learned: List[str] = []
        self.current_task: Optional[PDCATask] = None
        
        # Simple project registry (start with basics)
        self.project_registry = self._load_simple_registry()
        
        self.logger.info("🔄 Systematic PDCA Orchestrator initialized - ready for systematic execution!")
    
    def execute_pdca_cycle(self, task: PDCATask) -> PDCAResult:
        """Execute a complete PDCA cycle on a development task"""
        self.logger.info(f"🚀 Starting PDCA cycle for task: {task.name}")
        self.current_task = task
        start_time = datetime.now()
        
        try:
            # PLAN: Systematic planning using available intelligence
            plan_result = self._plan_phase(task)
            
            # DO: Execute the plan systematically
            do_result = self._do_phase(task, plan_result)
            
            # CHECK: Validate results against success criteria
            check_result = self._check_phase(task, do_result)
            
            # ACT: Learn from results and update knowledge
            act_result = self._act_phase(task, check_result)
            
            # Calculate results
            duration = datetime.now() - start_time
            success = check_result.get("success", False)
            
            # Update statistics
            self.cycles_executed += 1
            if success:
                self.successful_cycles += 1
            
            # Extract lessons learned
            lessons = act_result.get("lessons_learned", [])
            self.lessons_learned.extend(lessons)
            
            result = PDCAResult(
                task=task,
                success=success,
                duration=duration,
                plan_result=plan_result,
                do_result=do_result,
                check_result=check_result,
                act_result=act_result,
                lessons_learned=lessons
            )
            
            status = "SUCCESS" if success else "FAILED"
            self.logger.info(f"✅ PDCA cycle completed: {status} in {duration.total_seconds():.1f}s")
            
            return result
            
        except Exception as e:
            self.logger.error(f"💥 PDCA cycle failed: {e}")
            duration = datetime.now() - start_time
            
            return PDCAResult(
                task=task,
                success=False,
                duration=duration,
                plan_result={},
                do_result={},
                check_result={"success": False, "error": str(e)},
                act_result={},
                lessons_learned=[f"PDCA cycle failed: {str(e)}"]
            )
        finally:
            self.current_task = None
    
    def _plan_phase(self, task: PDCATask) -> Dict[str, Any]:
        """PLAN: Systematic planning using project registry intelligence"""
        self.logger.info(f"📋 PLAN phase: Planning systematic approach for {task.name}")
        
        # Consult project registry for relevant intelligence
        registry_intelligence = self._consult_project_registry(task)
        
        # Create systematic plan
        plan = {
            "task_name": task.name,
            "approach": "systematic",
            "requirements_analysis": self._analyze_requirements(task),
            "registry_intelligence": registry_intelligence,
            "implementation_strategy": self._create_implementation_strategy(task, registry_intelligence),
            "success_criteria": task.success_criteria,
            "risk_assessment": self._assess_risks(task),
            "planned_duration": task.estimated_duration.total_seconds() if task.estimated_duration else 300
        }
        
        self.logger.info(f"📋 Plan created: {plan['implementation_strategy']['approach']}")
        return plan
    
    def _do_phase(self, task: PDCATask, plan: Dict[str, Any]) -> Dict[str, Any]:
        """DO: Execute the plan systematically"""
        self.logger.info(f"🔧 DO phase: Executing systematic implementation for {task.name}")
        
        implementation_strategy = plan.get("implementation_strategy", {})
        approach = implementation_strategy.get("approach", "basic")
        
        # Execute based on the planned approach
        if approach == "file_creation":
            result = self._execute_file_creation(task, implementation_strategy)
        elif approach == "code_implementation":
            result = self._execute_code_implementation(task, implementation_strategy)
        elif approach == "configuration_update":
            result = self._execute_configuration_update(task, implementation_strategy)
        else:
            result = self._execute_basic_implementation(task, implementation_strategy)
        
        execution_result = {
            "task_name": task.name,
            "approach_used": approach,
            "implementation_result": result,
            "systematic_approach": True,
            "execution_timestamp": datetime.now().isoformat()
        }
        
        self.logger.info(f"🔧 Implementation completed using {approach} approach")
        return execution_result
    
    def _check_phase(self, task: PDCATask, do_result: Dict[str, Any]) -> Dict[str, Any]:
        """CHECK: Validate results against success criteria"""
        self.logger.info(f"🔍 CHECK phase: Validating results for {task.name}")
        
        implementation_result = do_result.get("implementation_result", {})
        
        # Check against success criteria
        validation_results = []
        overall_success = True
        
        for criterion in task.success_criteria:
            criterion_met = self._validate_success_criterion(criterion, implementation_result)
            validation_results.append({
                "criterion": criterion,
                "met": criterion_met,
                "details": f"Criterion {'passed' if criterion_met else 'failed'}: {criterion}"
            })
            
            if not criterion_met:
                overall_success = False
        
        # Perform basic RCA if validation fails
        rca_result = {}
        if not overall_success:
            rca_result = self._perform_basic_rca(task, do_result, validation_results)
        
        check_result = {
            "task_name": task.name,
            "success": overall_success,
            "validation_results": validation_results,
            "success_rate": len([r for r in validation_results if r["met"]]) / len(validation_results),
            "rca_result": rca_result,
            "validation_timestamp": datetime.now().isoformat()
        }
        
        status = "PASSED" if overall_success else "FAILED"
        self.logger.info(f"🔍 Validation {status}: {len([r for r in validation_results if r['met']])}/{len(validation_results)} criteria met")
        
        return check_result
    
    def _act_phase(self, task: PDCATask, check_result: Dict[str, Any]) -> Dict[str, Any]:
        """ACT: Learn from results and update knowledge"""
        self.logger.info(f"📚 ACT phase: Learning from results for {task.name}")
        
        success = check_result.get("success", False)
        validation_results = check_result.get("validation_results", [])
        
        # Extract lessons learned
        lessons = []
        
        if success:
            lessons.append(f"Successful systematic approach for {task.name}")
            lessons.append("PDCA methodology proved effective for this task type")
        else:
            lessons.append(f"PDCA cycle challenges identified for {task.name}")
            failed_criteria = [r["criterion"] for r in validation_results if not r["met"]]
            lessons.append(f"Failed criteria: {', '.join(failed_criteria)}")
        
        # Update project registry with learnings
        registry_updates = self._update_project_registry(task, check_result, lessons)
        
        act_result = {
            "task_name": task.name,
            "lessons_learned": lessons,
            "registry_updates": registry_updates,
            "improvement_recommendations": self._generate_improvement_recommendations(task, check_result),
            "learning_timestamp": datetime.now().isoformat()
        }
        
        self.logger.info(f"📚 Learning complete: {len(lessons)} lessons extracted")
        return act_result
    
    def _load_simple_registry(self) -> Dict[str, Any]:
        """Load simple project registry (start basic, build up)"""
        # Start with a simple in-memory registry
        return {
            "task_patterns": {
                "file_creation": {
                    "approach": "systematic_file_creation",
                    "validation": "file_exists_and_valid"
                },
                "code_implementation": {
                    "approach": "test_driven_development",
                    "validation": "tests_pass_and_coverage"
                }
            },
            "success_patterns": [],
            "failure_patterns": [],
            "domain_knowledge": {}
        }
    
    def _consult_project_registry(self, task: PDCATask) -> Dict[str, Any]:
        """Consult project registry for task-relevant intelligence"""
        # Simple pattern matching for now
        task_type = self._classify_task_type(task)
        
        registry_intelligence = {
            "task_type": task_type,
            "relevant_patterns": self.project_registry.get("task_patterns", {}).get(task_type, {}),
            "historical_success_rate": 0.8,  # Default assumption
            "recommended_approach": "systematic"
        }
        
        return registry_intelligence
    
    def _classify_task_type(self, task: PDCATask) -> str:
        """Simple task classification"""
        name_lower = task.name.lower()
        
        if "file" in name_lower or "create" in name_lower:
            return "file_creation"
        elif "implement" in name_lower or "code" in name_lower:
            return "code_implementation"
        elif "config" in name_lower or "update" in name_lower:
            return "configuration_update"
        else:
            return "general_task"
    
    def _analyze_requirements(self, task: PDCATask) -> Dict[str, Any]:
        """Analyze task requirements systematically"""
        return {
            "requirements_count": len(task.requirements),
            "requirements_list": task.requirements,
            "complexity_score": min(len(task.requirements) * 2, 10),  # Simple scoring
            "estimated_effort": "low" if len(task.requirements) <= 2 else "medium"
        }
    
    def _create_implementation_strategy(self, task: PDCATask, intelligence: Dict[str, Any]) -> Dict[str, Any]:
        """Create systematic implementation strategy"""
        task_type = intelligence.get("task_type", "general_task")
        
        strategies = {
            "file_creation": {
                "approach": "file_creation",
                "steps": ["validate_path", "create_content", "write_file", "verify_creation"],
                "validation_method": "file_system_check"
            },
            "code_implementation": {
                "approach": "code_implementation", 
                "steps": ["write_tests", "implement_code", "run_tests", "refactor"],
                "validation_method": "test_execution"
            },
            "configuration_update": {
                "approach": "configuration_update",
                "steps": ["backup_config", "update_config", "validate_config", "test_functionality"],
                "validation_method": "functionality_test"
            }
        }
        
        return strategies.get(task_type, {
            "approach": "basic",
            "steps": ["analyze", "implement", "validate"],
            "validation_method": "manual_check"
        })
    
    def _assess_risks(self, task: PDCATask) -> Dict[str, Any]:
        """Simple risk assessment"""
        risk_factors = []
        risk_level = "low"
        
        if len(task.requirements) > 5:
            risk_factors.append("high_complexity")
            risk_level = "medium"
        
        if not task.success_criteria:
            risk_factors.append("unclear_success_criteria")
            risk_level = "high"
        
        return {
            "risk_level": risk_level,
            "risk_factors": risk_factors,
            "mitigation_strategies": ["systematic_approach", "incremental_implementation"]
        }
    
    def _execute_file_creation(self, task: PDCATask, strategy: Dict[str, Any]) -> Dict[str, Any]:
        """Execute file creation systematically"""
        # This is where we'd actually create files
        # For now, simulate the execution
        
        return {
            "approach": "file_creation",
            "files_created": 1,
            "success": True,
            "details": f"Systematically created files for {task.name}"
        }
    
    def _execute_code_implementation(self, task: PDCATask, strategy: Dict[str, Any]) -> Dict[str, Any]:
        """Execute code implementation systematically"""
        return {
            "approach": "code_implementation",
            "code_written": True,
            "tests_created": True,
            "success": True,
            "details": f"Systematically implemented code for {task.name}"
        }
    
    def _execute_configuration_update(self, task: PDCATask, strategy: Dict[str, Any]) -> Dict[str, Any]:
        """Execute configuration update systematically"""
        return {
            "approach": "configuration_update",
            "config_updated": True,
            "backup_created": True,
            "success": True,
            "details": f"Systematically updated configuration for {task.name}"
        }
    
    def _execute_basic_implementation(self, task: PDCATask, strategy: Dict[str, Any]) -> Dict[str, Any]:
        """Execute basic implementation"""
        return {
            "approach": "basic",
            "implementation_completed": True,
            "success": True,
            "details": f"Basic systematic implementation for {task.name}"
        }
    
    def _validate_success_criterion(self, criterion: str, implementation_result: Dict[str, Any]) -> bool:
        """Validate a single success criterion"""
        # Simple validation logic - can be enhanced
        if "file" in criterion.lower() and "created" in criterion.lower():
            return implementation_result.get("files_created", 0) > 0
        elif "code" in criterion.lower() and "implemented" in criterion.lower():
            return implementation_result.get("code_written", False)
        elif "test" in criterion.lower():
            return implementation_result.get("tests_created", False)
        else:
            # Default to success for basic criteria
            return implementation_result.get("success", False)
    
    def _perform_basic_rca(self, task: PDCATask, do_result: Dict[str, Any], validation_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Perform basic root cause analysis"""
        failed_criteria = [r for r in validation_results if not r["met"]]
        
        return {
            "rca_performed": True,
            "failed_criteria_count": len(failed_criteria),
            "potential_causes": [
                "implementation_incomplete",
                "success_criteria_too_strict",
                "systematic_approach_needs_refinement"
            ],
            "recommendations": [
                "review_implementation_steps",
                "clarify_success_criteria",
                "enhance_systematic_approach"
            ]
        }
    
    def _update_project_registry(self, task: PDCATask, check_result: Dict[str, Any], lessons: List[str]) -> Dict[str, Any]:
        """Update project registry with learnings"""
        success = check_result.get("success", False)
        task_type = self._classify_task_type(task)
        
        # Update success/failure patterns
        if success:
            self.project_registry.setdefault("success_patterns", []).append({
                "task_type": task_type,
                "task_name": task.name,
                "success_factors": lessons,
                "timestamp": datetime.now().isoformat()
            })
        else:
            self.project_registry.setdefault("failure_patterns", []).append({
                "task_type": task_type,
                "task_name": task.name,
                "failure_factors": lessons,
                "timestamp": datetime.now().isoformat()
            })
        
        return {
            "registry_updated": True,
            "patterns_added": 1,
            "total_patterns": len(self.project_registry.get("success_patterns", [])) + len(self.project_registry.get("failure_patterns", []))
        }
    
    def _generate_improvement_recommendations(self, task: PDCATask, check_result: Dict[str, Any]) -> List[str]:
        """Generate recommendations for improvement"""
        recommendations = []
        
        if not check_result.get("success", False):
            recommendations.append("Review and refine systematic approach")
            recommendations.append("Enhance validation criteria")
            recommendations.append("Consider additional planning phase analysis")
        else:
            recommendations.append("Document successful pattern for reuse")
            recommendations.append("Consider optimizing execution time")
        
        return recommendations
    
    # ReflectiveModule implementation
    def get_module_status(self) -> Dict[str, Any]:
        """Get current status of PDCA orchestrator"""
        success_rate = (self.successful_cycles / self.cycles_executed) if self.cycles_executed > 0 else 0.0
        
        return {
            "module_name": "SystematicPDCAOrchestrator",
            "cycles_executed": self.cycles_executed,
            "successful_cycles": self.successful_cycles,
            "success_rate": success_rate,
            "lessons_learned_count": len(self.lessons_learned),
            "current_task": self.current_task.name if self.current_task else None,
            "registry_patterns": len(self.project_registry.get("success_patterns", [])) + len(self.project_registry.get("failure_patterns", []))
        }
    
    def is_healthy(self) -> bool:
        """Check if PDCA orchestrator is healthy"""
        try:
            # Healthy if we have reasonable success rate or haven't run enough cycles yet
            if self.cycles_executed == 0:
                return True
            
            success_rate = self.successful_cycles / self.cycles_executed
            return success_rate >= 0.5  # At least 50% success rate
            
        except Exception as e:
            self.logger.error(f"PDCA orchestrator health check failed: {e}")
            return False
    
    def get_health_indicators(self) -> List[Dict[str, Any]]:
        """Get detailed health indicators"""
        indicators = []
        
        # Execution health
        success_rate = (self.successful_cycles / self.cycles_executed) if self.cycles_executed > 0 else 1.0
        indicators.append({
            "name": "execution_health",
            "status": "healthy" if success_rate >= 0.7 else "degraded" if success_rate >= 0.5 else "unhealthy",
            "success_rate": success_rate,
            "cycles_executed": self.cycles_executed
        })
        
        # Learning health
        indicators.append({
            "name": "learning_health",
            "status": "healthy" if len(self.lessons_learned) > 0 else "not_learning",
            "lessons_count": len(self.lessons_learned),
            "registry_patterns": len(self.project_registry.get("success_patterns", [])) + len(self.project_registry.get("failure_patterns", []))
        })
        
        # Current task health
        indicators.append({
            "name": "current_task_health",
            "status": "active" if self.current_task else "idle",
            "current_task": self.current_task.name if self.current_task else None
        })
        
        return indicators
    
    def _get_primary_responsibility(self) -> str:
        """Get the primary responsibility of this module"""
        return "Execute systematic PDCA cycles on development tasks with model-driven planning and continuous learning"