import time
import logging
from fastapi import APIRouter, HTTPException, Depends, Request, BackgroundTasks, WebSocket, WebSocketDisconnect
from pydantic import BaseModel
from typing import Optional, Dict, Any
from ..dependencies import get_agi_service, get_current_user
from ..services.task_queue import enqueue_task, task_retry
from ..utils import validate_task_parameters
from ..auth import JWTBearer
from fastapi.responses import JSONResponse
from slowapi import Limiter
from slowapi.errors import RateLimitExceeded
import json

# Set up logging for this file
logger = logging.getLogger(__name__)

# Initialize rate limiter
limiter = Limiter()

router = APIRouter()

class AGIRequest(BaseModel):
    """Request schema for interacting with the AGI."""
    task: str
    parameters: Optional[Dict[str, Any]] = None  # Optional parameters for task execution

class AGIResponse(BaseModel):
    """Response schema from the AGI."""
    task: str
    result: Dict[str, Any]
    success: bool
    message: Optional[str] = None

class AGIConfigUpdate(BaseModel):
    """Request schema for updating AGI configurations."""
    config_key: str
    config_value: Any

class AGIErrorResponse(BaseModel):
    """Response schema for error handling."""
    detail: str
    code: int

@router.websocket("/ws/tasks")
async def websocket_tasks(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            # Simulate task updates being retrieved
            task_update = await get_task_update()  # Function to get the latest task update
            await websocket.send_text(json.dumps({"type": "taskUpdate", "payload": task_update}))
    except WebSocketDisconnect:
        print("Client disconnected")
        
# Middleware for logging requests and responses
@router.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all incoming requests and their response status."""
    logger.info(f"Request: {request.method} {request.url}")
    start_time = time.time()
    
    response = await call_next(request)
    
    process_time = time.time() - start_time
    logger.info(f"Response status: {response.status_code} - Time taken: {process_time:.4f}s")
    
    return response


# Custom exceptions for better error categorization
class TaskExecutionError(Exception):
    def __init__(self, task: str, message: str):
        self.task = task
        self.message = message

class ValidationError(Exception):
    def __init__(self, detail: str):
        self.detail = detail


# Rate limiting decorator with slowapi
@limiter.limit("5/minute")
@router.post("/execute", response_model=AGIResponse, responses={429: {"model": AGIErrorResponse}})
async def execute_task(request: AGIRequest, background_tasks: BackgroundTasks, agi_service=Depends(get_agi_service)):
    """
    Execute a task using the AGI system.
    
    Parameters:
    - task: The task to execute (e.g., "generate_plan", "analyze_data").
    - parameters: Optional parameters for the task.
    
    Returns:
    - AGIResponse: Result of the task execution.
    """
    try:
        # Validate parameters before processing
        validate_task_parameters(request.task, request.parameters)
        
        # Enqueue the task for background processing (asynchronous)
        background_tasks.add_task(enqueue_task, request.task, request.parameters, agi_service)
        
        logger.info(f"Task {request.task} started.")
        
        return AGIResponse(
            task=request.task,
            result={},
            success=True,
            message="Task is being processed in the background."
        )
    
    except RateLimitExceeded:
        logger.error("Rate limit exceeded for task execution.")
        raise HTTPException(status_code=429, detail="Too many requests. Please try again later.")
    
    except ValidationError as e:
        logger.error(f"Validation error: {e.detail}")
        raise HTTPException(status_code=400, detail=f"Validation failed: {e.detail}")
    
    except TaskExecutionError as e:
        logger.error(f"Task execution failed for {e.task}: {e.message}")
        raise HTTPException(status_code=500, detail=f"Task execution failed: {e.message}")
    
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")


@router.get("/status", response_model=Dict[str, Any])
async def get_agi_status(agi_service=Depends(get_agi_service)):
    """
    Fetch the current status of the AGI system.
    
    Returns:
    - Status: Current status and metrics of the AGI.
    """
    try:
        status = agi_service.get_cached_status()
        if not status:
            status = agi_service.get_status()
            agi_service.cache_status(status)  # Cache the status to optimize future requests
        
        return status
    
    except Exception as e:
        logger.error(f"Failed to fetch AGI status: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch AGI status: {str(e)}")


@router.put("/config", response_model=Dict[str, Any])
async def update_agi_config(update: AGIConfigUpdate, agi_service=Depends(get_agi_service)):
    """
    Update the configuration of the AGI system dynamically.
    
    Parameters:
    - config_key: Key of the configuration to update.
    - config_value: New value for the configuration.
    
    Returns:
    - Updated configuration.
    """
    try:
        updated_config = agi_service.update_config(update.config_key, update.config_value)
        return {"success": True, "updated_config": updated_config}
    except KeyError:
        logger.error(f"Configuration key not found: {update.config_key}")
        raise HTTPException(status_code=404, detail="Configuration key not found.")
    except Exception as e:
        logger.error(f"Failed to update configuration: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to update configuration: {str(e)}")


@router.websocket("/notifications")
async def websocket_notifications(websocket: WebSocket, agi_service=Depends(get_agi_service)):
    """
    WebSocket for real-time task notifications.
    
    This allows clients to receive updates on task progress or completion in real time.
    """
    await websocket.accept()
    
    try:
        while True:
            # Check for updates or task status
            task_updates = agi_service.get_task_updates()
            await websocket.send_text(task_updates)
            
            await asyncio.sleep(5)  # Update every 5 seconds
    
    except WebSocketDisconnect:
        logger.info("Client disconnected from WebSocket.")
    

@router.post("/retry-task")
async def retry_task(task_id: str, background_tasks: BackgroundTasks, agi_service=Depends(get_agi_service)):
    """
    Retry a failed task using an exponential backoff strategy.
    
    Parameters:
    - task_id: The ID of the task to retry.
    
    Returns:
    - Success message or error.
    """
    try:
        # Retry task with exponential backoff
        result = await task_retry(task_id, agi_service)
        
        return {"success": True, "message": f"Task {task_id} retried successfully."}
    
    except Exception as e:
        logger.error(f"Task retry failed for {task_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Task retry failed: {str(e)}")
