"""
Technical Debt Patch Annotation Reporting Module

This module provides comprehensive reporting and dashboard capabilities
for technical debt patch management, including inventory reports,
trend analysis, and executive dashboards.
"""

from .dashboard import (
    PatchDashboard,
    InventoryReport,
    TrendAnalysis,
    ExecutiveDashboard,
    ReportGenerator,
    DashboardMetrics
)

__all__ = [
    'PatchDashboard',
    'InventoryReport', 
    'TrendAnalysis',
    'ExecutiveDashboard',
    'ReportGenerator',
    'DashboardMetrics'
]