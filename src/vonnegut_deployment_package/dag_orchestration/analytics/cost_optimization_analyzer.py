"""
Cost Optimization Analyzer - Advanced cost analysis and budget forecasting

This module provides comprehensive cost analysis, optimization recommendations,
and budget forecasting for DAG orchestration operations.
"""

import json
import logging
import statistics
from collections import defaultdict, Counter
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from enum import Enum

from src.rm_ddd.core.unified_reflective_module import ReflectiveModule
from src.dag_orchestration.analytics.execution_pattern_analyzer import ExecutionMetrics


class CostCategory(Enum):
    """Categories of costs in the system."""
    LLM_EXECUTION = "llm_execution"
    COMPUTE_RESOURCES = "compute_resources"
    STORAGE = "storage"
    NETWORK = "network"
    INFRASTRUCTURE = "infrastructure"


class OptimizationStrategy(Enum):
    """Cost optimization strategies."""
    PROVIDER_SELECTION = "provider_selection"
    TASK_BATCHING = "task_batching"
    RESOURCE_RIGHTSIZING = "resource_rightsizing"
    CACHING = "caching"
    SCHEDULING_OPTIMIZATION = "scheduling_optimization"
    WORKLOAD_BALANCING = "workload_balancing"


@dataclass
class CostBreakdown:
    """Detailed cost breakdown by category."""
    category: CostCategory
    total_cost: float
    cost_per_unit: float
    unit_count: int
    percentage_of_total: float
    trend_direction: str  # "increasing", "decreasing", "stable"
    trend_strength: float


@dataclass
class ProviderCostAnalysis:
    """Cost analysis for a specific LLM provider."""
    provider_name: str
    total_cost: float
    average_cost_per_task: float
    task_count: int
    success_rate: float
    cost_efficiency_score: float  # Cost per successful task
    performance_cost_ratio: float  # Performance vs cost trade-off
    usage_percentage: float


@dataclass
class CostOptimizationOpportunity:
    """Identified cost optimization opportunity."""
    strategy: OptimizationStrategy
    potential_savings: float
    savings_percentage: float
    confidence: float
    implementation_effort: str  # LOW, MEDIUM, HIGH
    time_to_implement: str  # IMMEDIATE, DAYS, WEEKS
    affected_components: List[str]
    description: str
    implementation_steps: List[str]
    risks: List[str]
    expected_impact: Dict[str, float]


@dataclass
class BudgetForecast:
    """Budget forecast for future periods."""
    forecast_period_days: int
    predicted_total_cost: float
    confidence_interval: Tuple[float, float]
    cost_breakdown: Dict[CostCategory, float]
    key_assumptions: List[str]
    risk_factors: List[str]
    recommended_budget: float


@dataclass
class CostAlert:
    """Cost-related alert or warning."""
    alert_type: str
    severity: str  # LOW, MEDIUM, HIGH, CRITICAL
    current_value: float
    threshold_value: float
    description: str
    recommended_actions: List[str]
    time_to_threshold: Optional[timedelta]


class CostOptimizationAnalyzer(ReflectiveModule):
    """
    Advanced cost optimization analyzer with budget forecasting.
    
    Provides comprehensive cost analysis, identifies optimization opportunities,
    and generates budget forecasts for DAG orchestration operations.
    """
    
    def __init__(self, budget_limit: Optional[float] = None):
        super().__init__()
        self.budget_limit = budget_limit
        self.execution_history: List[ExecutionMetrics] = []
        self.cost_history: List[Tuple[datetime, float, CostCategory]] = []
        
        # Cost thresholds and targets
        self.thresholds = {
            'cost_spike_threshold': 2.0,  # 2x average cost
            'budget_warning_threshold': 0.8,  # 80% of budget
            'budget_critical_threshold': 0.95,  # 95% of budget
            'efficiency_threshold': 0.7,  # 70% efficiency target
            'savings_opportunity_threshold': 0.1,  # 10% savings minimum
        }
        
        # Provider cost benchmarks (example values - would be updated from real data)
        self.provider_benchmarks = {
            'openai': {'cost_per_1k_tokens': 0.002, 'performance_score': 0.9},
            'anthropic': {'cost_per_1k_tokens': 0.003, 'performance_score': 0.95},
            'local': {'cost_per_1k_tokens': 0.0001, 'performance_score': 0.7},
        }
        
        self.logger = logging.getLogger(__name__)
    
    def add_execution_metrics(self, metrics: List[ExecutionMetrics]) -> None:
        """Add execution metrics for cost analysis."""
        with self.trace_operation("add_execution_metrics"):
            self.execution_history.extend(metrics)
            
            # Extract cost data
            for metric in metrics:
                if metric.cost > 0:
                    self.cost_history.append((
                        metric.timestamp,
                        metric.cost,
                        CostCategory.LLM_EXECUTION  # Primary cost category
                    ))
            
            self.logger.info(
                f"Added {len(metrics)} execution metrics for cost analysis",
                extra={
                    'total_metrics': len(self.execution_history),
                    'cost_entries': len([m for m in metrics if m.cost > 0])
                }
            )
    
    def analyze_cost_breakdown(self, analysis_period_days: int = 30) -> List[CostBreakdown]:
        """
        Analyze cost breakdown by category.
        
        Args:
            analysis_period_days: Days of history to analyze
            
        Returns:
            List of cost breakdowns by category
        """
        with self.trace_operation("analyze_cost_breakdown"):
            cutoff_date = datetime.now() - timedelta(days=analysis_period_days)
            
            # Filter metrics by time period
            recent_metrics = [
                m for m in self.execution_history 
                if m.timestamp >= cutoff_date and m.cost > 0
            ]
            
            if not recent_metrics:
                return []
            
            # Calculate total cost
            total_cost = sum(m.cost for m in recent_metrics)
            
            # Analyze LLM execution costs
            llm_costs = [m.cost for m in recent_metrics]
            llm_total = sum(llm_costs)
            
            # Calculate trend for LLM costs
            trend_direction, trend_strength = self._calculate_cost_trend(llm_costs)
            
            breakdowns = [
                CostBreakdown(
                    category=CostCategory.LLM_EXECUTION,
                    total_cost=llm_total,
                    cost_per_unit=llm_total / len(llm_costs) if llm_costs else 0,
                    unit_count=len(llm_costs),
                    percentage_of_total=(llm_total / total_cost * 100) if total_cost > 0 else 0,
                    trend_direction=trend_direction,
                    trend_strength=trend_strength
                )
            ]
            
            # Add other cost categories (simplified for now)
            # In a real implementation, you'd have actual data for these
            compute_cost = total_cost * 0.1  # Estimate 10% for compute
            storage_cost = total_cost * 0.05  # Estimate 5% for storage
            
            if compute_cost > 0:
                breakdowns.append(CostBreakdown(
                    category=CostCategory.COMPUTE_RESOURCES,
                    total_cost=compute_cost,
                    cost_per_unit=compute_cost / len(recent_metrics),
                    unit_count=len(recent_metrics),
                    percentage_of_total=(compute_cost / total_cost * 100),
                    trend_direction="stable",
                    trend_strength=0.1
                ))
            
            if storage_cost > 0:
                breakdowns.append(CostBreakdown(
                    category=CostCategory.STORAGE,
                    total_cost=storage_cost,
                    cost_per_unit=storage_cost / len(recent_metrics),
                    unit_count=len(recent_metrics),
                    percentage_of_total=(storage_cost / total_cost * 100),
                    trend_direction="stable",
                    trend_strength=0.05
                ))
            
            self.logger.info(
                f"Analyzed cost breakdown for {len(recent_metrics)} metrics",
                extra={
                    'total_cost': total_cost,
                    'categories': len(breakdowns),
                    'analysis_period_days': analysis_period_days
                }
            )
            
            return breakdowns
    
    def analyze_provider_costs(self, analysis_period_days: int = 30) -> List[ProviderCostAnalysis]:
        """
        Analyze costs by LLM provider.
        
        Args:
            analysis_period_days: Days of history to analyze
            
        Returns:
            List of provider cost analyses
        """
        with self.trace_operation("analyze_provider_costs"):
            cutoff_date = datetime.now() - timedelta(days=analysis_period_days)
            
            # Filter metrics by time period
            recent_metrics = [
                m for m in self.execution_history 
                if m.timestamp >= cutoff_date and m.cost > 0 and m.llm_provider
            ]
            
            if not recent_metrics:
                return []
            
            # Group by provider
            provider_metrics = defaultdict(list)
            for metric in recent_metrics:
                provider_metrics[metric.llm_provider].append(metric)
            
            total_cost = sum(m.cost for m in recent_metrics)
            analyses = []
            
            for provider, metrics in provider_metrics.items():
                provider_total_cost = sum(m.cost for m in metrics)
                provider_task_count = len(metrics)
                successful_tasks = sum(1 for m in metrics if m.success)
                success_rate = successful_tasks / provider_task_count if provider_task_count > 0 else 0
                
                # Calculate cost efficiency (cost per successful task)
                cost_efficiency_score = (provider_total_cost / successful_tasks) if successful_tasks > 0 else float('inf')
                
                # Calculate performance-cost ratio
                avg_execution_time = statistics.mean(m.execution_time for m in metrics)
                performance_cost_ratio = avg_execution_time / (provider_total_cost / provider_task_count) if provider_total_cost > 0 else 0
                
                analyses.append(ProviderCostAnalysis(
                    provider_name=provider,
                    total_cost=provider_total_cost,
                    average_cost_per_task=provider_total_cost / provider_task_count,
                    task_count=provider_task_count,
                    success_rate=success_rate,
                    cost_efficiency_score=cost_efficiency_score,
                    performance_cost_ratio=performance_cost_ratio,
                    usage_percentage=(provider_total_cost / total_cost * 100) if total_cost > 0 else 0
                ))
            
            # Sort by total cost descending
            analyses.sort(key=lambda x: x.total_cost, reverse=True)
            
            self.logger.info(
                f"Analyzed costs for {len(analyses)} providers",
                extra={
                    'providers': [a.provider_name for a in analyses],
                    'total_cost': total_cost,
                    'analysis_period_days': analysis_period_days
                }
            )
            
            return analyses
    
    def identify_optimization_opportunities(self, 
                                         analysis_period_days: int = 30) -> List[CostOptimizationOpportunity]:
        """
        Identify cost optimization opportunities.
        
        Args:
            analysis_period_days: Days of history to analyze
            
        Returns:
            List of optimization opportunities
        """
        with self.trace_operation("identify_optimization_opportunities"):
            provider_analyses = self.analyze_provider_costs(analysis_period_days)
            cost_breakdown = self.analyze_cost_breakdown(analysis_period_days)
            
            opportunities = []
            
            # Provider selection optimization
            opportunities.extend(self._identify_provider_optimization(provider_analyses))
            
            # Task batching optimization
            opportunities.extend(self._identify_batching_optimization())
            
            # Resource rightsizing optimization
            opportunities.extend(self._identify_rightsizing_optimization())
            
            # Caching optimization
            opportunities.extend(self._identify_caching_optimization())
            
            # Scheduling optimization
            opportunities.extend(self._identify_scheduling_optimization())
            
            # Filter by minimum savings threshold
            opportunities = [
                opp for opp in opportunities 
                if opp.savings_percentage >= self.thresholds['savings_opportunity_threshold'] * 100
            ]
            
            # Sort by potential savings
            opportunities.sort(key=lambda x: x.potential_savings, reverse=True)
            
            self.logger.info(
                f"Identified {len(opportunities)} cost optimization opportunities",
                extra={
                    'total_potential_savings': sum(opp.potential_savings for opp in opportunities),
                    'high_impact_opportunities': len([opp for opp in opportunities if opp.potential_savings > 100])
                }
            )
            
            return opportunities
    
    def generate_budget_forecast(self, 
                               forecast_days: int = 30,
                               confidence_level: float = 0.95) -> BudgetForecast:
        """
        Generate budget forecast for future period.
        
        Args:
            forecast_days: Days to forecast ahead
            confidence_level: Confidence level for prediction interval
            
        Returns:
            Budget forecast with predictions and recommendations
        """
        with self.trace_operation("generate_budget_forecast"):
            if len(self.execution_history) < 10:
                return BudgetForecast(
                    forecast_period_days=forecast_days,
                    predicted_total_cost=0.0,
                    confidence_interval=(0.0, 0.0),
                    cost_breakdown={},
                    key_assumptions=["Insufficient historical data"],
                    risk_factors=["Prediction based on limited data"],
                    recommended_budget=0.0
                )
            
            # Analyze historical cost trends
            recent_costs = [m.cost for m in self.execution_history if m.cost > 0]
            daily_costs = self._calculate_daily_costs()
            
            # Calculate trend and seasonality
            trend_slope = self._calculate_cost_trend_slope(daily_costs)
            
            # Base prediction on recent average with trend adjustment
            recent_daily_average = statistics.mean(list(daily_costs.values())[-7:]) if len(daily_costs) >= 7 else statistics.mean(list(daily_costs.values()))
            
            # Apply trend to forecast
            predicted_daily_cost = recent_daily_average + (trend_slope * forecast_days / 2)  # Mid-point trend
            predicted_total_cost = predicted_daily_cost * forecast_days
            
            # Calculate confidence interval
            cost_variance = statistics.variance(list(daily_costs.values())) if len(daily_costs) > 1 else 0
            cost_std_dev = cost_variance ** 0.5
            
            # Simple confidence interval (would use more sophisticated methods in practice)
            margin_of_error = 1.96 * cost_std_dev * (forecast_days ** 0.5)  # Rough approximation
            confidence_interval = (
                max(0, predicted_total_cost - margin_of_error),
                predicted_total_cost + margin_of_error
            )
            
            # Forecast cost breakdown by category
            cost_breakdown_analysis = self.analyze_cost_breakdown()
            cost_breakdown = {}
            
            for breakdown in cost_breakdown_analysis:
                category_percentage = breakdown.percentage_of_total / 100
                cost_breakdown[breakdown.category] = predicted_total_cost * category_percentage
            
            # Key assumptions
            key_assumptions = [
                f"Based on {len(daily_costs)} days of historical data",
                f"Assumes current usage patterns continue",
                f"Trend slope: {trend_slope:.6f} per day",
                f"Recent daily average: ${recent_daily_average:.4f}"
            ]
            
            # Risk factors
            risk_factors = []
            if trend_slope > 0.01:
                risk_factors.append("Increasing cost trend detected")
            if cost_variance > recent_daily_average ** 2:
                risk_factors.append("High cost volatility observed")
            if len(daily_costs) < 14:
                risk_factors.append("Limited historical data for prediction")
            
            # Recommended budget (add 20% buffer)
            recommended_budget = confidence_interval[1] * 1.2
            
            forecast = BudgetForecast(
                forecast_period_days=forecast_days,
                predicted_total_cost=predicted_total_cost,
                confidence_interval=confidence_interval,
                cost_breakdown=cost_breakdown,
                key_assumptions=key_assumptions,
                risk_factors=risk_factors,
                recommended_budget=recommended_budget
            )
            
            self.logger.info(
                f"Generated budget forecast for {forecast_days} days",
                extra={
                    'predicted_total_cost': predicted_total_cost,
                    'recommended_budget': recommended_budget,
                    'confidence_interval': confidence_interval
                }
            )
            
            return forecast
    
    def generate_cost_alerts(self) -> List[CostAlert]:
        """
        Generate cost-related alerts and warnings.
        
        Returns:
            List of cost alerts
        """
        with self.trace_operation("generate_cost_alerts"):
            alerts = []
            
            # Budget alerts
            if self.budget_limit:
                current_month_cost = self._calculate_current_month_cost()
                budget_usage = current_month_cost / self.budget_limit
                
                if budget_usage >= self.thresholds['budget_critical_threshold']:
                    alerts.append(CostAlert(
                        alert_type='budget_critical',
                        severity='CRITICAL',
                        current_value=current_month_cost,
                        threshold_value=self.budget_limit * self.thresholds['budget_critical_threshold'],
                        description=f"Budget usage at {budget_usage:.1%} of limit",
                        recommended_actions=[
                            "Implement immediate cost controls",
                            "Review and optimize high-cost tasks",
                            "Consider pausing non-critical operations"
                        ],
                        time_to_threshold=None
                    ))
                elif budget_usage >= self.thresholds['budget_warning_threshold']:
                    alerts.append(CostAlert(
                        alert_type='budget_warning',
                        severity='HIGH',
                        current_value=current_month_cost,
                        threshold_value=self.budget_limit * self.thresholds['budget_warning_threshold'],
                        description=f"Budget usage at {budget_usage:.1%} of limit",
                        recommended_actions=[
                            "Monitor costs closely",
                            "Review optimization opportunities",
                            "Plan cost reduction measures"
                        ],
                        time_to_threshold=None
                    ))
            
            # Cost spike alerts
            recent_costs = [m.cost for m in self.execution_history[-50:] if m.cost > 0]
            if len(recent_costs) >= 10:
                avg_cost = statistics.mean(recent_costs[:-5])  # Exclude last 5 for comparison
                recent_avg = statistics.mean(recent_costs[-5:])  # Last 5 tasks
                
                if recent_avg > avg_cost * self.thresholds['cost_spike_threshold']:
                    alerts.append(CostAlert(
                        alert_type='cost_spike',
                        severity='HIGH',
                        current_value=recent_avg,
                        threshold_value=avg_cost * self.thresholds['cost_spike_threshold'],
                        description=f"Recent cost spike: {recent_avg:.4f} vs average {avg_cost:.4f}",
                        recommended_actions=[
                            "Investigate recent high-cost tasks",
                            "Check for provider pricing changes",
                            "Review task complexity and optimization"
                        ],
                        time_to_threshold=None
                    ))
            
            # Efficiency alerts
            provider_analyses = self.analyze_provider_costs(7)  # Last 7 days
            for analysis in provider_analyses:
                if analysis.success_rate < self.thresholds['efficiency_threshold']:
                    alerts.append(CostAlert(
                        alert_type='low_efficiency',
                        severity='MEDIUM',
                        current_value=analysis.success_rate,
                        threshold_value=self.thresholds['efficiency_threshold'],
                        description=f"Low efficiency for {analysis.provider_name}: {analysis.success_rate:.1%} success rate",
                        recommended_actions=[
                            f"Investigate failures for {analysis.provider_name}",
                            "Improve error handling and retry logic",
                            "Consider alternative providers"
                        ],
                        time_to_threshold=None
                    ))
            
            # Sort by severity
            severity_order = {'CRITICAL': 4, 'HIGH': 3, 'MEDIUM': 2, 'LOW': 1}
            alerts.sort(key=lambda x: severity_order.get(x.severity, 0), reverse=True)
            
            self.logger.info(
                f"Generated {len(alerts)} cost alerts",
                extra={
                    'critical_alerts': len([a for a in alerts if a.severity == 'CRITICAL']),
                    'high_alerts': len([a for a in alerts if a.severity == 'HIGH'])
                }
            )
            
            return alerts
    
    def get_cost_efficiency_metrics(self) -> Dict[str, Any]:
        """
        Calculate comprehensive cost efficiency metrics.
        
        Returns:
            Dictionary of cost efficiency metrics
        """
        with self.trace_operation("get_cost_efficiency_metrics"):
            if not self.execution_history:
                return {}
            
            # Filter metrics with cost data
            cost_metrics = [m for m in self.execution_history if m.cost > 0]
            
            if not cost_metrics:
                return {}
            
            # Basic cost metrics
            total_cost = sum(m.cost for m in cost_metrics)
            average_cost_per_task = total_cost / len(cost_metrics)
            
            # Success-based metrics
            successful_tasks = [m for m in cost_metrics if m.success]
            cost_per_successful_task = total_cost / len(successful_tasks) if successful_tasks else float('inf')
            
            # Time-based metrics
            total_execution_time = sum(m.execution_time for m in cost_metrics)
            cost_per_second = total_cost / total_execution_time if total_execution_time > 0 else 0
            
            # Provider efficiency
            provider_efficiency = {}
            provider_metrics = defaultdict(list)
            
            for metric in cost_metrics:
                if metric.llm_provider:
                    provider_metrics[metric.llm_provider].append(metric)
            
            for provider, metrics in provider_metrics.items():
                provider_total_cost = sum(m.cost for m in metrics)
                provider_successful = sum(1 for m in metrics if m.success)
                provider_efficiency[provider] = {
                    'cost_per_task': provider_total_cost / len(metrics),
                    'cost_per_success': provider_total_cost / provider_successful if provider_successful > 0 else float('inf'),
                    'success_rate': provider_successful / len(metrics)
                }
            
            # Cost trends
            daily_costs = self._calculate_daily_costs()
            cost_trend = self._calculate_cost_trend_slope(daily_costs)
            
            # Efficiency score (lower cost per successful task is better)
            baseline_cost_per_success = 0.01  # Baseline for scoring
            efficiency_score = max(0, 100 - (cost_per_successful_task / baseline_cost_per_success * 100))
            
            metrics = {
                'total_cost': total_cost,
                'average_cost_per_task': average_cost_per_task,
                'cost_per_successful_task': cost_per_successful_task,
                'cost_per_second': cost_per_second,
                'efficiency_score': efficiency_score,
                'cost_trend_per_day': cost_trend,
                'provider_efficiency': provider_efficiency,
                'cost_distribution': {
                    'min_cost': min(m.cost for m in cost_metrics),
                    'max_cost': max(m.cost for m in cost_metrics),
                    'median_cost': statistics.median(m.cost for m in cost_metrics),
                    'cost_variance': statistics.variance(m.cost for m in cost_metrics) if len(cost_metrics) > 1 else 0
                },
                'time_analysis': {
                    'total_tasks': len(cost_metrics),
                    'successful_tasks': len(successful_tasks),
                    'success_rate': len(successful_tasks) / len(cost_metrics),
                    'total_execution_time': total_execution_time
                }
            }
            
            return metrics
    
    def _calculate_cost_trend(self, costs: List[float]) -> Tuple[str, float]:
        """Calculate cost trend direction and strength."""
        if len(costs) < 2:
            return "stable", 0.0
        
        # Simple linear regression slope
        n = len(costs)
        x_values = list(range(n))
        
        x_mean = statistics.mean(x_values)
        y_mean = statistics.mean(costs)
        
        numerator = sum((x - x_mean) * (y - y_mean) for x, y in zip(x_values, costs))
        denominator = sum((x - x_mean) ** 2 for x in x_values)
        
        if denominator == 0:
            return "stable", 0.0
        
        slope = numerator / denominator
        
        # Determine direction and strength
        if abs(slope) < 0.0001:
            return "stable", abs(slope)
        elif slope > 0:
            return "increasing", min(abs(slope) * 1000, 1.0)
        else:
            return "decreasing", min(abs(slope) * 1000, 1.0)
    
    def _calculate_daily_costs(self) -> Dict[str, float]:
        """Calculate daily cost totals."""
        daily_costs = defaultdict(float)
        
        for metric in self.execution_history:
            if metric.cost > 0:
                date_key = metric.timestamp.strftime('%Y-%m-%d')
                daily_costs[date_key] += metric.cost
        
        return dict(daily_costs)
    
    def _calculate_cost_trend_slope(self, daily_costs: Dict[str, float]) -> float:
        """Calculate cost trend slope per day."""
        if len(daily_costs) < 2:
            return 0.0
        
        # Sort by date
        sorted_dates = sorted(daily_costs.keys())
        costs = [daily_costs[date] for date in sorted_dates]
        
        # Simple linear regression
        n = len(costs)
        x_values = list(range(n))
        
        x_mean = statistics.mean(x_values)
        y_mean = statistics.mean(costs)
        
        numerator = sum((x - x_mean) * (y - y_mean) for x, y in zip(x_values, costs))
        denominator = sum((x - x_mean) ** 2 for x in x_values)
        
        return numerator / denominator if denominator != 0 else 0.0
    
    def _calculate_current_month_cost(self) -> float:
        """Calculate total cost for current month."""
        now = datetime.now()
        month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        
        current_month_metrics = [
            m for m in self.execution_history 
            if m.timestamp >= month_start and m.cost > 0
        ]
        
        return sum(m.cost for m in current_month_metrics)
    
    def _identify_provider_optimization(self, 
                                      provider_analyses: List[ProviderCostAnalysis]) -> List[CostOptimizationOpportunity]:
        """Identify provider selection optimization opportunities."""
        opportunities = []
        
        if len(provider_analyses) < 2:
            return opportunities
        
        # Sort by cost efficiency (cost per successful task)
        efficient_providers = sorted(provider_analyses, key=lambda x: x.cost_efficiency_score)
        
        # Compare most efficient vs others
        most_efficient = efficient_providers[0]
        
        for provider in efficient_providers[1:]:
            if provider.cost_efficiency_score > most_efficient.cost_efficiency_score * 1.2:  # 20% worse
                potential_savings = (provider.cost_efficiency_score - most_efficient.cost_efficiency_score) * provider.task_count
                savings_percentage = ((provider.cost_efficiency_score - most_efficient.cost_efficiency_score) / 
                                    provider.cost_efficiency_score * 100)
                
                if potential_savings > 0:
                    opportunities.append(CostOptimizationOpportunity(
                        strategy=OptimizationStrategy.PROVIDER_SELECTION,
                        potential_savings=potential_savings,
                        savings_percentage=savings_percentage,
                        confidence=0.8,
                        implementation_effort="LOW",
                        time_to_implement="IMMEDIATE",
                        affected_components=[provider.provider_name],
                        description=f"Switch from {provider.provider_name} to {most_efficient.provider_name} for better cost efficiency",
                        implementation_steps=[
                            f"Configure task routing to prefer {most_efficient.provider_name}",
                            f"Update provider selection policies",
                            f"Monitor performance impact of provider switch"
                        ],
                        risks=[
                            "Potential performance differences between providers",
                            "Provider availability and rate limits",
                            "Task compatibility with different providers"
                        ],
                        expected_impact={
                            'cost_reduction': savings_percentage,
                            'efficiency_improvement': 20
                        }
                    ))
        
        return opportunities
    
    def _identify_batching_optimization(self) -> List[CostOptimizationOpportunity]:
        """Identify task batching optimization opportunities."""
        opportunities = []
        
        # Analyze task patterns for batching potential
        task_types = defaultdict(list)
        for metric in self.execution_history:
            if metric.cost > 0:
                # Group by task type (simplified - would use more sophisticated grouping)
                task_type = metric.task_id.split('_')[0] if '_' in metric.task_id else metric.task_id
                task_types[task_type].append(metric)
        
        for task_type, metrics in task_types.items():
            if len(metrics) >= 10:  # Enough data for analysis
                avg_cost = statistics.mean(m.cost for m in metrics)
                avg_time = statistics.mean(m.execution_time for m in metrics)
                
                # Estimate batching savings (simplified model)
                if avg_cost > 0.001 and avg_time < 30:  # Small, frequent tasks
                    estimated_batch_size = min(10, len(metrics) // 5)
                    estimated_savings_per_batch = avg_cost * estimated_batch_size * 0.3  # 30% savings
                    total_potential_savings = estimated_savings_per_batch * (len(metrics) // estimated_batch_size)
                    
                    if total_potential_savings > 0.01:  # Minimum threshold
                        opportunities.append(CostOptimizationOpportunity(
                            strategy=OptimizationStrategy.TASK_BATCHING,
                            potential_savings=total_potential_savings,
                            savings_percentage=30.0,
                            confidence=0.6,
                            implementation_effort="MEDIUM",
                            time_to_implement="DAYS",
                            affected_components=[task_type],
                            description=f"Batch {task_type} tasks to reduce per-task overhead",
                            implementation_steps=[
                                f"Implement batching logic for {task_type} tasks",
                                "Configure optimal batch sizes",
                                "Update task scheduling to support batching",
                                "Monitor batch performance and adjust"
                            ],
                            risks=[
                                "Increased latency for individual tasks",
                                "Complexity in error handling for batches",
                                "Potential for batch failures affecting multiple tasks"
                            ],
                            expected_impact={
                                'cost_reduction': 30,
                                'throughput_improvement': 20,
                                'latency_increase': 15
                            }
                        ))
        
        return opportunities
    
    def _identify_rightsizing_optimization(self) -> List[CostOptimizationOpportunity]:
        """Identify resource rightsizing opportunities."""
        opportunities = []
        
        # Analyze resource usage patterns
        resource_metrics = [m for m in self.execution_history if m.cpu_usage > 0 or m.memory_usage > 0]
        
        if len(resource_metrics) >= 20:
            avg_cpu = statistics.mean(m.cpu_usage for m in resource_metrics if m.cpu_usage > 0)
            avg_memory = statistics.mean(m.memory_usage for m in resource_metrics if m.memory_usage > 0)
            
            # Check for over-provisioning
            if avg_cpu < 0.3:  # Less than 30% CPU usage
                estimated_savings = sum(m.cost for m in resource_metrics) * 0.2  # 20% savings
                
                opportunities.append(CostOptimizationOpportunity(
                    strategy=OptimizationStrategy.RESOURCE_RIGHTSIZING,
                    potential_savings=estimated_savings,
                    savings_percentage=20.0,
                    confidence=0.7,
                    implementation_effort="MEDIUM",
                    time_to_implement="DAYS",
                    affected_components=["compute_resources"],
                    description="Reduce compute resources due to low CPU utilization",
                    implementation_steps=[
                        "Analyze detailed resource usage patterns",
                        "Test with reduced resource allocations",
                        "Implement dynamic resource scaling",
                        "Monitor performance impact"
                    ],
                    risks=[
                        "Potential performance degradation during peak loads",
                        "Complexity in dynamic resource management",
                        "Need for careful monitoring and adjustment"
                    ],
                    expected_impact={
                        'cost_reduction': 20,
                        'resource_efficiency': 30
                    }
                ))
            
            if avg_memory < 0.4:  # Less than 40% memory usage
                estimated_savings = sum(m.cost for m in resource_metrics) * 0.15  # 15% savings
                
                opportunities.append(CostOptimizationOpportunity(
                    strategy=OptimizationStrategy.RESOURCE_RIGHTSIZING,
                    potential_savings=estimated_savings,
                    savings_percentage=15.0,
                    confidence=0.7,
                    implementation_effort="MEDIUM",
                    time_to_implement="DAYS",
                    affected_components=["memory_resources"],
                    description="Reduce memory allocation due to low utilization",
                    implementation_steps=[
                        "Analyze memory usage patterns",
                        "Test with reduced memory allocations",
                        "Implement memory-aware scheduling",
                        "Monitor for memory-related issues"
                    ],
                    risks=[
                        "Potential out-of-memory errors",
                        "Performance impact on memory-intensive tasks",
                        "Need for careful capacity planning"
                    ],
                    expected_impact={
                        'cost_reduction': 15,
                        'resource_efficiency': 25
                    }
                ))
        
        return opportunities
    
    def _identify_caching_optimization(self) -> List[CostOptimizationOpportunity]:
        """Identify caching optimization opportunities."""
        opportunities = []
        
        # Analyze for repeated tasks that could benefit from caching
        task_patterns = defaultdict(int)
        task_costs = defaultdict(list)
        
        for metric in self.execution_history:
            if metric.cost > 0:
                # Simplified pattern matching - would use more sophisticated analysis
                pattern = f"{metric.task_id}_{metric.llm_provider}"
                task_patterns[pattern] += 1
                task_costs[pattern].append(metric.cost)
        
        # Find patterns with high repetition
        for pattern, count in task_patterns.items():
            if count >= 5:  # Repeated at least 5 times
                avg_cost = statistics.mean(task_costs[pattern])
                total_cost = sum(task_costs[pattern])
                
                # Estimate caching savings (assume 80% cache hit rate after first execution)
                cache_savings = total_cost * 0.8 * 0.9  # 80% hits, 90% cost reduction per hit
                
                if cache_savings > 0.01:  # Minimum threshold
                    opportunities.append(CostOptimizationOpportunity(
                        strategy=OptimizationStrategy.CACHING,
                        potential_savings=cache_savings,
                        savings_percentage=(cache_savings / total_cost * 100),
                        confidence=0.7,
                        implementation_effort="MEDIUM",
                        time_to_implement="DAYS",
                        affected_components=[pattern.split('_')[0]],
                        description=f"Implement caching for repeated task pattern: {pattern}",
                        implementation_steps=[
                            "Implement result caching system",
                            "Define cache keys and expiration policies",
                            "Update task execution to check cache first",
                            "Monitor cache hit rates and effectiveness"
                        ],
                        risks=[
                            "Stale cache data affecting results",
                            "Cache storage and management overhead",
                            "Complexity in cache invalidation"
                        ],
                        expected_impact={
                            'cost_reduction': (cache_savings / total_cost * 100),
                            'response_time_improvement': 50,
                            'cache_hit_rate': 80
                        }
                    ))
        
        return opportunities
    
    def _identify_scheduling_optimization(self) -> List[CostOptimizationOpportunity]:
        """Identify scheduling optimization opportunities."""
        opportunities = []
        
        # Analyze execution timing patterns
        hourly_costs = defaultdict(list)
        
        for metric in self.execution_history:
            if metric.cost > 0:
                hour = metric.timestamp.hour
                hourly_costs[hour].append(metric.cost)
        
        if len(hourly_costs) >= 12:  # Have data for at least half the day
            # Calculate average cost by hour
            hourly_averages = {hour: statistics.mean(costs) for hour, costs in hourly_costs.items()}
            
            # Find cost variations by time of day
            min_cost_hour = min(hourly_averages, key=hourly_averages.get)
            max_cost_hour = max(hourly_averages, key=hourly_averages.get)
            
            cost_variation = (hourly_averages[max_cost_hour] - hourly_averages[min_cost_hour]) / hourly_averages[max_cost_hour]
            
            if cost_variation > 0.2:  # 20% cost variation
                total_high_cost_executions = sum(len(costs) for hour, costs in hourly_costs.items() 
                                               if hourly_averages.get(hour, 0) > statistics.mean(hourly_averages.values()))
                
                estimated_savings = total_high_cost_executions * (hourly_averages[max_cost_hour] - hourly_averages[min_cost_hour]) * 0.5
                
                if estimated_savings > 0.01:
                    opportunities.append(CostOptimizationOpportunity(
                        strategy=OptimizationStrategy.SCHEDULING_OPTIMIZATION,
                        potential_savings=estimated_savings,
                        savings_percentage=(cost_variation * 50),  # Assume 50% of variation can be captured
                        confidence=0.6,
                        implementation_effort="HIGH",
                        time_to_implement="WEEKS",
                        affected_components=["scheduler"],
                        description=f"Optimize scheduling to prefer low-cost hours (e.g., hour {min_cost_hour})",
                        implementation_steps=[
                            "Analyze detailed cost patterns by time",
                            "Implement time-aware scheduling policies",
                            "Configure task prioritization by cost windows",
                            "Monitor and adjust scheduling effectiveness"
                        ],
                        risks=[
                            "Potential delays for time-sensitive tasks",
                            "Complexity in balancing cost vs. latency",
                            "Provider pricing changes affecting patterns"
                        ],
                        expected_impact={
                            'cost_reduction': (cost_variation * 50),
                            'scheduling_efficiency': 30,
                            'average_latency_increase': 10
                        }
                    ))
        
        return opportunities
    
    def export_cost_analysis_report(self, output_path: Path) -> None:
        """Export comprehensive cost analysis report."""
        with self.trace_operation("export_cost_analysis_report"):
            cost_breakdown = self.analyze_cost_breakdown()
            provider_analyses = self.analyze_provider_costs()
            optimization_opportunities = self.identify_optimization_opportunities()
            budget_forecast = self.generate_budget_forecast()
            cost_alerts = self.generate_cost_alerts()
            efficiency_metrics = self.get_cost_efficiency_metrics()
            
            report = {
                'generated_at': datetime.now().isoformat(),
                'analysis_summary': {
                    'total_executions_analyzed': len(self.execution_history),
                    'executions_with_cost_data': len([m for m in self.execution_history if m.cost > 0]),
                    'analysis_period_days': 30,
                    'budget_limit': self.budget_limit
                },
                'cost_breakdown': [asdict(cb) for cb in cost_breakdown],
                'provider_analysis': [asdict(pa) for pa in provider_analyses],
                'optimization_opportunities': [asdict(opp) for opp in optimization_opportunities],
                'budget_forecast': asdict(budget_forecast),
                'cost_alerts': [asdict(alert) for alert in cost_alerts],
                'efficiency_metrics': efficiency_metrics,
                'summary': {
                    'total_cost': sum(cb.total_cost for cb in cost_breakdown),
                    'optimization_potential': sum(opp.potential_savings for opp in optimization_opportunities),
                    'active_alerts': len(cost_alerts),
                    'critical_alerts': len([a for a in cost_alerts if a.severity == 'CRITICAL']),
                    'efficiency_score': efficiency_metrics.get('efficiency_score', 0),
                    'recommended_budget': budget_forecast.recommended_budget
                }
            }
            
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, 'w') as f:
                json.dump(report, f, indent=2, default=str)
            
            self.logger.info(
                f"Exported cost analysis report to {output_path}",
                extra={'report_size': len(json.dumps(report))}
            )