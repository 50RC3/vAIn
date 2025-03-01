from typing import Dict, Any
import logging
import sys
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from slowapi import Limiter
from slowapi.util import get_remote_address
import uvicorn
from core.module_manager import ModuleManager
from core.exceptions import ModuleInitializationError
from logging_config import setup_logging

# Import services
from services.p2p.network import P2PNetwork
from services.memory.manager import MemoryManager
from services.ai.orchestrator import AIOrchestrator


# Import API endpoints
from api.mobile_api import router as mobile_router
from api.federated_endpoints import create_federated_router
from services.api.endpoints.agi import router as agi_router
from services.api.endpoints.p2p import router as p2p_router
from services.api.endpoints.health import router as health_router

# Setup logging and rate limiting
setup_logging()
logger = logging.getLogger(__name__)
limiter = Limiter(key_func=get_remote_address)

# Initialize FastAPI app
app = FastAPI(
    title="vAIn API",
    description="Unified API for vAIn platform including P2P, AGI, and Mobile functionality",
    version="1.0.0"
)

# Static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# CORS with restricted origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://yourdomain.com"],  # Replace with actual domain
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["Authorization", "Content-Type"],
)

# Dependency Injection
module_manager = ModuleManager()
p2p_network = P2PNetwork()
memory_manager = MemoryManager()
ai_orchestrator = AIOrchestrator()

def get_p2p_network() -> P2PNetwork:
    return p2p_network

def get_ai_orchestrator() -> AIOrchestrator:
    return ai_orchestrator

# Register API routers
app.include_router(mobile_router, prefix="/mobile", tags=["Mobile"])
app.include_router(create_federated_router(), prefix="/federated", tags=["Federated Learning"])
app.include_router(agi_router, prefix="/agi", tags=["AGI"])
app.include_router(p2p_router, prefix="/p2p", tags=["P2P"])
app.include_router(health_router, prefix="/health", tags=["Health"])

# WebSocket Management
active_connections: Dict[str, WebSocket] = {}

@app.on_event("startup")
async def startup_event():
    """Initialize required services and validate dependencies."""
    try:
        module_manager.register_module('api', app)
        module_manager.register_module('p2p', p2p_network)
        module_manager.register_module('memory', memory_manager)
        module_manager.register_module('ai', ai_orchestrator)
        
        if not module_manager.validate_dependencies():
            raise ModuleInitializationError("Module dependency validation failed")
        
        logger.info("All services initialized successfully")
    except ModuleInitializationError as e:
        logger.error("Startup failed: %s", str(e))
        sys.exit(1)  # Graceful shutdown on startup failure

@app.on_event("shutdown")
async def shutdown_event():
    """Gracefully shut down services."""
    logger.info("Shutting down services...")
    await p2p_network.cleanup()
    await ai_orchestrator.shutdown()

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """Unified WebSocket endpoint for real-time updates with authentication."""
    await websocket.accept()
    client_id = str(id(websocket))
    active_connections[client_id] = websocket
    
    try:
        while True:
            data = await websocket.receive_json()
            if data.get("type") == "agi_update":
                await handle_agi_socket(websocket, data)
            elif data.get("type") == "p2p_message":
                await handle_p2p_socket(websocket, data)
    except WebSocketDisconnect:
        logger.info("Client disconnected: %s", client_id)
    except Exception as exc:
        logger.error("WebSocket error: %s", str(exc))
    finally:
        active_connections.pop(client_id, None)

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Global exception handler."""
    logger.error("Global error: %s", str(exc))
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error", "message": str(exc)}
    )

@app.get("/")
async def root():
    """Root endpoint showing API status."""
    return {
        "status": "online",
        "services": {
            "p2p": p2p_network.get_status(),
            "memory": memory_manager.get_status(),
            "ai": ai_orchestrator.get_status(),
        },
        "endpoints": {
            "mobile": "/mobile",
            "federated": "/federated",
            "agi": "/agi",
            "p2p": "/p2p",
            "health": "/health",
        }
    }

async def handle_agi_socket(websocket: WebSocket, data: Dict[str, Any]) -> None:
    """Handle AGI-related WebSocket messages."""
    await websocket.send_json({"status": "processing", "type": "agi_update"})

async def handle_p2p_socket(websocket: WebSocket, data: Dict[str, Any]) -> None:
    """Handle P2P-related WebSocket messages."""
    await websocket.send_json({"status": "processing", "type": "p2p_message"})

# AIOrchestrator class definition removed as it is imported from services.ai.orchestrator

class P2PNetwork:
    def __init__(self):
        # Initialization code
        pass

    async def cleanup(self):
        """Cleanup resources."""
        # Add cleanup code here
        pass

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
