"""
Master Training Script - Train All Models
Run this script to train all three AI models
"""
import os
import sys

print("=" * 70)
print(" FLAME GUARD - AI Model Training Suite")
print("=" * 70)
print("\nThis script will train 3 AI models:")
print("  1. Fire Detection Model")
print("  2. Animal Detection Model")
print("  3. Human Detection Model")
print("\nEstimated time: 10-15 minutes total")
print("=" * 70)

# Check if TensorFlow is installed
try:
    import tensorflow as tf
    print(f"\n✓ TensorFlow {tf.__version__} detected")
except ImportError:
    print("\n✗ TensorFlow not found!")
    print("\nPlease install it first:")
    print("  pip install tensorflow")
    sys.exit(1)

# Import training scripts
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ml import train_fire, train_animal, train_human

def main():
    """Train all models"""
    
    print("\n" + "=" * 70)
    print(" STEP 1/3: Training Fire Detection Model")
    print("=" * 70)
    try:
        train_fire.train_model_with_sample_data()
    except Exception as e:
        print(f"✗ Error training fire model: {e}")
        return
    
    print("\n" + "=" * 70)
    print(" STEP 2/3: Training Animal Detection Model")
    print("=" * 70)
    try:
        train_animal.train_model_with_sample_data()
    except Exception as e:
        print(f"✗ Error training animal model: {e}")
        return
    
    print("\n" + "=" * 70)
    print(" STEP 3/3: Training Human Detection Model")
    print("=" * 70)
    try:
        train_human.train_model_with_sample_data()
    except Exception as e:
        print(f"✗ Error training human model: {e}")
        return
    
    print("\n" + "=" * 70)
    print(" ✓ ALL MODELS TRAINED SUCCESSFULLY!")
    print("=" * 70)
    print("\nModels saved in: camera_module/models/")
    print("\nYou can now:")
    print("  1. Test predictions: python camera_module/test_predictions.py")
    print("  2. Use Django API endpoints:")
    print("     - POST /api/camera/detect-fire/")
    print("     - POST /api/camera/detect-animal/")
    print("     - POST /api/camera/detect-human/")
    print("\n" + "=" * 70)

if __name__ == "__main__":
    main()
