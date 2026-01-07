"""
API Testing Script for FLAME Guard
Tests all three AI detection APIs
"""
import requests
import os
from PIL import Image
import numpy as np

# API Base URL
BASE_URL = "http://localhost:8000/api/camera"

# Create a test image
def create_test_image(filename="test_image.jpg"):
    """Create a random test image"""
    img_array = np.random.randint(0, 255, (224, 224, 3), dtype=np.uint8)
    img = Image.fromarray(img_array)
    img.save(filename)
    return filename

def test_fire_detection_api():
    """Test Fire Detection API"""
    print("\n" + "="*60)
    print("Testing Fire Detection API")
    print("="*60)
    
    # Create test image
    test_image = create_test_image("test_fire.jpg")
    
    try:
        # Make API request
        url = f"{BASE_URL}/detect-fire/"
        files = {'image': open(test_image, 'rb')}
        data = {'station_id': 1}
        
        print(f"Sending request to: {url}")
        response = requests.post(url, files=files, data=data)
        
        # Print results
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        
        if response.status_code == 200:
            print("✓ Fire Detection API is working!")
        else:
            print("✗ API returned an error")
            
    except Exception as e:
        print(f"✗ Error: {e}")
    finally:
        # Cleanup
        if os.path.exists(test_image):
            os.remove(test_image)

def test_animal_detection_api():
    """Test Animal Detection API"""
    print("\n" + "="*60)
    print("Testing Animal Detection API")
    print("="*60)
    
    # Create test image
    test_image = create_test_image("test_animal.jpg")
    
    try:
        # Make API request
        url = f"{BASE_URL}/detect-animal/"
        files = {'image': open(test_image, 'rb')}
        
        print(f"Sending request to: {url}")
        response = requests.post(url, files=files)
        
        # Print results
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        
        if response.status_code == 200:
            print("✓ Animal Detection API is working!")
        else:
            print("✗ API returned an error")
            
    except Exception as e:
        print(f"✗ Error: {e}")
    finally:
        # Cleanup
        if os.path.exists(test_image):
            os.remove(test_image)

def test_human_detection_api():
    """Test Human Detection API"""
    print("\n" + "="*60)
    print("Testing Human Detection API")
    print("="*60)
    
    # Create test image
    test_image = create_test_image("test_human.jpg")
    
    try:
        # Make API request
        url = f"{BASE_URL}/detect-human/"
        files = {'image': open(test_image, 'rb')}
        data = {'station_id': 1}
        
        print(f"Sending request to: {url}")
        response = requests.post(url, files=files, data=data)
        
        # Print results
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        
        if response.status_code == 200:
            print("✓ Human Detection API is working!")
        else:
            print("✗ API returned an error")
            
    except Exception as e:
        print(f"✗ Error: {e}")
    finally:
        # Cleanup
        if os.path.exists(test_image):
            os.remove(test_image)

def main():
    """Run all API tests"""
    print("="*60)
    print(" FLAME GUARD - API Testing Suite")
    print("="*60)
    print("\nMake sure Django server is running at http://localhost:8000")
    print("Press Enter to continue...")
    input()
    
    # Test all APIs
    test_fire_detection_api()
    test_animal_detection_api()
    test_human_detection_api()
    
    print("\n" + "="*60)
    print(" Testing Complete!")
    print("="*60)
    print("\nNote: Results are random because we used random test images.")
    print("For real testing, use actual fire/animal/human images.")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nTesting cancelled by user.")
    except Exception as e:
        print(f"\n\nError: {e}")
        print("\nMake sure:")
        print("  1. Django server is running")
        print("  2. AI models are trained")
        print("  3. 'requests' library is installed: pip install requests")
