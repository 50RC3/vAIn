import numpy as np
from typing import Dict, List, Any
import logging

logger = logging.getLogger(__name__)

class AnomalyDetector:
    def __init__(self):
        self.baseline_metrics = {}
        self.threshold = 2.0  # Standard deviations from mean
        self.history = {}

    def update_baseline(self, node_id: str, metrics: Dict[str, float]):
        if node_id not in self.baseline_metrics:
            self.baseline_metrics[node_id] = []
        self.baseline_metrics[node_id].append(metrics)
        
        # Keep only last 1000 measurements
        if len(self.baseline_metrics[node_id]) > 1000:
            self.baseline_metrics[node_id].pop(0)

    def check_node(self, node_id: str) -> List[Dict[str, Any]]:
        if node_id not in self.baseline_metrics:
            return []

        anomalies = []
        current_metrics = self.baseline_metrics[node_id][-1]
        historical_metrics = np.array(self.baseline_metrics[node_id][:-1])

        for metric, value in current_metrics.items():
            if len(historical_metrics) > 0:
                mean = np.mean([m[metric] for m in historical_metrics])
                std = np.std([m[metric] for m in historical_metrics])
                
                if abs(value - mean) > self.threshold * std:
                    anomalies.append({
                        "metric": metric,
                        "value": value,
                        "mean": mean,
                        "std": std,
                        "severity": "high" if abs(value - mean) > 3 * std else "medium"
                    })

        return anomalies

    def get_node_status(self, node_id: str) -> Dict[str, Any]:
        anomalies = self.check_node(node_id)
        return {
            "node_id": node_id,
            "anomaly_count": len(anomalies),
            "anomalies": anomalies,
            "status": "unhealthy" if anomalies else "healthy"
        }
