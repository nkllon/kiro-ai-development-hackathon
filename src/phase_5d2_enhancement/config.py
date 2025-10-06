"""
Configuration management for Phase 5D2 Enhancement System
"""

import os
from dataclasses import dataclass
from typing import Dict, Any, Optional


@dataclass
class EnhancementConfig:
    """Configuration for Phase 5D2 Enhancement System with environment variable support."""
    
    # Jaeger distributed tracing configuration
    jaeger_endpoint: str = os.getenv('JAEGER_ENDPOINT', 'http://jaeger:14268/api/traces')
    jaeger_service_name: str = os.getenv('JAEGER_SERVICE_NAME', 'phase-5d2-enhancement')
    jaeger_enabled: bool = os.getenv('JAEGER_ENABLED', 'true').lower() == 'true'
    
    # Redis coordination and caching
    redis_url: str = os.getenv('REDIS_URL', 'redis://localhost:6379')
    redis_password: str = os.getenv('REDIS_PASSWORD', '')
    redis_db: int = int(os.getenv('REDIS_DB', '0'))
    
    # Prometheus monitoring
    prometheus_gateway: str = os.getenv('PROMETHEUS_GATEWAY', 'http://prometheus:9091')
    prometheus_job_name: str = os.getenv('PROMETHEUS_JOB_NAME', 'phase-5d2-enhancement')
    
    # Enhancement processing configuration
    enhancement_batch_size: int = int(os.getenv('ENHANCEMENT_BATCH_SIZE', '10'))
    max_enhancement_cycles: int = int(os.getenv('MAX_ENHANCEMENT_CYCLES', '3'))
    parallel_workers: int = int(os.getenv('PARALLEL_WORKERS', '4'))
    
    # Quality targets and thresholds
    quality_target_threshold: float = float(os.getenv('QUALITY_TARGET_THRESHOLD', '70.0'))
    critical_gap_threshold: float = float(os.getenv('CRITICAL_GAP_THRESHOLD', '10.0'))
    improvement_threshold: float = float(os.getenv('IMPROVEMENT_THRESHOLD', '5.0'))
    
    # File system paths
    spec_repository_path: str = os.getenv('SPEC_REPOSITORY_PATH', '.kiro/specs')
    reports_path: str = os.getenv('REPORTS_PATH', '.kiro/reports')
    gap_mitigation_path: str = os.getenv('GAP_MITIGATION_PATH', '.kiro/reports/phase-5d2-gap-mitigation')
    
    # Enhancement engine configuration
    problem_taxonomy_weight: float = float(os.getenv('PROBLEM_TAXONOMY_WEIGHT', '1.5'))
    cost_optimization_weight: float = float(os.getenv('COST_OPTIMIZATION_WEIGHT', '1.5'))
    scalability_weight: float = float(os.getenv('SCALABILITY_WEIGHT', '1.3'))
    
    # Timeout and retry configuration
    analysis_timeout: int = int(os.getenv('ANALYSIS_TIMEOUT', '300'))
    enhancement_timeout: int = int(os.getenv('ENHANCEMENT_TIMEOUT', '600'))
    max_retries: int = int(os.getenv('MAX_RETRIES', '3'))
    retry_delay: float = float(os.getenv('RETRY_DELAY', '1.0'))
    
    def __post_init__(self):
        """Validate configuration after initialization."""
        self._validate_configuration()
    
    def _validate_configuration(self) -> None:
        """Validate configuration values and provide helpful error messages."""
        if self.quality_target_threshold <= 0 or self.quality_target_threshold > 100:
            raise ValueError(f"Quality target threshold must be between 0 and 100, got {self.quality_target_threshold}")
        
        if self.critical_gap_threshold < 0 or self.critical_gap_threshold > 100:
            raise ValueError(f"Critical gap threshold must be between 0 and 100, got {self.critical_gap_threshold}")
        
        if self.enhancement_batch_size <= 0:
            raise ValueError(f"Enhancement batch size must be positive, got {self.enhancement_batch_size}")
        
        if self.max_enhancement_cycles <= 0:
            raise ValueError(f"Max enhancement cycles must be positive, got {self.max_enhancement_cycles}")
        
        if self.parallel_workers <= 0:
            raise ValueError(f"Parallel workers must be positive, got {self.parallel_workers}")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary for logging and serialization."""
        return {
            'jaeger_endpoint': self.jaeger_endpoint,
            'jaeger_service_name': self.jaeger_service_name,
            'jaeger_enabled': self.jaeger_enabled,
            'redis_url': self.redis_url,
            'redis_db': self.redis_db,
            'prometheus_gateway': self.prometheus_gateway,
            'enhancement_batch_size': self.enhancement_batch_size,
            'max_enhancement_cycles': self.max_enhancement_cycles,
            'parallel_workers': self.parallel_workers,
            'quality_target_threshold': self.quality_target_threshold,
            'critical_gap_threshold': self.critical_gap_threshold,
            'improvement_threshold': self.improvement_threshold,
            'spec_repository_path': self.spec_repository_path,
            'reports_path': self.reports_path,
            'gap_mitigation_path': self.gap_mitigation_path,
            'analysis_timeout': self.analysis_timeout,
            'enhancement_timeout': self.enhancement_timeout,
            'max_retries': self.max_retries,
            'retry_delay': self.retry_delay
        }
    
    @classmethod
    def from_environment(cls) -> 'EnhancementConfig':
        """Create configuration from environment variables with validation."""
        return cls()
    
    def get_redis_connection_params(self) -> Dict[str, Any]:
        """Get Redis connection parameters."""
        params = {
            'url': self.redis_url,
            'db': self.redis_db,
            'decode_responses': True
        }
        if self.redis_password:
            params['password'] = self.redis_password
        return params
    
    def get_jaeger_config(self) -> Dict[str, Any]:
        """Get Jaeger configuration parameters."""
        return {
            'endpoint': self.jaeger_endpoint,
            'service_name': self.jaeger_service_name,
            'enabled': self.jaeger_enabled
        }
    
    def get_quality_thresholds(self) -> Dict[str, float]:
        """Get quality threshold configuration."""
        return {
            'overall_quality_target': self.quality_target_threshold,
            'critical_gap_threshold': self.critical_gap_threshold,
            'improvement_threshold': self.improvement_threshold,
            'problem_taxonomy_weight': self.problem_taxonomy_weight,
            'cost_optimization_weight': self.cost_optimization_weight,
            'scalability_weight': self.scalability_weight
        }


def load_enhancement_config() -> EnhancementConfig:
    """Load and validate enhancement configuration from environment."""
    try:
        config = EnhancementConfig.from_environment()
        return config
    except Exception as e:
        raise ValueError(f"Failed to load enhancement configuration: {e}")


# Global configuration instance
_config: Optional[EnhancementConfig] = None


def get_config() -> EnhancementConfig:
    """Get global configuration instance, loading if necessary."""
    global _config
    if _config is None:
        _config = load_enhancement_config()
    return _config


def reload_config() -> EnhancementConfig:
    """Reload configuration from environment variables."""
    global _config
    _config = load_enhancement_config()
    return _config