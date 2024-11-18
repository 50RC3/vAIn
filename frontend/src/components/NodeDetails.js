// frontend/src/components/NodeDetails.js

import React from "react";

// Sample NodeDetails component
const NodeDetails = ({ nodeData }) => {
  if (!nodeData) {
    return <p>Loading node details...</p>;
  }

  return (
    <div className="node-details">
      <h2>Node Details</h2>
      <div>
        <strong>Node ID:</strong> {nodeData.id}
      </div>
      <div>
        <strong>Status:</strong> {nodeData.status}
      </div>
      <div>
        <strong>Location:</strong> {nodeData.location}
      </div>
      <div>
        <strong>Last Update:</strong> {nodeData.lastUpdate}
      </div>
      <div>
        <strong>Active Tasks:</strong>
        <ul>
          {nodeData.activeTasks.map((task, index) => (
            <li key={index}>{task}</li>
          ))}
        </ul>
      </div>
    </div>
  );
};

export default NodeDetails;
