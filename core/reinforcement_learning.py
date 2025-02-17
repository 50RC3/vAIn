import numpy as np
from typing import Dict, List, Tuple
import torch
import torch.nn as nn
import torch.optim as optim

class AdaptivePolicy(nn.Module):
    def __init__(self, state_dim: int, action_dim: int):
        super().__init__()
        self.network = nn.Sequential(
            nn.Linear(state_dim, 128),
            nn.ReLU(),
            nn.Linear(128, 64),
            nn.ReLU(),
            nn.Linear(64, action_dim)
        )
    
    def forward(self, state):
        return torch.softmax(self.network(state), dim=-1)

class RLController:
    def __init__(self, learning_rate: float = 0.001, gamma: float = 0.99):
        """
        Initialize the RL controller for adaptive federated learning.
        
        Args:
            learning_rate: Learning rate for policy updates
            gamma: Discount factor for future rewards
        """
        self.state_dim = 5  # [model_performance, client_diversity, data_distribution, resource_usage, time_efficiency]
        self.action_dim = 4  # [adjust_learning_rate, modify_aggregation, change_architecture, request_resources]
        
        self.policy = AdaptivePolicy(self.state_dim, self.action_dim)
        self.optimizer = optim.Adam(self.policy.parameters(), lr=learning_rate)
        self.gamma = gamma
        self.state_history = []
        self.action_history = []
        self.reward_history = []

    def get_state(self, metrics: Dict[str, float]) -> torch.Tensor:
        """Convert system metrics to state vector"""
        state = torch.tensor([
            metrics.get('model_performance', 0),
            metrics.get('client_diversity', 0),
            metrics.get('data_distribution', 0),
            metrics.get('resource_usage', 0),
            metrics.get('time_efficiency', 0)
        ], dtype=torch.float32)
        return state

    def select_action(self, state: torch.Tensor) -> Tuple[int, float]:
        """Select action based on current policy"""
        action_probs = self.policy(state)
        action = torch.multinomial(action_probs, 1).item()
        log_prob = torch.log(action_probs[action])
        return action, log_prob

    def calculate_reward(self, metrics: Dict[str, float]) -> float:
        """Calculate reward based on system performance"""
        reward = (
            0.4 * metrics.get('model_performance', 0) +
            0.2 * metrics.get('time_efficiency', 0) +
            0.2 * metrics.get('resource_efficiency', 0) +
            0.2 * metrics.get('adaptation_success', 0)
        )
        return reward

    def update_policy(self):
        """Update policy using collected experiences"""
        if not self.reward_history:
            return

        rewards = torch.tensor(self.reward_history)
        returns = self._calculate_returns(rewards)
        log_probs = torch.stack(self.action_history)

        loss = -(returns * log_probs).mean()
        
        self.optimizer.zero_grad()
        loss.backward()
        self.optimizer.step()

        self._clear_history()

    def _calculate_returns(self, rewards: torch.Tensor) -> torch.Tensor:
        """Calculate discounted returns"""
        returns = torch.zeros_like(rewards)
        running_return = 0
        for t in reversed(range(len(rewards))):
            running_return = rewards[t] + self.gamma * running_return
            returns[t] = running_return
        returns = (returns - returns.mean()) / (returns.std() + 1e-8)
        return returns

    def _clear_history(self):
        """Clear experience history"""
        self.state_history.clear()
        self.action_history.clear()
        self.reward_history.clear()
