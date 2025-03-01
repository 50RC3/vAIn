/**
 * Represents a task entity in the application.
 * @interface Task
 * @property {string} id - The unique identifier for the task
 * @property {string} title - The title or name of the task
 * @property {string} status - The current status of the task
 * @property {any} [key: string] - Additional dynamic properties that can be added to the task
 */
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
