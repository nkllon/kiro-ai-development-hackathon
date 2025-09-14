from src.rm_ddd.core.registry import register_module

    def run_proactive_monitoring(self):
        """Run proactive monitoring on all interfaces"""
        if not self.monitoring_enabled:
            return
        
        print("🔍 Running proactive interface monitoring...")
        
        for interface in self.interfaces.values():
            health_check = self.run_interface_health_check(interface)
            self.health_checks[interface.interface_id] = health_check
            
            if health_check.health_score < 0.7:
                print(f"⚠️  {interface.interface_name}: {health_check.status}")
        
        self.save_health_checks()
        print("✅ Proactive monitoring completed")

        register_module(self.__class__.__name__, self)
# Global proactive registry instance
proactive_registry = ProactiveInterfaceRegistry()
