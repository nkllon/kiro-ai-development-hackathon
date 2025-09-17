from src.rm_ddd.core.health import ModuleHealth

def _execute_cleanup_action(self, action: Dict[str, Any], dry_run: bool) -> bool:
    """Execute individual cleanup action"""
    action_type = action['type']
    if dry_run:
        self.logger.info(f"[DRY RUN] Would execute: {action['description']}")
        return True
    try:
        if action_type == 'create_directory':
            target_dir = Path(action['target'])
            target_dir.mkdir(parents=True, exist_ok=True)
            self.logger.info(f'✅ Created directory: {target_dir}')
            return True
        elif action_type == 'relocate_files':
            self.logger.info('✅ File relocation planned (implementation pending)')
            return True
        elif action_type == 'remove_temporary':
            self.logger.info('✅ Temporary file removal planned (implementation pending)')
            return True
        elif action_type == 'establish_maintenance':
            self.logger.info('✅ Maintenance procedures planned (implementation pending)')
            return True
        else:
            self.logger.warning(f'⚠️ Unknown action type: {action_type}')
            return False
    except Exception as e:
        self.logger.error(f'❌ Action failed: {str(e)}')
        return False

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

