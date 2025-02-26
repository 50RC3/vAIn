export const createWebSocketConnection = (url, onMessage, onError) => {
    const ws = new WebSocket(url);

    ws.onmessage = (event) => {
        const message = JSON.parse(event.data);
        onMessage(message);
    };

    ws.onerror = (error) => {
        console.error("WebSocket error:", error);
        onError("Failed to connect to the server.");
    };

    return ws;
};
