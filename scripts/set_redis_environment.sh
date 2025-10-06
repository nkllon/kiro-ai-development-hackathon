#!/bin/bash
# Redis Environment Configuration for Vonnegut
# Set these environment variables to point ReflectiveModules to Redis on Vonnegut

# Redis connection details for Vonnegut
export REDIS_HOST="vonnegut"
export REDIS_PORT="6379"
export REDIS_PASSWORD=""  # Set if Redis has password authentication

# Optional: Beast Mode specific Redis settings
export BEAST_MODE_REDIS_ENABLED="true"
export BEAST_MODE_REDIS_HOST="$REDIS_HOST"
export BEAST_MODE_REDIS_PORT="$REDIS_PORT"
export BEAST_MODE_REDIS_PASSWORD="$REDIS_PASSWORD"

echo "✅ Redis environment variables set for Vonnegut:"
echo "   REDIS_HOST=$REDIS_HOST"
echo "   REDIS_PORT=$REDIS_PORT"
echo "   REDIS_PASSWORD=[${#REDIS_PASSWORD} chars]"

# Test connection
echo "Testing Redis connection..."
redis-cli -h "$REDIS_HOST" -p "$REDIS_PORT" ping 2>/dev/null && echo "✅ Redis connection successful" || echo "❌ Redis connection failed"