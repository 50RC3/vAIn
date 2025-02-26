class WebSocketService {
    constructor() {
        this.ws = null;
        this.listeners = new Map();
        this.connect();
    }

    connect() {
        this.ws = new WebSocket(process.env.REACT_APP_WS_URL || 'ws://localhost:8000/ws');
        
        this.ws.onmessage = (event) => {
            const data = JSON.parse(event.data);
            const listeners = this.listeners.get(data.type) || [];
            listeners.forEach(listener => listener(data.payload));
        };

        this.ws.onerror = (error) => {
            console.error('WebSocket error:', error);
        };

        this.ws.onclose = () => {
            setTimeout(() => this.connect(), 5000);
        };
    }

    on(event, callback) {
        if (!this.listeners.has(event)) {
            this.listeners.set(event, []);
        }
        this.listeners.get(event).push(callback);
    }

    close() {
        if (this.ws) {
            this.ws.close();
        }
    }
}

export { WebSocketService };
