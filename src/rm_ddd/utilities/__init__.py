"""
Convenience utilities for RM-DDD framework.

This module provides decorators, validators, generators, and other
convenience utilities that make it easier to implement domain-driven
design patterns with systematic compliance.
"""

from .decorators import (
    domain_entity,
    aggregate_root,
    domain_service,
    ubiquitous_language,
    value_object,
    domain_event,
)
from .validators import DomainValidator
from .generators import RMDDDCodeGenerator
from .complexity import ComplexityMonitor

__all__ = [
    "domain_entity",
    "aggregate_root", 
    "domain_service",
    "ubiquitous_language",
    "value_object",
    "domain_event",
    "DomainValidator",
    "RMDDDCodeGenerator",
    "ComplexityMonitor",
]