# Railway-optimized Dockerfile for ACT Strategic Service
FROM mcr.microsoft.com/playwright/python:v1.40.0-jammy

# Set working directory
WORKDIR /app

# Set environment variables for Railway
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV HEADLESS=true
ENV HOST=0.0.0.0
ENV MAX_CONCURRENCY=2
ENV TIMEOUT_MS=30000

# Install system dependencies needed for Railway
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better Docker layer caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Install Playwright browsers (Firefox for our service)
RUN python -m playwright install firefox && \
    python -m playwright install-deps firefox

# Create directory for storage state and logs
RUN mkdir -p /app/data && \
    chmod 777 /app/data

# Make Railway start script executable
RUN chmod +x start_railway.py

# Expose port (Railway will set the actual port via PORT env var)
EXPOSE $PORT

# Health check optimized for Railway
HEALTHCHECK --interval=60s --timeout=30s --start-period=120s --retries=3 \
    CMD curl -f http://localhost:$PORT/health || exit 1

# Use Railway-specific startup script
CMD ["python", "start_railway.py"]