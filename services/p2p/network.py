import logging
import asyncio
import json
import websockets
from cryptography.fernet import Fernet
from fastapi import HTTPException
from typing import List, Dict, Any
from ..services.task_queue import distribute_task, validate_task_parameters
from ..services.result_logging import log_task_result, log_task_failure
from ..services.task_scheduler import schedule_task, cancel_scheduled_task
from ..utils import get_node_id, get_peers, register_node, check_peer_health
from pydantic import BaseModel
import time

# Set up logging
logger = logging.getLogger(__name__)

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

class TaskResponse(BaseModel):
    """Schema for task responses to peers."""
    task_name: str
    result: Dict[str, Any]
    success: bool
    message: str

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
        async with websockets.connect(f"ws://{peer_ip}:{peer_port}") as websocket:
            # Encrypt the message
            encrypted_message = cipher.encrypt(json.dumps(message).encode())
            await websocket.send(encrypted_message)
            logger.info(f"Sent secure message to {peer_ip}:{peer_port}")
    except Exception as e:
        logger.error(f"Failed to send message to {peer_ip}:{peer_port}. Error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to send message to {peer_ip}:{peer_port}. {str(e)}")

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
async def distribute_task_to_peer(task_request: TaskRequest, peer_ip: str, peer_port: int) -> TaskResponse:
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
        # Send the task to the peer node securely
        await secure_send(peer_ip, peer_port, task_request.dict())
        
        # Wait for the task response
        response = await secure_receive(peer_ip, peer_port)
        
        # Log the task result
        task_response = TaskResponse(**response)
        log_task_result(task_request.task_name, task_response.success, task_response.message)
        
        # Return the task response
        logger.info(f"Task {task_request.task_name} completed successfully on peer {peer_ip}:{peer_port}.")
        return task_response
    except Exception as e:
        logger.error(f"Error distributing task {task_request.task_name} to peer {peer_ip}:{peer_port}: {str(e)}")
        log_task_failure(task_request.task_name, task_request.target_node_id, str(e))
        
        # Retry if task has not reached maximum retries
        if task_request.retry_count < 3:
            logger.info(f"Retrying task {task_request.task_name}, attempt {task_request.retry_count + 1}.")
            task_request.retry_count += 1
            return await distribute_task_to_peer(task_request, peer_ip, peer_port)
        
        raise HTTPException(status_code=500, detail=f"Error distributing task: {str(e)}")

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
