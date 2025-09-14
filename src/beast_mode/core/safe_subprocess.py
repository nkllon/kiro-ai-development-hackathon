from .safe_subprocess_part_1 import *
from .safe_subprocess_part_2 import *
from .safe_subprocess_part_3 import *
from .safe_subprocess_part_4 import *
from .safe_subprocess_part_5 import *
from .safe_subprocess_part_6 import *
from .safe_subprocess_part_7 import *
from .safe_subprocess_part_8 import *
from .safe_subprocess_part_9 import *
from .safe_subprocess_part_10 import *
from .safe_subprocess_part_11 import *
from .safe_subprocess_part_12 import *
from .safe_subprocess_part_13 import *
from .safe_subprocess_part_14 import *
from .safe_subprocess_part_15 import *
from .safe_subprocess_part_16 import *
from .safe_subprocess_part_17 import *
from .safe_subprocess_part_18 import *
from .safe_subprocess_part_19 import *
from .safe_subprocess_part_20 import *
from .safe_subprocess_part_21 import *
from .safe_subprocess_part_22 import *
from .safe_subprocess_part_23 import *
from .safe_subprocess_part_24 import *
from .safe_subprocess_part_25 import *
from .safe_subprocess_part_26 import *
from .safe_subprocess_part_27 import *
from .safe_subprocess_part_28 import *
from .safe_subprocess_part_29 import *
from .safe_subprocess_part_30 import *
from .safe_subprocess_part_31 import *
from .safe_subprocess_part_32 import *
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

