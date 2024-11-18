// services/websocket.js
export class WebSocketService {
  constructor() {
    this.socket = null;
  }

  connect(url) {
    this.socket = new WebSocket(url);

    this.socket.onopen = () => {
      console.log('WebSocket connected');
    };

    this.socket.onmessage = (event) => {
      const message = JSON.parse(event.data);
      this.handleMessage(message);
    };

    this.socket.onerror = (error) => {
      console.error('WebSocket error:', error);
    };

    this.socket.onclose = () => {
      console.log('WebSocket closed');
    };
  }

  handleMessage(message) {
    // Handle different types of messages (task updates, model performance, etc.)
    if (message.type === 'taskUpdate') {
      // Trigger task update
      handleTaskUpdate(message.payload);
    } else if (message.type === 'visualizationUpdate') {
      // Trigger visualization update
      handleVisualizationUpdate(message.payload);
    }
  }

  send(data) {
    if (this.socket && this.socket.readyState === WebSocket.OPEN) {
      this.socket.send(JSON.stringify(data));
    }
  }

  close() {
    if (this.socket) {
      this.socket.close();
    }
  }
}
