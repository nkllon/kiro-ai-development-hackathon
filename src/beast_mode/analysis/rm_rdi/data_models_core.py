from .data_models_core_part_1 import *
from .data_models_core_part_2 import *
from .data_models_core_part_3 import *
from .data_models_core_part_4 import *
from .data_models_core_part_5 import *
from .data_models_core_part_6 import *
from .data_models_core_part_7 import *
from .data_models_core_part_8 import *
from .data_models_core_part_9 import *
from .data_models_core_part_10 import *
from .data_models_core_part_11 import *
from .data_models_core_part_12 import *
from .data_models_core_part_13 import *
from .data_models_core_part_14 import *
from .data_models_core_part_15 import *
from .data_models_core_part_16 import *
from .data_models_core_part_17 import *
from .data_models_core_part_18 import *
from .data_models_core_part_19 import *
from .data_models_core_part_20 import *
from .data_models_core_part_21 import *
from .data_models_core_part_22 import *
from .data_models_core_part_23 import *
from .data_models_core_part_24 import *
from .data_models_core_part_25 import *
from .data_models_core_part_26 import *
from .data_models_core_part_27 import *
from .data_models_core_part_28 import *
from .data_models_core_part_29 import *
from .data_models_core_part_30 import *
from .data_models_core_part_31 import *
from .data_models_core_part_32 import *
from .data_models_core_part_33 import *
from .data_models_core_part_34 import *
from .data_models_core_part_35 import *
from .data_models_core_part_36 import *
from .data_models_core_part_37 import *
from .data_models_core_part_38 import *
from .data_models_core_part_39 import *
from .data_models_core_part_40 import *
from .data_models_core_part_41 import *
from .data_models_core_part_42 import *
from .data_models_core_part_43 import *
from .data_models_core_part_44 import *
from .data_models_core_part_45 import *
from .data_models_core_part_46 import *
from .data_models_core_part_47 import *
from .data_models_core_part_48 import *
from .data_models_core_part_49 import *
from .data_models_core_part_50 import *
from .data_models_core_part_51 import *
from .data_models_core_part_52 import *
from .data_models_core_part_53 import *
from .data_models_core_part_54 import *
from .data_models_core_part_55 import *
from .data_models_core_part_56 import *
from .data_models_core_part_57 import *
from .data_models_core_part_58 import *
from .data_models_core_part_59 import *
from .data_models_core_part_60 import *
from .data_models_core_part_61 import *
from .data_models_core_part_62 import *
from .data_models_core_part_63 import *
from .data_models_core_part_64 import *
from .data_models_core_part_65 import *
from .data_models_core_part_66 import *
from .data_models_core_part_67 import *
from .data_models_core_part_68 import *
from .data_models_core_part_69 import *
from .data_models_core_part_70 import *
from .data_models_core_part_71 import *
from .data_models_core_part_72 import *
from .data_models_core_part_73 import *
from .data_models_core_part_74 import *
from .data_models_core_part_75 import *
from .data_models_core_part_76 import *
from .data_models_core_part_77 import *
from .data_models_core_part_78 import *
from .data_models_core_part_79 import *
from .data_models_core_part_80 import *
from .data_models_core_part_81 import *
from .data_models_core_part_82 import *
from .data_models_core_part_83 import *
from .data_models_core_part_84 import *
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

