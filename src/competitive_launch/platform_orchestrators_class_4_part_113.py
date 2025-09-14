from src.rm_ddd.core.registry import register_module

def _deploy_core_services(self, resources: GKEResources) -> List[str]:
    """Deploy core Beast Mode services on GKE."""
    services = ['beast-mode-api', 'beast-mode-agents', 'beast-mode-monitoring', 'beast-mode-messaging']
    logger.info(f'Deploying core services: {services}')
    return services
