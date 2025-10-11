# Multi-stage Dockerfile for Online Bookstore Application
# Stage 1: Build stage
FROM python:3.12-slim AS builder

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Create and set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Stage 2: Production stage
FROM python:3.12-slim AS production

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    FLASK_APP=app_refactored.py \
    FLASK_ENV=production \
    PORT=5000

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Create non-root user
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Create and set working directory
WORKDIR /app

# Copy Python dependencies from builder stage
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy application code
COPY app_refactored.py .
COPY models_refactored.py .
COPY services.py .
COPY config.py .
COPY run_refactored.py .
COPY run_refactored_tests.py .

# Copy static files and templates
COPY static/ ./static/
COPY templates/ ./templates/

# Copy tests (for running tests in container)
COPY tests/ ./tests/

# Create necessary directories
RUN mkdir -p /app/logs /app/data

# Set ownership to non-root user
RUN chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

# Expose port
EXPOSE 5000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5000/ || exit 1

# Default command
CMD ["python", "run_refactored.py"]

# Stage 3: Development stage
FROM production AS development

# Switch back to root for development tools
USER root

# Install development dependencies
RUN pip install --no-cache-dir \
    pytest \
    pytest-cov \
    pytest-xdist \
    pytest-html \
    flake8 \
    black \
    isort \
    mypy \
    pylint \
    bandit \
    safety

# Install additional development tools
RUN apt-get update && apt-get install -y \
    git \
    vim \
    && rm -rf /var/lib/apt/lists/*

# Switch back to appuser
USER appuser

# Override command for development
CMD ["python", "run_refactored.py"]

# Stage 4: Testing stage
FROM development AS testing

# Copy test configuration
COPY pytest.ini* ./

# Override command for testing
CMD ["python", "run_refactored_tests.py"]

# Labels for metadata
LABEL maintainer="Baffoe L.K." \
      version="1.0.0" \
      description="Online Bookstore Flask Application" \
      org.opencontainers.image.title="Online Bookstore" \
      org.opencontainers.image.description="A refactored Flask web application for an online bookstore" \
      org.opencontainers.image.version="1.0.0" \
      org.opencontainers.image.authors="Baffoe L.K." \
      org.opencontainers.image.url="https://github.com/Baffoe6/online_bookstore_final_assessment_Baffoe_L_K_2416509" \
      org.opencontainers.image.source="https://github.com/Baffoe6/online_bookstore_final_assessment_Baffoe_L_K_2416509" \
      org.opencontainers.image.licenses="MIT"
