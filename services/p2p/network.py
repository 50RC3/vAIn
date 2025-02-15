import logging
import asyncio
import json
import websockets
from cryptography.fernet import Fernet
from fastapi import HTTPException

from typing import List, Dict, Any, Optional, Tuple
from ..utils.validators import validate_task_parameters
from ..utils.logger import setup_logger
from ..utils.crypto import encrypt_message, decrypt_message
from ..models.network_models import Peer, TaskRequest, TaskResponse
from ..config import WEBSOCKET_TIMEOUT, MAX_RETRIES

# Initialize logger
logger = setup_logger(__name__)

# Encryption key for secure communication
encryption_key = Fernet.generate_key()
cipher = Fernet(encryption_key)

# --- Network Configuration ---
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
    retry_count: int = 0  # Number of retries attempted

    @validator('parameters')
    def validate_params(cls, v):
        if not isinstance(v, dict):
            raise ValueError('Parameters must be a dictionary')
        return v

class TaskResponse(BaseModel):
    """Schema for task responses to peers."""
    task_name: str
    result: Dict[str, Any]
    success: bool
    message: str

async def task_retry(task_id: str) -> Tuple[bool, Dict[str, Any]]:
    """
    Implement task retry logic with backoff mechanism.
    
    Args:
    - task_id: The ID of the task to retry
    
    Returns:
    - Tuple[bool, Dict]: Success status and result/error message
    """
    try:
        attempt = 0
        while attempt < MAX_RETRIES:
            try:
                # Get task details from storage
                task_details = await get_task_details(task_id)
                if not task_details:
                    return False, {"error": "Task not found"}

                # Attempt to execute the task
                result = await distribute_task_to_peer(
                    task_details["task_request"],
                    task_details["peer_ip"],
                    task_details["peer_port"]
                )
                
                if result and result.success:
                    return True, result.dict()
                
                # Exponential backoff
                await asyncio.sleep(2 ** attempt)
                attempt += 1
                
            except Exception as e:
                logger.warning(f"Retry attempt {attempt + 1} failed: {str(e)}")
                continue
                
        return False, {"error": f"Task failed after {MAX_RETRIES} attempts"}
        
    except Exception as e:
        logger.error(f"Error in task retry: {str(e)}")
        return False, {"error": str(e)}

# --- Network Communication Functions ---
async def secure_send(peer_ip: str, peer_port: int, message: Dict[str, Any]) -> None:
    """
    Securely sends a message to a peer node via WebSocket.
    
    Args:
    - peer_ip: IP address of the peer node
    - peer_port: Port of the peer node
    - message: The message to send (dictionary format)
    
    Returns:
    - None
    """
    try:
        uri = f"ws://{peer_ip}:{peer_port}"
        async with websockets.connect(uri, timeout=WEBSOCKET_TIMEOUT) as websocket:
            encrypted_message = encrypt_message(message)
            await asyncio.wait_for(
                websocket.send(encrypted_message),
                timeout=WEBSOCKET_TIMEOUT
            )
            logger.info(f"Sent secure message to {uri}")
    except asyncio.TimeoutError:
        logger.error(f"Timeout while sending message to {peer_ip}:{peer_port}")
        raise HTTPException(status_code=504, detail="Connection timeout")
    except websockets.exceptions.WebSocketException as e:
        logger.error(f"WebSocket error: {str(e)}")
        raise HTTPException(status_code=503, detail="WebSocket connection failed")
    except Exception as e:
        logger.error(f"Failed to send message: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

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
    except Exception as e:
        logger.error(f"Failed to receive message. Error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to receive message.")

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
                logger.info(f"Peer {peer_ip}:{peer_port} is healthy.")
                return True
            else:
                logger.warning(f"Unexpected response from {peer_ip}:{peer_port}")
                return False
    except Exception as e:
        logger.error(f"Peer {peer_ip}:{peer_port} is unreachable. Error: {str(e)}")
        return False

# --- Node Management Functions ---
async def register_new_peer(peer: Peer) -> None:
    """
    Register a new peer in the network.
    
    Args:
    - peer: Peer object containing node information
    
    Returns:
    - None
    """
    try:
        # Register the peer in the node registry (could be a DB or distributed system)
        register_node(peer.node_id, peer.ip_address, peer.port)
        logger.info(f"Node {peer.node_id} registered successfully at {peer.ip_address}:{peer.port}.")
    except Exception as e:
        logger.error(f"Failed to register node {peer.node_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to register node {peer.node_id}: {str(e)}")

async def discover_peers() -> List[Peer]:
    """
    Discover peers in the network.
    
    Returns:
    - List of available peers
    """
    try:
        peers = get_peers()  # Fetch the list of peers from the registry
        logger.info(f"Discovered {len(peers)} peers in the network.")
        return peers
    except Exception as e:
        logger.error(f"Failed to discover peers: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to discover peers.")

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
        logger.error(f"WebSocket error with peer {peer_ip}:{peer_port}: {str(e)}")
    except Exception as e:
        logger.error(f"Error in task distribution: {str(e)}")
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
        # Placeholder for actual retry logic, potentially re-distributing task to a different node
        result = await task_retry(task_id)
        logger.info(f"Task {task_id} has been retried successfully.")
        return {"status": "success", "message": f"Task {task_id} retried successfully."}
    except Exception as e:
        logger.error(f"Failed to retry task {task_id}: {str(e)}")
        return {"status": "failed", "message": f"Failed to retry task {task_id}: {str(e)}"}

# --- Example of Broadcasting a Message to All Peers ---
async def broadcast_message(message: Dict[str, Any], exclude_peer: Peer = None) -> None:
    """
    Broadcast a message to all peers except a specific one.
    
    Args:
    - message: The message to broadcast
    - exclude_peer: A specific peer to exclude from the broadcast (optional)
    
    Returns:
    - None
    """
    peers = await discover_peers()
    for peer in peers:
        if exclude_peer and peer.node_id == exclude_peer.node_id:
            continue  # Skip this peer
        try:
            # Send the message to the peer via WebSocket
            await secure_send(peer.ip_address, peer.port, message)
            logger.info(f"Broadcast message to {peer.node_id} at {peer.ip_address}:{peer.port}")
        except Exception as e:
            logger.error(f"Failed to broadcast message to {peer.node_id}: {str(e)}")

# --- Task Scheduling Integration ---
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
            time.sleep(interval)
    except Exception as e:
        logger.error(f"Error scheduling task {task_name} periodically: {str(e)}")
