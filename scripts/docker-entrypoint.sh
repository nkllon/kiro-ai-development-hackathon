#!/bin/bash
# MSP SSL Chaos Tamer - Docker Entrypoint Script

set -e

# Default configuration
MSP_SSL_DATA_DIR=${MSP_SSL_DATA_DIR:-/app/data}
MSP_SSL_LOG_DIR=${MSP_SSL_LOG_DIR:-/app/logs}
MSP_SSL_CONFIG_DIR=${MSP_SSL_CONFIG_DIR:-/app/config}

# Ensure directories exist
mkdir -p "$MSP_SSL_DATA_DIR" "$MSP_SSL_LOG_DIR" "$MSP_SSL_CONFIG_DIR"

# Initialize database if it doesn't exist
if [ ! -f "$MSP_SSL_DATA_DIR/certificates.db" ]; then
    echo "Initializing certificate database..."
    python -c "
import sys
sys.path.insert(0, '/app/src')
from msp_ssl_chaos_tamer.storage.database import CertificateDatabase
db = CertificateDatabase('$MSP_SSL_DATA_DIR/certificates.db')
print('Database initialized successfully')
"
fi

# Start the application based on command
case "$1" in
    server)
        echo "Starting MSP SSL Chaos Tamer server..."
        exec python -m msp_ssl_chaos_tamer.server
        ;;
    worker)
        echo "Starting MSP SSL Chaos Tamer worker..."
        exec python -m msp_ssl_chaos_tamer.worker
        ;;
    cli)
        shift
        exec python -m msp_ssl_chaos_tamer.cli "$@"
        ;;
    *)
        exec "$@"
        ;;
esac