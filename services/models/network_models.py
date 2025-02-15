
from pydantic import BaseModel, validator
from typing import Dict, Any, Optional

class Peer(BaseModel):
    """Schema for storing peer node details."""
    node_id: str
    ip_address: str
    port: int
    last_seen: Optional[float] = None
    status: str = "active"

class TaskRequest(BaseModel):
    """Schema for incoming task requests in the P2P network."""
    task_id: str
    task_name: str
    parameters: Dict[str, Any]
    target_node_id: str
    retry_count: int = 0
    timestamp: Optional[float] = None

    @validator('parameters')
    def validate_params(cls, v):
        if not isinstance(v, dict):
            raise ValueError('Parameters must be a dictionary')
        return v

class TaskResponse(BaseModel):
    """Schema for task responses to peers."""
    task_id: str
    task_name: str
    result: Dict[str, Any]
    success: bool
    message: str
    timestamp: Optional[float] = None
