import logging
import time
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from datetime import datetime

logger = logging.getLogger(__name__)

@dataclass
class UserRating:
    rating: int
    comment: str
    timestamp: datetime
    aspects: Dict[str, int]

class RateLimiter:
    def __init__(self, requests_per_minute: int = 50, burst_limit: int = 10):
        self.rate_limit = requests_per_minute
        self.burst_limit = burst_limit
        self.requests: Dict[str, List[float]] = {}
    
    def check_limit(self, user_id: str) -> bool:
        current_time = time.time()
        if user_id not in self.requests:
            self.requests[user_id] = []
        
        # Clean old requests
        self.requests[user_id] = [t for t in self.requests[user_id] 
                                if current_time - t < 60]
        
        if len(self.requests[user_id]) >= (self.rate_limit + self.burst_limit):
            return False
        
        self.requests[user_id].append(current_time)
        return True

class UserInteraction:
    def __init__(self):
        self.rate_limiter = RateLimiter()
        self.supported_languages = ['en', 'es', 'fr', 'de', 'zh', 'ja']
        self.conversation_history: Dict[str, List[Dict]] = {}
        self.user_ratings: Dict[str, List[UserRating]] = {}
        self.contexts: Dict[str, Dict] = {}
    
    def handle_command(self, user_id: str, command: str, params: List[str]) -> str:
        if not self.rate_limiter.check_limit(user_id):
            return "Rate limit exceeded. Please wait a moment."
            
        try:
            if command == "help":
                return self._handle_help(params[0] if params else None)
            elif command == "reset":
                return self._handle_reset(user_id, "--keep-context" in params)
            elif command == "context":
                return self._handle_context(user_id, params)
            elif command == "mode":
                return self._handle_mode(user_id, params[0] if params else None)
            else:
                return f"Unknown command: {command}. Type /help for available commands."
        except Exception as e:
            logger.error(f"Command error: {str(e)}")
            return f"Error executing command: {str(e)}"

    def submit_rating(self, user_id: str, rating: int, comment: str = "", 
                     aspects: Dict[str, int] = None) -> bool:
        if not 1 <= rating <= 5:
            return False
            
        user_rating = UserRating(
            rating=rating,
            comment=comment,
            timestamp=datetime.now(),
            aspects=aspects or {}
        )
        
        if user_id not in self.user_ratings:
            self.user_ratings[user_id] = []
        
        self.user_ratings[user_id].append(user_rating)
        return True

    def _handle_help(self, topic: Optional[str]) -> str:
        help_topics = {
            "commands": "Available commands: /help, /reset, /context, /mode",
            "safety": "Safety features include user confirmation for critical actions...",
            "modes": "Available modes: creative, precise, safe",
            None: "Use /help [topic] for specific help. Topics: commands, safety, modes"
        }
        return help_topics.get(topic, "Topic not found. Use /help for topics list.")

    def _handle_reset(self, user_id: str, keep_context: bool) -> str:
        if not keep_context:
            self.conversation_history[user_id] = []
            return "Conversation history cleared."
        else:
            # Keep learned preferences but clear current conversation
            current_context = self.conversation_history[user_id][-10:] if user_id in self.conversation_history else []
            self.conversation_history[user_id] = current_context
            return "Conversation partially reset, keeping context."

    def _handle_context(self, user_id: str, params: List[str]) -> str:
        if not params:
            return "Context command requires parameters."
            
        action = params[0]
        name = params[1] if len(params) > 1 else None
        
        if action == "save" and name:
            self.contexts[name] = {
                'history': self.conversation_history.get(user_id, []),
                'timestamp': datetime.now()
            }
            return f"Context saved as '{name}'"
        elif action == "load" and name:
            if name in self.contexts:
                self.conversation_history[user_id] = self.contexts[name]['history']
                return f"Context '{name}' loaded"
            return f"Context '{name}' not found"
        elif action == "list":
            return "Saved contexts: " + ", ".join(self.contexts.keys())
            
        return "Invalid context command"

    def _handle_mode(self, user_id: str, mode: Optional[str]) -> str:
        valid_modes = {'creative', 'precise', 'safe'}
        if not mode or mode not in valid_modes:
            return f"Valid modes are: {', '.join(valid_modes)}"
            
        # Store mode in user context
        if user_id not in self.conversation_history:
            self.conversation_history[user_id] = []
        self.conversation_history[user_id].append({'mode_change': mode})
        
        return f"Mode changed to: {mode}"
