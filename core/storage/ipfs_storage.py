import ipfshttpclient
import json
from typing import Dict, Any
import torch

class IPFSStorage:
    def __init__(self, ipfs_host: str = '/ip4/127.0.0.1/tcp/5001'):
        self.client = ipfshttpclient.connect(ipfs_host)
        
    def store_model(self, model: torch.nn.Module) -> str:
        """Store model weights in IPFS"""
        # Serialize model state
        state_dict = model.state_dict()
        buffer = io.BytesIO()
        torch.save(state_dict, buffer)
        
        # Store in IPFS
        res = self.client.add_bytes(buffer.getvalue())
        return res['Hash']
        
    def load_model(self, model_hash: str, model: torch.nn.Module):
        """Load model weights from IPFS"""
        # Get model state from IPFS
        data = self.client.cat(model_hash)
        buffer = io.BytesIO(data)
        
        # Load into model
        state_dict = torch.load(buffer)
        model.load_state_dict(state_dict)
        
    def store_metrics(self, metrics: Dict[str, Any]) -> str:
        """Store performance metrics in IPFS"""
        data = json.dumps(metrics).encode()
        res = self.client.add_bytes(data)
        return res['Hash']
        
    def load_metrics(self, metrics_hash: str) -> Dict[str, Any]:
        """Load metrics from IPFS"""
        data = self.client.cat(metrics_hash)
        return json.loads(data)
