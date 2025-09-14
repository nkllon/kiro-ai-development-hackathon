from src.rm_ddd.core.health import ModuleHealth, ModuleStatus

    def timestamping_init(self, *args, **kwargs):
        original_init(self, *args, **kwargs)
        if not hasattr(self, 'timestamp') or not self.timestamp:
            from datetime import datetime
            self.timestamp = datetime.now()
    cls.__init__ = timestamping_init
