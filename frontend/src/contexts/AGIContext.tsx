import React, { createContext, useContext, useState, useCallback } from 'react';

interface ModelPerformance {
  accuracy: number;
  loss: number;
  timestamp: string;
}

interface TaskData {
  id: string;
  status: 'pending' | 'running' | 'completed' | 'failed';
  progress: number;
  result?: any;
}

interface VisualizationData {
  type: string;
  data: any;
}

interface AGIContextType {
  modelPerformance: ModelPerformance | null;
  taskData: TaskData[] | null;
  visualizationData: VisualizationData | null;
  updateModelPerformance: (data: ModelPerformance) => void;
  updateTaskData: (data: TaskData[]) => void;
  updateVisualizationData: (data: VisualizationData) => void;
}

const AGIContext = createContext<AGIContextType | undefined>(undefined);

export function AGIProvider({ children }: { children: React.ReactNode }) {
  const [modelPerformance, setModelPerformance] = useState<ModelPerformance | null>(null);
  const [taskData, setTaskData] = useState<TaskData[] | null>(null);
  const [visualizationData, setVisualizationData] = useState<VisualizationData | null>(null);

  const updateModelPerformance = useCallback((data: ModelPerformance) => {
    setModelPerformance(data);
  }, []);

  const updateTaskData = useCallback((data: TaskData[]) => {
    setTaskData(data);
  }, []);

  const updateVisualizationData = useCallback((data: VisualizationData) => {
    setVisualizationData(data);
  }, []);

  return (
    <AGIContext.Provider
      value={{
        modelPerformance,
        taskData,
        visualizationData,
        updateModelPerformance,
        updateTaskData,
        updateVisualizationData,
      }}
    >
      {children}
    </AGIContext.Provider>
  );
}

export function useAGI() {
  const context = useContext(AGIContext);
  if (context === undefined) {
    throw new Error('useAGI must be used within an AGIProvider');
  }
  return context;
}
