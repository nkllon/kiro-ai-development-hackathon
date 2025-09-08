"""
Parallel execution optimizer for DAG orchestration system.

Identifies maximum parallelism within dependency constraints and optimizes
parallel execution with systematic bottleneck identification and coordination.
"""

from typing import Dict, List, Set, Tuple, Optional
from dataclasses import dataclass
from collections import defaultdict, deque
import math

from ..models.dag_models import (
    TaskNode, ParallelGroup, OptimizedExecution, ExecutionPhase,
    ResourceRequirements, ResourceAllocation, TeamAssignment
)
from ..models.enums import TaskStatus, OptimizationStrategy, ParallelizationLevel
from ..analysis.dependency_mapper import ConstraintGraph


@dataclass
class ParallelOpportunity:
    """Parallel execution opportunity."""
    opportunity_id: str
    tasks: List[TaskNode]
    estimated_speedup: float  # Expected speedup ratio
    coordination_overhead: float
    resource_requirements: ResourceRequirements
    constraints: List[str]


@dataclass
class OptimizationResult:
    """Parallel optimization result."""
    optimized_execution: OptimizedExecution
    parallel_opportunities: List[ParallelOpportunity]
    bottlenecks: List[str]
    optimization_metrics: Dict[str, float]
    recommendations: List[str]


class ParallelExecutionOptimizer:
    """
    Systematic parallel execution optimizer with BEASTMASTER efficiency.
    
    Maximizes parallel execution opportunities while respecting dependencies,
    resource constraints, and systematic quality requirements.
    """
    
    def __init__(self):
        self.max_parallel_tasks = 8  # Maximum tasks per parallel group
        self.coordination_overhead_base = 0.1  # 10% base overhead
        self.efficiency_threshold = 0.7  # Minimum efficiency for parallelization
        self.resource_utilization_target = 0.85  # Target resource utilization    
    a
sync def optimize_parallel_execution_with_extreme_prejudice(self, 
                                                               execution_plan: 'ExecutionPlan', 
                                                               resource_constraints: 'ResourceConstraints') -> OptimizedExecution:
        """
        Optimize execution plan for MAXIMUM parallelism with BEASTMASTER precision.
        
        Args:
            execution_plan: Initial execution plan with dependencies
            resource_constraints: Available resources and limitations
            
        Returns:
            OptimizedExecution: Systematically optimized parallel execution strategy
        """
        # PHASE 1: IDENTIFY PARALLEL OPPORTUNITIES
        parallel_opportunities = self._identify_systematic_parallel_opportunities(
            execution_plan.tasks, execution_plan.constraint_graph
        )
        
        # PHASE 2: OPTIMIZE PARALLEL GROUPS
        optimized_groups = self._optimize_parallel_groups_with_prejudice(
            parallel_opportunities, resource_constraints
        )
        
        # PHASE 3: CREATE EXECUTION PHASES
        execution_phases = self._create_systematic_execution_phases(
            optimized_groups, execution_plan.constraint_graph
        )
        
        # PHASE 4: CALCULATE RESOURCE ALLOCATION
        resource_allocation = await self._calculate_optimal_resource_allocation(
            execution_phases, resource_constraints
        )
        
        # PHASE 5: IDENTIFY BOTTLENECKS
        bottlenecks = self._identify_systematic_bottlenecks(
            execution_phases, resource_allocation
        )
        
        # PHASE 6: CALCULATE METRICS
        timeline = self._calculate_optimized_timeline(execution_phases)
        max_parallelism = self._calculate_maximum_parallelism(optimized_groups)
        
        return OptimizedExecution(
            execution_id=f"optimized_{execution_plan.plan_id}",
            execution_phases=execution_phases,
            resource_allocation=resource_allocation,
            parallel_groups=optimized_groups,
            estimated_timeline=timeline,
            maximum_parallelism=max_parallelism,
            bottlenecks=bottlenecks
        )
    
    def identify_maximum_parallelism_opportunities(self, 
                                                 constraint_graph: ConstraintGraph) -> List[ParallelOpportunity]:
        """
        Identify MAXIMUM parallelism opportunities within dependency constraints.
        
        Args:
            constraint_graph: Complete constraint graph with dependencies
            
        Returns:
            List[ParallelOpportunity]: All systematic parallel opportunities
        """
        opportunities = []
        
        # ANALYZE EACH DEPENDENCY LAYER
        for layer, task_ids in constraint_graph.dependency_layers.items():
            if len(task_ids) < 2:
                continue  # Need at least 2 tasks for parallelism
            
            # GET TASK NODES
            layer_tasks = [
                constraint_graph.nodes[task_id] 
                for task_id in task_ids 
                if task_id in constraint_graph.nodes
            ]
            
            # IDENTIFY PARALLEL GROUPS WITHIN LAYER
            parallel_groups = self._group_tasks_for_parallel_execution(layer_tasks)
            
            for i, group in enumerate(parallel_groups):
                if len(group) >= 2:  # Minimum for parallel execution
                    opportunity = self._create_parallel_opportunity(
                        f"layer_{layer}_group_{i}", group
                    )
                    opportunities.append(opportunity)
        
        return opportunities   
 
    async def calculate_optimal_resource_allocation(self, 
                                                  optimized_execution: OptimizedExecution,
                                                  team_capabilities: 'TeamCapabilities') -> ResourceAllocation:
        """
        Calculate OPTIMAL resource allocation for parallel execution.
        
        Args:
            optimized_execution: Optimized execution plan
            team_capabilities: Available team capabilities
            
        Returns:
            ResourceAllocation: Systematic team and resource assignment
        """
        # ANALYZE RESOURCE REQUIREMENTS
        total_requirements = self._analyze_total_resource_requirements(optimized_execution)
        
        # CREATE TEAM ASSIGNMENTS
        team_assignments = self._create_systematic_team_assignments(
            optimized_execution, team_capabilities, total_requirements
        )
        
        # CALCULATE UTILIZATION
        resource_utilization = self._calculate_resource_utilization(
            team_assignments, total_requirements
        )
        
        # IDENTIFY BOTTLENECKS
        bottleneck_resources = self._identify_resource_bottlenecks(
            team_assignments, total_requirements
        )
        
        # GENERATE SCALING RECOMMENDATIONS
        scaling_recommendations = self._generate_scaling_recommendations(
            bottleneck_resources, resource_utilization
        )
        
        return ResourceAllocation(
            teams=team_assignments,
            resource_utilization=resource_utilization,
            bottleneck_resources=bottleneck_resources,
            scaling_recommendations=scaling_recommendations
        )
    
    # BEASTMASTER OPTIMIZATION METHODS
    
    def _identify_systematic_parallel_opportunities(self, 
                                                  tasks: List[TaskNode],
                                                  constraint_graph: ConstraintGraph) -> List[ParallelOpportunity]:
        """Identify systematic parallel opportunities with BEASTMASTER precision."""
        opportunities = []
        
        # STRATEGY 1: LAYER-BASED PARALLELISM
        layer_opportunities = self._identify_layer_based_opportunities(constraint_graph)
        opportunities.extend(layer_opportunities)
        
        # STRATEGY 2: SKILL-BASED PARALLELISM
        skill_opportunities = self._identify_skill_based_opportunities(tasks)
        opportunities.extend(skill_opportunities)
        
        # STRATEGY 3: EFFORT-BASED PARALLELISM
        effort_opportunities = self._identify_effort_based_opportunities(tasks)
        opportunities.extend(effort_opportunities)
        
        # STRATEGY 4: INDEPENDENT TASK PARALLELISM
        independent_opportunities = self._identify_independent_task_opportunities(tasks, constraint_graph)
        opportunities.extend(independent_opportunities)
        
        return opportunities
    
    def _optimize_parallel_groups_with_prejudice(self, 
                                               opportunities: List[ParallelOpportunity],
                                               resource_constraints: 'ResourceConstraints') -> List[ParallelGroup]:
        """Optimize parallel groups with SYSTEMATIC PREJUDICE."""
        optimized_groups = []
        
        # SORT OPPORTUNITIES BY POTENTIAL SPEEDUP
        sorted_opportunities = sorted(
            opportunities, 
            key=lambda x: x.estimated_speedup, 
            reverse=True
        )
        
        used_tasks = set()
        
        for opportunity in sorted_opportunities:
            # CHECK IF TASKS ARE ALREADY USED
            if any(task.task_id in used_tasks for task in opportunity.tasks):
                continue
            
            # CHECK RESOURCE CONSTRAINTS
            if self._meets_resource_constraints(opportunity, resource_constraints):
                # CREATE OPTIMIZED PARALLEL GROUP
                group = self._create_optimized_parallel_group(opportunity)
                optimized_groups.append(group)
                
                # MARK TASKS AS USED
                for task in opportunity.tasks:
                    used_tasks.add(task.task_id)
        
        return optimized_groups    
    
def _create_systematic_execution_phases(self, 
                                          parallel_groups: List[ParallelGroup],
                                          constraint_graph: ConstraintGraph) -> List[ExecutionPhase]:
        """Create systematic execution phases with BEASTMASTER organization."""
        phases = []
        
        # GROUP BY DEPENDENCY LAYERS
        layer_groups = defaultdict(list)
        
        for group in parallel_groups:
            # DETERMINE LAYER FOR THIS GROUP
            group_layer = self._determine_group_layer(group, constraint_graph)
            layer_groups[group_layer].append(group)
        
        # CREATE PHASES FROM LAYERS
        for layer in sorted(layer_groups.keys()):
            groups = layer_groups[layer]
            
            # CALCULATE PHASE REQUIREMENTS
            phase_tasks = []
            for group in groups:
                phase_tasks.extend(group.tasks)
            
            phase_requirements = self._calculate_phase_resource_requirements(phase_tasks)
            
            # CALCULATE PHASE DURATION
            max_group_duration = max(group.estimated_duration for group in groups) if groups else 1
            
            # GET SATISFIED DEPENDENCIES
            dependencies_satisfied = []
            for task in phase_tasks:
                dependencies_satisfied.extend(task.requirements_traced)
            
            phase = ExecutionPhase(
                phase_name=f"Parallel Execution Phase {layer + 1}",
                tasks=phase_tasks,
                parallel_groups=groups,
                dependencies_satisfied=list(set(dependencies_satisfied)),
                estimated_duration=max_group_duration,
                resource_requirements=phase_requirements
            )
            
            phases.append(phase)
        
        return phases
    
    # PARALLEL OPPORTUNITY IDENTIFICATION METHODS
    
    def _identify_layer_based_opportunities(self, constraint_graph: ConstraintGraph) -> List[ParallelOpportunity]:
        """Identify opportunities based on dependency layers."""
        opportunities = []
        
        for layer, task_ids in constraint_graph.dependency_layers.items():
            if len(task_ids) >= 2:
                layer_tasks = [
                    constraint_graph.nodes[task_id] 
                    for task_id in task_ids 
                    if task_id in constraint_graph.nodes
                ]
                
                # CREATE OPPORTUNITY FOR ENTIRE LAYER
                opportunity = self._create_parallel_opportunity(
                    f"layer_based_{layer}", layer_tasks
                )
                opportunities.append(opportunity)
        
        return opportunities
    
    def _identify_skill_based_opportunities(self, tasks: List[TaskNode]) -> List[ParallelOpportunity]:
        """Identify opportunities based on required skills."""
        opportunities = []
        
        # GROUP TASKS BY SKILL REQUIREMENTS
        skill_groups = defaultdict(list)
        
        for task in tasks:
            required_skills = self._extract_task_skills(task)
            
            for skill in required_skills:
                skill_groups[skill].append(task)
        
        # CREATE OPPORTUNITIES FOR SKILL GROUPS
        for skill, skill_tasks in skill_groups.items():
            if len(skill_tasks) >= 2:
                opportunity = self._create_parallel_opportunity(
                    f"skill_based_{skill.lower().replace(' ', '_')}", skill_tasks
                )
                opportunities.append(opportunity)
        
        return opportunities
    
    def _identify_effort_based_opportunities(self, tasks: List[TaskNode]) -> List[ParallelOpportunity]:
        """Identify opportunities based on similar effort levels."""
        opportunities = []
        
        # GROUP TASKS BY EFFORT RANGES
        effort_groups = {
            'small': [],    # 1-8 hours
            'medium': [],   # 9-24 hours  
            'large': [],    # 25+ hours
        }
        
        for task in tasks:
            if task.estimated_effort <= 8:
                effort_groups['small'].append(task)
            elif task.estimated_effort <= 24:
                effort_groups['medium'].append(task)
            else:
                effort_groups['large'].append(task)
        
        # CREATE OPPORTUNITIES FOR EFFORT GROUPS
        for effort_type, effort_tasks in effort_groups.items():
            if len(effort_tasks) >= 2:
                opportunity = self._create_parallel_opportunity(
                    f"effort_based_{effort_type}", effort_tasks
                )
                opportunities.append(opportunity)
        
        return opportunities 
   
    def _identify_independent_task_opportunities(self, 
                                               tasks: List[TaskNode],
                                               constraint_graph: ConstraintGraph) -> List[ParallelOpportunity]:
        """Identify opportunities for truly independent tasks."""
        opportunities = []
        
        # FIND TASKS WITH NO DEPENDENCIES
        independent_tasks = []
        
        for task in tasks:
            dependencies = constraint_graph.get_dependencies(task.task_id)
            if not dependencies:  # No dependencies
                independent_tasks.append(task)
        
        # GROUP INDEPENDENT TASKS
        if len(independent_tasks) >= 2:
            # CREATE MULTIPLE GROUPS TO AVOID OVER-PARALLELIZATION
            group_size = min(self.max_parallel_tasks, len(independent_tasks))
            
            for i in range(0, len(independent_tasks), group_size):
                group_tasks = independent_tasks[i:i + group_size]
                if len(group_tasks) >= 2:
                    opportunity = self._create_parallel_opportunity(
                        f"independent_group_{i // group_size}", group_tasks
                    )
                    opportunities.append(opportunity)
        
        return opportunities
    
    def _create_parallel_opportunity(self, 
                                   opportunity_id: str, 
                                   tasks: List[TaskNode]) -> ParallelOpportunity:
        """Create a parallel opportunity from tasks."""
        # CALCULATE ESTIMATED SPEEDUP
        estimated_speedup = self._calculate_estimated_speedup(tasks)
        
        # CALCULATE COORDINATION OVERHEAD
        coordination_overhead = self._calculate_coordination_overhead(tasks)
        
        # CALCULATE RESOURCE REQUIREMENTS
        resource_requirements = self._calculate_opportunity_resource_requirements(tasks)
        
        # IDENTIFY CONSTRAINTS
        constraints = self._identify_opportunity_constraints(tasks)
        
        return ParallelOpportunity(
            opportunity_id=opportunity_id,
            tasks=tasks,
            estimated_speedup=estimated_speedup,
            coordination_overhead=coordination_overhead,
            resource_requirements=resource_requirements,
            constraints=constraints
        )
    
    def _calculate_estimated_speedup(self, tasks: List[TaskNode]) -> float:
        """Calculate estimated speedup from parallelization."""
        if len(tasks) <= 1:
            return 1.0
        
        # THEORETICAL MAXIMUM SPEEDUP
        theoretical_speedup = len(tasks)
        
        # APPLY EFFICIENCY FACTORS
        
        # COORDINATION OVERHEAD REDUCTION
        coordination_penalty = 1.0 - (len(tasks) - 1) * 0.05  # 5% penalty per additional task
        
        # EFFORT VARIANCE PENALTY
        efforts = [task.estimated_effort for task in tasks]
        avg_effort = sum(efforts) / len(efforts)
        effort_variance = sum((e - avg_effort) ** 2 for e in efforts) / len(efforts)
        variance_penalty = 1.0 - min(0.3, effort_variance / (avg_effort ** 2))  # Cap at 30% penalty
        
        # SKILL DIVERSITY BONUS
        required_skills = set()
        for task in tasks:
            task_skills = self._extract_task_skills(task)
            required_skills.update(task_skills)
        
        skill_bonus = 1.0 + min(0.2, len(required_skills) * 0.05)  # Up to 20% bonus
        
        # CALCULATE REALISTIC SPEEDUP
        realistic_speedup = theoretical_speedup * coordination_penalty * variance_penalty * skill_bonus
        
        return max(1.0, min(theoretical_speedup, realistic_speedup))
    
    def _calculate_coordination_overhead(self, tasks: List[TaskNode]) -> float:
        """Calculate coordination overhead for parallel tasks."""
        base_overhead = self.coordination_overhead_base
        
        # INCREASE WITH NUMBER OF TASKS
        task_overhead = (len(tasks) - 1) * 0.02  # 2% per additional task
        
        # INCREASE WITH COMPLEXITY
        avg_complexity = sum(task.estimated_effort for task in tasks) / len(tasks)
        complexity_overhead = min(0.1, avg_complexity / 100)  # Up to 10% for very complex tasks
        
        # INCREASE WITH SKILL DIVERSITY
        required_skills = set()
        for task in tasks:
            task_skills = self._extract_task_skills(task)
            required_skills.update(task_skills)
        
        skill_overhead = len(required_skills) * 0.01  # 1% per different skill
        
        total_overhead = base_overhead + task_overhead + complexity_overhead + skill_overhead
        
        return min(0.5, total_overhead)  # Cap at 50% overhead
    
    def _extract_task_skills(self, task: TaskNode) -> List[str]:
        """Extract required skills from task."""
        skills = []
        task_text = f"{task.task_name} {task.description}".lower()
        
        # TECHNICAL SKILLS
        skill_keywords = {
            'python': 'Python Development',
            'javascript': 'JavaScript Development',
            'frontend': 'Frontend Development',
            'backend': 'Backend Development',
            'api': 'API Development',
            'database': 'Database Development',
            'test': 'Testing & QA',
            'devops': 'DevOps',
            'design': 'UI/UX Design',
            'documentation': 'Technical Writing'
        }
        
        for keyword, skill in skill_keywords.items():
            if keyword in task_text:
                skills.append(skill)
        
        return skills if skills else ['General Development'] 
   
    # RESOURCE ALLOCATION AND OPTIMIZATION METHODS
    
    def _calculate_opportunity_resource_requirements(self, tasks: List[TaskNode]) -> ResourceRequirements:
        """Calculate resource requirements for parallel opportunity."""
        total_effort = sum(task.estimated_effort for task in tasks)
        required_skills = []
        
        for task in tasks:
            task_skills = self._extract_task_skills(task)
            required_skills.extend(task_skills)
        
        unique_skills = list(set(required_skills))
        developers_needed = min(len(tasks), len(unique_skills))  # One dev per skill or task
        
        tools_required = self._identify_required_tools_for_tasks(tasks)
        
        return ResourceRequirements(
            developers_needed=developers_needed,
            skill_requirements=unique_skills,
            estimated_hours=total_effort,
            tools_required=tools_required
        )
    
    def _identify_opportunity_constraints(self, tasks: List[TaskNode]) -> List[str]:
        """Identify constraints for parallel opportunity."""
        constraints = []
        
        # SKILL CONSTRAINTS
        required_skills = set()
        for task in tasks:
            task_skills = self._extract_task_skills(task)
            required_skills.update(task_skills)
        
        if len(required_skills) > 3:
            constraints.append(f"Requires {len(required_skills)} different skill sets")
        
        # EFFORT CONSTRAINTS
        max_effort = max(task.estimated_effort for task in tasks)
        if max_effort > 40:  # More than 1 week
            constraints.append("Contains high-effort tasks requiring dedicated focus")
        
        # DEPENDENCY CONSTRAINTS
        total_dependencies = sum(len(task.dependencies) for task in tasks)
        if total_dependencies > len(tasks) * 2:  # More than 2 deps per task on average
            constraints.append("High dependency complexity may limit parallelization")
        
        return constraints
    
    def _meets_resource_constraints(self, 
                                  opportunity: ParallelOpportunity,
                                  resource_constraints: 'ResourceConstraints') -> bool:
        """Check if opportunity meets resource constraints."""
        # SIMPLIFIED CONSTRAINT CHECKING
        # In a real implementation, this would check against actual resource availability
        
        # CHECK DEVELOPER AVAILABILITY
        if hasattr(resource_constraints, 'max_developers'):
            if opportunity.resource_requirements.developers_needed > resource_constraints.max_developers:
                return False
        
        # CHECK SKILL AVAILABILITY
        if hasattr(resource_constraints, 'available_skills'):
            required_skills = set(opportunity.resource_requirements.skill_requirements)
            available_skills = set(resource_constraints.available_skills)
            if not required_skills.issubset(available_skills):
                return False
        
        # CHECK EFFICIENCY THRESHOLD
        if opportunity.estimated_speedup < self.efficiency_threshold:
            return False
        
        return True
    
    def _create_optimized_parallel_group(self, opportunity: ParallelOpportunity) -> ParallelGroup:
        """Create optimized parallel group from opportunity."""
        # CALCULATE OPTIMAL DURATION
        max_task_effort = max(task.estimated_effort for task in opportunity.tasks)
        estimated_duration = math.ceil(max_task_effort / 8)  # Convert to days
        
        return ParallelGroup(
            group_id=opportunity.opportunity_id,
            tasks=opportunity.tasks,
            estimated_duration=estimated_duration,
            coordination_overhead=opportunity.coordination_overhead,
            resource_requirements=opportunity.resource_requirements.__dict__
        )
    
    def _determine_group_layer(self, group: ParallelGroup, constraint_graph: ConstraintGraph) -> int:
        """Determine dependency layer for parallel group."""
        # FIND MINIMUM LAYER OF ALL TASKS IN GROUP
        min_layer = float('inf')
        
        for task in group.tasks:
            for layer, task_ids in constraint_graph.dependency_layers.items():
                if task.task_id in task_ids:
                    min_layer = min(min_layer, layer)
                    break
        
        return int(min_layer) if min_layer != float('inf') else 0
    
    def _calculate_phase_resource_requirements(self, tasks: List[TaskNode]) -> ResourceRequirements:
        """Calculate resource requirements for execution phase."""
        return self._calculate_opportunity_resource_requirements(tasks)
    
    def _identify_required_tools_for_tasks(self, tasks: List[TaskNode]) -> List[str]:
        """Identify required tools for tasks."""
        tools = set()
        
        for task in tasks:
            task_text = f"{task.task_name} {task.description}".lower()
            
            # DEVELOPMENT TOOLS
            tool_keywords = {
                'git': 'Git',
                'docker': 'Docker',
                'kubernetes': 'Kubernetes',
                'api': 'API Development Tools',
                'test': 'Testing Framework',
                'database': 'Database Tools',
                'ci/cd': 'CI/CD Pipeline'
            }
            
            for keyword, tool in tool_keywords.items():
                if keyword in task_text:
                    tools.add(tool)
        
        return list(tools) if tools else ['Standard Development Environment']
    
    # SYSTEMATIC CALCULATION METHODS
    
    async def _calculate_optimal_resource_allocation(self, 
                                                   execution_phases: List[ExecutionPhase],
                                                   resource_constraints: 'ResourceConstraints') -> ResourceAllocation:
        """Calculate optimal resource allocation."""
        # ANALYZE TOTAL REQUIREMENTS
        total_requirements = self._analyze_total_resource_requirements_from_phases(execution_phases)
        
        # CREATE TEAM ASSIGNMENTS (SIMPLIFIED)
        team_assignments = self._create_basic_team_assignments(execution_phases)
        
        # CALCULATE UTILIZATION
        resource_utilization = min(1.0, total_requirements.estimated_hours / (40 * 8))  # 8 weeks baseline
        
        # IDENTIFY BOTTLENECKS
        bottleneck_resources = self._identify_basic_bottlenecks(total_requirements)
        
        # SCALING RECOMMENDATIONS
        scaling_recommendations = self._generate_basic_scaling_recommendations(total_requirements)
        
        return ResourceAllocation(
            teams=team_assignments,
            resource_utilization=resource_utilization,
            bottleneck_resources=bottleneck_resources,
            scaling_recommendations=scaling_recommendations
        )
    
    def _analyze_total_resource_requirements_from_phases(self, phases: List[ExecutionPhase]) -> ResourceRequirements:
        """Analyze total resource requirements from phases."""
        total_effort = sum(phase.resource_requirements.estimated_hours for phase in phases)
        all_skills = set()
        all_tools = set()
        max_developers = 0
        
        for phase in phases:
            all_skills.update(phase.resource_requirements.skill_requirements)
            all_tools.update(phase.resource_requirements.tools_required)
            max_developers = max(max_developers, phase.resource_requirements.developers_needed)
        
        return ResourceRequirements(
            developers_needed=max_developers,
            skill_requirements=list(all_skills),
            estimated_hours=total_effort,
            tools_required=list(all_tools)
        )
    
    def _create_basic_team_assignments(self, phases: List[ExecutionPhase]) -> List[TeamAssignment]:
        """Create basic team assignments."""
        assignments = []
        
        # CREATE ONE TEAM PER MAJOR SKILL AREA
        skill_teams = defaultdict(list)
        
        for i, phase in enumerate(phases):
            for skill in phase.resource_requirements.skill_requirements:
                skill_teams[skill].append(f"phase_{i}_tasks")
        
        for skill, assigned_tasks in skill_teams.items():
            assignments.append(TeamAssignment(
                team_name=f"{skill.replace(' ', '_').lower()}_team",
                team_members=[f"developer_{skill.split()[0].lower()}"],
                assigned_tasks=assigned_tasks,
                capabilities=[skill],
                availability=0.8  # 80% availability
            ))
        
        return assignments
    
    def _identify_basic_bottlenecks(self, requirements: ResourceRequirements) -> List[str]:
        """Identify basic resource bottlenecks."""
        bottlenecks = []
        
        if requirements.developers_needed > 4:
            bottlenecks.append("High developer count requirement")
        
        if len(requirements.skill_requirements) > 5:
            bottlenecks.append("Diverse skill requirements")
        
        if requirements.estimated_hours > 1000:
            bottlenecks.append("High total effort requirement")
        
        return bottlenecks
    
    def _generate_basic_scaling_recommendations(self, requirements: ResourceRequirements) -> List[str]:
        """Generate basic scaling recommendations."""
        recommendations = []
        
        if requirements.developers_needed > 3:
            recommendations.append("Consider team scaling or task parallelization")
        
        if len(requirements.skill_requirements) > 4:
            recommendations.append("Plan for cross-training or specialist hiring")
        
        if requirements.estimated_hours > 800:
            recommendations.append("Consider scope reduction or timeline extension")
        
        return recommendations
    
    def _identify_systematic_bottlenecks(self, 
                                       phases: List[ExecutionPhase],
                                       resource_allocation: ResourceAllocation) -> List[str]:
        """Identify systematic bottlenecks."""
        bottlenecks = []
        
        # PHASE DURATION BOTTLENECKS
        max_duration = max(phase.estimated_duration for phase in phases) if phases else 0
        avg_duration = sum(phase.estimated_duration for phase in phases) / len(phases) if phases else 0
        
        if max_duration > avg_duration * 2:
            bottlenecks.append(f"Phase duration imbalance: max {max_duration} vs avg {avg_duration:.1f} days")
        
        # RESOURCE UTILIZATION BOTTLENECKS
        if resource_allocation.resource_utilization > 0.9:
            bottlenecks.append("High resource utilization may cause scheduling conflicts")
        
        # SKILL BOTTLENECKS
        skill_counts = defaultdict(int)
        for phase in phases:
            for skill in phase.resource_requirements.skill_requirements:
                skill_counts[skill] += 1
        
        high_demand_skills = [skill for skill, count in skill_counts.items() if count > len(phases) * 0.7]
        if high_demand_skills:
            bottlenecks.append(f"High demand skills: {', '.join(high_demand_skills)}")
        
        return bottlenecks
    
    def _calculate_optimized_timeline(self, phases: List[ExecutionPhase]) -> int:
        """Calculate optimized timeline in weeks."""
        total_days = sum(phase.estimated_duration for phase in phases)
        return max(1, math.ceil(total_days / 5))  # Convert to weeks
    
    def _calculate_maximum_parallelism(self, groups: List[ParallelGroup]) -> int:
        """Calculate maximum concurrent tasks."""
        return max(len(group.tasks) for group in groups) if groups else 1