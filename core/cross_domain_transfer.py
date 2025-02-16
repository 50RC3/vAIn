import numpy as np
import tensorflow as tf
from typing import Dict, List, Any, Tuple
from enum import Enum

class DomainType(Enum):
    NLP = "nlp"
    COMPUTER_VISION = "cv"
    AUDIO = "audio"
    TABULAR = "tabular"
    REINFORCEMENT = "rl"

class CrossDomainTransfer:
    """Handles knowledge transfer between different AI domains"""
    
    def __init__(self):
        self.domain_embeddings = {}
        self.transfer_mappings = {}
        self.adaptation_metrics = {}
        
    def register_domain(self, domain_id: str, domain_type: DomainType, model_architecture: Dict):
        """Register a new domain with its characteristics"""
        embedding = self._compute_domain_embedding(domain_type, model_architecture)
        self.domain_embeddings[domain_id] = {
            'type': domain_type,
            'embedding': embedding,
            'architecture': model_architecture
        }
        
    def transfer_knowledge(self, source_domain: str, target_domain: str, knowledge: Dict) -> Dict:
        """Transfer knowledge from source to target domain with adaptation"""
        if not self._domains_compatible(source_domain, target_domain):
            return None
            
        adapted_knowledge = self._adapt_knowledge(
            knowledge,
            self.domain_embeddings[source_domain],
            self.domain_embeddings[target_domain]
        )
        
        return adapted_knowledge
        
    def _compute_domain_embedding(self, domain_type: DomainType, architecture: Dict) -> np.ndarray:
        """Compute embedding vector for a domain based on its characteristics"""
        # Convert domain characteristics to numerical embedding
        arch_features = self._extract_architecture_features(architecture)
        domain_features = self._get_domain_features(domain_type)
        return np.concatenate([arch_features, domain_features])
    
    def _extract_architecture_features(self, architecture: Dict) -> np.ndarray:
        """Extract numerical features from model architecture"""
        features = []
        features.append(len(architecture.get('layers', [])))
        features.append(sum(l.get('units', 0) for l in architecture.get('layers', [])))
        return np.array(features)
    
    def _get_domain_features(self, domain_type: DomainType) -> np.ndarray:
        """Get characteristic features for each domain type"""
        feature_map = {
            DomainType.NLP: [1, 0, 0, 0, 0],
            DomainType.COMPUTER_VISION: [0, 1, 0, 0, 0],
            DomainType.AUDIO: [0, 0, 1, 0, 0],
            DomainType.TABULAR: [0, 0, 0, 1, 0],
            DomainType.REINFORCEMENT: [0, 0, 0, 0, 1]
        }
        return np.array(feature_map[domain_type])
    
    def _domains_compatible(self, source_domain: str, target_domain: str) -> bool:
        """Check if two domains are compatible for knowledge transfer"""
        source_embed = self.domain_embeddings[source_domain]['embedding']
        target_embed = self.domain_embeddings[target_domain]['embedding']
        similarity = self._compute_similarity(source_embed, target_embed)
        return similarity > 0.5
    
    def _adapt_knowledge(self, knowledge: Dict, source_domain: Dict, target_domain: Dict) -> Dict:
        """Adapt knowledge from source domain to target domain"""
        adapted = {}
        
        # Adapt model parameters
        if 'model_params' in knowledge:
            adapted['model_params'] = self._adapt_parameters(
                knowledge['model_params'],
                source_domain['architecture'],
                target_domain['architecture']
            )
            
        # Adapt feature representations
        if 'features' in knowledge:
            adapted['features'] = self._adapt_features(
                knowledge['features'],
                source_domain['type'],
                target_domain['type']
            )
            
        return adapted
    
    def _compute_similarity(self, embed1: np.ndarray, embed2: np.ndarray) -> float:
        """Compute similarity between domain embeddings"""
        return np.dot(embed1, embed2) / (np.linalg.norm(embed1) * np.linalg.norm(embed2))
