FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first to leverage Docker cache
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Create agents directory structure 
RUN mkdir -p /app/agents /app/data /app/backups && \
    chmod -R 755 /app/agents /app/data /app/backups

# Create __init__.py in the agents directory
RUN echo "# Agents package" > /app/agents/__init__.py

# Copy the entire repository content
COPY . /app/

# Set environment variables
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# Debug - list files to verify
RUN ls -la /app && \
    ls -la /app/agents

# Make start script executable
RUN chmod +x /app/start.sh

# Command to run the application
CMD ["gunicorn", "main:app", "--workers", "2", "--worker-class", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8000", "--timeout", "120", "--log-level", "debug"]