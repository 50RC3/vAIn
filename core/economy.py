from typing import Dict, List, Any
from enum import Enum
import hashlib
import time
from dataclasses import dataclass
from web3 import Web3

class ResourceType(Enum):
    COMPUTE = "compute"
    STORAGE = "storage" 
    BANDWIDTH = "bandwidth"
    MEMORY = "memory"

@dataclass
class Transaction:
    sender: str
    receiver: str
    resource_type: ResourceType
    amount: float
    credits: float
    timestamp: float
    proof: str

class InternalEconomy:
    def __init__(self, blockchain_url: str = "http://localhost:8545"):
        self.w3 = Web3(Web3.HTTPProvider(blockchain_url))
        self.credit_balances = {}
        self.resource_prices = {
            ResourceType.COMPUTE: 1.0,
            ResourceType.STORAGE: 0.5,
            ResourceType.BANDWIDTH: 0.3,
            ResourceType.MEMORY: 0.8
        }
        self.transactions = []
        self.contribution_scores = {}
        
    def register_node(self, node_id: str):
        """Register a new node in the economy"""
        if node_id not in self.credit_balances:
            self.credit_balances[node_id] = 100  # Initial credits
            self.contribution_scores[node_id] = 0
            
    def request_resource(self, requester: str, resource_type: ResourceType, 
                        amount: float) -> bool:
        """Request resources from the network"""
        required_credits = self._calculate_cost(resource_type, amount)
        
        if self.credit_balances[requester] < required_credits:
            return False
            
        available_nodes = self._find_available_nodes(resource_type, amount)
        if not available_nodes:
            return False
            
        # Execute transaction
        provider = self._select_best_provider(available_nodes)
        self._execute_transaction(requester, provider, resource_type, 
                                amount, required_credits)
        return True
        
    def offer_resource(self, provider: str, resource_type: ResourceType, 
                      amount: float, price_modifier: float = 1.0):
        """Offer resources to the network"""
        base_price = self.resource_prices[resource_type]
        offer_price = base_price * price_modifier
        
        # Register the offer in the marketplace
        offer = {
            'provider': provider,
            'resource_type': resource_type,
            'amount': amount,
            'price': offer_price
        }
        return self._register_offer(offer)
        
    def update_contribution_score(self, node_id: str, task_success: float, 
                                resource_quality: float):
        """Update a node's contribution score"""
        quality_weight = 0.7
        success_weight = 0.3
        score_update = (quality_weight * resource_quality + 
                       success_weight * task_success)
        
        self.contribution_scores[node_id] = (
            0.9 * self.contribution_scores[node_id] + 0.1 * score_update
        )
        
    def generate_proof_of_contribution(self, node_id: str, 
                                     contribution_data: Dict) -> str:
        """Generate proof of contribution for a node"""
        timestamp = time.time()
        data_string = (f"{node_id}-{contribution_data}-{timestamp}"
                      f"-{self.contribution_scores[node_id]}")
        return hashlib.sha256(data_string.encode()).hexdigest()
        
    def _calculate_cost(self, resource_type: ResourceType, 
                       amount: float) -> float:
        """Calculate the cost of resources"""
        base_price = self.resource_prices[resource_type]
        market_factor = self._get_market_factor(resource_type)
        return base_price * amount * market_factor
        
    def _get_market_factor(self, resource_type: ResourceType) -> float:
        """Get current market adjustment factor based on supply/demand"""
        # Implementation based on current network state
        return 1.0
        
    def _execute_transaction(self, sender: str, receiver: str, 
                           resource_type: ResourceType, amount: float, 
                           credits: float):
        """Execute a resource transaction"""
        # Update balances
        self.credit_balances[sender] -= credits
        self.credit_balances[receiver] += credits
        
        # Generate proof and record transaction
        proof = self.generate_proof_of_contribution(
            receiver, 
            {'resource_type': resource_type, 'amount': amount}
        )
        
        transaction = Transaction(
            sender=sender,
            receiver=receiver,
            resource_type=resource_type,
            amount=amount,
            credits=credits,
            timestamp=time.time(),
            proof=proof
        )
        
        # Record in blockchain
        self._record_in_blockchain(transaction)
        self.transactions.append(transaction)
        
    def _record_in_blockchain(self, transaction: Transaction):
        """Record a transaction in the blockchain"""
        # Implementation using web3 to interact with smart contract
        pass
