from src.rm_ddd.core.health import ModuleHealth, ModuleStatus

    def stateless_init(self, *args, **kwargs):
        self._initializing = True
        original_init(self, *args, **kwargs)
        del self._initializing
    cls.__init__ = stateless_init
