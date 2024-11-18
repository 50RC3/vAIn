import logging
import spacy
import json
from datetime import datetime
from typing import List, Dict, Any
from .nlp_pipeline import nlp_pipeline_task
from .services.result_logging import log_task_result, log_task_failure
from .services.task_queue import schedule_task
from .services.user_management import get_user_profile, update_user_profile
from .services.context_manager import ContextManager

# Set up logging
logger = logging.getLogger(__name__)

# Load pre-trained SpaCy model for NLP processing
nlp = spacy.load('en_core_web_sm')

# Initialize context manager for managing conversation state
context_manager = ContextManager()

# --- Chatbot Helper Functions ---

def clean_user_input(input_text: str) -> str:
    """
    Clean user input by removing unwanted characters and normalizing text.
    """
    try:
        # Remove non-alphanumeric characters, convert to lowercase
        cleaned_text = input_text.strip().lower()
        cleaned_text = ' '.join(cleaned_text.split())  # Remove excess spaces
        logger.info(f"Cleaned user input: {cleaned_text}")
        return cleaned_text
    except Exception as e:
        logger.error(f"Error cleaning user input: {e}")
        raise

def process_nlp_input(user_input: str) -> Dict[str, Any]:
    """
    Process the cleaned user input through the NLP pipeline.
    """
    try:
        # Process text with NLP pipeline
        result = nlp_pipeline_task(user_input)
        logger.info(f"NLP processing result: {result}")
        return result
    except Exception as e:
        logger.error(f"Error processing NLP input: {e}")
        raise

def get_response_from_intent(user_input: str) -> str:
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

# --- Conversation Management ---

def handle_user_message(user_id: str, user_input: str) -> str:
    """
    Handle the entire conversation flow by managing context and processing input.
    """
    try:
        # Step 1: Clean user input
        cleaned_input = clean_user_input(user_input)

        # Step 2: Check if there is an active conversation context for the user
        user_context = context_manager.get_user_context(user_id)
        
        # If no active context, create new context
        if not user_context:
            context_manager.create_new_context(user_id)

        # Step 3: Process the cleaned input through the NLP pipeline
        nlp_result = process_nlp_input(cleaned_input)
        
        # Step 4: Generate a response based on user input
        response = get_response_from_intent(cleaned_input)

        # Step 5: Update the user's profile/context (e.g., task tracking, preferences)
        update_user_profile(user_id, nlp_result)
        
        # Step 6: Log the result for future reference and debugging
        log_task_result(user_input, True, "Processed user message successfully.", nlp_result)

        return response
    except Exception as e:
        logger.error(f"Error handling user message: {e}")
        log_task_failure(user_input, "Chatbot", str(e))
        return "There was an error processing your request. Please try again later."

# --- Task Scheduling and Integration ---

def schedule_user_task(user_id: str, task_data: Dict[str, Any]) -> str:
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

# --- User Profile and Interaction Logging ---

def get_user_response(user_id: str, user_input: str) -> str:
    """
    Generate a response to the user based on their input and interaction history.
    """
    try:
        # Retrieve user profile
        user_profile = get_user_profile(user_id)

        # Step 1: Handle user message and generate response
        response = handle_user_message(user_id, user_input)

        # Step 2: Return the response to the user
        logger.info(f"Generated response for user {user_id}: {response}")
        return response
    except Exception as e:
        logger.error(f"Error generating user response: {e}")
        return "Sorry, I couldn't process your request."

# --- Chatbot API Interaction ---

def initiate_chat(user_id: str, user_input: str) -> Dict[str, Any]:
    """
    Start a new conversation or continue an existing one based on user input.
    """
    try:
        # Step 1: Retrieve user response based on input
        response = get_user_response(user_id, user_input)
        
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
    
    response = initiate_chat(user_id, user_input)
    logger.info(f"Chatbot response: {response}")

# Next Steps:
"""
Model Integration: Integrate pre-trained models like BERT or GPT for advanced intent classification, improving the chatbot’s understanding and response accuracy.

Context Expansion: Enhance the context manager to support long-term conversations by maintaining session data or a knowledge base for richer interactions.

User Interaction: Add advanced features like voice recognition, multi-turn conversations, and personalized responses for a more dynamic and engaging user experience.

Advanced Scheduling: Implement complex scheduling logic, including recurring tasks, prioritization, and parallel processing, to handle tasks more efficiently.
"""
