import torch
import torch.nn as nn
import torch.optim as optim
import numpy as np
from collections import deque
import random


class PolicyNetwork(nn.Module):
    """
    Neural network for approximating the policy.
    """
    def __init__(self, state_dim, action_dim, hidden_layers=[128, 128], activation=nn.ReLU):
        """
        Initialize the policy network.

        Args:
            state_dim (int): Dimensionality of the state space.
            action_dim (int): Dimensionality of the action space.
            hidden_layers (list): List of hidden layer sizes.
            activation (class): Activation function for the hidden layers.
        """
        super(PolicyNetwork, self).__init__()
        layers = []
        input_dim = state_dim

        # Build hidden layers
        for hidden_dim in hidden_layers:
            layers.append(nn.Linear(input_dim, hidden_dim))
            layers.append(activation())
            input_dim = hidden_dim

        # Output layer
        layers.append(nn.Linear(input_dim, action_dim))
        self.model = nn.Sequential(*layers)

    def forward(self, state):
        """
        Forward pass through the policy network.

        Args:
            state (torch.Tensor): Input state.

        Returns:
            torch.Tensor: Action probabilities or logits.
        """
        return self.model(state)


class RLPolicy:
    """
    A reinforcement learning policy with dynamic adaptation.
    """
    def __init__(
        self, 
        state_dim, 
        action_dim, 
        lr=1e-3, 
        gamma=0.99, 
        epsilon_start=1.0, 
        epsilon_end=0.01, 
        epsilon_decay=500, 
        hidden_layers=[128, 128],
        adaptive=True
    ):
        """
        Initialize the RL policy.

        Args:
            state_dim (int): Dimensionality of the state space.
            action_dim (int): Dimensionality of the action space.
            lr (float): Learning rate for the optimizer.
            gamma (float): Discount factor for rewards.
            epsilon_start (float): Initial epsilon for epsilon-greedy strategy.
            epsilon_end (float): Minimum epsilon for epsilon-greedy strategy.
            epsilon_decay (int): Decay rate for epsilon.
            hidden_layers (list): List of hidden layer sizes.
            adaptive (bool): Whether to enable dynamic adaptation.
        """
        self.state_dim = state_dim
        self.action_dim = action_dim
        self.gamma = gamma
        self.epsilon = epsilon_start
        self.epsilon_min = epsilon_end
        self.epsilon_decay = epsilon_decay
        self.adaptive = adaptive

        # Initialize networks
        self.policy_network = PolicyNetwork(state_dim, action_dim, hidden_layers)
        self.optimizer = optim.Adam(self.policy_network.parameters(), lr=lr)
        self.criterion = nn.MSELoss()

        # Experience replay buffer
        self.replay_buffer = deque(maxlen=10000)

        # Dynamic adaptation parameters
        self.adaptation_threshold = 0.1
        self.adaptation_factor = 1.05

    def select_action(self, state, train=True):
        """
        Select an action using an epsilon-greedy or adaptive strategy.

        Args:
            state (np.ndarray): The current state.
            train (bool): Whether the policy is in training mode.

        Returns:
            int: The selected action.
        """
        if train and random.random() < self.epsilon:
            # Exploration: Choose a random action
            return random.randint(0, self.action_dim - 1)
        else:
            # Exploitation: Choose the action with the highest predicted value
            state_tensor = torch.FloatTensor(state).unsqueeze(0)
            with torch.no_grad():
                action_probs = self.policy_network(state_tensor)
            return torch.argmax(action_probs).item()

    def update_policy(self, batch_size=64):
        """
        Update the policy network using experience replay.

        Args:
            batch_size (int): Number of experiences to sample from the buffer.
        """
        if len(self.replay_buffer) < batch_size:
            return

        # Sample a random batch of experiences
        batch = random.sample(self.replay_buffer, batch_size)
        states, actions, rewards, next_states, dones = zip(*batch)

        states = torch.FloatTensor(states)
        actions = torch.LongTensor(actions)
        rewards = torch.FloatTensor(rewards)
        next_states = torch.FloatTensor(next_states)
        dones = torch.FloatTensor(dones)

        # Calculate target Q-values
        with torch.no_grad():
            next_q_values = self.policy_network(next_states).max(dim=1)[0]
            targets = rewards + (1 - dones) * self.gamma * next_q_values

        # Predicted Q-values
        q_values = self.policy_network(states).gather(1, actions.unsqueeze(-1)).squeeze(-1)

        # Compute loss and update policy network
        loss = self.criterion(q_values, targets)
        self.optimizer.zero_grad()
        loss.backward()
        self.optimizer.step()

        # Decay epsilon
        if self.adaptive:
            self._adapt_epsilon(loss.item())
        else:
            self.epsilon = max(self.epsilon_min, self.epsilon * np.exp(-1 / self.epsilon_decay))

    def _adapt_epsilon(self, loss):
        """
        Dynamically adapt epsilon based on loss value.

        Args:
            loss (float): Current loss value.
        """
        if loss < self.adaptation_threshold:
            self.epsilon = max(self.epsilon_min, self.epsilon / self.adaptation_factor)
        else:
            self.epsilon = min(1.0, self.epsilon * self.adaptation_factor)

    def store_experience(self, state, action, reward, next_state, done):
        """
        Store an experience in the replay buffer.

        Args:
            state (np.ndarray): The current state.
            action (int): The action taken.
            reward (float): The reward received.
            next_state (np.ndarray): The next state.
            done (bool): Whether the episode is done.
        """
        self.replay_buffer.append((state, action, reward, next_state, done))


# Example Usage
if __name__ == "__main__":
    policy = RLPolicy(state_dim=10, action_dim=4)

    # Simulate interaction with the environment
    for episode in range(10):
        state = np.random.rand(10)  # Random initial state
        total_reward = 0
        done = False

        while not done:
            action = policy.select_action(state)
            next_state = np.random.rand(10)  # Random next state
            reward = random.random()  # Random reward
            done = random.choice([True, False])  # Random termination
            total_reward += reward

            policy.store_experience(state, action, reward, next_state, done)
            state = next_state

        policy.update_policy()
        print(f"Episode {episode + 1}: Total Reward = {total_reward:.2f}, Epsilon = {policy.epsilon:.2f}")

    # Future Enhancements:
    """
    Entropy Regularization: Encourage exploration by penalizing overconfidence in action selection.
    Policy Gradient: Add support for advanced methods like Advantage Actor-Critic (A2C) or Proximal Policy Optimization (PPO).
    Multi-Agent Compatibility: Extend for cooperative or competitive multi-agent systems.
    Transfer Learning: Allow pre-trained policies to adapt to new environments.
    """
