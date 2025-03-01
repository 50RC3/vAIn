import asyncio
from core.p2p.peer_manager import PeerManager
from core.consensus.raft_consensus import RaftConsensus
from core.consensus.state_manager import DistributedStateManager

async def main():
    peer_manager = PeerManager()
    consensus = RaftConsensus(node_id="node1", peers=peer_manager)
    state_manager = DistributedStateManager(
        node_id="node1",
        peer_manager=peer_manager,
        consensus=consensus
    )
    
    # Propose a state update
    success = await state_manager.propose_state_update({"key": "value"})
    if success:
        print("State update accepted")
    
    # Sync with network
    await state_manager.sync_state()

if __name__ == "__main__":
    asyncio.run(main())
