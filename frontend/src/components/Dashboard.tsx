
import React, { useEffect, useState } from 'react';
import { 
    NodeStatus, 
    TrainingMetrics,
    ResourceUsage 
} from '../types';
import { 
    PerformanceGraph,
    NodeList,
    ResourceMonitor
} from './monitoring';

const Dashboard: React.FC = () => {
    const [nodes, setNodes] = useState<NodeStatus[]>([]);
    const [metrics, setMetrics] = useState<TrainingMetrics[]>([]);
    const [resources, setResources] = useState<ResourceUsage>({});

    useEffect(() => {
        // Connect to WebSocket for real-time updates
        const ws = new WebSocket('ws://localhost/ws/events');
        
        ws.onmessage = (event) => {
            const data = JSON.parse(event.data);
            switch (data.type) {
                case 'NODE_STATUS':
                    updateNodes(data.payload);
                    break;
                case 'TRAINING_METRICS':
                    updateMetrics(data.payload);
                    break;
                case 'RESOURCE_USAGE':
                    updateResources(data.payload);
                    break;
            }
        };

        return () => ws.close();
    }, []);

    return (
        <div className="dashboard">
            <header>
                <h1>vAIn Network Dashboard</h1>
            </header>
            <main>
                <section>
                    <NodeList nodes={nodes} />
                </section>
                <section>
                    <PerformanceGraph metrics={metrics} />
                </section>
                <section>
                    <ResourceMonitor usage={resources} />
                </section>
            </main>
        </div>
    );
};

export default Dashboard;
