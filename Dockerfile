# Use Python 3.10 slim image as base
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY setup.py .
COPY pyproject.toml .
COPY src/ src/
COPY api_definitions/ api_definitions/

# Install the package
RUN pip install --no-cache-dir -e .

# Expose the port the app runs on
EXPOSE 8000

# Run the application
CMD ["uvicorn", "camarapsap.main:app", "--host", "0.0.0.0", "--port", "8000"]
