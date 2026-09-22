"""
Enhanced Camera Detection with Database Integration
Detects and creates alerts in database
"""
import cv2
import time
import sys
import os
import django

# Setup Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'flame_guard_project.settings')
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
django.setup()

# Import models
from admin_module.models import ForestStation, FireAlert, Notification, CustomUser
from officer_module.models import HumanIntrusionAlert, UserAlert
from camera_module.ml import predict

# Configuration - HIGH THRESHOLD TO PREVENT FALSE ALERTS
DETECTION_INTERVAL = 5
CONFIDENCE_THRESHOLD = 80  # 80% - Very high to avoid false positives with synthetic data

def get_or_create_station():
    """Get first station or create demo station"""
    station = ForestStation.objects.first()
    if not station:
        from admin_module.models import ForestDivision
        division = ForestDivision.objects.first()
        if not division:
            division = ForestDivision.objects.create(
                name="Demo Division",
                location="Demo Location"
            )
        station = ForestStation.objects.create(
            division=division,
            name="Demo Station",
            location="Demo Location"
        )
        print(f"✓ Created demo station: {station.name}")
    return station

def get_admin():
    """Get admin user"""
    admin = CustomUser.objects.filter(user_type='ADMIN').first()
    if not admin:
        print("⚠️  No admin user found. Alerts will be created but notifications skipped.")
    return admin

def create_fire_alert(station, confidence):
    """Create fire alert in database"""
    severity = 'CRITICAL' if confidence > 90 else 'HIGH' if confidence > 75 else 'MEDIUM' if confidence > 50 else 'LOW'
    
    alert = FireAlert.objects.create(
        station=station,
        severity=severity,
        location_details=f"AI Camera Detection (Confidence: {confidence:.1f}%)"
    )
    
    print(f"\n  ✅ FIRE ALERT CREATED IN DATABASE!")
    print(f"     Alert ID: {alert.id}, Severity: {severity}")
    
    # Notify officers
    notify_officers(station, f"🔥 Fire Detected at {station.name}", 
                   f"Severity: {severity}, Confidence: {confidence:.1f}%")
    return alert

def create_animal_alert(station, animal_type, confidence):
    """Create user alert for animal"""
    admin = get_admin()
    if not admin:
        return None
    
    alert = UserAlert.objects.create(
        officer=admin,
        title=f"{animal_type.title()} Spotted",
        message=f"A {animal_type} was detected at {station.name}. Confidence: {confidence:.1f}%",
        alert_type='WARNING',
        location=station.name
    )
    
    print(f"\n  ✅ ANIMAL ALERT CREATED IN DATABASE!")
    print(f"     Alert ID: {alert.id}, Animal: {animal_type}")
    
    # Notify officers
    notify_officers(station, f"🐅 {animal_type.title()} Detected", 
                   f"Location: {station.name}, Confidence: {confidence:.1f}%")
    return alert

def create_human_alert(station, confidence):
    """Create human intrusion alert"""
    alert = HumanIntrusionAlert.objects.create(
        station=station,
        location_details=f"AI Camera Detection (Confidence: {confidence:.1f}%)",
        officer_notified=True
    )
    
    print(f"\n  ✅ HUMAN INTRUSION ALERT CREATED IN DATABASE!")
    print(f"     Alert ID: {alert.id}")
    
    # Notify officers
    notify_officers(station, f"🚶 Human Intrusion at {station.name}", 
                   f"Unauthorized person detected. Confidence: {confidence:.1f}%")
    return alert

def notify_officers(station, title, message):
    """Send notifications to officers"""
    admin = get_admin()
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
        print(f"     📧 Sent notifications to {count} officer(s)")

def main():
    print("="*70)
    print(" FLAME GUARD - Enhanced Camera Detection")
    print("="*70)
    print("\n[1/3] Initializing database...")
    
    station = get_or_create_station()
    print(f"✓ Using station: {station.name}")
    
    print("\n[2/3] Loading AI models...")
    print("✓ Models loaded")
    
    print("\n[3/3] Starting camera...")
    camera = cv2.VideoCapture(0)
    
    if not camera.isOpened():
        print("✗ Could not open camera!")
        return
    
    print("✓ Camera started")
    print(f"\nDetection Settings:")
    print(f"  - Interval: {DETECTION_INTERVAL} seconds")
    print(f"  - Threshold: {CONFIDENCE_THRESHOLD}% (LOWERED FOR TESTING)")
    print(f"\nControls: Press Q to quit\n")
    print("="*70 + "\n")
    
    last_detection = 0
    frame_count = 0
    
    try:
        while True:
            ret, frame = camera.read()
            if not ret:
                break
            
            frame_count += 1
            
            # Display
            cv2.putText(frame, "FLAME Guard - Enhanced Detection", (10, 30),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            cv2.imshow('FLAME Guard - Camera Monitor', frame)
            
            # Detect every N seconds
            current_time = time.time()
            if current_time - last_detection >= DETECTION_INTERVAL:
                print(f"[Frame {frame_count}] Detecting...")
                
                # Run detections
                fire_result = predict.predict_fire(frame)
                animal_result = predict.predict_animal(frame)
                human_result = predict.predict_human(frame)
                
                fire_conf = fire_result.get('confidence', 0)
                animal_conf = animal_result.get('confidence', 0)
                animal_type = animal_result.get('animal', 'none')
                human_conf = human_result.get('confidence', 0)
                
                # Display
                print(f"  🔥 Fire: {fire_conf:.1f}%")
                print(f"  🐅 Animal: {animal_type} ({animal_conf:.1f}%)")
                print(f"  🚶 Human: {human_conf:.1f}%")
                
                # Create alerts if above threshold
                if fire_conf > CONFIDENCE_THRESHOLD:
                    create_fire_alert(station, fire_conf)
                
                if animal_type != 'none' and animal_conf > CONFIDENCE_THRESHOLD:
                    create_animal_alert(station, animal_type, animal_conf)
                
                if human_conf > CONFIDENCE_THRESHOLD:
                    create_human_alert(station, human_conf)
                
                last_detection = current_time
            
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
    
    except KeyboardInterrupt:
        print("\n\nStopped by user")
    finally:
        camera.release()
        cv2.destroyAllWindows()
        print("\n" + "="*70)
        print("✓ Camera monitoring stopped")

if __name__ == "__main__":
    main()
