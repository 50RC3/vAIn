import re
import logging
import spacy
import nltk
from nltk.tokenize import word_tokenize
from nltk.tag import pos_tag
from nltk.chunk import ne_chunk
from nltk.corpus import stopwords
from typing import List, Tuple, Dict, Any
from .services.result_logging import log_task_result, log_task_failure
from .services.task_queue import schedule_task
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get configuration from environment variables
SPACY_MODEL = os.getenv('SPACY_MODEL', 'en_core_web_sm')
NLTK_DATA_PATH = os.getenv('NLTK_DATA_PATH')
MAX_SEQUENCE_LENGTH = int(os.getenv('MAX_SEQUENCE_LENGTH', '512'))

# Set NLTK data path
if NLTK_DATA_PATH:
    nltk.data.path.append(NLTK_DATA_PATH)

# Set up logging
logger = logging.getLogger(__name__)

# Verify NLTK downloads
def verify_nltk_downloads():
    required_data = ['punkt', 'stopwords', 'averaged_perceptron_tagger']
    for item in required_data:
        try:
            nltk.data.find(f'tokenizers/{item}')
        except LookupError:
            nltk.download(item)

verify_nltk_downloads()

class NLPPipeline:
    def __init__(self):
        try:
            self.nlp = spacy.load(SPACY_MODEL)
        except OSError:
            logging.error(f"SpaCy model {SPACY_MODEL} not found. Installing...")
            from spacy.cli import download
            download(SPACY_MODEL)
            self.nlp = spacy.load(SPACY_MODEL)

# --- NLP Pipeline Setup ---
# Load pre-trained SpaCy NLP model (for NER and Dependency Parsing)
try:
    nlp = spacy.load(SPACY_MODEL)
except OSError:
    logging.error(f"SpaCy model {SPACY_MODEL} not found. Installing...")
    from spacy.cli import download
    download(SPACY_MODEL)
    nlp = spacy.load(SPACY_MODEL)

# --- Preprocessing ---
def clean_text(text: str) -> str:
    """
    Clean the input text by removing unwanted characters and normalizing.
    """
    try:
        # Remove special characters, URLs, and extra spaces
        text = re.sub(r'http\S+', '', text)  # Remove URLs
        text = re.sub(r'\d+', '', text)  # Remove digits
        text = re.sub(r'[^\w\s]', '', text)  # Remove punctuation
        text = text.lower().strip()  # Convert to lowercase and remove leading/trailing spaces
        logger.info("Text cleaned successfully.")
        return text
    except Exception as e:
        logger.error(f"Error cleaning text: {e}")
        raise

def tokenize_text(text: str) -> List[str]:
    """
    Tokenize the cleaned text into words using NLTK tokenizer.
    """
    try:
        tokens = word_tokenize(text)
        logger.info(f"Tokenized text into {len(tokens)} tokens.")
        return tokens
    except Exception as e:
        logger.error(f"Error tokenizing text: {e}")
        raise

# --- Named Entity Recognition (NER) ---
def perform_ner(text: str) -> List[Dict[str, Any]]:
    """
    Perform Named Entity Recognition (NER) using SpaCy's pre-trained model.
    Returns a list of named entities and their labels.
    """
    try:
        doc = nlp(text)
        entities = [{"text": ent.text, "label": ent.label_} for ent in doc.ents]
        logger.info(f"Detected {len(entities)} named entities.")
        return entities
    except Exception as e:
        logger.error(f"Error in Named Entity Recognition: {e}")
        raise

# --- Part-of-Speech (POS) Tagging ---
def pos_tagging(tokens: List[str]) -> List[Tuple[str, str]]:
    """
    Perform POS tagging using NLTK's POS tagger.
    Returns a list of tuples (word, POS tag).
    """
    try:
        tagged = pos_tag(tokens)
        logger.info(f"Tagged {len(tagged)} tokens with part-of-speech tags.")
        return tagged
    except Exception as e:
        logger.error(f"Error in POS tagging: {e}")
        raise

# --- Stopwords Removal ---
def remove_stopwords(tokens: List[str]) -> List[str]:
    """
    Remove stopwords from the list of tokens.
    """
    try:
        stop_words = set(stopwords.words('english'))
        filtered_tokens = [word for word in tokens if word not in stop_words]
        logger.info(f"Removed stopwords, remaining tokens: {len(filtered_tokens)}.")
        return filtered_tokens
    except Exception as e:
        logger.error(f"Error removing stopwords: {e}")
        raise

# --- Sentiment Analysis (Optional) ---
# You can integrate a sentiment analysis model here if needed.
def analyze_sentiment(text: str) -> Dict[str, Any]:
    """
    Perform sentiment analysis on the input text (optional step).
    """
    # Placeholder for sentiment analysis logic (e.g., using pre-trained models like VADER, BERT, etc.)
    sentiment = {
        'positive': 0.85,
        'neutral': 0.1,
        'negative': 0.05
    }
    logger.info(f"Sentiment analysis result: {sentiment}")
    return sentiment

# --- Text Classification (Optional) ---
# Placeholder for text classification (can integrate a model like BERT or custom ML models)
def classify_text(text: str) -> str:
    """
    Perform text classification (e.g., topic classification, spam detection, etc.).
    """
    # Placeholder for classification logic (e.g., using a BERT model or a custom classifier)
    classification = "General"
    logger.info(f"Text classified as: {classification}")
    return classification

# --- NLP Pipeline Task ---
def nlp_pipeline_task(text: str) -> Dict:
    """
    Run the full NLP pipeline on the input text and log the results.
    """
    try:
        # Step 1: Clean the text
        cleaned_text = clean_text(text)
        
        # Step 2: Tokenize the cleaned text
        tokens = tokenize_text(cleaned_text)
        
        # Step 3: Perform Named Entity Recognition (NER)
        entities = perform_ner(cleaned_text)
        
        # Step 4: Perform Part-of-Speech (POS) tagging
        pos_tags = pos_tagging(tokens)
        
        # Step 5: Remove stopwords
        filtered_tokens = remove_stopwords(tokens)
        
        # Step 6: Sentiment Analysis (optional)
        sentiment = analyze_sentiment(cleaned_text)
        
        # Step 7: Text Classification (optional)
        classification = classify_text(cleaned_text)
        
        # Step 8: Log results
        result = {
            "entities": entities,
            "pos_tags": pos_tags,
            "filtered_tokens": filtered_tokens,
            "sentiment": sentiment,
            "classification": classification
        }
        
        # Log the results
        log_task_result(text, True, "NLP pipeline task completed successfully.", result)
        
        return {"status": "success", "result": result}
    
    except Exception as e:
        logger.error(f"Error processing NLP pipeline task: {e}")
        log_task_failure(text, "NLP Pipeline", str(e))
        return {"status": "error", "message": str(e)}

# --- Task Scheduling ---
def schedule_nlp_pipeline_task(text: str):
    """
    Schedules the NLP pipeline task for distributed execution.
    """
    try:
        task_data = {"text": text}
        schedule_task("nlp_pipeline", task_data)
        logger.info(f"Task for text scheduled for NLP pipeline processing.")
    except Exception as e:
        logger.error(f"Error scheduling NLP pipeline task: {e}")
        raise

# --- Example Usage ---
if __name__ == "__main__":
    # Example of processing a text document through the NLP pipeline
    text = "John Doe is a software engineer at Acme Corp. He works on AI projects."
    task_result = nlp_pipeline_task(text)
    logger.info(f"NLP Task result: {task_result}")
    
    # Example of scheduling an NLP pipeline task
    schedule_nlp_pipeline_task(text)

#Next Steps:
"""
Integration: Integrate this module with other services like result logging and task scheduling.
Expand: Extend the pipeline with additional features like machine translation, summarization, or question answering.
Optimize: Fine-tune the models (e.g., BERT, GPT) for domain-specific tasks and integrate them into the pipeline.
Scalability: Implement distributed NLP pipelines to handle larger datasets or real-time processing.
This module is designed to be highly extensible, allowing for easy integration of new NLP tasks and models as the vAIn AGI system evolves.
"""
