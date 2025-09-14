from .rca_engine_services_core_core_part_1 import *
from .rca_engine_services_core_core_part_2 import *
from .rca_engine_services_core_core_part_3 import *
from .rca_engine_services_core_core_part_4 import *
from .rca_engine_services_core_core_part_5 import *
from .rca_engine_services_core_core_part_6 import *
from .rca_engine_services_core_core_part_7 import *
from .rca_engine_services_core_core_part_8 import *
from .rca_engine_services_core_core_part_9 import *
from .rca_engine_services_core_core_part_10 import *
from .rca_engine_services_core_core_part_11 import *
from .rca_engine_services_core_core_part_12 import *
from .rca_engine_services_core_core_part_13 import *
from .rca_engine_services_core_core_part_14 import *
from .rca_engine_services_core_core_part_15 import *
from .rca_engine_services_core_core_part_16 import *
from .rca_engine_services_core_core_part_17 import *
from .rca_engine_services_core_core_part_18 import *
from .rca_engine_services_core_core_part_19 import *
from .rca_engine_services_core_core_part_20 import *
from .rca_engine_services_core_core_part_21 import *
from .rca_engine_services_core_core_part_22 import *
from .rca_engine_services_core_core_part_23 import *
from .rca_engine_services_core_core_part_24 import *
from .rca_engine_services_core_core_part_25 import *
from .rca_engine_services_core_core_part_26 import *
from .rca_engine_services_core_core_part_27 import *
from .rca_engine_services_core_core_part_28 import *
from .rca_engine_services_core_core_part_29 import *
from .rca_engine_services_core_core_part_30 import *
from .rca_engine_services_core_core_part_31 import *
from .rca_engine_services_core_core_part_32 import *
from .rca_engine_services_core_core_part_33 import *
from .rca_engine_services_core_core_part_34 import *
from .rca_engine_services_core_core_part_35 import *
from .rca_engine_services_core_core_part_36 import *
from .rca_engine_services_core_core_part_37 import *
from .rca_engine_services_core_core_part_38 import *
from .rca_engine_services_core_core_part_39 import *
from .rca_engine_services_core_core_part_40 import *
from .rca_engine_services_core_core_part_41 import *
from .rca_engine_services_core_core_part_42 import *
from .rca_engine_services_core_core_part_43 import *
from .rca_engine_services_core_core_part_44 import *
from .rca_engine_services_core_core_part_45 import *
from .rca_engine_services_core_core_part_46 import *
from .rca_engine_services_core_core_part_47 import *
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

