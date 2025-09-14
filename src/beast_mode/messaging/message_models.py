from .message_models_part_1 import *
from .message_models_part_2 import *
from .message_models_part_3 import *
from .message_models_part_4 import *
from .message_models_part_5 import *
from .message_models_part_6 import *
from .message_models_part_7 import *
from .message_models_part_8 import *
from .message_models_part_9 import *
from .message_models_part_10 import *
from .message_models_part_11 import *
from .message_models_part_12 import *
from .message_models_part_13 import *
from .message_models_part_14 import *
from .message_models_part_15 import *
from .message_models_part_16 import *
from .message_models_part_17 import *
from .message_models_part_18 import *
from .message_models_part_19 import *
from .message_models_part_20 import *
from .message_models_part_21 import *
from .message_models_part_22 import *
from .message_models_part_23 import *
from .message_models_part_24 import *
from .message_models_part_25 import *
from .message_models_part_26 import *
from .message_models_part_27 import *
from .message_models_part_28 import *
from .message_models_part_29 import *
from .message_models_part_30 import *
from .message_models_part_31 import *
from .message_models_part_32 import *
from .message_models_part_33 import *
from .message_models_part_34 import *
from .message_models_part_35 import *
from .message_models_part_36 import *
from .message_models_part_37 import *
from .message_models_part_38 import *
from .message_models_part_39 import *
from .message_models_part_40 import *
from .message_models_part_41 import *
from .message_models_part_42 import *
from .message_models_part_43 import *
from .message_models_part_44 import *
from .message_models_part_45 import *
from .message_models_part_46 import *
from .message_models_part_47 import *
from .message_models_part_48 import *
from .message_models_part_49 import *
from .message_models_part_50 import *
from .message_models_part_51 import *
from .message_models_part_52 import *
from .message_models_part_53 import *
from .message_models_part_54 import *
from .message_models_part_55 import *
from .message_models_part_56 import *
from .message_models_part_57 import *
from .message_models_part_58 import *
from .message_models_part_59 import *
from .message_models_part_60 import *
from .message_models_part_61 import *
from .message_models_part_62 import *
from .message_models_part_63 import *
from .message_models_part_64 import *
from .message_models_part_65 import *
from .message_models_part_66 import *
from .message_models_part_67 import *
from .message_models_part_68 import *
from .message_models_part_69 import *
from .message_models_part_70 import *
from .message_models_part_71 import *
from .message_models_part_72 import *
from .message_models_part_73 import *
from .message_models_part_74 import *
from .message_models_part_75 import *
from .message_models_part_76 import *
from .message_models_part_77 import *
from .message_models_part_78 import *
from .message_models_part_79 import *
from .message_models_part_80 import *
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

