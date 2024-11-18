import logging
import json
import time
import os
from collections import deque
from datetime import datetime

# Setup logger for AI-driven episodic memory
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

class EpisodicMemory:
    def __init__(self, max_size=100, persistent_storage_path=None, memory_format="json", memory_lifetime=None):
        """
        EpisodicMemory stores and manages episodes with timestamps, optional metadata, and more.
        :param max_size: Maximum number of episodes to store in memory.
        :param persistent_storage_path: Optional path to save/load episodes from disk.
        :param memory_format: Format of stored memory (e.g., "json", "binary", etc.).
        :param memory_lifetime: Optional time duration (in seconds) after which episodes expire (default is None, meaning no expiration).
        """
        self.max_size = max_size
        self.memory_lifetime = memory_lifetime  # Expiry time for memories (in seconds)
        self.episodes = deque()  # Efficient deque for appending/removing episodes
        self.persistent_storage_path = persistent_storage_path
        self.memory_format = memory_format

        # Load episodes from storage if a path is provided
        if self.persistent_storage_path:
            self.load_from_storage()

    def _expire_episodes(self):
        """Remove expired episodes based on memory lifetime."""
        if self.memory_lifetime:
            current_time = time.time()
            initial_size = len(self.episodes)
            self.episodes = deque(
                episode for episode in self.episodes if current_time - episode["timestamp"] < self.memory_lifetime
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
        else:
            logger.warning("Attempted to remove an episode not found in memory.")

    def clear_memory(self):
        """Clear all episodes from memory."""
        self.episodes.clear()
        logger.debug("Cleared all episodes from memory.")

    def save_to_storage(self):
        """Save episodes to persistent storage (e.g., JSON file or binary)."""
        if self.persistent_storage_path:
            try:
                if self.memory_format == "json":
                    with open(self.persistent_storage_path, 'w') as file:
                        json.dump([dict(episode) for episode in self.episodes], file)
                elif self.memory_format == "binary":
                    # Example: Implement custom binary serialization
                    with open(self.persistent_storage_path, 'wb') as file:
                        pass  # Implement binary serialization logic
                logger.info(f"Memory saved to {self.persistent_storage_path}")
            except Exception as e:
                logger.error(f"Failed to save memory to storage: {e}")
        else:
            logger.warning("No persistent storage path provided.")

    def load_from_storage(self):
        """Load episodes from persistent storage."""
        if self.persistent_storage_path:
            try:
                if self.memory_format == "json":
                    with open(self.persistent_storage_path, 'r') as file:
                        loaded_episodes = json.load(file)
                        for episode in loaded_episodes:
                            self.add_episode(episode["event_data"], episode.get("metadata"), episode.get("system_state"))
                elif self.memory_format == "binary":
                    # Example: Implement custom binary deserialization
                    with open(self.persistent_storage_path, 'rb') as file:
                        pass  # Implement binary deserialization logic
                logger.info(f"Loaded memory from {self.persistent_storage_path}")
            except Exception as e:
                logger.error(f"Failed to load memory from storage: {e}")
        else:
            logger.warning("No persistent storage path provided.")

    def get_memory_summary(self):
        """Provide a summary of the stored memory for analysis or visualization."""
        memory_summary = {
            "total_episodes": len(self.episodes),
            "latest_timestamp": datetime.fromtimestamp(self.episodes[-1]["timestamp"]) if self.episodes else None,
            "oldest_timestamp": datetime.fromtimestamp(self.episodes[0]["timestamp"]) if self.episodes else None
        }
        logger.info(f"Memory Summary: {memory_summary}")
        return memory_summary


# Example usage
if __name__ == "__main__":
    # Initialize EpisodicMemory with a max size of 10 and optional persistent storage (JSON format)
    episodic_memory = EpisodicMemory(max_size=10, persistent_storage_path="episodic_memory.json", memory_lifetime=3600)

    # Add episodes with event data, metadata, and system state
    episodic_memory.add_episode("AI decision made", metadata={"action": "recommend", "user_id": 1}, system_state={"model_version": "v1.2"})
    episodic_memory.add_episode("User provided feedback", metadata={"user_id": 1, "feedback": "positive"}, system_state={"model_version": "v1.2"})

    # Retrieve all episodes
    all_episodes = episodic_memory.get_episodes()
    logger.info(f"All episodes: {all_episodes}")

    # Retrieve episodes by time range
    start_time = time.time() - 60  # Last 60 seconds
    end_time = time.time()
    recent_episodes = episodic_memory.get_episode_by_time_range(start_time, end_time)
    logger.info(f"Recent episodes: {recent_episodes}")

    # Retrieve episodes by metadata (e.g., all episodes with user_id 1)
    user_episodes = episodic_memory.get_episode_by_metadata("user_id", 1)
    logger.info(f"User episodes: {user_episodes}")

    # Remove an episode
    episodic_memory.remove_episode(all_episodes[0])

    # Save to storage
    episodic_memory.save_to_storage()

    # Clear memory
    episodic_memory.clear_memory()

    # Get memory summary
    episodic_memory.get_memory_summary()
