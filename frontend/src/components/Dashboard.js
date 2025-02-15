// frontend/src/components/Dashboard.js

import React, { useState, useEffect, useCallback } from "react";
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
    try {
      const ws = new WebSocket("ws://localhost:8000/ws/tasks");

      ws.onopen = () => {
        setIsConnected(true);
        setIsLoading(false);
        setError(null);
        setRetryCount(0);
      };

      ws.onmessage = (event) => {
        try {
          const message = JSON.parse(event.data);
          if (message.type === "taskUpdate") {
            setTaskUpdates((prevUpdates) => [message.payload, ...prevUpdates].slice(0, 50));
          }
        } catch (e) {
          console.error("Failed to parse WebSocket message:", e);
        }
      };

      ws.onclose = () => {
        setIsConnected(false);
        if (retryCount < 5) {
          setTimeout(() => {
            setRetryCount(prev => prev + 1);
            connectWebSocket();
          }, 3000 * Math.pow(2, retryCount));
        } else {
          setError("Connection lost. Please refresh the page.");
        }
      };

      ws.onerror = (error) => {
        console.error("WebSocket error:", error);
        setError("Failed to connect to the server.");
      };

      return ws;
    } catch (error) {
      setError("Failed to establish connection.");
      setIsLoading(false);
      return null;
    }
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
