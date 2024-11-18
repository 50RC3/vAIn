import cv2
import numpy as np
import logging
from typing import List, Dict, Tuple
from tensorflow.keras.preprocessing import image as keras_image
from .services.result_logging import log_task_result, log_task_failure
from .services.task_queue import schedule_task

# Set up logging
logger = logging.getLogger(__name__)

# --- Object Detection Setup ---
# Load YOLO or Faster R-CNN pre-trained models (you can switch models as needed)
MODEL_TYPE = 'YOLO'  # Options: 'YOLO', 'FasterRCNN'

# YOLO Configurations (YOLOv3 as an example)
yolo_net = cv2.dnn.readNetFromDarknet('yolov3.cfg', 'yolov3.weights')
layer_names = yolo_net.getLayerNames()
output_layers = [layer_names[i - 1] for i in yolo_net.getUnconnectedOutLayers()]

# Faster R-CNN Setup (Optional)
# from tensorflow import keras
# faster_rcnn_model = keras.applications.ResNet50(weights='imagenet') # Example of a pre-trained model

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

def preprocess_image(image: np.ndarray, model_type: str = 'YOLO') -> np.ndarray:
    """
    Preprocess the image based on the selected model (YOLO or Faster R-CNN).
    """
    try:
        if model_type == 'YOLO':
            blob = cv2.dnn.blobFromImage(image, 0.00392, (416, 416), (0, 0, 0), True, crop=False)
            yolo_net.setInput(blob)
            logger.info("Image preprocessed for YOLO")
            return blob
        elif model_type == 'FasterRCNN':
            # Preprocessing for Faster R-CNN (Example)
            # faster_rcnn_preprocessed = some_preprocessing_method(image)
            logger.info("Image preprocessed for Faster R-CNN")
            return image
        else:
            raise ValueError("Unsupported model type.")
    except Exception as e:
        logger.error(f"Error in preprocessing image: {e}")
        raise

# --- Object Detection (YOLO) ---
def detect_objects_yolo(image: np.ndarray) -> List[Dict]:
    """
    Perform object detection using the YOLO model.
    Returns a list of detected objects with their bounding boxes and class names.
    """
    try:
        # Run inference with YOLO
        outputs = yolo_net.forward(output_layers)
        
        height, width, channels = image.shape
        class_ids = []
        confidences = []
        boxes = []
        
        # Post-process YOLO outputs
        for output in outputs:
            for detection in output:
                scores = detection[5:]
                class_id = np.argmax(scores)
                confidence = scores[class_id]
                
                if confidence > 0.5:  # Confidence threshold
                    center_x = int(detection[0] * width)
                    center_y = int(detection[1] * height)
                    w = int(detection[2] * width)
                    h = int(detection[3] * height)
                    
                    # Rectangular box coordinates
                    x = int(center_x - w / 2)
                    y = int(center_y - h / 2)
                    
                    boxes.append([x, y, w, h])
                    confidences.append(float(confidence))
                    class_ids.append(class_id)
        
        # Non-maxima suppression to eliminate overlapping boxes
        indexes = cv2.dnn.NMSBoxes(boxes, confidences, 0.5, 0.4)
        
        detected_objects = []
        for i in range(len(boxes)):
            if i in indexes:
                x, y, w, h = boxes[i]
                detected_objects.append({
                    'class_id': class_ids[i],
                    'confidence': confidences[i],
                    'bounding_box': (x, y, w, h)
                })
        
        logger.info(f"Detected {len(detected_objects)} objects.")
        return detected_objects
    except Exception as e:
        logger.error(f"Error in YOLO object detection: {e}")
        raise

# --- Object Detection (Faster R-CNN) ---
# def detect_objects_fasterrcnn(image: np.ndarray) -> List[Dict]:
#     """
#     Perform object detection using Faster R-CNN model.
#     Returns a list of detected objects with bounding boxes and class names.
#     """
#     try:
#         # Example processing with pre-trained Faster R-CNN model
#         detections = faster_rcnn_model.predict(image)
#         detected_objects = parse_faster_rcnn_detections(detections)
#         logger.info(f"Detected {len(detected_objects)} objects.")
#         return detected_objects
#     except Exception as e:
#         logger.error(f"Error in Faster R-CNN object detection: {e}")
#         raise

# --- Post-processing ---
def draw_bounding_boxes(image: np.ndarray, detected_objects: List[Dict]) -> np.ndarray:
    """
    Draws bounding boxes and labels on the image based on detected objects.
    """
    try:
        for obj in detected_objects:
            x, y, w, h = obj['bounding_box']
            label = f"Class {obj['class_id']} - {obj['confidence']:.2f}"
            cv2.rectangle(image, (x, y), (x+w, y+h), (0, 255, 0), 2)
            cv2.putText(image, label, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
        logger.info(f"Bounding boxes drawn for {len(detected_objects)} objects.")
        return image
    except Exception as e:
        logger.error(f"Error drawing bounding boxes: {e}")
        raise

# --- Object Detection Task ---
def object_detection_task(image_path: str, model_type: str = 'YOLO') -> Dict:
    """
    Detects objects in the image and logs the results.
    """
    try:
        # Load and preprocess image
        image = load_image(image_path)
        preprocessed_image = preprocess_image(image, model_type)
        
        # Perform object detection
        if model_type == 'YOLO':
            detected_objects = detect_objects_yolo(image)
        else:
            # Fallback if model is not YOLO
            detected_objects = []  # Placeholder for Faster R-CNN or other models
            logger.warning(f"Object detection not implemented for {model_type}")
        
        # Draw bounding boxes on the image
        image_with_boxes = draw_bounding_boxes(image, detected_objects)
        
        # Save processed image with bounding boxes
        output_path = f"output_{model_type}_{image_path.split('/')[-1]}"
        cv2.imwrite(output_path, image_with_boxes)
        logger.info(f"Processed image saved at {output_path}")
        
        # Log task result
        log_task_result(image_path, True, f"Object detection ({model_type}) successful.")
        
        # Return results
        return {"status": "success", "detected_objects": detected_objects, "output_image_path": output_path}
    
    except Exception as e:
        logger.error(f"Error processing object detection task for {image_path}: {e}")
        log_task_failure(image_path, model_type, str(e))
        return {"status": "error", "message": str(e)}

# --- Task Scheduling ---
def schedule_object_detection_task(image_path: str, model_type: str):
    """
    Schedules the object detection task for distributed execution.
    """
    try:
        task_data = {"image_path": image_path, "model_type": model_type}
        schedule_task("object_detection", task_data)
        logger.info(f"Task for image {image_path} scheduled for {model_type} object detection.")
    except Exception as e:
        logger.error(f"Error scheduling object detection task for {image_path}: {e}")
        raise

# --- Example Usage ---
if __name__ == "__main__":
    # Example of processing an image with YOLO object detection
    task_result = object_detection_task("sample_image.jpg", model_type='YOLO')
    logger.info(f"Task result: {task_result}")
    
    # Example of scheduling a task for distributed processing
    schedule_object_detection_task("sample_image.jpg", model_type='YOLO')

# Next Steps:
    """
    Integration: Integrate this module into the vAIn project.
    Task Queue: Set up a task queue (like Celery) for handling scheduled tasks.
    Model Optimization: Fine-tune YOLO or Faster R-CNN for your specific use cases, and add support for more models.
    """
