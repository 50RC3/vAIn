import numpy as np
import random
import time

class EvolvingEnvironment:
    """
    Enhanced environment for training AGI-like agents.
    Includes dynamic challenges, hierarchical objectives, and a persistent state.
    """

    def __init__(self, grid_size=(10, 10), max_steps=500, evolution_rate=0.05):
        """
        Initialize the evolving environment.

        Args:
            grid_size (tuple): The dimensions of the grid environment.
            max_steps (int): Maximum number of steps per episode.
            evolution_rate (float): Probability of environment evolving per step.
        """
        self.grid_size = grid_size
        self.max_steps = max_steps
        self.evolution_rate = evolution_rate
        self.state = None
        self.steps = 0
        self.done = False
        self.objectives = {}
        self.reset()

    def reset(self):
        """
        Reset the environment to the initial state.

        Returns:
            state (np.ndarray): The initial state of the environment.
        """
        self.state = np.zeros(self.grid_size)  # Initialize a zero grid
        self.agent_position = [0, 0]  # Agent starts at top-left
        self.steps = 0
        self.done = False

        # Initialize dynamic objectives
        self._initialize_objectives()
        return self._get_state_representation()

    def step(self, action):
        """
        Take a step in the environment.

        Args:
            action (int): The action chosen by the agent.

        Returns:
            state (np.ndarray): The next state after taking the action.
            reward (float): The reward for the action taken.
            done (bool): Whether the episode is finished.
            info (dict): Additional information about the environment.
        """
        if self.done:
            return self._get_state_representation(), 0, True, {}

        # Move the agent based on the action
        self._move_agent(action)

        # Calculate reward and check objectives
        reward = self._calculate_reward()

        # Increment step counter and possibly evolve the environment
        self.steps += 1
        if random.random() < self.evolution_rate:
            self._evolve_environment()

        # Check if the environment is done
        if self.steps >= self.max_steps:
            self.done = True

        return self._get_state_representation(), reward, self.done, {}

    def _move_agent(self, action):
        """
        Move the agent within the environment.

        Args:
            action (int): The chosen action.
        """
        moves = {
            0: (0, 1),   # Right
            1: (1, 0),   # Down
            2: (0, -1),  # Left
            3: (-1, 0),  # Up
        }
        move = moves.get(action, (0, 0))
        new_row = self.agent_position[0] + move[0]
        new_col = self.agent_position[1] + move[1]

        # Keep the agent within bounds
        if 0 <= new_row < self.grid_size[0] and 0 <= new_col < self.grid_size[1]:
            self.agent_position = [new_row, new_col]

    def _calculate_reward(self):
        """
        Calculate the reward based on the agent's position and objectives.

        Returns:
            reward (float): The calculated reward.
        """
        reward = 0
        position = tuple(self.agent_position)

        # Check if agent reached an objective
        if position in self.objectives:
            reward += self.objectives[position]["reward"]
            del self.objectives[position]  # Remove completed objective

        # Reward for movement or exploration
        reward += -0.1  # Small penalty to encourage efficiency

        return reward

    def _initialize_objectives(self):
        """
        Initialize dynamic objectives within the environment.
        """
        num_objectives = random.randint(5, 10)  # Number of objectives to start with
        for _ in range(num_objectives):
            position = (
                random.randint(0, self.grid_size[0] - 1),
                random.randint(0, self.grid_size[1] - 1),
            )
            self.objectives[position] = {"reward": random.uniform(1, 5)}

    def _evolve_environment(self):
        """
        Evolve the environment by modifying objectives or the state.
        """
        # Add new objectives randomly
        if random.random() < 0.5:
            position = (
                random.randint(0, self.grid_size[0] - 1),
                random.randint(0, self.grid_size[1] - 1),
            )
            if position not in self.objectives:
                self.objectives[position] = {"reward": random.uniform(2, 10)}

        # Introduce obstacles or dynamic changes
        for _ in range(random.randint(1, 3)):
            row = random.randint(0, self.grid_size[0] - 1)
            col = random.randint(0, self.grid_size[1] - 1)
            self.state[row, col] = -1  # Mark as an obstacle

    def _get_state_representation(self):
        """
        Get a representation of the current state.

        Returns:
            state (np.ndarray): The current state representation.
        """
        state = np.copy(self.state)
        state[self.agent_position[0], self.agent_position[1]] = 1  # Mark agent's position
        return state

    def render(self):
        """
        Render the environment for visualization.

        Returns:
            None
        """
        visual = np.copy(self.state)
        visual[self.agent_position[0], self.agent_position[1]] = 1  # Agent's position
        print(f"Step: {self.steps}")
        print(visual)
        print(f"Objectives: {self.objectives}")
        print("-----")


# Example Usage
if __name__ == "__main__":
    env = EvolvingEnvironment(grid_size=(10, 10), max_steps=100)
    state = env.reset()
    done = False
    total_reward = 0

    while not done:
        action = random.choice([0, 1, 2, 3])  # Random action for testing
        next_state, reward, done, info = env.step(action)
        total_reward += reward
        env.render()

    print(f"Total reward after episode: {total_reward}")
    
    # Future Enhancements:
    """
    Multi-Agent Interaction: Add multiple agents to simulate cooperation or competition.
    Complex Reward Signals: Introduce composite rewards involving dependencies on time, action sequences, or other agents.
    State Abstraction: Provide partial observations, requiring the agent to infer hidden states.
    Adaptable Evolution Rates: Dynamically adjust the rate of evolution based on agent performance.
    """    
