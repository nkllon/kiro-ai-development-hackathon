"""
RC1 DAG Organization Module
===========================

DAG-based document organization and hierarchy management.
Part of the Beast Mode parallel execution system.
"""

from .dag_builder import DAGBuilder, DocumentNode, DocumentDAG

__all__ = ['DAGBuilder', 'DocumentNode', 'DocumentDAG']
