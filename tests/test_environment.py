import pytest
import numpy as np
from core.reinforcement_learning.environment import EvolvingEnvironment

def test_environment_initialization():
    # Test invalid parameters
    with pytest.raises(ValueError):
        EvolvingEnvironment(grid_size=(0, 10))
    with pytest.raises(ValueError):
        EvolvingEnvironment(max_steps=0)
    
    # Test default initialization
    env = EvolvingEnvironment()
    assert env.grid_size == (10, 10)
    assert env.max_steps == 500

def test_environment_step():
    env = EvolvingEnvironment()
    initial_state = env.reset()
    assert initial_state.shape == (10, 10)
    
    # Test valid action
    state, reward, done, info = env.step(0)  # 0 is a valid action
    assert state.shape == (10, 10)
    assert isinstance(reward, float)
    assert isinstance(done, bool)
    assert isinstance(info, dict)
    
    # Test invalid action
    with pytest.raises(ValueError):
        env.step(5)  # Assuming 5 is out of action space

def test_environment_reset():
    env = EvolvingEnvironment()
    _ = env.step(0)
    reset_state = env.reset()
    assert reset_state.shape == (10, 10)
    assert env.current_step == 0
