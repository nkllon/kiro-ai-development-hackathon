# Systematic PDCA Orchestrator - Production Deployment
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY src/ ./src/
COPY project_model_registry.json .
COPY learning_patterns/ ./learning_patterns/

# Copy test files for validation
COPY test_pdca_integration.py .
COPY test_real_registry.py .
COPY test_enhanced_learning.py .

# Create non-root user
RUN useradd -m -u 1000 pdca && chown -R pdca:pdca /app
USER pdca

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "from src.beast_mode.core.model_registry import ModelRegistry; r = ModelRegistry(); print('Health:', r.get_health_status()['status'])"

# Expose port
EXPOSE 8080

# Environment variables
ENV PYTHONPATH=/app
ENV PORT=8080
ENV ENVIRONMENT=production

# Start command
CMD ["python", "-m", "uvicorn", "src.beast_mode.api.main:app", "--host", "0.0.0.0", "--port", "8080"]