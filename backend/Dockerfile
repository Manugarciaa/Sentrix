# Sentrix Backend - Dockerfile
# Multi-stage build for optimized production image

# ============================================
# Stage 1: Builder
# ============================================
FROM python:3.11-slim as builder

# Set working directory
WORKDIR /build

# Install system dependencies for building Python packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    postgresql-client \
    libpq-dev \
    libgeos-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy shared library first
COPY shared /build/shared

# Copy backend requirements
COPY backend/requirements.txt .

# Create virtual environment and install dependencies
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Upgrade pip
RUN pip install --no-cache-dir --upgrade pip

# Install shared library first (NOT editable for Docker)
RUN pip install --no-cache-dir /build/shared

# Install other requirements (excluding shared which is already installed)
RUN grep -v "^\-e.*shared" requirements.txt > requirements-docker.txt && \
    pip install --no-cache-dir -r requirements-docker.txt

# ============================================
# Stage 2: Runtime
# ============================================
FROM python:3.11-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH="/opt/venv/bin:$PATH" \
    PORT=8000

# Install runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    postgresql-client \
    libpq5 \
    libgeos-c1v5 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create app user for security
RUN useradd -m -u 1000 appuser && \
    mkdir -p /app /app/logs /app/uploads /app/temp && \
    chown -R appuser:appuser /app

# Set working directory
WORKDIR /app

# Copy virtual environment from builder
COPY --from=builder /opt/venv /opt/venv

# Copy shared library (needed because it's installed as editable)
COPY --from=builder --chown=appuser:appuser /build/shared /app/shared

# Copy application code from backend directory
COPY --chown=appuser:appuser backend/ .

# Switch to non-root user
USER appuser

# Health check - use /health/ready for comprehensive dependency checks
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:${PORT}/health/ready || exit 1

# Expose port
EXPOSE ${PORT}

# Run the application
CMD ["python", "-m", "uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
