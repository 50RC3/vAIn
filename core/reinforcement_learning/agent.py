import numpy as np
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense
from tensorflow.keras.optimizers import Adam
import random
import os

class RLAgent:
    """
    A generic reinforcement learning agent supporting various algorithms.
    """

    def __init__(self, state_size: int, action_size: int, algorithm: str = 'DQN', learning_rate: float = 0.001, gamma: float = 0.99, epsilon: float = 1.0, epsilon_min: float = 0.01, epsilon_decay: float = 0.995, batch_size: int = 32, memory_size: int = 10000, model_save_path: str = './models', tau: float = 0.125, use_double_dqn: bool = False):
        """
        Initialize the RL agent.

        Args:
            state_size (int): The size of the state space.
            action_size (int): The size of the action space.
            algorithm (str): The RL algorithm to use, e.g., "DQN", "A3C", "PPO".
            learning_rate (float): The learning rate for training.
            gamma (float): The discount factor for future rewards.
            epsilon (float): The exploration rate for epsilon-greedy strategy.
            epsilon_min (float): The minimum exploration rate.
            epsilon_decay (float): The decay rate for epsilon.
            batch_size (int): The batch size for training.
            memory_size (int): The size of the experience replay buffer.
            model_save_path (str): Path to save model weights.
            tau (float): Soft update parameter for target network in DQN.
            use_double_dqn (bool): Whether to use Double DQN for better stability.
        """
        self.state_size = state_size
        self.action_size = action_size
        self.algorithm = algorithm
        self.learning_rate = learning_rate
        self.gamma = gamma
        self.epsilon = epsilon
        self.epsilon_min = epsilon_min
        self.epsilon_decay = epsilon_decay
        self.batch_size = batch_size
        self.memory_size = memory_size
        self.model_save_path = model_save_path
        self.tau = tau
        self.use_double_dqn = use_double_dqn
        
        # Experience Replay
        self.memory = deque(maxlen=memory_size)
        
        # Initialize the model based on the chosen RL algorithm
        if algorithm == 'DQN':
            self.model = self._build_model()
            self.target_model = self._build_model()
            self._update_target_model()  # Initialize target model with same weights
        else:
            raise NotImplementedError(f"Algorithm {algorithm} is not implemented yet.")
        
        # Initialize optimizer
        self.optimizer = Adam(learning_rate=self.learning_rate)
        
        # Load model if exists
        self._load_model()

    def _build_model(self):
        """
        Build a deep Q-network (DQN) model.

        Returns:
            A Keras model representing the Q-network.
        """
        model = Sequential()
        model.add(Dense(64, input_dim=self.state_size, activation='relu'))
        model.add(Dense(64, activation='relu'))
        model.add(Dense(self.action_size, activation='linear'))  # Linear activation for Q-values
        model.compile(loss='mse', optimizer=self.optimizer)
        return model

    def _update_target_model(self):
        """
        Update the target model with the weights of the primary model.
        """
        self.target_model.set_weights(self.model.get_weights())

    def _epsilon_greedy(self, state: np.ndarray):
        """
        Choose an action using epsilon-greedy strategy.

        Args:
            state (np.ndarray): The current state.

        Returns:
            action (int): The chosen action.
        """
        if np.random.rand() <= self.epsilon:
            return random.randint(0, self.action_size - 1)  # Explore
        q_values = self.model.predict(state)
        return np.argmax(q_values[0])  # Exploit

    def store_experience(self, state: np.ndarray, action: int, reward: float, next_state: np.ndarray, done: bool):
        """
        Store experience in the agent's memory buffer.

        Args:
            state (np.ndarray): The current state.
            action (int): The chosen action.
            reward (float): The received reward.
            next_state (np.ndarray): The next state.
            done (bool): Whether the episode is done.
        """
        self.memory.append((state, action, reward, next_state, done))

    def train(self):
        """
        Train the model using experience replay.
        """
        if len(self.memory) < self.batch_size:
            return  # Not enough experience to train

        # Sample a batch from memory
        batch = random.sample(self.memory, self.batch_size)
        
        for state, action, reward, next_state, done in batch:
            target = reward
            if not done:
                # Predict Q-values for the next state from the target model
                if self.use_double_dqn:
                    next_action = np.argmax(self.model.predict(next_state)[0])
                    target = reward + self.gamma * self.target_model.predict(next_state)[0][next_action]
                else:
                    target = reward + self.gamma * np.amax(self.target_model.predict(next_state)[0])
            
            # Get current Q-values from the model
            target_f = self.model.predict(state)
            target_f[0][action] = target
            
            # Train the model
            self.model.fit(state, target_f, epochs=1, verbose=0)
        
        # Reduce epsilon (exploration rate)
        if self.epsilon > self.epsilon_min:
            self.epsilon *= self.epsilon_decay

    def save_model(self):
        """
        Save the model weights to disk.
        """
        if not os.path.exists(self.model_save_path):
            os.makedirs(self.model_save_path)
        self.model.save_weights(os.path.join(self.model_save_path, 'dqn_weights.h5'))

    def _load_model(self):
        """
        Load model weights from disk if they exist.
        """
        model_path = os.path.join(self.model_save_path, 'dqn_weights.h5')
        if os.path.exists(model_path):
            self.model.load_weights(model_path)
            self.target_model.load_weights(model_path)

    def act(self, state: np.ndarray):
        """
        Choose an action based on the current policy (epsilon-greedy).

        Args:
            state (np.ndarray): The current state.

        Returns:
            action (int): The chosen action.
        """
        return self._epsilon_greedy(state)

    def evaluate(self, environment) -> float:
        """
        Evaluate the agent's performance on a given environment.

        Args:
            environment: The environment to evaluate the agent.

        Returns:
            score (float): The performance score of the agent.
        """
        total_reward = 0
        state = environment.reset()
        done = False

        while not done:
            action = self.act(state)
            next_state, reward, done, _ = environment.step(action)
            total_reward += reward
            state = next_state

        return total_reward


# Example Usage
if __name__ == '__main__':
    # Assume environment has been defined
    state_size = 4  # Example: 4 continuous state features
    action_size = 2  # Example: 2 discrete actions

    agent = RLAgent(state_size=state_size, action_size=action_size, algorithm='DQN')

    for episode in range(1000):
        state = np.reshape(env.reset(), [1, state_size])  # Assuming `env` is defined
        done = False
        while not done:
            action = agent.act(state)
            next_state, reward, done, _ = env.step(action)
            next_state = np.reshape(next_state, [1, state_size])
            agent.store_experience(state, action, reward, next_state, done)
            state = next_state
            agent.train()
        
        if episode % 50 == 0:
            print(f"Episode {episode}: Agent training complete.")
            agent.save_model()  # Save the model periodically
