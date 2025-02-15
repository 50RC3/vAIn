import pytest
import torch
import numpy as np
from core.reinforcement_learning.policy import PolicyNetwork, RLPolicy

def test_policy_network_initialization():
    with pytest.raises(ValueError):
        PolicyNetwork(0, 4)  # Invalid state_dim
    with pytest.raises(ValueError):
        PolicyNetwork(4, -1)  # Invalid action_dim
    
    network = PolicyNetwork(4, 2)
    assert isinstance(network, torch.nn.Module)
    
    # Test forward pass
    state = torch.randn(1, 4)
    output = network(state)
    assert output.shape == (1, 2)

def test_rl_policy():
    policy = RLPolicy(state_dim=4, action_dim=2)
    
    # Test action selection
    state = np.random.rand(4)
    action = policy.select_action(state)
    assert 0 <= action < 2
    
    # Test experience storage
    policy.store_experience(state, action, 1.0, np.random.rand(4), False)
    assert len(policy.replay_buffer) == 1
    
    # Test policy update
    policy.update_policy(batch_size=1)
    assert policy.epsilon <= 1.0
