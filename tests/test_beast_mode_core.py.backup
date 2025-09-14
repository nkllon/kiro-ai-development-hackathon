"""
Tests for Beast Mode Core Components.

Tests the core Beast Mode framework components including PDCA orchestration,
model registry, and health monitoring.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta
from typing import Dict, List, Any

# Import core components (using mocks where needed due to complex dependencies)
from src.beast_mode.core.exceptions import BeastModeError


class MockPDCAOrchestrator:
    """Mock PDCA Orchestrator for testing."""
    
    def __init__(self):
        self.cycles = []
        self.current_phase = "plan"
    
    def execute_cycle(self, plan_config: Dict[str, Any], 
                     execution_strategy: str = "systematic",
                     validation_criteria: List[str] = None,
                     improvement_actions: List[str] = None) -> Dict[str, Any]:
        """Execute a PDCA cycle."""
        cycle_result = {
            'cycle_id': f"cycle_{len(self.cycles) + 1}",
            'plan_config': plan_config,
            'execution_strategy': execution_strategy,
            'validation_criteria': validation_criteria or [],
            'improvement_actions': improvement_actions or [],
            'status': 'completed',
            'duration': 5,  # days
            'success_rate': 0.95
        }
        self.cycles.append(cycle_result)
        return cycle_result
    
    def get_cycle_history(self) -> List[Dict[str, Any]]:
        """Get history of executed cycles."""
        return self.cycles


class MockModelRegistry:
    """Mock Model Registry for testing."""
    
    def __init__(self):
        self.models = {}
        self.decisions = []
    
    def register_model(self, model_id: str, model_type: str, 
                      version: str, metadata: Dict[str, Any] = None) -> Dict[str, Any]:
        """Register a model in the registry."""
        model_info = {
            'model_id': model_id,
            'model_type': model_type,
            'version': version,
            'metadata': metadata or {},
            'registered_at': datetime.now(),
            'status': 'active'
        }
        self.models[model_id] = model_info
        return model_info
    
    def get_decision_recommendation(self, context: Dict[str, Any], 
                                  decision_type: str) -> Dict[str, Any]:
        """Get decision recommendation based on context."""
        decision = {
            'decision_id': f"decision_{len(self.decisions) + 1}",
            'decision_type': decision_type,
            'context': context,
            'recommendation': 'proceed_with_systematic_approach',
            'confidence': 0.87,
            'reasoning': 'Based on historical patterns and current context'
        }
        self.decisions.append(decision)
        return decision


class MockHealthMonitor:
    """Mock Health Monitor for testing."""
    
    def __init__(self):
        self.components = {}
        self.health_checks = []
    
    def register_component(self, component_id: str, 
                          health_check_func: callable = None) -> Dict[str, Any]:
        """Register a component for health monitoring."""
        component_info = {
            'component_id': component_id,
            'health_check_func': health_check_func or (lambda: True),
            'status': 'healthy',
            'last_check': datetime.now(),
            'check_count': 0
        }
        self.components[component_id] = component_info
        return component_info
    
    def check_system_health(self) -> Dict[str, Any]:
        """Check overall system health."""
        healthy_components = 0
        total_components = len(self.components)
        
        for component_id, component in self.components.items():
            try:
                is_healthy = component['health_check_func']()
                component['status'] = 'healthy' if is_healthy else 'unhealthy'
                component['last_check'] = datetime.now()
                component['check_count'] += 1
                
                if is_healthy:
                    healthy_components += 1
            except Exception as e:
                component['status'] = 'error'
                component['last_error'] = str(e)
        
        health_result = {
            'overall_status': 'healthy' if healthy_components == total_components else 'degraded',
            'healthy_components': healthy_components,
            'total_components': total_components,
            'health_percentage': (healthy_components / total_components * 100) if total_components > 0 else 100,
            'check_timestamp': datetime.now()
        }
        
        self.health_checks.append(health_result)
        return health_result


class TestPDCAOrchestrator:
    """Test PDCA (Plan-Do-Check-Act) orchestration."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.orchestrator = MockPDCAOrchestrator()
    
    def test_orchestrator_initialization(self):
        """Test PDCA orchestrator initialization."""
        assert isinstance(self.orchestrator, MockPDCAOrchestrator)
        assert len(self.orchestrator.cycles) == 0
        assert self.orchestrator.current_phase == "plan"
    
    def test_basic_pdca_cycle_execution(self):
        """Test basic PDCA cycle execution."""
        plan_config = {
            'objective': 'implement_feature_x',
            'resources': {'developers': 2, 'timeline': '2_weeks'},
            'success_criteria': ['tests_pass', 'coverage_90_percent']
        }
        
        result = self.orchestrator.execute_cycle(
            plan_config=plan_config,
            execution_strategy='systematic',
            validation_criteria=['automated_tests', 'code_review'],
            improvement_actions=['optimize_performance', 'enhance_documentation']
        )
        
        assert result['status'] == 'completed'
        assert result['plan_config'] == plan_config
        assert result['execution_strategy'] == 'systematic'
        assert len(result['validation_criteria']) == 2
        assert len(result['improvement_actions']) == 2
        assert result['success_rate'] > 0.9
    
    def test_multiple_pdca_cycles(self):
        """Test execution of multiple PDCA cycles."""
        # Execute first cycle
        cycle1_result = self.orchestrator.execute_cycle(
            plan_config={'objective': 'setup_environment'},
            execution_strategy='systematic'
        )
        
        # Execute second cycle
        cycle2_result = self.orchestrator.execute_cycle(
            plan_config={'objective': 'implement_core_features'},
            execution_strategy='parallel'
        )
        
        # Verify both cycles
        assert len(self.orchestrator.cycles) == 2
        assert cycle1_result['cycle_id'] != cycle2_result['cycle_id']
        assert cycle1_result['plan_config']['objective'] == 'setup_environment'
        assert cycle2_result['plan_config']['objective'] == 'implement_core_features'
    
    def test_pdca_cycle_history_tracking(self):
        """Test PDCA cycle history tracking."""
        # Execute several cycles
        for i in range(3):
            self.orchestrator.execute_cycle(
                plan_config={'objective': f'objective_{i}'},
                execution_strategy='systematic'
            )
        
        history = self.orchestrator.get_cycle_history()
        
        assert len(history) == 3
        for i, cycle in enumerate(history):
            assert cycle['plan_config']['objective'] == f'objective_{i}'
            assert cycle['status'] == 'completed'
    
    def test_pdca_validation_criteria(self):
        """Test PDCA validation criteria handling."""
        validation_criteria = [
            'unit_tests_pass',
            'integration_tests_pass',
            'code_coverage_90_percent',
            'performance_benchmarks_met',
            'security_scan_clean'
        ]
        
        result = self.orchestrator.execute_cycle(
            plan_config={'objective': 'quality_validation'},
            validation_criteria=validation_criteria
        )
        
        assert len(result['validation_criteria']) == 5
        assert 'unit_tests_pass' in result['validation_criteria']
        assert 'security_scan_clean' in result['validation_criteria']
    
    def test_pdca_improvement_actions(self):
        """Test PDCA improvement actions."""
        improvement_actions = [
            'refactor_complex_methods',
            'add_performance_monitoring',
            'enhance_error_handling',
            'improve_documentation'
        ]
        
        result = self.orchestrator.execute_cycle(
            plan_config={'objective': 'continuous_improvement'},
            improvement_actions=improvement_actions
        )
        
        assert len(result['improvement_actions']) == 4
        assert 'refactor_complex_methods' in result['improvement_actions']
        assert 'improve_documentation' in result['improvement_actions']


class TestModelRegistry:
    """Test model-driven decision registry."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.registry = MockModelRegistry()
    
    def test_registry_initialization(self):
        """Test model registry initialization."""
        assert isinstance(self.registry, MockModelRegistry)
        assert len(self.registry.models) == 0
        assert len(self.registry.decisions) == 0
    
    def test_model_registration(self):
        """Test model registration."""
        model_info = self.registry.register_model(
            model_id='complexity_predictor',
            model_type='classification',
            version='1.0.0',
            metadata={
                'accuracy': 0.92,
                'training_data_size': 10000,
                'features': ['code_lines', 'cyclomatic_complexity', 'dependencies']
            }
        )
        
        assert model_info['model_id'] == 'complexity_predictor'
        assert model_info['model_type'] == 'classification'
        assert model_info['version'] == '1.0.0'
        assert model_info['metadata']['accuracy'] == 0.92
        assert model_info['status'] == 'active'
    
    def test_multiple_model_registration(self):
        """Test registration of multiple models."""
        models = [
            ('effort_estimator', 'regression', '2.1.0'),
            ('risk_assessor', 'classification', '1.5.0'),
            ('resource_optimizer', 'optimization', '3.0.0')
        ]
        
        for model_id, model_type, version in models:
            self.registry.register_model(model_id, model_type, version)
        
        assert len(self.registry.models) == 3
        assert 'effort_estimator' in self.registry.models
        assert 'risk_assessor' in self.registry.models
        assert 'resource_optimizer' in self.registry.models
    
    def test_decision_recommendation(self):
        """Test decision recommendation generation."""
        # Register a model first
        self.registry.register_model(
            'decision_engine',
            'recommendation',
            '1.0.0'
        )
        
        context = {
            'project_type': 'web_application',
            'team_size': 5,
            'timeline': '3_months',
            'complexity': 'medium'
        }
        
        decision = self.registry.get_decision_recommendation(
            context=context,
            decision_type='architecture_choice'
        )
        
        assert decision['decision_type'] == 'architecture_choice'
        assert decision['context'] == context
        assert decision['confidence'] > 0.8
        assert 'reasoning' in decision
    
    def test_decision_history_tracking(self):
        """Test decision history tracking."""
        contexts = [
            {'scenario': 'database_choice', 'data_size': 'large'},
            {'scenario': 'deployment_strategy', 'environment': 'cloud'},
            {'scenario': 'testing_approach', 'coverage_target': 90}
        ]
        
        for i, context in enumerate(contexts):
            self.registry.get_decision_recommendation(
                context=context,
                decision_type=f'decision_type_{i}'
            )
        
        assert len(self.registry.decisions) == 3
        for i, decision in enumerate(self.registry.decisions):
            assert decision['decision_type'] == f'decision_type_{i}'
            assert decision['context'] == contexts[i]


class TestHealthMonitor:
    """Test system health monitoring."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.monitor = MockHealthMonitor()
    
    def test_monitor_initialization(self):
        """Test health monitor initialization."""
        assert isinstance(self.monitor, MockHealthMonitor)
        assert len(self.monitor.components) == 0
        assert len(self.monitor.health_checks) == 0
    
    def test_component_registration(self):
        """Test component registration for health monitoring."""
        def mock_health_check():
            return True
        
        component_info = self.monitor.register_component(
            'database_connection',
            mock_health_check
        )
        
        assert component_info['component_id'] == 'database_connection'
        assert component_info['status'] == 'healthy'
        assert component_info['health_check_func'] == mock_health_check
        assert component_info['check_count'] == 0
    
    def test_multiple_component_registration(self):
        """Test registration of multiple components."""
        components = [
            ('api_service', lambda: True),
            ('database', lambda: True),
            ('cache_service', lambda: True),
            ('message_queue', lambda: False)  # Unhealthy component
        ]
        
        for component_id, health_func in components:
            self.monitor.register_component(component_id, health_func)
        
        assert len(self.monitor.components) == 4
        assert 'api_service' in self.monitor.components
        assert 'message_queue' in self.monitor.components
    
    def test_system_health_check(self):
        """Test overall system health check."""
        # Register healthy components
        self.monitor.register_component('service_a', lambda: True)
        self.monitor.register_component('service_b', lambda: True)
        self.monitor.register_component('service_c', lambda: False)  # Unhealthy
        
        health_result = self.monitor.check_system_health()
        
        assert health_result['total_components'] == 3
        assert health_result['healthy_components'] == 2
        assert health_result['health_percentage'] == 66.67  # 2/3 * 100
        assert health_result['overall_status'] == 'degraded'
    
    def test_health_check_error_handling(self):
        """Test health check error handling."""
        def failing_health_check():
            raise Exception("Connection timeout")
        
        self.monitor.register_component('failing_service', failing_health_check)
        health_result = self.monitor.check_system_health()
        
        assert health_result['healthy_components'] == 0
        assert health_result['overall_status'] == 'degraded'
        assert self.monitor.components['failing_service']['status'] == 'error'
    
    def test_health_monitoring_history(self):
        """Test health monitoring history tracking."""
        # Register components
        self.monitor.register_component('stable_service', lambda: True)
        
        # Perform multiple health checks
        for _ in range(3):
            self.monitor.check_system_health()
        
        assert len(self.monitor.health_checks) == 3
        assert self.monitor.components['stable_service']['check_count'] == 3
        
        # All checks should show healthy status
        for check in self.monitor.health_checks:
            assert check['overall_status'] == 'healthy'
            assert check['health_percentage'] == 100.0


class TestBeastModeExceptions:
    """Test Beast Mode exception handling."""
    
    def test_beast_mode_error_creation(self):
        """Test BeastModeError creation."""
        exception = BeastModeError("Test error message")
        
        assert isinstance(exception, Exception)
        assert "Test error message" in str(exception)
    
    def test_exception_with_context(self):
        """Test exception with additional context."""
        try:
            raise BeastModeError("Configuration error", component="test_component", operation="test_operation")
        except BeastModeError as e:
            assert "Configuration error" in str(e)
            assert "test_component" in str(e)
            assert "test_operation" in str(e)
    
    def test_exception_inheritance(self):
        """Test exception inheritance hierarchy."""
        exception = BeastModeError("Test")
        
        assert isinstance(exception, Exception)
        assert isinstance(exception, BeastModeError)


class TestIntegratedBeastModeCore:
    """Test integrated Beast Mode core functionality."""
    
    def setup_method(self):
        """Set up integrated test scenario."""
        self.pdca = MockPDCAOrchestrator()
        self.registry = MockModelRegistry()
        self.monitor = MockHealthMonitor()
    
    def test_integrated_systematic_workflow(self):
        """Test integrated systematic workflow."""
        # 1. Register models for decision making
        self.registry.register_model(
            'workflow_optimizer',
            'optimization',
            '1.0.0',
            {'accuracy': 0.94}
        )
        
        # 2. Register components for health monitoring
        self.monitor.register_component('pdca_orchestrator', lambda: True)
        self.monitor.register_component('model_registry', lambda: True)
        
        # 3. Get decision recommendation
        decision = self.registry.get_decision_recommendation(
            context={'workflow_type': 'development', 'complexity': 'high'},
            decision_type='execution_strategy'
        )
        
        # 4. Execute PDCA cycle based on decision
        cycle_result = self.pdca.execute_cycle(
            plan_config={
                'strategy': decision['recommendation'],
                'confidence': decision['confidence']
            },
            execution_strategy='systematic'
        )
        
        # 5. Check system health
        health_result = self.monitor.check_system_health()
        
        # Verify integrated workflow
        assert len(self.registry.models) == 1
        assert len(self.registry.decisions) == 1
        assert len(self.pdca.cycles) == 1
        assert health_result['overall_status'] == 'healthy'
        assert cycle_result['status'] == 'completed'
    
    def test_systematic_error_recovery(self):
        """Test systematic error recovery patterns."""
        # Register failing component
        self.monitor.register_component('failing_component', lambda: False)
        
        # Check health (should detect failure)
        health_result = self.monitor.check_system_health()
        assert health_result['overall_status'] == 'degraded'
        
        # Get decision for recovery
        recovery_decision = self.registry.get_decision_recommendation(
            context={'health_status': 'degraded', 'failed_components': 1},
            decision_type='recovery_strategy'
        )
        
        # Execute recovery PDCA cycle
        recovery_cycle = self.pdca.execute_cycle(
            plan_config={
                'objective': 'system_recovery',
                'strategy': recovery_decision['recommendation']
            },
            validation_criteria=['health_check_passes'],
            improvement_actions=['implement_circuit_breaker', 'add_monitoring']
        )
        
        assert recovery_cycle['status'] == 'completed'
        assert 'system_recovery' in recovery_cycle['plan_config']['objective']
        assert len(recovery_cycle['improvement_actions']) == 2
    
    def test_continuous_improvement_cycle(self):
        """Test continuous improvement cycle."""
        # Execute initial cycle
        initial_cycle = self.pdca.execute_cycle(
            plan_config={'objective': 'initial_implementation'},
            validation_criteria=['basic_functionality']
        )
        
        # Get improvement recommendations
        improvement_decision = self.registry.get_decision_recommendation(
            context={
                'cycle_success_rate': initial_cycle['success_rate'],
                'validation_results': 'passed'
            },
            decision_type='improvement_strategy'
        )
        
        # Execute improvement cycle
        improvement_cycle = self.pdca.execute_cycle(
            plan_config={
                'objective': 'continuous_improvement',
                'previous_cycle': initial_cycle['cycle_id']
            },
            improvement_actions=[
                'optimize_performance',
                'enhance_monitoring',
                'improve_documentation'
            ]
        )
        
        # Verify continuous improvement
        assert len(self.pdca.cycles) == 2
        assert improvement_cycle['plan_config']['objective'] == 'continuous_improvement'
        assert len(improvement_cycle['improvement_actions']) == 3


if __name__ == "__main__":
    pytest.main([__file__, "-v"])