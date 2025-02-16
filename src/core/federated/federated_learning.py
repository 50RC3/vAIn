import numpy as np
import os
from threading import Thread
from tensorflow.keras.optimizers import Adam
from typing import List, Dict, Any
import logging

class FederatedLearning:
    """
    A class to manage the federated learning process in the vAIn decentralized AGI system.
    """

    def __init__(self, global_model: Any, client_models: List[Any], aggregation_method: str = "average", 
                 learning_rate: float = 0.01, patience: int = 3, checkpoint_dir: str = "./checkpoints", 
                 adaptive: bool = False, secure_aggregation: bool = True, noise_factor: float = 0.1):
        self.global_model = global_model
        self.client_models = client_models
        self.aggregation_method = aggregation_method
        self.learning_rate = learning_rate
        self.patience = patience
        self.checkpoint_dir = checkpoint_dir
        self.best_loss = float('inf')
        self.epochs_without_improvement = 0
        self.optimizer = Adam(learning_rate=self.learning_rate)
        self.adaptive = adaptive
        self.secure_aggregation = secure_aggregation
        self.noise_factor = noise_factor

        self.logger = logging.getLogger(__name__)
        logging.basicConfig(level=logging.INFO)
        self.logger.info("Federated Learning initialized with aggregation method: %s", self.aggregation_method)

        os.makedirs(checkpoint_dir, exist_ok=True)

        self.health_monitor = HealthMonitor()
        self.anomaly_detector = AnomalyDetector()
        self.zero_knowledge_verifier = ZKPVerifier()

    def _validate_updates(self, model_updates):
        if not model_updates:
            return False
        
        try:
            for update in model_updates:
                if not isinstance(update, dict):
                    return False
            return True
        except Exception:
            return False

    def aggregate_updates(self, client_updates: List[Dict[str, Any]]):
        self.logger.info("Aggregating updates from clients.")
        if not client_updates:
            raise ValueError("Client updates cannot be empty.")
        if self.secure_aggregation:
            client_updates = self._apply_secure_aggregation(client_updates)
        if self.aggregation_method == "average":
            self._average_aggregation(client_updates)
        elif self.aggregation_method == "median":
            self._median_aggregation(client_updates)
        elif self.aggregation_method == "weighted_average":
            self._weighted_average_aggregation(client_updates)
        else:
            raise ValueError(f"Unsupported aggregation method: {self.aggregation_method}")

    def _apply_secure_aggregation(self, client_updates: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        self.logger.info("Applying secure aggregation.")
        for update in client_updates:
            for key in update["weights"]:
                update["weights"][key] = self._add_noise(update["weights"][key])
        return client_updates

    def _add_noise(self, weights: np.ndarray) -> np.ndarray:
        noise = np.random.normal(0, self.noise_factor, weights.shape)
        return weights + noise

    def aggregate_models(self, model_updates):
        if not self._validate_updates(model_updates):
            raise ValueError("Invalid model updates")
        
        try:
            return self._perform_aggregation(model_updates)
        except Exception as e:
            self.logger.error(f"Aggregation failed: {str(e)}")
            raise

    def _perform_aggregation(self, model_updates):
        aggregated_weights = {}
        num_clients = len(model_updates)
        
        for update in model_updates:
            for layer_name, weights in update.items():
                if layer_name not in aggregated_weights:
                    aggregated_weights[layer_name] = np.zeros_like(weights)
                aggregated_weights[layer_name] += weights / num_clients
        
        return aggregated_weights

    def async_train_clients(self, train_data: List[Any], epochs: int = 1) -> List[Dict[str, Any]]:
        self.logger.info("Starting asynchronous training for %d epochs.", epochs)
        client_updates = []
        threads = []
        for client_model, data in zip(self.client_models, train_data):
            thread = Thread(target=self._train_client, args=(client_model, data, epochs, client_updates))
            thread.start()
            threads.append(thread)

        for thread in threads:
            thread.join()
        return client_updates

    def _train_client(self, client_model, data, epochs, client_updates):
        """
        Train a single client model.
        """
        client_model.train(data, epochs)
        update = {
            "weights": client_model.get_weights(),
            "num_samples": len(data)
        }
        client_updates.append(update)

    def distribute_model(self):
        """
        Distribute the global model to all clients.
        """
        self.logger.info("Distributing global model to clients.")
        for client_model in self.client_models:
            client_model.set_weights(self.global_model.get_weights())

    def save_checkpoint(self, epoch: int):
        """
        Save the current state of the global model.
        """
        checkpoint_path = os.path.join(self.checkpoint_dir, f"checkpoint_epoch_{epoch}.h5")
        self.global_model.save(checkpoint_path)
        self.logger.info(f"Checkpoint saved at {checkpoint_path}")

    def load_checkpoint(self, epoch: int):
        """
        Load a previously saved model state.
        """
        checkpoint_path = os.path.join(self.checkpoint_dir, f"checkpoint_epoch_{epoch}.h5")
        self.global_model.load_weights(checkpoint_path)
        self.logger.info(f"Checkpoint loaded from {checkpoint_path}")

    def global_training_round(self, train_data: List[Any], epochs: int = 1, validation_data: List[Any] = None):
        """
        Conduct a global training round.
        """
        self.logger.info("Starting global training round for %d epochs.", epochs)
        self.distribute_model()
        client_updates = self.async_train_clients(train_data, epochs)
        self.aggregate_updates(client_updates)

        if validation_data:
            val_loss = self.evaluate_model(validation_data)
            if val_loss < self.best_loss:
                self.best_loss = val_loss
                self.epochs_without_improvement = 0
                self.save_checkpoint(epochs)
            else:
                self.epochs_without_improvement += 1
                if self.epochs_without_improvement >= self.patience:
                    self.logger.info("Early stopping triggered")
                    return

    def evaluate_model(self, validation_data: List[Any]) -> float:
        """
        Evaluate the global model on validation data.
        """
        self.logger.info("Evaluating model on validation data.")
        return self.global_model.evaluate(validation_data)

    def _validate_client_update(self, client_id: str, update: Dict[str, Any]) -> bool:
        """Validate client updates using zero-knowledge proofs."""
        try:
            # Verify update signature
            if not self.zero_knowledge_verifier.verify_proof(update['proof']):
                self.logger.warning(f"Invalid update proof from client {client_id}")
                return False
                
            # Check for anomalous updates
            if self.anomaly_detector.is_anomalous(update['weights']):
                self.logger.warning(f"Anomalous update detected from client {client_id}")
                return False
                
            return True
        except Exception as e:
            self.logger.error(f"Error validating client update: {str(e)}")
            return False

    def _handle_node_failure(self, failed_node_id: str):
        """Handle node failures by redistributing workload."""
        try:
            # Get healthy nodes
            healthy_nodes = self.health_monitor.get_healthy_nodes()
            
            # Redistribute workload
            workload = self.task_scheduler.get_node_workload(failed_node_id)
            self.task_scheduler.redistribute_workload(workload, healthy_nodes)
            
            # Update network topology
            self.network_manager.update_topology(failed_node_id, "failed")
            
            self.logger.info(f"Successfully handled failure of node {failed_node_id}")
        except Exception as e:
            self.logger.error(f"Error handling node failure: {str(e)}")
