import React, { useEffect, useState } from "react";

const P2PNetworkStats = () => {
  const [networkStats, setNetworkStats] = useState(null);

  useEffect(() => {
    fetchNetworkStats();
  }, []);

  const fetchNetworkStats = async () => {
    // Placeholder for fetching network stats from the backend
    // Replace with actual API call
    const stats = {
      peers: 5,
      status: "Connected",
      dataTransferred: "1.2 GB",
    };
    setNetworkStats(stats);
  };

  return (
    <div className="p2p-network-stats">
      <h2>P2P Network Statistics</h2>
      {networkStats ? (
        <div>
          <p>Connected Peers: {networkStats.peers}</p>
          <p>Status: {networkStats.status}</p>
          <p>Data Transferred: {networkStats.dataTransferred}</p>
        </div>
      ) : (
        <p>Loading network stats...</p>
      )}
    </div>
  );
};

export default P2PNetworkStats;
