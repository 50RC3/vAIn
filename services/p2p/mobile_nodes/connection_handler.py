import asyncio
import json
from typing import Any, Dict
import websockets
import logging
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.backends import default_backend

# Logging configuration
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ConnectionHandler")

class ConnectionHandler:
    def __init__(self, node_id: str, private_key: rsa.RSAPrivateKey, network_address: str):
        """
        Initialize the connection handler for mobile node integration.

        :param node_id: Unique identifier for the mobile node.
        :param private_key: RSA private key for secure communication.
        :param network_address: Network address of the peer-to-peer node.
        """
        self.node_id = node_id
        self.private_key = private_key
        self.public_key = private_key.public_key()
        self.network_address = network_address
        self.peers = {}  # Active connections to peers

    async def start(self):
        """Start the connection handler and listen for incoming connections."""
        logger.info(f"Node {self.node_id} starting on {self.network_address}")
        async with websockets.serve(self.handle_incoming_connection, *self.network_address.split(":")):
            await asyncio.Future()  # Keep running indefinitely

    async def handle_incoming_connection(self, websocket: websockets.WebSocketServerProtocol, path: str):
        """
        Handle incoming WebSocket connections.

        :param websocket: WebSocket connection.
        :param path: Connection path.
        """
        try:
            logger.info("Incoming connection received.")
            handshake_data = await websocket.recv()
            peer_info = self.verify_handshake(handshake_data)
            logger.info(f"Verified handshake with peer: {peer_info['node_id']}")

            self.peers[peer_info['node_id']] = websocket
            await self.synchronize_data(peer_info['node_id'], websocket)

        except Exception as e:
            logger.error(f"Error handling connection: {e}")
        finally:
            await websocket.close()

    def verify_handshake(self, handshake_data: str) -> Dict[str, Any]:
        """
        Verify the handshake data and authenticate the peer.

        :param handshake_data: Data received from the peer during the handshake.
        :return: Decoded handshake information.
        """
        try:
            handshake_json = json.loads(handshake_data)
            signature = bytes.fromhex(handshake_json['signature'])
            node_id = handshake_json['node_id']
            public_key_pem = handshake_json['public_key']

            peer_public_key = serialization.load_pem_public_key(
                public_key_pem.encode('utf-8'),
                backend=default_backend()
            )

            # Verify the signature
            peer_public_key.verify(
                signature,
                node_id.encode('utf-8'),
                padding.PKCS1v15(),
                hashes.SHA256()
            )
            return {"node_id": node_id, "public_key": peer_public_key}
        except Exception as e:
            logger.error(f"Handshake verification failed: {e}")
            raise ValueError("Invalid handshake data")

    async def connect_to_peer(self, peer_address: str, peer_node_id: str):
        """
        Establish a connection with another peer.

        :param peer_address: Address of the peer (host:port).
        :param peer_node_id: Unique identifier of the peer node.
        """
        try:
            logger.info(f"Connecting to peer {peer_node_id} at {peer_address}")
            async with websockets.connect(f"ws://{peer_address}") as websocket:
                # Send handshake
                handshake_data = self.generate_handshake()
                await websocket.send(handshake_data)

                response = await websocket.recv()
                peer_info = self.verify_handshake(response)
                logger.info(f"Connection established with peer: {peer_info['node_id']}")

                self.peers[peer_info['node_id']] = websocket
                await self.synchronize_data(peer_node_id, websocket)
        except Exception as e:
            logger.error(f"Error connecting to peer: {e}")

    def generate_handshake(self) -> str:
        """
        Generate handshake data for secure peer connection.

        :return: Serialized handshake data.
        """
        try:
            node_id_encoded = self.node_id.encode('utf-8')
            signature = self.private_key.sign(
                node_id_encoded,
                padding.PKCS1v15(),
                hashes.SHA256()
            )

            handshake_data = {
                "node_id": self.node_id,
                "public_key": self.public_key.public_bytes(
                    encoding=serialization.Encoding.PEM,
                    format=serialization.PublicFormat.SubjectPublicKeyInfo
                ).decode('utf-8'),
                "signature": signature.hex()
            }
            return json.dumps(handshake_data)
        except Exception as e:
            logger.error(f"Error generating handshake: {e}")
            raise

    async def synchronize_data(self, peer_node_id: str, websocket: websockets.WebSocketClientProtocol):
        """
        Synchronize data with a connected peer.

        :param peer_node_id: Unique identifier of the peer node.
        :param websocket: WebSocket connection to the peer.
        """
        try:
            logger.info(f"Synchronizing data with peer {peer_node_id}")
            # Send synchronization request
            sync_request = {"action": "sync", "node_id": self.node_id}
            await websocket.send(json.dumps(sync_request))

            # Process response
            sync_response = await websocket.recv()
            logger.info(f"Data synchronized with peer {peer_node_id}: {sync_response}")
        except Exception as e:
            logger.error(f"Error during data synchronization with {peer_node_id}: {e}")

    def disconnect_peer(self, peer_node_id: str):
        """
        Disconnect a peer from the network.

        :param peer_node_id: Unique identifier of the peer node to disconnect.
        """
        if peer_node_id in self.peers:
            logger.info(f"Disconnecting peer {peer_node_id}")
            websocket = self.peers.pop(peer_node_id)
            asyncio.create_task(websocket.close())
        else:
            logger.warning(f"Peer {peer_node_id} not found in active connections.")

# Example usage
if __name__ == "__main__":
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
        backend=default_backend()
    )
    handler = ConnectionHandler(node_id="MobileNode1", private_key=private_key, network_address="localhost:8765")

    asyncio.run(handler.start())
