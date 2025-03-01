"""
AGI API endpoints for task execution, system monitoring and configuration.
Provides interfaces for AGI interactions and federated learning coordination.
"""

import asyncio
import json
from typing import Dict, Optional, Any

from fastapi import APIRouter, HTTPException, BackgroundTasks, WebSocket, WebSocketDisconnect
from pydantic import BaseModel
from slowapi import Limiter
from slowapi.errors import RateLimitExceeded

from services.api.dependencies import get_agi_service
from services.api.task_queue import enqueue_task, task_retry
try:
    from services.utils.validators import validate_task_parameters
except ImportError:
    raise ImportError("Module 'services.utils.validators' not found. Ensure it exists and is correctly named.")

# Set up logging and rate limiting
logger = logging.getLogger(__name__)
limiter = Limiter(key_func=lambda: "default")
router = APIRouter()

class AGIRequest(BaseModel):
    """Request schema for interacting with the AGI."""
    task: str
    parameters: Optional[Dict[str, Any]] = None

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

async def get_task_update():
    """Retrieve the latest task update."""
    await asyncio.sleep(1)
    return {"task_id": "123", "status": "in_progress"}

@router.websocket("/ws/tasks")
async def websocket_tasks(websocket: WebSocket):
    """Handle WebSocket connections for real-time task updates."""
    await websocket.accept()
    try:
        while True:
            task_update = await get_task_update()
            await websocket.send_text(json.dumps({
                "type": "taskUpdate",
                "payload": task_update
            }))
    except WebSocketDisconnect:
        logger.info("Client disconnected")

@limiter.limit("5/minute")
@router.post("/execute", response_model=AGIResponse)
async def execute_task(
    request: AGIRequest,
    background_tasks: BackgroundTasks,
    agi_service=Depends(get_agi_service)
):
    """
    Execute a task using the AGI system.

    Args:
        request: The task request containing task name and parameters
        background_tasks: FastAPI background tasks handler
        agi_service: AGI service instance

    Returns:
        AGIResponse: Result of the task execution
    """
    try:
        validate_task_parameters(request.task, request.parameters)
        
        logger.info("Task %s started", request.task)
        background_tasks.add_task(enqueue_task, request.task, request.parameters, agi_service)
        
        return AGIResponse(
            task=request.task,
            result={},
            success=True,
            message="Task is being processed in the background."
        )
    
    except RateLimitExceeded as exc:
        logger.error("Rate limit exceeded for task execution")
        raise HTTPException(
            status_code=429,
            detail="Too many requests. Please try again later."
        ) from exc
    
    except ValidationError as e:
        logger.error("Validation error: %s", e.detail)
        raise HTTPException(
            status_code=400,
            detail="Validation failed: %s" % e.detail
        ) from e
    
    except TaskExecutionError as e:
        logger.error("Task execution failed for %s: %s", e.task, e.message)
        raise HTTPException(
            status_code=500,
            detail="Task execution failed: %s" % e.message
        ) from e
    
    except Exception as e:
        logger.error("Unexpected error: %s", str(e))
        raise HTTPException(
            status_code=500,
            detail="Unexpected error: %s" % str(e)
        ) from e

@router.get("/status")
async def get_agi_status(agi_service=Depends(get_agi_service)):
    """Get current AGI system status."""
    try:
        status = agi_service.get_cached_status()
        if not status:
            status = agi_service.get_status()
            agi_service.cache_status(status)
        return status
    
    except Exception as e:
        logger.error("Failed to fetch AGI status: %s", str(e))
        raise HTTPException(
            status_code=500,
            detail="Failed to fetch AGI status: %s" % str(e)
        ) from e

@router.put("/config")
async def update_agi_config(update: AGIConfigUpdate, agi_service=Depends(get_agi_service)):
    """Update AGI system configuration."""
    try:
        updated_config = agi_service.update_config(update.config_key, update.config_value)
        return {"success": True, "updated_config": updated_config}
    
    except KeyError as exc:
        logger.error("Configuration key not found: %s", update.config_key)
        raise HTTPException(
            status_code=404,
            detail="Configuration key not found."
        ) from exc
    
    except Exception as e:
        logger.error("Failed to update configuration: %s", str(e))
        raise HTTPException(
            status_code=500,
            detail="Failed to update configuration: %s" % str(e)
        ) from e

@router.post("/retry-task")
async def retry_task(task_id: str, agi_service=Depends(get_agi_service)):
    """
    Retry a failed task.
    
    Args:
        task_id: ID of the task to retry
        agi_service: AGI service instance
    """
    try:
        await task_retry(task_id, agi_service)
        return {"success": True, "message": "Task %s retried successfully" % task_id}
    
    except Exception as e:
        logger.error("Task retry failed for %s: %s", task_id, str(e))
        raise HTTPException(
            status_code=500,
            detail="Task retry failed: %s" % str(e)
        ) from e
