"""
CA Plugin system for MSP SSL Chaos Tamer

This module contains Certificate Authority plugins that implement
the CAPlugin interface for different certificate providers.
"""

# Plugin registry will be populated as plugins are loaded
AVAILABLE_PLUGINS = {}

def register_plugin(plugin_name: str, plugin_class):
    """Register a CA plugin"""
    AVAILABLE_PLUGINS[plugin_name] = plugin_class

def get_plugin(plugin_name: str):
    """Get a registered CA plugin class"""
    return AVAILABLE_PLUGINS.get(plugin_name)

def list_plugins():
    """List all available CA plugins"""
    return list(AVAILABLE_PLUGINS.keys())