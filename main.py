from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
import os
import sys
import importlib.util
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Add the current directory to the Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)
logger.info(f"Added current directory to path: {current_dir}")
logger.info(f"Python path: {sys.path}")
logger.info(f"Contents of current directory: {os.listdir(current_dir)}")

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

# Create a simple FastAPI app to use if agent modules are not available
simple_app = FastAPI()

@simple_app.get("/health")
async def simple_health():
    return {"status": "healthy", "component": "simple-app"}

@simple_app.post("/process")
async def simple_process():
    return {"result": "This is a placeholder response"}

# Try to import agent apps
agents_loaded = False
loaded_agents = []

try:
    # Check if the agents directory exists
    agents_dir = os.path.join(current_dir, "agents")
    if os.path.exists(agents_dir):
        logger.info(f"Agents directory exists: {agents_dir}")
        logger.info(f"Contents of agents directory: {os.listdir(agents_dir)}")
        
        # Try to load the simplified agent
        try:
            # First try to import the simple strategy agent
            from agents.simple_strategy_agent import app as strategy_app
            app.mount("/strategy", strategy_app)
            loaded_agents.append("strategy")
            logger.info("Successfully loaded simple_strategy_agent")
            agents_loaded = True
        except ImportError as e:
            logger.warning(f"Could not import simple_strategy_agent: {e}")
            app.mount("/strategy", simple_app)
            
        # Mount placeholder apps for other agents
        app.mount("/workflow", simple_app)
        app.mount("/script", simple_app)
        app.mount("/visual", simple_app)
    else:
        logger.error(f"Agents directory does not exist!")
except Exception as e:
    logger.error(f"Error when checking agents directory: {e}")
    app.mount("/strategy", simple_app)
    app.mount("/workflow", simple_app)
    app.mount("/script", simple_app)
    app.mount("/visual", simple_app)

@app.get("/")
async def root():
    if agents_loaded:
        return {
            "message": "Welcome to the Content Creation API",
            "status": "Partial functionality available",
            "loaded_agents": loaded_agents,
            "endpoints": {
                "workflow": "/workflow/process",
                "strategy": "/strategy/analyze",
                "script": "/script/process",
                "visual": "/visual/process"
            }
        }
    else:
        return {
            "message": "Welcome to the Content Creation API",
            "status": "Limited functionality - Agent modules not loaded",
            "available_endpoints": ["/health"],
            "debug_info": {
                "python_path": sys.path,
                "current_directory": current_dir,
                "agents_directory_exists": os.path.exists(os.path.join(current_dir, "agents"))
            }
        }

@app.get("/debug")
async def debug_info():
    """Endpoint to get debug information"""
    try:
        agents_dir = os.path.join(current_dir, "agents")
        agents_dir_exists = os.path.exists(agents_dir)
        
        return {
            "python_path": sys.path,
            "current_directory": current_dir,
            "files_in_current_dir": os.listdir(current_dir),
            "agents_directory_exists": agents_dir_exists,
            "agents_directory": agents_dir,
            "files_in_agents_dir": os.listdir(agents_dir) if agents_dir_exists else None,
            "agents_loaded": agents_loaded,
            "loaded_agents": loaded_agents
        }
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    port = int(os.environ.get("PORT", "8000"))
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=port) 