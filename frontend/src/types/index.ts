export interface Task {
  id: string;
  title: string;
  status: string;
  [key: string]: any;
}

export interface Notification {
  type: 'error' | 'info' | 'success' | 'warning';
  message: string;
}

export interface ModelPerformance {
  metrics: {
    accuracy: number;
    loss: number;
    [key: string]: number;
  };
}

export interface VisualizationData {
  type: string;
  data: any;
}

export interface AGIContextType {
  modelPerformance: ModelPerformance | null;
  taskData: Task[] | null;
  visualizationData: VisualizationData | null;
}
