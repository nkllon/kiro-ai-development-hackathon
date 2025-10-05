"""
Deployment Data Governance Auditor

A real-time monitoring daemon that continuously watches the repository for violations
of deployment data governance rules, preventing volatile data from entering version control.
"""

__version__ = "1.0.0"
__author__ = "Beast Mode Framework"

from .core import DeploymentAuditor
from .models import FileEvent, Violation, ClassifiedViolation, RemediationResult

__all__ = [
    "DeploymentAuditor",
    "FileEvent", 
    "Violation",
    "ClassifiedViolation",
    "RemediationResult"
]