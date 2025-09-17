import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from pathlib import Path
from .interfaces import BillingProvider, BillingMetrics, BillingProviderType, HealthStatus, ReflectiveModule
from .asset_bridge.gcp_billing_client import GCPBillingClientBridge
from .asset_bridge.cost_analyzer import CostAnalyzerBridge
import random
import random
import random
import random
import random
import random
from .gcp_integration_core_core_core import *
from src.rm_ddd.core.health import ModuleHealth


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

