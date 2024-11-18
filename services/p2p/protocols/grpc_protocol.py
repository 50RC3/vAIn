import logging
import grpc
import json
from concurrent import futures
from cryptography.fernet import Fernet
from typing import List, Dict
from fastapi import HTTPException
from .services.result_logging import log_task_result, log_task_failure
from .services.task_queue import distribute_task, validate_task_parameters
from .services.node_management import register_node, get_peers
from .proto import grpc_messages_pb2, grpc_messages_pb2_grpc

# Set up logging
logger = logging.getLogger(__name__)

# Encryption setup for secure communication
encryption_key = Fernet.generate_key()
cipher = Fernet(encryption_key)

# --- GRPC Server ---
class NodeService(grpc_messages_pb2_grpc.NodeServiceServicer):
    """
    GRPC service for handling node requests, task distribution, and result logging.
    """
    
    async def TaskRequest(self, request, context):
        """
        Handles incoming task requests from peers or clients.
        """
        try:
            # Decrypt and process the task request
            decrypted_request = cipher.decrypt(request.encrypted_task_data).decode()
            task_data = json.loads(decrypted_request)
            
            # Validate task parameters
            if not validate_task_parameters(task_data):
                log_task_failure(task_data["task_name"], task_data["target_node_id"], "Invalid parameters.")
                return grpc_messages_pb2.TaskResponse(success=False, message="Invalid task parameters")
            
            # Distribute the task (this could be to a local service or peer)
            task_response = await distribute_task(task_data)
            
            # Log the result of the task execution
            log_task_result(task_data["task_name"], task_response["success"], task_response["message"])
            
            # Encrypt the task result before sending back to the peer
            encrypted_response = cipher.encrypt(json.dumps(task_response).encode())
            return grpc_messages_pb2.TaskResponse(
                success=task_response["success"],
                message=task_response["message"],
                encrypted_task_result=encrypted_response
            )
        
        except Exception as e:
            logger.error(f"Error handling TaskRequest: {str(e)}")
            return grpc_messages_pb2.TaskResponse(success=False, message=f"Error: {str(e)}")
    
    async def RegisterNode(self, request, context):
        """
        Registers a new node in the network.
        """
        try:
            # Register the node using the provided details
            node_id = request.node_id
            node_ip = request.node_ip
            node_port = request.node_port
            
            # Register node in the system (this could be a database or distributed registry)
            register_node(node_id, node_ip, node_port)
            logger.info(f"Node {node_id} registered successfully.")
            
            return grpc_messages_pb2.RegisterNodeResponse(
                success=True,
                message=f"Node {node_id} registered successfully."
            )
        
        except Exception as e:
            logger.error(f"Error registering node {request.node_id}: {str(e)}")
            return grpc_messages_pb2.RegisterNodeResponse(success=False, message=f"Error: {str(e)}")
    
    async def PeerDiscovery(self, request, context):
        """
        Returns a list of peers registered in the network.
        """
        try:
            peers = get_peers()
            peer_list = []
            for peer in peers:
                peer_list.append(grpc_messages_pb2.PeerInfo(node_id=peer["node_id"], node_ip=peer["node_ip"], node_port=peer["node_port"]))
            
            return grpc_messages_pb2.PeerDiscoveryResponse(peers=peer_list)
        
        except Exception as e:
            logger.error(f"Error discovering peers: {str(e)}")
            return grpc_messages_pb2.PeerDiscoveryResponse(peers=[])

# --- GRPC Client ---
class NodeClient:
    """
    Client to interact with the GRPC server. Can send task requests, register nodes, and discover peers.
    """
    
    def __init__(self, node_id: str, node_ip: str, node_port: int):
        self.node_id = node_id
        self.node_ip = node_ip
        self.node_port = node_port
        self.channel = grpc.insecure_channel(f"{node_ip}:{node_port}")
        self.stub = grpc_messages_pb2_grpc.NodeServiceStub(self.channel)
    
    def send_task_request(self, task_data: Dict) -> Dict:
        """
        Sends a task request to the GRPC server and waits for a response.
        """
        try:
            # Encrypt the task data before sending
            encrypted_data = cipher.encrypt(json.dumps(task_data).encode())
            request = grpc_messages_pb2.TaskRequest(
                encrypted_task_data=encrypted_data
            )
            
            # Send the request and get the response
            response = self.stub.TaskRequest(request)
            
            # Decrypt and process the response
            decrypted_response = cipher.decrypt(response.encrypted_task_result).decode()
            return json.loads(decrypted_response)
        
        except grpc.RpcError as e:
            logger.error(f"RPC error occurred: {str(e)}")
            raise HTTPException(status_code=500, detail="Error occurred while sending task request.")
    
    def register_node(self) -> Dict:
        """
        Registers the current node with the GRPC server.
        """
        try:
            request = grpc_messages_pb2.RegisterNodeRequest(
                node_id=self.node_id,
                node_ip=self.node_ip,
                node_port=self.node_port
            )
            response = self.stub.RegisterNode(request)
            return {"success": response.success, "message": response.message}
        
        except grpc.RpcError as e:
            logger.error(f"RPC error occurred during node registration: {str(e)}")
            raise HTTPException(status_code=500, detail="Error occurred during node registration.")
    
    def discover_peers(self) -> List[Dict]:
        """
        Discovers peers from the GRPC server.
        """
        try:
            request = grpc_messages_pb2.PeerDiscoveryRequest()
            response = self.stub.PeerDiscovery(request)
            peers = [{"node_id": peer.node_id, "node_ip": peer.node_ip, "node_port": peer.node_port} for peer in response.peers]
            return peers
        
        except grpc.RpcError as e:
            logger.error(f"RPC error occurred during peer discovery: {str(e)}")
            raise HTTPException(status_code=500, detail="Error occurred during peer discovery.")

# --- GRPC Server Setup ---
def start_grpc_server(host: str, port: int):
    """
    Start the GRPC server for handling incoming requests.
    """
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    grpc_messages_pb2_grpc.add_NodeServiceServicer_to_server(NodeService(), server)
    server.add_insecure_port(f"{host}:{port}")
    server.start()
    logger.info(f"GRPC server started on {host}:{port}")
    server.wait_for_termination()

# --- Example Usage ---
if __name__ == "__main__":
    # Start the server (this would typically be done in a separate process or container)
    start_grpc_server("localhost", 50051)

    # Example client usage:
    client = NodeClient(node_id="node1", node_ip="localhost", node_port=50051)
    task_data = {
        "task_name": "data_processing",
        "parameters": {"input_data": "some_data"},
        "target_node_id": "node2"
    }
    result = client.send_task_request(task_data)
    logger.info(f"Task result: {result}")
