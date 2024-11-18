import json
from .episodic_memory import EpisodicMemory
from .semantic_memory import SemanticMemory
from .procedural_memory import ProceduralMemory
from .cognitive_model import CognitiveModel
from .util import Logger
from .learning_algorithm import LearningAlgorithm
from .multi_modal_memory import MultiModalMemory
from .distributed_memory import DistributedMemory
from .self_awareness import SelfAwareness

class MemoryController:
    def __init__(self, config_path="configs/memory_config.json"):
        self.config = self.load_config(config_path)
        self.logger = Logger()  # Enhanced logging for memory actions
        self.learning_algorithm = LearningAlgorithm(self.config['learning_algorithm'])  # Adaptive learning

        # Initialize memory components
        self.episodic_memory = EpisodicMemory(self.config['episodic'])
        self.semantic_memory = SemanticMemory(self.config['semantic'])
        self.procedural_memory = ProceduralMemory(self.config['procedural'])  # New procedural memory
        self.multi_modal_memory = MultiModalMemory(self.config['multi_modal'])  # Multi-modal memory for various data types
        self.distributed_memory = DistributedMemory(self.config['distributed'])  # Distributed memory across nodes
        self.self_awareness = SelfAwareness(self.config['self_awareness'])  # Self-awareness for introspection

        # Cognitive model for decision-making and recall (higher-order processing)
        self.cognitive_model = CognitiveModel(self.config['cognitive'])

        # Store memory configuration details for future references
        self.memory_usage_stats = {
            'episodic_memory_usage': 0,
            'semantic_memory_usage': 0,
            'procedural_memory_usage': 0,
            'multi_modal_memory_usage': 0,
            'distributed_memory_usage': 0,
        }

    def load_config(self, config_path):
        """ Load memory configuration from file """
        try:
            with open(config_path, 'r') as file:
                return json.load(file)
        except FileNotFoundError:
            self.logger.log_error(f"Configuration file {config_path} not found!")
            raise
        except json.JSONDecodeError:
            self.logger.log_error(f"Error decoding configuration file {config_path}!")
            raise

    def store_episodic_memory(self, data):
        """ Store episodic memory (specific events, experiences) """
        try:
            self.episodic_memory.store(data)
            self.logger.log_info(f"Episodic memory stored: {data}")
            self.memory_usage_stats['episodic_memory_usage'] += 1  # Track memory usage
        except Exception as e:
            self.logger.log_error(f"Error storing episodic memory: {e}")

    def retrieve_episodic_memory(self, query):
        """ Retrieve episodic memory """
        try:
            result = self.episodic_memory.retrieve(query)
            self.logger.log_info(f"Episodic memory retrieved: {result}")
            return result
        except Exception as e:
            self.logger.log_error(f"Error retrieving episodic memory: {e}")
            return None

    def store_semantic_memory(self, data):
        """ Store semantic memory (general knowledge) """
        try:
            self.semantic_memory.store(data)
            self.logger.log_info(f"Semantic memory stored: {data}")
            self.memory_usage_stats['semantic_memory_usage'] += 1  # Track memory usage
        except Exception as e:
            self.logger.log_error(f"Error storing semantic memory: {e}")

    def retrieve_semantic_memory(self, query):
        """ Retrieve semantic memory """
        try:
            result = self.semantic_memory.retrieve(query)
            self.logger.log_info(f"Semantic memory retrieved: {result}")
            return result
        except Exception as e:
            self.logger.log_error(f"Error retrieving semantic memory: {e}")
            return None

    def store_procedural_memory(self, data):
        """ Store procedural memory (how-to knowledge, skills) """
        try:
            self.procedural_memory.store(data)
            self.logger.log_info(f"Procedural memory stored: {data}")
            self.memory_usage_stats['procedural_memory_usage'] += 1  # Track memory usage
        except Exception as e:
            self.logger.log_error(f"Error storing procedural memory: {e}")

    def retrieve_procedural_memory(self, query):
        """ Retrieve procedural memory """
        try:
            result = self.procedural_memory.retrieve(query)
            self.logger.log_info(f"Procedural memory retrieved: {result}")
            return result
        except Exception as e:
            self.logger.log_error(f"Error retrieving procedural memory: {e}")
            return None

    def store_multi_modal_memory(self, data):
        """ Store multi-modal memory (e.g., visual, auditory, sensory) """
        try:
            self.multi_modal_memory.store(data)
            self.logger.log_info(f"Multi-modal memory stored: {data}")
            self.memory_usage_stats['multi_modal_memory_usage'] += 1  # Track memory usage
        except Exception as e:
            self.logger.log_error(f"Error storing multi-modal memory: {e}")

    def retrieve_multi_modal_memory(self, query):
        """ Retrieve multi-modal memory """
        try:
            result = self.multi_modal_memory.retrieve(query)
            self.logger.log_info(f"Multi-modal memory retrieved: {result}")
            return result
        except Exception as e:
            self.logger.log_error(f"Error retrieving multi-modal memory: {e}")
            return None

    def store_distributed_memory(self, data):
        """ Store distributed memory across nodes (collaborative memory) """
        try:
            self.distributed_memory.store(data)
            self.logger.log_info(f"Distributed memory stored: {data}")
            self.memory_usage_stats['distributed_memory_usage'] += 1  # Track memory usage
        except Exception as e:
            self.logger.log_error(f"Error storing distributed memory: {e}")

    def retrieve_distributed_memory(self, query):
        """ Retrieve distributed memory from networked nodes """
        try:
            result = self.distributed_memory.retrieve(query)
            self.logger.log_info(f"Distributed memory retrieved: {result}")
            return result
        except Exception as e:
            self.logger.log_error(f"Error retrieving distributed memory: {e}")
            return None

    def analyze_memory(self):
        """ Analyze and optimize memory usage """
        try:
            self.episodic_memory.analyze()
            self.semantic_memory.analyze()
            self.procedural_memory.analyze()
            self.multi_modal_memory.analyze()
            self.distributed_memory.analyze()

            # Optimize memory based on analysis
            self.learning_algorithm.optimize_memory(self.episodic_memory, self.semantic_memory, 
                                                    self.procedural_memory, self.multi_modal_memory, 
                                                    self.distributed_memory)
            self.logger.log_info("Memory analysis complete and optimization applied.")
        except Exception as e:
            self.logger.log_error(f"Error analyzing and optimizing memory: {e}")

    def perform_adaptive_learning(self):
        """ Trigger adaptive learning based on changes in memory or environment """
        try:
            # Perform adaptive learning to optimize memory use
            self.learning_algorithm.adapt_to_changes(self.episodic_memory, self.semantic_memory, 
                                                     self.procedural_memory, self.multi_modal_memory, 
                                                     self.distributed_memory)
            self.logger.log_info("Adaptive learning triggered successfully.")
        except Exception as e:
            self.logger.log_error(f"Error triggering adaptive learning: {e}")

    def update_self_awareness(self, new_data):
        """ Update self-awareness based on memory and experiences """
        try:
            self.self_awareness.update(new_data)
            self.logger.log_info(f"Self-awareness updated with new data: {new_data}")
        except Exception as e:
            self.logger.log_error(f"Error updating self-awareness: {e}")

    def share_memory_across_nodes(self, data):
        """ Share memory data with other nodes (agents) in the system for collective learning """
        try:
            # Implement memory sharing logic across nodes (AGI network)
            # Data is shared and synchronized with other nodes to allow collective learning.
            # This could involve sending data to a central server or peer-to-peer communication.
            self.logger.log_info(f"Sharing memory across nodes: {data}")
            # Simulate memory sharing
            return True  # Assume sharing is successful
        except Exception as e:
            self.logger.log_error(f"Error sharing memory across nodes: {e}")
            return False

    def update_cognitive_model(self, new_data):
        """ Update cognitive model based on new memories and experiences """
        try:
            self.cognitive_model.update(new_data)
            self.logger.log_info(f"Cognitive model updated with new data: {new_data}")
        except Exception as e:
            self.logger.log_error(f"Error updating cognitive model: {e}")

    def get_memory_stats(self):
        """ Retrieve current memory usage statistics """
        return self.memory_usage_stats

    def get_cognitive_model_state(self):
        """ Retrieve the current state of the cognitive model """
        return self.cognitive_model.get_state()

    def optimize_memory(self):
        """ Optimize overall memory management based on the latest analysis and cognitive model """
        try:
            # Consolidate memory strategies based on cognitive model
            self.cognitive_model.apply_memory_optimization(self.episodic_memory, self.semantic_memory, 
                                                           self.procedural_memory, self.multi_modal_memory, 
                                                           self.distributed_memory)
            self.logger.log_info("Memory optimization applied based on cognitive model.")
        except Exception as e:
            self.logger.log_error(f"Error applying memory optimization: {e}")
