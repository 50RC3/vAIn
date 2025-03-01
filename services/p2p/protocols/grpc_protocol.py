"""
gRPC protocol implementation for P2P communication in vAIn.
Handles node registration, peer discovery, and task distribution.
"""

import concurrent.futures
import json
from typing import Dict, Any, Optional
import logging

import grpc
from cryptography.fernet import Fernet
from fastapi import HTTPException

from vain.services.result_logging import ResultLogger
from vain.services.task_queue import TaskQueue
from vain.services.node_management import NodeManager
from vain.services.p2p.proto import p2p_pb2, p2p_pb2_grpc

logger = logging.getLogger(__name__)

class P2PServicer(p2p_pb2_grpc.P2PServiceServicer):
    """gRPC servicer implementation for P2P communication."""

    def __init__(self, node_manager: NodeManager, task_queue: TaskQueue, result_logger: ResultLogger):
        self.node_manager = node_manager
        self.task_queue = task_queue
        self.result_logger = result_logger
        self.fernet = Fernet(Fernet.generate_key())

    def task_request(self, request, context) -> p2p_pb2.TaskResponse:
        """Handle incoming task requests."""
        try:
            task_id = request.task_id
            request_data = json.loads(request.task_data)
            
            if not self.validate_task_data(request_data):
                return p2p_pb2.TaskResponse(
                    success=False,
                    message="Invalid task data format"
                )
            
            processed_data = self.task_queue.process_task(task_id, request_data)
            encrypted_result = self.fernet.encrypt(json.dumps(processed_data).encode())
            
            return p2p_pb2.TaskResponse(
                success=True,
                result=encrypted_result,
                message="Task processed successfully"
            )
            
        except Exception as e:
            logger.error("Task request failed: %s", str(e))
            return p2p_pb2.TaskResponse(
                success=False,
                message="Error processing task: %s" % str(e)
            )

    def register_node(self, request, context) -> p2p_pb2.RegistrationResponse:
        """Handle node registration requests."""
        try:
            node_info = {
                'id': request.node_id,
                'address': request.address,
                'capabilities': json.loads(request.capabilities)
            }
            
            success = self.node_manager.register_node(node_info)
            
            if success:
                logger.info("Node registered successfully: %s", request.node_id)
                return p2p_pb2.RegistrationResponse(
                    success=True,
                    message="Node registered successfully"
                )
            
            return p2p_pb2.RegistrationResponse(
                success=False,
                message="Node registration failed"
            )
            
        except Exception as e:
            logger.error("Node registration failed: %s", str(e))
            return p2p_pb2.RegistrationResponse(
                success=False,
                message=str(e)
            )

    def peer_discovery(self, request, context) -> p2p_pb2.PeerDiscoveryResponse:
        """Handle peer discovery requests."""
        try:
            node_id = request.node_id
            capabilities_filter = (json.loads(request.capabilities_filter) 
                                if request.capabilities_filter else None)
            
            peers = self.node_manager.get_peers(node_id, capabilities_filter)
            peer_list = [
                p2p_pb2.PeerInfo(
                    node_id=peer['id'],
                    address=peer['address'],
                    capabilities=json.dumps(peer['capabilities'])
                ) for peer in peers
            ]
            
            return p2p_pb2.PeerDiscoveryResponse(
                success=True,
                peers=peer_list
            )
            
        except Exception as e:
            logger.error("Peer discovery failed: %s", str(e))
            return p2p_pb2.PeerDiscoveryResponse(
                success=False,
                peers=[],
                message=str(e)
            )

    def send_task_request(self, node_address: str, task_id: str, task_data: Dict[str, Any]) -> bool:
        """Send task request to a specific node."""
        try:
            logger.info("Sending task request to %s", node_address)
            channel = grpc.insecure_channel(node_address)
            stub = p2p_pb2_grpc.P2PServiceStub(channel)
            
            response = stub.task_request(p2p_pb2.TaskRequest(
                task_id=task_id,
                task_data=json.dumps(task_data)
            ))
            
            if response.success:
                logger.info("Task request sent successfully")
                return True
            
            logger.error("Task request failed: %s", response.message)
            raise grpc.RpcError(response.message)
            
        except Exception as e:
            logger.error("Error sending task request: %s", str(e))
            raise HTTPException(
                status_code=500, 
                detail="Error occurred while sending task request."
            ) from e

    def register_with_peer(self, peer_address: str, node_info: Dict[str, Any]) -> bool:
        """Register this node with a peer node."""
        try:
            logger.info("Registering with peer at %s", peer_address)
            channel = grpc.insecure_channel(peer_address)
            stub = p2p_pb2_grpc.P2PServiceStub(channel)
            
            response = stub.register_node(p2p_pb2.RegistrationRequest(
                node_id=node_info['id'],
                address=node_info['address'],
                capabilities=json.dumps(node_info['capabilities'])
            ))
            
            if response.success:
                logger.info("Registration with peer successful")
                return True
            
            logger.error("Registration with peer failed: %s", response.message)
            raise grpc.RpcError(response.message)
            
        except Exception as e:
            logger.error("Error during peer registration: %s", str(e))
            raise HTTPException(
                status_code=500,
                detail="Error occurred during node registration."
            ) from e

    def validate_task_data(self, task_data: Dict[str, Any]) -> bool:
        """Validate incoming task data structure."""
        required_fields = ['type', 'payload']
        return all(field in task_data for field in required_fields)

    def start_server(self, address: str) -> grpc.Server:
        """Start the gRPC server."""
        server = grpc.server(concurrent.futures.ThreadPoolExecutor(max_workers=10))
        p2p_pb2_grpc.add_P2PServiceServicer_to_server(self, server)
        server.add_insecure_port(address)
        server.start()
        logger.info("gRPC server started on %s", address)
        return server
