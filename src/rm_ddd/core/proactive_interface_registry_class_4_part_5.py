from src.rm_ddd.core.registry import register_module

    def load_health_checks(self):
        """Load interface health checks from storage"""
        health_file = self.registry_file.replace('.json', '_health.json')
        if os.path.exists(health_file):
            try:
                with open(health_file, 'r') as f:
                    data = json.load(f)
                for interface_id, health_data in data.items():
                    self.health_checks[interface_id] = InterfaceHealthCheck(**health_data)
            except Exception as e:
                print(f"Warning: Could not load health checks: {e}")
    