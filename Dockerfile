# Multi-stage build for optimized production image
# Stage 1: Base image with dependencies
FROM python:3.11-slim AS base

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements file
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --trusted-host pypi.org --trusted-host files.pythonhosted.org -r requirements.txt && \
    pip install --no-cache-dir --trusted-host pypi.org --trusted-host files.pythonhosted.org gunicorn

# Stage 2: Production image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy installed packages from base stage
COPY --from=base /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=base /usr/local/bin /usr/local/bin

# Copy application code
COPY KS.py .
COPY config.py .
COPY simulator.py .
COPY plotting.py .
COPY ks_web_gui.py .
COPY wsgi.py .
COPY *.json ./

# Create non-root user for security
RUN useradd -m -u 1000 ksuser && \
    chown -R ksuser:ksuser /app

USER ksuser

# Set environment variables
ENV PORT=8080
ENV HOST=0.0.0.0
ENV PYTHONUNBUFFERED=1

# Expose port
EXPOSE 8080

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8080/', timeout=5)" || exit 1

# Run the application with gunicorn
CMD ["sh", "-c", "gunicorn --bind ${HOST}:${PORT} --workers 1 --threads 4 --timeout 120 --access-logfile - --error-logfile - --log-level info wsgi:server"]
