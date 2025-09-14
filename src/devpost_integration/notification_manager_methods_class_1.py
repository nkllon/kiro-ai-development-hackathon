from .notification_manager_methods_class_1_part_1 import *
from .notification_manager_methods_class_1_part_2 import *
from .notification_manager_methods_class_1_part_3 import *
from .notification_manager_methods_class_1_part_4 import *
from .notification_manager_methods_class_1_part_5 import *
from .notification_manager_methods_class_1_part_6 import *
from .notification_manager_methods_class_1_part_7 import *
from .notification_manager_methods_class_1_part_8 import *
from .notification_manager_methods_class_1_part_9 import *
from .notification_manager_methods_class_1_part_10 import *
from .notification_manager_methods_class_1_part_11 import *
from .notification_manager_methods_class_1_part_12 import *
from .notification_manager_methods_class_1_part_13 import *
from .notification_manager_methods_class_1_part_14 import *
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

