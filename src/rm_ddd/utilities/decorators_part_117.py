from src.rm_ddd.core.health import ModuleHealth, ModuleStatus

def enhanced_init(self, *args, **kwargs):
    original_init(self, *args, **kwargs)
    _auto_register_aggregate(self, domain_context)
