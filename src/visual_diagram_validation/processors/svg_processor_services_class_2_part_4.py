from src.rm_ddd.core.registry import register_module
from src.rm_ddd.core.health import ModuleHealth


class InitClass:
    """Auto-generated class for functions."""

    def __init__(self):
    register_module(self.__class__.__name__, self)
    """Initialize SVG processor."""
    self._supported_formats = ['svg']

    @property