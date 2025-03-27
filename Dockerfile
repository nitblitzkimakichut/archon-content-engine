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

# Directly create simple_strategy_agent.py in the image
RUN echo 'from fastapi import FastAPI, HTTPException\nfrom pydantic import BaseModel, Field\nfrom typing import List, Dict, Any, Optional\nimport os\nfrom datetime import datetime\n\napp = FastAPI()\n\nclass VideoData(BaseModel):\n    title: str = Field(..., min_length=1, max_length=200)\n    description: Optional[str] = None\n    views: int = Field(..., ge=0)\n    publishedAt: str\n    channel: Optional[str] = None\n\nclass ContentAnalysisRequest(BaseModel):\n    videos: List[VideoData]\n    analysis_type: str = "full"\n\n@app.get("/health")\nasync def health_check():\n    return {\n        "status": "healthy",\n        "timestamp": datetime.utcnow().isoformat(),\n        "component": "strategy-agent"\n    }\n\n@app.post("/analyze")\nasync def analyze_content(request: ContentAnalysisRequest):\n    try:\n        # Simplified response for testing\n        return {\n            "hook_patterns": [\n                {"type": "Question", "example": "Example question hook"}\n            ],\n            "format_trends": [\n                "Trend 1", \n                "Trend 2"\n            ],\n            "engagement_tactics": [\n                "Tactic 1", \n                "Tactic 2"\n            ],\n            "content_themes": [\n                "Theme 1", \n                "Theme 2"\n            ],\n            "summary": "This is a simplified analysis response for testing."\n        }\n    except Exception as e:\n        raise HTTPException(status_code=500, detail=str(e))' > /app/agents/simple_strategy_agent.py

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