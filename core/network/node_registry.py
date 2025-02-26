import asyncio
import logging
from typing import Dict, Optional
from dataclasses import dataclass
from datetime import datetime

@dataclass
class Node:
    id: str
    writer: asyncio.StreamWriter
    connected_at: datetime
    last_seen: datetime

class NodeRegistry:
    def __init__(self):
        self.nodes: Dict[str, Node] = {}
        self.logger = logging.getLogger(__name__)

    async def register(self, node_id: str, writer: asyncio.StreamWriter):
        """Register a new node"""
        now = datetime.utcnow()
        self.nodes[node_id] = Node(
            id=node_id,
            writer=writer,
            connected_at=now,
            last_seen=now
        )

    async def broadcast(self, data: bytes):
        """Send data to all registered nodes"""
        dead_nodes = []
        for node_id, node in self.nodes.items():
            try:
                node.writer.write(data)
                await node.writer.drain()
                node.last_seen = datetime.utcnow()
            except:
                dead_nodes.append(node_id)
                
        # Clean up dead nodes
        for node_id in dead_nodes:
            await self.disconnect(node_id)

    async def disconnect(self, node_id: str):
        """Remove a node from registry"""
        if node := self.nodes.pop(node_id, None):
            node.writer.close()
            await node.writer.wait_closed()

    async def disconnect_all(self):
        """Disconnect all nodes"""
        for node_id in list(self.nodes.keys()):
            await self.disconnect(node_id)
