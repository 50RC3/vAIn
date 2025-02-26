import React, { useState, useEffect, useCallback } from "react";
import { createWebSocketConnection } from '../utils/websocket';
import P2PNetworkStats from "./P2PNetworkStats";
import Chatbot from "./Chatbot";
import "../styles/dashboard.css";

const Dashboard = () => {
  const [taskUpdates, setTaskUpdates] = useState([]);
  const [isConnected, setIsConnected] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  const [retryCount, setRetryCount] = useState(0);

  const connectWebSocket = useCallback(() => {
    const onMessage = (message) => {
      if (message.type === "taskUpdate") {
        setTaskUpdates((prevUpdates) => [message.payload, ...prevUpdates].slice(0, 50));
      }
    };

    const onError = (errorMessage) => {
      setError(errorMessage);
    };

    const ws = createWebSocketConnection("ws://localhost:8000/ws/tasks", onMessage, onError);

    return () => {
      if (ws) {
        ws.close();
      }
    };
  }, [retryCount]);

  useEffect(() => {
    const ws = connectWebSocket();
    return () => {
      if (ws) {
        ws.close();
      }
    };
  }, [connectWebSocket]);

  // Render task updates
  const renderTaskUpdates = () => {
    return taskUpdates.map((task, index) => (
      <div key={index} className="task-update">
        <h3>Task ID: {task.id}</h3>
        <p>Status: {task.status}</p>
        <p>Description: {task.description}</p>
      </div>
    ));
  };

  return (
    <div className="dashboard-container">
      <h1>vAIn Task Dashboard</h1>
      <div className="status">
        <span>Status: {isConnected ? "Connected" : "Disconnected"}</span>
      </div>
      <div className="task-updates-container">
        {isLoading ? (
          <p>Loading...</p>
        ) : error ? (
          <p>{error}</p>
        ) : isConnected ? (
          renderTaskUpdates()
        ) : (
          <p>Waiting for task updates...</p>
        )}
      </div>
    </div>
  );
};

export default Dashboard;
