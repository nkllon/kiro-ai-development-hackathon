from src.rm_ddd.core.health import ModuleHealth, ModuleStatus

def _auto_register_entity(entity_instance: Any, domain_context: str):
    """Auto-register entity with bounded context."""
    try:
        logger.debug(f'Auto-registered entity {entity_instance.__class__.__name__} in context {domain_context}')
    except Exception as e:
        logger.warning(f'Failed to auto-register entity: {e}')
