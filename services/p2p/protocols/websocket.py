import asyncio
import websockets
import json
import logging
from typing import Dict
from cryptography.fernet import Fernet
from .services.result_logging import log_task_result, log_task_failure
from .services.node_management import register_node, get_peers
from .services.task_queue import distribute_task, validate_task_parameters

# Set up logging
logger = logging.getLogger(__name__)

# Encryption setup for secure communication
encryption_key = Fernet.generate_key()
cipher = Fernet(encryption_key)

# --- WebSocket Server ---
class WebSocketServer:
    """
    WebSocket server for handling real-time communication with peers, task distribution, and result logging.
    """
    
    async def register_node(self, websocket, node_id: str, node_ip: str, node_port: int):
        """
        Register the node with the network.
        """
        try:
            # Register the node with the provided details
            register_node(node_id, node_ip, node_port)
            logger.info(f"Node {node_id} registered successfully.")
            await websocket.send(json.dumps({"status": "success", "message": f"Node {node_id} registered successfully."}))
        except Exception as e:
            logger.error(f"Error registering node {node_id}: {str(e)}")
            await websocket.send(json.dumps({"status": "error", "message": str(e)}))

    async def handle_task_request(self, websocket, task_data: Dict):
        """
        Handle incoming task requests and process them in real-time.
        """
        try:
            # Validate task parameters
            if not validate_task_parameters(task_data):
                log_task_failure(task_data["task_name"], task_data["target_node_id"], "Invalid parameters.")
                await websocket.send(json.dumps({"status": "error", "message": "Invalid task parameters"}))
                return
            
            # Process and distribute the task
            task_response = await distribute_task(task_data)
            
            # Log task result
            log_task_result(task_data["task_name"], task_response["success"], task_response["message"])
            
            # Send back the result to the client
            await websocket.send(json.dumps(task_response))
        except Exception as e:
            logger.error(f"Error processing task: {str(e)}")
            await websocket.send(json.dumps({"status": "error", "message": str(e)}))

    async def handle_peer_discovery(self, websocket):
        """
        Handles peer discovery and sends back the list of registered peers.
        """
        try:
            peers = get_peers()
            peer_list = [{"node_id": peer["node_id"], "node_ip": peer["node_ip"], "node_port": peer["node_port"]} for peer in peers]
            await websocket.send(json.dumps({"status": "success", "peers": peer_list}))
        except Exception as e:
            logger.error(f"Error discovering peers: {str(e)}")
            await websocket.send(json.dumps({"status": "error", "message": str(e)}))

    async def handler(self, websocket, path):
        """
        Main handler for incoming WebSocket connections.
        """
        try:
            async for message in websocket:
                # Decrypt the incoming message
                decrypted_message = cipher.decrypt(message.encode()).decode()
                data = json.loads(decrypted_message)
                
                # Handle task request or node registration
                if "task_data" in data:
                    await self.handle_task_request(websocket, data["task_data"])
                elif "register_node" in data:
                    await self.register_node(websocket, data["node_id"], data["node_ip"], data["node_port"])
                elif "discover_peers" in data:
                    await self.handle_peer_discovery(websocket)
                else:
                    await websocket.send(json.dumps({"status": "error", "message": "Unknown request"}))
        except Exception as e:
            logger.error(f"Error in WebSocket communication: {str(e)}")
            await websocket.send(json.dumps({"status": "error", "message": str(e)}))

# --- WebSocket Client ---
class WebSocketClient:
    """
    WebSocket client for interacting with other nodes in the network.
    """
    
    def __init__(self, node_id: str, node_ip: str, node_port: int):
        self.node_id = node_id
        self.node_ip = node_ip
        self.node_port = node_port
        self.uri = f"ws://{node_ip}:{node_port}"
    
    async def connect(self):
        """
        Establish WebSocket connection with the peer.
        """
        try:
            async with websockets.connect(self.uri) as websocket:
                # Send node registration request
                register_data = {
                    "register_node": True,
                    "node_id": self.node_id,
                    "node_ip": self.node_ip,
                    "node_port": self.node_port
                }
                encrypted_register_data = cipher.encrypt(json.dumps(register_data).encode())
                await websocket.send(encrypted_register_data)
                
                # Wait for server response
                response = await websocket.recv()
                logger.info(f"Received response: {response}")
        
        except Exception as e:
            logger.error(f"Error connecting to WebSocket server: {str(e)}")

    async def send_task_request(self, task_data: Dict) -> Dict:
        """
        Sends a task request to another node over WebSocket and waits for the result.
        """
        try:
            async with websockets.connect(self.uri) as websocket:
                # Encrypt and send task data
                task_request_data = {
                    "task_data": task_data
                }
                encrypted_task_data = cipher.encrypt(json.dumps(task_request_data).encode())
                await websocket.send(encrypted_task_data)
                
                # Receive the task result
                response = await websocket.recv()
                decrypted_response = cipher.decrypt(response.encode()).decode()
                return json.loads(decrypted_response)
        
        except Exception as e:
            logger.error(f"Error sending task request: {str(e)}")
            return {"status": "error", "message": str(e)}
    
    async def discover_peers(self) -> Dict:
        """
        Discover peers in the network.
        """
        try:
            async with websockets.connect(self.uri) as websocket:
                discover_data = {
                    "discover_peers": True
                }
                encrypted_discover_data = cipher.encrypt(json.dumps(discover_data).encode())
                await websocket.send(encrypted_discover_data)
                
                # Receive the peers list
                response = await websocket.recv()
                decrypted_response = cipher.decrypt(response.encode()).decode()
                return json.loads(decrypted_response)
        
        except Exception as e:
            logger.error(f"Error discovering peers: {str(e)}")
            return {"status": "error", "message": str(e)}

# --- Start WebSocket Server ---
def start_websocket_server(host: str, port: int):
    """
    Starts the WebSocket server to listen for incoming connections.
    """
    server = WebSocketServer()
    start_server = websockets.serve(server.handler, host, port)
    
    # Run the WebSocket server
    asyncio.get_event_loop().run_until_complete(start_server)
    logger.info(f"WebSocket server started on {host}:{port}")
    asyncio.get_event_loop().run_forever()

# --- Example Usage ---
if __name__ == "__main__":
    # Start the server (this would typically be done in a separate process or container)
    start_websocket_server("localhost", 8765)

    # Example client usage
    client = WebSocketClient(node_id="node1", node_ip="localhost", node_port=8765)
    asyncio.run(client.connect())

    task_data = {
        "task_name": "data_processing",
        "parameters": {"input_data": "some_data"},
        "target_node_id": "node2"
    }
    result = asyncio.run(client.send_task_request(task_data))
    logger.info(f"Task result: {result}")
