import cv2
import numpy as np
import logging
from typing import List, Dict
from skimage.feature import hog
from skimage import exposure
from .services.result_logging import log_task_result, log_task_failure
from .services.task_queue import schedule_task

# Set up logging
logger = logging.getLogger(__name__)

# --- Image Preprocessing ---
def load_image(image_path: str) -> np.ndarray:
    """
    Loads an image from a file path.
    """
    try:
        image = cv2.imread(image_path)
        if image is None:
            raise ValueError(f"Failed to load image from {image_path}")
        logger.info(f"Image loaded successfully from {image_path}")
        return image
    except Exception as e:
        logger.error(f"Error loading image from {image_path}: {e}")
        raise

def resize_image(image: np.ndarray, target_size: tuple) -> np.ndarray:
    """
    Resizes the input image to the target size.
    """
    try:
        resized_image = cv2.resize(image, target_size)
        logger.info(f"Image resized to {target_size}")
        return resized_image
    except Exception as e:
        logger.error(f"Error resizing image: {e}")
        raise

def normalize_image(image: np.ndarray) -> np.ndarray:
    """
    Normalize the image to have pixel values between 0 and 1.
    """
    try:
        normalized_image = image.astype(np.float32) / 255.0
        logger.info("Image normalization successful.")
        return normalized_image
    except Exception as e:
        logger.error(f"Error normalizing image: {e}")
        raise

# --- Feature Extraction ---
def extract_hog_features(image: np.ndarray, pixels_per_cell=(8, 8), cells_per_block=(2, 2)) -> np.ndarray:
    """
    Extracts Histogram of Oriented Gradients (HOG) features from the image.
    """
    try:
        # Convert image to grayscale for HOG extraction
        gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Extract HOG features
        fd, hog_image = hog(gray_image, pixels_per_cell=pixels_per_cell, cells_per_block=cells_per_block, visualize=True)
        
        # Enhance the HOG image for visualization
        hog_image_rescaled = exposure.rescale_intensity(hog_image, in_range=(0, 10))
        
        logger.info("HOG feature extraction successful.")
        return fd, hog_image_rescaled
    except Exception as e:
        logger.error(f"Error extracting HOG features: {e}")
        raise

def extract_sift_features(image: np.ndarray) -> List[cv2.KeyPoint]:
    """
    Extracts Scale-Invariant Feature Transform (SIFT) features from the image.
    """
    try:
        # Initialize SIFT detector
        sift = cv2.SIFT_create()
        
        # Detect keypoints and descriptors
        keypoints, descriptors = sift.detectAndCompute(image, None)
        
        logger.info(f"SIFT feature extraction successful: {len(keypoints)} keypoints detected.")
        return keypoints, descriptors
    except Exception as e:
        logger.error(f"Error extracting SIFT features: {e}")
        raise

# --- Utility Functions ---
def save_processed_image(image: np.ndarray, save_path: str):
    """
    Saves the processed image to the specified path.
    """
    try:
        cv2.imwrite(save_path, image)
        logger.info(f"Processed image saved at {save_path}")
    except Exception as e:
        logger.error(f"Error saving processed image: {e}")
        raise

# --- Vision Processing Task ---
def process_image_task(image_path: str, target_size: tuple = (224, 224), feature_type: str = 'hog') -> Dict:
    """
    Processes an image based on the requested feature extraction type.
    """
    try:
        # Load and preprocess image
        image = load_image(image_path)
        resized_image = resize_image(image, target_size)
        normalized_image = normalize_image(resized_image)
        
        # Extract features based on requested type
        if feature_type == 'hog':
            features, _ = extract_hog_features(normalized_image)
            feature_name = 'HOG'
        elif feature_type == 'sift':
            keypoints, descriptors = extract_sift_features(normalized_image)
            features = {"keypoints": keypoints, "descriptors": descriptors}
            feature_name = 'SIFT'
        else:
            raise ValueError("Unsupported feature type requested.")
        
        # Save processed image (optional)
        save_path = f"processed_{feature_name}_{image_path.split('/')[-1]}"
        save_processed_image(resized_image, save_path)
        
        # Log task result
        log_task_result(image_path, True, f"Feature extraction ({feature_name}) successful.")
        
        # Return the extracted features
        return {"status": "success", "features": features, "feature_name": feature_name}
    
    except Exception as e:
        logger.error(f"Error processing image {image_path}: {e}")
        log_task_failure(image_path, feature_type, str(e))
        return {"status": "error", "message": str(e)}

# --- Task Scheduling and Distributed Integration ---
def schedule_vision_task(image_path: str, target_size: tuple, feature_type: str):
    """
    Schedules the image processing task for distributed execution.
    """
    try:
        task_data = {"image_path": image_path, "target_size": target_size, "feature_type": feature_type}
        schedule_task("vision_processing", task_data)
        logger.info(f"Task for image {image_path} scheduled for feature extraction ({feature_type})")
    except Exception as e:
        logger.error(f"Error scheduling vision task for {image_path}: {e}")
        raise

# --- Example Usage ---
if __name__ == "__main__":
    # Example of processing an image with HOG features
    task_result = process_image_task("sample_image.jpg", target_size=(224, 224), feature_type='hog')
    logger.info(f"Task result: {task_result}")
    
    # Example of scheduling a task for distributed processing
    schedule_vision_task("sample_image.jpg", target_size=(224, 224), feature_type='sift')
