"""
Prediction Module - Load models and make predictions
"""
import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

import numpy as np
from PIL import Image
import tensorflow as tf
import cv2

# Model paths
FIRE_MODEL_PATH = 'camera_module/models/fire_detection_model.h5'
ANIMAL_MODEL_PATH = 'camera_module/models/animal_detection_model.h5'
HUMAN_MODEL_PATH = 'camera_module/models/human_detection_model.h5'
ANIMAL_CLASSES_PATH = 'camera_module/models/animal_classes.txt'

# Image size
IMG_SIZE = 224

# Global model variables (loaded once)
fire_model = None
animal_model = None
human_model = None
animal_classes = []

def load_models():
    """Load all trained models into memory"""
    global fire_model, animal_model, human_model, animal_classes
    
    try:
        # Load fire detection model
        if os.path.exists(FIRE_MODEL_PATH):
            fire_model = tf.keras.models.load_model(FIRE_MODEL_PATH)
            print("✓ Fire detection model loaded")
        
        # Load animal detection model
        if os.path.exists(ANIMAL_MODEL_PATH):
            animal_model = tf.keras.models.load_model(ANIMAL_MODEL_PATH)
            print("✓ Animal detection model loaded")
            
            # Load animal classes
            if os.path.exists(ANIMAL_CLASSES_PATH):
                with open(ANIMAL_CLASSES_PATH, 'r') as f:
                    animal_classes = [line.strip() for line in f.readlines()]
        
        # Load human detection model
        if os.path.exists(HUMAN_MODEL_PATH):
            human_model = tf.keras.models.load_model(HUMAN_MODEL_PATH)
            print("✓ Human detection model loaded")
            
    except Exception as e:
        print(f"Error loading models: {e}")

def preprocess_image(image_path_or_file):
    """
    Preprocess image for model prediction
    
    Args:
        image_path_or_file: Path to image file, file object, or numpy array
    
    Returns:
        Preprocessed image array
    """
    try:
        # Check if it's already a numpy array (from OpenCV)
        if isinstance(image_path_or_file, np.ndarray):
            img_array = image_path_or_file
            # Convert BGR to RGB (OpenCV uses BGR)
            img_array = cv2.cvtColor(img_array, cv2.COLOR_BGR2RGB)
        else:
            # Load image from file
            if isinstance(image_path_or_file, str):
                img = Image.open(image_path_or_file)
            else:
                img = Image.open(image_path_or_file)
            
            # Convert to RGB
            img = img.convert('RGB')
            
            # Resize
            img = img.resize((IMG_SIZE, IMG_SIZE))
            
            # Convert to array
            img_array = np.array(img)
        
        # Resize if needed
        if img_array.shape[:2] != (IMG_SIZE, IMG_SIZE):
            img_array = cv2.resize(img_array, (IMG_SIZE, IMG_SIZE))
        
        # Normalize (0-1 range)
        img_array = img_array / 255.0
        
        # Add batch dimension
        img_array = np.expand_dims(img_array, axis=0)
        
        return img_array
        
    except Exception as e:
        print(f"Error preprocessing image: {e}")
        return None

def predict_fire(image_path_or_file):
    """
    Predict if image contains fire
    
    Returns:
        dict: {'detected': bool, 'confidence': float}
    """
    global fire_model
    
    if fire_model is None:
        return {'detected': False, 'confidence': 0.0, 'error': 'Model not loaded'}
    
    try:
        # Preprocess
        img_array = preprocess_image(image_path_or_file)
        if img_array is None:
            return {'detected': False, 'confidence': 0.0, 'error': 'Image preprocessing failed'}
        
        # Predict
        prediction = fire_model.predict(img_array, verbose=0)[0][0]
        
        # Threshold: 0.5
        detected = prediction > 0.5
        confidence = float(prediction) if detected else float(1 - prediction)
        
        return {
            'detected': bool(detected),
            'confidence': round(confidence * 100, 2)
        }
        
    except Exception as e:
        return {'detected': False, 'confidence': 0.0, 'error': str(e)}

def predict_animal(image_path_or_file):
    """
    Predict animal type in image
    
    Returns:
        dict: {'animal': str, 'confidence': float, 'all_predictions': dict}
    """
    global animal_model, animal_classes
    
    if animal_model is None:
        return {'animal': 'none', 'confidence': 0.0, 'error': 'Model not loaded'}
    
    try:
        # Preprocess
        img_array = preprocess_image(image_path_or_file)
        if img_array is None:
            return {'animal': 'none', 'confidence': 0.0, 'error': 'Image preprocessing failed'}
        
        # Predict
        predictions = animal_model.predict(img_array, verbose=0)[0]
        
        # Get top prediction
        top_index = np.argmax(predictions)
        top_confidence = float(predictions[top_index])
        
        # Get animal name
        animal_name = animal_classes[top_index] if animal_classes else f"class_{top_index}"
        
        # All predictions
        all_preds = {
            animal_classes[i] if animal_classes else f"class_{i}": round(float(predictions[i]) * 100, 2)
            for i in range(len(predictions))
        }
        
        return {
            'animal': animal_name,
            'confidence': round(top_confidence * 100, 2),
            'all_predictions': all_preds
        }
        
    except Exception as e:
        return {'animal': 'none', 'confidence': 0.0, 'error': str(e)}

def predict_human(image_path_or_file):
    """
    Predict if image contains human
    
    Returns:
        dict: {'detected': bool, 'confidence': float}
    """
    global human_model
    
    if human_model is None:
        return {'detected': False, 'confidence': 0.0, 'error': 'Model not loaded'}
    
    try:
        # Preprocess
        img_array = preprocess_image(image_path_or_file)
        if img_array is None:
            return {'detected': False, 'confidence': 0.0, 'error': 'Image preprocessing failed'}
        
        # Predict
        prediction = human_model.predict(img_array, verbose=0)[0][0]
        
        # Threshold: 0.5
        detected = prediction > 0.5
        confidence = float(prediction) if detected else float(1 - prediction)
        
        return {
            'detected': bool(detected),
            'confidence': round(confidence * 100, 2)
        }
        
    except Exception as e:
        return {'detected': False, 'confidence': 0.0, 'error': str(e)}

# Load models when module is imported
load_models()
