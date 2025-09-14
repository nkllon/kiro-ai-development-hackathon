from .command_center_class_2_part_1 import *
from .command_center_class_2_part_2 import *
from .command_center_class_2_part_3 import *
from .command_center_class_2_part_4 import *
from .command_center_class_2_part_5 import *
from .command_center_class_2_part_6 import *
from .command_center_class_2_part_7 import *
from .command_center_class_2_part_8 import *
from .command_center_class_2_part_9 import *
from .command_center_class_2_part_10 import *
from .command_center_class_2_part_11 import *
from .command_center_class_2_part_12 import *
from .command_center_class_2_part_13 import *
from .command_center_class_2_part_14 import *
from .command_center_class_2_part_15 import *
from .command_center_class_2_part_16 import *
from .command_center_class_2_part_17 import *
from .command_center_class_2_part_18 import *
from .command_center_class_2_part_19 import *
from .command_center_class_2_part_20 import *
from .command_center_class_2_part_21 import *
from .command_center_class_2_part_22 import *
from .command_center_class_2_part_23 import *
from .command_center_class_2_part_24 import *
from .command_center_class_2_part_25 import *
from .command_center_class_2_part_26 import *
from .command_center_class_2_part_27 import *
from .command_center_class_2_part_28 import *
from .command_center_class_2_part_29 import *
from .command_center_class_2_part_30 import *
from .command_center_class_2_part_31 import *
from .command_center_class_2_part_32 import *
from .command_center_class_2_part_33 import *
from .command_center_class_2_part_34 import *
from .command_center_class_2_part_35 import *
from .command_center_class_2_part_36 import *
from .command_center_class_2_part_37 import *
from .command_center_class_2_part_38 import *
from .command_center_class_2_part_39 import *
from .command_center_class_2_part_40 import *
from .command_center_class_2_part_41 import *
from .command_center_class_2_part_42 import *
from .command_center_class_2_part_43 import *
from .command_center_class_2_part_44 import *
from .command_center_class_2_part_45 import *
from .command_center_class_2_part_46 import *
from .command_center_class_2_part_47 import *
from .command_center_class_2_part_48 import *
from .command_center_class_2_part_49 import *
from .command_center_class_2_part_50 import *
from .command_center_class_2_part_51 import *
from .command_center_class_2_part_52 import *
from .command_center_class_2_part_53 import *
from .command_center_class_2_part_54 import *
from .command_center_class_2_part_55 import *
from .command_center_class_2_part_56 import *
from .command_center_class_2_part_57 import *
from .command_center_class_2_part_58 import *
from .command_center_class_2_part_59 import *
from .command_center_class_2_part_60 import *
from .command_center_class_2_part_61 import *
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

