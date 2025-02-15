import React, { useEffect, useState, useCallback } from "react";

const P2PNetworkStats = () => {
  const [networkStats, setNetworkStats] = useState(null);
  const [error, setError] = useState(null);
  const [isLoading, setIsLoading] = useState(true);

  const fetchNetworkStats = useCallback(async () => {
    try {
      const response = await fetch('/api/network/stats');
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      const data = await response.json();
      setNetworkStats(data);
      setError(null);
    } catch (err) {
      setError("Failed to fetch network stats");
      console.error("Error fetching network stats:", err);
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchNetworkStats();
    const interval = setInterval(fetchNetworkStats, 30000); // Update every 30 seconds
    return () => clearInterval(interval);
  }, [fetchNetworkStats]);

  if (isLoading) {
    return <div className="loading">Loading network stats...</div>;
  }

  if (error) {
    return <div className="error">{error}</div>;
  }

  return (
    <div className="p2p-network-stats">
      <h2>P2P Network Statistics</h2>
      {networkStats && (
        <div className="stats-container">
          <div className="stat-item">
            <span className="stat-label">Connected Peers:</span>
            <span className="stat-value">{networkStats.peers}</span>
          </div>
          <div className="stat-item">
            <span className="stat-label">Status:</span>
            <span className={`stat-value status-${networkStats.status.toLowerCase()}`}>
              {networkStats.status}
            </span>
          </div>
          <div className="stat-item">
            <span className="stat-label">Data Transferred:</span>
            <span className="stat-value">{networkStats.dataTransferred}</span>
          </div>
          <div className="stat-item">
            <span className="stat-label">Network Health:</span>
            <span className="stat-value">{networkStats.health || 'N/A'}</span>
          </div>
        </div>
      )}
    </div>
  );
};

export default P2PNetworkStats;
