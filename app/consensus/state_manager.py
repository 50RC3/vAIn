from typing import Dict, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime
import asyncio
import json
import logging
from core.p2p.peer_manager import PeerManager
from ..consensus.raft_consensus import RaftConsensus

@dataclass
class ConsensusState:
    """Represents a state update that requires consensus"""
    version: int
    timestamp: datetime
    data: Dict[str, Any]
    proposer: str
    signatures: Dict[str, str] = field(default_factory=dict)

class DistributedStateManager:
    def __init__(self, node_id: str, peer_manager: PeerManager, consensus: RaftConsensus):
        self.node_id = node_id
        self.peer_manager = peer_manager
        self.consensus = consensus
        self.current_state = ConsensusState(
            version=0,
            timestamp=datetime.now(),
            data={},
            proposer=node_id
        )
        self.logger = logging.getLogger(__name__)

    # ...existing code for propose_state_update...
    # ...existing code for validate_state_update...
    # ...existing code for get_current_state...
    # ...existing code for sync_state...
    # ...existing code for serialize_state...
    # ...existing code for deserialize_state...
