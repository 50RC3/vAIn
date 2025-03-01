from typing import Dict, List, Optional
import asyncio
from dataclasses import dataclass
import logging

@dataclass
class Peer:
    node_id: str
    address: str
    is_active: bool = True
    last_seen: float = 0.0

class PeerManager:
    def __init__(self):
        self.peers: Dict[str, Peer] = {}
        self.logger = logging.getLogger(__name__)

    async def add_peer(self, node_id: str, address: str) -> bool:
        if node_id not in self.peers:
            self.peers[node_id] = Peer(node_id=node_id, address=address)
            self.logger.info(f"Added new peer: {node_id} at {address}")
            return True
        return False

    async def remove_peer(self, node_id: str) -> bool:
        if node_id in self.peers:
            del self.peers[node_id]
            self.logger.info(f"Removed peer: {node_id}")
            return True
        return False

    def get_active_peers(self) -> List[Peer]:
        return [peer for peer in self.peers.values() if peer.is_active]

    def get_peer(self, node_id: str) -> Optional[Peer]:
        return self.peers.get(node_id)
