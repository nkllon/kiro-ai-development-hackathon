FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create data directories
RUN mkdir -p observatory_data/metrics observatory_data/dashboards observatory_data/logs observatory_data/config

# Expose port
EXPOSE 8888

# Start Observatory
CMD ["python", "start_observatory.py"]
