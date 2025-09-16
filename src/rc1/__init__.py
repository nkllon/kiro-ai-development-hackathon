"""
RC1 Module - Systematic Intelligence for System Recovery

Advanced AI-powered system diagnosis and repair with DAG-driven architecture.
Provides enterprise-grade solutions for complex development challenges.
"""

__version__ = "1.0.0"
__author__ = "RC1 Development Team"

from .foundation import MakefileHealthManager, DAGAnalyzer, HealthScorer, AutoFixer
from .cli import beast_mode
from .monitoring import HealthMonitor, MetricsCollector, AlertSystem

__all__ = [
    'MakefileHealthManager',
    'DAGAnalyzer', 
    'HealthScorer',
    'AutoFixer',
    'beast_mode',
    'HealthMonitor',
    'MetricsCollector',
    'AlertSystem'
]