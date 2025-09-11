"""
Devpost Integration Package

Multi-target implementation:
- Hackathon submission demo
- Kiro AI systematic development showcase  
- TiDB-scale architecture example

The Requirements ARE the Solution.
"""

__version__ = "0.1.0"

from .project_manager import DevpostProjectManager
from .sync_manager import DevpostSyncManager
from .preview_generator import DevpostPreviewGenerator
from .api_client import DevPostAPIClient
from .auth_service import DevpostAuthService
from .config import DevpostConfig
from .logging_infrastructure import LoggingInfrastructure, LoggingConfig, LogLevel, get_logging_infrastructure
from .performance_profiler import PerformanceProfiler, ProfilingContext, ProfilingResult, get_performance_profiler
from .debugging_engine import DebuggingEngine, DebugInfo, ExecutionTrace, DiagnosticResult, get_debugging_engine

__all__ = [
    'DevpostProjectManager',
    'DevpostSyncManager',
    'DevpostPreviewGenerator',
    'DevPostAPIClient',
    'DevpostAuthService',
    'DevpostConfig',
    'LoggingInfrastructure',
    'LoggingConfig',
    'LogLevel',
    'get_logging_infrastructure',
    'PerformanceProfiler',
    'ProfilingContext',
    'ProfilingResult',
    'get_performance_profiler',
    'DebuggingEngine',
    'DebugInfo',
    'ExecutionTrace',
    'DiagnosticResult',
    'get_debugging_engine'
]