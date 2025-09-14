
    def analyze_module(self, module: ReflectiveModule) -> ModuleAnalysis:
        """Analyze ReflectiveModule and extract CLI-relevant information"""
        try:
            capabilities = module.get_capabilities()
            methods = self._analyze_methods(module)
            configuration = module.get_configuration()
            health = module.check_health()
            metrics = module.get_metrics()
            return ModuleAnalysis(module=module, capabilities=capabilities, methods=methods, configuration=configuration, health=health, metrics=metrics)
        except Exception as e:
            return ModuleAnalysis(module=module, capabilities=[], methods=[], configuration=ModuleConfiguration(module_id=module.module_id, settings={}, last_updated=datetime.now()), health=ModuleHealth(module_id=module.module_id, status=ModuleStatus.ERROR, health_score=0.0, issues=[f'Analysis error: {str(e)}'], capabilities=[], dependencies=[], metrics={}, last_check=datetime.now()), metrics={})

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

