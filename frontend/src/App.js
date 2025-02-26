// App.js
// Main Entry Point with Real-Time Updates, Visualization, and Task Management

import React, { useState, useEffect, useContext } from 'react';
import './App.css'; // Styling for the frontend
import { BrowserRouter as Router, Route, Routes } from 'react-router-dom'; // Note: Switch is now Routes in v6
import { Header, Footer, Sidebar } from './components/Layout';
import Home from './pages/Home';
import Performance from './pages/Performance';
import Tasks from './pages/Tasks';
import TaskDetails from './pages/TaskDetails';
import Visualization from './pages/Visualization';
import { fetchModelPerformance, fetchTaskData, fetchVisualizationData } from './services/api';
import { AGIContext } from './contexts/AGIContext';
import { Notification } from './components/Notification';
import { WebSocketService } from './services/websocket'; // WebSocket service for real-time updates
import Chatbot from './components/Chatbot';
import ErrorBoundary from './components/ErrorBoundary';

function App() {
  const [modelPerformance, setModelPerformance] = useState(null);
  const [taskData, setTaskData] = useState(null);
  const [visualizationData, setVisualizationData] = useState(null);
  const [notifications, setNotifications] = useState([]);
  const [loading, setLoading] = useState(true);
  const [ws, setWs] = useState(null); // WebSocket state for real-time updates

  // Context for shared AGI data
  const agiContext = useContext(AGIContext);

  useEffect(() => {
    // Initialize WebSocket connection for real-time updates
    const websocket = new WebSocketService();
    setWs(websocket);

    // WebSocket event listeners
    websocket.on('taskUpdate', handleTaskUpdate);
    websocket.on('visualizationUpdate', handleVisualizationUpdate);

    // Fetch initial data
    loadData();

    // Cleanup WebSocket connection on component unmount
    return () => {
      if (ws) {
        ws.close();
      }
    };
  }, []);

  const loadData = async () => {
    try {
      const performanceData = await fetchModelPerformance();
      const tasks = await fetchTaskData();
      const visualizations = await fetchVisualizationData();
      setModelPerformance(performanceData);
      setTaskData(tasks);
      setVisualizationData(visualizations);
    } catch (error) {
      setNotifications([...notifications, { type: 'error', message: 'Failed to load data' }]);
    } finally {
      setLoading(false);
    }
  };

  const handleTaskUpdate = (taskUpdate) => {
    // Process real-time task update received from WebSocket
    setTaskData((prevTaskData) => {
      return prevTaskData.map(task =>
        task.id === taskUpdate.id ? { ...task, ...taskUpdate } : task
      );
    });
    setNotifications([...notifications, { type: 'info', message: `Task ${taskUpdate.id} updated` }]);
  };

  // Handling visualization updates (possibly for performance graphs, model metrics)
  const handleVisualizationUpdate = (data) => {
    setVisualizationData(data);
  };

  return (
    <AGIContext.Provider value={{ modelPerformance, taskData, visualizationData }}>
      <Router>
        <div className="app">
          <Header />
          <Sidebar />
          <main className="main-content">
            {loading ? (
              <div className="loading-spinner">Loading...</div>
            ) : (
              <Routes>
                <Route path="/" element={<Home />} />
                <Route path="/performance" element={<Performance />} />
                <Route path="/tasks" element={<Tasks />} />
                <Route path="/tasks/:taskId" element={<TaskDetails />} />
                <Route path="/visualization" element={<Visualization />} />
              </Routes>
            )}
          </main>
          <Footer />
        </div>
      </Router>
      
      {/* Notifications Component */}
      <Notification 
        notifications={notifications} 
        onClose={(index) => {
          setNotifications(prevNotifications => prevNotifications.filter((_, i) => i !== index));
        }} 
      />
      <div className="app-container">
        <ErrorBoundary>
          <Chatbot />
        </ErrorBoundary>
      </div>
    </AGIContext.Provider>
  );
}

export default App;
