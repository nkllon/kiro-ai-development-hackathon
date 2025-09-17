from .path_normalizer_class_3_part_1 import *
from .path_normalizer_class_3_part_2 import *
from .path_normalizer_class_3_part_3 import *
from .path_normalizer_class_3_part_4 import *
from .path_normalizer_class_3_part_5 import *
from .path_normalizer_class_3_part_6 import *
from .path_normalizer_class_3_part_7 import *
from .path_normalizer_class_3_part_8 import *
from .path_normalizer_class_3_part_9 import *
from .path_normalizer_class_3_part_10 import *
from .path_normalizer_class_3_part_11 import *
from .path_normalizer_class_3_part_12 import *
from .path_normalizer_class_3_part_13 import *
from .path_normalizer_class_3_part_14 import *
from .path_normalizer_class_3_part_15 import *
from .path_normalizer_class_3_part_16 import *
from .path_normalizer_class_3_part_17 import *
from .path_normalizer_class_3_part_18 import *
from .path_normalizer_class_3_part_19 import *
from .path_normalizer_class_3_part_20 import *
from .path_normalizer_class_3_part_21 import *
from .path_normalizer_class_3_part_22 import *
from .path_normalizer_class_3_part_23 import *
from .path_normalizer_class_3_part_24 import *
from .path_normalizer_class_3_part_25 import *
from .path_normalizer_class_3_part_26 import *
from .path_normalizer_class_3_part_27 import *
from .path_normalizer_class_3_part_28 import *
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

