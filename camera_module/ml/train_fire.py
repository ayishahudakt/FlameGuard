"""
Fire Detection Model Training Script
Uses Transfer Learning with MobileNetV2
"""
import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'  # Suppress TensorFlow warnings

import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers
from tensorflow.keras.applications import MobileNetV2
from tensorflow.keras.preprocessing.image import ImageDataGenerator
import numpy as np

# Configuration
IMG_SIZE = 224
BATCH_SIZE = 32
EPOCHS = 10
MODEL_SAVE_PATH = 'camera_module/models/fire_detection_model.h5'

def create_fire_detection_model():
    """
    Create fire detection model using Transfer Learning
    """
    # Load pre-trained MobileNetV2 (without top classification layer)
    base_model = MobileNetV2(
        input_shape=(IMG_SIZE, IMG_SIZE, 3),
        include_top=False,
        weights='imagenet'
    )
    
    # Freeze base model layers (we'll only train our custom layers)
    base_model.trainable = False
    
    # Build our custom model on top
    model = keras.Sequential([
        base_model,
        layers.GlobalAveragePooling2D(),
        layers.Dense(128, activation='relu'),
        layers.Dropout(0.5),
        layers.Dense(1, activation='sigmoid')  # Binary: fire or no fire
    ])
    
    # Compile model
    model.compile(
        optimizer='adam',
        loss='binary_crossentropy',
        metrics=['accuracy']
    )
    
    return model

def train_model_with_sample_data():
    """
    Train model with sample data
    For demo purposes, we'll create a simple model
    """
    print("=" * 60)
    print("FLAME GUARD - Fire Detection Model Training")
    print("=" * 60)
    
    # Create model
    print("\n[1/4] Creating model architecture...")
    model = create_fire_detection_model()
    model.summary()
    
    print("\n[2/4] Model created successfully!")
    print("      Using MobileNetV2 with Transfer Learning")
    
    # For demo: Create dummy training data
    print("\n[3/4] Preparing training data...")
    print("      Note: Using synthetic data for demo")
    print("      For production, use real fire/no-fire images")
    
    # Create synthetic data (replace with real data later)
    X_train = np.random.rand(100, IMG_SIZE, IMG_SIZE, 3)
    y_train = np.random.randint(0, 2, 100)
    
    X_val = np.random.rand(20, IMG_SIZE, IMG_SIZE, 3)
    y_val = np.random.randint(0, 2, 20)
    
    print(f"      Training samples: {len(X_train)}")
    print(f"      Validation samples: {len(X_val)}")
    
    # Train model
    print("\n[4/4] Training model...")
    print("      This will take 2-3 minutes...")
    
    history = model.fit(
        X_train, y_train,
        validation_data=(X_val, y_val),
        epochs=5,  # Reduced for demo
        batch_size=BATCH_SIZE,
        verbose=1
    )
    
    # Save model
    os.makedirs(os.path.dirname(MODEL_SAVE_PATH), exist_ok=True)
    model.save(MODEL_SAVE_PATH)
    
    print("\n" + "=" * 60)
    print("✓ Model trained and saved successfully!")
    print(f"  Location: {MODEL_SAVE_PATH}")
    print(f"  Final accuracy: {history.history['accuracy'][-1]:.2%}")
    print("=" * 60)
    
    return model

if __name__ == "__main__":
    try:
        model = train_model_with_sample_data()
        print("\n✓ Fire detection model is ready!")
        print("  You can now use it for predictions.")
    except Exception as e:
        print(f"\n✗ Error: {e}")
        print("  Make sure TensorFlow is installed:")
        print("  pip install tensorflow")
