from .png_utils_part_1 import *
from .png_utils_part_2 import *
from .png_utils_part_3 import *
from .png_utils_part_4 import *
from .png_utils_part_5 import *
from .png_utils_part_6 import *
from .png_utils_part_7 import *
from .png_utils_part_8 import *
from .png_utils_part_9 import *
from .png_utils_part_10 import *
from .png_utils_part_11 import *
from .png_utils_part_12 import *
from .png_utils_part_13 import *
from .png_utils_part_14 import *
from .png_utils_part_15 import *
from .png_utils_part_16 import *
from .png_utils_part_17 import *
from .png_utils_part_18 import *
from .png_utils_part_19 import *
from .png_utils_part_20 import *
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

