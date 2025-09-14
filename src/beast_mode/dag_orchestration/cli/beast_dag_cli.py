#!/usr/bin/env python3
"""
Beast Mode DAG Orchestration CLI Entry Point.

Provides the beast-dag command for systematic ecosystem orchestration.
"""

from .dag_cli import beast_dag
from src.rm_ddd.core.health import ModuleHealth


if __name__ == '__main__':
    beast_dag()