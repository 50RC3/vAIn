import logging
from datetime import datetime
from .memory_storage import MemoryStorage
from .memory_encryption import encrypt_data, decrypt_data
from .memory_compression import compress_memory, decompress_memory
from .utils import generate_unique_id

# Set up logging for the short-term memory module
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger('vAIn.ShortTermMemory')

class ShortTermMemory:
    def __init__(self):
        self.memory_storage = MemoryStorage()

    def store(self, data, metadata=None):
        """Store short-term memory data with optional metadata."""
        try:
            logger.info("Storing data in short-term memory.")

            # Encrypt and compress the data before storing it
            encrypted_data = encrypt_data(data)
            compressed_data = compress_memory(encrypted_data)

            # Generate a unique ID for the memory entry
            memory_id = generate_unique_id()

            # Store in memory storage
            timestamp = datetime.now().isoformat()
            memory_entry = {
                'memory_id': memory_id,
                'data': compressed_data,
                'metadata': metadata,
                'timestamp': timestamp,
                'type': 'short_term'
            }
            self.memory_storage.store(memory_entry)

            logger.info(f"Short-term memory successfully stored with ID: {memory_id}")
            return memory_id  # Return the memory ID for future reference
        except Exception as e:
            logger.error(f"Error storing short-term memory data: {e}")
            return None

    def retrieve(self, memory_id):
        """Retrieve short-term memory data using its unique ID."""
        try:
            logger.info(f"Retrieving data from short-term memory with ID: {memory_id}")

            # Retrieve the memory entry from the storage
            memory_entry = self.memory_storage.retrieve(memory_id)

            if memory_entry and memory_entry['type'] == 'short_term':
                # Decompress and decrypt the data before returning
                decompressed_data = decompress_memory(memory_entry['data'])
                decrypted_data = decrypt_data(decompressed_data)
                logger.info("Short-term memory successfully retrieved.")
                return decrypted_data
            else:
                logger.warning(f"Memory ID {memory_id} not found in short-term memory.")
                return None
        except Exception as e:
            logger.error(f"Error retrieving short-term memory: {e}")
            return None

    def update(self, memory_id, data, metadata=None):
        """Update existing short-term memory data."""
        try:
            logger.info(f"Updating short-term memory with ID: {memory_id}")

            # Retrieve the existing memory entry
            memory_entry = self.memory_storage.retrieve(memory_id)

            if memory_entry and memory_entry['type'] == 'short_term':
                # Encrypt, compress, and update the data
                encrypted_data = encrypt_data(data)
                compressed_data = compress_memory(encrypted_data)

                # Update the memory entry in storage
                memory_entry['data'] = compressed_data
                memory_entry['metadata'] = metadata
                memory_entry['timestamp'] = datetime.now().isoformat()

                # Store the updated memory entry
                self.memory_storage.update(memory_id, memory_entry)
                logger.info(f"Short-term memory with ID {memory_id} successfully updated.")
                return True
            else:
                logger.warning(f"Memory ID {memory_id} not found for update.")
                return False
        except Exception as e:
            logger.error(f"Error updating short-term memory: {e}")
            return False

    def delete(self, memory_id):
        """Delete short-term memory data using its unique ID."""
        try:
            logger.info(f"Deleting short-term memory with ID: {memory_id}")

            # Retrieve the existing memory entry
            memory_entry = self.memory_storage.retrieve(memory_id)

            if memory_entry and memory_entry['type'] == 'short_term':
                # Delete the memory entry from storage
                self.memory_storage.delete(memory_id)
                logger.info(f"Short-term memory with ID {memory_id} successfully deleted.")
                return True
            else:
                logger.warning(f"Memory ID {memory_id} not found for deletion.")
                return False
        except Exception as e:
            logger.error(f"Error deleting short-term memory: {e}")
            return False

    def clear_all(self):
        """Clear all short-term memory data."""
        try:
            logger.info("Clearing all short-term memory.")
            self.memory_storage.clear_by_type('short_term')
            logger.info("All short-term memory data cleared.")
        except Exception as e:
            logger.error(f"Error clearing short-term memory: {e}")

    def backup(self):
        """Backup short-term memory to persistent storage."""
        try:
            logger.info("Backing up short-term memory.")
            all_entries = self.memory_storage.retrieve_all_by_type('short_term')

            # Implement a backup mechanism (e.g., saving to an external system or file)
            # For now, we'll log the process
            for entry in all_entries:
                logger.info(f"Backing up memory entry ID: {entry['memory_id']}")

            logger.info("Short-term memory backup completed.")
        except Exception as e:
            logger.error(f"Error backing up short-term memory: {e}")
