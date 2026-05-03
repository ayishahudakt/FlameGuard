from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import re
import json
from django.utils import timezone
from django.utils.dateparse import parse_date
from django.utils.timezone import make_aware
from datetime import datetime, time
from django.db.models import Q
from admin_module.models import (CustomUser, ForestStation, Complaint,
                                 Notification, Report, FireAlert,
                                 Animal, PreservedAnimal)
from .models import ForestOfficer, UserAlert, HumanIntrusionAlert, UserNotification

# ================================
# HELPER DECORATOR
# ================================
def officer_required(view_func):
    """Decorator to ensure only Officer users can access the view"""
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('officer_login')
        if request.user.user_type != 'OFFICER':
            messages.error(request, 'Access denied. Officer privileges required.')
            return redirect('officer_login')
        return view_func(request, *args, **kwargs)
    return wrapper

# ================================
# 1. OFFICER LOGIN
# ================================
def officer_login(request):
    """Custom officer login page"""
    if request.user.is_authenticated and request.user.user_type == 'OFFICER':
        return redirect('officer_dashboard')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None and user.user_type == 'OFFICER':
            login(request, user)
            messages.success(request, f'Welcome back, {user.username}!')
            return redirect('officer_dashboard')
        else:
            messages.error(request, 'Invalid credentials or not an officer account.')
    
    return render(request, 'officer/login.html')

def officer_logout(request):
    """Logout officer user"""
    logout(request)
    messages.success(request, 'Logged out successfully.')
    return redirect('officer_login')

# ================================
# 2. OFFICER DASHBOARD
# ================================
@officer_required
def officer_dashboard(request):
    """Main officer dashboard"""
    try:
        officer_profile = request.user.officer_profile
        station = officer_profile.station
    except:
        officer_profile = None
        station = None
    
    context = {
        'officer_profile': officer_profile,
        'station': station,
        'pending_complaints': Complaint.objects.filter(sender=request.user, status='PENDING').count(),
        'unread_notifications': Notification.objects.filter(to_officer=request.user, is_read=False).count(),
        'active_fire_alerts': FireAlert.objects.filter(station=station, status='ACTIVE').count() if station else 0,
        'new_intrusions': HumanIntrusionAlert.objects.filter(station=station, status='NEW').count() if station else 0,
        'recent_notifications': Notification.objects.filter(to_officer=request.user)[:5],
        'recent_fire_alerts': FireAlert.objects.filter(station=station)[:5] if station else [],
    }
    return render(request, 'officer/dashboard.html', context)

# ================================
# 3. COMPLAINT MANAGEMENT
# ================================
@officer_required
def send_complaint(request):
    """Send complaint to admin"""
    if request.method == 'POST':
        subject = request.POST.get('subject')
        message = request.POST.get('message')
        
        if not re.match(r'^[A-Za-z\s]+$', subject):
            messages.error(request, 'Subject must contain only letters and spaces.')
            return redirect('send_complaint')
            
        Complaint.objects.create(
            sender=request.user,
            subject=subject,
            message=message
        )
        messages.success(request, 'Complaint sent successfully!')
        return redirect('view_officer_complaints')
    
    return render(request, 'officer/send_complaint.html')

@officer_required
def view_officer_complaints(request):
    """View all complaints and replies"""
    complaints = Complaint.objects.filter(sender=request.user)
    date_filter = request.GET.get('date_filter')
    parsed_date = parse_date(date_filter) if date_filter else None
    if parsed_date:
        start_t = make_aware(datetime.combine(parsed_date, time.min))
        end_t = make_aware(datetime.combine(parsed_date, time.max))
        complaints = complaints.filter(created_at__range=(start_t, end_t))
    complaints = complaints.order_by('-created_at')
    return render(request, 'officer/view_complaints.html', {'complaints': complaints, 'date_filter': date_filter})

# ================================
# 4. REPORT SUBMISSION
# ================================
@officer_required
def submit_report(request):
    """Submit daily/incident report"""
    if request.method == 'POST':
        title = request.POST.get('title')
        content = request.POST.get('content')
        
        try:
            station = request.user.officer_profile.station
        except:
            station = None
        
        Report.objects.create(
            officer=request.user,
            title=title,
            content=content,
            station=station
        )
        messages.success(request, 'Report submitted successfully!')
        return redirect('view_my_reports')
    
    return render(request, 'officer/submit_report.html')


@officer_required
def view_fire_alerts(request):
    """View fire alerts for officer's station"""
    alerts = []
    error_message = None
    debug_info = {}
    
    try:
        # Check if user has officer profile
        if not hasattr(request.user, 'officer_profile'):
            error_message = "Your account does not have an officer profile. Please contact admin."
            debug_info['has_profile'] = False
        else:
            officer_profile = request.user.officer_profile
            station = officer_profile.station
            debug_info['has_profile'] = True
            debug_info['username'] = request.user.username
            
            # Check if officer has station assigned
            if not station:
                error_message = "No station assigned to your profile. Please contact admin to assign a station."
                debug_info['has_station'] = False
            else:
                debug_info['has_station'] = True
                debug_info['station_name'] = station.name
                debug_info['station_id'] = station.id
                
                # Query alerts
                alerts = FireAlert.objects.filter(station=station)
                date_filter = request.GET.get('date_filter')
                parsed_date = parse_date(date_filter) if date_filter else None
                if parsed_date:
                    start_t = make_aware(datetime.combine(parsed_date, time.min))
                    end_t = make_aware(datetime.combine(parsed_date, time.max))
                    alerts = alerts.filter(detected_at__range=(start_t, end_t))
                alerts = alerts.order_by('-detected_at')
                debug_info['alert_count'] = alerts.count()
                
    except AttributeError as e:
        error_message = f"Profile error: {str(e)}"
        debug_info['error'] = str(e)
    except Exception as e:
        error_message = f"Unexpected error: {str(e)}"
        debug_info['error'] = str(e)
    
    date_filter = request.GET.get('date_filter') if 'request' in locals() else None
    
    context = {
        'alerts': alerts,
        'error_message': error_message,
        'debug_info': debug_info,
        'date_filter': date_filter,
    }
    return render(request, 'officer/fire_alerts.html', context)

# ================================
# 6. USER ALERTS
# ================================
@officer_required
def view_sent_alerts(request):
    """View all alerts sent by the logged-in officer to public users"""
    alerts = UserAlert.objects.filter(officer=request.user)
    date_filter = request.GET.get('date_filter')
    parsed_date = parse_date(date_filter) if date_filter else None
    if parsed_date:
        start_t = make_aware(datetime.combine(parsed_date, time.min))
        end_t = make_aware(datetime.combine(parsed_date, time.max))
        alerts = alerts.filter(created_at__range=(start_t, end_t))
    alerts = alerts.order_by('-created_at')
    return render(request, 'officer/sent_alerts.html', {'alerts': alerts, 'date_filter': date_filter})


@officer_required
def delete_sent_alert(request, pk):
    """Delete a user alert sent by the logged-in officer"""
    alert = get_object_or_404(UserAlert, pk=pk, officer=request.user)
    alert.delete()
    messages.success(request, 'Alert deleted successfully!')
    return redirect('view_sent_alerts')

@officer_required
def toggle_sent_alert_status(request, pk):
    """Toggle the active status of a user alert sent by the logged-in officer"""
    alert = get_object_or_404(UserAlert, pk=pk, officer=request.user)
    
    # We only accept POST requests for state-changing actions
    if request.method == 'POST':
        alert.is_active = not alert.is_active
        alert.save()
        status_msg = "activated" if alert.is_active else "deactivated"
        messages.success(request, f'Alert {status_msg} successfully.')
        
    return redirect('view_sent_alerts')


@officer_required
def send_user_alert(request):
    """Send alert to public users"""
    if request.method == 'POST':
        title = request.POST.get('title')
        message = request.POST.get('message')
        alert_type = request.POST.get('alert_type')
        location = request.POST.get('location')
        
        UserAlert.objects.create(
            officer=request.user,
            title=title,
            message=message,
            alert_type=alert_type,
            location=location
        )
        messages.success(request, 'Alert sent to users successfully!')
        return redirect('officer_dashboard')
    
    return render(request, 'officer/send_alert.html')

# ================================
# 7. HUMAN INTRUSION ALERTS
# ================================
@officer_required
def view_human_intrusion(request):
    """View human intrusion alerts"""
    intrusions = []
    error_message = None
    debug_info = {}
    
    try:
        # Check if user has officer profile
        if not hasattr(request.user, 'officer_profile'):
            error_message = "Your account does not have an officer profile. Please contact admin."
            debug_info['has_profile'] = False
        else:
            officer_profile = request.user.officer_profile
            station = officer_profile.station
            debug_info['has_profile'] = True
            debug_info['username'] = request.user.username
            
            # Check if officer has station assigned
            if not station:
                error_message = "No station assigned to your profile. Please contact admin to assign a station."
                debug_info['has_station'] = False
            else:
                debug_info['has_station'] = True
                debug_info['station_name'] = station.name
                debug_info['station_id'] = station.id
                
                # Query alerts
                intrusions = HumanIntrusionAlert.objects.filter(station=station)
                date_filter = request.GET.get('date_filter')
                parsed_date = parse_date(date_filter) if date_filter else None
                if parsed_date:
                    start_t = make_aware(datetime.combine(parsed_date, time.min))
                    end_t = make_aware(datetime.combine(parsed_date, time.max))
                    intrusions = intrusions.filter(detected_at__range=(start_t, end_t))
                intrusions = intrusions.order_by('-detected_at')
                debug_info['alert_count'] = intrusions.count()
                
    except AttributeError as e:
        error_message = f"Profile error: {str(e)}"
        debug_info['error'] = str(e)
    except Exception as e:
        error_message = f"Unexpected error: {str(e)}"
        debug_info['error'] = str(e)
    
    date_filter = request.GET.get('date_filter') if 'request' in locals() else None

    context = {
        'intrusions': intrusions,
        'error_message': error_message,
        'debug_info': debug_info,
        'date_filter': date_filter,
    }
    return render(request, 'officer/human_intrusion.html', context)

@officer_required
def update_intrusion_status(request, pk):
    """Update intrusion alert status"""
    intrusion = get_object_or_404(HumanIntrusionAlert, pk=pk)
    
    if request.method == 'POST':
        status = request.POST.get('status')
        notes = request.POST.get('notes')
        
        intrusion.status = status
        intrusion.notes = notes
        intrusion.officer_notified = True
        
        if status in ['RESOLVED', 'FALSE_ALARM']:
            intrusion.resolved_at = timezone.now()
        
        intrusion.save()
        messages.success(request, 'Intrusion alert updated successfully!')
        return redirect('view_human_intrusion')
    
    return render(request, 'officer/update_intrusion.html', {'intrusion': intrusion})

# ================================
# 8. ADMIN NOTIFICATIONS
# ================================
@officer_required
def view_notifications(request):
    """View notifications from admin"""
    # Only show notifications from actual admin users (not auto-generated by camera modules)
    notifications = Notification.objects.filter(
        to_officer=request.user,
        from_admin__user_type='ADMIN'  # Ensure from_admin is actually an admin
    )
    
    date_filter = request.GET.get('date_filter')
    parsed_date = parse_date(date_filter) if date_filter else None
    if parsed_date:
        start_t = make_aware(datetime.combine(parsed_date, time.min))
        end_t = make_aware(datetime.combine(parsed_date, time.max))
        notifications = notifications.filter(created_at__range=(start_t, end_t))
    notifications = notifications.order_by('-created_at')
    
    # Mark as read
    notifications.filter(is_read=False).update(is_read=True)
    
    return render(request, 'officer/notifications.html', {'notifications': notifications, 'date_filter': date_filter})


# ================================
# 9. ANIMAL DETECTION ALERTS
# ================================
@officer_required
def view_animal_alerts(request):
    """View animal detection alerts for officer's station"""
    from .models import AnimalAlert
    
    alerts = []
    error_message = None
    debug_info = {}
    
    try:
        # Check if user has officer profile
        if not hasattr(request.user, 'officer_profile'):
            error_message = "Your account does not have an officer profile. Please contact admin."
            debug_info['has_profile'] = False
        else:
            officer_profile = request.user.officer_profile
            station = officer_profile.station
            debug_info['has_profile'] = True
            debug_info['username'] = request.user.username
            
            # Check if officer has station assigned
            if not station:
                error_message = "No station assigned to your profile. Please contact admin to assign a station."
                debug_info['has_station'] = False
            else:
                debug_info['has_station'] = True
                debug_info['station_name'] = station.name
                debug_info['station_id'] = station.id
                
                # Query alerts
                alerts = AnimalAlert.objects.filter(station=station)
                date_filter = request.GET.get('date_filter')
                parsed_date = parse_date(date_filter) if date_filter else None
                if parsed_date:
                    start_t = make_aware(datetime.combine(parsed_date, time.min))
                    end_t = make_aware(datetime.combine(parsed_date, time.max))
                    alerts = alerts.filter(detected_at__range=(start_t, end_t))
                alerts = alerts.order_by('-detected_at')
                debug_info['alert_count'] = alerts.count()
                
    except AttributeError as e:
        error_message = f"Profile error: {str(e)}"
        debug_info['error'] = str(e)
    except Exception as e:
        error_message = f"Unexpected error: {str(e)}"
        debug_info['error'] = str(e)
    
    date_filter = request.GET.get('date_filter') if 'request' in locals() else None

    context = {
        'alerts': alerts,
        'error_message': error_message,
        'debug_info': debug_info,
        'date_filter': date_filter,
    }
    return render(request, 'officer/animal_alerts.html', context)

# ================================
# 10. MY REPORTS
# ================================
@officer_required
def view_my_reports(request):
    """View officer's own submitted reports"""
    reports = Report.objects.filter(officer=request.user)
    date_filter = request.GET.get('date_filter')
    parsed_date = parse_date(date_filter) if date_filter else None
    if parsed_date:
        start_t = make_aware(datetime.combine(parsed_date, time.min))
        end_t = make_aware(datetime.combine(parsed_date, time.max))
        reports = reports.filter(submitted_at__range=(start_t, end_t))
    reports = reports.order_by('-submitted_at')
    return render(request, 'officer/my_reports.html', {'reports': reports, 'date_filter': date_filter})

# ================================
# 11. FIRE ALERT STATUS UPDATE
# ================================

def _notify_division_users(fire_alert, notif_type='STATUS_UPDATE'):
    """
    Helper: create UserNotification entries for all users in the same
    division as the given fire alert.
    Returns the count of users notified.
    """
    division = fire_alert.station.division if fire_alert.station else None
    if not division:
        return 0

    users_in_division = CustomUser.objects.filter(
        user_type='USER',
        division=division
    )

    if notif_type == 'FIRE_ALERT':
        title = f'🔥 Fire Alert – {division.name}'
        body = (
            f'A fire alert has been issued for {fire_alert.station.name}.\n'
            f'Severity: {fire_alert.severity} | Status: {fire_alert.status}\n'
            f'Time: {fire_alert.detected_at.strftime("%d %b %Y, %I:%M %p")}'
        )
    else:
        title = f'🔥 Fire Alert Update – {division.name}'
        body = (
            f'Status updated for {fire_alert.station.name}.\n'
            f'Severity: {fire_alert.severity} | New Status: {fire_alert.status}\n'
            f'Time: {timezone.now().strftime("%d %b %Y, %I:%M %p")}'
        )

    notifications = [
        UserNotification(
            fire_alert=fire_alert,
            recipient=user,
            title=title,
            body=body,
            notif_type=notif_type,
        )
        for user in users_in_division
    ]
    UserNotification.objects.bulk_create(notifications)
    return len(notifications)


@officer_required
def update_fire_alert_status(request, pk):
    """Update fire alert status and auto-notify division users."""
    alert = get_object_or_404(FireAlert, pk=pk)

    if request.method == 'POST':
        status = request.POST.get('status')
        alert.status = status

        if status == 'RESOLVED':
            alert.resolved_at = timezone.now()
            try:
                alert.resolved_by = request.user.officer_profile
            except Exception:
                pass

        alert.save()

        # Auto-notify users in the same division
        notified = _notify_division_users(alert, notif_type='STATUS_UPDATE')
        messages.success(
            request,
            f'Fire alert status updated successfully! {notified} user(s) in {alert.station.division.name if alert.station and alert.station.division else "division"} notified.'
        )
        return redirect('view_fire_alerts_officer')

    return render(request, 'officer/update_fire_alert.html', {'alert': alert})


@csrf_exempt
def send_fire_alert_to_users(request, pk):
    """
    AJAX endpoint: manually send a fire alert notification to
    all users in the same division as the alert.

    NOTE: We do NOT use @officer_required here because that decorator
    issues an HTTP redirect to the login page when the session has
    expired, and the browser's fetch() then tries to parse that HTML
    response as JSON — which throws a SyntaxError that lands in the
    .catch() block as "Connection error."  Instead we return a proper
    JSON 401 so the frontend can handle it gracefully.
    """
    # ── Auth check (returns JSON, not an HTML redirect) ──────────────
    if not request.user.is_authenticated:
        return JsonResponse({'success': False, 'error': 'Login required.'}, status=401)
    if request.user.user_type != 'OFFICER':
        return JsonResponse({'success': False, 'error': 'Officer access only.'}, status=403)

    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'POST required.'}, status=405)

    alert = get_object_or_404(FireAlert, pk=pk)

    division = alert.station.division if alert.station else None
    if not division:
        return JsonResponse({'success': False, 'error': 'Alert has no division assigned.'}, status=400)

    division_name = division.name

    # ── Division-based users ──────────────────────────────────────────
    users_in_division = CustomUser.objects.filter(
        user_type='USER',
        division=division
    )

    if not users_in_division.exists():
        return JsonResponse({
            'success': True,
            'notified': 0,
            'division': division_name,
            'message': f'No users registered in {division_name} yet.'
        })

    # ── Prevent duplicate alerts for the same fire alert ─────────────
    already_notified_ids = set(
        UserNotification.objects.filter(
            fire_alert=alert,
            notif_type='FIRE_ALERT'
        ).values_list('recipient_id', flat=True)
    )

    title = f'🔥 Fire Alert – {division_name}'
    body = (
        f'A fire alert has been issued at {alert.station.name}.\n'
        f'Severity: {alert.severity} | Status: {alert.status}\n'
        f'Time: {alert.detected_at.strftime("%d %b %Y, %I:%M %p")}'
    )

    new_notifications = [
        UserNotification(
            fire_alert=alert,
            recipient=user,
            title=title,
            body=body,
            notif_type='FIRE_ALERT',
        )
        for user in users_in_division
        if user.id not in already_notified_ids
    ]

    UserNotification.objects.bulk_create(new_notifications)
    notified = len(new_notifications)
    skipped = len(already_notified_ids)

    msg = f'Alert sent to {notified} user(s) in {division_name}.'
    if skipped:
        msg += f' ({skipped} already notified — no duplicates created.)'

    return JsonResponse({
        'success': True,
        'notified': notified,
        'skipped': skipped,
        'division': division_name,
        'message': msg,
    })


@officer_required
def update_animal_alert_status(request, pk):
    """Update animal alert status"""
    from .models import AnimalAlert
    alert = get_object_or_404(AnimalAlert, pk=pk)

    if request.method == 'POST':
        status = request.POST.get('status')
        alert.status = status

        if status == 'RESOLVED':
            alert.resolved_at = timezone.now()

        alert.save()
        messages.success(request, 'Animal alert status updated successfully!')
        return redirect('view_animal_alerts')

    return render(request, 'officer/update_animal_alert.html', {'alert': alert})


@officer_required
def delete_fire_alert(request, pk):
    """Delete a fire alert (officer only)"""
    alert = get_object_or_404(FireAlert, pk=pk)
    alert.delete()
    messages.success(request, 'Fire alert deleted successfully!')
    return redirect('view_fire_alerts_officer')


@officer_required
def delete_animal_alert(request, pk):
    """Delete an animal detection alert (officer only)"""
    from .models import AnimalAlert
    alert = get_object_or_404(AnimalAlert, pk=pk)
    alert.delete()
    messages.success(request, 'Animal alert deleted successfully!')
    return redirect('view_animal_alerts')


@officer_required
def delete_human_intrusion(request, pk):
    """Delete a human intrusion alert (officer only)"""
    intrusion = get_object_or_404(HumanIntrusionAlert, pk=pk)
    intrusion.delete()
    messages.success(request, 'Human intrusion alert deleted successfully!')
    return redirect('view_human_intrusion')


# ================================
# 12. VIEW USER (MOBILE) COMPLAINTS
# ================================
@officer_required
def view_user_complaints(request):
    """View complaints submitted by mobile app users in the officer's division"""
    complaints = []
    error_message = None

    try:
        officer_profile = request.user.officer_profile
        station = officer_profile.station
        if station and station.division:
            # Show complaints from users in same division
            complaints = Complaint.objects.filter(
                sender__user_type='USER',
                sender__division=station.division
            )
        else:
            error_message = "No station/division assigned to your profile."
            complaints = Complaint.objects.none()
    except Exception:
        # Officer may not have a profile — show nothing
        complaints = Complaint.objects.filter(sender__user_type='USER')

    date_filter = request.GET.get('date_filter')
    parsed_date = parse_date(date_filter) if date_filter else None
    if parsed_date:
        start_t = make_aware(datetime.combine(parsed_date, time.min))
        end_t = make_aware(datetime.combine(parsed_date, time.max))
        complaints = complaints.filter(created_at__range=(start_t, end_t))
    complaints = complaints.order_by('-created_at')

    return render(request, 'officer/user_complaints.html', {
        'complaints': complaints,
        'error_message': error_message,
        'date_filter': date_filter,
    })


@officer_required
def reply_user_complaint(request, pk):
    """Reply to a mobile user complaint"""
    complaint = get_object_or_404(Complaint, pk=pk, sender__user_type='USER')

    if request.method == 'POST':
        reply_text = request.POST.get('reply', '').strip()
        new_status = request.POST.get('status', 'IN_PROGRESS')

        if reply_text:
            from django.utils import timezone
            complaint.reply = reply_text
            complaint.status = new_status
            complaint.replied_at = timezone.now()
            complaint.save()
            messages.success(request, 'Reply sent successfully!')
        else:
            messages.error(request, 'Reply cannot be empty.')
        return redirect('view_user_complaints')

    return render(request, 'officer/reply_user_complaint.html', {'complaint': complaint})


# ================================
# 13. ANIMAL MANAGEMENT (Officer)
# ================================
@officer_required
def officer_manage_animals(request):
    """View all animals in the registry"""
    animals = Animal.objects.all()
    return render(request, 'officer/animals.html', {'animals': animals})


@officer_required
def officer_add_animal(request):
    """Add new animal"""
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        scientific_name = request.POST.get('scientific_name', '').strip()
        description = request.POST.get('description', '').strip()
        is_dangerous = request.POST.get('is_dangerous') == 'on'
        image = request.FILES.get('image')

        # Validations
        if not name or not scientific_name:
            messages.error(request, 'Both animal name and scientific name are required.')
            return render(request, 'officer/add_animal.html')

        if Animal.objects.filter(name__iexact=name).exists():
            messages.error(request, f'An animal with the name "{name}" already exists.')
            return render(request, 'officer/add_animal.html')

        if Animal.objects.filter(scientific_name__iexact=scientific_name).exists():
            messages.error(request, f'An animal with the scientific name "{scientific_name}" already exists.')
            return render(request, 'officer/add_animal.html')

        animal = Animal.objects.create(
            name=name,
            scientific_name=scientific_name,
            description=description,
            is_dangerous=is_dangerous,
        )
        if image:
            animal.image = image
            animal.save()
        messages.success(request, 'Animal added successfully!')
        return redirect('officer_manage_animals')

    return render(request, 'officer/add_animal.html')


@officer_required
def officer_edit_animal(request, pk):
    """Edit an existing animal"""
    animal = get_object_or_404(Animal, pk=pk)

    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        scientific_name = request.POST.get('scientific_name', '').strip()
        
        # Validations
        if not name or not scientific_name:
            messages.error(request, 'Both animal name and scientific name are required.')
            return render(request, 'officer/edit_animal.html', {'animal': animal})

        if Animal.objects.filter(name__iexact=name).exclude(pk=pk).exists():
            messages.error(request, f'An animal with the name "{name}" already exists.')
            return render(request, 'officer/edit_animal.html', {'animal': animal})

        if Animal.objects.filter(scientific_name__iexact=scientific_name).exclude(pk=pk).exists():
            messages.error(request, f'An animal with the scientific name "{scientific_name}" already exists.')
            return render(request, 'officer/edit_animal.html', {'animal': animal})

        animal.name = name
        animal.scientific_name = scientific_name
        animal.description = request.POST.get('description', '').strip()
        animal.is_dangerous = request.POST.get('is_dangerous') == 'on'
        if request.FILES.get('image'):
            animal.image = request.FILES['image']
        animal.save()
        messages.success(request, 'Animal updated successfully!')
        return redirect('officer_manage_animals')

    return render(request, 'officer/edit_animal.html', {'animal': animal})


@officer_required
def officer_delete_animal(request, pk):
    """Delete an animal"""
    animal = get_object_or_404(Animal, pk=pk)
    animal.delete()
    messages.success(request, 'Animal deleted successfully!')
    return redirect('officer_manage_animals')


# ================================
# 14. PRESERVED ANIMAL MANAGEMENT (Officer)
# ================================
@officer_required
def officer_manage_preserved_animals(request):
    """View all preserved animals"""
    preserved = PreservedAnimal.objects.select_related('animal').all()
    return render(request, 'officer/preserved_animals.html', {'preserved_animals': preserved})


@officer_required
def officer_add_preserved_animal(request):
    """Add an animal to the preserved list"""
    if request.method == 'POST':
        animal_id = request.POST.get('animal')
        preservation_status = request.POST.get('preservation_status')
        threat_level = request.POST.get('threat_level')
        population_estimate = request.POST.get('population_estimate') or None
        conservation_notes = request.POST.get('conservation_notes', '')

        PreservedAnimal.objects.create(
            animal_id=animal_id,
            preservation_status=preservation_status,
            threat_level=threat_level,
            population_estimate=population_estimate,
            conservation_notes=conservation_notes,
        )
        messages.success(request, 'Preserved animal added successfully!')
        return redirect('officer_manage_preserved_animals')

    animals = Animal.objects.all()
    return render(request, 'officer/add_preserved_animal.html', {'animals': animals})


@officer_required
def officer_edit_preserved_animal(request, pk):
    """Edit a preserved animal entry"""
    preserved = get_object_or_404(PreservedAnimal, pk=pk)

    if request.method == 'POST':
        preserved.animal_id = request.POST.get('animal')
        preserved.preservation_status = request.POST.get('preservation_status')
        preserved.threat_level = request.POST.get('threat_level')
        preserved.population_estimate = request.POST.get('population_estimate') or None
        preserved.conservation_notes = request.POST.get('conservation_notes', '')
        preserved.save()
        messages.success(request, 'Preserved animal updated successfully!')
        return redirect('officer_manage_preserved_animals')

    animals = Animal.objects.all()
    return render(request, 'officer/edit_preserved_animal.html', {'preserved': preserved, 'animals': animals})


@officer_required
def officer_delete_preserved_animal(request, pk):
    """Delete a preserved animal entry"""
    preserved = get_object_or_404(PreservedAnimal, pk=pk)
    preserved.delete()
    messages.success(request, 'Preserved animal removed successfully!')
    return redirect('officer_manage_preserved_animals')
