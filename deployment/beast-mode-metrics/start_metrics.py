#!/usr/bin/env python3
"""
Beast Mode Metrics Exporter Daemon
==================================

Simple daemon to run Prometheus metrics exporter.
"""

import time
import logging
from src.beast_mode.monitoring.prometheus_exporter import PrometheusExporter

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('beast_mode_metrics')

def main():
    """Main metrics exporter daemon."""
    logger.info('Starting Beast Mode Prometheus exporter on port 8000')
    
    try:
        # Create exporter instance
        exporter = PrometheusExporter(port=8000, enable_http_server=True)
        logger.info('Beast Mode metrics available at http://localhost:8000/metrics')
        
        # Keep daemon running
        while True:
            time.sleep(60)
            logger.debug('Beast Mode metrics heartbeat')
            
    except KeyboardInterrupt:
        logger.info('Beast Mode metrics exporter shutting down')
    except Exception as e:
        logger.error(f'Beast Mode metrics exporter error: {e}')
        raise

if __name__ == '__main__':
    main()