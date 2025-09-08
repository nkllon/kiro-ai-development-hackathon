"""
Risk assessor for DAG orchestration system.

Systematic risk factor analysis, Monte Carlo simulation for timeline and 
success probability estimation with systematic risk-adjusted planning.
"""

import random
import math
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from collections import defaultdict

from ..models.dag_models import (
    TaskNode, MVPRoute, MVPPhase, RiskFactor, 
    ParallelGroup, ResourceRequirements
)
from ..models.enums import TaskStatus, RiskType, RiskImpact


@dataclass
class MonteCarloResult:
    """Monte Carlo simulation result."""
    mean_duration: float  # weeks
    std_deviation: float
    percentile_50: float  # median
    percentile_80: float  # 80th percentile
    percentile_95: float  # 95th percentile
    success_probability: float
    simulation_runs: int


@dataclass
class RiskAssessmentResult:
    """Complete risk assessment result."""
    overall_risk_score: float  # 0.0 to 1.0
    success_probability: float  # 0.0 to 1.0
    risk_factors: List[RiskFactor]
    monte_carlo_analysis: MonteCarloResult
    mitigation_strategies: List[str]
    contingency_plans: List[str]


@dataclass
class SuccessProbabilityFactors:
    """Factors affecting success probability."""
    team_experience: float  # 0.0 to 1.0
    technology_maturity: float  # 0.0 to 1.0
    requirement_clarity: float  # 0.0 to 1.0
    timeline_pressure: float  # 0.0 to 1.0 (higher = more pressure)
    resource_availability: float  # 0.0 to 1.0
    external_dependencies: float  # 0.0 to 1.0 (higher = more dependencies)


class RiskAssessor:
    """
    Systematic risk assessor with BEASTMASTER precision.
    
    Provides Monte Carlo simulation, systematic risk analysis,
    and success probability calculation with extreme accuracy.
    """
    
    def __init__(self):
        self.simulation_runs = 10000  # Monte Carlo iterations
        self.base_success_probability = 0.75  # 75% base success rate
        self.risk_tolerance_threshold = 0.7  # Risk tolerance level
        
        # BEASTMASTER RISK PARAMETERS
        self.critical_risk_threshold = 0.8
        self.high_risk_threshold = 0.6
        self.medium_risk_threshold = 0.4
        
    def assess_systematic_risk_with_prejudice(self, 
                                            mvp_route: MVPRoute,
                                            success_factors: Optional[SuccessProbabilityFactors] = None) -> RiskAssessmentResult:
        """
        Assess systematic risk with BEASTMASTER prejudice and precision.
        
        Args:
            mvp_route: MVP route to assess
            success_factors: Optional success probability factors
            
        Returns:
            RiskAssessmentResult: Complete systematic risk assessment
        """
        # PHASE 1: IDENTIFY ALL RISK FACTORS
        risk_factors = self._identify_comprehensive_risk_factors(mvp_route)
        
        # PHASE 2: CALCULATE OVERALL RISK SCORE
        overall_risk_score = self._calculate_systematic_risk_score(risk_factors, mvp_route)
        
        # PHASE 3: MONTE CARLO SIMULATION
        monte_carlo_result = self._run_monte_carlo_simulation(mvp_route, risk_factors)
        
        # PHASE 4: SUCCESS PROBABILITY CALCULATION
        success_probability = self._calculate_systematic_success_probability(
            mvp_route, risk_factors, success_factors, monte_carlo_result
        )
        
        # PHASE 5: MITIGATION STRATEGIES
        mitigation_strategies = self._generate_mitigation_strategies(risk_factors)
        
        # PHASE 6: CONTINGENCY PLANS
        contingency_plans = self._generate_contingency_plans(risk_factors, mvp_route)
        
        return RiskAssessmentResult(
            overall_risk_score=overall_risk_score,
            success_probability=success_probability,
            risk_factors=risk_factors,
            monte_carlo_analysis=monte_carlo_result,
            mitigation_strategies=mitigation_strategies,
            contingency_plans=contingency_plans
        )
    
    def run_monte_carlo_timeline_simulation(self, 
                                          mvp_route: MVPRoute,
                                          confidence_level: float = 0.95) -> MonteCarloResult:
        """
        Run Monte Carlo simulation for timeline estimation with SYSTEMATIC PRECISION.
        
        Args:
            mvp_route: MVP route to simulate
            confidence_level: Confidence level for estimation
            
        Returns:
            MonteCarloResult: Detailed simulation results
        """
        simulation_results = []
        
        for _ in range(self.simulation_runs):
            # SIMULATE EACH PHASE
            total_duration = 0
            phase_success = True
            
            for phase in mvp_route.phases:
                phase_duration, phase_succeeded = self._simulate_phase_execution(phase)
                total_duration += phase_duration
                
                if not phase_succeeded:
                    phase_success = False
                    total_duration *= 1.5  # Penalty for failure
            
            simulation_results.append({
                'duration': total_duration,
                'success': phase_success
            })
        
        # ANALYZE RESULTS
        durations = [result['duration'] for result in simulation_results]
        successes = [result['success'] for result in simulation_results]
        
        durations.sort()
        
        mean_duration = sum(durations) / len(durations)
        std_deviation = math.sqrt(sum((d - mean_duration) ** 2 for d in durations) / len(durations))
        
        # PERCENTILES
        percentile_50 = durations[int(len(durations) * 0.5)]
        percentile_80 = durations[int(len(durations) * 0.8)]
        percentile_95 = durations[int(len(durations) * 0.95)]
        
        success_probability = sum(successes) / len(successes)
        
        return MonteCarloResult(
            mean_duration=mean_duration,
            std_deviation=std_deviation,
            percentile_50=percentile_50,
            percentile_80=percentile_80,
            percentile_95=percentile_95,
            success_probability=success_probability,
            simulation_runs=self.simulation_runs
        )
    
    def calculate_success_probability_with_factors(self, 
                                                 mvp_route: MVPRoute,
                                                 success_factors: SuccessProbabilityFactors) -> float:
        """
        Calculate success probability with systematic factor analysis.
        
        Args:
            mvp_route: MVP route to analyze
            success_factors: Success probability factors
            
        Returns:
            float: Calculated success probability (0.0 to 1.0)
        """
        base_probability = self.base_success_probability
        
        # FACTOR ADJUSTMENTS
        adjustments = []
        
        # TEAM EXPERIENCE FACTOR
        experience_adjustment = (success_factors.team_experience - 0.5) * 0.3
        adjustments.append(experience_adjustment)
        
        # TECHNOLOGY MATURITY FACTOR
        tech_adjustment = (success_factors.technology_maturity - 0.5) * 0.2
        adjustments.append(tech_adjustment)
        
        # REQUIREMENT CLARITY FACTOR
        clarity_adjustment = (success_factors.requirement_clarity - 0.5) * 0.25
        adjustments.append(clarity_adjustment)
        
        # TIMELINE PRESSURE FACTOR (negative impact)
        pressure_adjustment = -(success_factors.timeline_pressure - 0.5) * 0.2
        adjustments.append(pressure_adjustment)
        
        # RESOURCE AVAILABILITY FACTOR
        resource_adjustment = (success_factors.resource_availability - 0.5) * 0.15
        adjustments.append(resource_adjustment)
        
        # EXTERNAL DEPENDENCIES FACTOR (negative impact)
        dependency_adjustment = -(success_factors.external_dependencies - 0.5) * 0.1
        adjustments.append(dependency_adjustment)
        
        # ROUTE-SPECIFIC FACTORS
        route_adjustment = self._calculate_route_specific_adjustments(mvp_route)
        adjustments.append(route_adjustment)
        
        # COMBINE ADJUSTMENTS
        total_adjustment = sum(adjustments)
        final_probability = base_probability + total_adjustment
        
        return max(0.1, min(0.95, final_probability))  # Clamp between 10% and 95%
    
    # BEASTMASTER RISK IDENTIFICATION METHODS
    
    def _identify_comprehensive_risk_factors(self, mvp_route: MVPRoute) -> List[RiskFactor]:
        """Identify comprehensive risk factors with BEASTMASTER thoroughness."""
        risk_factors = []
        
        # TIMELINE RISKS
        risk_factors.extend(self._identify_timeline_risks(mvp_route))
        
        # TECHNICAL RISKS
        risk_factors.extend(self._identify_technical_risks(mvp_route))
        
        # RESOURCE RISKS
        risk_factors.extend(self._identify_resource_risks(mvp_route))
        
        # DEPENDENCY RISKS
        risk_factors.extend(self._identify_dependency_risks(mvp_route))
        
        # QUALITY RISKS
        risk_factors.extend(self._identify_quality_risks(mvp_route))
        
        # INTEGRATION RISKS
        risk_factors.extend(self._identify_integration_risks(mvp_route))
        
        return risk_factors
    
    def _identify_timeline_risks(self, mvp_route: MVPRoute) -> List[RiskFactor]:
        """Identify timeline-related risks."""
        risks = []
        
        # AGGRESSIVE TIMELINE
        if mvp_route.estimated_timeline < 4:  # Less than 4 weeks
            risks.append(RiskFactor(
                risk_id="aggressive_timeline",
                risk_type=RiskType.TIMELINE_RISK,
                probability=0.7,
                impact=RiskImpact.HIGH,
                affected_tasks=[task.task_id for task in mvp_route.critical_tasks[:3]],
                mitigation_strategy="Add timeline buffer and prioritize critical path tasks"
            ))
        
        # HIGH EFFORT CONCENTRATION
        total_effort = mvp_route.total_estimated_effort
        if total_effort > 800:  # More than 20 weeks for single developer
            risks.append(RiskFactor(
                risk_id="high_effort_concentration",
                risk_type=RiskType.TIMELINE_RISK,
                probability=0.6,
                impact=RiskImpact.MEDIUM,
                affected_tasks=[task.task_id for task in mvp_route.critical_tasks],
                mitigation_strategy="Increase team size or reduce scope"
            ))
        
        # PHASE IMBALANCE
        if len(mvp_route.phases) > 0:
            phase_efforts = [sum(task.estimated_effort for task in phase.tasks) for phase in mvp_route.phases]
            max_effort = max(phase_efforts)
            avg_effort = sum(phase_efforts) / len(phase_efforts)
            
            if max_effort > avg_effort * 2:  # One phase is more than 2x average
                risks.append(RiskFactor(
                    risk_id="phase_imbalance",
                    risk_type=RiskType.TIMELINE_RISK,
                    probability=0.5,
                    impact=RiskImpact.MEDIUM,
                    affected_tasks=[],
                    mitigation_strategy="Rebalance phases to distribute effort more evenly"
                ))
        
        return risks
    
    def _identify_technical_risks(self, mvp_route: MVPRoute) -> List[RiskFactor]:
        """Identify technical risks."""
        risks = []
        
        # COMPLEX TASKS
        complex_tasks = [
            task for task in mvp_route.critical_tasks 
            if task.estimated_effort > 40  # More than 1 week
        ]
        
        if complex_tasks:
            risks.append(RiskFactor(
                risk_id="complex_technical_tasks",
                risk_type=RiskType.TECHNICAL_RISK,
                probability=0.6,
                impact=RiskImpact.MEDIUM,
                affected_tasks=[task.task_id for task in complex_tasks],
                mitigation_strategy="Break down complex tasks into smaller components"
            ))
        
        # UNSTARTED CRITICAL TASKS
        unstarted_critical = [
            task for task in mvp_route.critical_tasks
            if task.completion_status == TaskStatus.NOT_STARTED and task.estimated_effort > 20
        ]
        
        if unstarted_critical:
            risks.append(RiskFactor(
                risk_id="unstarted_critical_tasks",
                risk_type=RiskType.TECHNICAL_RISK,
                probability=0.4,
                impact=RiskImpact.MEDIUM,
                affected_tasks=[task.task_id for task in unstarted_critical],
                mitigation_strategy="Start critical tasks early with proof-of-concept development"
            ))
        
        return risks
    
    def _identify_resource_risks(self, mvp_route: MVPRoute) -> List[RiskFactor]:
        """Identify resource-related risks."""
        risks = []
        
        # SKILL DIVERSITY REQUIREMENTS
        required_skills = set()
        for phase in mvp_route.phases:
            for task in phase.tasks:
                task_text = f"{task.task_name} {task.description}".lower()
                if 'frontend' in task_text:
                    required_skills.add('frontend')
                if 'backend' in task_text:
                    required_skills.add('backend')
                if 'devops' in task_text:
                    required_skills.add('devops')
                if 'design' in task_text:
                    required_skills.add('design')
        
        if len(required_skills) > 3:
            risks.append(RiskFactor(
                risk_id="diverse_skill_requirements",
                risk_type=RiskType.RESOURCE_RISK,
                probability=0.5,
                impact=RiskImpact.MEDIUM,
                affected_tasks=[],
                mitigation_strategy="Ensure team has diverse skills or plan for external expertise"
            ))
        
        # PARALLEL EXECUTION COMPLEXITY
        max_parallel_tasks = 0
        for phase in mvp_route.phases:
            phase_parallel = sum(len(group.tasks) for group in phase.parallel_groups)
            max_parallel_tasks = max(max_parallel_tasks, phase_parallel)
        
        if max_parallel_tasks > 6:  # More than 6 parallel tasks
            risks.append(RiskFactor(
                risk_id="parallel_execution_complexity",
                risk_type=RiskType.RESOURCE_RISK,
                probability=0.4,
                impact=RiskImpact.MEDIUM,
                affected_tasks=[],
                mitigation_strategy="Reduce parallel complexity or increase coordination overhead"
            ))
        
        return risks
    
    def _identify_dependency_risks(self, mvp_route: MVPRoute) -> List[RiskFactor]:
        """Identify dependency-related risks."""
        risks = []
        
        # BLOCKED TASKS
        blocked_tasks = [
            task for task in mvp_route.critical_tasks
            if task.completion_status == TaskStatus.BLOCKED
        ]
        
        if blocked_tasks:
            risks.append(RiskFactor(
                risk_id="blocked_dependencies",
                risk_type=RiskType.DEPENDENCY_RISK,
                probability=0.8,
                impact=RiskImpact.HIGH,
                affected_tasks=[task.task_id for task in blocked_tasks],
                mitigation_strategy="Resolve blocking dependencies immediately or find alternatives"
            ))
        
        # COMPLEX DEPENDENCY CHAINS
        complex_dep_tasks = [
            task for task in mvp_route.critical_tasks
            if len(task.dependencies) > 3
        ]
        
        if complex_dep_tasks:
            risks.append(RiskFactor(
                risk_id="complex_dependency_chains",
                risk_type=RiskType.DEPENDENCY_RISK,
                probability=0.5,
                impact=RiskImpact.MEDIUM,
                affected_tasks=[task.task_id for task in complex_dep_tasks],
                mitigation_strategy="Simplify dependency chains or add parallel alternatives"
            ))
        
        return risks
    
    def _identify_quality_risks(self, mvp_route: MVPRoute) -> List[RiskFactor]:
        """Identify quality-related risks."""
        risks = []
        
        # INSUFFICIENT TESTING TASKS
        testing_tasks = [
            task for task in mvp_route.critical_tasks
            if 'test' in task.task_name.lower() or 'validation' in task.task_name.lower()
        ]
        
        total_tasks = len(mvp_route.critical_tasks)
        testing_ratio = len(testing_tasks) / total_tasks if total_tasks > 0 else 0
        
        if testing_ratio < 0.2:  # Less than 20% testing tasks
            risks.append(RiskFactor(
                risk_id="insufficient_testing",
                risk_type=RiskType.QUALITY_RISK,
                probability=0.6,
                impact=RiskImpact.MEDIUM,
                affected_tasks=[],
                mitigation_strategy="Add comprehensive testing tasks and quality validation"
            ))
        
        return risks
    
    def _identify_integration_risks(self, mvp_route: MVPRoute) -> List[RiskFactor]:
        """Identify integration-related risks."""
        risks = []
        
        # LATE INTEGRATION
        integration_tasks = [
            task for task in mvp_route.critical_tasks
            if 'integration' in task.task_name.lower() or 'integrate' in task.task_name.lower()
        ]
        
        if integration_tasks:
            # Check if integration tasks are in later phases
            total_phases = len(mvp_route.phases)
            late_integration = False
            
            for task in integration_tasks:
                for i, phase in enumerate(mvp_route.phases):
                    if task in phase.tasks and i > total_phases * 0.7:  # In last 30% of phases
                        late_integration = True
                        break
            
            if late_integration:
                risks.append(RiskFactor(
                    risk_id="late_integration",
                    risk_type=RiskType.INTEGRATION_RISK,
                    probability=0.5,
                    impact=RiskImpact.MEDIUM,
                    affected_tasks=[task.task_id for task in integration_tasks],
                    mitigation_strategy="Move integration tasks earlier or add incremental integration"
                ))
        
        return risks
    
    # SYSTEMATIC CALCULATION METHODS
    
    def _calculate_systematic_risk_score(self, 
                                       risk_factors: List[RiskFactor], 
                                       mvp_route: MVPRoute) -> float:
        """Calculate overall systematic risk score."""
        if not risk_factors:
            return 0.2  # Base risk level
        
        # WEIGHTED RISK CALCULATION
        total_weighted_risk = 0.0
        total_weight = 0.0
        
        for risk in risk_factors:
            # IMPACT WEIGHTS
            impact_weight = {
                RiskImpact.LOW: 0.25,
                RiskImpact.MEDIUM: 0.5,
                RiskImpact.HIGH: 0.75,
                RiskImpact.CRITICAL: 1.0
            }.get(risk.impact, 0.5)
            
            # RISK CONTRIBUTION
            risk_contribution = risk.probability * impact_weight
            total_weighted_risk += risk_contribution
            total_weight += impact_weight
        
        # NORMALIZE
        if total_weight > 0:
            normalized_risk = total_weighted_risk / total_weight
        else:
            normalized_risk = 0.2
        
        # ROUTE-SPECIFIC ADJUSTMENTS
        route_risk_adjustment = self._calculate_route_risk_adjustments(mvp_route)
        
        final_risk = min(1.0, normalized_risk + route_risk_adjustment)
        return final_risk
    
    def _calculate_systematic_success_probability(self, 
                                                mvp_route: MVPRoute,
                                                risk_factors: List[RiskFactor],
                                                success_factors: Optional[SuccessProbabilityFactors],
                                                monte_carlo_result: MonteCarloResult) -> float:
        """Calculate systematic success probability."""
        # BASE PROBABILITY FROM MONTE CARLO
        base_probability = monte_carlo_result.success_probability
        
        # RISK FACTOR ADJUSTMENTS
        risk_adjustment = 0.0
        for risk in risk_factors:
            impact_penalty = {
                RiskImpact.LOW: 0.02,
                RiskImpact.MEDIUM: 0.05,
                RiskImpact.HIGH: 0.1,
                RiskImpact.CRITICAL: 0.2
            }.get(risk.impact, 0.05)
            
            risk_adjustment -= risk.probability * impact_penalty
        
        # SUCCESS FACTORS ADJUSTMENTS
        if success_factors:
            factor_adjustment = self._calculate_success_factor_adjustments(success_factors)
        else:
            factor_adjustment = 0.0
        
        # ROUTE COMPLEXITY ADJUSTMENT
        complexity_adjustment = self._calculate_complexity_adjustments(mvp_route)
        
        # COMBINE ADJUSTMENTS
        final_probability = base_probability + risk_adjustment + factor_adjustment + complexity_adjustment
        
        return max(0.1, min(0.95, final_probability))
    
    def _simulate_phase_execution(self, phase: MVPPhase) -> Tuple[float, bool]:
        """Simulate execution of a single phase."""
        # BASE DURATION
        base_duration = phase.estimated_duration
        
        # RANDOM VARIATION (±30%)
        variation = random.uniform(0.7, 1.3)
        actual_duration = base_duration * variation
        
        # SUCCESS PROBABILITY BASED ON PHASE CHARACTERISTICS
        success_probability = 0.85  # Base success rate
        
        # ADJUST FOR PHASE COMPLEXITY
        total_effort = sum(task.estimated_effort for task in phase.tasks)
        if total_effort > 100:  # High effort phase
            success_probability -= 0.1
        
        # ADJUST FOR PARALLEL COMPLEXITY
        if len(phase.parallel_groups) > 3:
            success_probability -= 0.05
        
        # ADJUST FOR TASK STATUS
        incomplete_tasks = [
            task for task in phase.tasks 
            if task.completion_status != TaskStatus.COMPLETED
        ]
        
        if len(incomplete_tasks) > len(phase.tasks) * 0.8:  # More than 80% incomplete
            success_probability -= 0.1
        
        # SIMULATE SUCCESS
        phase_succeeded = random.random() < success_probability
        
        return actual_duration, phase_succeeded
    
    def _calculate_route_specific_adjustments(self, mvp_route: MVPRoute) -> float:
        """Calculate route-specific success probability adjustments."""
        adjustment = 0.0
        
        # TIMELINE PRESSURE
        if mvp_route.estimated_timeline < 6:  # Less than 6 weeks
            adjustment -= 0.1
        elif mvp_route.estimated_timeline > 12:  # More than 12 weeks
            adjustment -= 0.05
        
        # EFFORT DISTRIBUTION
        if len(mvp_route.phases) > 0:
            phase_efforts = [sum(task.estimated_effort for task in phase.tasks) for phase in mvp_route.phases]
            effort_std = math.sqrt(sum((e - sum(phase_efforts)/len(phase_efforts))**2 for e in phase_efforts) / len(phase_efforts))
            
            if effort_std > 50:  # High variation in phase efforts
                adjustment -= 0.05
        
        # COMPLETION STATUS
        completed_tasks = [
            task for task in mvp_route.critical_tasks
            if task.completion_status == TaskStatus.COMPLETED
        ]
        
        completion_ratio = len(completed_tasks) / len(mvp_route.critical_tasks) if mvp_route.critical_tasks else 0
        adjustment += completion_ratio * 0.2  # Bonus for completed work
        
        return adjustment
    
    def _calculate_route_risk_adjustments(self, mvp_route: MVPRoute) -> float:
        """Calculate route-specific risk adjustments."""
        adjustment = 0.0
        
        # PHASE COUNT RISK
        if len(mvp_route.phases) > 5:
            adjustment += 0.1  # More phases = more coordination risk
        
        # CRITICAL TASK COUNT RISK
        if len(mvp_route.critical_tasks) > 20:
            adjustment += 0.05  # More tasks = more complexity risk
        
        return adjustment
    
    def _calculate_success_factor_adjustments(self, success_factors: SuccessProbabilityFactors) -> float:
        """Calculate adjustments based on success factors."""
        adjustment = 0.0
        
        # POSITIVE FACTORS
        adjustment += (success_factors.team_experience - 0.5) * 0.15
        adjustment += (success_factors.technology_maturity - 0.5) * 0.1
        adjustment += (success_factors.requirement_clarity - 0.5) * 0.12
        adjustment += (success_factors.resource_availability - 0.5) * 0.08
        
        # NEGATIVE FACTORS
        adjustment -= (success_factors.timeline_pressure - 0.5) * 0.1
        adjustment -= (success_factors.external_dependencies - 0.5) * 0.05
        
        return adjustment
    
    def _calculate_complexity_adjustments(self, mvp_route: MVPRoute) -> float:
        """Calculate complexity-based adjustments."""
        adjustment = 0.0
        
        # TASK COMPLEXITY
        complex_tasks = [
            task for task in mvp_route.critical_tasks
            if task.estimated_effort > 30
        ]
        
        complexity_ratio = len(complex_tasks) / len(mvp_route.critical_tasks) if mvp_route.critical_tasks else 0
        adjustment -= complexity_ratio * 0.1
        
        return adjustment
    
    # MITIGATION AND CONTINGENCY METHODS
    
    def _generate_mitigation_strategies(self, risk_factors: List[RiskFactor]) -> List[str]:
        """Generate systematic mitigation strategies."""
        strategies = set()
        
        for risk in risk_factors:
            if risk.mitigation_strategy:
                strategies.add(risk.mitigation_strategy)
        
        # GENERAL STRATEGIES BASED ON RISK TYPES
        risk_types = [risk.risk_type for risk in risk_factors]
        
        if RiskType.TIMELINE_RISK in risk_types:
            strategies.add("Implement systematic timeline monitoring with early warning alerts")
        
        if RiskType.TECHNICAL_RISK in risk_types:
            strategies.add("Conduct systematic technical risk assessment and proof-of-concept validation")
        
        if RiskType.RESOURCE_RISK in risk_types:
            strategies.add("Establish systematic resource allocation with backup team members")
        
        if RiskType.DEPENDENCY_RISK in risk_types:
            strategies.add("Create systematic dependency tracking with alternative path planning")
        
        if RiskType.QUALITY_RISK in risk_types:
            strategies.add("Implement systematic quality gates with continuous validation")
        
        return list(strategies)
    
    def _generate_contingency_plans(self, 
                                  risk_factors: List[RiskFactor], 
                                  mvp_route: MVPRoute) -> List[str]:
        """Generate systematic contingency plans."""
        plans = []
        
        # HIGH-IMPACT RISK CONTINGENCIES
        high_impact_risks = [risk for risk in risk_factors if risk.impact in [RiskImpact.HIGH, RiskImpact.CRITICAL]]
        
        if high_impact_risks:
            plans.append("🚨 Emergency scope reduction plan: Remove non-critical features to meet timeline")
            plans.append("⚡ Resource escalation plan: Add additional team members or external expertise")
            plans.append("🔄 Alternative implementation plan: Simplified approach for critical components")
        
        # TIMELINE CONTINGENCIES
        timeline_risks = [risk for risk in risk_factors if risk.risk_type == RiskType.TIMELINE_RISK]
        if timeline_risks:
            plans.append("📅 Timeline extension plan: Negotiate additional time with stakeholders")
            plans.append("🎯 MVP scope adjustment: Focus on core value demonstration only")
        
        # TECHNICAL CONTINGENCIES
        technical_risks = [risk for risk in risk_factors if risk.risk_type == RiskType.TECHNICAL_RISK]
        if technical_risks:
            plans.append("🛠️ Technical pivot plan: Alternative technology stack or approach")
            plans.append("🔬 Prototype validation plan: Build minimal proof-of-concept first")
        
        # RESOURCE CONTINGENCIES
        resource_risks = [risk for risk in risk_factors if risk.risk_type == RiskType.RESOURCE_RISK]
        if resource_risks:
            plans.append("👥 Team augmentation plan: Bring in specialists or consultants")
            plans.append("🔄 Task redistribution plan: Rebalance workload across team members")
        
        return plans if plans else ["✅ No specific contingency plans required - risk levels acceptable"]