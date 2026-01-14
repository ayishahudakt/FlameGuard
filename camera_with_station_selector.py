"""
Enhanced YOLOv3 Detection with Station Selection
Users can choose which forest station to monitor
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

from admin_module.models import ForestStation, FireAlert, Notification, CustomUser, ForestDivision
from officer_module.models import HumanIntrusionAlert, UserAlert

# Configuration
DETECTION_INTERVAL = 10  # Run detection every 10 seconds
CONFIDENCE_THRESHOLD = 0.3  # Lowered to 30% for better animal detection
NMS_THRESHOLD = 0.4

# Paths to YOLO files
YOLO_DIR = "yolo-coco"
WEIGHTS_PATH = os.path.join(YOLO_DIR, "yolov3.weights")
CONFIG_PATH = os.path.join(YOLO_DIR, "yolov3.cfg")
NAMES_PATH = os.path.join(YOLO_DIR, "coco.names")

# All animal classes from COCO dataset
# NOTE: COCO does NOT include tiger, cheetah, leopard, lion, deer, monkey
# Available animals: bird, cat, dog, horse, sheep, cow, elephant, bear, zebra, giraffe
ANIMAL_CLASSES = [
    'bird', 'cat', 'dog', 'horse', 'sheep', 'cow', 
    'elephant', 'bear', 'zebra', 'giraffe'
]
HUMAN_CLASS = 'person'

def load_yolo_model():
    """Load YOLOv3 model"""
    print("Loading YOLOv3 model...")
    
    with open(NAMES_PATH, 'r') as f:
        classes = [line.strip() for line in f.readlines()]
    
    net = cv2.dnn.readNetFromDarknet(CONFIG_PATH, WEIGHTS_PATH)
    net.setPreferableBackend(cv2.dnn.DNN_BACKEND_OPENCV)
    net.setPreferableTarget(cv2.dnn.DNN_TARGET_CPU)
    
    layer_names = net.getLayerNames()
    output_layers = [layer_names[i - 1] for i in net.getUnconnectedOutLayers()]
    
    print("✓ YOLOv3 model loaded successfully")
    return net, classes, output_layers

def detect_fire_by_color(frame):
    """Detect fire using color analysis"""
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    
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

def select_station():
    """Interactive station selection"""
    print("\n" + "="*70)
    print(" SELECT FOREST STATION FOR MONITORING")
    print("="*70)
    
    stations = ForestStation.objects.all()
    
    if not stations.exists():
        print("\n⚠️  No stations found in database!")
        print("\nCreating demo stations...")
        
        # Create demo division if needed
        division, _ = ForestDivision.objects.get_or_create(
            name="KEEZHATOOR",
            defaults={'location': 'Kerala', 'description': 'Demo Division'}
        )
        
        # Create demo stations
        demo_stations = [
            {"name": "FOREST OFFICE", "division": division, "contact": "9876543210", "address": "Keezhatoor, Kerala"},
            {"name": "Silent Valley Station", "division": division, "contact": "9876543211", "address": "Silent Valley, Palakkad"},
            {"name": "Wayanad Station", "division": division, "contact": "9876543212", "address": "Wayanad, Kerala"},
        ]
        
        for station_data in demo_stations:
            ForestStation.objects.get_or_create(
                name=station_data["name"],
                division=station_data["division"],
                defaults={
                    'contact_number': station_data["contact"],
                    'address': station_data["address"]
                }
            )
        
        stations = ForestStation.objects.all()
        print("✓ Demo stations created\n")
    
    # Display stations
    print("\nAvailable Stations:\n")
    for idx, station in enumerate(stations, 1):
        print(f"  {idx}. {station.name} ({station.division.name})")
        print(f"     Address: {station.address}")
        print()
    
    # Get user selection
    while True:
        try:
            choice = input(f"Select station (1-{stations.count()}): ").strip()
            choice_num = int(choice)
            
            if 1 <= choice_num <= stations.count():
                selected_station = list(stations)[choice_num - 1]
                print(f"\n✓ Selected: {selected_station.name}, {selected_station.division.name}")
                return selected_station
            else:
                print(f"❌ Please enter a number between 1 and {stations.count()}")
        except ValueError:
            print("❌ Please enter a valid number")
        except KeyboardInterrupt:
            print("\n\nCancelled by user")
            sys.exit(0)

class YOLOv3Detector:
    """Enhanced YOLO detection with station selection"""
    
    def __init__(self, station=None):
        self.station = station
        self.camera = None
        self.net = None
        self.classes = None
        self.output_layers = None
        
        print("="*70)
        print(" FLAME GUARD - YOLOv3 Detection with Station Selection")
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
        if not self.station:
            print("✗ No station selected!")
            return False
        print(f"✓ Monitoring station: {self.station.name}, {self.station.division.name}")
        
        print("\n[3/4] Opening camera...")
        self.camera = cv2.VideoCapture(0)
        if not self.camera.isOpened():
            print("✗ Could not open camera!")
            return False
        print("✓ Camera opened")
        
        print("\n[4/4] System ready!")
        print(f"\nMonitoring Configuration:")
        print(f"  - Station: {self.station.name}")
        print(f"  - Division: {self.station.division.name}")
        print(f"  - Location: {self.station.address}")
        print(f"  - Detection Interval: {DETECTION_INTERVAL} seconds")
        print(f"  - Confidence Threshold: {CONFIDENCE_THRESHOLD*100}%")
        print("\nAll alerts will show location as:")
        print(f"  → {self.station.name}, {self.station.division.name}")
        print("\nControls: Press Q to quit")
        print("="*70 + "\n")
        
        return True
    
    def detect_objects(self, frame):
        """Run YOLOv3 detection"""
        height, width = frame.shape[:2]
        
        blob = cv2.dnn.blobFromImage(frame, 1/255.0, (416, 416), swapRB=True, crop=False)
        self.net.setInput(blob)
        outputs = self.net.forward(self.output_layers)
        
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
        
        indices = cv2.dnn.NMSBoxes(boxes, confidences, CONFIDENCE_THRESHOLD, NMS_THRESHOLD)
        
        detections = {
            'fire': False,
            'fire_conf': 0,
            'animals': [],
            'animal_conf': 0,
            'human': False,
            'human_conf': 0
        }
        
        fire_detected, fire_conf = detect_fire_by_color(frame)
        detections['fire'] = fire_detected
        detections['fire_conf'] = fire_conf
        
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
                
                # Display station info on frame
                cv2.putText(frame, f"FLAME Guard - {self.station.name}", (10, 30),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                cv2.putText(frame, f"{self.station.division.name}", (10, 60),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
                
                cv2.imshow('FLAME Guard - YOLOv3 Detection', frame)
                
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
    # Let user select station
    selected_station = select_station()
    
    # Start detection with selected station
    detector = YOLOv3Detector(station=selected_station)
    detector.run()

if __name__ == "__main__":
    main()
