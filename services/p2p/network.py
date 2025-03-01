"""
P2P networking service for distributed communication.

This module provides peer-to-peer networking capabilities for the vAIn platform,
including secure message passing, peer discovery, and distributed task management.
"""

from typing import Dict, List, Any, Optional, Tuple
import json
import asyncio
from datetime import datetime

try:
    # Third-party imports
    import aiofiles
    from cryptography.fernet import Fernet
    import websockets
    from fastapi import HTTPException
    from pydantic import BaseModel, validator
except ImportError as e:
    raise ImportError(
        "Required package not found. Please run: "
        "'pip install aiofiles cryptography websockets'"
    ) from e

# Change relative imports to absolute imports
from services.utils.validators import validate_task_parameters
from services.utils.logger import setup_logger
from services.utils.crypto import encrypt_message

# Initialize logger and encryption
logger = setup_logger(__name__)
encryption_key = Fernet.generate_key()
cipher = Fernet(encryption_key)

class Peer(BaseModel):
    """Schema for storing peer node details."""
    node_id: str
    ip_address: str
    port: int

class TaskRequest(BaseModel):
    """Schema for incoming task requests in the P2P network."""
    task_name: str
    parameters: Dict[str, Any]
    target_node_id: str
    retry_count: int = 0

    @classmethod
    @validator("parameters")
    def validate_params(cls, value: Dict[str, Any]) -> Dict[str, Any]:
        """Validate task parameters."""
        if not isinstance(value, dict):
            raise ValueError("Parameters must be a dictionary")
        return value

class TaskResponse(BaseModel):
    """Schema for task responses to peers."""
    task_name: str
    result: Dict[str, Any]
    success: bool
    message: str

# Network configuration
WEBSOCKET_TIMEOUT = 30  # seconds
MAX_RETRIES = 3  # maximum number of retry attempts
_node_registry: Dict[str, Dict[str, Any]] = {}

async def get_task_details(task_id: str) -> Optional[Dict[str, Any]]:
    """Retrieve task details from storage."""
    try:
        async with aiofiles.open(f"tasks/{task_id}.json", mode='r') as f:
            content = await f.read()
            return json.loads(content)
    except FileNotFoundError:
        return None
    except (json.JSONDecodeError, IOError) as e:
        logger.error("Error retrieving task details: %s", str(e))
        return None

async def task_retry(task_id: str) -> Tuple[bool, Dict[str, Any]]:
    """Implement task retry logic with backoff mechanism."""
    attempt = 0
    while attempt < MAX_RETRIES:
        try:
            task_details = await get_task_details(task_id)
            if not task_details:
                return False, {"error": "Task not found"}

            async with websockets.connect(
                f"ws://{task_details['peer_ip']}:{task_details['peer_port']}"
            ) as websocket:
                await secure_send(
                    websocket, 
                    task_details["task_request"]
                )
                response = await secure_receive(websocket)
                if response:
                    return True, response

            await asyncio.sleep(2 ** attempt)
            attempt += 1

        except (
            websockets.exceptions.WebSocketException,
            asyncio.TimeoutError
        ) as e:
            logger.warning(
                "Retry attempt %d failed: %s",
                attempt + 1,
                str(e)
            )
            continue

    return False, {"error": f"Task failed after {MAX_RETRIES} attempts"}

# --- Network Communication Functions ---
async def secure_send(
    websocket: websockets.WebSocketServerProtocol, 
    message: Dict[str, Any]
) -> None:
    """Securely sends a message to a peer node via WebSocket."""
    try:
        encrypted_message = encrypt_message(message)
        await asyncio.wait_for(
            websocket.send(encrypted_message),
            timeout=WEBSOCKET_TIMEOUT
        )
        logger.info("Message sent successfully")
    except asyncio.TimeoutError as exc:
        logger.error("Connection timeout")
        raise HTTPException(
            status_code=504, 
            detail="Connection timeout"
        ) from exc
    except websockets.exceptions.WebSocketException as exc:
        logger.error("WebSocket error: %s", str(exc))
        raise HTTPException(
            status_code=503, 
            detail="WebSocket connection failed"
        ) from exc
    except Exception as exc:
        logger.error("Failed to send message: %s", str(exc))
        raise HTTPException(
            status_code=500, 
            detail="Internal server error"
        ) from exc

async def secure_receive(websocket: websockets.WebSocketServerProtocol) -> Dict[str, Any]:
    """
    Receives a message securely from a peer node via WebSocket.
    
    Args:
    - websocket: The active WebSocket connection
    
    Returns:
    - message (decrypted): The decrypted message
    """
    try:
        encrypted_message = await websocket.recv()
        decrypted_message = cipher.decrypt(encrypted_message).decode()
        return json.loads(decrypted_message)
    except websockets.exceptions.WebSocketException as e:
        logger.error("WebSocket error: %s", str(e))
        raise HTTPException(status_code=503, detail="WebSocket error") from e
    except json.JSONDecodeError as e:
        logger.error("JSON decode error: %s", str(e))
        raise HTTPException(status_code=400, detail="Invalid message format") from e
    except ValueError as e:
        logger.error("Value error: %s", str(e))
        raise HTTPException(status_code=400, detail="Invalid data") from e

async def peer_heartbeat(peer_ip: str, peer_port: int) -> bool:
    """
    Check if the peer node is responsive by sending a heartbeat message.
    
    Args:
    - peer_ip: IP address of the peer node
    - peer_port: Port of the peer node
    
    Returns:
    - True if the peer is responsive, False otherwise
    """
    try:
        async with websockets.connect(f"ws://{peer_ip}:{peer_port}") as websocket:
            await websocket.send(json.dumps({"heartbeat": "ping"}))
            response = await websocket.recv()
            if response == '{"heartbeat": "pong"}':
                logger.info("Peer %s:%d is healthy.", peer_ip, peer_port)
                return True
            else:
                logger.warning("Unexpected response from %s:%d", peer_ip, peer_port)
                return False
    except Exception as e:
        logger.error("Peer %s:%d is unreachable. Error: %s", peer_ip, peer_port, str(e))
        return False

# --- Node Management Functions ---
def get_peers() -> List['Peer']:
    """
    Get list of registered peers from the node registry.
    
    Returns:
    - List[Peer]: List of registered peers
    """
    return [Peer(node_id=node_id, **details) for node_id, details in _node_registry.items()]

async def register_new_peer(peer: Peer) -> None:
    """
    Register a new peer in the network.
    
    Args:
    - peer: Peer object containing node information
    
    Returns:
    - None
    """
    try:
        # Register the peer in the node registry
        _node_registry[peer.node_id] = {
            "ip_address": peer.ip_address,
            "port": peer.port
        }
        logger.info("Node %s registered successfully at %s:%d.", peer.node_id, peer.ip_address, peer.port)
    except Exception as e:
        logger.error("Failed to register node %s: %s", peer.node_id, str(e))
        raise HTTPException(status_code=500, detail=f"Failed to register node {peer.node_id}: {str(e)}") from e

async def discover_peers() -> List[Peer]:
    """
    Discover peers in the network.
    
    Returns:
    - List of available peers
    """
    try:
        peers = get_peers()  # Fetch the list of peers from the registry
        logger.info("Discovered %d peers in the network.", len(peers))
        return peers
    except Exception as e:
        logger.error("Failed to discover peers: %s", str(e))
        raise HTTPException(status_code=500, detail="Failed to discover peers.") from e

# --- Task Distribution and Management ---
async def distribute_task_to_peer(task_request: TaskRequest, peer_ip: str, peer_port: int) -> Optional[TaskResponse]:
    """
    Distribute task to a peer and get the result.
    
    Args:
    - task_request: The task request to send to the peer
    - peer_ip: IP address of the peer node
    - peer_port: Port of the peer node
    
    Returns:
    - TaskResponse: The response from the peer after processing the task
    """
    try:
        async with websockets.connect(f"ws://{peer_ip}:{peer_port}", timeout=10) as websocket:
            await secure_send(websocket, task_request.dict())
            response = await secure_receive(websocket)
            if response:
                return TaskResponse(**response)
    except websockets.exceptions.WebSocketException as e:
        logger.error("WebSocket error with peer %s:%d: %s", peer_ip, peer_port, str(e))
    except Exception as e:
        logger.error("Error in task distribution: %s", str(e))
    return None

async def retry_failed_task(task_id: str) -> Dict[str, Any]:
    """
    Retry a failed task.
    
    Args:
    - task_id: The task ID that needs to be retried
    
    Returns:
    - Dict: Status of the retry operation
    """
    try:
        success, retry_result = await task_retry(task_id)
        if success:
            logger.info("Task %s has been retried successfully", task_id)
            return {"status": "success", "message": f"Task {task_id} retried successfully"}
        return {"status": "failed", "message": retry_result.get("error", "Unknown error")}
    except (ValueError, KeyError) as e:
        logger.error("Failed to retry task %s: %s", task_id, str(e))
        return {"status": "failed", "message": str(e)}

# --- Example of Broadcasting a Message to All Peers ---
async def broadcast_message(
    message: Dict[str, Any], 
    exclude_peer: Optional[Peer] = None
) -> None:
    """Broadcast a message to all peers except a specific one."""
    peers = await discover_peers()
    for peer in peers:
        if exclude_peer and peer.node_id == exclude_peer.node_id:
            continue
        try:
            # Create WebSocket connection for each peer
            uri = f"ws://{peer.ip_address}:{peer.port}"
            async with websockets.connect(uri) as websocket:
                await secure_send(websocket, message)
                logger.info(
                    "Broadcast message to %s at %s:%d",
                    peer.node_id, 
                    peer.ip_address, 
                    peer.port
                )
        except websockets.exceptions.WebSocketException as e:
            logger.error(
                "Failed to broadcast to %s: %s", 
                peer.node_id, 
                str(e)
            )

# --- Task Scheduling Integration ---
async def schedule_task(task_name: str) -> None:
    """
    Schedule a single task execution.
    
    Args:
        task_name: The name of the task to schedule
    
    Raises:
        HTTPException: If task scheduling fails
        ValueError: If no peers are available
    """
    try:
        # Get available peers and resource requirements
        peers = await discover_peers()
        if not peers:
            raise ValueError("No peers available for task distribution")

        # Create task request with validation
        task_request = TaskRequest(
            task_name=task_name,
            parameters={},
            target_node_id="",
            retry_count=0
        )
        
        # Validate task parameters
        validate_task_parameters(task_name, task_request.parameters)

        # Find best peer based on resource availability
        for peer in peers:
            try:
                if await peer_heartbeat(peer.ip_address, peer.port):
                    response = await distribute_task_to_peer(
                        task_request,
                        peer.ip_address,
                        peer.port
                    )
                    if response and response.success:
                        return
            except websockets.exceptions.WebSocketException as e:
                logger.warning(
                    "Failed to distribute task to %s: %s",
                    peer.node_id,
                    str(e)
                )
                continue

        # If all peers fail, attempt retry
        await retry_failed_task(task_name)
        logger.info("Scheduling task: %s", task_name)

    except ValueError as e:
        logger.error("Error scheduling task %s: %s", task_name, str(e))
        raise HTTPException(status_code=503, detail=str(e)) from e
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Unexpected error in task %s: %s", task_name, str(e))
        raise HTTPException(
            status_code=500,
            detail="Internal server error"
        ) from e

async def schedule_task_periodically(task_name: str, interval: int) -> None:
    """
    Schedule a task to run periodically at a specific interval.
    
    Args:
    - task_name: The name of the task
    - interval: Interval (in seconds) between task executions
    
    Returns:
    - None
    """
    try:
        while True:
            await schedule_task(task_name)
            await asyncio.sleep(interval)
    except Exception as e:
        logger.error("Error scheduling task %s periodically: %s", task_name, str(e))

from dataclasses import dataclass

@dataclass
class Route:
    """Network route information."""
    id: str
    source: str
    destination: str
    weight: float = 1.0

@dataclass
class PheromoneMarker:
    """Pheromone marker for route optimization."""
    timestamp: datetime
    route: Route
    strength: float = 1.0

async def deposit_marker(route_id: str, marker: PheromoneMarker) -> None:
    """Deposit a pheromone marker on a network route."""
    # Placeholder for actual implementation
    logger.info("Deposited marker on route %s with strength %f", route_id, marker.strength)

async def leave_pheromone_trail(route: Route) -> None:
    """Leave a pheromone marker on a network route."""
    marker = PheromoneMarker(
        timestamp=datetime.now(),
        route=route
    )
    await deposit_marker(route.id, marker)

class P2PNetwork:
    """Manages peer-to-peer network connections."""
    
    def __init__(self):
        """Initialize P2P network manager."""
        self.peers = set()
        self.cipher = cipher
        
    async def start(self):
        """Start the P2P network service."""
        logger.info("Starting P2P network service")
