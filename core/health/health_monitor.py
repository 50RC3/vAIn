import numpy as np
from typing import Dict, List, Any
import logging
from .anomaly_detection import AnomalyDetector
from .metrics_collector import MetricsCollector

class HealthMonitor:
    """Monitor and manage system health across the network."""
    
    def __init__(self, threshold: float = 0.7):
        self.logger = logging.getLogger(__name__)
        self.threshold = threshold
        self.metrics_collector = MetricsCollector()
        self.anomaly_detector = AnomalyDetector()
        
    def check_node_health(self, node_id: str) -> Dict[str, Any]:
        """Check health metrics for a specific node."""
        metrics = self.metrics_collector.get_node_metrics(node_id)
        anomalies = self.anomaly_detector.detect(metrics)
        health_score = self._calculate_health_score(metrics)
        
        return {
            "node_id": node_id,
            "health_score": health_score,
            "anomalies": anomalies,
            "metrics": metrics,
            "status": "healthy" if health_score >= self.threshold else "unhealthy"
        }
    
    def get_network_health(self) -> Dict[str, Any]:
        """Get overall network health status."""
        node_healths = self.metrics_collector.get_all_nodes_metrics()
        network_score = np.mean([self._calculate_health_score(nh) for nh in node_healths])
        
        return {
            "network_health_score": network_score,
            "unhealthy_nodes": len([nh for nh in node_healths if nh["health_score"] < self.threshold]),
            "total_nodes": len(node_healths)
        }
    
    def _calculate_health_score(self, metrics: Dict[str, float]) -> float:
        """Calculate health score based on metrics."""
        weights = {
            "cpu_usage": 0.2,
            "memory_usage": 0.2,
            "response_time": 0.3,
            "task_success_rate": 0.3
        }
        
        return sum(metrics[key] * weights[key] for key in weights)
