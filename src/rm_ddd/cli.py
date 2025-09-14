import asyncio
import json
import logging
from pathlib import Path
from typing import Optional
import click
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.syntax import Syntax
from . import __version__, get_ecosystem_info, quick_start_example
from .core.registry import get_global_registry
from .core.compliance import get_global_compliance_orchestrator
import webbrowser
from .cli_core import *
from src.rm_ddd.core.health import ModuleHealth


class RegistermoduleClass:
    """Auto-generated class for functions."""

    def register_module(self, registry):
    """Register module with registry."""
    metadata = self.get_interface_metadata()
    if hasattr(registry, 'register'):
    registry.register(metadata)

    def get_interface_metadata(self):
    """Get interface metadata for registry."""
    return {
    'module_id': getattr(self, 'module_id', self.__class__.__name__),
    'interface_type': self.__class__.__name__,
    'version': '1.0.0',
    'dependencies': [],
    'capabilities': []
    }

