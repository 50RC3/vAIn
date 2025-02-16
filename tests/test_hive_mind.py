import pytest
import tempfile
from core.hive_mind import HiveMind, HyperparameterNode
import os

@pytest.fixture
def temp_config_file():
    config_content = """
[MODEL]
num_clusters = 5
max_features = 5000
min_samples = 10
learning_rate = 0.001
gamma = 0.99
epsilon = 0.1

[DATA]
dataset_path = test_dataset.json
backup_interval = 3600
"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.ini', delete=False) as f:
        f.write(config_content)
        temp_path = f.name
    yield temp_path
    os.unlink(temp_path)

@pytest.fixture
def mock_dataset():
    return [{"input": "test", "output": "result"}] * 10

@pytest.fixture(scope="function")
def complex_mock_dataset():
    """Provide more realistic test data"""
    return [
        {"input": "complex query", "output": "detailed result", "metadata": {"confidence": 0.9}},
        {"input": "", "output": "error", "metadata": {"error": "empty input"}},
        # Add edge cases
    ]

@pytest.fixture(autouse=True)
def cleanup_after_test():
    """Ensure cleanup after each test"""
    yield
    # Cleanup code here
    cleanup_test_files()

@pytest.fixture
def hive_mind(temp_config_file, mock_dataset):
    hm = HiveMind(config_file=temp_config_file)
    hm.dataset = mock_dataset
    return hm

def test_hyperparameter_node_creation():
    node = HyperparameterNode("test", "float", value_range=(0.0, 1.0))
    assert node.name == "test"
    assert node.param_type == "float"
    assert node.value_range == (0.0, 1.0)

def test_hyperparameter_node_sample_value():
    node = HyperparameterNode("test", "float", value_range=(0.0, 1.0))
    node.sample_value()
    assert 0.0 <= node.value <= 1.0

def test_hyperparameter_node():
    node = HyperparameterNode("test", "float", value_range=(0, 1))
    node.sample_value()
    assert 0 <= node.value <= 1
    
    config = node.get_config()
    assert "test" in config
    assert isinstance(config["test"], float)

def test_hive_mind_basic_initialization(tmp_path):
    config_file = tmp_path / "test_config.ini"
    hive_mind = HiveMind(config_file=str(config_file))
    assert hive_mind.config is not None
    
    # Test hyperparameter optimization
    config = hive_mind.optimize_hyperparameters(population_size=2, generations=2)
    assert isinstance(config, dict)
    assert "alpha" in config

def test_hive_mind_components(hive_mind):
    assert hive_mind.config is not None
    assert hive_mind.dataset is not None
    assert hive_mind.vectorizer is not None
    assert hive_mind.cluster_model is not None

def test_hyperparameter_tree_creation(hive_mind):
    tree = hive_mind._create_hyperparameter_tree()
    assert tree.name == "Root"
    assert len(tree.children) == 1
    assert tree.children[0].name == "Q-Learning"

def test_optimize_hyperparameters(hive_mind):
    best_config = hive_mind.optimize_hyperparameters(population_size=5, generations=2)
    assert isinstance(best_config, dict)
    assert 'alpha' in best_config
    assert 'gamma' in best_config
    assert 'epsilon' in best_config

def test_evaluate_fitness(hive_mind):
    tree = hive_mind._create_hyperparameter_tree()
    fitness_metrics = hive_mind.evaluate_fitness(tree)
    assert len(fitness_metrics) == 4
    assert all(isinstance(metric, float) for metric in fitness_metrics)
    assert all(0 <= metric <= 1 for metric in fitness_metrics)
