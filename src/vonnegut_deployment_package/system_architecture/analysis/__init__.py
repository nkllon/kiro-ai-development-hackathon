"""
System Architecture Analysis Module
==================================

Analysis components for the Beast Mode framework system architecture,
including dependency analysis, relationship mapping, and mathematical validation.

Components:
- RelationshipMapper: DAG-compliant dependency analysis with mathematical validation
- DataFlowMapper: Comprehensive data flow analysis and visualization
- AutomationChainAnalyzer: Automation workflow and dependency analysis
- ErrorPropagationAnalyzer: Error propagation path analysis and recovery mapping
"""

from .relationship_mapper import RelationshipMapper, create_relationship_mapper

__all__ = [
    'RelationshipMapper',
    'create_relationship_mapper'
]