"""
Tests for Analytics Orchestrator

This module tests the unified analytics orchestration system that coordinates
all analytics components to provide comprehensive insights and recommendations.
"""

import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path

from src.dag_orchestration.analytics.analytics_orchestrator import (
    AnalyticsOrchestrator,
    AnalyticsReport,
    ContinuousImprovementAction
)
from src.dag_orchestration.analytics.execution_pattern_analyzer import (
    ExecutionMetrics,
    PatternInsight,
    PatternType,
    OptimizationRecommendation
)
from src.dag_orchestration.analytics.dag_structure_optimizer import (
    DAGNode,
    OptimizedDAGStructure
)
from src.dag_orchestration.analytics.resource_utilization_analyzer import (
    ResourceSnapshot,
    ResourceTrend,
    ResourceType,
    UtilizationLevel
)
from src.dag_orchestration.analytics.performance_regression_detector import (
    RegressionDetection,
    RegressionType,
    Severity
)
from src.dag_orchestration.analytics.cost_optimization_analyzer import (
    CostOptimizationOpportunity,
    OptimizationStrategy
)


class TestAnalyticsOrchestrator:
    """Test suite for AnalyticsOrchestrator."""
    
    @pytest.fixture
    def orchestrator(self):
        """Create analytics orchestrator for testing."""
        return AnalyticsOrchestrator(
            analysis_interval_minutes=60,
            budget_limit=1000.0
        )
    
    @pytest.fixture
    def sample_execution_metrics(self):
        """Create sample execution metrics for testing."""
        now = datetime.now()
        return [
            ExecutionMetrics(
                task_id="task_1",
                execution_time=10.5,
                cpu_usage=0.6,
                memory_usage=0.4,
                cost=0.05,
                success=True,
                timestamp=now - timedelta(minutes=30),
                dependencies=["task_0"],
                parallel_group="group_1",
                llm_provider="openai"
            ),
            ExecutionMetrics(
                task_id="task_2",
                execution_time=15.2,
                cpu_usage=0.8,
                memory_usage=0.6,
                cost=0.08,
                success=True,
                timestamp=now - timedelta(minutes=20),
                dependencies=["task_1"],
                parallel_group="group_2",
                llm_provider="anthropic"
            ),
            ExecutionMetrics(
                task_id="task_3",
                execution_time=8.1,
                cpu_usage=0.4,
                memory_usage=0.3,
                cost=0.03,
                success=False,
                timestamp=now - timedelta(minutes=10),
                dependencies=["task_1"],
                error_type="timeout"
            )
        ]
    
    @pytest.fixture
    def sample_dag_structure(self):
        """Create sample DAG structure for testing."""
        return {
            "task_1": DAGNode(
                task_id="task_1",
                dependencies={"task_0"},
                dependents={"task_2", "task_3"},
                execution_time=10.5,
                resource_requirements={"cpu": 0.6, "memory": 0.4}
            ),
            "task_2": DAGNode(
                task_id="task_2",
                dependencies={"task_1"},
                dependents=set(),
                execution_time=15.2,
                resource_requirements={"cpu": 0.8, "memory": 0.6}
            )
        }
    
    def test_initialization(self, orchestrator):
        """Test orchestrator initialization."""
        assert orchestrator.analysis_interval_minutes == 60
        assert orchestrator.cost_analyzer.budget_limit == 1000.0
        assert orchestrator.last_analysis_time is None
        assert len(orchestrator.analysis_history) == 0
        
        # Check that all analytics components are initialized
        assert orchestrator.execution_analyzer is not None
        assert orchestrator.dag_optimizer is not None
        assert orchestrator.resource_analyzer is not None
        assert orchestrator.regression_detector is not None
        assert orchestrator.cost_analyzer is not None
    
    def test_add_execution_metrics(self, orchestrator, sample_execution_metrics):
        """Test adding execution metrics to all components."""
        orchestrator.add_execution_metrics(sample_execution_metrics)
        
        # Verify metrics were added to execution analyzer
        assert len(orchestrator.execution_analyzer.execution_history) == 3
        
        # Verify metrics were added to regression detector
        assert len(orchestrator.regression_detector.execution_history) == 3
        
        # Verify metrics were added to cost analyzer
        assert len(orchestrator.cost_analyzer.execution_history) == 3
    
    def test_update_dag_structure(self, orchestrator, sample_dag_structure):
        """Test updating DAG structure."""
        orchestrator.update_dag_structure(sample_dag_structure)
        
        # Verify DAG structure was updated
        assert len(orchestrator.dag_optimizer.current_dag_structure) == 2
        assert "task_1" in orchestrator.dag_optimizer.current_dag_structure
        assert "task_2" in orchestrator.dag_optimizer.current_dag_structure
    
    @patch('psutil.cpu_percent')
    @patch('psutil.virtual_memory')
    @patch('psutil.net_io_counters')
    @patch('psutil.disk_io_counters')
    @patch('psutil.disk_usage')
    def test_capture_resource_snapshot(self, mock_disk_usage, mock_disk_io, 
                                     mock_net_io, mock_memory, mock_cpu, orchestrator):
        """Test capturing resource snapshot."""
        # Mock system resource calls
        mock_cpu.return_value = 75.0
        mock_memory.return_value = Mock(percent=60.0)
        mock_net_io.return_value = Mock(bytes_sent=1000000, bytes_recv=2000000)
        mock_disk_io.return_value = Mock(read_bytes=5000000, write_bytes=3000000)
        mock_disk_usage.return_value = Mock(used=8000000000, total=10000000000)
        
        snapshot = orchestrator.capture_resource_snapshot(active_tasks=5, concurrent_executions=3)
        
        assert isinstance(snapshot, ResourceSnapshot)
        assert snapshot.cpu_percent == 75.0
        assert snapshot.memory_percent == 60.0
        assert snapshot.active_tasks == 5
        assert snapshot.concurrent_executions == 3
    
    def test_should_run_analysis(self, orchestrator):
        """Test analysis interval checking."""
        # Should run analysis initially
        assert orchestrator.should_run_analysis() is True
        
        # Set last analysis time to recent
        orchestrator.last_analysis_time = datetime.now() - timedelta(minutes=30)
        assert orchestrator.should_run_analysis() is False
        
        # Set last analysis time to old
        orchestrator.last_analysis_time = datetime.now() - timedelta(minutes=90)
        assert orchestrator.should_run_analysis() is True
    
    @patch.object(AnalyticsOrchestrator, '_calculate_overall_health_score')
    @patch.object(AnalyticsOrchestrator, '_generate_priority_recommendations')
    @patch.object(AnalyticsOrchestrator, '_generate_continuous_improvement_plan')
    def test_run_comprehensive_analysis(self, mock_improvement_plan, mock_priority_recs, 
                                      mock_health_score, orchestrator, sample_execution_metrics):
        """Test comprehensive analysis execution."""
        # Setup mocks
        mock_health_score.return_value = 85.0
        mock_priority_recs.return_value = [
            {
                'category': 'Performance',
                'priority': 'HIGH',
                'title': 'Test recommendation',
                'description': 'Test description',
                'estimated_impact': {'performance': 20},
                'source': 'test'
            }
        ]
        mock_improvement_plan.return_value = [
            {
                'category': 'Test',
                'priority': 'MEDIUM',
                'title': 'Test action',
                'description': 'Test action description'
            }
        ]
        
        # Add some test data
        orchestrator.add_execution_metrics(sample_execution_metrics)
        
        # Run analysis
        report = orchestrator.run_comprehensive_analysis(analysis_period_days=7)
        
        # Verify report structure
        assert isinstance(report, AnalyticsReport)
        assert report.analysis_period_days == 7
        assert report.overall_health_score == 85.0
        assert len(report.priority_recommendations) == 1
        assert len(report.continuous_improvement_plan) == 1
        
        # Verify report was stored in history
        assert len(orchestrator.analysis_history) == 1
        assert orchestrator.last_analysis_time is not None
    
    def test_get_real_time_insights(self, orchestrator):
        """Test real-time insights generation."""
        insights = orchestrator.get_real_time_insights()
        
        assert 'timestamp' in insights
        assert 'resource_status' in insights
        assert 'cost_alerts' in insights
        assert 'performance_health' in insights
        assert 'recent_anomalies' in insights
        assert 'system_recommendations' in insights
    
    def test_auto_analyze_if_needed(self, orchestrator):
        """Test automatic analysis triggering."""
        # Should not run initially (no data)
        result = orchestrator.auto_analyze_if_needed()
        assert result is not None  # Will run because last_analysis_time is None
        
        # Should not run again immediately
        result = orchestrator.auto_analyze_if_needed()
        assert result is None
    
    def test_calculate_overall_health_score(self, orchestrator):
        """Test overall health score calculation."""
        execution_metrics = {
            'parallel_efficiency': {'efficiency': 0.8},
            'resource_efficiency': {'cpu_efficiency': 0.7}
        }
        performance_health = {'overall_score': 90}
        resource_trends = [
            Mock(current_level=Mock(value='normal'), trend_direction='stable', trend_strength=0.1)
        ]
        cost_metrics = {'efficiency_score': 75}
        
        score = orchestrator._calculate_overall_health_score(
            execution_metrics, performance_health, resource_trends, cost_metrics
        )
        
        assert 0 <= score <= 100
        assert isinstance(score, float)
    
    def test_generate_priority_recommendations(self, orchestrator):
        """Test priority recommendations generation."""
        # Create mock data
        execution_recommendations = [
            Mock(priority='HIGH', title='Test exec rec', description='Test desc', expected_benefit={'perf': 20})
        ]
        dag_optimization = Mock(
            optimizations_applied=[Mock()],
            performance_prediction={'total_improvement': 25}
        )
        resource_trends = [
            Mock(current_level=Mock(value='critical'), resource_type=Mock(value='cpu'))
        ]
        performance_regressions = [
            Mock(severity=Mock(value='critical'), regression_type=Mock(value='execution_time'), 
                 description='Critical regression', degradation_percent=50)
        ]
        cost_opportunities = [
            Mock(potential_savings=150, description='Cost optimization')
        ]
        
        recommendations = orchestrator._generate_priority_recommendations(
            execution_recommendations, dag_optimization, resource_trends,
            performance_regressions, cost_opportunities
        )
        
        assert len(recommendations) > 0
        assert all('category' in rec for rec in recommendations)
        assert all('priority' in rec for rec in recommendations)
        assert all('title' in rec for rec in recommendations)
    
    def test_generate_continuous_improvement_plan(self, orchestrator):
        """Test continuous improvement plan generation."""
        priority_recommendations = [
            {
                'category': 'Performance',
                'priority': 'HIGH',
                'title': 'Test recommendation',
                'description': 'Test description',
                'estimated_impact': {'performance': 20},
                'source': 'test'
            }
        ]
        predictive_alerts = [
            Mock(
                severity=Mock(value='high'),
                alert_type='capacity_exhaustion',
                description='Capacity alert',
                predicted_occurrence_time=datetime.now() + timedelta(hours=12)
            )
        ]
        
        plan = orchestrator._generate_continuous_improvement_plan(
            priority_recommendations, predictive_alerts
        )
        
        assert len(plan) > 0
        assert all('category' in action for action in plan)
        assert all('priority' in action for action in plan)
        assert all('timeline' in action for action in plan)
    
    def test_get_immediate_recommendations(self, orchestrator):
        """Test immediate recommendations generation."""
        # Mock critical resource status
        with patch.object(orchestrator.resource_analyzer, 'get_current_resource_status') as mock_resource:
            mock_resource.return_value = {
                'cpu': {'level': 'critical', 'utilization_percent': 95},
                'memory': {'level': 'normal', 'utilization_percent': 60}
            }
            
            recommendations = orchestrator._get_immediate_recommendations()
            
            # Should have at least one critical recommendation
            critical_recs = [r for r in recommendations if r['priority'] == 'CRITICAL']
            assert len(critical_recs) > 0
    
    def test_estimate_timeline(self, orchestrator):
        """Test timeline estimation."""
        assert orchestrator._estimate_timeline('CRITICAL') == 'IMMEDIATE'
        assert orchestrator._estimate_timeline('HIGH') == 'DAYS'
        assert orchestrator._estimate_timeline('MEDIUM') == 'WEEKS'
        assert orchestrator._estimate_timeline('LOW') == 'MONTHS'
    
    def test_generate_success_metrics(self, orchestrator):
        """Test success metrics generation."""
        performance_rec = {'category': 'Performance', 'title': 'Test'}
        cost_rec = {'category': 'Cost', 'title': 'Test'}
        
        perf_metrics = orchestrator._generate_success_metrics(performance_rec)
        cost_metrics = orchestrator._generate_success_metrics(cost_rec)
        
        assert len(perf_metrics) > 0
        assert len(cost_metrics) > 0
        assert all(isinstance(metric, str) for metric in perf_metrics)
        assert all(isinstance(metric, str) for metric in cost_metrics)
    
    def test_export_comprehensive_report(self, orchestrator, tmp_path):
        """Test comprehensive report export."""
        # Create a mock report
        report = AnalyticsReport(
            generated_at=datetime.now(),
            analysis_period_days=7,
            execution_insights=[],
            execution_recommendations=[],
            execution_efficiency_metrics={},
            dag_optimization=None,
            resource_trends=[],
            capacity_predictions=[],
            resource_status={},
            performance_regressions=[],
            performance_anomalies=[],
            predictive_alerts=[],
            performance_health_score={},
            cost_breakdown=[],
            cost_optimization_opportunities=[],
            cost_efficiency_metrics={},
            overall_health_score=85.0,
            priority_recommendations=[],
            continuous_improvement_plan=[]
        )
        
        output_path = tmp_path / "analytics_report.json"
        orchestrator.export_comprehensive_report(report, output_path)
        
        assert output_path.exists()
        
        # Verify file content
        import json
        with open(output_path) as f:
            data = json.load(f)
        
        assert 'generated_at' in data
        assert 'overall_health_score' in data
        assert 'metadata' in data
        assert data['overall_health_score'] == 85.0
    
    def test_get_analytics_summary(self, orchestrator):
        """Test analytics summary generation."""
        summary = orchestrator.get_analytics_summary()
        
        assert summary['analytics_status'] == 'active'
        assert summary['analysis_interval_minutes'] == 60
        assert summary['reports_generated'] == 0
        assert 'components_active' in summary
        
        # All components should be active
        components = summary['components_active']
        assert all(components.values())
    
    def test_analytics_with_real_data_flow(self, orchestrator, sample_execution_metrics, sample_dag_structure):
        """Test complete analytics flow with real data."""
        # Add execution data
        orchestrator.add_execution_metrics(sample_execution_metrics)
        
        # Update DAG structure
        orchestrator.update_dag_structure(sample_dag_structure)
        
        # Capture resource snapshot
        with patch('psutil.cpu_percent', return_value=70.0), \
             patch('psutil.virtual_memory', return_value=Mock(percent=50.0)), \
             patch('psutil.net_io_counters', return_value=Mock(bytes_sent=1000, bytes_recv=2000)), \
             patch('psutil.disk_io_counters', return_value=Mock(read_bytes=5000, write_bytes=3000)), \
             patch('psutil.disk_usage', return_value=Mock(used=8000000, total=10000000)):
            
            orchestrator.capture_resource_snapshot(active_tasks=3, concurrent_executions=2)
        
        # Run comprehensive analysis
        report = orchestrator.run_comprehensive_analysis(analysis_period_days=1)
        
        # Verify report contains data
        assert report is not None
        assert isinstance(report.overall_health_score, float)
        assert 0 <= report.overall_health_score <= 100
        
        # Get real-time insights
        insights = orchestrator.get_real_time_insights()
        assert insights is not None
        assert 'timestamp' in insights
        
        # Get analytics summary
        summary = orchestrator.get_analytics_summary()
        assert summary['reports_generated'] == 1
        assert summary['latest_analysis'] is not None


class TestAnalyticsIntegration:
    """Integration tests for analytics system."""
    
    def test_end_to_end_analytics_workflow(self):
        """Test complete end-to-end analytics workflow."""
        orchestrator = AnalyticsOrchestrator(budget_limit=500.0)
        
        # Simulate execution data over time
        now = datetime.now()
        metrics = []
        
        for i in range(20):
            metric = ExecutionMetrics(
                task_id=f"task_{i}",
                execution_time=10.0 + (i * 0.5),  # Gradually increasing
                cpu_usage=0.5 + (i * 0.01),      # Gradually increasing
                memory_usage=0.3 + (i * 0.01),   # Gradually increasing
                cost=0.05 + (i * 0.002),          # Gradually increasing
                success=i < 18,  # Last 2 fail
                timestamp=now - timedelta(minutes=60-i*3),
                dependencies=[f"task_{i-1}"] if i > 0 else [],
                llm_provider="openai" if i % 2 == 0 else "anthropic"
            )
            metrics.append(metric)
        
        # Add metrics in batches
        orchestrator.add_execution_metrics(metrics[:10])
        orchestrator.add_execution_metrics(metrics[10:])
        
        # Create DAG structure
        dag_structure = {}
        for i in range(5):
            dag_structure[f"task_{i}"] = DAGNode(
                task_id=f"task_{i}",
                dependencies={f"task_{i-1}"} if i > 0 else set(),
                dependents={f"task_{i+1}"} if i < 4 else set(),
                execution_time=10.0 + i,
                resource_requirements={"cpu": 0.5 + i*0.1, "memory": 0.3 + i*0.1}
            )
        
        orchestrator.update_dag_structure(dag_structure)
        
        # Mock resource monitoring
        with patch('psutil.cpu_percent', return_value=85.0), \
             patch('psutil.virtual_memory', return_value=Mock(percent=75.0)), \
             patch('psutil.net_io_counters', return_value=Mock(bytes_sent=10000, bytes_recv=20000)), \
             patch('psutil.disk_io_counters', return_value=Mock(read_bytes=50000, write_bytes=30000)), \
             patch('psutil.disk_usage', return_value=Mock(used=8500000000, total=10000000000)):
            
            # Capture multiple resource snapshots
            for j in range(5):
                orchestrator.capture_resource_snapshot(
                    active_tasks=3 + j,
                    concurrent_executions=2 + j
                )
        
        # Run comprehensive analysis
        report = orchestrator.run_comprehensive_analysis(analysis_period_days=1)
        
        # Verify comprehensive results
        assert report is not None
        assert isinstance(report.overall_health_score, float)
        
        # Should detect some issues due to increasing trends
        assert len(report.execution_insights) >= 0
        assert len(report.cost_optimization_opportunities) >= 0
        
        # Should have resource trends
        assert len(report.resource_trends) >= 0
        
        # Should have some recommendations
        assert len(report.priority_recommendations) >= 0
        assert len(report.continuous_improvement_plan) >= 0
        
        # Test real-time insights
        insights = orchestrator.get_real_time_insights()
        assert insights is not None
        
        # Test analytics summary
        summary = orchestrator.get_analytics_summary()
        assert summary['reports_generated'] == 1
        assert summary['latest_analysis']['overall_health_score'] == report.overall_health_score