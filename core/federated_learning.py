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

        # Logging setup
        self.logger = logging.getLogger(__name__)
        logging.basicConfig(level=logging.INFO)

        # Create checkpoints directory
        os.makedirs(checkpoint_dir, exist_ok=True)

    def distribute_model(self):
        for client_model in self.client_models:
            client_model.set_weights(self.global_model.get_weights())

    def aggregate_updates(self, client_updates: List[Dict[str, Any]]):
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
        for update in client_updates:
            for key in update["weights"]:
                update["weights"][key] = self._add_noise(update["weights"][key])
        return client_updates

    def _add_noise(self, weights: np.ndarray) -> np.ndarray:
        noise = np.random.normal(0, self.noise_factor, weights.shape)
        return weights + noise

    def _average_aggregation(self, client_updates: List[Dict[str, Any]]):
        aggregated_weights = {key: np.mean([update["weights"][key] for update in client_updates], axis=0)
                              for key in client_updates[0]["weights"]}
        self.global_model.set_weights(aggregated_weights)

    def _median_aggregation(self, client_updates: List[Dict[str, Any]]):
        aggregated_weights = {key: np.median([update["weights"][key] for update in client_updates], axis=0)
                              for key in client_updates[0]["weights"]}
        self.global_model.set_weights(aggregated_weights)

    def _weighted_average_aggregation(self, client_updates: List[Dict[str, Any]]):
        total_samples = sum(update["num_samples"] for update in client_updates)
        aggregated_weights = {
            key: sum(update["weights"][key] * update["num_samples"] / total_samples for update in client_updates)
            for key in client_updates[0]["weights"]
        }
        self.global_model.set_weights(aggregated_weights)

    def async_train_clients(self, train_data: List[Any], epochs: int = 1) -> List[Dict[str, Any]]:
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
        client_model.train(data, epochs)
        update = {
            "weights": client_model.get_weights(),
            "num_samples": len(data)
        }
        client_updates.append(update)

    def save_checkpoint(self, epoch: int):
        checkpoint_path = os.path.join(self.checkpoint_dir, f"checkpoint_epoch_{epoch}.h5")
        self.global_model.save(checkpoint_path)
        self.logger.info(f"Checkpoint saved at {checkpoint_path}")

    def load_checkpoint(self, epoch: int):
        checkpoint_path = os.path.join(self.checkpoint_dir, f"checkpoint_epoch_{epoch}.h5")
        self.global_model.load_weights(checkpoint_path)
        self.logger.info(f"Checkpoint loaded from {checkpoint_path}")

    def global_training_round(self, train_data: List[Any], epochs: int = 1, validation_data: List[Any] = None):
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
        return self.global_model.evaluate(validation_data)
