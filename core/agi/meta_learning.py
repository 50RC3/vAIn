from typing import Dict, List
import numpy as np
import torch
import torch.nn as nn

class MAMLLearner:
    def __init__(self, model: nn.Module, inner_lr: float = 0.01, outer_lr: float = 0.001):
        self.model = model
        self.inner_lr = inner_lr
        self.outer_lr = outer_lr
        self.meta_optimizer = torch.optim.Adam(model.parameters(), lr=outer_lr)
        
    def adapt(self, task_batch: List[Dict], num_inner_steps: int = 5):
        """Adapt to new tasks using MAML"""
        outer_loss = 0.0
        
        for task in task_batch:
            # Clone model for task-specific adaptation
            task_model = self.clone_model()
            
            # Inner loop - task adaptation
            for _ in range(num_inner_steps):
                support_loss = self.compute_loss(task_model, task['support_data'])
                grad = torch.autograd.grad(support_loss, task_model.parameters())
                self.inner_step(task_model, grad)
            
            # Outer loop - meta update
            query_loss = self.compute_loss(task_model, task['query_data'])
            outer_loss += query_loss
            
        # Meta-optimization step
        self.meta_optimizer.zero_grad()
        outer_loss.backward()
        self.meta_optimizer.step()
        
        return outer_loss.item()

    def clone_model(self) -> nn.Module:
        """Create a clone of the model for task adaptation"""
        return copy.deepcopy(self.model)

    def compute_loss(self, model: nn.Module, data: Dict) -> torch.Tensor:
        """Compute task-specific loss"""
        x, y = data['x'], data['y']
        pred = model(x)
        return nn.functional.cross_entropy(pred, y)

    def inner_step(self, model: nn.Module, gradients: List[torch.Tensor]):
        """Perform inner loop optimization step"""
        for param, grad in zip(model.parameters(), gradients):
            param.data = param.data - self.inner_lr * grad
