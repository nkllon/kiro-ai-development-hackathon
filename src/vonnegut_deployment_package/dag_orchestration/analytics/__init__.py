"""
DAG Orchestration Analytics Module

This module provides comprehensive analytics and optimization capabilities
for DAG orchestration systems, including:

- Execution pattern analysis and optimization recommendations
- DAG structure optimization based on execution history
- Resource utilization analysis and capacity planning
- Performance regression detection and anomaly detection
- Cost optimization analysis and budget forecasting
- Unified analytics orchestration and reporting

Key Components:
- ExecutionPatternAnalyzer: Analyzes execution patterns and identifies optimization opportunities
- DAGStructureOptimizer: Optimizes DAG structures based on execution data
- ResourceUtilizationAnalyzer: Monitors resource usage and predicts capacity needs
- PerformanceRegressionDetector: Detects performance degradation and anomalies
- CostOptimizationAnalyzer: Analyzes costs and identifies savings opportunities
- AnalyticsOrchestrator: Coordinates all analytics components for unified insights
"""

from .execution_pattern_analyzer import (
    ExecutionPatternAnalyzer,
    ExecutionMetrics,
    PatternInsight,
    OptimizationRecommendation,
    PatternType
)

from .dag_structure_optimizer import (
    DAGStructureOptimizer,
    DAGNode,
    DAGOptimization,
    OptimizedDAGStructure,
    OptimizationType
)

from .resource_utilization_analyzer import (
    ResourceUtilizationAnalyzer,
    ResourceSnapshot,
    ResourceTrend,
    CapacityPrediction,
    ResourceBottleneck,
    ResourceType,
    UtilizationLevel
)

from .performance_regression_detector import (
    PerformanceRegressionDetector,
    RegressionDetection,
    AnomalyDetection,
    PredictiveAlert,
    PerformanceBaseline,
    RegressionType,
    AnomalyType,
    Severity
)

from .cost_optimization_analyzer import (
    CostOptimizationAnalyzer,
    CostBreakdown,
    ProviderCostAnalysis,
    CostOptimizationOpportunity,
    BudgetForecast,
    CostAlert,
    CostCategory,
    OptimizationStrategy
)

from .analytics_orchestrator import (
    AnalyticsOrchestrator,
    AnalyticsReport,
    ContinuousImprovementAction
)

__all__ = [
    # Main orchestrator
    'AnalyticsOrchestrator',
    'AnalyticsReport',
    'ContinuousImprovementAction',
    
    # Execution pattern analysis
    'ExecutionPatternAnalyzer',
    'ExecutionMetrics',
    'PatternInsight',
    'OptimizationRecommendation',
    'PatternType',
    
    # DAG structure optimization
    'DAGStructureOptimizer',
    'DAGNode',
    'DAGOptimization',
    'OptimizedDAGStructure',
    'OptimizationType',
    
    # Resource utilization analysis
    'ResourceUtilizationAnalyzer',
    'ResourceSnapshot',
    'ResourceTrend',
    'CapacityPrediction',
    'ResourceBottleneck',
    'ResourceType',
    'UtilizationLevel',
    
    # Performance regression detection
    'PerformanceRegressionDetector',
    'RegressionDetection',
    'AnomalyDetection',
    'PredictiveAlert',
    'PerformanceBaseline',
    'RegressionType',
    'AnomalyType',
    'Severity',
    
    # Cost optimization analysis
    'CostOptimizationAnalyzer',
    'CostBreakdown',
    'ProviderCostAnalysis',
    'CostOptimizationOpportunity',
    'BudgetForecast',
    'CostAlert',
    'CostCategory',
    'OptimizationStrategy',
]

# Version information
__version__ = '1.0.0'
__author__ = 'DAG Orchestration Analytics Team'
__description__ = 'Advanced analytics and optimization for DAG orchestration systems'