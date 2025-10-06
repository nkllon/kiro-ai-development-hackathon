#!/usr/bin/env python3
"""
Cost Optimizer for DAG Orchestration
====================================

Cost analysis and optimization system with budget forecasting
and cost optimization recommendations.

Author: Beast Mode Framework
Date: 2025-01-27
Version: 1.0
"""

import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import statistics
import uuid

from src.rm_ddd.core.unified_reflective_module import ReflectiveModule


class CostCategory(Enum):
    """Categories of costs."""
    LLM_USAGE = "llm_usage"
    COMPUTE_RESOURCES = "compute_resources"
    STORAGE = "storage"
    NETWORK = "network"
    INFRASTRUCTURE = "infrastructure"


@dataclass
class CostAnalysisReport:
    """Report of cost analysis."""
    report_id: str
    analysis_period: Dict[str, datetime]
    total_cost: float
    cost_breakdown: Dict[str, float]
    cost_trends: Dict[str, List[float]]
    cost_per_execution: float
    cost_efficiency_score: float
    generated_at: datetime = field(default_factory=datetime.now)


@dataclass
class BudgetForecast:
    """Budget forecast based on historical data."""
    forecast_id: str
    forecast_period: Dict[str, datetime]
    predicted_cost: float
    confidence_interval: Tuple[float, float]
    cost_drivers: List[str]
    risk_factors: List[str]
    generated_at: datetime = field(default_factory=datetime.now)


@dataclass
class CostOptimizationRecommendation:
    """Cost optimization recommendation."""
    recommendation_id: str
    title: str
    description: str
    category: CostCategory
    potential_savings: float
    implementation_effort: str
    confidence: float
    priority: int
    implementation_steps: List[str] = field(default_factory=list)


class CostOptimizer(ReflectiveModule):
    """
    Cost optimizer for DAG orchestration system.
    
    Features:
    - Cost analysis and reporting
    - Budget forecasting
    - Cost optimization recommendations
    - Cost trend analysis
    """
    
    def __init__(self):
        super().__init__()
        self.module_id = "CostOptimizer"
        self._logger = logging.getLogger(f"dag_orchestration.{self.__class__.__name__}")
        
        # Cost tracking
        self._cost_history: List[Dict[str, Any]] = []
        self._budget_forecasts: List[BudgetForecast] = []
        self._optimization_recommendations: List[CostOptimizationRecommendation] = []
        
        # Configuration
        self._cost_categories = {
            CostCategory.LLM_USAGE: 0.0,
            CostCategory.COMPUTE_RESOURCES: 0.0,
            CostCategory.STORAGE: 0.0,
            CostCategory.NETWORK: 0.0,
            CostCategory.INFRASTRUCTURE: 0.0
        }
        
        # Statistics
        self._total_cost_tracked = 0.0
        self._total_analyses = 0
        self._recommendations_generated = 0
        
        self._logger.info("CostOptimizer initialized")
    
    def record_cost(self, cost_data: Dict[str, Any]) -> None:
        """Record cost data for analysis."""
        cost_record = {
            'timestamp': datetime.now(),
            'execution_id': cost_data.get('execution_id', str(uuid.uuid4())),
            'total_cost': cost_data.get('total_cost', 0.0),
            'llm_cost': cost_data.get('llm_cost', 0.0),
            'compute_cost': cost_data.get('compute_cost', 0.0),
            'storage_cost': cost_data.get('storage_cost', 0.0),
            'network_cost': cost_data.get('network_cost', 0.0),
            'infrastructure_cost': cost_data.get('infrastructure_cost', 0.0),
            'task_count': cost_data.get('task_count', 0),
            'execution_duration': cost_data.get('execution_duration', 0.0),
            'llm_provider': cost_data.get('llm_provider', 'unknown'),
            'execution_strategy': cost_data.get('execution_strategy', 'unknown'),
            'metadata': cost_data.get('metadata', {})
        }
        
        self._cost_history.append(cost_record)
        self._total_cost_tracked += cost_record['total_cost']
        
        # Keep only recent history (last 1000 records)
        if len(self._cost_history) > 1000:
            self._cost_history = self._cost_history[-1000:]
        
        self._logger.debug(f"Recorded cost ${cost_record['total_cost']:.2f} for execution {cost_record['execution_id']}")
    
    async def analyze_costs(self, analysis_period_days: int = 30) -> CostAnalysisReport:
        """Analyze costs over specified period."""
        with self.trace_operation("analyze_costs", 
                                analysis_period_days=analysis_period_days) as trace:
            
            report_id = str(uuid.uuid4())
            end_date = datetime.now()
            start_date = end_date - timedelta(days=analysis_period_days)
            
            # Filter cost data by period
            period_costs = [
                record for record in self._cost_history
                if start_date <= record['timestamp'] <= end_date
            ]
            
            if not period_costs:
                self._logger.warning("No cost data available for analysis period")
                return CostAnalysisReport(
                    report_id=report_id,
                    analysis_period={'start': start_date, 'end': end_date},
                    total_cost=0.0,
                    cost_breakdown={},
                    cost_trends={},
                    cost_per_execution=0.0,
                    cost_efficiency_score=0.0
                )
            
            # Calculate total cost
            total_cost = sum(record['total_cost'] for record in period_costs)
            
            # Calculate cost breakdown by category
            cost_breakdown = {
                'llm_usage': sum(record['llm_cost'] for record in period_costs),
                'compute_resources': sum(record['compute_cost'] for record in period_costs),
                'storage': sum(record['storage_cost'] for record in period_costs),
                'network': sum(record['network_cost'] for record in period_costs),
                'infrastructure': sum(record['infrastructure_cost'] for record in period_costs)
            }
            
            # Calculate cost trends (daily costs)
            cost_trends = self._calculate_cost_trends(period_costs, analysis_period_days)
            
            # Calculate cost per execution
            cost_per_execution = total_cost / len(period_costs) if period_costs else 0.0
            
            # Calculate cost efficiency score
            cost_efficiency_score = self._calculate_cost_efficiency(period_costs)
            
            report = CostAnalysisReport(
                report_id=report_id,
                analysis_period={'start': start_date, 'end': end_date},
                total_cost=total_cost,
                cost_breakdown=cost_breakdown,
                cost_trends=cost_trends,
                cost_per_execution=cost_per_execution,
                cost_efficiency_score=cost_efficiency_score
            )
            
            self._total_analyses += 1
            
            trace.output_result = {
                'report_id': report_id,
                'total_cost': total_cost,
                'cost_per_execution': cost_per_execution,
                'efficiency_score': cost_efficiency_score,
                'records_analyzed': len(period_costs)
            }
            
            self._logger.info(f"Cost analysis {report_id} completed: ${total_cost:.2f} total cost")
            return report
    
    async def forecast_budget(self, forecast_period_days: int = 30) -> BudgetForecast:
        """Forecast budget requirements based on historical data."""
        with self.trace_operation("forecast_budget", 
                                forecast_period_days=forecast_period_days) as trace:
            
            forecast_id = str(uuid.uuid4())
            start_date = datetime.now()
            end_date = start_date + timedelta(days=forecast_period_days)
            
            if len(self._cost_history) < 7:  # Need at least a week of data
                self._logger.warning("Insufficient historical data for budget forecasting")
                return BudgetForecast(
                    forecast_id=forecast_id,
                    forecast_period={'start': start_date, 'end': end_date},
                    predicted_cost=0.0,
                    confidence_interval=(0.0, 0.0),
                    cost_drivers=[],
                    risk_factors=["Insufficient historical data"]
                )
            
            # Use recent data for forecasting
            recent_data = self._cost_history[-30:]  # Last 30 records
            
            # Calculate daily average cost
            daily_costs = self._group_costs_by_day(recent_data)
            if not daily_costs:
                predicted_daily_cost = 0.0
            else:
                predicted_daily_cost = statistics.mean(daily_costs)
            
            # Predict total cost for forecast period
            predicted_cost = predicted_daily_cost * forecast_period_days
            
            # Calculate confidence interval (simple approach using standard deviation)
            if len(daily_costs) > 1:
                std_dev = statistics.stdev(daily_costs)
                confidence_interval = (
                    max(0, predicted_cost - 1.96 * std_dev * (forecast_period_days ** 0.5)),
                    predicted_cost + 1.96 * std_dev * (forecast_period_days ** 0.5)
                )
            else:
                confidence_interval = (predicted_cost * 0.8, predicted_cost * 1.2)
            
            # Identify cost drivers
            cost_drivers = self._identify_cost_drivers(recent_data)
            
            # Identify risk factors
            risk_factors = self._identify_risk_factors(recent_data)
            
            forecast = BudgetForecast(
                forecast_id=forecast_id,
                forecast_period={'start': start_date, 'end': end_date},
                predicted_cost=predicted_cost,
                confidence_interval=confidence_interval,
                cost_drivers=cost_drivers,
                risk_factors=risk_factors
            )
            
            self._budget_forecasts.append(forecast)
            
            # Keep only recent forecasts
            if len(self._budget_forecasts) > 20:
                self._budget_forecasts = self._budget_forecasts[-20:]
            
            trace.output_result = {
                'forecast_id': forecast_id,
                'predicted_cost': predicted_cost,
                'confidence_interval': confidence_interval,
                'cost_drivers_count': len(cost_drivers),
                'risk_factors_count': len(risk_factors)
            }
            
            self._logger.info(f"Budget forecast {forecast_id} completed: ${predicted_cost:.2f} predicted")
            return forecast
    
    async def generate_optimization_recommendations(self) -> List[CostOptimizationRecommendation]:
        """Generate cost optimization recommendations."""
        with self.trace_operation("generate_optimization_recommendations") as trace:
            
            recommendations = []
            
            if not self._cost_history:
                return recommendations
            
            recent_data = self._cost_history[-50:]  # Last 50 records
            
            # Analyze LLM cost optimization opportunities
            llm_recommendations = self._analyze_llm_cost_optimization(recent_data)
            recommendations.extend(llm_recommendations)
            
            # Analyze compute resource optimization
            compute_recommendations = self._analyze_compute_cost_optimization(recent_data)
            recommendations.extend(compute_recommendations)
            
            # Analyze execution strategy optimization
            strategy_recommendations = self._analyze_strategy_cost_optimization(recent_data)
            recommendations.extend(strategy_recommendations)
            
            # Sort by potential savings
            recommendations.sort(key=lambda r: r.potential_savings, reverse=True)
            
            # Store recommendations
            self._optimization_recommendations.extend(recommendations)
            self._recommendations_generated += len(recommendations)
            
            # Keep only recent recommendations
            if len(self._optimization_recommendations) > 100:
                self._optimization_recommendations = self._optimization_recommendations[-100:]
            
            trace.output_result = {
                'recommendations_generated': len(recommendations),
                'total_potential_savings': sum(r.potential_savings for r in recommendations)
            }
            
            self._logger.info(f"Generated {len(recommendations)} cost optimization recommendations")
            return recommendations
    
    def _calculate_cost_trends(self, cost_data: List[Dict[str, Any]], period_days: int) -> Dict[str, List[float]]:
        """Calculate cost trends over the analysis period."""
        # Group costs by day
        daily_costs = {}
        
        for record in cost_data:
            date_key = record['timestamp'].date()
            if date_key not in daily_costs:
                daily_costs[date_key] = {
                    'total': 0.0,
                    'llm': 0.0,
                    'compute': 0.0,
                    'storage': 0.0,
                    'network': 0.0,
                    'infrastructure': 0.0
                }
            
            daily_costs[date_key]['total'] += record['total_cost']
            daily_costs[date_key]['llm'] += record['llm_cost']
            daily_costs[date_key]['compute'] += record['compute_cost']
            daily_costs[date_key]['storage'] += record['storage_cost']
            daily_costs[date_key]['network'] += record['network_cost']
            daily_costs[date_key]['infrastructure'] += record['infrastructure_cost']
        
        # Convert to trend lists
        sorted_dates = sorted(daily_costs.keys())
        
        trends = {
            'total_cost': [daily_costs[date]['total'] for date in sorted_dates],
            'llm_cost': [daily_costs[date]['llm'] for date in sorted_dates],
            'compute_cost': [daily_costs[date]['compute'] for date in sorted_dates],
            'storage_cost': [daily_costs[date]['storage'] for date in sorted_dates],
            'network_cost': [daily_costs[date]['network'] for date in sorted_dates],
            'infrastructure_cost': [daily_costs[date]['infrastructure'] for date in sorted_dates]
        }
        
        return trends
    
    def _calculate_cost_efficiency(self, cost_data: List[Dict[str, Any]]) -> float:
        """Calculate cost efficiency score (0.0 to 1.0)."""
        if not cost_data:
            return 0.0
        
        # Simple efficiency calculation based on cost per task and execution time
        total_cost = sum(record['total_cost'] for record in cost_data)
        total_tasks = sum(record['task_count'] for record in cost_data)
        total_time = sum(record['execution_duration'] for record in cost_data)
        
        if total_tasks == 0 or total_time == 0:
            return 0.0
        
        # Cost per task per minute (lower is better)
        cost_per_task_per_minute = (total_cost / total_tasks) / (total_time / 60)
        
        # Normalize to 0-1 scale (assuming $1 per task per minute is very inefficient)
        efficiency_score = max(0.0, 1.0 - min(cost_per_task_per_minute, 1.0))
        
        return efficiency_score
    
    def _group_costs_by_day(self, cost_data: List[Dict[str, Any]]) -> List[float]:
        """Group costs by day and return daily totals."""
        daily_costs = {}
        
        for record in cost_data:
            date_key = record['timestamp'].date()
            if date_key not in daily_costs:
                daily_costs[date_key] = 0.0
            daily_costs[date_key] += record['total_cost']
        
        return list(daily_costs.values())
    
    def _identify_cost_drivers(self, cost_data: List[Dict[str, Any]]) -> List[str]:
        """Identify main cost drivers."""
        drivers = []
        
        # Calculate category totals
        category_totals = {
            'LLM Usage': sum(record['llm_cost'] for record in cost_data),
            'Compute Resources': sum(record['compute_cost'] for record in cost_data),
            'Storage': sum(record['storage_cost'] for record in cost_data),
            'Network': sum(record['network_cost'] for record in cost_data),
            'Infrastructure': sum(record['infrastructure_cost'] for record in cost_data)
        }
        
        total_cost = sum(category_totals.values())
        
        # Identify categories that represent >20% of total cost
        for category, cost in category_totals.items():
            if cost > total_cost * 0.2:
                percentage = (cost / total_cost) * 100
                drivers.append(f"{category} ({percentage:.1f}% of total cost)")
        
        return drivers
    
    def _identify_risk_factors(self, cost_data: List[Dict[str, Any]]) -> List[str]:
        """Identify cost risk factors."""
        risk_factors = []
        
        if not cost_data:
            return risk_factors
        
        # Check for cost volatility
        daily_costs = self._group_costs_by_day(cost_data)
        if len(daily_costs) > 1:
            avg_daily_cost = statistics.mean(daily_costs)
            std_dev = statistics.stdev(daily_costs)
            
            if std_dev > avg_daily_cost * 0.5:  # High volatility
                risk_factors.append("High cost volatility detected")
        
        # Check for increasing cost trend
        if len(daily_costs) >= 7:
            recent_avg = statistics.mean(daily_costs[-3:])  # Last 3 days
            older_avg = statistics.mean(daily_costs[:3])    # First 3 days
            
            if recent_avg > older_avg * 1.2:  # 20% increase
                risk_factors.append("Increasing cost trend detected")
        
        # Check for high LLM costs
        total_cost = sum(record['total_cost'] for record in cost_data)
        llm_cost = sum(record['llm_cost'] for record in cost_data)
        
        if llm_cost > total_cost * 0.7:  # LLM costs >70% of total
            risk_factors.append("High dependency on LLM costs")
        
        return risk_factors
    
    def _analyze_llm_cost_optimization(self, cost_data: List[Dict[str, Any]]) -> List[CostOptimizationRecommendation]:
        """Analyze LLM cost optimization opportunities."""
        recommendations = []
        
        # Calculate LLM cost statistics
        llm_costs = [record['llm_cost'] for record in cost_data if record['llm_cost'] > 0]
        
        if not llm_costs:
            return recommendations
        
        total_llm_cost = sum(llm_costs)
        avg_llm_cost = statistics.mean(llm_costs)
        
        # Check if LLM costs are high
        total_cost = sum(record['total_cost'] for record in cost_data)
        llm_percentage = (total_llm_cost / total_cost) * 100 if total_cost > 0 else 0
        
        if llm_percentage > 60:  # LLM costs >60% of total
            recommendation = CostOptimizationRecommendation(
                recommendation_id=str(uuid.uuid4()),
                title="Optimize LLM usage and selection",
                description=f"LLM costs represent {llm_percentage:.1f}% of total costs (${total_llm_cost:.2f})",
                category=CostCategory.LLM_USAGE,
                potential_savings=total_llm_cost * 0.3,  # Assume 30% savings possible
                implementation_effort="medium",
                confidence=0.8,
                priority=9,
                implementation_steps=[
                    "Review LLM selection policies to prefer cost-effective models",
                    "Implement intelligent task batching to reduce LLM calls",
                    "Consider using cost-first execution strategies",
                    "Optimize prompts to reduce token usage"
                ]
            )
            recommendations.append(recommendation)
        
        return recommendations
    
    def _analyze_compute_cost_optimization(self, cost_data: List[Dict[str, Any]]) -> List[CostOptimizationRecommendation]:
        """Analyze compute cost optimization opportunities."""
        recommendations = []
        
        # Calculate compute cost statistics
        compute_costs = [record['compute_cost'] for record in cost_data if record['compute_cost'] > 0]
        
        if not compute_costs:
            return recommendations
        
        total_compute_cost = sum(compute_costs)
        
        # Check for high compute costs
        total_cost = sum(record['total_cost'] for record in cost_data)
        compute_percentage = (total_compute_cost / total_cost) * 100 if total_cost > 0 else 0
        
        if compute_percentage > 40:  # Compute costs >40% of total
            recommendation = CostOptimizationRecommendation(
                recommendation_id=str(uuid.uuid4()),
                title="Optimize compute resource usage",
                description=f"Compute costs represent {compute_percentage:.1f}% of total costs (${total_compute_cost:.2f})",
                category=CostCategory.COMPUTE_RESOURCES,
                potential_savings=total_compute_cost * 0.2,  # Assume 20% savings possible
                implementation_effort="medium",
                confidence=0.7,
                priority=7,
                implementation_steps=[
                    "Review resource allocation per task",
                    "Implement dynamic resource scaling",
                    "Optimize task scheduling for resource efficiency",
                    "Consider using spot instances or reserved capacity"
                ]
            )
            recommendations.append(recommendation)
        
        return recommendations
    
    def _analyze_strategy_cost_optimization(self, cost_data: List[Dict[str, Any]]) -> List[CostOptimizationRecommendation]:
        """Analyze execution strategy cost optimization opportunities."""
        recommendations = []
        
        # Analyze cost by execution strategy
        strategy_costs = {}
        for record in cost_data:
            strategy = record['execution_strategy']
            if strategy not in strategy_costs:
                strategy_costs[strategy] = []
            strategy_costs[strategy].append(record['total_cost'])
        
        if len(strategy_costs) > 1:
            # Find most and least cost-effective strategies
            strategy_averages = {
                strategy: statistics.mean(costs)
                for strategy, costs in strategy_costs.items()
                if len(costs) >= 3  # Need minimum data points
            }
            
            if len(strategy_averages) > 1:
                best_strategy = min(strategy_averages, key=strategy_averages.get)
                worst_strategy = max(strategy_averages, key=strategy_averages.get)
                
                if strategy_averages[worst_strategy] > strategy_averages[best_strategy] * 1.5:
                    potential_savings = (strategy_averages[worst_strategy] - strategy_averages[best_strategy]) * len(strategy_costs[worst_strategy])
                    
                    recommendation = CostOptimizationRecommendation(
                        recommendation_id=str(uuid.uuid4()),
                        title=f"Switch from {worst_strategy} to {best_strategy} execution strategy",
                        description=f"{worst_strategy} strategy costs ${strategy_averages[worst_strategy]:.2f} vs ${strategy_averages[best_strategy]:.2f} for {best_strategy}",
                        category=CostCategory.COMPUTE_RESOURCES,
                        potential_savings=potential_savings,
                        implementation_effort="low",
                        confidence=0.8,
                        priority=8,
                        implementation_steps=[
                            f"Update default execution strategy to {best_strategy}",
                            "Monitor performance impact of strategy change",
                            "Adjust strategy selection based on task characteristics"
                        ]
                    )
                    recommendations.append(recommendation)
        
        return recommendations
    
    def get_cost_statistics(self) -> Dict[str, Any]:
        """Get cost tracking statistics."""
        return {
            'total_cost_tracked': self._total_cost_tracked,
            'total_analyses': self._total_analyses,
            'recommendations_generated': self._recommendations_generated,
            'cost_records_count': len(self._cost_history),
            'budget_forecasts_count': len(self._budget_forecasts),
            'active_recommendations': len(self._optimization_recommendations)
        }


# Convenience functions
def create_cost_optimizer() -> CostOptimizer:
    """Factory function to create cost optimizer."""
    return CostOptimizer()