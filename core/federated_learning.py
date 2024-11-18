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

    def __init__(self, global_model: Any, client_models: List[Any], aggregation_method: str = "average", learning_rate: float = 0.01, patience: int = 3, checkpoint_dir: str = "./checkpoints", adaptive: bool = False, secure_aggregation: bool = True):
        """
        Initialize FederatedLearning with a global model, client models, aggregation method, learning rate, early stopping patience, and checkpoint directory.

        Args:
            global_model (Any): The initial global model.
            client_models (List[Any]): Models used by each client.
            aggregation_method (str): Method to aggregate client updates. Default is "average".
            learning_rate (float): Learning rate for global model update. Default is 0.01.
            patience (int): Number of epochs without improvement before early stopping. Default is 3.
            checkpoint_dir (str): Directory to save model checkpoints. Default is "./checkpoints".
            adaptive (bool): Flag to enable adaptive learning strategies. Default is False.
            secure_aggregation (bool): Flag to enable secure aggregation. Default is True.
        """
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

        # Set up logging
        self.logger = logging.getLogger(__name__)
        logging.basicConfig(level=logging.INFO)

        # Create checkpoints directory if it doesn't exist
        os.makedirs(checkpoint_dir, exist_ok=True)

    def distribute_model(self):
        """
        Distribute the global model to all clients.
        """
        for client_model in self.client_models:
            client_model.set_weights(self.global_model.get_weights())

    def aggregate_updates(self, client_updates: List[Dict[str, Any]]):
        """
        Aggregate client updates into the global model with additional privacy and robustness measures.

        Args:
            client_updates (List[Dict[str, Any]]): Updates from clients.
        """
        if not client_updates:
            raise ValueError("Client updates cannot be empty.")

        # Secure Aggregation (e.g., using simple randomization or adding noise)
        if self.secure_aggregation:
            client_updates = self._secure_aggregation(client_updates)

        if self.aggregation_method == "average":
            self._average_aggregation(client_updates)
        elif self.aggregation_method == "median":
            self._median_aggregation(client_updates)
        elif self.aggregation_method == "weighted_average":
            self._weighted_average_aggregation(client_updates)
        else:
            raise ValueError(f"Unsupported aggregation method: {self.aggregation_method}")

    def _secure_aggregation(self, client_updates: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Apply simple secure aggregation by adding noise (e.g., Gaussian noise) to client updates.
        
        Args:
            client_updates (List[Dict[str, Any]]): Updates from clients.
        """
        noise_factor = 0.1  # Noise level to ensure privacy
        for update in client_updates:
            for key in update["weights"]:
                update["weights"][key] += np.random.normal(0, noise_factor, update["weights"][key].shape)
        return client_updates

    def _average_aggregation(self, client_updates: List[Dict[str, Any]]):
        """
        Aggregate updates using simple averaging.

        Args:
            client_updates (List[Dict[str, Any]]): Updates from clients.
        """
        aggregated_weights = {key: np.mean([update["weights"][key] for update in client_updates], axis=0)
                              for key in client_updates[0]["weights"]}
        self.global_model.set_weights(aggregated_weights)

    def _median_aggregation(self, client_updates: List[Dict[str, Any]]):
        """
        Aggregate updates using median.

        Args:
            client_updates (List[Dict[str, Any]]): Updates from clients.
        """
        aggregated_weights = {key: np.median([update["weights"][key] for update in client_updates], axis=0)
                              for key in client_updates[0]["weights"]}
        self.global_model.set_weights(aggregated_weights)

    def _weighted_average_aggregation(self, client_updates: List[Dict[str, Any]]):
        """
        Aggregate updates using a weighted average.

        Args:
            client_updates (List[Dict[str, Any]]): Updates from clients.
        """
        total_samples = sum(update["num_samples"] for update in client_updates)
        aggregated_weights = {
            key: sum(update["weights"][key] * update["num_samples"] / total_samples for update in client_updates)
            for key in client_updates[0]["weights"]
        }
        self.global_model.set_weights(aggregated_weights)

    def async_train_clients(self, train_data: List[Any], epochs: int = 1) -> List[Dict[str, Any]]:
        """
        Train client models asynchronously.

        Args:
            train_data (List[Any]): Data for each client.
            epochs (int): Number of epochs for training.

        Returns:
            List[Dict[str, Any]]: Updates from each client.
        """
        client_updates = []
        threads = []
        
        # Start threads for each client training
        for client_model, data in zip(self.client_models, train_data):
            thread = Thread(target=self._train_client, args=(client_model, data, epochs, client_updates))
            thread.start()
            threads.append(thread)

        # Wait for all threads to finish
        for thread in threads:
            thread.join()

        return client_updates

    def _train_client(self, client_model, data, epochs, client_updates):
        """
        Train a single client model.

        Args:
            client_model: The model of the client.
            data: Data for training.
            epochs: Number of epochs for training.
            client_updates: List to store updates from clients.
        """
        client_model.train(data, epochs)
        update = {
            "weights": client_model.get_weights(),
            "num_samples": len(data)
        }
        client_updates.append(update)

    def robust_client_selection(self, client_data: List[Any], performance_metric: str = "accuracy", selection_ratio: float = 0.5) -> List[Any]:
        """
        Select clients based on a performance metric.

        Args:
            client_data (List[Any]): Data for each client.
            performance_metric (str): Metric to evaluate client performance.
            selection_ratio (float): Ratio of clients to select.

        Returns:
            List[Any]: Selected clients.
        """
        sorted_clients = sorted(zip(client_data, performance_metric), key=lambda x: x[1], reverse=True)
        selected_clients = [client for client, _ in sorted_clients[:int(len(client_data) * selection_ratio)]]
        return selected_clients

    def save_checkpoint(self, epoch: int):
        """
        Save the current state of the global model.

        Args:
            epoch (int): Current epoch number.
        """
        checkpoint_path = os.path.join(self.checkpoint_dir, f"checkpoint_epoch_{epoch}.h5")
        self.global_model.save(checkpoint_path)
        self.logger.info(f"Checkpoint saved at {checkpoint_path}")

    def load_checkpoint(self, epoch: int):
        """
        Load a previously saved model state.

        Args:
            epoch (int): Epoch number of the checkpoint to load.
        """
        checkpoint_path = os.path.join(self.checkpoint_dir, f"checkpoint_epoch_{epoch}.h5")
        self.global_model.load(checkpoint_path)
        self.logger.info(f"Checkpoint loaded from {checkpoint_path}")

    def global_training_round(self, train_data: List[Any], epochs: int = 1, validation_data: List[Any] = None):
        """
        Conduct a global training round.

        Args:
            train_data (List[Any]): Data for training.
            epochs (int): Number of epochs for training.
            validation_data (List[Any]): Data for validation.
        """
        self.distribute_model()
        client_updates = self.async_train_clients(train_data, epochs)
        self.aggregate_updates(client_updates)

        # Early stopping based on validation loss
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

        Args:
            validation_data (List[Any]): Validation data.
        """
        return self.global_model.evaluate(validation_data)

