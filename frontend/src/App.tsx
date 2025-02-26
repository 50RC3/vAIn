import React, { useEffect, useState, useContext } from 'react';
import { RouterProvider, createBrowserRouter } from 'react-router-dom';
import { AGIProvider, AGIContext } from './contexts/AGIContext';
import { WebSocketService } from './services/websocket';
import { ErrorBoundary } from './components/ErrorBoundary';
import { routes } from './routes';
import { Notification } from './components/Notification';
import { Task, Notification as NotificationType, ModelPerformance, VisualizationData, AGIContextType } from './types';
import './App.css';

const router = createBrowserRouter(routes);

function App(): JSX.Element {
  const [ws, setWs] = useState<WebSocketService | null>(null);
  const [notifications, setNotifications] = useState<NotificationType[]>([]);
  const [modelPerformance, setModelPerformance] = useState<ModelPerformance | null>(null);
  const [taskData, setTaskData] = useState<Task[] | null>(null);
  const [visualizationData, setVisualizationData] = useState<VisualizationData | null>(null);
  const [loading, setLoading] = useState<boolean>(true);

  const agiContext = useContext<AGIContextType>(AGIContext);

  useEffect(() => {
    const websocket = new WebSocketService();
    setWs(websocket);

    return () => {
      websocket.close();
    };
  }, []);

  const handleTaskUpdate = (taskUpdate: Task): void => {
    setTaskData((prevTaskData) => {
      if (!prevTaskData) return null;
      return prevTaskData.map(task =>
        task.id === taskUpdate.id ? { ...task, ...taskUpdate } : task
      );
    });
    setNotifications(prev => [...prev, { type: 'info', message: `Task ${taskUpdate.id} updated` }]);
  };

  const handleVisualizationUpdate = (data: VisualizationData): void => {
    setVisualizationData(data);
  };

  return (
    <ErrorBoundary>
      <AGIProvider>
        <RouterProvider router={router} />
        <Notification
          notifications={notifications}
          onClose={(index) => {
            setNotifications((prev) => prev.filter((_, i) => i !== index));
          }}
        />
      </AGIProvider>
    </ErrorBoundary>
  );
}

export default App;
