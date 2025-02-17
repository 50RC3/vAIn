from enum import Enum
from typing import Dict, List, Any
import time
from dataclasses import dataclass
from web3 import Web3
import hashlib

class ResourceType(Enum):
    GPU = "gpu"
    CPU = "cpu"
    MEMORY = "memory"
    STORAGE = "storage"
    BANDWIDTH = "bandwidth"

@dataclass
class ResourceOffer:
    node_id: str
    resource_type: ResourceType
    amount: float
    price_per_unit: float
    duration: int
    timestamp: int

@dataclass
class Transaction:
    from_node: str
    to_node: str
    resource_type: ResourceType
    amount: float
    price: float
    timestamp: int

class InternalEconomy:
    def __init__(self, blockchain_url: str):
        self.w3 = Web3(Web3.HTTPProvider(blockchain_url))
        self.resource_market = {}
        self.transactions = []
        self.node_balances = {}
        self.node_contributions = {}
        self.resource_prices = {
            ResourceType.GPU: 100,
            ResourceType.CPU: 50,
            ResourceType.MEMORY: 30,
            ResourceType.STORAGE: 20,
            ResourceType.BANDWIDTH: 40
        }

    def register_node(self, node_id: str, initial_balance: float = 1000):
        """Register a new node in the economy"""
        if node_id not in self.node_balances:
            self.node_balances[node_id] = initial_balance
            self.node_contributions[node_id] = 0

    def create_resource_offer(self, offer: ResourceOffer) -> bool:
        """Create a new resource offer in the marketplace"""
        offer_hash = self._generate_offer_hash(offer)
        if offer_hash not in self.resource_market:
            self.resource_market[offer_hash] = offer
            return True
        return False

    def request_resources(self, requester_id: str, resource_type: ResourceType, 
                         amount: float, max_price: float) -> bool:
        """Request resources from the marketplace"""
        available_offers = self._find_matching_offers(resource_type, amount, max_price)
        if not available_offers:
            return False

        selected_offer = min(available_offers, key=lambda x: x.price_per_unit)
        return self._execute_transaction(requester_id, selected_offer)

    def _execute_transaction(self, requester_id: str, offer: ResourceOffer) -> bool:
        """Execute a resource transaction between nodes"""
        total_cost = offer.price_per_unit * offer.amount

        if self.node_balances[requester_id] < total_cost:
            return False

        # Update balances
        self.node_balances[requester_id] -= total_cost
        self.node_balances[offer.node_id] += total_cost

        # Record transaction
        transaction = Transaction(
            from_node=requester_id,
            to_node=offer.node_id,
            resource_type=offer.resource_type,
            amount=offer.amount,
            price=total_cost,
            timestamp=int(time.time())
        )
        self._record_transaction(transaction)

        # Update contribution scores
        self._update_contributions(offer.node_id, total_cost)
        
        return True

    def _find_matching_offers(self, resource_type: ResourceType, 
                            amount: float, max_price: float) -> List[ResourceOffer]:
        """Find matching resource offers based on requirements"""
        return [
            offer for offer in self.resource_market.values()
            if (offer.resource_type == resource_type and
                offer.amount >= amount and
                offer.price_per_unit <= max_price and
                int(time.time()) < offer.timestamp + offer.duration)
        ]

    def _generate_offer_hash(self, offer: ResourceOffer) -> str:
        """Generate a unique hash for a resource offer"""
        offer_str = f"{offer.node_id}{offer.resource_type.value}{offer.amount}{offer.timestamp}"
        return hashlib.sha256(offer_str.encode()).hexdigest()

    def _record_transaction(self, transaction: Transaction):
        """Record a transaction in the distributed ledger"""
        self.transactions.append(transaction)
        # Here we would normally commit to blockchain
        # self.w3.eth.send_transaction({...})

    def _update_contributions(self, node_id: str, contribution_value: float):
        """Update node contribution scores"""
        self.node_contributions[node_id] += contribution_value

    def get_node_balance(self, node_id: str) -> float:
        """Get the current balance of a node"""
        return self.node_balances.get(node_id, 0)

    def get_contribution_score(self, node_id: str) -> float:
        """Get the contribution score of a node"""
        return self.node_contributions.get(node_id, 0)

    def calculate_resource_price(self, resource_type: ResourceType) -> float:
        """Calculate current market price for a resource type"""
        base_price = self.resource_prices[resource_type]
        market_demand = self._calculate_market_demand(resource_type)
        return base_price * (1 + market_demand)

    def _calculate_market_demand(self, resource_type: ResourceType) -> float:
        """Calculate current market demand for a resource type"""
        recent_transactions = [t for t in self.transactions[-100:]
                             if t.resource_type == resource_type]
        if not recent_transactions:
            return 0
        return len(recent_transactions) / 100
