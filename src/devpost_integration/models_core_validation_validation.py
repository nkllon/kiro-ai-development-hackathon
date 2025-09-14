from .models_core_validation_validation_part_1 import *
from .models_core_validation_validation_part_2 import *
from .models_core_validation_validation_part_3 import *
from .models_core_validation_validation_part_4 import *
from .models_core_validation_validation_part_5 import *
from .models_core_validation_validation_part_6 import *
from .models_core_validation_validation_part_7 import *
from .models_core_validation_validation_part_8 import *
from .models_core_validation_validation_part_9 import *
from .models_core_validation_validation_part_10 import *
from .models_core_validation_validation_part_11 import *
from .models_core_validation_validation_part_12 import *
from .models_core_validation_validation_part_13 import *
from .models_core_validation_validation_part_14 import *
from .models_core_validation_validation_part_15 import *
from .models_core_validation_validation_part_16 import *
from .models_core_validation_validation_part_17 import *
from .models_core_validation_validation_part_18 import *
from .models_core_validation_validation_part_19 import *
from .models_core_validation_validation_part_20 import *
from .models_core_validation_validation_part_21 import *
from .models_core_validation_validation_part_22 import *
from .models_core_validation_validation_part_23 import *
from .models_core_validation_validation_part_24 import *
from .models_core_validation_validation_part_25 import *
from .models_core_validation_validation_part_26 import *
from .models_core_validation_validation_part_27 import *
from .models_core_validation_validation_part_28 import *
from .models_core_validation_validation_part_29 import *
from .models_core_validation_validation_part_30 import *
from .models_core_validation_validation_part_31 import *
from .models_core_validation_validation_part_32 import *
from .models_core_validation_validation_part_33 import *
from .models_core_validation_validation_part_34 import *
from .models_core_validation_validation_part_35 import *
from .models_core_validation_validation_part_36 import *
from .models_core_validation_validation_part_37 import *
from .models_core_validation_validation_part_38 import *
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

