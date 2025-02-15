import unittest
import numpy as np
import tempfile
import os

from core.reinforcement_learning.agent import RLAgent
from core.hive_mind import HiveMind

class TestHiveMindRLIntegration(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Create temporary directory for test artifacts
        cls.test_dir = tempfile.mkdtemp()
        cls.config_path = os.path.join(cls.test_dir, "test_config.ini")
        with open(cls.config_path, "w") as f:
            f.write("""
[MODEL]
learning_rate = 0.001
gamma = 0.99
epsilon = 0.1
[DATA]
dataset_path = test_dataset.json
            """)

    def setUp(self):
        self.state_size = 4
        self.action_size = 2
        self.agent = RLAgent(
            state_size=self.state_size,
            action_size=self.action_size,
            model_save_path=self.test_dir
        )
        self.hive_mind = HiveMind(config_file=self.config_path)

    @classmethod
    def tearDownClass(cls):
        # Cleanup temporary files
        import shutil
        shutil.rmtree(cls.test_dir)

    def test_hyperparameter_optimization(self):
        initial_params = {
            'learning_rate': self.agent.learning_rate,
            'gamma': self.agent.gamma,
            'epsilon': self.agent.epsilon
        }
        
        # Run optimization with explicit parameters
        optimized_params = self.hive_mind.optimize_hyperparameters(
            population_size=2,
            generations=2,
            mutation_rate=0.1
        )
        
        self.agent.update_parameters(optimized_params)
        
        # Verify at least one parameter has changed
        self.assertTrue(any(
            initial_params[param] != getattr(self.agent, param)
            for param in initial_params
        ))

    def test_model_architecture(self):
        # Test if model architecture can be customized
        layer_sizes = [128, 64]
        model = self.agent._build_model(layer_sizes=layer_sizes)
        
        # Verify layer sizes
        self.assertEqual(len(model.layers), len(layer_sizes) + 1)
        for i, layer in enumerate(model.layers[:-1]):
            self.assertEqual(layer.units, layer_sizes[i])

    def test_evaluation_metrics(self):
        # Mock environment
        class MockEnv:
            def reset(self):
                return np.zeros(self.agent.state_size)
            
            def step(self, action):
                return np.zeros(self.agent.state_size), 1.0, False, {}
        
        env = MockEnv()
        results = self.agent.evaluate(env)
        
        # Verify evaluation metrics
        self.assertIn('total_rewards', results)
        self.assertIn('episode_lengths', results)
        self.assertIn('average_reward', results)

    def test_error_handling(self):
        # Test invalid hyperparameters
        with self.assertRaises(ValueError):
            self.agent = RLAgent(self.state_size, self.action_size, learning_rate=-0.1)
        
        # Test invalid layer sizes
        with self.assertRaises(ValueError):
            self.agent._build_model(layer_sizes=[])

if __name__ == '__main__':
    unittest.main()
