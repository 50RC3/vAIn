# Encryption and decryption utilities
import base64
import json
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from typing import Dict, Any, Union

class CryptoManager:
    def __init__(self):
        self._key = Fernet.generate_key()
        self._cipher = Fernet(self._key)

    def get_public_key(self) -> str:
        """Return the public key for handshake"""
        return base64.b64encode(self._key).decode()

    def set_key(self, key: str):
        """Set encryption key from string"""
        self._key = base64.b64decode(key.encode())
        self._cipher = Fernet(self._key)

def encrypt_message(message: Union[Dict, str], key: bytes = None) -> bytes:
    """
    Encrypt a message using Fernet symmetric encryption.
    """
    if key is None:
        key = Fernet.generate_key()
    
    cipher = Fernet(key)
    
    if isinstance(message, dict):
        message = json.dumps(message)
    
    encrypted_data = cipher.encrypt(message.encode())
    return encrypted_data

def decrypt_message(encrypted_data: bytes, key: bytes) -> Dict[str, Any]:
    """
    Decrypt a message using Fernet symmetric encryption.
    """
    cipher = Fernet(key)
    decrypted_data = cipher.decrypt(encrypted_data)
    return json.loads(decrypted_data.decode())

def generate_key_from_password(password: str, salt: bytes = None) -> bytes:
    """
    Generate a Fernet key from a password using PBKDF2.
    """
    if salt is None:
        salt = b'vain_salt_bytes'  # In production, use a random salt
        
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
    )
    
    key = base64.b64encode(kdf.derive(password.encode()))
    return key
