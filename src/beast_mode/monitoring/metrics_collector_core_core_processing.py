"""
Metrics Collector Core Core Processing

This module was extracted from metrics_collector_core_core.py
as part of RM-DDD compliance refactoring.
"""

import asyncio
import logging
import time
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field
from collections import defaultdict, deque
import json
from src.rm_ddd.core.health import ModuleHealth


def _parse_metric_key(self, metric_key: str) -> tuple[str, Dict[str, str]]:
    """Parse a metric key back into name and labels."""
    if '{' not in metric_key:
        return (metric_key, {})
    name, label_part = metric_key.split('{', 1)
    label_part = label_part.rstrip('}')
    labels = {}
    if label_part:
        for label_pair in label_part.split(','):
            key, value = label_pair.split('=', 1)
            labels[key] = value
    return (name, labels)

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

