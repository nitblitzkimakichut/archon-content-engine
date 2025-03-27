from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
import os
import sys
import importlib
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Add current directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)
    logger.debug(f"Added {current_dir} to Python path")

# Create FastAPI app
app = FastAPI(title="TitanFlow Content Creation API")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files if available
static_dir = os.path.join(current_dir, "static")
if os.path.exists(static_dir):
    app.mount("/test", StaticFiles(directory=static_dir), name="static")
    logger.info(f"Mounted static files at /test from {static_dir}")

# Agent modules configuration
agent_modules = {
    "/strategy": "simple_strategy_agent",
    "/script": "simple_scriptwriter_agent",
    "/visual": "simple_visual_planner_agent"
}

# Dictionary to track loaded agents
loaded_agents = {}

# Mount agent apps
agents_dir = os.path.join(current_dir, "agents")
if os.path.exists(agents_dir):
    logger.info(f"Found agents directory at {agents_dir}")
    for mount_path, module_name in agent_modules.items():
        module_path = os.path.join(agents_dir, f"{module_name}.py")
        if os.path.exists(module_path):
            try:
                logger.info(f"Loading agent module {module_name}")
                module = importlib.import_module(f"agents.{module_name}")
                app.mount(mount_path, module.app)
                loaded_agents[mount_path] = module_name
                logger.info(f"Successfully mounted {module_name} at {mount_path}")
            except Exception as e:
                logger.error(f"Failed to mount {module_name}: {str(e)}")
        else:
            logger.warning(f"Agent module {module_name} not found at {module_path}")
else:
    logger.warning("Agents directory not found")

# Health check endpoint
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "python_version": sys.version,
        "loaded_agents": loaded_agents
    }

# Root endpoint
@app.get("/")
async def root(request: Request):
    # If static files are available, redirect to test interface
    if os.path.exists(static_dir):
        return RedirectResponse(url="/test/index.html")
    
    # Otherwise return API info
    return {
        "app": "TitanFlow Content Creation API",
        "version": "1.0.0",
        "endpoints": {
            "strategy": "/strategy/analyze",
            "script": "/script/generate-script",
            "visual": "/visual/create-plan"
        },
        "documentation": "/docs"
    }

# Debug endpoint
@app.get("/debug")
async def debug():
    return {
        "python_path": sys.path,
        "current_directory": current_dir,
        "loaded_agents": loaded_agents,
        "static_directory": {
            "exists": os.path.exists(static_dir),
            "contents": os.listdir(static_dir) if os.path.exists(static_dir) else None
        },
        "agents_directory": {
            "exists": os.path.exists(agents_dir),
            "contents": os.listdir(agents_dir) if os.path.exists(agents_dir) else None
        },
        "environment": {
            key: value for key, value in os.environ.items() 
            if key.startswith(("PYTHON", "PORT", "OPENROUTER"))
        }
    }

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True) 