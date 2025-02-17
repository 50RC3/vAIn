from typing import List, Dict
import psutil
import gputil
import time

class HealthMonitor:
    def __init__(self):
        self.node_stats = {}
        self.healthy_threshold = {
            'cpu': 90.0,  # CPU usage threshold
            'memory': 90.0,  # Memory usage threshold
            'gpu': 85.0,  # GPU usage threshold
            'network': 90.0  # Network bandwidth usage threshold
        }

    def get_healthy_nodes(self) -> List[str]:
        """Return list of healthy node IDs"""
        healthy_nodes = []
        for node_id, stats in self.node_stats.items():
            if self._is_node_healthy(stats):
                healthy_nodes.append(node_id)
        return healthy_nodes

    def _is_node_healthy(self, stats: Dict) -> bool:
        """Check if node metrics are within healthy thresholds"""
        return (stats['cpu'] < self.healthy_threshold['cpu'] and
                stats['memory'] < self.healthy_threshold['memory'] and
                stats['gpu'] < self.healthy_threshold['gpu'] and
                stats['network'] < self.healthy_threshold['network'])

    def update_node_status(self, node_id: str):
        """Update health metrics for a node"""
        self.node_stats[node_id] = {
            'cpu': psutil.cpu_percent(),
            'memory': psutil.virtual_memory().percent,
            'gpu': self._get_gpu_usage(),
            'network': self._get_network_usage(),
            'last_update': time.time()
        }

    def _get_gpu_usage(self) -> float:
        """Get GPU usage if available"""
        try:
            return gputil.getGPUs()[0].load * 100
        except:
            return 0.0

    def _get_network_usage(self) -> float:
        """Get network bandwidth usage"""
        return psutil.net_io_counters().bytes_sent / 1024 / 1024  # MB/s
