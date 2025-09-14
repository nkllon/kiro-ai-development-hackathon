from src.rm_ddd.core.health import ModuleHealth, ModuleStatus

        def enhanced_init(self, *args, **kwargs):
            original_init(self, *args, **kwargs)
            _auto_register_aggregate(self, domain_context)
        cls.__init__ = enhanced_init
    logger.debug(f'Applied @aggregate_root decorator to {cls.__name__}')
    return cls
