"""
Episodic Memory Module for vAIn Core.

This module implements episodic memory capabilities for storing and retrieving
temporal sequences of experiences and events.
"""

from typing import Dict, Any, Optional
from datetime import datetime
from ..storage import MemoryStorage
from core.memory.exceptions import MemoryStorageError

class EpisodicMemory:
    """
    Manages episodic memory storage and retrieval.
    
    Provides functionality for storing, retrieving, and managing temporal sequences
    of experiences and events in a structured memory system.
    """
    
    def __init__(self):
        """Initialize episodic memory with storage backend."""
        self.storage = MemoryStorage()
        self.episodes: Dict[str, Any] = {}

    async def store(self, episode_id: str, data: Any) -> bool:
        """
        Store a new episode in memory.
        
        Args:
            episode_id: Unique identifier for the episode
            data: Episode data to store
            
        Returns:
            bool: True if storage was successful, False otherwise
        
        Raises:
            MemoryStorageError: If storage operation fails
        """
        try:
            self.episodes[episode_id] = {
                'data': data,
                'timestamp': datetime.now()
            }
            return True
        except MemoryStorageError as e:
            raise e
        except Exception as e:
            raise MemoryStorageError(f"Failed to store episode: {str(e)}") from e

    async def retrieve(self, episode_id: str) -> Optional[Any]:
        """
        Retrieve an episode from memory.
        
        Args:
            episode_id: ID of the episode to retrieve
            
        Returns:
            Optional[Any]: Episode data if found, None otherwise
        """
        return self.episodes.get(episode_id, {}).get('data')
