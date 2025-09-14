from src.rm_ddd.core.registry import register_module
from src.rm_ddd.core.health import ModuleHealth


    def get_provider_capabilities(self) -> Dict[str, bool]:
        """Get provider-specific capabilities"""
        return {'branch_management': True, 'commit_operations': True, 'remote_operations': True, 'conflict_resolution': True, 'visual_merge_tools': False, 'enhanced_ui': False, 'api_integration': False, 'advanced_analytics': False}
