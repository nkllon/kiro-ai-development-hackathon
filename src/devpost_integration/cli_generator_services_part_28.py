
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
