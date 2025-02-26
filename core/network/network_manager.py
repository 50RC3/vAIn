import asyncio
import logging
from typing import Dict, List, Optional
from .network_security import SecureChannel
from core.utils.validation import validate_node
from .node_registry import NodeRegistry

class NetworkManager:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.nodes = NodeRegistry()
        self.secure_channel = SecureChannel()
        self._active = False

    async def start(self, port: int = 8000):
        """Start the network manager and listen for connections"""
        try:
            self._active = True
            self.server = await asyncio.start_server(
                self._handle_connection, '0.0.0.0', port
            )
            self.logger.info(f"Network manager started on port {port}")
        except Exception as e:
            self.logger.error(f"Failed to start network manager: {e}")
            raise

    async def _handle_connection(self, reader: asyncio.StreamReader, 
                               writer: asyncio.StreamWriter):
        """Handle incoming node connections"""
        try:
            data = await self.secure_channel.receive(reader)
            node_id = data.get('node_id')
            
            if not validate_node(node_id, data):
                writer.close()
                return

            await self.nodes.register(node_id, writer)
            self.logger.info(f"Node {node_id} connected")
            
        except Exception as e:
            self.logger.error(f"Connection handling error: {e}")
            writer.close()

    async def broadcast(self, message: Dict):
        """Broadcast message to all connected nodes"""
        await self.nodes.broadcast(
            self.secure_channel.encrypt(message)
        )

    async def stop(self):
        """Stop the network manager"""
        self._active = False
        self.server.close()
        await self.server.wait_closed()
        await self.nodes.disconnect_all()
