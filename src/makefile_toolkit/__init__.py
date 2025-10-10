"""Makefile toolkit shared modules."""

from .system_tester import MakefileSystemTester, main as system_test_main
from .safety_validator import MakefileSafetyValidator, main as safety_validator_main
from .performance_optimizer import MakefilePerformanceOptimizer, main as performance_optimizer_main
from .target_validator import MakefileTargetValidator, main as target_validator_main

__all__ = [
    'MakefileSystemTester',
    'MakefileSafetyValidator',
    'MakefilePerformanceOptimizer',
    'MakefileTargetValidator',
    'system_test_main',
    'safety_validator_main',
    'performance_optimizer_main',
    'target_validator_main',
]
