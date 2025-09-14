from src.rm_ddd.core.health import ModuleHealth

    def get_module_status(self) -> Dict[str, Any]:
        """Get current status of tool health manager"""
        successful_repairs = len([r for r in self.repair_history if r.repair_successful])
        repair_success_rate = successful_repairs / len(self.repair_history) if self.repair_history else 0.0
        return {'module_name': 'ToolHealthManager', 'monitored_tools_count': len(self.monitored_tools), 'repairs_performed': len(self.repair_history), 'successful_repairs': successful_repairs, 'repair_success_rate': repair_success_rate, 'fix_tools_first_principle': 'active', 'systematic_approach': 'proven'}
