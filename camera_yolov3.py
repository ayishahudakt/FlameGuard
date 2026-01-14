"""
Enhanced YOLO Detection using YOLOv3 weights
Uses OpenCV DNN module with custom YOLOv3 configuration
"""
import cv2
import numpy as np
import time
import sys
import os
import django

# Setup Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'flame_guard_project.settings')
django.setup()

from admin_module.models import ForestStation, FireAlert, Notification, CustomUser
from officer_module.models import HumanIntrusionAlert, UserAlert

# Configuration
DETECTION_INTERVAL = 10  # Run detection every 10 seconds
CONFIDENCE_THRESHOLD = 0.5  # 50% confidence
NMS_THRESHOLD = 0.4  # Non-maximum suppression

# Paths to YOLO files
YOLO_DIR = "yolo-coco"
WEIGHTS_PATH = os.path.join(YOLO_DIR, "yolov3.weights")
CONFIG_PATH = os.path.join(YOLO_DIR, "yolov3.cfg")
NAMES_PATH = os.path.join(YOLO_DIR, "coco.names")

# Animal classes from COCO
ANIMAL_CLASSES = ['bird', 'cat', 'dog', 'horse', 'sheep', 'cow', 'elephant', 'bear', 'zebra', 'giraffe']
HUMAN_CLASS = 'person'

def load_yolo_model():
    """Load YOLOv3 model using OpenCV DNN"""
    print("Loading YOLOv3 model...")
    
    # Load class names
    with open(NAMES_PATH, 'r') as f:
        classes = [line.strip() for line in f.readlines()]
    
    # Load YOLO network
    net = cv2.dnn.readNetFromDarknet(CONFIG_PATH, WEIGHTS_PATH)
    net.setPreferableBackend(cv2.dnn.DNN_BACKEND_OPENCV)
    net.setPreferableTarget(cv2.dnn.DNN_TARGET_CPU)
    
    # Get output layer names
    layer_names = net.getLayerNames()
    output_layers = [layer_names[i - 1] for i in net.getUnconnectedOutLayers()]
    
    print("✓ YOLOv3 model loaded successfully")
    return net, classes, output_layers

def detect_fire_by_color(frame):
    """Detect fire using color analysis"""
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    
    # Fire color ranges
    lower_fire1 = np.array([0, 100, 100])
    upper_fire1 = np.array([20, 255, 255])
    lower_fire2 = np.array([20, 100, 100])
    upper_fire2 = np.array([40, 255, 255])
    
    mask1 = cv2.inRange(hsv, lower_fire1, upper_fire1)
    mask2 = cv2.inRange(hsv, lower_fire2, upper_fire2)
    fire_mask = cv2.bitwise_or(mask1, mask2)
    
    fire_pixels = cv2.countNonZero(fire_mask)
    total_pixels = frame.shape[0] * frame.shape[1]
    fire_percentage = (fire_pixels / total_pixels) * 100
    
    confidence = min(fire_percentage / 10, 1.0)
    detected = fire_percentage > 2
    
    return detected, confidence

class YOLOv3Detector:
    """Enhanced YOLO detection with YOLOv3 weights"""
    
    def __init__(self, station_id=1):
        self.station_id = station_id
        self.camera = None
        self.net = None
        self.classes = None
        self.output_layers = None
        self.station = None
        
        print("="*70)
        print(" FLAME GUARD - YOLOv3 Enhanced Detection")
        print("="*70)
    
    def initialize(self):
        """Initialize system"""
        print("\n[1/4] Loading YOLOv3 model...")
        try:
            self.net, self.classes, self.output_layers = load_yolo_model()
        except Exception as e:
            print(f"✗ Error loading YOLO: {e}")
            return False
        
        print("\n[2/4] Connecting to database...")
        try:
            self.station = ForestStation.objects.first()
            if not self.station:
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
        print("✓ Camera opened")
        
        print("\n[4/4] System ready!")
        print(f"\nDetection Settings:")
        print(f"  - Model: YOLOv3 (Darknet)")
        print(f"  - Weights: 248MB pre-trained")
        print(f"  - Classes: 80 (COCO dataset)")
        print(f"  - Confidence: {CONFIDENCE_THRESHOLD*100}%")
        print(f"  - Station: {self.station.name}")
        print("\nControls: Press Q to quit")
        print("="*70 + "\n")
        
        return True
    
    def detect_objects(self, frame):
        """Run YOLOv3 detection"""
        height, width = frame.shape[:2]
        
        # Prepare image for YOLO
        blob = cv2.dnn.blobFromImage(frame, 1/255.0, (416, 416), swapRB=True, crop=False)
        self.net.setInput(blob)
        outputs = self.net.forward(self.output_layers)
        
        # Process detections
        class_ids = []
        confidences = []
        boxes = []
        
        for output in outputs:
            for detection in output:
                scores = detection[5:]
                class_id = np.argmax(scores)
                confidence = scores[class_id]
                
                if confidence > CONFIDENCE_THRESHOLD:
                    center_x = int(detection[0] * width)
                    center_y = int(detection[1] * height)
                    w = int(detection[2] * width)
                    h = int(detection[3] * height)
                    x = int(center_x - w/2)
                    y = int(center_y - h/2)
                    
                    boxes.append([x, y, w, h])
                    confidences.append(float(confidence))
                    class_ids.append(class_id)
        
        # Non-maximum suppression
        indices = cv2.dnn.NMSBoxes(boxes, confidences, CONFIDENCE_THRESHOLD, NMS_THRESHOLD)
        
        detections = {
            'fire': False,
            'fire_conf': 0,
            'animals': [],
            'animal_conf': 0,
            'human': False,
            'human_conf': 0
        }
        
        # Fire detection (color-based)
        fire_detected, fire_conf = detect_fire_by_color(frame)
        detections['fire'] = fire_detected
        detections['fire_conf'] = fire_conf
        
        # Process YOLO detections
        if len(indices) > 0:
            for i in indices.flatten():
                class_name = self.classes[class_ids[i]]
                conf = confidences[i]
                
                if class_name in ANIMAL_CLASSES:
                    detections['animals'].append(class_name)
                    detections['animal_conf'] = max(detections['animal_conf'], conf)
                
                elif class_name == HUMAN_CLASS:
                    detections['human'] = True
                    detections['human_conf'] = max(detections['human_conf'], conf)
        
        return detections
    
    def create_fire_alert(self, confidence):
        """Create fire alert"""
        severity = 'CRITICAL' if confidence > 0.9 else 'HIGH' if confidence > 0.75 else 'MEDIUM'
        
        # Get proper location from station
        location = f"{self.station.name}, {self.station.division.name}"
        
        alert = FireAlert.objects.create(
            station=self.station,
            severity=severity,
            location_details=location
        )
        
        print(f"\n  🔥 FIRE ALERT CREATED!")
        print(f"     Alert ID: {alert.id}")
        print(f"     Severity: {severity}")
        print(f"     Location: {location}")
        
        self.notify_officers(
            f"🔥 Fire at {self.station.name}",
            f"Severity: {severity}, Conf: {confidence*100:.1f}%"
        )
    
    def create_animal_alert(self, animals, confidence):
        """Create animal alert"""
        admin = CustomUser.objects.filter(user_type='ADMIN').first()
        if not admin:
            return
        
        animal_list = ', '.join(set(animals))
        location = f"{self.station.name}, {self.station.division.name}"
        
        alert = UserAlert.objects.create(
            officer=admin,
            title=f"Wildlife: {animal_list.title()}",
            message=f"At {location}. Conf: {confidence*100:.1f}%",
            alert_type='WARNING',
            location=location
        )
        
        print(f"\n  🐅 ANIMAL ALERT!")
        print(f"     Animals: {animal_list}")
        print(f"     Location: {location}")
        
        self.notify_officers(
            f"🐅 Wildlife: {animal_list.title()}",
            f"Location: {location}"
        )
    
    def create_human_alert(self, confidence):
        """Create human intrusion alert"""
        # Get proper location from station
        location = f"{self.station.name}, {self.station.division.name}"
        
        alert = HumanIntrusionAlert.objects.create(
            station=self.station,
            location_details=location,
            officer_notified=True
        )
        
        print(f"\n  🚶 HUMAN INTRUSION!")
        print(f"     Alert ID: {alert.id}")
        print(f"     Location: {location}")
        
        self.notify_officers(
            f"🚶 Intrusion at {self.station.name}",
            f"Location: {location}, Conf: {confidence*100:.1f}%"
        )
    
    def notify_officers(self, title, message):
        """Send notifications"""
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
                    break
                
                frame_count += 1
                
                # Overlay
                cv2.putText(frame, "FLAME Guard - YOLOv3", (10, 30),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                
                cv2.imshow('FLAME Guard - YOLOv3 Detection', frame)
                
                # Detect
                current_time = time.time()
                if current_time - last_detection >= DETECTION_INTERVAL:
                    print(f"\n[Frame {frame_count}] Running YOLOv3...")
                    
                    detections = self.detect_objects(frame)
                    
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
        print("✓ Detection stopped")
        print("="*70)

def main():
    detector = YOLOv3Detector()
    detector.run()

if __name__ == "__main__":
    main()
