import pytest
import numpy as np
from core.federated_learning import FederatedLearning
import torch

class DummyModel:
    def __init__(self, client_id):
        self.weights = np.random.rand(10)
        self.client_id = client_id
    
    def get_weights(self):
        return self.weights
    
    def set_weights(self, weights):
        self.weights = weights
    
    def train(self, data, epochs):
        pass

def test_federated_learning_initialization():
    global_model = DummyModel("global")
    client_models = [DummyModel(f"client_{i}") for i in range(3)]
    
    fl = FederatedLearning(global_model, client_models)
    assert fl.global_model is not None
    assert len(fl.client_models) == 3

def test_secure_aggregation():
    global_model = DummyModel("global")
    client_models = [DummyModel(f"client_{i}") for i in range(3)]
    fl = FederatedLearning(global_model, client_models)
    
    updates = [{"weights": np.random.rand(10), 
                "num_samples": 100,
                "client_id": f"client_{i}"} for i in range(3)]
    
    secure_updates = fl._apply_secure_aggregation(updates)
    assert len(secure_updates) == len(updates)
    assert "weights" in secure_updates[0]
