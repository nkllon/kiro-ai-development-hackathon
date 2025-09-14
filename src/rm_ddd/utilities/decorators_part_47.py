from src.rm_ddd.core.health import ModuleHealth, ModuleStatus

    def immutable_init(self, *args, **kwargs):
        original_init(self, *args, **kwargs)
        self._initialized = True
    cls.__init__ = immutable_init
