import numpy as np
from typing import Dict, List, Optional
import tensorflow as tf
from datetime import datetime, timedelta
import logging
from .time_series import TransformerPredictor, LSTMPredictor
from .resource_monitor import ResourceMonitor

class PredictiveComputeScheduler:
    def __init__(self, 
                 forecast_horizon: int = 24, 
                 resource_buffer: float = 0.2,
                 update_interval: int = 60):
        self.resource_monitor = ResourceMonitor()
        self.forecast_horizon = forecast_horizon  # hours
        self.resource_buffer = resource_buffer    # 20% buffer
        self.update_interval = update_interval    # minutes
        self.logger = logging.getLogger(__name__)
        
        # Initialize predictive models
        self.transformer = TransformerPredictor(
            input_window=168,  # 1 week of hourly data
            forecast_horizon=forecast_horizon
        )
        self.lstm = LSTMPredictor(
            input_window=168,
            forecast_horizon=forecast_horizon
        )
        
        self.historical_usage = {
            'gpu': [],
            'memory': [],
            'cpu': [],
            'timestamps': []
        }
        
        self.predicted_demands = {}
        self.scheduled_tasks = []
        self.last_prediction = None

    def predict_resource_demand(self, resource_type: str) -> np.ndarray:
        """Predict future resource demand using ensemble of models"""
        if len(self.historical_usage[resource_type]) < 168:
            return np.zeros(self.forecast_horizon)
            
        # Get predictions from both models
        transformer_pred = self.transformer.predict(
            self.historical_usage[resource_type][-168:]
        )
        lstm_pred = self.lstm.predict(
            self.historical_usage[resource_type][-168:]
        )
        
        # Ensemble predictions with weighted average
        # Weight based on recent accuracy
        weights = self._calculate_model_weights()
        ensemble_prediction = (
            weights['transformer'] * transformer_pred +
            weights['lstm'] * lstm_pred
        )
        
        # Add safety buffer
        return ensemble_prediction * (1 + self.resource_buffer)

    def schedule_resources(self, task_requirements: Dict[str, float], 
                         start_time: datetime) -> bool:
        """Schedule resources based on predictions and requirements"""
        future_usage = self._get_future_usage(start_time)
        
        # Update predictions if needed
        if self._should_update_predictions():
            self._update_resource_predictions()
        
        # Check if resources will be available
        if self._can_accommodate_task(task_requirements, future_usage):
            self._allocate_resources(task_requirements, start_time)
            return True
            
        # Try to pre-scale if resources insufficient
        if self._attempt_prescaling(task_requirements, future_usage):
            self._allocate_resources(task_requirements, start_time)
            return True
            
        return False

    def _should_update_predictions(self) -> bool:
        """Check if predictions need updating"""
        if not self.last_prediction:
            return True
            
        time_since_update = datetime.now() - self.last_prediction
        return time_since_update.seconds / 60 >= self.update_interval

    def _update_resource_predictions(self):
        """Update predictions for all resource types"""
        for resource in ['gpu', 'memory', 'cpu']:
            self.predicted_demands[resource] = self.predict_resource_demand(resource)
        self.last_prediction = datetime.now()

    def _can_accommodate_task(self, requirements: Dict[str, float], 
                            future_usage: Dict[str, np.ndarray]) -> bool:
        """Check if task can be accommodated based on predictions"""
        for resource_type, amount in requirements.items():
            if resource_type in future_usage:
                peak_usage = max(future_usage[resource_type])
                available = self.resource_monitor.get_total_capacity(resource_type)
                if peak_usage + amount > available * 0.9:  # 90% threshold
                    return False
        return True

    def _attempt_prescaling(self, requirements: Dict[str, float], 
                          future_usage: Dict[str, np.ndarray]) -> bool:
        """Attempt to pre-scale resources if needed"""
        try:
            scaling_plan = {}
            for resource_type, amount in requirements.items():
                if resource_type in future_usage:
                    needed_capacity = max(future_usage[resource_type]) + amount
                    current_capacity = self.resource_monitor.get_total_capacity(resource_type)
                    if needed_capacity > current_capacity * 0.9:
                        scaling_plan[resource_type] = needed_capacity * 1.2  # 20% buffer
                        
            if scaling_plan:
                return self._execute_scaling_plan(scaling_plan)
            return True
        except Exception as e:
            self.logger.error(f"Pre-scaling failed: {str(e)}")
            return False

    def _execute_scaling_plan(self, scaling_plan: Dict[str, float]) -> bool:
        """Execute the scaling plan"""
        try:
            for resource_type, target_capacity in scaling_plan.items():
                # Implement actual scaling logic here
                self.logger.info(f"Pre-scaling {resource_type} to {target_capacity}")
                # Example: self.cluster_manager.scale_resource(resource_type, target_capacity)
            return True
        except Exception as e:
            self.logger.error(f"Failed to execute scaling plan: {str(e)}")
            return False

    def _calculate_model_weights(self) -> Dict[str, float]:
        """Calculate weights for ensemble models based on recent performance"""
        # Example: Simple 50-50 weighting
        return {'transformer': 0.5, 'lstm': 0.5}
