"""
Animal Detection Model Training Script
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
NUM_CLASSES = 4  # tiger, elephant, deer, none
MODEL_SAVE_PATH = 'camera_module/models/animal_detection_model.h5'

ANIMAL_CLASSES = ['tiger', 'elephant', 'deer', 'none']

def create_animal_detection_model():
    """
    Create animal detection model using Transfer Learning
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
        layers.Dense(256, activation='relu'),
        layers.Dropout(0.5),
        layers.Dense(128, activation='relu'),
        layers.Dropout(0.3),
        layers.Dense(NUM_CLASSES, activation='softmax')  # Multi-class
    ])
    
    # Compile
    model.compile(
        optimizer='adam',
        loss='sparse_categorical_crossentropy',
        metrics=['accuracy']
    )
    
    return model

def train_model_with_sample_data():
    """
    Train animal detection model
    """
    print("=" * 60)
    print("FLAME GUARD - Animal Detection Model Training")
    print("=" * 60)
    
    # Create model
    print("\n[1/4] Creating model architecture...")
    model = create_animal_detection_model()
    
    print("\n[2/4] Model created successfully!")
    print(f"      Classes: {', '.join(ANIMAL_CLASSES)}")
    
    # Create synthetic data
    print("\n[3/4] Preparing training data...")
    print("      Note: Using synthetic data for demo")
    
    X_train = np.random.rand(200, IMG_SIZE, IMG_SIZE, 3)
    y_train = np.random.randint(0, NUM_CLASSES, 200)
    
    X_val = np.random.rand(40, IMG_SIZE, IMG_SIZE, 3)
    y_val = np.random.randint(0, NUM_CLASSES, 40)
    
    print(f"      Training samples: {len(X_train)}")
    print(f"      Validation samples: {len(X_val)}")
    
    # Train
    print("\n[4/4] Training model...")
    print("      This will take 3-4 minutes...")
    
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
    
    # Save class names
    class_file = 'camera_module/models/animal_classes.txt'
    with open(class_file, 'w') as f:
        f.write('\n'.join(ANIMAL_CLASSES))
    
    print("\n" + "=" * 60)
    print("✓ Model trained and saved successfully!")
    print(f"  Model: {MODEL_SAVE_PATH}")
    print(f"  Classes: {class_file}")
    print(f"  Final accuracy: {history.history['accuracy'][-1]:.2%}")
    print("=" * 60)
    
    return model

if __name__ == "__main__":
    try:
        model = train_model_with_sample_data()
        print("\n✓ Animal detection model is ready!")
    except Exception as e:
        print(f"\n✗ Error: {e}")
        print("  Make sure TensorFlow is installed:")
        print("  pip install tensorflow")
