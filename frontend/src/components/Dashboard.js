// frontend/src/components/Dashboard.js

import React, { useState, useEffect } from "react";

const Dashboard = () => {
  const [taskUpdates, setTaskUpdates] = useState([]);
  const [isConnected, setIsConnected] = useState(false);
  const [webSocket, setWebSocket] = useState(null);

  // Function to handle WebSocket connection and listen for messages
  useEffect(() => {
    const ws = new WebSocket("ws://localhost:8000/ws/tasks");

    ws.onopen = () => {
      setIsConnected(true);
      console.log("Connected to WebSocket");
    };

    ws.onmessage = (event) => {
      const message = JSON.parse(event.data);
      if (message.type === "taskUpdate") {
        setTaskUpdates((prevUpdates) => [
          ...prevUpdates,
          message.payload,
        ]);
      }
    };

    ws.onclose = () => {
      setIsConnected(false);
      console.log("Disconnected from WebSocket");
    };

    setWebSocket(ws);

    return () => {
      if (ws) {
        ws.close();
      }
    };
  }, []);

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
        {isConnected ? (
          renderTaskUpdates()
        ) : (
          <p>Waiting for task updates...</p>
        )}
      </div>
    </div>
  );
};

export default Dashboard;
