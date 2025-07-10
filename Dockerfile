FROM python:3.11-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV VESPA_ENDPOINT=http://localhost:8080

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .
COPY pyproject.toml .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY src/ ./src/
COPY scripts/ ./scripts/
COPY vespa/ ./vespa/
COPY config/ ./config/
COPY muvera.py .
COPY setup.py .

# Create necessary directories
RUN mkdir -p data/raw data/processed data/embeddings logs

# Make scripts executable
RUN chmod +x muvera.py setup.py

# Expose ports
EXPOSE 5000 8080

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5000/health || exit 1

# Default command
CMD ["python", "muvera.py", "ui"]