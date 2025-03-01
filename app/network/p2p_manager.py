from typing import List, Dict, Optional
import asyncio
from ..utils.security import SecureSession
from ..config.network_config import NetworkConfig

class P2PManager:
    def __init__(self, config: NetworkConfig):
        self.nodes: Dict[str, 'Node'] = {}
        self.session = SecureSession()
        self.config = config
        
    async def connect_node(self, node_id: str, address: str) -> bool:
        try:
            response = await self.session.post(f"{address}/handshake", 
                                            json={"node_id": node_id})
            if response.status_code == 200:
                self.nodes[node_id] = Node(node_id, address)
                return True
            return False
        except Exception:
            return False

    async def broadcast(self, message: Dict) -> List[str]:
        failed_nodes = []
        for node_id, node in self.nodes.items():
            try:
                await node.send_message(message)
            except Exception:
                failed_nodes.append(node_id)
        return failed_nodes

class Node:
    def __init__(self, node_id: str, address: str):
        self.node_id = node_id
        self.address = address
        self.session = SecureSession()

    async def send_message(self, message: Dict) -> bool:
        try:
            response = await self.session.post(
                f"{self.address}/message",
                json=message
            )
            return response.status_code == 200
        except Exception:
            return False
