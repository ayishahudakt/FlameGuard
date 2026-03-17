"""
Django API Views for AI Detection
"""
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from admin_module.models import ForestStation, FireAlert
from officer_module.models import HumanIntrusionAlert, AnimalAlert
import sys
import os

# Add camera_module to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from ml import predict
except ImportError:
    predict = None

@csrf_exempt
@require_http_methods(["POST"])
def detect_fire_api(request):
    """
    API endpoint to detect fire in uploaded image
    
    POST /api/camera/detect-fire/
    Body: multipart/form-data with 'image' file
    Optional: 'station_id' to link alert to station
    """
    if predict is None:
        return JsonResponse({
            'success': False,
            'error': 'AI models not loaded. Please train models first.'
        }, status=500)
    
    try:
        # Get uploaded image
        if 'image' not in request.FILES:
            return JsonResponse({
                'success': False,
                'error': 'No image file provided'
            }, status=400)
        
        image_file = request.FILES['image']
        station_id = request.POST.get('station_id')
        
        # Run prediction
        result = predict.predict_fire(image_file)
        
        # If fire detected and station provided, create alert
        if result.get('detected') and station_id:
            try:
                station = ForestStation.objects.get(pk=station_id)
                
                # Determine severity based on confidence
                confidence = result.get('confidence', 0)
                if confidence > 90:
                    severity = 'CRITICAL'
                elif confidence > 75:
                    severity = 'HIGH'
                elif confidence > 60:
                    severity = 'MEDIUM'
                else:
                    severity = 'LOW'
                
                # Create fire alert
                alert = FireAlert.objects.create(
                    station=station,
                    severity=severity,
                    location_details=f"AI Detection (Confidence: {confidence}%)",
                    image=image_file
                )
                
                result['alert_created'] = True
                result['alert_id'] = alert.pk
                
            except ForestStation.DoesNotExist:
                result['alert_created'] = False
                result['error'] = 'Invalid station_id'
        
        return JsonResponse({
            'success': True,
            'detection': result
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def detect_animal_api(request):
    """
    API endpoint to detect animals in uploaded image
    
    POST /api/camera/detect-animal/
    Body: multipart/form-data with 'image' file
    """
    if predict is None:
        return JsonResponse({
            'success': False,
            'error': 'AI models not loaded. Please train models first.'
        }, status=500)
    
    try:
        # Get uploaded image
        if 'image' not in request.FILES:
            return JsonResponse({
                'success': False,
                'error': 'No image file provided'
            }, status=400)
        
        image_file = request.FILES['image']
        station_id = request.POST.get('station_id')
        
        # Run prediction
        result = predict.predict_animal(image_file)
        
        # If animal detected and station provided, create animal alert
        if result.get('animal') and result.get('animal') != 'none' and station_id:
            try:
                station = ForestStation.objects.get(pk=station_id)
                confidence = result.get('confidence', 0)
                
                # Determine severity based on confidence
                if confidence > 90:
                    severity = 'CRITICAL'
                elif confidence > 75:
                    severity = 'HIGH'
                elif confidence > 60:
                    severity = 'MEDIUM'
                else:
                    severity = 'LOW'
                
                # Create animal alert
                alert = AnimalAlert.objects.create(
                    station=station,
                    animal_type=result.get('animal'),
                    confidence_score=confidence / 100.0,
                    severity=severity,
                    location_details=f"AI Detection (Confidence: {confidence}%)",
                    image=image_file
                )
                
                result['alert_created'] = True
                result['alert_id'] = alert.pk
                
            except ForestStation.DoesNotExist:
                result['alert_created'] = False
                result['error'] = 'Invalid station_id'
        
        return JsonResponse({
            'success': True,
            'detection': result
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def detect_human_api(request):
    """
    API endpoint to detect humans in uploaded image
    
    POST /api/camera/detect-human/
    Body: multipart/form-data with 'image' file
    Optional: 'station_id' to link alert to station
    """
    if predict is None:
        return JsonResponse({
            'success': False,
            'error': 'AI models not loaded. Please train models first.'
        }, status=500)
    
    try:
        # Get uploaded image
        if 'image' not in request.FILES:
            return JsonResponse({
                'success': False,
                'error': 'No image file provided'
            }, status=400)
        
        image_file = request.FILES['image']
        station_id = request.POST.get('station_id')
        
        # Run prediction
        result = predict.predict_human(image_file)
        
        # If human detected and station provided, create intrusion alert
        if result.get('detected') and station_id:
            try:
                station = ForestStation.objects.get(pk=station_id)
                
                # Create intrusion alert
                alert = HumanIntrusionAlert.objects.create(
                    station=station,
                    location_details=f"AI Detection (Confidence: {result.get('confidence', 0)}%)",
                    image=image_file
                )
                
                result['alert_created'] = True
                result['alert_id'] = alert.pk
                
            except ForestStation.DoesNotExist:
                result['alert_created'] = False
                result['error'] = 'Invalid station_id'
        
        return JsonResponse({
            'success': True,
            'detection': result
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)
