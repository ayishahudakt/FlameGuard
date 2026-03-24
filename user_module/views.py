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
        login_input = data.get('username', '').strip()
        password = data.get('password', '').strip()

        if not login_input or not password:
            return JsonResponse({'error': 'Username/email and password are required.'}, status=400)

        # If input looks like an email, find the actual username first
        if '@' in login_input:
            try:
                matched_user = CustomUser.objects.get(email__iexact=login_input)
                login_input = matched_user.username
            except CustomUser.DoesNotExist:
                return JsonResponse({'error': 'Invalid username or password.'}, status=401)

        user = authenticate(username=login_input, password=password)
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

        if phone and CustomUser.objects.filter(phone_number=phone).exists():
            return JsonResponse({'error': 'This phone number is already registered.'}, status=400)

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

    # Only show fire alerts that the officer has explicitly "Sent Alert" for.
    # We know an alert is sent if there's a UserNotification of type 'FIRE_ALERT'
    from officer_module.models import UserNotification

    if hasattr(user, 'division') and user.division:
        # Get IDs of all fire alerts this user was notified about
        notified_alert_ids = UserNotification.objects.filter(
            recipient=user, 
            notif_type='FIRE_ALERT'
        ).values_list('fire_alert_id', flat=True)
        
        alerts = FireAlert.objects.select_related('station', 'station__division').filter(
            id__in=notified_alert_ids,
            station__division=user.division
        )
    else:
        alerts = FireAlert.objects.none()

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

    if hasattr(user, 'division') and user.division:
        alerts = AnimalAlert.objects.select_related('station', 'station__division').filter(station__division=user.division)
    else:
        alerts = AnimalAlert.objects.select_related('station', 'station__division').all()

    data = []
    for alert in alerts:
        data.append({
            'id': alert.id,
            'animal_type': alert.animal_type if hasattr(alert, 'animal_type') else 'Unknown',
            'location': alert.location_details if hasattr(alert, 'location_details') else '',
            'status': alert.status if hasattr(alert, 'status') else 'ACTIVE',
            'detected_at': alert.detected_at.strftime('%d %b %Y, %I:%M %p') if hasattr(alert, 'detected_at') and alert.detected_at else '',
            'confidence': alert.confidence_score if hasattr(alert, 'confidence_score') else None,
            'division': alert.station.division.name if alert.station and alert.station.division else '',
            'image': request.build_absolute_uri(alert.image.url) if hasattr(alert, 'image') and alert.image else None,
        })

    return JsonResponse(data, safe=False, status=200)


# ============================================================
# 5. NOTIFICATIONS (User-specific)
# GET /api/notifications/
# Only shows manual alerts pushed by officers via Send User Alert page.
# ============================================================
@csrf_exempt
@require_http_methods(["GET"])
def notifications(request):
    user = get_user_from_token(request)
    if not user:
        return JsonResponse({'error': 'Authentication required.'}, status=401)

    from officer_module.models import UserAlert

    data = []

    # Only show manual alerts sent by officers in the same division
    if hasattr(user, 'division') and user.division:
        user_alerts = UserAlert.objects.filter(
            officer__officer_profile__station__division=user.division,
            is_active=True
        ).order_by('-created_at')[:50]

        for ua in user_alerts:
            body = f"{ua.message}\nLocation: {ua.location}" if ua.location else ua.message
            data.append({
                'id': f"alert_{ua.id}",
                'title': ua.title,
                'body': body,
                'type': 'alert',
                'notif_type': ua.alert_type,
                'is_read': True,
                'created_at': ua.created_at.strftime('%d %b %Y, %I:%M %p'),
            })

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


@csrf_exempt
@require_http_methods(["DELETE"])
def delete_complaint(request, pk):
    """Delete a specific complaint by the owner"""
    user = get_user_from_token(request)
    if not user:
        return JsonResponse({'error': 'Authentication required.'}, status=401)
    
    try:
        complaint = Complaint.objects.get(pk=pk, sender=user)
        complaint.delete()
        return JsonResponse({'message': 'Complaint deleted successfully!'}, status=200)
    except Complaint.DoesNotExist:
        return JsonResponse({'error': 'Complaint not found or you are not the owner.'}, status=404)
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


# ============================================================
# 10. USER PROFILE
# GET, POST /api/user/profile/
# ============================================================
@csrf_exempt
@require_http_methods(["GET", "POST"])
def user_profile(request):
    user = get_user_from_token(request)
    if not user:
        return JsonResponse({'error': 'Authentication required.'}, status=401)

    if request.method == "GET":
        data = {
            'username': user.username,
            'email': user.email,
            'phone': user.phone_number or '',
            'division': user.division.name if hasattr(user, 'division') and user.division else 'N/A',
            'user_type': user.user_type,
            'date_joined': user.date_joined.strftime('%d %b %Y') if user.date_joined else '',
            'profile_picture': request.build_absolute_uri(user.profile_picture.url) if user.profile_picture else None,
        }
        return JsonResponse(data, status=200)
    
    elif request.method == "POST":
        try:
            # Check if this is a multipart request (Django handles POST and FILES natively)
            if request.content_type.startswith('multipart/form-data'):
                phone = request.POST.get('phone', '').strip()
                profile_pic = request.FILES.get('profile_picture')
            else:
                # Fallback to JSON payload if available
                data = json.loads(request.body)
                phone = data.get('phone', '').strip()
                profile_pic = None

            if phone:
                if CustomUser.objects.filter(phone_number=phone).exclude(id=user.id).exists():
                    return JsonResponse({'error': 'This phone number is already registered.'}, status=400)
                user.phone_number = phone
                
            if profile_pic:
                user.profile_picture = profile_pic
                
            user.save()
            return JsonResponse({
                'message': 'Profile updated successfully!', 
                'phone': user.phone_number,
                'profile_picture': request.build_absolute_uri(user.profile_picture.url) if user.profile_picture else None
            }, status=200)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
