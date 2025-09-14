from .sync_manager_part_1 import *
from .sync_manager_part_2 import *
from .sync_manager_part_3 import *
from .sync_manager_part_4 import *
from .sync_manager_part_5 import *
from .sync_manager_part_6 import *
from .sync_manager_part_7 import *
from .sync_manager_part_8 import *
from .sync_manager_part_9 import *
from .sync_manager_part_10 import *
from .sync_manager_part_11 import *
from .sync_manager_part_12 import *
from .sync_manager_part_13 import *
from .sync_manager_part_14 import *
from .sync_manager_part_15 import *
from .sync_manager_part_16 import *
from .sync_manager_part_17 import *
from .sync_manager_part_18 import *
from .sync_manager_part_19 import *
from .sync_manager_part_20 import *
from .sync_manager_part_21 import *
from .sync_manager_part_22 import *
from .sync_manager_part_23 import *
from .sync_manager_part_24 import *
from .sync_manager_part_25 import *
from .sync_manager_part_26 import *
from .sync_manager_part_27 import *
from .sync_manager_part_28 import *
from .sync_manager_part_29 import *
from .sync_manager_part_30 import *
from .sync_manager_part_31 import *
from .sync_manager_part_32 import *
from .sync_manager_part_33 import *
from .sync_manager_part_34 import *
from .sync_manager_part_35 import *
from .sync_manager_part_36 import *
from .sync_manager_part_37 import *
from .sync_manager_part_38 import *
from .sync_manager_part_39 import *
from .sync_manager_part_40 import *
from .sync_manager_part_41 import *
from .sync_manager_part_42 import *
from .sync_manager_part_43 import *
from .sync_manager_part_44 import *
from .sync_manager_part_45 import *
from .sync_manager_part_46 import *
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

