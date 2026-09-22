"""
Real-time Camera Detection System
Monitors camera feed and automatically detects fire, animals, and humans
"""
import os
import sys
import cv2
import time
import django
from datetime import datetime

# Setup Django environment
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'flame_guard_project.settings')
django.setup()

# Import Django models and prediction module
from admin_module.models import ForestStation, FireAlert, Notification, CustomUser
from officer_module.models import HumanIntrusionAlert, UserAlert
from camera_module.ml import predict

# Configuration
DETECTION_INTERVAL = 5  # seconds between detections
CONFIDENCE_THRESHOLD = 0.2  # minimum confidence to create alert (20% - more sensitive!)
DEFAULT_STATION_ID = 1  # Default station for testing

class CameraMonitor:
    """Real-time camera monitoring with AI detection"""
    
    def __init__(self, station_id=DEFAULT_STATION_ID):
        self.station_id = station_id
        self.camera = None
        self.running = False
        
        # Load station
        try:
            self.station = ForestStation.objects.get(pk=station_id)
            print(f"✓ Monitoring station: {self.station.name}")
        except ForestStation.DoesNotExist:
            print(f"✗ Station {station_id} not found. Please create it first.")
            sys.exit(1)
    
    def start_camera(self):
        """Initialize camera"""
        print("\n[1/3] Starting camera...")
        self.camera = cv2.VideoCapture(0)  # 0 = default webcam
        
        if not self.camera.isOpened():
            print("✗ Could not open camera!")
            return False
        
        print("✓ Camera started successfully")
        return True
    
    def detect_and_alert(self, frame):
        """Run AI detection and create alerts"""
        
        # 1. Fire Detection
        fire_result = predict.predict_fire(frame)
        if fire_result.get('detected') and fire_result.get('confidence', 0) > CONFIDENCE_THRESHOLD * 100:
            self.create_fire_alert(fire_result['confidence'], frame)
        
        # 2. Animal Detection
        animal_result = predict.predict_animal(frame)
        if animal_result.get('animal') != 'none' and animal_result.get('confidence', 0) > CONFIDENCE_THRESHOLD * 100:
            self.create_animal_alert(animal_result['animal'], animal_result['confidence'], frame)
        
        # 3. Human Detection
        human_result = predict.predict_human(frame)
        if human_result.get('detected') and human_result.get('confidence', 0) > CONFIDENCE_THRESHOLD * 100:
            self.create_human_alert(human_result['confidence'], frame)
        
        # Display results
        print(f"\r🔥 Fire: {fire_result.get('confidence', 0):.1f}% | "
              f"🐅 Animal: {animal_result.get('animal', 'none')} ({animal_result.get('confidence', 0):.1f}%) | "
              f"🚶 Human: {human_result.get('confidence', 0):.1f}%", end='')
    
    def _frame_to_file(self, frame, prefix):
        """Encode a cv2 frame as JPEG and return a Django ContentFile"""
        import cv2
        from django.core.files.base import ContentFile
        _, buffer = cv2.imencode('.jpg', frame)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{prefix}_{timestamp}.jpg"
        return ContentFile(buffer.tobytes(), name=filename)

    def create_fire_alert(self, confidence, frame):
        """Create fire alert with captured frame image"""
        # Determine severity
        if confidence > 90:
            severity = 'CRITICAL'
        elif confidence > 75:
            severity = 'HIGH'
        elif confidence > 60:
            severity = 'MEDIUM'
        else:
            severity = 'LOW'
        
        # Save the fire frame image to the alert
        image_file = self._frame_to_file(frame, 'fire')
        alert = FireAlert.objects.create(
            station=self.station,
            severity=severity,
            location_details=f"AI Camera Detection (Confidence: {confidence:.1f}%)",
            image=image_file
        )
        
        print(f"\n🔥 FIRE ALERT CREATED! Severity: {severity}, Confidence: {confidence:.1f}%")
        
        # Notify officers and admin
        self.notify_all(f"🔥 Fire Detected at {self.station.name}", 
                       f"Severity: {severity}, Confidence: {confidence:.1f}%")
    
    def create_animal_alert(self, animal_type, confidence, frame):
        """Create user alert for animal sighting"""
        alert = UserAlert.objects.create(
            officer=self.get_admin_user(),
            title=f"{animal_type.title()} Spotted",
            message=f"A {animal_type} was detected at {self.station.name} by AI camera. Confidence: {confidence:.1f}%",
            alert_type='WARNING',
            location=self.station.name
        )
        
        print(f"\n🐅 ANIMAL ALERT CREATED! Type: {animal_type}, Confidence: {confidence:.1f}%")
        
        # Notify officers and admin
        self.notify_all(f"🐅 {animal_type.title()} Detected", 
                       f"Location: {self.station.name}, Confidence: {confidence:.1f}%")
    
    def create_human_alert(self, confidence, frame):
        """Create human intrusion alert with captured frame image"""
        image_file = self._frame_to_file(frame, 'human')
        alert = HumanIntrusionAlert.objects.create(
            station=self.station,
            location_details=f"AI Camera Detection (Confidence: {confidence:.1f}%)",
            officer_notified=True,
            image=image_file
        )
        
        print(f"\n🚶 HUMAN INTRUSION ALERT! Confidence: {confidence:.1f}%")
        
        # Notify officers and admin
        self.notify_all(f"🚶 Human Intrusion at {self.station.name}", 
                       f"Unauthorized person detected. Confidence: {confidence:.1f}%")
    
    def notify_all(self, title, message):
        """Send notifications to all officers and admin"""
        # Get admin user
        admin = self.get_admin_user()
        
        # Get all officers
        officers = CustomUser.objects.filter(user_type='OFFICER')
        
        # Send notifications
        for officer in officers:
            Notification.objects.create(
                from_admin=admin,
                to_officer=officer,
                title=title,
                message=message
            )
    
    def get_admin_user(self):
        """Get admin user for notifications"""
        try:
            return CustomUser.objects.filter(user_type='ADMIN').first()
        except:
            return None
    
    def run(self):
        """Main monitoring loop"""
        if not self.start_camera():
            return
        
        print("\n[2/3] Loading AI models...")
        print("✓ Models loaded")
        
        print("\n[3/3] Starting real-time detection...")
        print(f"Detection interval: {DETECTION_INTERVAL} seconds")
        print(f"Confidence threshold: {CONFIDENCE_THRESHOLD * 100}%")
        print("\nPress Ctrl+C to stop monitoring\n")
        print("="*70)
        
        self.running = True
        last_detection_time = 0
        
        try:
            while self.running:
                ret, frame = self.camera.read()
                
                if not ret:
                    print("\n✗ Failed to capture frame")
                    break
                
                # Display frame
                cv2.imshow('FLAME Guard - Camera Monitor', frame)
                
                # Run detection every N seconds
                current_time = time.time()
                if current_time - last_detection_time >= DETECTION_INTERVAL:
                    self.detect_and_alert(frame)
                    last_detection_time = current_time
                
                # Exit on 'q' key
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
                    
        except KeyboardInterrupt:
            print("\n\n✓ Monitoring stopped by user")
        finally:
            self.cleanup()
    
    def cleanup(self):
        """Release resources"""
        if self.camera:
            self.camera.release()
        cv2.destroyAllWindows()
        print("\n✓ Camera released")
        print("="*70)

def main():
    """Main entry point"""
    print("="*70)
    print(" FLAME GUARD - Real-time Camera Detection System")
    print("="*70)
    
    # Check if station exists
    try:
        station_count = ForestStation.objects.count()
        if station_count == 0:
            print("\n✗ No stations found in database!")
            print("Please create a station via Admin Panel first.")
            return
    except Exception as e:
        print(f"\n✗ Database error: {e}")
        print("Make sure Django server is configured correctly.")
        return
    
    # Start monitoring
    monitor = CameraMonitor(station_id=DEFAULT_STATION_ID)
    monitor.run()

if __name__ == "__main__":
    main()
