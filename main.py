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
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0"
    }

if __name__ == "__main__":
    import uvicorn
    # Get port from environment variable with fallback to 8000
    port = int(os.environ.get("PORT", "8000"))
    uvicorn.run(app, host="0.0.0.0", port=port) 