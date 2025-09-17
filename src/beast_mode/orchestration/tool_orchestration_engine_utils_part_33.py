from src.rm_ddd.core.health import ModuleHealth

def handle_unknown_tool_failure(self, failure_context: Dict[str, Any]) -> Dict[str, Any]:
    """
        Handle unknown tool failure using adaptive patterns
        Implements UK-06: Tool failure diversity unknowns handling
        """
    try:
        failure_signature = self._generate_failure_signature(failure_context)
        matching_pattern = None
        if hasattr(self, 'adaptive_patterns'):
            for pattern_name, pattern in self.adaptive_patterns.items():
                if self._matches_failure_pattern(failure_signature, pattern):
                    matching_pattern = pattern
                    break
        if matching_pattern:
            self.logger.info(f"Applying adaptive pattern for unknown failure: {matching_pattern['failure_type']}")
            response = self._apply_adaptive_response(failure_context, matching_pattern)
            self._update_adaptive_pattern_learning(matching_pattern, response)
            return {'unknown_failure_handled': True, 'adaptive_pattern_used': matching_pattern['failure_type'], 'response_strategy': matching_pattern['response_strategy'], 'outcome': response, 'learning_updated': True}
        else:
            self.logger.info('No matching adaptive pattern - creating new approach')
            new_pattern = self._create_adaptive_pattern_for_unknown(failure_context)
            response = self._apply_adaptive_response(failure_context, new_pattern)
            if not hasattr(self, 'adaptive_patterns'):
                self.adaptive_patterns = {}
            self.adaptive_patterns[new_pattern['failure_type']] = new_pattern
            return {'unknown_failure_handled': True, 'new_adaptive_pattern_created': True, 'pattern_name': new_pattern['failure_type'], 'response_strategy': new_pattern['response_strategy'], 'outcome': response, 'pattern_stored_for_learning': True}
    except Exception as e:
        self.logger.error(f'Unknown tool failure handling failed: {e}')
        return {'unknown_failure_handled': False, 'error': str(e), 'fallback': 'escalate_to_manual_intervention'}

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

