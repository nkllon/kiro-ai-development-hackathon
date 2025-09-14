from src.rm_ddd.core.registry import register_module

def _configure_auto_scaling(self, resources: GKEResources) -> None:
    """Configure GKE auto-scaling based on resources."""
    logger.info('Configuring GKE auto-scaling')
