import os
import django
import sys

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'flame_guard_project.settings')
django.setup()

from admin_module.models import FireAlert, ForestStation
from officer_module.models import AnimalAlert, HumanIntrusionAlert, ForestOfficer

# Redirect output to file
with open('alert_diagnosis.txt', 'w') as f:
    sys.stdout = f
    
    print('=' * 70)
    print('DATABASE ALERT STATUS CHECK')
    print('=' * 70)
    
    print('\n=== FIRE ALERTS ===')
    fire_count = FireAlert.objects.count()
    print(f'Total: {fire_count}')
    if fire_count > 0:
        for alert in FireAlert.objects.all()[:10]:
            station_name = alert.station.name if alert.station else "None"
            print(f'  - ID {alert.id}: Station={station_name}, Severity={alert.severity}, Status={alert.status}, Detected={alert.detected_at}')
    else:
        print('  ❌ No fire alerts found in database')
    
    print('\n=== ANIMAL ALERTS ===')
    animal_count = AnimalAlert.objects.count()
    print(f'Total: {animal_count}')
    if animal_count > 0:
        for alert in AnimalAlert.objects.all()[:10]:
            station_name = alert.station.name if alert.station else "None"
            print(f'  - ID {alert.id}: Station={station_name}, Animal={alert.animal_type}, Detected={alert.detected_at}')
    else:
        print('  ❌ No animal alerts found in database')
    
    print('\n=== HUMAN INTRUSION ALERTS ===')
    human_count = HumanIntrusionAlert.objects.count()
    print(f'Total: {human_count}')
    if human_count > 0:
        for alert in HumanIntrusionAlert.objects.all()[:10]:
            station_name = alert.station.name if alert.station else "None"
            print(f'  - ID {alert.id}: Station={station_name}, Detected={alert.detected_at}')
    else:
        print('  ❌ No human intrusion alerts found in database')
    
    print('\n=== FOREST STATIONS ===')
    station_count = ForestStation.objects.count()
    print(f'Total: {station_count}')
    for station in ForestStation.objects.all():
        print(f'  - ID {station.id}: {station.name} ({station.division.name})')
    
    print('\n=== FOREST OFFICERS ===')
    officer_count = ForestOfficer.objects.count()
    print(f'Total: {officer_count}')
    for officer in ForestOfficer.objects.all():
        station_name = officer.station.name if officer.station else "⚠️ NO STATION ASSIGNED!"
        print(f'  - {officer.user.username}: Station={station_name}')
    
    print('\n' + '=' * 70)
    print('DIAGNOSIS:')
    print('=' * 70)
    
    if fire_count == 0 and animal_count == 0 and human_count == 0:
        print('❌ CRITICAL ISSUE: No alerts exist in database!')
        print('   → Camera modules have NOT created any alerts yet')
        print('   → You need to run a camera detection script first')
        print('   → Try running: python camera_complete.py')
    elif officer_count == 0:
        print('❌ ISSUE: No officers exist in database!')
        print('   → Need to create officers via admin panel first')
    else:
        # Check for station mismatches
        officers_without_stations = ForestOfficer.objects.filter(station__isnull=True).count()
        if officers_without_stations > 0:
            print(f'⚠️  WARNING: {officers_without_stations} officer(s) have NO station assigned!')
            print('   → Officers without stations cannot see any alerts')
            print('   → Assign stations to officers in admin panel')
        
        # Check if alerts and officers are on different stations
        if fire_count > 0 or animal_count > 0 or human_count > 0:
            alert_stations = set()
            if fire_count > 0:
                alert_stations.update(FireAlert.objects.values_list('station_id', flat=True))
            if animal_count > 0:
                alert_stations.update(AnimalAlert.objects.values_list('station_id', flat=True))
            if human_count > 0:
                alert_stations.update(HumanIntrusionAlert.objects.values_list('station_id', flat=True))
            
            officer_stations = set(ForestOfficer.objects.filter(station__isnull=False).values_list('station_id', flat=True))
            
            print(f'\nAlert Stations (IDs): {sorted(alert_stations)}')
            print(f'Officer Stations (IDs): {sorted(officer_stations)}')
            
            if not alert_stations.intersection(officer_stations):
                print('\n❌ CRITICAL: Alerts and Officers are on DIFFERENT stations!')
                print('   → No officer will see any alerts!')
                print('   → SOLUTION: Assign officers to the correct stations in admin panel')
            else:
                common_stations = alert_stations.intersection(officer_stations)
                print(f'\n✓ Common Stations (IDs): {sorted(common_stations)}')
                print('   → Alerts and officers share common stations')
                print('   → Officers on these stations SHOULD see alerts')
                print('   → If still not visible, check officer panel views/templates')
    
    print('=' * 70)

# Restore stdout
sys.stdout = sys.__stdout__
print('✓ Diagnosis saved to alert_diagnosis.txt')
