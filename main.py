from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
import os
import sys
import importlib
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)
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

# Create simple FastAPI apps for each route
def create_simple_app(name):
    simple_app = FastAPI()
    
    @simple_app.get("/health")
    async def simple_health():
        return {"status": "healthy", "component": f"simple-{name}-app"}
    
    @simple_app.post("/process")
    async def simple_process():
        return {"result": f"This is a placeholder response for {name}"}
    
    return simple_app

# Initialize agents info
agents_info = {}
agents_loaded = False

# Mount agent apps
try:
    # Log the content of the agents directory
    agents_dir = os.path.join(current_dir, "agents")
    agents_dir_exists = os.path.exists(agents_dir)
    logger.info(f"Agents directory exists: {agents_dir_exists}")
    
    if agents_dir_exists:
        logger.info(f"Contents of agents directory: {os.listdir(agents_dir)}")
        
        # Create a file list for all Python files in agents directory
        agent_files = [f for f in os.listdir(agents_dir) if f.endswith('.py') and f != '__init__.py']
        logger.info(f"Python files in agents directory: {agent_files}")
        
        # Try to import simple_strategy_agent
        try:
            # Check if file exists first
            agent_path = os.path.join(agents_dir, "simple_strategy_agent.py")
            if os.path.exists(agent_path):
                logger.info(f"simple_strategy_agent.py exists at {agent_path}")
                
                # Dynamically import the module
                spec = importlib.util.spec_from_file_location("agents.simple_strategy_agent", agent_path)
                simple_strategy = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(simple_strategy)
                
                # Mount the app
                app.mount("/strategy", simple_strategy.app)
                agents_info["strategy"] = {"status": "loaded", "type": "simple"}
                agents_loaded = True
                logger.info("Successfully loaded simple_strategy_agent module")
            else:
                logger.warning(f"simple_strategy_agent.py not found at {agent_path}")
                app.mount("/strategy", create_simple_app("strategy"))
                agents_info["strategy"] = {"status": "fallback", "reason": "file_not_found"}
        except Exception as e:
            logger.error(f"Error importing simple_strategy_agent: {str(e)}", exc_info=True)
            app.mount("/strategy", create_simple_app("strategy"))
            agents_info["strategy"] = {"status": "error", "error": str(e)}
        
        # Mount placeholder apps for other routes
        app.mount("/workflow", create_simple_app("workflow"))
        app.mount("/script", create_simple_app("script"))
        app.mount("/visual", create_simple_app("visual"))
        agents_info.update({
            "workflow": {"status": "placeholder"},
            "script": {"status": "placeholder"},
            "visual": {"status": "placeholder"}
        })
    else:
        logger.error("Agents directory does not exist!")
        for route in ["strategy", "workflow", "script", "visual"]:
            app.mount(f"/{route}", create_simple_app(route))
            agents_info[route] = {"status": "error", "reason": "agents_directory_missing"}
except Exception as e:
    logger.error(f"Error during agent mounting: {str(e)}", exc_info=True)
    for route in ["strategy", "workflow", "script", "visual"]:
        app.mount(f"/{route}", create_simple_app(route))
        agents_info[route] = {"status": "error", "reason": "mount_exception", "error": str(e)}

@app.get("/")
async def root():
    return {
        "message": "Welcome to the Content Creation API",
        "status": "Agents loaded" if agents_loaded else "Limited functionality - Agent modules not loaded",
        "agents_info": agents_info,
        "endpoints": {
            "health": "/health",
            "debug": "/debug",
            "strategy": "/strategy/analyze" if agents_info.get("strategy", {}).get("status") == "loaded" else "/strategy/health",
            "workflow": "/workflow/health",
            "script": "/script/health",
            "visual": "/visual/health"
        }
    }

@app.get("/debug")
async def debug_info():
    """Endpoint to get debug information"""
    try:
        agents_dir = os.path.join(current_dir, "agents")
        agents_dir_exists = os.path.exists(agents_dir)
        agent_files = []
        
        if agents_dir_exists:
            agent_files = os.listdir(agents_dir)
        
        # Get file content of simple_strategy_agent.py
        agent_content = None
        agent_path = os.path.join(agents_dir, "simple_strategy_agent.py")
        if os.path.exists(agent_path):
            try:
                with open(agent_path, 'r') as f:
                    agent_content = f.read()[:100] + "..." # Just get the first 100 chars
            except Exception as e:
                agent_content = f"Error reading file: {str(e)}"
        
        return {
            "python_path": sys.path,
            "current_directory": current_dir,
            "files_in_current_dir": os.listdir(current_dir),
            "agents_directory_exists": agents_dir_exists,
            "agents_directory": agents_dir,
            "files_in_agents_dir": agent_files,
            "agents_loaded": agents_loaded,
            "agents_info": agents_info,
            "simple_strategy_exists": os.path.exists(agent_path),
            "simple_strategy_preview": agent_content
        }
    except Exception as e:
        return {"error": str(e), "traceback": logging.traceback.format_exc()}

if __name__ == "__main__":
    port = int(os.environ.get("PORT", "8000"))
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=port) 