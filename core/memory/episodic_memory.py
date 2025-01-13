import logging
import json
import time
import os
from collections import deque
from datetime import datetime
from cryptography.fernet import Fernet  # For encryption
import pickle  # For binary serialization

# Setup logger for AI-driven episodic memory
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

class EpisodicMemory:
    def __init__(self, max_size=100, persistent_storage_path=None, memory_format="json", 
                 memory_lifetime=None, encryption_key=None):
        """
        EpisodicMemory stores and manages episodes with timestamps, optional metadata, and more.
        :param max_size: Maximum number of episodes to store in memory.
        :param persistent_storage_path: Optional path to save/load episodes from disk.
        :param memory_format: Format of stored memory (e.g., "json", "binary", "pickle").
        :param memory_lifetime: Optional time duration (in seconds) after which episodes expire (default is None, meaning no expiration).
        :param encryption_key: Optional encryption key for secure storage.
        """
        self.max_size = max_size
        self.memory_lifetime = memory_lifetime  # Expiry time for memories (in seconds)
        self.episodes = deque()  # Efficient deque for appending/removing episodes
        self.persistent_storage_path = persistent_storage_path
        self.memory_format = memory_format
        self.encryption_key = encryption_key
        self.cipher = Fernet(encryption_key.encode()) if encryption_key else None

        if self.persistent_storage_path:
            self.load_from_storage()

    def _expire_episodes(self):
        """Remove expired episodes based on memory lifetime."""
        if self.memory_lifetime:
            current_time = time.time()
            initial_size = len(self.episodes)
            self.episodes = deque(
                episode for episode in self.episodes 
                if current_time - episode["timestamp"] < self.memory_lifetime
            )
            expired = initial_size - len(self.episodes)
            if expired:
                logger.debug(f"Expired {expired} episodes due to memory lifetime")

    def add_episode(self, event_data, metadata=None, system_state=None):
        """
        Add an episode to the memory with the option to include system states.
        :param event_data: Core data representing the event or experience.
        :param metadata: Optional metadata about the episode (context, outcome).
        :param system_state: Optional system state at the time of the event (e.g., AI's decision or action taken).
        """
        timestamp = time.time()  # Current timestamp for the event
        episode = {
            "timestamp": timestamp,
            "event_data": event_data,
            "metadata": metadata,
            "system_state": system_state
        }

        self._expire_episodes()  # Remove expired episodes before adding a new one

        if len(self.episodes) >= self.max_size:
            removed_episode = self.episodes.popleft()  # Remove oldest episode if max size is reached
            logger.debug(f"Memory is full. Removed oldest episode: {removed_episode['event_data']}")

        self.episodes.append(episode)
        logger.debug(f"Added new episode at {timestamp}: {event_data}")

        if self.persistent_storage_path:
            self.save_to_storage()  # Save after each addition for immediate persistence

    def get_episodes(self):
        """Retrieve all stored episodes, sorted by timestamp."""
        logger.debug(f"Retrieving all episodes. Total episodes: {len(self.episodes)}")
        return list(self.episodes)

    def get_episode_by_time_range(self, start_time, end_time):
        """
        Retrieve episodes within a specific time range.
        :param start_time: Start timestamp for the range.
        :param end_time: End timestamp for the range.
        """
        episodes_in_range = [
            episode for episode in self.episodes
            if start_time <= episode["timestamp"] <= end_time
        ]
        logger.debug(f"Retrieved {len(episodes_in_range)} episodes in time range {start_time} - {end_time}")
        return episodes_in_range

    def get_episode_by_metadata(self, metadata_key, metadata_value):
        """
        Retrieve episodes by specific metadata.
        :param metadata_key: Key to search for in the metadata.
        :param metadata_value: Value associated with the metadata key.
        """
        matching_episodes = [
            episode for episode in self.episodes
            if episode["metadata"] and episode["metadata"].get(metadata_key) == metadata_value
        ]
        logger.debug(f"Retrieved {len(matching_episodes)} episodes with {metadata_key} = {metadata_value}")
        return matching_episodes

    def remove_episode(self, episode):
        """
        Remove a specific episode from memory.
        :param episode: The episode to be removed.
        """
        if episode in self.episodes:
            self.episodes.remove(episode)
            logger.debug(f"Removed episode: {episode['event_data']}")
            if self.persistent_storage_path:
                self.save_to_storage()  # Update persistent storage after removal
        else:
            logger.warning("Attempted to remove an episode not found in memory.")

    def clear_memory(self):
        """Clear all episodes from memory."""
        self.episodes.clear()
        logger.debug("Cleared all episodes from memory.")
        if self.persistent_storage_path:
            try:
                os.remove(self.persistent_storage_path)
                logger.info(f"Deleted persistent storage file: {self.persistent_storage_path}")
            except OSError as e:
                logger.warning(f"Failed to delete persistent storage file: {e}")

    def save_to_storage(self):
        """Save episodes to persistent storage (e.g., JSON file, binary, pickle)."""
        if self.persistent_storage_path:
            try:
                if self.memory_format == "json":
                    with open(self.persistent_storage_path, 'w') as file:
                        json.dump([dict(episode) for episode in self.episodes], file)
                elif self.memory_format == "binary":
                    with open(self.persistent_storage_path, 'wb') as file:
                        pickle.dump(self.episodes, file)
                elif self.memory_format == "pickle":
                    with open(self.persistent_storage_path, 'wb') as file:
                        pickle.dump(self.episodes, file) 
                else:
                    logger.warning(f"Unsupported memory format: {self.memory_format}")
                    return

                if self.encryption_key:
                    with open(self.persistent_storage_path, 'rb') as f:
                        data = f.read()
                    encrypted_data = self.cipher.encrypt(data)
                    with open(self.persistent_storage_path, 'wb') as f:
                        f.write(encrypted_data)

                logger.info(f"Memory saved to {self.persistent_storage_path}")
            except Exception as e:
                logger.error(f"Failed to save memory to storage: {e}")
        else:
            logger.warning("No persistent storage path provided.")

    def load_from_storage(self):
        """Load episodes from persistent storage."""
        if self.persistent_storage_path:
            try:
                if self.encryption_key:
                    with open(self.persistent_storage_path, 'rb') as f:
                        encrypted_data = f.read()
                    decrypted_data = self.cipher.decrypt(encrypted_data)
                else:
                    with open(self.persistent_storage_path, 'rb') as f:
                        decrypted_data = f.read()

                if self.memory_format == "json":
                    loaded_episodes = json.loads(decrypted_data.decode('utf-8'))
                elif self.memory_format == "binary":
                    loaded_episodes = pickle.loads(decrypted_data)
                elif self.memory_format == "pickle":
                    loaded_episodes = pickle.loads(decrypted_data) 
                else:
                    logger.warning(f"Unsupported memory format: {self.memory_format}")
                    return

                for episode in loaded_episodes:
                    self.add_episode(episode["event_data"], episode.get("metadata"), episode.get("system_state"))
                logger.info(f"Loaded memory from {self.persistent_storage_path}")
            except Exception as e:
