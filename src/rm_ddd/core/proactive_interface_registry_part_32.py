from datetime import datetime
from typing import Dict, List, Any

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

# Global proactive registry instance
proactive_registry = ProactiveInterfaceRegistry()
