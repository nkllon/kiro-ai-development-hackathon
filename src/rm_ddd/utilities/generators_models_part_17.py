from src.rm_ddd.core.health import ModuleHealth

    def __init__(self, template_registry: TemplateRegistry):
        super().__init__(template_registry)
        self._register_default_extensions()
