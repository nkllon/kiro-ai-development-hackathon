from datetime import datetime
from typing import Dict, List, Any

    def _deploy_core_services(self, resources: GKEResources) -> List[str]:
        """Deploy core Beast Mode services on GKE."""
        services = ['beast-mode-api', 'beast-mode-agents', 'beast-mode-monitoring', 'beast-mode-messaging']
        logger.info(f'Deploying core services: {services}')
        return services
