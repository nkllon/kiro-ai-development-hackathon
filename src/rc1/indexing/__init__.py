"""
RC1 Indexing Module - Multi-dimensional indexing with DAG overlay
"""

from .multi_dimensional_indexer import MultiDimensionalIndexer
from .dimensions import *

__all__ = [
    'MultiDimensionalIndexer',
    'TemporalDimension',
    'SpatialDimension', 
    'SemanticDimension',
    'StructuralDimension',
    'QualityDimension',
    'SecurityDimension',
    'PerformanceDimension',
    'DependencyDimension',
    'ArchitectureDimension',
    'TechnologyDimension',
    'StakeholderDimension',
    'ProcessDimension',
    'LifecycleDimension',
    'GovernanceDimension',
    'KnowledgeDimension',
    'MaintenanceDimension',
    'DocumentTypeDimension',
    'ComplexityDimension',
    'AudienceDimension',
    'UrgencyDimension'
]
