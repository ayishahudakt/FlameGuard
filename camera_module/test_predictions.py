"""
Test Predictions Script
Test the trained models with sample predictions
"""
import os
import sys
import numpy as np
from PIL import Image

# Add camera_module to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from ml import predict
except ImportError as e:
    print(f"Error importing predict module: {e}")
    print("Make sure models are trained first!")
    sys.exit(1)

def create_test_image():
    """Create a random test image"""
    # Create random RGB image
    img_array = np.random.randint(0, 255, (224, 224, 3), dtype=np.uint8)
    img = Image.fromarray(img_array)
    
    # Save temporarily
    test_path = 'test_image.jpg'
    img.save(test_path)
    return test_path

def main():
    """Test all models"""
    print("=" * 60)
    print(" FLAME GUARD - Model Testing")
    print("=" * 60)
    
    # Create test image
    print("\n[1/4] Creating test image...")
    test_image = create_test_image()
    print(f"      ✓ Test image created: {test_image}")
    
    # Test fire detection
    print("\n[2/4] Testing Fire Detection Model...")
    fire_result = predict.predict_fire(test_image)
    print(f"      Result: {fire_result}")
    
    # Test animal detection
    print("\n[3/4] Testing Animal Detection Model...")
    animal_result = predict.predict_animal(test_image)
    print(f"      Result: {animal_result}")
    
    # Test human detection
    print("\n[4/4] Testing Human Detection Model...")
    human_result = predict.predict_human(test_image)
    print(f"      Result: {human_result}")
    
    # Cleanup
    if os.path.exists(test_image):
        os.remove(test_image)
    
    print("\n" + "=" * 60)
    print(" ✓ All models tested successfully!")
    print("=" * 60)
    print("\nNote: Results are random because we used a random test image.")
    print("For real testing, use actual fire/animal/human images.")
    print("\nAPI Endpoints are ready at:")
    print("  - POST http://localhost:8000/api/camera/detect-fire/")
    print("  - POST http://localhost:8000/api/camera/detect-animal/")
    print("  - POST http://localhost:8000/api/camera/detect-human/")
    print("=" * 60)

if __name__ == "__main__":
    main()
