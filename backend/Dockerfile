FROM python:3.11-slim-bookworm

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update \
    && apt-get upgrade -y --no-install-recommends \
    && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --upgrade --no-cache-dir pip setuptools wheel \
    && pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY app/ ./app/
COPY basecamp_todos/ ./basecamp_todos/
COPY start_server.py .

# Copy entrypoint scripts
COPY ../docker-entrypoint.sh /docker-entrypoint.sh
COPY ../aws/scripts/aws-entrypoint.sh /aws-entrypoint.sh
RUN chmod +x /docker-entrypoint.sh /aws-entrypoint.sh

# Create non-root user with home directory
RUN useradd --create-home --uid 1000 --shell /bin/bash appuser \
    && mkdir -p /app/data \
    && chown -R appuser:appuser /app

# Change d’utilisateur
USER appuser

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
    CMD curl --fail http://localhost:8000/health || exit 1

# Use entrypoint script for secure startup
ENTRYPOINT ["/docker-entrypoint.sh"]
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1"]
