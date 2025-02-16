import numpy as np
from typing import Dict, List
from sklearn.ensemble import IsolationForest

class AnomalyDetector:
    def __init__(self):
        self.model = IsolationForest(contamination=0.1)
        self.update_history = []
        self.trained = False

    def is_anomalous(self, weights: Dict[str, np.ndarray]) -> bool:
        """Check if model update is anomalous"""
        try:
            # Convert weights to feature vector
            features = self._extract_features(weights)
            
            # Train model if needed
            if len(self.update_history) > 100 and not self.trained:
                self._train_model()

            # Detect anomalies
            if self.trained:
                prediction = self.model.predict([features])[0]
                return prediction == -1  # -1 indicates anomaly
            
            # Basic statistical check if model not trained
            return self._basic_anomaly_check(features)

        except Exception:
            return True  # Treat errors as anomalies

    def _extract_features(self, weights: Dict[str, np.ndarray]) -> List[float]:
        """Extract statistical features from weights"""
        features = []
        for layer_weights in weights.values():
            features.extend([
                np.mean(layer_weights),
                np.std(layer_weights),
                np.max(np.abs(layer_weights)),
                np.percentile(layer_weights, 90)
            ])
        return features

    def _train_model(self):
        """Train anomaly detection model"""
        X = np.array(self.update_history)
        self.model.fit(X)
        self.trained = True

    def _basic_anomaly_check(self, features: List[float]) -> bool:
        """Basic statistical anomaly check"""
        if len(self.update_history) < 2:
            self.update_history.append(features)
            return False

        mean = np.mean(self.update_history, axis=0)
        std = np.std(self.update_history, axis=0)
        z_scores = np.abs((features - mean) / (std + 1e-10))
        
        self.update_history.append(features)
        return np.any(z_scores > 3.0)  # Z-score threshold
