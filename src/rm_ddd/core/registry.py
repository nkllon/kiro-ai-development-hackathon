from .registry_part_1 import *
from .registry_part_2 import *
from .registry_part_3 import *
from .registry_part_4 import *
from .registry_part_5 import *
from .registry_part_6 import *
from .registry_part_7 import *
from .registry_part_8 import *
from .registry_part_9 import *
from .registry_part_10 import *
from .registry_part_11 import *
from .registry_part_12 import *
from .registry_part_13 import *
from .registry_part_14 import *
from .registry_part_15 import *
from .registry_part_16 import *
from .registry_part_17 import *
from .registry_part_18 import *
from .registry_part_19 import *
from .registry_part_20 import *
from .registry_part_21 import *
from .registry_part_22 import *
from .registry_part_23 import *
from .registry_part_24 import *
from .registry_part_25 import *
from .registry_part_26 import *
from .registry_part_27 import *
from .registry_part_28 import *
from .registry_part_29 import *
from .registry_part_30 import *
from .registry_part_31 import *
from .registry_part_32 import *
from .registry_part_33 import *
from .registry_part_34 import *
from .registry_part_35 import *
from .registry_part_36 import *
from .registry_part_37 import *
from .registry_part_38 import *
from .registry_part_39 import *
from .registry_part_40 import *
from .registry_part_41 import *
from .registry_part_42 import *
from .registry_part_43 import *
from .registry_part_44 import *
from .registry_part_45 import *
from .registry_part_46 import *
from .registry_part_47 import *
from .registry_part_48 import *
from .registry_part_49 import *
from .registry_part_50 import *
from .registry_part_51 import *
from .registry_part_52 import *
from .registry_part_53 import *
from .registry_part_54 import *
from .registry_part_55 import *
from .registry_part_56 import *
from .registry_part_57 import *
from .registry_part_58 import *
from .registry_part_59 import *
from .registry_part_60 import *
from .registry_part_61 import *
from .registry_part_62 import *
from .registry_part_63 import *
from .registry_part_64 import *
from .registry_part_65 import *
from .registry_part_66 import *
from .registry_part_67 import *
from .registry_part_68 import *
from .registry_part_69 import *
from .registry_part_70 import *
from .registry_part_71 import *
from .registry_part_72 import *
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

