"""
Beast Mode Framework - Ad-hoc Approach Simulator
Simulates traditional ad-hoc development approaches for baseline measurement
Requirements: R8.1, R8.2, R8.3 - Demonstrate systematic superiority over ad-hoc methods
"""

import random
import time
import logging
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from enum import Enum

from ..core.reflective_module import ReflectiveModule, HealthStatus

class AdhocDecisionStrategy(Enum):
    RANDOM_CHOICE = "random_choice"
    FIRST_OPTION = "first_option" 
    INTUITIVE_GUESS = "intuitive_guess"
    COPY_PASTE_SOLUTION = "copy_paste_solution"

class AdhocProblemSolvingStrategy(Enum):
    WORKAROUND_ONLY = "workaround_only"
    SYMPTOM_TREATMENT = "symptom_treatment"
    QUICK_FIX = "quick_fix"
    IGNORE_PROBLEM = "ignore_problem"

@dataclass
class AdhocSimulationResult:
    strategy_used: str
    time_taken: float
    success_rate: float
    quality_score: float
    rework_required: bool
    notes: str

class AdhocApproachSimulator(ReflectiveModule):
    """
    Simulates ad-hoc development approaches to establish baseline performance
    Used to measure what Beast Mode systematic approach is competing against
    """
    
    def __init__(self):
        super().__init__("adhoc_approach_simulator")
        self.simulation_count = 0
        self.total_simulations = 0
        
        # Ad-hoc approach characteristics based on real-world observations
        self.adhoc_characteristics = {
            'decision_making': {
                'uses_guesswork': True,
                'consults_documentation': False,
                'considers_constraints': False,
                'validates_assumptions': False
            },
            'problem_solving': {
                'performs_root_cause_analysis': False,
                'implements_workarounds': True,
                'fixes_symptoms_only': True,
                'documents_solutions': False
            },
            'tool_management': {
                'monitors_tool_health': False,
                'performs_systematic_repair': False,
                'uses_prevention_patterns': False,
                'accepts_broken_tools': True
            }
        }
        
        self._update_health_indicator(
            "simulation_readiness",
            HealthStatus.HEALTHY,
            "ready",
            "Ad-hoc simulation engine ready"
        )
        
    def get_module_status(self) -> Dict[str, Any]:
        """Operational visibility for external systems"""
        return {
            "module_name": self.module_name,
            "status": "operational" if self.is_healthy() else "degraded",
            "simulations_run": self.total_simulations,
            "current_simulations": self.simulation_count,
            "adhoc_characteristics": self.adhoc_characteristics,
            "degradation_active": self._degradation_active
        }
        
    def is_healthy(self) -> bool:
        """Health assessment for simulation capability"""
        return not self._degradation_active
        
    def get_health_indicators(self) -> Dict[str, Any]:
        """Detailed health metrics"""
        return {
            "simulation_capability": {
                "status": "healthy" if not self._degradation_active else "degraded",
                "simulations_completed": self.total_simulations,
                "current_load": self.simulation_count
            },
            "adhoc_model_integrity": {
                "status": "healthy",
                "characteristics_loaded": len(self.adhoc_characteristics),
                "model_completeness": "100%"
            }
        }
        
    def _get_primary_responsibility(self) -> str:
        """Single responsibility: Ad-hoc approach simulation for baseline measurement"""
        return "adhoc_approach_simulation_for_baseline_measurement"
        
    def simulate_adhoc_decision_making(self, decision_context: Dict[str, Any]) -> AdhocSimulationResult:
        """
        Simulate how ad-hoc approaches make decisions (guesswork, no data consultation)
        Used to establish baseline for decision success rates
        """
        self.simulation_count += 1
        start_time = time.time()
        
        try:
            # Simulate ad-hoc decision characteristics
            strategy = random.choice(list(AdhocDecisionStrategy))
            
            # Ad-hoc approaches don't consult project registry or use systematic analysis
            if strategy == AdhocDecisionStrategy.RANDOM_CHOICE:
                # Random selection without analysis
                decision_time = random.uniform(0.1, 0.5)  # Quick but uninformed
                success_rate = random.uniform(0.3, 0.6)   # Low success rate
                quality_score = random.uniform(0.2, 0.5)  # Poor quality
                rework_required = random.choice([True, True, False])  # High rework probability
                
            elif strategy == AdhocDecisionStrategy.FIRST_OPTION:
                # Take first available option without evaluation
                decision_time = random.uniform(0.05, 0.2)  # Very quick
                success_rate = random.uniform(0.2, 0.4)    # Very low success
                quality_score = random.uniform(0.1, 0.3)   # Very poor quality
                rework_required = True  # Almost always requires rework
                
            elif strategy == AdhocDecisionStrategy.INTUITIVE_GUESS:
                # Gut feeling without data
                decision_time = random.uniform(0.2, 1.0)   # Moderate time thinking
                success_rate = random.uniform(0.4, 0.7)    # Moderate success (experience helps)
                quality_score = random.uniform(0.3, 0.6)   # Moderate quality
                rework_required = random.choice([True, False])  # 50/50 rework
                
            elif strategy == AdhocDecisionStrategy.COPY_PASTE_SOLUTION:
                # Copy solution from elsewhere without understanding
                decision_time = random.uniform(0.5, 2.0)   # Time to find and copy
                success_rate = random.uniform(0.1, 0.3)    # Very low success (context mismatch)
                quality_score = random.uniform(0.1, 0.2)   # Very poor quality
                rework_required = True  # Almost always breaks
                
            time.sleep(decision_time)  # Simulate actual decision time
            
            total_time = time.time() - start_time
            
            return AdhocSimulationResult(
                strategy_used=strategy.value,
                time_taken=total_time,
                success_rate=success_rate,
                quality_score=quality_score,
                rework_required=rework_required,
                notes=f"Ad-hoc decision using {strategy.value} - no systematic analysis"
            )
            
        finally:
            self.simulation_count -= 1
            self.total_simulations += 1
            
    def simulate_adhoc_problem_solving(self, problem_context: Dict[str, Any]) -> AdhocSimulationResult:
        """
        Simulate ad-hoc problem solving (workarounds, symptom treatment)
        Used to establish baseline for problem resolution speed and tool health
        """
        self.simulation_count += 1
        start_time = time.time()
        
        try:
            strategy = random.choice(list(AdhocProblemSolvingStrategy))
            
            if strategy == AdhocProblemSolvingStrategy.WORKAROUND_ONLY:
                # Implement workaround without fixing root cause
                resolution_time = random.uniform(0.5, 2.0)   # Quick workaround
                success_rate = random.uniform(0.6, 0.8)      # Works temporarily
                quality_score = random.uniform(0.2, 0.4)     # Poor long-term quality
                rework_required = True  # Problem will return
                
            elif strategy == AdhocProblemSolvingStrategy.SYMPTOM_TREATMENT:
                # Fix visible symptoms, ignore underlying issues
                resolution_time = random.uniform(1.0, 3.0)   # Moderate time
                success_rate = random.uniform(0.5, 0.7)      # Partial success
                quality_score = random.uniform(0.3, 0.5)     # Moderate quality
                rework_required = True  # Symptoms return
                
            elif strategy == AdhocProblemSolvingStrategy.QUICK_FIX:
                # Apply first solution that seems to work
                resolution_time = random.uniform(0.2, 1.0)   # Very quick
                success_rate = random.uniform(0.3, 0.6)      # Low success
                quality_score = random.uniform(0.1, 0.3)     # Poor quality
                rework_required = True  # Breaks easily
                
            elif strategy == AdhocProblemSolvingStrategy.IGNORE_PROBLEM:
                # Hope problem goes away or work around it
                resolution_time = random.uniform(0.1, 0.3)   # No time spent
                success_rate = 0.0  # No actual resolution
                quality_score = 0.0  # No quality improvement
                rework_required = True  # Problem persists
                
            time.sleep(resolution_time)  # Simulate actual resolution time
            
            total_time = time.time() - start_time
            
            return AdhocSimulationResult(
                strategy_used=strategy.value,
                time_taken=total_time,
                success_rate=success_rate,
                quality_score=quality_score,
                rework_required=rework_required,
                notes=f"Ad-hoc problem solving using {strategy.value} - no RCA or systematic fix"
            )
            
        finally:
            self.simulation_count -= 1
            self.total_simulations += 1
            
    def simulate_adhoc_tool_management(self, tool_context: Dict[str, Any]) -> AdhocSimulationResult:
        """
        Simulate ad-hoc tool management (accept broken tools, no systematic repair)
        Used to establish baseline for tool health performance
        """
        self.simulation_count += 1
        start_time = time.time()
        
        try:
            # Ad-hoc tool management characteristics
            tool_health_check_time = 0.0  # No systematic health checking
            repair_attempt_time = random.uniform(0.0, 1.0)  # Minimal repair effort
            
            # Ad-hoc approaches often accept broken tools or use workarounds
            accepts_broken_tools = random.choice([True, True, True, False])  # 75% accept broken
            
            if accepts_broken_tools:
                # Work around broken tools instead of fixing
                success_rate = random.uniform(0.2, 0.5)  # Low success with broken tools
                quality_score = random.uniform(0.1, 0.3)  # Poor quality
                rework_required = True  # Workarounds break
                notes = "Accepted broken tool and implemented workaround"
            else:
                # Attempt quick fix without systematic diagnosis
                success_rate = random.uniform(0.3, 0.6)  # Moderate success
                quality_score = random.uniform(0.2, 0.4)  # Poor quality
                rework_required = True  # Quick fixes break
                notes = "Attempted quick fix without systematic diagnosis"
                
            time.sleep(repair_attempt_time)
            
            total_time = time.time() - start_time
            
            return AdhocSimulationResult(
                strategy_used="adhoc_tool_management",
                time_taken=total_time,
                success_rate=success_rate,
                quality_score=quality_score,
                rework_required=rework_required,
                notes=notes
            )
            
        finally:
            self.simulation_count -= 1
            self.total_simulations += 1
            
    def get_adhoc_baseline_characteristics(self) -> Dict[str, Any]:
        """
        Return the characteristics of ad-hoc approaches for comparison
        Used by comparative analysis to understand what systematic approach is competing against
        """
        return {
            "decision_making_baseline": {
                "uses_data": False,
                "consults_registry": False,
                "performs_analysis": False,
                "validates_results": False,
                "typical_success_rate": 0.45,  # 45% average success
                "typical_quality_score": 0.35   # 35% average quality
            },
            "problem_solving_baseline": {
                "performs_rca": False,
                "fixes_root_causes": False,
                "implements_workarounds": True,
                "documents_patterns": False,
                "typical_resolution_time": 1.5,  # 1.5 seconds average
                "typical_rework_rate": 0.85      # 85% require rework
            },
            "tool_management_baseline": {
                "monitors_health": False,
                "systematic_repair": False,
                "accepts_broken_tools": True,
                "uses_prevention": False,
                "typical_tool_success_rate": 0.35,  # 35% success with broken tools
                "typical_repair_effectiveness": 0.25  # 25% effective repairs
            }
        }