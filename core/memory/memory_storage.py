import os
import json
import logging
from datetime import datetime
from .memory_encryption import encrypt_data, decrypt_data
from .memory_compression import compress_memory, decompress_memory
from .utils import generate_unique_id

# Set up logging for memory storage
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class MemoryStorage:
    def __init__(self, storage_path="memory_storage"):
        """Initialize memory storage system"""
        self.storage_path = storage_path
        self.ensure_storage_path_exists()

    def ensure_storage_path_exists(self):
        """Ensure the storage directory exists"""
        if not os.path.exists(self.storage_path):
            os.makedirs(self.storage_path)
            logger.info(f"Storage directory created at {self.storage_path}")
        else:
            logger.info(f"Storage directory already exists at {self.storage_path}")

    def store_data(self, memory_type, data, metadata=None, encrypted=False, compressed=False):
        """Store data into the appropriate memory storage type"""
        try:
            memory_id = generate_unique_id()  # Generate a unique ID for the memory entry
            memory_entry = {
                'id': memory_id,
                'timestamp': datetime.now().isoformat(),
                'data': data,
                'metadata': metadata or {},
                'encrypted': encrypted,
                'compressed': compressed
            }
            
            # Apply encryption if required
            if encrypted:
                memory_entry['data'] = encrypt_data(memory_entry['data'])

            # Apply compression if required
            if compressed:
                memory_entry['data'] = compress_memory(memory_entry['data'])

            # Store the data to the appropriate memory file
            memory_file_path = os.path.join(self.storage_path, f"{memory_type}.json")
            if os.path.exists(memory_file_path):
                with open(memory_file_path, "r+") as file:
                    existing_data = json.load(file)
                    existing_data.append(memory_entry)
                    file.seek(0)
                    json.dump(existing_data, file, indent=4)
            else:
                with open(memory_file_path, "w") as file:
                    json.dump([memory_entry], file, indent=4)

            logger.info(f"Data stored successfully in {memory_type} memory with ID {memory_id}.")
            return memory_id
        except Exception as e:
            logger.error(f"Error storing data in {memory_type} memory: {e}")
            return None

    def retrieve_data(self, memory_type, memory_id, decrypted=False, decompressed=False):
        """Retrieve data from the specified memory type by memory ID"""
        try:
            memory_file_path = os.path.join(self.storage_path, f"{memory_type}.json")
            if not os.path.exists(memory_file_path):
                logger.warning(f"Memory file for {memory_type} does not exist.")
                return None

            with open(memory_file_path, "r") as file:
                data = json.load(file)
                memory_entry = next((entry for entry in data if entry['id'] == memory_id), None)

                if memory_entry:
                    # Decrypt the data if required
                    if decrypted and memory_entry['encrypted']:
                        memory_entry['data'] = decrypt_data(memory_entry['data'])

                    # Decompress the data if required
                    if decompressed and memory_entry['compressed']:
                        memory_entry['data'] = decompress_memory(memory_entry['data'])

                    logger.info(f"Data retrieved from {memory_type} memory with ID {memory_id}.")
                    return memory_entry
                else:
                    logger.warning(f"No entry found with ID {memory_id} in {memory_type} memory.")
                    return None
        except Exception as e:
            logger.error(f"Error retrieving data from {memory_type} memory: {e}")
            return None

    def update_data(self, memory_type, memory_id, new_data, new_metadata=None, encrypted=False, compressed=False):
        """Update an existing memory entry with new data"""
        try:
            memory_file_path = os.path.join(self.storage_path, f"{memory_type}.json")
            if not os.path.exists(memory_file_path):
                logger.warning(f"Memory file for {memory_type} does not exist.")
                return False

            with open(memory_file_path, "r+") as file:
                data = json.load(file)
                memory_entry = next((entry for entry in data if entry['id'] == memory_id), None)

                if memory_entry:
                    memory_entry['data'] = new_data
                    memory_entry['metadata'] = new_metadata or memory_entry['metadata']

                    # Apply encryption if required
                    if encrypted:
                        memory_entry['data'] = encrypt_data(memory_entry['data'])

                    # Apply compression if required
                    if compressed:
                        memory_entry['data'] = compress_memory(memory_entry['data'])

                    # Write the updated data back to the file
                    file.seek(0)
                    json.dump(data, file, indent=4)
                    logger.info(f"Data with ID {memory_id} updated in {memory_type} memory.")
                    return True
                else:
                    logger.warning(f"No entry found with ID {memory_id} in {memory_type} memory.")
                    return False
        except Exception as e:
            logger.error(f"Error updating data in {memory_type} memory: {e}")
            return False

    def delete_data(self, memory_type, memory_id):
        """Delete a specific memory entry"""
        try:
            memory_file_path = os.path.join(self.storage_path, f"{memory_type}.json")
            if not os.path.exists(memory_file_path):
                logger.warning(f"Memory file for {memory_type} does not exist.")
                return False

            with open(memory_file_path, "r+") as file:
                data = json.load(file)
                memory_entry = next((entry for entry in data if entry['id'] == memory_id), None)

                if memory_entry:
                    data.remove(memory_entry)
                    # Write the updated data back to the file
                    file.seek(0)
                    json.dump(data, file, indent=4)
                    logger.info(f"Data with ID {memory_id} deleted from {memory_type} memory.")
                    return True
                else:
                    logger.warning(f"No entry found with ID {memory_id} in {memory_type} memory.")
                    return False
        except Exception as e:
            logger.error(f"Error deleting data from {memory_type} memory: {e}")
            return False

    def get_all_memory_entries(self, memory_type):
        """Retrieve all entries from a specific memory type"""
        try:
            memory_file_path = os.path.join(self.storage_path, f"{memory_type}.json")
            if not os.path.exists(memory_file_path):
                logger.warning(f"Memory file for {memory_type} does not exist.")
                return []

            with open(memory_file_path, "r") as file:
                data = json.load(file)
                logger.info(f"Retrieved all entries from {memory_type} memory.")
                return data
        except Exception as e:
            logger.error(f"Error retrieving all data from {memory_type} memory: {e}")
            return []

    def backup_memory(self, backup_path=None):
        """Backup all memory data to a specified directory or default backup path"""
        backup_path = backup_path or os.path.join(self.storage_path, "backup")
        try:
            if not os.path.exists(backup_path):
                os.makedirs(backup_path)

            for memory_type in ["semantic", "episodic", "procedural", "multi_modal", "long_term", "short_term"]:
                memory_file_path = os.path.join(self.storage_path, f"{memory_type}.json")
                if os.path.exists(memory_file_path):
                    backup_file_path = os.path.join(backup_path, f"{memory_type}_backup.json")
                    with open(memory_file_path, "r") as source_file:
                        with open(backup_file_path, "w") as backup_file:
                            json.dump(json.load(source_file), backup_file, indent=4)
                    logger.info(f"Backed up {memory_type} memory to {backup_file_path}.")
                else:
                    logger.warning(f"{memory_type} memory file does not exist. Skipping backup.")

            return True
        except Exception as e:
            logger.error(f"Error backing up memory: {e}")
            return False

    def restore_memory(self, backup_path):
        """Restore memory data from a backup"""
        try:
            if not os.path.exists(backup_path):
                logger.warning(f"Backup path {backup_path} does not exist.")
                return False

            for memory_type in ["semantic", "episodic", "procedural", "multi_modal", "long_term", "short_term"]:
                backup_file_path = os.path.join(backup_path, f"{memory_type}_backup.json")
                if os.path.exists(backup_file_path):
                    memory_file_path = os.path.join(self.storage_path, f"{memory_type}.json")
                    with open(backup_file_path, "r") as backup_file:
                        with open(memory_file_path, "w") as memory_file:
                            json.dump(json.load(backup_file), memory_file, indent=4)
                    logger.info(f"Restored {memory_type} memory from {backup_file_path}.")
                else:
                    logger.warning(f"No backup found for {memory_type} memory. Skipping restore.")

            return True
        except Exception as e:
            logger.error(f"Error restoring memory: {e}")
            return False
