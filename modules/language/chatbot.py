import logging
import spacy
import json
from datetime import datetime
from typing import List, Dict, Any
from .nlp_pipeline import nlp_pipeline_task, NLPPipeline
from .services.result_logging import log_task_result, log_task_failure
from .services.task_queue import schedule_task
from .services.user_management import get_user_profile, update_user_profile
from .services.context_manager import ContextManager
from pathlib import Path
from ..interaction.user_interaction import UserInteraction
from ..voice.voice_processor import VoiceProcessor

# Set up logging
logger = logging.getLogger(__name__)

# Initialize SpaCy with try-catch
try:
    nlp = spacy.load('en_core_web_sm')
except OSError:
    logging.error("SpaCy model 'en_core_web_sm' not found. Installing...")
    from spacy.cli import download
    download('en_core_web_sm')
    nlp = spacy.load('en_core_web_sm')

# Initialize context manager for managing conversation state
context_manager = ContextManager()

# Initialize user interaction handler
user_interaction = UserInteraction()

class Chatbot:
    def __init__(self):
        self.nlp_pipeline = NLPPipeline()
        self.voice_processor = VoiceProcessor()

    def handle_voice_input(self, user_id: str) -> Dict[str, Any]:
        """Handle voice input from user"""
        try:
            # Record and transcribe audio
            audio = self.voice_processor.listen()
            text, confidence = self.voice_processor.transcribe(audio)
            
            if confidence < 0.6:
                return {"status": "low_confidence", "text": text}
            
            # Process text through normal pipeline
            response = self.handle_user_message(user_id, text)
            
            # Convert response to speech
            audio_response = self.voice_processor.synthesize(response)
            
            return {
                "status": "success",
                "text": text,
                "response": response,
                "audio": audio_response
            }
            
        except Exception as e:
            logger.error(f"Error processing voice input: {e}")
            return {"status": "error", "message": str(e)}

    def process_nlp_input(self, user_input: str) -> Dict[str, Any]:
        """Enhanced NLP processing"""
        try:
            analysis = self.nlp_pipeline.analyze_text(user_input)
            response = self.nlp_pipeline.generate_response(user_input)
            return {
                "analysis": analysis,
                "response": response
            }
        except Exception as e:
            logger.error(f"Error in NLP processing: {e}")
            raise

    def clean_user_input(self, input_text: str) -> str:
        """
        Clean user input by removing unwanted characters and normalizing text.
        """
        if not isinstance(input_text, str):
            raise ValueError("Input must be a string")
        try:
            # Remove non-alphanumeric characters, convert to lowercase
            cleaned_text = input_text.strip().lower()
            cleaned_text = ' '.join(cleaned_text.split())  # Remove excess spaces
            logger.info(f"Cleaned user input: {cleaned_text}")
            return cleaned_text
        except Exception as e:
            logger.error(f"Error cleaning user input: {e}")
            raise

    def get_response_from_intent(self, user_input: str) -> str:
        """
        Based on the intent detected in the user input, generate a response.
        For now, it's a simple matching mechanism. This can be expanded with ML models.
        """
        try:
            if "hello" in user_input or "hi" in user_input:
                return "Hello! How can I assist you today?"
            elif "your name" in user_input:
                return "I am the vAIn AGI chatbot. How can I help?"
            elif "help" in user_input:
                return "I can help you with various tasks like managing your profile or answering questions."
            else:
                return "I'm sorry, I didn't quite understand that. Can you rephrase?"
        except Exception as e:
            logger.error(f"Error in response generation: {e}")
            raise

    def handle_user_message(self, user_id: str, user_input: str) -> str:
        """
        Handle the entire conversation flow by managing context and processing input.
        """
        try:
            # Check if input is a command
            if user_input.startswith('/'):
                command_parts = user_input[1:].split()
                command = command_parts[0]
                params = command_parts[1:]
                return user_interaction.handle_command(user_id, command, params)

            # Regular message handling
            cleaned_input = self.clean_user_input(user_input)
            
            # Get user context
            user_context = context_manager.get_user_context(user_id)
            if not user_context:
                context_manager.create_new_context(user_id)
            
            # Process input and generate response
            nlp_result = self.process_nlp_input(cleaned_input)
            response = self.get_response_from_intent(cleaned_input)
            
            # Update user profile and log
            update_user_profile(user_id, nlp_result)
            log_task_result(user_input, True, "Processed user message successfully.", nlp_result)
            
            return response
            
        except Exception as e:
            logger.error(f"Error handling user message: {e}")
            log_task_failure(user_input, "Chatbot", str(e))
            return "There was an error processing your request. Please try again later."

    def schedule_user_task(self, user_id: str, task_data: Dict[str, Any]) -> str:
        """
        Schedule a task (such as an external API call or backend operation) based on user interaction.
        """
        try:
            # Step 1: Schedule task for background processing
            schedule_task("user_task", task_data)
            logger.info(f"Task for user {user_id} scheduled successfully.")
            
            # Step 2: Notify user about the task scheduling
            return f"Your task has been scheduled. We'll notify you once it's completed."
        except Exception as e:
            logger.error(f"Error scheduling user task: {e}")
            raise

    def get_user_response(self, user_id: str, user_input: str) -> str:
        """
        Generate a response to the user based on their input and interaction history.
        """
        try:
            # Retrieve user profile
            user_profile = get_user_profile(user_id)

            # Step 1: Handle user message and generate response
            response = self.handle_user_message(user_id, user_input)

            # Step 2: Return the response to the user
            logger.info(f"Generated response for user {user_id}: {response}")
            return response
        except Exception as e:
            logger.error(f"Error generating user response: {e}")
            return "Sorry, I couldn't process your request."

    def initiate_chat(self, user_id: str, user_input: str) -> Dict[str, Any]:
        """
        Start a new conversation or continue an existing one based on user input.
        """
        try:
            # Step 1: Retrieve user response based on input
            response = self.get_user_response(user_id, user_input)
            
            # Step 2: Return structured response
            return {"status": "success", "response": response, "timestamp": datetime.now()}
        except Exception as e:
            logger.error(f"Error in initiating chat: {e}")
            return {"status": "error", "message": "Failed to initiate chat. Please try again."}

# --- Example Usage ---
if __name__ == "__main__":
    # Example of initiating a conversation with a user
    user_id = "user_12345"
    user_input = "Hello, what's your name?"
    
    chatbot = Chatbot()
    response = chatbot.initiate_chat(user_id, user_input)
    logger.info(f"Chatbot response: {response}")

# Next Steps:
"""
Model Integration: Integrate pre-trained models like BERT or GPT for advanced intent classification, improving the chatbot’s understanding and response accuracy.

Context Expansion: Enhance the context manager to support long-term conversations by maintaining session data or a knowledge base for richer interactions.

User Interaction: Add advanced features like voice recognition, multi-turn conversations, and personalized responses for a more dynamic and engaging user experience.

Advanced Scheduling: Implement complex scheduling logic, including recurring tasks, prioritization, and parallel processing, to handle tasks more efficiently.
"""
