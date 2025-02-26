import { createContext } from 'react';

export const AGIContext = createContext({
    modelPerformance: null,
    taskData: null,
    visualizationData: null
});
