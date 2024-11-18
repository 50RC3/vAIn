# visualization.py
# Advanced AGI Visualization for Insights, Metrics, and Decision-making

import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import pandas as pd
from sklearn.decomposition import PCA
from sklearn.manifold import TSNE
from .utils import load_data, process_data

class AGIVisualizer:
    def __init__(self, model, data_loader, task_manager):
        """
        Initialize AGIVisualizer to track and visualize AGI system progress, performance, and task execution.
        :param model: The AGI model being developed and trained (can be a reinforcement learning model, NLP model, etc.)
        :param data_loader: DataLoader object to fetch and preprocess relevant data for visualization
        :param task_manager: TaskManager to access task history and performance for visual tracking
        """
        self.model = model
        self.data_loader = data_loader
        self.task_manager = task_manager

    def visualize_model_performance(self):
        """
        Visualize the performance of the AGI model over time, including metrics such as accuracy, reward, loss, etc.
        """
        performance_data = self.model.get_performance_metrics()  # Assuming model tracks metrics like accuracy, reward, etc.
        epochs = np.arange(len(performance_data['loss']))
        
        plt.figure(figsize=(10, 6))
        plt.plot(epochs, performance_data['loss'], label='Loss')
        plt.plot(epochs, performance_data['accuracy'], label='Accuracy')
        plt.title('Model Performance Over Time')
        plt.xlabel('Epochs')
        plt.ylabel('Metrics')
        plt.legend()
        plt.grid(True)
        plt.show()

    def visualize_latent_space(self, data=None):
        """
        Visualize the latent space learned by the AGI model to gain insight into its representation of tasks or input data.
        :param data: The data to visualize. If None, will load from DataLoader.
        """
        if data is None:
            data = self.data_loader.load_data()
        
        # Assume the model has a method to extract its latent space representation
        latent_representation = self.model.get_latent_space(data)
        
        # Apply dimensionality reduction for visualization
        pca = PCA(n_components=2)
        reduced_data = pca.fit_transform(latent_representation)
        
        plt.figure(figsize=(10, 6))
        plt.scatter(reduced_data[:, 0], reduced_data[:, 1], c='b', alpha=0.5)
        plt.title('Latent Space Visualization (PCA Reduced)')
        plt.xlabel('Principal Component 1')
        plt.ylabel('Principal Component 2')
        plt.grid(True)
        plt.show()

    def visualize_task_progress(self):
        """
        Visualize task execution progress, showing the AGI's task history, success rate, and learning trajectory.
        """
        task_history = self.task_manager.get_task_history()
        task_ids = [task['task_id'] for task in task_history]
        success_rate = [task['success_rate'] for task in task_history]
        task_times = [task['time_taken'] for task in task_history]

        # Plot task success rate and time taken
        fig, ax1 = plt.subplots(figsize=(10, 6))

        ax1.set_xlabel('Task ID')
        ax1.set_ylabel('Success Rate', color='tab:blue')
        ax1.plot(task_ids, success_rate, color='tab:blue', label='Success Rate')
        ax1.tick_params(axis='y', labelcolor='tab:blue')

        ax2 = ax1.twinx()  # Create a second y-axis to plot task time
        ax2.set_ylabel('Time Taken (s)', color='tab:green')
        ax2.plot(task_ids, task_times, color='tab:green', label='Time Taken')
        ax2.tick_params(axis='y', labelcolor='tab:green')

        plt.title('Task Progress Visualization: Success Rate and Time Taken')
        fig.tight_layout()
        plt.show()

    def visualize_decision_making(self, state, action, reward):
        """
        Visualize the decision-making process of the AGI model for a specific state-action pair.
        :param state: Current state of the AGI agent
        :param action: Action taken by the agent
        :param reward: Reward received after taking the action
        """
        state_info = self.model.get_state_info(state)
        action_info = self.model.get_action_info(action)
        
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 6))
        
        # Visualize the state information (can be based on image, vector data, etc.)
        ax1.imshow(state_info, cmap='gray')
        ax1.set_title('State Representation')
        ax1.axis('off')

        # Visualize the action choice and the resulting reward
        ax2.bar(action_info.keys(), action_info.values(), color='b')
        ax2.set_title(f'Action: {action} - Reward: {reward}')
        ax2.set_xlabel('Action Features')
        ax2.set_ylabel('Value')

        plt.tight_layout()
        plt.show()

    def visualize_task_network(self, task_data=None):
        """
        Visualize the relationships between tasks in the AGI system, including dependencies, execution sequences, and outcomes.
        :param task_data: Task-related data for visualization. If None, it loads from TaskManager.
        """
        if task_data is None:
            task_data = self.task_manager.get_task_network_data()
        
        # Visualize task dependencies and relationships
        task_df = pd.DataFrame(task_data)
        task_graph = sns.heatmap(task_df.corr(), annot=True, cmap='coolwarm', fmt='.2f')
        task_graph.set_title('Task Dependency and Correlation Network')
        plt.show()

# Example Usage:
# Assuming `model`, `data_loader`, and `task_manager` are components of the vAIn system
# visualizer = AGIVisualizer(model, data_loader, task_manager)
# visualizer.visualize_model_performance()
# visualizer.visualize_latent_space()
# visualizer.visualize_task_progress()
