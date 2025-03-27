from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
import os
import sys

# Add the current directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

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

# Important: Create health route before mounting sub-apps
@app.get("/health")
async def health_check():
    """Health check endpoint for Railway deployment"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0"
    }

# Try to import agent apps
try:
    from agents.content_workflow_orchestrator import app as workflow_app
    from agents.content_strategy_agent import app as strategy_app
    from agents.content_scriptwriter_agent import app as script_app
    from agents.visual_content_planner_agent import app as visual_app
    
    # Mount the individual agent apps
    app.mount("/workflow", workflow_app)
    app.mount("/strategy", strategy_app)
    app.mount("/script", script_app)
    app.mount("/visual", visual_app)
    
    agents_loaded = True
except ImportError as e:
    print(f"Warning: Could not import agent modules: {e}")
    agents_loaded = False

@app.get("/")
async def root():
    if agents_loaded:
        return {
            "message": "Welcome to the Content Creation API",
            "endpoints": {
                "workflow": "/workflow/process-workflow",
                "strategy": "/strategy/analyze",
                "script": "/script/generate-script",
                "visual": "/visual/create-plan"
            }
        }
    else:
        return {
            "message": "Welcome to the Content Creation API",
            "status": "Limited functionality - Agent modules not loaded",
            "available_endpoints": ["/health"]
        }

if __name__ == "__main__":
    port = int(os.environ.get("PORT", "8000"))
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=port) 