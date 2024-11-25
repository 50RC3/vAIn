import os
from cryptography.fernet import Fernet
import logging

# Set up logging for encryption/decryption processes
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Load the encryption key securely from environment variable or file (example with env var)
def load_encryption_key():
    """Load the encryption key from a secure location."""
    key = os.getenv("ENCRYPTION_KEY")
    
    # If the key is not set in environment variables, generate a new one (only to be used in testing)
    if not key:
        logger.warning("No encryption key found in environment. Generating a new key (only for testing purposes).")
        key = Fernet.generate_key().decode()
    
    return key

# Initialize cipher suite with the loaded key
key = load_encryption_key()
cipher_suite = Fernet(key)

def encrypt_data(data):
    """Encrypt the data."""
    try:
        # If the data is a string, encode it; if it's already bytes, use it directly
        if isinstance(data, str):
            data = data.encode('utf-8')
        
        encrypted_data = cipher_suite.encrypt(data)
        logger.debug("Data successfully encrypted.")
        return encrypted_data
    except Exception as e:
        logger.error(f"Error encrypting data: {e}")
        raise

def decrypt_data(encrypted_data):
    """Decrypt the data."""
    try:
        decrypted_data = cipher_suite.decrypt(encrypted_data)
        logger.debug("Data successfully decrypted.")
        # Attempt to decode it as a string, in case it's text
        return decrypted_data.decode('utf-8')
    except Exception as e:
        logger.error(f"Error decrypting data: {e}")
        raise

def encrypt_object(data_object):
    """Encrypt a Python object (convert to JSON first)."""
    try:
        import json
        data_str = json.dumps(data_object)  # Convert object to JSON string
        encrypted_data = encrypt_data(data_str)
        logger.debug("Object successfully encrypted.")
        return encrypted_data
    except Exception as e:
        logger.error(f"Error encrypting object: {e}")
        raise

def decrypt_object(encrypted_data):
    """Decrypt a Python object (assumes it was serialized into JSON)."""
    try:
        decrypted_str = decrypt_data(encrypted_data)
        return json.loads(decrypted_str)  # Convert back to Python object
    except Exception as e:
        logger.error(f"Error decrypting object: {e}")
        raise

# For demonstration purposes, set the encryption key through an environment variable.
# Example: export ENCRYPTION_KEY="your_key_here"
