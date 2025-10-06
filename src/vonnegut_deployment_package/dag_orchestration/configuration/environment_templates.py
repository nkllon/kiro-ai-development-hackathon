#!/usr/bin/env python3
"""
Environment-Specific Configuration Templates
==========================================

Pre-configured templates for different deployment environments
with optimized settings for development, production, and testing.

Author: Beast Mode Framework
Date: 2025-01-27
Version: 1.0
"""

import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum

from .configuration_manager import ConfigurationTemplate
from .llm_selection_policies import LLMSelectionStrategy
from .execution_strategy_config import ExecutionMode
from .monitoring_config import MetricType, AlertSeverity, ReportFormat


class EnvironmentType(Enum):
    """Environment types for template selection."""
    DEVELOPMENT = "development"
    TESTING = "testing"
    STAGING = "staging"
    PRODUCTION = "production"
    PERFORMANCE = "performance"
    DEMO = "demo"


@dataclass
class EnvironmentTemplate:
    """Base class for environment-specific templates."""
    name: str
    environment_type: EnvironmentType
    description: str
    base_configuration: Dict[str, Any]
    optimization_goals: List[str] = field(default_factory=list)
    constraints: List[str] = field(default_factory=list)
    recommended_resources: Dict[str, Any] = field(default_factory=dict)


class DevelopmentTemplate(EnvironmentTemplate):
    """Template optimized for development environment."""
    
    def __init__(self):
        super().__init__(
            name="development",
            environment_type=EnvironmentType.DEVELOPMENT,
            description="Optimized for development with detailed logging and debugging features",
            base_configuration=self._create_development_config(),
            optimization_goals=[
                "Fast feedback loops",
                "Detailed debugging information",
                "Low resource usage",
                "Easy troubleshooting"
            ],
            constraints=[
                "Limited parallelism to avoid resource contention",
                "Verbose logging may impact performance",
                "No production-level security"
            ],
            recommended_resources={
                "cpu_cores": 4,
                "memory_gb": 8,
                "disk_gb": 50,
                "network_bandwidth": "100 Mbps"
            }
        )
    
    def _create_development_config(self) -> Dict[str, Any]:
        """Create development-specific configuration."""
        return {
            "execution": {
                "strategy": ExecutionMode.CONSERVATIVE_PARALLEL.value,
                "max_workers": 4,
                "timeout_seconds": 300,
                "retry_attempts": 2,
                "batch_size": 5,
                "queue_size": 20
            },
            "llm_selection": {
                "policy": LLMSelectionStrategy.COST_FIRST.value,
                "budget_limit": 5.0,  # $5 daily limit
                "fallback_enabled": True,
                "simulation_mode": True,  # Use simulation for testing
                "detailed_logging": True,
                "cost_tracking": True
            },
            "resources": {
                "cpu_threshold": 0.6,
                "memory_threshold": 0.6,
                "disk_threshold": 0.7,
                "monitoring_interval": 10.0,
                "auto_scaling": False
            },
            "monitoring": {
                "metrics_collection_interval": 15.0,
                "detailed_logging": True,
                "performance_tracking": True,
                "debug_mode": True,
                "log_level": "DEBUG",
                "metrics_retention_days": 3,
                "alerting_enabled": False,
                "dashboard_enabled": True,
                "api_enabled": True
            },
            "integration": {
                "ace_reporter_enabled": True,
                "ai_memory_palace_enabled": True,
                "external_apis_enabled": False,  # Avoid external dependencies
                "mock_services": True
            },
            "security": {
                "authentication_required": False,
                "ssl_enabled": False,
                "api_key_required": False,
                "cors_enabled": True
            },
            "development": {
                "hot_reload": True,
                "auto_restart": True,
                "code_coverage": True,
                "profiling_enabled": True,
                "test_mode": True
            }
        }


class TestingTemplate(EnvironmentTemplate):
    """Template optimized for testing environment."""
    
    def __init__(self):
        super().__init__(
            name="testing",
            environment_type=EnvironmentType.TESTING,
            description="Optimized for automated testing with fast execution and isolation",
            base_configuration=self._create_testing_config(),
            optimization_goals=[
                "Fast test execution",
                "Isolated test environments",
                "Deterministic behavior",
                "Comprehensive test coverage"
            ],
            constraints=[
                "Sequential execution for predictability",
                "Limited resource usage",
                "No external dependencies",
                "Simplified configuration"
            ],
            recommended_resources={
                "cpu_cores": 2,
                "memory_gb": 4,
                "disk_gb": 20,
                "network_bandwidth": "50 Mbps"
            }
        )
    
    def _create_testing_config(self) -> Dict[str, Any]:
        """Create testing-specific configuration."""
        return {
            "execution": {
                "strategy": ExecutionMode.SEQUENTIAL_FALLBACK.value,
                "max_workers": 1,  # Sequential for predictability
                "timeout_seconds": 60,
                "retry_attempts": 1,
                "batch_size": 1,
                "queue_size": 10
            },
            "llm_selection": {
                "policy": LLMSelectionStrategy.COST_FIRST.value,
                "budget_limit": 1.0,  # $1 limit for tests
                "fallback_enabled": True,
                "simulation_mode": True,  # Always use simulation
                "detailed_logging": False,
                "cost_tracking": False
            },
            "resources": {
                "cpu_threshold": 0.5,
                "memory_threshold": 0.5,
                "disk_threshold": 0.6,
                "monitoring_interval": 30.0,
                "auto_scaling": False
            },
            "monitoring": {
                "metrics_collection_interval": 60.0,
                "detailed_logging": False,
                "performance_tracking": False,
                "debug_mode": False,
                "log_level": "INFO",
                "metrics_retention_days": 1,
                "alerting_enabled": False,
                "dashboard_enabled": False,
                "api_enabled": False
            },
            "integration": {
                "ace_reporter_enabled": False,
                "ai_memory_palace_enabled": False,
                "external_apis_enabled": False,
                "mock_services": True
            },
            "security": {
                "authentication_required": False,
                "ssl_enabled": False,
                "api_key_required": False,
                "cors_enabled": False
            },
            "testing": {
                "test_isolation": True,
                "cleanup_after_test": True,
                "deterministic_mode": True,
                "fast_mode": True,
                "coverage_enabled": True
            }
        }


class ProductionTemplate(EnvironmentTemplate):
    """Template optimized for production environment."""
    
    def __init__(self):
        super().__init__(
            name="production",
            environment_type=EnvironmentType.PRODUCTION,
            description="Optimized for production with high performance, reliability, and security",
            base_configuration=self._create_production_config(),
            optimization_goals=[
                "Maximum performance",
                "High reliability",
                "Comprehensive monitoring",
                "Security compliance",
                "Cost optimization"
            ],
            constraints=[
                "High resource requirements",
                "Complex configuration",
                "Security restrictions",
                "Compliance requirements"
            ],
            recommended_resources={
                "cpu_cores": 16,
                "memory_gb": 32,
                "disk_gb": 500,
                "network_bandwidth": "1 Gbps"
            }
        )
    
    def _create_production_config(self) -> Dict[str, Any]:
        """Create production-specific configuration."""
        return {
            "execution": {
                "strategy": ExecutionMode.AGGRESSIVE_PARALLEL.value,
                "max_workers": 20,
                "timeout_seconds": 600,
                "retry_attempts": 3,
                "batch_size": 20,
                "queue_size": 200
            },
            "llm_selection": {
                "policy": LLMSelectionStrategy.BALANCED.value,
                "budget_limit": 100.0,  # $100 daily limit
                "fallback_enabled": True,
                "simulation_mode": False,
                "detailed_logging": False,
                "cost_tracking": True,
                "cost_optimization": True
            },
            "resources": {
                "cpu_threshold": 0.8,
                "memory_threshold": 0.8,
                "disk_threshold": 0.9,
                "monitoring_interval": 5.0,
                "auto_scaling": True,
                "scale_up_threshold": 0.7,
                "scale_down_threshold": 0.3
            },
            "monitoring": {
                "metrics_collection_interval": 30.0,
                "detailed_logging": False,
                "performance_tracking": True,
                "debug_mode": False,
                "log_level": "INFO",
                "metrics_retention_days": 30,
                "alerting_enabled": True,
                "dashboard_enabled": True,
                "api_enabled": True,
                "health_checks": True
            },
            "integration": {
                "ace_reporter_enabled": True,
                "ai_memory_palace_enabled": True,
                "external_apis_enabled": True,
                "mock_services": False
            },
            "security": {
                "authentication_required": True,
                "ssl_enabled": True,
                "api_key_required": True,
                "cors_enabled": False,
                "rate_limiting": True,
                "encryption_at_rest": True,
                "audit_logging": True
            },
            "production": {
                "high_availability": True,
                "backup_enabled": True,
                "disaster_recovery": True,
                "compliance_mode": True,
                "performance_optimization": True
            },
            "alerting": {
                "critical_alerts": True,
                "escalation_enabled": True,
                "notification_channels": ["email", "slack", "pagerduty"],
                "alert_thresholds": {
                    "error_rate": 0.01,
                    "response_time": 5.0,
                    "resource_usage": 0.9
                }
            }
        }


class StagingTemplate(EnvironmentTemplate):
    """Template optimized for staging environment."""
    
    def __init__(self):
        super().__init__(
            name="staging",
            environment_type=EnvironmentType.STAGING,
            description="Production-like environment for final testing and validation",
            base_configuration=self._create_staging_config(),
            optimization_goals=[
                "Production-like behavior",
                "Integration testing",
                "Performance validation",
                "Security testing"
            ],
            constraints=[
                "Limited resources compared to production",
                "Temporary data retention",
                "Reduced monitoring"
            ],
            recommended_resources={
                "cpu_cores": 8,
                "memory_gb": 16,
                "disk_gb": 200,
                "network_bandwidth": "500 Mbps"
            }
        )
    
    def _create_staging_config(self) -> Dict[str, Any]:
        """Create staging-specific configuration."""
        return {
            "execution": {
                "strategy": ExecutionMode.CONSERVATIVE_PARALLEL.value,
                "max_workers": 10,
                "timeout_seconds": 450,
                "retry_attempts": 3,
                "batch_size": 15,
                "queue_size": 100
            },
            "llm_selection": {
                "policy": LLMSelectionStrategy.BALANCED.value,
                "budget_limit": 20.0,  # $20 daily limit
                "fallback_enabled": True,
                "simulation_mode": False,
                "detailed_logging": True,
                "cost_tracking": True
            },
            "resources": {
                "cpu_threshold": 0.75,
                "memory_threshold": 0.75,
                "disk_threshold": 0.85,
                "monitoring_interval": 10.0,
                "auto_scaling": True
            },
            "monitoring": {
                "metrics_collection_interval": 30.0,
                "detailed_logging": True,
                "performance_tracking": True,
                "debug_mode": False,
                "log_level": "INFO",
                "metrics_retention_days": 7,
                "alerting_enabled": True,
                "dashboard_enabled": True,
                "api_enabled": True
            },
            "integration": {
                "ace_reporter_enabled": True,
                "ai_memory_palace_enabled": True,
                "external_apis_enabled": True,
                "mock_services": False
            },
            "security": {
                "authentication_required": True,
                "ssl_enabled": True,
                "api_key_required": True,
                "cors_enabled": False,
                "rate_limiting": True
            },
            "staging": {
                "data_refresh": True,
                "load_testing": True,
                "integration_testing": True,
                "security_testing": True
            }
        }


class PerformanceTemplate(EnvironmentTemplate):
    """Template optimized for performance testing."""
    
    def __init__(self):
        super().__init__(
            name="performance",
            environment_type=EnvironmentType.PERFORMANCE,
            description="Optimized for performance testing and benchmarking",
            base_configuration=self._create_performance_config(),
            optimization_goals=[
                "Maximum throughput",
                "Minimum latency",
                "Resource optimization",
                "Scalability testing"
            ],
            constraints=[
                "High resource requirements",
                "Specialized monitoring",
                "Limited external dependencies"
            ],
            recommended_resources={
                "cpu_cores": 32,
                "memory_gb": 64,
                "disk_gb": 1000,
                "network_bandwidth": "10 Gbps"
            }
        )
    
    def _create_performance_config(self) -> Dict[str, Any]:
        """Create performance testing-specific configuration."""
        return {
            "execution": {
                "strategy": ExecutionMode.AGGRESSIVE_PARALLEL.value,
                "max_workers": 50,
                "timeout_seconds": 300,
                "retry_attempts": 1,  # Minimal retries for performance
                "batch_size": 50,
                "queue_size": 500
            },
            "llm_selection": {
                "policy": LLMSelectionStrategy.PERFORMANCE_FIRST.value,
                "budget_limit": 200.0,
                "fallback_enabled": False,  # No fallback for performance testing
                "simulation_mode": False,
                "detailed_logging": False,
                "cost_tracking": False
            },
            "resources": {
                "cpu_threshold": 0.95,
                "memory_threshold": 0.95,
                "disk_threshold": 0.95,
                "monitoring_interval": 1.0,  # High-frequency monitoring
                "auto_scaling": True,
                "aggressive_scaling": True
            },
            "monitoring": {
                "metrics_collection_interval": 5.0,
                "detailed_logging": False,
                "performance_tracking": True,
                "debug_mode": False,
                "log_level": "WARN",
                "metrics_retention_days": 1,
                "alerting_enabled": False,
                "dashboard_enabled": True,
                "api_enabled": True,
                "high_resolution_metrics": True
            },
            "integration": {
                "ace_reporter_enabled": False,
                "ai_memory_palace_enabled": False,
                "external_apis_enabled": True,
                "mock_services": False
            },
            "security": {
                "authentication_required": False,
                "ssl_enabled": False,
                "api_key_required": False,
                "cors_enabled": True
            },
            "performance": {
                "optimization_mode": True,
                "profiling_enabled": True,
                "benchmarking": True,
                "load_generation": True,
                "stress_testing": True
            }
        }


class DemoTemplate(EnvironmentTemplate):
    """Template optimized for demonstrations and presentations."""
    
    def __init__(self):
        super().__init__(
            name="demo",
            environment_type=EnvironmentType.DEMO,
            description="Optimized for demonstrations with visual feedback and reliability",
            base_configuration=self._create_demo_config(),
            optimization_goals=[
                "Visual appeal",
                "Reliable execution",
                "Clear feedback",
                "Impressive performance"
            ],
            constraints=[
                "Simplified configuration",
                "Predictable behavior",
                "Limited complexity"
            ],
            recommended_resources={
                "cpu_cores": 8,
                "memory_gb": 16,
                "disk_gb": 100,
                "network_bandwidth": "1 Gbps"
            }
        )
    
    def _create_demo_config(self) -> Dict[str, Any]:
        """Create demo-specific configuration."""
        return {
            "execution": {
                "strategy": ExecutionMode.CONSERVATIVE_PARALLEL.value,
                "max_workers": 8,
                "timeout_seconds": 180,
                "retry_attempts": 2,
                "batch_size": 8,
                "queue_size": 50
            },
            "llm_selection": {
                "policy": LLMSelectionStrategy.BALANCED.value,
                "budget_limit": 50.0,
                "fallback_enabled": True,
                "simulation_mode": False,
                "detailed_logging": True,
                "cost_tracking": True,
                "demo_mode": True
            },
            "resources": {
                "cpu_threshold": 0.7,
                "memory_threshold": 0.7,
                "disk_threshold": 0.8,
                "monitoring_interval": 5.0,
                "auto_scaling": False  # Predictable behavior
            },
            "monitoring": {
                "metrics_collection_interval": 10.0,
                "detailed_logging": True,
                "performance_tracking": True,
                "debug_mode": False,
                "log_level": "INFO",
                "metrics_retention_days": 1,
                "alerting_enabled": False,
                "dashboard_enabled": True,
                "api_enabled": True,
                "real_time_updates": True
            },
            "integration": {
                "ace_reporter_enabled": True,
                "ai_memory_palace_enabled": True,
                "external_apis_enabled": True,
                "mock_services": False
            },
            "security": {
                "authentication_required": False,
                "ssl_enabled": True,
                "api_key_required": False,
                "cors_enabled": True
            },
            "demo": {
                "visual_feedback": True,
                "progress_indicators": True,
                "success_animations": True,
                "error_handling": "graceful",
                "presentation_mode": True
            }
        }


class EnvironmentTemplateManager:
    """Manager for environment-specific configuration templates."""
    
    def __init__(self):
        self._templates: Dict[str, EnvironmentTemplate] = {}
        self._logger = logging.getLogger(f"dag_orchestration.{self.__class__.__name__}")
        
        # Initialize default templates
        self._initialize_default_templates()
        
        self._logger.info("EnvironmentTemplateManager initialized with default templates")
    
    def _initialize_default_templates(self) -> None:
        """Initialize all default environment templates."""
        templates = [
            DevelopmentTemplate(),
            TestingTemplate(),
            ProductionTemplate(),
            StagingTemplate(),
            PerformanceTemplate(),
            DemoTemplate()
        ]
        
        for template in templates:
            self._templates[template.name] = template
    
    def get_template(self, name: str) -> EnvironmentTemplate:
        """Get environment template by name."""
        if name not in self._templates:
            raise ValueError(f"Template '{name}' not found")
        
        return self._templates[name]
    
    def list_templates(self) -> List[str]:
        """List all available template names."""
        return list(self._templates.keys())
    
    def get_template_by_environment(self, environment_type: EnvironmentType) -> EnvironmentTemplate:
        """Get template by environment type."""
        for template in self._templates.values():
            if template.environment_type == environment_type:
                return template
        
        raise ValueError(f"No template found for environment type: {environment_type}")
    
    def create_configuration_template(self, environment_name: str) -> ConfigurationTemplate:
        """Create ConfigurationTemplate from environment template."""
        if environment_name not in self._templates:
            raise ValueError(f"Environment template '{environment_name}' not found")
        
        env_template = self._templates[environment_name]
        
        return ConfigurationTemplate(
            name=env_template.name,
            description=env_template.description,
            environment=env_template.environment_type.value,
            base_config=env_template.base_configuration,
            required_keys=list(env_template.base_configuration.keys())
        )
    
    def recommend_template(self, requirements: Dict[str, Any]) -> str:
        """Recommend best template based on requirements."""
        # Simple heuristic-based recommendation
        use_case = requirements.get('use_case', 'development')
        performance_requirements = requirements.get('performance', 'medium')
        security_requirements = requirements.get('security', 'low')
        
        if use_case == 'production':
            return 'production'
        elif use_case == 'testing':
            return 'testing'
        elif use_case == 'demo':
            return 'demo'
        elif performance_requirements == 'high':
            return 'performance'
        elif security_requirements == 'high':
            return 'staging'
        else:
            return 'development'
    
    def get_template_comparison(self) -> Dict[str, Any]:
        """Get comparison of all templates."""
        comparison = {
            'templates': {},
            'resource_requirements': {},
            'optimization_goals': {},
            'constraints': {}
        }
        
        for name, template in self._templates.items():
            comparison['templates'][name] = {
                'environment_type': template.environment_type.value,
                'description': template.description
            }
            
            comparison['resource_requirements'][name] = template.recommended_resources
            comparison['optimization_goals'][name] = template.optimization_goals
            comparison['constraints'][name] = template.constraints
        
        return comparison


# Convenience functions
def create_environment_template_manager() -> EnvironmentTemplateManager:
    """Factory function to create environment template manager."""
    return EnvironmentTemplateManager()


def get_environment_config(environment: str) -> Dict[str, Any]:
    """Get configuration for specific environment."""
    manager = EnvironmentTemplateManager()
    template = manager.get_template(environment)
    return template.base_configuration