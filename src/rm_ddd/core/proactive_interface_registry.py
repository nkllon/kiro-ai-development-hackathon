from .proactive_interface_registry_part_1 import *
from .proactive_interface_registry_part_2 import *
from .proactive_interface_registry_part_3 import *
from .proactive_interface_registry_part_4 import *
from .proactive_interface_registry_part_5 import *
from .proactive_interface_registry_part_6 import *
from .proactive_interface_registry_part_7 import *
from .proactive_interface_registry_part_8 import *
from .proactive_interface_registry_part_9 import *
from .proactive_interface_registry_part_10 import *
from .proactive_interface_registry_part_11 import *
from .proactive_interface_registry_part_12 import *
from .proactive_interface_registry_part_13 import *
from .proactive_interface_registry_part_14 import *
from .proactive_interface_registry_part_15 import *
from .proactive_interface_registry_part_16 import *
from .proactive_interface_registry_part_17 import *
from .proactive_interface_registry_part_18 import *
from .proactive_interface_registry_part_19 import *
from .proactive_interface_registry_part_20 import *
from .proactive_interface_registry_part_21 import *
from .proactive_interface_registry_part_22 import *
from .proactive_interface_registry_part_23 import *
from .proactive_interface_registry_part_24 import *
from .proactive_interface_registry_part_25 import *
from .proactive_interface_registry_part_26 import *
from .proactive_interface_registry_part_27 import *
from .proactive_interface_registry_part_28 import *
from .proactive_interface_registry_part_29 import *
from .proactive_interface_registry_part_30 import *
from .proactive_interface_registry_part_31 import *
from .proactive_interface_registry_part_32 import *
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

