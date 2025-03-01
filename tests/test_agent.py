import pytest
import numpy as np
from core.reinforcement_learning.agent import RLAgent
import torch

def test_agent_initialization():
    with pytest.raises(ValueError):
        RLAgent(state_size=0, action_size=4)
    with pytest.raises(ValueError):
        RLAgent(state_size=4, action_size=-1)
    
    agent = RLAgent(state_size=4, action_size=2)
    assert agent.state_size == 4
    assert agent.action_size == 2

def test_agent_training():
    agent = RLAgent(state_size=4, action_size=2)
    state = np.random.rand(1, 4)
    
    # Test action selection
    action = agent.act(state)
    assert 0 <= action < 2
    
    # Test experience storage and training
    next_state = np.random.rand(1, 4)
    agent.store_experience(state, action, 1.0, next_state, False)
    initial_epsilon = agent.epsilon
    agent.train()
    assert agent.epsilon <= initial_epsilon

def test_model_save_load(tmp_path):
    agent = RLAgent(state_size=4, action_size=2, model_save_path=str(tmp_path))
    agent.save_model()
    assert (tmp_path / "dqn_weights.h5").exists()
