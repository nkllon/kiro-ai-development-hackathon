from .gcp_integration_part_1 import *
from .gcp_integration_part_2 import *
from .gcp_integration_part_3 import *
from .gcp_integration_part_4 import *
from .gcp_integration_part_5 import *
from .gcp_integration_part_6 import *
from .gcp_integration_part_7 import *
from .gcp_integration_part_8 import *
from .gcp_integration_part_9 import *
from .gcp_integration_part_10 import *
from .gcp_integration_part_11 import *
from .gcp_integration_part_12 import *
from .gcp_integration_part_13 import *
from .gcp_integration_part_14 import *
from .gcp_integration_part_15 import *
from .gcp_integration_part_16 import *
from .gcp_integration_part_17 import *
from .gcp_integration_part_18 import *
from .gcp_integration_part_19 import *
from .gcp_integration_part_20 import *
from .gcp_integration_part_21 import *
from .gcp_integration_part_22 import *
from .gcp_integration_part_23 import *
from .gcp_integration_part_24 import *
from .gcp_integration_part_25 import *
from .gcp_integration_part_26 import *
from .gcp_integration_part_27 import *
from .gcp_integration_part_28 import *
from .gcp_integration_part_29 import *
from .gcp_integration_part_30 import *
from .gcp_integration_part_31 import *
from .gcp_integration_part_32 import *
from .gcp_integration_part_33 import *
from .gcp_integration_part_34 import *
from .gcp_integration_part_35 import *
from .gcp_integration_part_36 import *
from .gcp_integration_part_37 import *
from .gcp_integration_part_38 import *
from .gcp_integration_part_39 import *
from .gcp_integration_part_40 import *
from .gcp_integration_part_41 import *
from .gcp_integration_part_42 import *
from .gcp_integration_part_43 import *
from .gcp_integration_part_44 import *
from .gcp_integration_part_45 import *
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

