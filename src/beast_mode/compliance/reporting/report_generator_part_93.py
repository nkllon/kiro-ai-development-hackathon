from datetime import datetime
from typing import Dict, List, Any
from src.rm_ddd.core.health import ModuleHealth


def __init__(self) -> Any:
    """Initialize the report generator."""
    self.report_format = 'markdown'
    self.severity_weights = {IssueSeverity.CRITICAL: 4.0, IssueSeverity.HIGH: 3.0, IssueSeverity.MEDIUM: 2.0, IssueSeverity.LOW: 1.0}
