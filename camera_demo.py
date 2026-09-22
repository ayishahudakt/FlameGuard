"""
Simple Camera Detection Demo
Shows real-time detection without database requirements
"""
import cv2
import time
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Suppress TensorFlow warnings
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

try:
    from camera_module.ml import predict
    print("✓ AI models loaded successfully")
except Exception as e:
    print(f"✗ Error loading models: {e}")
    print("Make sure models are trained first!")
    sys.exit(1)

def main():
    """Simple camera monitoring demo"""
    print("="*70)
    print(" FLAME GUARD - Camera Detection Demo")
    print("="*70)
    print("\nStarting camera...")
    
    # Open camera
    camera = cv2.VideoCapture(0)
    
    if not camera.isOpened():
        print("✗ Could not open camera!")
        print("\nTroubleshooting:")
        print("  1. Check if webcam is connected")
        print("  2. Close other apps using camera (Zoom, Teams, etc.)")
        print("  3. Try running as administrator")
        return
    
    print("✓ Camera opened successfully")
    print("\nDetection Settings:")
    print("  - Detection interval: 5 seconds")
    print("  - Confidence threshold: 60%")
    print("\nControls:")
    print("  - Press 'Q' to quit")
    print("  - Press 'S' to take screenshot")
    print("\n" + "="*70)
    print("Starting detection...\n")
    
    last_detection_time = 0
    frame_count = 0
    
    try:
        while True:
            ret, frame = camera.read()
            
            if not ret:
                print("\n✗ Failed to capture frame")
                break
            
            frame_count += 1
            
            # Add text overlay
            cv2.putText(frame, "FLAME Guard - AI Detection", (10, 30),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            cv2.putText(frame, "Press Q to quit", (10, 60),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
            
            # Display frame
            cv2.imshow('FLAME Guard - Camera Monitor', frame)
            
            # Run detection every 5 seconds
            current_time = time.time()
            if current_time - last_detection_time >= 5:
                print(f"\n[Frame {frame_count}] Running detection...")
                
                # Fire detection
                fire_result = predict.predict_fire(frame)
                fire_conf = fire_result.get('confidence', 0)
                fire_detected = fire_result.get('detected', False)
                
                # Animal detection
                animal_result = predict.predict_animal(frame)
                animal_type = animal_result.get('animal', 'none')
                animal_conf = animal_result.get('confidence', 0)
                
                # Human detection
                human_result = predict.predict_human(frame)
                human_conf = human_result.get('confidence', 0)
                human_detected = human_result.get('detected', False)
                
                # Display results
                print(f"  🔥 Fire: {'YES' if fire_detected else 'NO'} ({fire_conf:.1f}%)")
                print(f"  🐅 Animal: {animal_type} ({animal_conf:.1f}%)")
                print(f"  🚶 Human: {'YES' if human_detected else 'NO'} ({human_conf:.1f}%)")
                
                # Alert if high confidence
                if fire_detected and fire_conf > 60:
                    print("  ⚠️  FIRE ALERT! High confidence detection")
                if animal_type != 'none' and animal_conf > 60:
                    print(f"  ⚠️  ANIMAL ALERT! {animal_type.upper()} detected")
                if human_detected and human_conf > 60:
                    print("  ⚠️  HUMAN INTRUSION ALERT!")
                
                last_detection_time = current_time
            
            # Handle keyboard input
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q') or key == ord('Q'):
                print("\n\nStopping camera monitoring...")
                break
            elif key == ord('s') or key == ord('S'):
                filename = f"screenshot_{int(time.time())}.jpg"
                cv2.imwrite(filename, frame)
                print(f"\n📸 Screenshot saved: {filename}")
    
    except KeyboardInterrupt:
        print("\n\nStopped by user (Ctrl+C)")
    
    finally:
        camera.release()
        cv2.destroyAllWindows()
        print("✓ Camera released")
        print("="*70)

if __name__ == "__main__":
    main()
