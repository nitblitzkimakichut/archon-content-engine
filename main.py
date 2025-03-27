from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from agents.content_workflow_orchestrator import app as workflow_app
from agents.content_strategy_agent import app as strategy_app
from agents.content_scriptwriter_agent import app as script_app
from agents.visual_content_planner_agent import app as visual_app
from datetime import datetime
import os

app = FastAPI(
    title="Content Creation API",
    description="API for content creation workflow",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount the individual agent apps
app.mount("/workflow", workflow_app)
app.mount("/strategy", strategy_app)
app.mount("/script", script_app)
app.mount("/visual", visual_app)

@app.get("/")
async def root():
    return {
        "message": "Welcome to the Content Creation API",
        "endpoints": {
            "workflow": "/workflow/process-workflow",
            "strategy": "/strategy/analyze",
            "script": "/script/generate-script",
            "visual": "/visual/create-plan"
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint for Railway deployment"""
    try:
        # Basic application health check
        return {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "environment": "production" if os.getenv("RAILWAY_ENVIRONMENT") else "development",
            "version": "1.0.0"
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "timestamp": datetime.utcnow().isoformat(),
            "error": str(e)
        }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", "8000"))) 