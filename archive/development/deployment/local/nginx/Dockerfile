# Nginx Dockerfile for Kiro AI Development Hackathon
FROM nginx:1.25-alpine

# Install additional tools for debugging and health checks
RUN apk add --no-cache curl

# Copy custom nginx configuration
COPY nginx.conf /etc/nginx/nginx.conf

# Create directories for logs and static files
RUN mkdir -p /var/log/nginx /var/www/static

# Create a simple status page
RUN echo '<!DOCTYPE html><html><head><title>Kiro AI Development Hackathon</title><style>body{font-family:Arial,sans-serif;margin:40px}.status{color:#28a745;font-weight:bold}.container{max-width:800px;margin:0 auto}</style></head><body><div class="container"><h1>Kiro AI Development Hackathon</h1><p class="status">✅ Nginx is running</p><p>API endpoints are available at <a href="/api/">/api/</a></p><p>Health check: <a href="/health">/health</a></p><p>Nginx health: <a href="/nginx-health">/nginx-health</a></p></div></body></html>' > /usr/share/nginx/html/index.html

# Set proper permissions
RUN chown -R nginx:nginx /var/log/nginx /var/www

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost/nginx-health || exit 1

# Expose port 80
EXPOSE 80

# Start nginx
CMD ["nginx", "-g", "daemon off;"]
