import asyncio
import websockets
import json
import logging
from typing import Optional, Dict, Any, Callable

logger = logging.getLogger(__name__)

class WebSocketService:
    def __init__(self):
        self.websocket: Optional[websockets.WebSocketClientProtocol] = None
        self.handlers: Dict[str, Callable] = {}
        
    async def connect(self, url: str):
        try:
            self.websocket = await websockets.connect(url)
            logger.info('WebSocket connected')
            await self.message_handler()
        except Exception as e:
            logger.error(f'WebSocket connection error: {str(e)}')
            
    async def message_handler(self):
        while True:
            try:
                if self.websocket:
                    message = await self.websocket.recv()
                    data = json.loads(message)
                    await self.handle_message(data)
            except websockets.exceptions.ConnectionClosed:
                logger.info('WebSocket connection closed')
                break
            except Exception as e:
                logger.error(f'Error handling message: {str(e)}')
                break

    async def handle_message(self, message: Dict[str, Any]):
        message_type = message.get('type')
        if message_type in self.handlers:
            await self.handlers[message_type](message.get('payload'))
        else:
            logger.warning(f'No handler for message type: {message_type}')

    async def send(self, data: Dict[str, Any]):
        if self.websocket and not self.websocket.closed:
            try:
                await self.websocket.send(json.dumps(data))
            except Exception as e:
                logger.error(f'Error sending message: {str(e)}')

    def register_handler(self, message_type: str, handler: Callable):
        self.handlers[message_type] = handler

    async def close(self):
        if self.websocket:
            await self.websocket.close()
            logger.info('WebSocket closed')
