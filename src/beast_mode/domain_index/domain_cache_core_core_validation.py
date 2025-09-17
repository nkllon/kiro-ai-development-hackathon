"""
Domain Cache Core Core Validation

This module was extracted from domain_cache_core_core.py
as part of RM-DDD compliance refactoring.
"""

import time
import threading
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List, Set, Callable
from collections import defaultdict
from dataclasses import dataclass
from .base import DomainSystemComponent
from .interfaces import CacheInterface
from .models import Domain, DomainCollection
import fnmatch
import fnmatch
import fnmatch

def invalidate_by_tag(self, tag: str) -> int:
    """Invalidate all entries with a specific tag"""
    with self._lock:
        keys_to_remove = list(self._tag_index.get(tag, set()))
        for key in keys_to_remove:
            self._remove_entry(key)
        self.invalidations += len(keys_to_remove)
        self.logger.debug(f"Invalidated {len(keys_to_remove)} entries with tag '{tag}'")
        return len(keys_to_remove)

def invalidate_by_pattern(self, pattern: str) -> int:
    """Invalidate all entries matching a key pattern"""
    with self._lock:
        import fnmatch
from src.rm_ddd.core.health import ModuleHealth

        keys_to_remove = [key for key in self._cache.keys() if fnmatch.fnmatch(key, pattern)]
        for key in keys_to_remove:
            self._remove_entry(key)
        self.invalidations += len(keys_to_remove)
        self.logger.debug(f"Invalidated {len(keys_to_remove)} entries matching pattern '{pattern}'")
        return len(keys_to_remove)

def invalidate_domain(self, domain_name: str) -> bool:
    """Invalidate cached domain and related data"""
    self.cache.delete(f'domain:{domain_name}')
    self.cache.invalidate_by_tag('domain_collection')
    self.cache.invalidate_by_pattern('search:*')
    return True

def invalidate_by_category(self, category: str) -> int:
    """Invalidate all domains in a category"""
    return self.cache.invalidate_by_tag(f'category:{category}')

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

