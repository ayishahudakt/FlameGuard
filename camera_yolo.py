"""
YOLO-based Detection System
High accuracy real-time detection using YOLOv8
"""
import cv2
import time
import sys
import os
import django

# Setup Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'flame_guard_project.settings')
django.setup()

from ultralytics import YOLO
from admin_module.models import ForestStation, FireAlert, Notification, CustomUser
from officer_module.models import HumanIntrusionAlert, UserAlert

# Configuration
DETECTION_INTERVAL = 5  # seconds
CONFIDENCE_THRESHOLD = 0.6  # 60% confidence

# YOLO class mappings (COCO dataset doesn't have 'fire')
# We'll use color-based detection for fire
ANIMAL_CLASSES = ['elephant', 'bear', 'zebra', 'giraffe', 'horse', 'cow', 'sheep', 'dog', 'cat', 'bird']
HUMAN_CLASS = 'person'

def detect_fire_by_color(frame):
    """
    Detect fire using color analysis (red/orange/yellow pixels)
    Returns: (detected: bool, confidence: float)
    """
    import numpy as np
    
    # Convert BGR to HSV
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    
    # Define fire color ranges (red, orange, yellow)
    # Red-orange range
    lower_fire1 = np.array([0, 100, 100])
    upper_fire1 = np.array([20, 255, 255])
    
    # Yellow-orange range
    lower_fire2 = np.array([20, 100, 100])
    upper_fire2 = np.array([40, 255, 255])
    
    # Create masks
    mask1 = cv2.inRange(hsv, lower_fire1, upper_fire1)
    mask2 = cv2.inRange(hsv, lower_fire2, upper_fire2)
    
    # Combine masks
    fire_mask = cv2.bitwise_or(mask1, mask2)
    
    # Calculate percentage of fire pixels
    fire_pixels = cv2.countNonZero(fire_mask)
    total_pixels = frame.shape[0] * frame.shape[1]
    fire_percentage = (fire_pixels / total_pixels) * 100
    
    # Confidence based on percentage
    confidence = min(fire_percentage / 10, 1.0)  # Max at 10% coverage
    detected = fire_percentage > 2  # Detect if > 2% of image is fire-colored
    
    return detected, confidence

class YOLODetector:
    """YOLO-based detection system"""
    
    def __init__(self, station_id=1):
        self.station_id = station_id
        self.camera = None
        self.model = None
        self.station = None
        
        print("="*70)
        print(" FLAME GUARD - YOLO Detection System")
        print("="*70)
        
    def initialize(self):
        """Initialize YOLO model and camera"""
        print("\n[1/4] Loading YOLO model...")
        try:
            # Load YOLOv8 nano model (fastest)
            self.model = YOLO('yolov8n.pt')
            print("✓ YOLOv8 model loaded successfully")
        except Exception as e:
            print(f"✗ Error loading YOLO model: {e}")
            print("Downloading model... (this happens once)")
            self.model = YOLO('yolov8n.pt')
            print("✓ Model downloaded and loaded")
        
        print("\n[2/4] Connecting to database...")
        try:
            self.station = ForestStation.objects.first()
            if not self.station:
                print("✗ No station found. Creating demo station...")
                from admin_module.models import ForestDivision
                division = ForestDivision.objects.first()
                if not division:
                    division = ForestDivision.objects.create(
                        name="Demo Division",
                        location="Demo Location"
                    )
                self.station = ForestStation.objects.create(
                    division=division,
                    name="Demo Station",
                    location="Demo Location"
                )
            print(f"✓ Using station: {self.station.name}")
        except Exception as e:
            print(f"✗ Database error: {e}")
            return False
        
        print("\n[3/4] Opening camera...")
        self.camera = cv2.VideoCapture(0)
        if not self.camera.isOpened():
            print("✗ Could not open camera!")
            return False
        print("✓ Camera opened successfully")
        
        print("\n[4/4] System ready!")
        print(f"\nDetection Settings:")
        print(f"  - Model: YOLOv8 Nano")
        print(f"  - Interval: {DETECTION_INTERVAL} seconds")
        print(f"  - Confidence: {CONFIDENCE_THRESHOLD*100}%")
        print(f"  - Station: {self.station.name}")
        print("\nControls: Press Q to quit")
        print("="*70 + "\n")
        
        return True
    
    def detect_objects(self, frame):
        """Run YOLO detection + color-based fire detection"""
        results = self.model(frame, conf=CONFIDENCE_THRESHOLD, verbose=False)
        
        detections = {
            'fire': False,
            'fire_conf': 0,
            'animals': [],
            'animal_conf': 0,
            'human': False,
            'human_conf': 0
        }
        
        # Color-based fire detection
        fire_detected, fire_conf = detect_fire_by_color(frame)
        detections['fire'] = fire_detected
        detections['fire_conf'] = fire_conf
        
        # Process YOLO detections for animals and humans
        for result in results:
            boxes = result.boxes
            for box in boxes:
                cls = int(box.cls[0])
                conf = float(box.conf[0])
                class_name = result.names[cls]
                
                # Check for animals
                if class_name.lower() in ANIMAL_CLASSES:
                    detections['animals'].append(class_name)
                    detections['animal_conf'] = max(detections['animal_conf'], conf)
                
                # Check for humans
                elif class_name.lower() == HUMAN_CLASS:
                    detections['human'] = True
                    detections['human_conf'] = max(detections['human_conf'], conf)
        
        return detections
    
    def create_fire_alert(self, confidence):
        """Create fire alert in database"""
        severity = 'CRITICAL' if confidence > 0.9 else 'HIGH' if confidence > 0.75 else 'MEDIUM'
        
        alert = FireAlert.objects.create(
            station=self.station,
            severity=severity,
            location_details=f"YOLO Detection (Confidence: {confidence*100:.1f}%)"
        )
        
        print(f"\n  🔥 FIRE ALERT CREATED!")
        print(f"     Alert ID: {alert.id}")
        print(f"     Severity: {severity}")
        print(f"     Confidence: {confidence*100:.1f}%")
        
        self.notify_officers(
            f"🔥 Fire Detected at {self.station.name}",
            f"Severity: {severity}, Confidence: {confidence*100:.1f}%"
        )
    
    def create_animal_alert(self, animals, confidence):
        """Create animal alert"""
        admin = CustomUser.objects.filter(user_type='ADMIN').first()
        if not admin:
            return
        
        animal_list = ', '.join(set(animals))
        
        alert = UserAlert.objects.create(
            officer=admin,
            title=f"Wildlife Spotted: {animal_list.title()}",
            message=f"Detected at {self.station.name}. Confidence: {confidence*100:.1f}%",
            alert_type='WARNING',
            location=self.station.name
        )
        
        print(f"\n  🐅 ANIMAL ALERT CREATED!")
        print(f"     Alert ID: {alert.id}")
        print(f"     Animals: {animal_list}")
        print(f"     Confidence: {confidence*100:.1f}%")
        
        self.notify_officers(
            f"🐅 Wildlife Detected: {animal_list.title()}",
            f"Location: {self.station.name}, Confidence: {confidence*100:.1f}%"
        )
    
    def create_human_alert(self, confidence):
        """Create human intrusion alert"""
        alert = HumanIntrusionAlert.objects.create(
            station=self.station,
            location_details=f"YOLO Detection (Confidence: {confidence*100:.1f}%)",
            officer_notified=True
        )
        
        print(f"\n  🚶 HUMAN INTRUSION ALERT!")
        print(f"     Alert ID: {alert.id}")
        print(f"     Confidence: {confidence*100:.1f}%")
        
        self.notify_officers(
            f"🚶 Human Intrusion at {self.station.name}",
            f"Unauthorized person detected. Confidence: {confidence*100:.1f}%"
        )
    
    def notify_officers(self, title, message):
        """Send notifications to officers"""
        admin = CustomUser.objects.filter(user_type='ADMIN').first()
        if not admin:
            return
        
        officers = CustomUser.objects.filter(user_type='OFFICER')
        count = 0
        
        for officer in officers:
            Notification.objects.create(
                from_admin=admin,
                to_officer=officer,
                title=title,
                message=message
            )
            count += 1
        
        if count > 0:
            print(f"     📧 Sent to {count} officer(s)")
    
    def run(self):
        """Main detection loop"""
        if not self.initialize():
            return
        
        last_detection = 0
        frame_count = 0
        
        try:
            while True:
                ret, frame = self.camera.read()
                if not ret:
                    print("\n✗ Failed to capture frame")
                    break
                
                frame_count += 1
                
                # Add overlay
                cv2.putText(frame, "FLAME Guard - YOLO Detection", (10, 30),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                cv2.putText(frame, "Press Q to quit", (10, 60),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
                
                # Display
                cv2.imshow('FLAME Guard - YOLO Detection', frame)
                
                # Detect every N seconds
                current_time = time.time()
                if current_time - last_detection >= DETECTION_INTERVAL:
                    print(f"\n[Frame {frame_count}] Running YOLO detection...")
                    
                    detections = self.detect_objects(frame)
                    
                    # Display results
                    print(f"  🔥 Fire: {'YES' if detections['fire'] else 'NO'} ({detections['fire_conf']*100:.1f}%)")
                    
                    if detections['animals']:
                        print(f"  🐅 Animals: {', '.join(set(detections['animals']))} ({detections['animal_conf']*100:.1f}%)")
                    else:
                        print(f"  🐅 Animals: None")
                    
                    print(f"  🚶 Human: {'YES' if detections['human'] else 'NO'} ({detections['human_conf']*100:.1f}%)")
                    
                    # Create alerts
                    if detections['fire']:
                        self.create_fire_alert(detections['fire_conf'])
                    
                    if detections['animals']:
                        self.create_animal_alert(detections['animals'], detections['animal_conf'])
                    
                    if detections['human']:
                        self.create_human_alert(detections['human_conf'])
                    
                    last_detection = current_time
                
                # Exit on Q
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
        
        except KeyboardInterrupt:
            print("\n\nStopped by user")
        finally:
            self.cleanup()
    
    def cleanup(self):
        """Release resources"""
        if self.camera:
            self.camera.release()
        cv2.destroyAllWindows()
        print("\n" + "="*70)
        print("✓ Camera released. Detection stopped.")
        print("="*70)

def main():
    detector = YOLODetector()
    detector.run()

if __name__ == "__main__":
    main()
