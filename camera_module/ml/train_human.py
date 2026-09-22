"""
Human Detection Model Training Script
Uses Transfer Learning with MobileNetV2
"""
import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers
from tensorflow.keras.applications import MobileNetV2
import numpy as np

# Configuration
IMG_SIZE = 224
BATCH_SIZE = 32
EPOCHS = 10
MODEL_SAVE_PATH = 'camera_module/models/human_detection_model.h5'

def create_human_detection_model():
    """
    Create human detection model using Transfer Learning
    """
    # Load pre-trained MobileNetV2
    base_model = MobileNetV2(
        input_shape=(IMG_SIZE, IMG_SIZE, 3),
        include_top=False,
        weights='imagenet'
    )
    
    # Freeze base model
    base_model.trainable = False
    
    # Build custom model
    model = keras.Sequential([
        base_model,
        layers.GlobalAveragePooling2D(),
        layers.Dense(128, activation='relu'),
        layers.Dropout(0.5),
        layers.Dense(1, activation='sigmoid')  # Binary: human or no human
    ])
    
    # Compile
    model.compile(
        optimizer='adam',
        loss='binary_crossentropy',
        metrics=['accuracy']
    )
    
    return model

def train_model_with_sample_data():
    """
    Train human detection model
    """
    print("=" * 60)
    print("FLAME GUARD - Human Detection Model Training")
    print("=" * 60)
    
    # Create model
    print("\n[1/4] Creating model architecture...")
    model = create_human_detection_model()
    
    print("\n[2/4] Model created successfully!")
    print("      Detection: Human / No Human")
    
    # Create synthetic data
    print("\n[3/4] Preparing training data...")
    print("      Note: Using synthetic data for demo")
    
    X_train = np.random.rand(150, IMG_SIZE, IMG_SIZE, 3)
    y_train = np.random.randint(0, 2, 150)
    
    X_val = np.random.rand(30, IMG_SIZE, IMG_SIZE, 3)
    y_val = np.random.randint(0, 2, 30)
    
    print(f"      Training samples: {len(X_train)}")
    print(f"      Validation samples: {len(X_val)}")
    
    # Train
    print("\n[4/4] Training model...")
    print("      This will take 2-3 minutes...")
    
    history = model.fit(
        X_train, y_train,
        validation_data=(X_val, y_val),
        epochs=5,
        batch_size=BATCH_SIZE,
        verbose=1
    )
    
    # Save
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
        print("\n✓ Human detection model is ready!")
    except Exception as e:
        print(f"\n✗ Error: {e}")
        print("  Make sure TensorFlow is installed:")
        print("  pip install tensorflow")
