from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Any, List

from roadman_mind.core import config
from roadman_mind.core.plugins import load_plugins, get_all_routes, PLUGIN_REGISTRY
from roadman_mind.core.logger import setup_logger, logger

# --- Application Setup ---

# Initialize logger
setup_logger()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    A lifespan context manager for FastAPI to handle startup and shutdown events.
    """
    # --- Startup ---
    logger.info("Bootstrapping FastAPI server...")
    load_plugins()
    logger.info(f"Loaded {len(PLUGIN_REGISTRY)} plugins for API.")
    logger.info("FastAPI server has started and is ready to accept requests.")

    yield

    # --- Shutdown ---
    logger.info("FastAPI server is shutting down.")

# Create the FastAPI application instance with the lifespan manager
app = FastAPI(
    title=config.APP_NAME,
    description=config.DESCRIPTION,
    version=config.VERSION,
    lifespan=lifespan
)

# --- Pydantic Models ---

class RunRequest(BaseModel):
    name: str

class RouteInfo(BaseModel):
    name: str
    description: str

class RoutesResponse(BaseModel):
    routes: List[RouteInfo]

class RunResponse(BaseModel):
    route: str
    status: str
    result: Any

# --- API Endpoints ---

@app.get("/routes",
         response_model=RoutesResponse,
         summary="List all available plugin routes")
def list_plugin_routes():
    """
    Retrieves a list of all registered plugin commands (routes),
    including their names and descriptions.
    """
    routes = get_all_routes()
    route_list = [
        RouteInfo(name=name, description=func.__doc__ or "No description available.")
        for name, func in routes.items()
    ]
    return RoutesResponse(routes=route_list)

@app.post("/run",
          response_model=RunResponse,
          summary="Execute a plugin route")
def run_plugin_route(request: RunRequest):
    """
    Executes a specific plugin command (route) by its full name
    (e.g., 'sys:cpu_percent').
    """
    routes = get_all_routes()
    handler = routes.get(request.name)

    if not handler:
        raise HTTPException(
            status_code=404,
            detail=f"Route '{request.name}' not found. Use GET /routes to see available routes."
        )

    try:
        logger.info(f"Executing API route: {request.name}")
        result = handler()
        return RunResponse(route=request.name, status="success", result=result)
    except Exception as e:
        logger.error(f"API route execution failed for '{request.name}': {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred while executing route '{request.name}': {str(e)}"
        )
