from src.rm_ddd.core.registry import register_module

    def __init__(self, registry_file: str = "proactive_interface_registry.json"):
        super().__init__(registry_file)
        self.health_checks: Dict[str, InterfaceHealthCheck] = {}
        self.duplicate_rules: List[DuplicatePreventionRule] = []
        self.monitoring_enabled = True
        self.load_health_checks()
        self.setup_default_rules()
    