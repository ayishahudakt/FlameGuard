import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib.auth import authenticate
from django.db.models import Q
from rest_framework.authtoken.models import Token

from admin_module.models import (
    CustomUser, FireAlert, Animal, Complaint,
    Notification, ForestStation, ForestDivision
)
from officer_module.models import AnimalAlert


# ============================================================
# HELPER: Get authenticated user from token
# ============================================================
def get_user_from_token(request):
    auth = request.headers.get('Authorization', '')
    if not auth.startswith('Token '):
        return None
    token_key = auth.split(' ')[1]
    try:
        token = Token.objects.get(key=token_key)
        return token.user
    except Token.DoesNotExist:
        return None


# ============================================================
# 1. LOGIN
# POST /api/user/login/
# ============================================================
@csrf_exempt
@require_http_methods(["POST"])
def user_login(request):
    try:
        data = json.loads(request.body)
        username = data.get('username', '').strip()
        password = data.get('password', '').strip()

        if not username or not password:
            return JsonResponse({'error': 'Username and password are required.'}, status=400)

        user = authenticate(username=username, password=password)
        if user is None:
            return JsonResponse({'error': 'Invalid username or password.'}, status=401)

        # Create or get a token for this user
        token, _ = Token.objects.get_or_create(user=user)

        return JsonResponse({
            'token': token.key,
            'username': user.username,
            'email': user.email,
            'user_type': user.user_type,
        }, status=200)

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


# ============================================================
# 2. REGISTER
# POST /api/user/register/
# ============================================================
@csrf_exempt
@require_http_methods(["POST"])
def user_register(request):
    try:
        data = json.loads(request.body)
        username = data.get('username', '').strip()
        email = data.get('email', '').strip()
        password = data.get('password', '')
        phone = data.get('phone', '').strip()
        division_id = data.get('division_id')

        if not username or not email or not password:
            return JsonResponse({'error': 'Username, email and password are required.'}, status=400)

        if not division_id:
            return JsonResponse({'error': 'Please select a division.'}, status=400)

        # Validate division exists
        try:
            division = ForestDivision.objects.get(id=int(division_id))
        except (ForestDivision.DoesNotExist, ValueError, TypeError):
            return JsonResponse({'error': 'Invalid division selected.'}, status=400)

        if CustomUser.objects.filter(username=username).exists():
            return JsonResponse({'error': 'Username already exists. Please choose another.'}, status=400)

        if CustomUser.objects.filter(email=email).exists():
            return JsonResponse({'error': 'Email already registered. Please login.'}, status=400)

        user = CustomUser.objects.create_user(
            username=username,
            email=email,
            password=password,
            phone_number=phone,
            user_type='USER',
            division=division,
        )

        return JsonResponse({'message': 'Account created successfully!'}, status=201)

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


# ============================================================
# 3. FIRE ALERTS (Read-only)
# GET /api/fire-alerts/
# ============================================================
@csrf_exempt
@require_http_methods(["GET"])
def fire_alerts(request):
    user = get_user_from_token(request)
    if not user:
        return JsonResponse({'error': 'Authentication required.'}, status=401)

    alerts = FireAlert.objects.select_related('station', 'station__division').all()

    data = []
    for alert in alerts:
        data.append({
            'id': alert.id,
            'location': alert.station.name if alert.station else 'Unknown',
            'division': alert.station.division.name if alert.station and alert.station.division else 'Unknown',
            'severity': alert.severity,
            'status': alert.status,
            'detected_at': alert.detected_at.strftime('%d %b %Y, %I:%M %p') if alert.detected_at else '',
            'description': alert.location_details or '',
            'image': request.build_absolute_uri(alert.image.url) if alert.image else None,
        })

    return JsonResponse(data, safe=False, status=200)


# ============================================================
# 4. ANIMAL ALERTS (Read-only)
# GET /api/animal-alerts/
# ============================================================
@csrf_exempt
@require_http_methods(["GET"])
def animal_alerts(request):
    user = get_user_from_token(request)
    if not user:
        return JsonResponse({'error': 'Authentication required.'}, status=401)

    alerts = AnimalAlert.objects.select_related('officer').all()

    data = []
    for alert in alerts:
        data.append({
            'id': alert.id,
            'animal_type': alert.animal_type if hasattr(alert, 'animal_type') else 'Unknown',
            'location': alert.location if hasattr(alert, 'location') else '',
            'status': alert.status if hasattr(alert, 'status') else 'ACTIVE',
            'detected_at': alert.detected_at.strftime('%d %b %Y, %I:%M %p') if hasattr(alert, 'detected_at') and alert.detected_at else '',
            'confidence': alert.confidence if hasattr(alert, 'confidence') else None,
            'division': alert.officer.forest_station.division.name if hasattr(alert, 'officer') and alert.officer and hasattr(alert.officer, 'forest_station') and alert.officer.forest_station else '',
            'image': request.build_absolute_uri(alert.image.url) if hasattr(alert, 'image') and alert.image else None,
        })

    return JsonResponse(data, safe=False, status=200)


# ============================================================
# 5. NOTIFICATIONS (User-specific, division-based)
# GET /api/notifications/
# ============================================================
@csrf_exempt
@require_http_methods(["GET"])
def notifications(request):
    user = get_user_from_token(request)
    if not user:
        return JsonResponse({'error': 'Authentication required.'}, status=401)

    from officer_module.models import UserNotification
    notifs = UserNotification.objects.filter(recipient=user).order_by('-created_at')[:50]

    data = []
    for n in notifs:
        data.append({
            'id': n.id,
            'title': n.title,
            'body': n.body,
            'type': 'fire',
            'notif_type': n.notif_type,
            'is_read': n.is_read,
            'created_at': n.created_at.strftime('%d %b %Y, %I:%M %p'),
        })

    # Mark all as read after fetching
    notifs.filter(is_read=False).update(is_read=True)

    return JsonResponse(data, safe=False, status=200)


# ============================================================
# 6. COMPLAINTS
# GET  /api/complaints/  → list my complaints
# POST /api/complaints/  → send a complaint
# ============================================================
@csrf_exempt
@require_http_methods(["GET", "POST"])
def complaints(request):
    user = get_user_from_token(request)
    if not user:
        return JsonResponse({'error': 'Authentication required.'}, status=401)

    if request.method == 'GET':
        my_complaints = Complaint.objects.filter(sender=user)
        data = []
        for c in my_complaints:
            data.append({
                'id': c.id,
                'subject': c.subject,
                'message': c.message,
                'status': c.status,
                'reply': c.reply or '',
                'created_at': c.created_at.strftime('%d %b %Y, %I:%M %p') if c.created_at else '',
            })
        return JsonResponse(data, safe=False, status=200)

    elif request.method == 'POST':
        try:
            data = json.loads(request.body)
            subject = data.get('subject', '').strip()
            message = data.get('message', '').strip()

            if not subject or not message:
                return JsonResponse({'error': 'Subject and message are required.'}, status=400)

            # Validate subject (only letters and spaces, as per model validator)
            import re
            if not re.match(r'^[A-Za-z\s]+$', subject):
                return JsonResponse({'error': 'Subject must contain only letters and spaces.'}, status=400)

            complaint = Complaint.objects.create(
                sender=user,
                subject=subject,
                message=message,
                status='PENDING',
            )
            return JsonResponse({'message': 'Complaint submitted successfully!', 'id': complaint.id}, status=201)

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)


# ============================================================
# 7. ANIMALS (Division-wise)
# GET /api/animals/  or  /api/animals/?division=Division+1
# ============================================================
@csrf_exempt
@require_http_methods(["GET"])
def animals(request):
    user = get_user_from_token(request)
    if not user:
        return JsonResponse({'error': 'Authentication required.'}, status=401)

    queryset = Animal.objects.all()

    data = []
    for animal in queryset:
        data.append({
            'id': animal.id,
            'name': animal.name,
            'scientific_name': animal.scientific_name or '',
            'description': animal.description or '',
            'is_dangerous': animal.is_dangerous,
            'image': request.build_absolute_uri(animal.image.url) if animal.image else None,
        })

    return JsonResponse(data, safe=False, status=200)


# ============================================================
# 8. CONTACTS (Forest Stations)
# GET /api/contacts/
# ============================================================
@csrf_exempt
@require_http_methods(["GET"])
def contacts(request):
    user = get_user_from_token(request)
    if not user:
        return JsonResponse({'error': 'Authentication required.'}, status=401)

    stations = ForestStation.objects.select_related('division').all()

    data = []
    for station in stations:
        data.append({
            'id': station.id,
            'name': station.name,
            'division': station.division.name if station.division else '',
            'phone': station.contact_number,
            'address': station.address or '',
            'type': 'station',
        })

    return JsonResponse(data, safe=False, status=200)


# ============================================================
# 9. DIVISIONS (Public – no auth, used during registration)
# GET /api/divisions/
# ============================================================
@csrf_exempt
@require_http_methods(["GET"])
def divisions(request):
    all_divisions = ForestDivision.objects.all().order_by('name')
    data = [
        {'id': d.id, 'name': d.name}
        for d in all_divisions
    ]
    return JsonResponse(data, safe=False, status=200)
