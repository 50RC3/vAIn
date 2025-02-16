# analytics/insights.py
from pathlib import Path
import pandas as pd
import numpy as np
from datetime import datetime
import matplotlib.pyplot as plt
import seaborn as sns
import logging
import os
from dotenv import load_dotenv
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA

# Load environment variables
load_dotenv()

class Insights:
    def __init__(self, data_source: str):
        # Add model cache directory handling
        self.model_cache_dir = Path(os.getenv('MODEL_CACHE_DIR', 'cache/models'))
        self.model_cache_dir.mkdir(parents=True, exist_ok=True)
        
        if not data_source:
            raise ValueError("Data source must be provided")
        
        self.data_source = Path(data_source)
        if not self.data_source.exists():
            raise FileNotFoundError(f"Data source not found: {data_source}")
            
        self.data = self.load_data()
        if self.data.empty:
            raise ValueError("No data loaded")
            
        self.cleaned_data = self.clean_data(self.data)
        self.scaler = StandardScaler()
        self.pca = PCA(n_components=2)
        self.kmeans = KMeans(n_clusters=3)

    def load_data(self) -> pd.DataFrame:
        try:
            suffix = self.data_source.suffix.lower()
            data = None
            
            if suffix == '.csv':
                data = pd.read_csv(self.data_source)
            elif suffix in ['.xlsx', '.xls']:
                data = pd.read_excel(self.data_source)
            else:
                raise ValueError(f"Unsupported file format: {suffix}")
            
            # Validate data structure
            required_columns = ['task_type', 'execution_time', 'interaction_timestamp', 'user_id', 'status']
            missing_columns = [col for col in required_columns if col not in data.columns]
            
            if missing_columns:
                raise ValueError(f"Missing required columns: {missing_columns}")
                
            return data
            
        except Exception as e:
            logging.error(f"Error loading data: {e}")
            raise

    def clean_data(self, data):
        """
        Clean the loaded data by handling missing values, outliers, etc.
        
        :param data: The loaded data.
        :return: Cleaned data.
        """
        # Handle missing values
        cleaned_data = data.dropna()
        
        # Additional cleaning operations can be added here
        # Example: removing duplicates
        cleaned_data = cleaned_data.drop_duplicates()
        
        return cleaned_data

    def generate_performance_report(self):
        """
        Generate a report on AGI performance metrics.
        
        :return: DataFrame with performance insights.
        """
        try:
            # Example of AGI performance metrics (adjust according to vAIn system)
            performance_metrics = self.cleaned_data.groupby('task_type')['execution_time'].describe()
            return performance_metrics
        except KeyError as e:
            print(f"Error generating performance report: {e}")
            return pd.DataFrame()

    def analyze_user_interactions(self):
        """
        Analyze user interactions and behavior patterns over time.
        
        :return: Insights into user engagement and trends.
        """
        try:
            # Example analysis: User interactions by date
            self.cleaned_data['interaction_date'] = pd.to_datetime(self.cleaned_data['interaction_timestamp'])
            user_interactions = self.cleaned_data.groupby(self.cleaned_data['interaction_date'].dt.date)['user_id'].count()
            return user_interactions
        except KeyError as e:
            print(f"Error analyzing user interactions: {e}")
            return pd.DataFrame()

    def visualize_insights(self, data, chart_type='line', title='Data Visualization', xlabel='Date', ylabel='Value'):
        """
        Visualize the insights with a chart.
        
        :param data: The data to visualize.
        :param chart_type: The type of chart to use (line, bar, etc.).
        :param title: Chart title.
        :param xlabel: Label for the x-axis.
        :param ylabel: Label for the y-axis.
        """
        plt.figure(figsize=(10, 6))
        
        if chart_type == 'line':
            data.plot(kind='line')
        elif chart_type == 'bar':
            data.plot(kind='bar')
        else:
            raise ValueError(f"Unsupported chart type: {chart_type}")
        
        plt.title(title)
        plt.xlabel(xlabel)
        plt.ylabel(ylabel)
        plt.grid(True)
        plt.show()

    def generate_task_summary(self):
        """
        Generate a summary of completed tasks and their success rates.
        
        :return: Task summary DataFrame.
        """
        try:
            # Example: Task status (success/failure)
            task_summary = self.cleaned_data.groupby('task_type')['status'].value_counts().unstack(fill_value=0)
            return task_summary
        except KeyError as e:
            print(f"Error generating task summary: {e}")
            return pd.DataFrame()

    def analyze_patterns(self) -> dict:
        """Analyze patterns in the data using ML techniques"""
        try:
            # Prepare numerical data
            numerical_data = self.cleaned_data.select_dtypes(include=[np.number])
            
            if numerical_data.empty:
                raise ValueError("No numerical data available for analysis")
                
            if numerical_data.shape[0] < 3:
                raise ValueError("Insufficient data for pattern analysis")
            
            # Handle infinite values
            numerical_data = numerical_data.replace([np.inf, -np.inf], np.nan)
            numerical_data = numerical_data.fillna(numerical_data.mean())
            
            scaled_data = self.scaler.fit_transform(numerical_data)
            
            # Adjust number of components based on data
            n_components = min(2, numerical_data.shape[1])
            self.pca = PCA(n_components=n_components)
            
            pca_result = self.pca.fit_transform(scaled_data)
            
            # Adjust number of clusters based on data size
            n_clusters = min(3, numerical_data.shape[0] // 2)
            self.kmeans = KMeans(n_clusters=n_clusters)
            clusters = self.kmeans.fit_predict(scaled_data)
            
            return {
                'pca_components': pca_result.tolist(),
                'clusters': clusters.tolist(),
                'explained_variance': self.pca.explained_variance_ratio_.tolist()
            }
            
        except Exception as e:
            logging.error(f"Error in pattern analysis: {e}")
            raise

# Example Usage
if __name__ == "__main__":
    # Assuming data is stored in a CSV file
    insights_module = Insights(data_source='path_to_data.csv')

    # Generate and print performance report
    performance_report = insights_module.generate_performance_report()
    print("AGI Performance Report:")
    print(performance_report)

    # Analyze and print user interaction data
    user_interactions = insights_module.analyze_user_interactions()
    print("User Interaction Insights:")
    print(user_interactions)

    # Generate and visualize task summary
    task_summary = insights_module.generate_task_summary()
    print("Task Summary:")
    print(task_summary)

    # Visualize user interactions
    insights_module.visualize_insights(user_interactions, chart_type='line', title='User Interactions Over Time')

# Next Steps
"""
Database Integration: Add support for connecting to databases (e.g., SQL, NoSQL) to fetch data.
Advanced Visualization: Integrate with advanced plotting libraries (e.g., Plotly) for interactive visualizations.
Task Performance Metrics: Implement more sophisticated metrics, such as resource usage, task latency, and error rates, for deeper insights.
This module can be extended further to cater to more granular insights and complex reporting mechanisms based on the data structure
"""
