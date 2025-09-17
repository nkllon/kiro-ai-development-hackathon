from .workflow_part_1 import *
from .workflow_part_2 import *
from .workflow_part_3 import *
from .workflow_part_4 import *
from .workflow_part_5 import *
from .workflow_part_6 import *
from .workflow_part_7 import *
from .workflow_part_8 import *
from .workflow_part_9 import *
from .workflow_part_10 import *
from .workflow_part_11 import *
from .workflow_part_12 import *
from .workflow_part_13 import *
from .workflow_part_14 import *
from .workflow_part_15 import *
from .workflow_part_16 import *
from .workflow_part_17 import *
from .workflow_part_18 import *
from .workflow_part_19 import *
from .workflow_part_20 import *
from .workflow_part_21 import *
from .workflow_part_22 import *
from .workflow_part_23 import *
from .workflow_part_24 import *
from .workflow_part_25 import *
from .workflow_part_26 import *
from .workflow_part_27 import *
from .workflow_part_28 import *
from .workflow_part_29 import *
from .workflow_part_30 import *
from .workflow_part_31 import *
from .workflow_part_32 import *
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

