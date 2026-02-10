from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
import re
from django.utils import timezone
from django.db.models import Q
from admin_module.models import (CustomUser, ForestStation, Complaint, 
                                 Notification, Report, FireAlert)
from .models import ForestOfficer, UserAlert, HumanIntrusionAlert

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
    complaints = Complaint.objects.filter(sender=request.user).order_by('-created_at')
    return render(request, 'officer/view_complaints.html', {'complaints': complaints})

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
                alerts = FireAlert.objects.filter(station=station).order_by('-detected_at')
                debug_info['alert_count'] = alerts.count()
                
    except AttributeError as e:
        error_message = f"Profile error: {str(e)}"
        debug_info['error'] = str(e)
    except Exception as e:
        error_message = f"Unexpected error: {str(e)}"
        debug_info['error'] = str(e)
    
    context = {
        'alerts': alerts,
        'error_message': error_message,
        'debug_info': debug_info,
    }
    return render(request, 'officer/fire_alerts.html', context)

# ================================
# 6. USER ALERTS
# ================================
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
                intrusions = HumanIntrusionAlert.objects.filter(station=station).order_by('-detected_at')
                debug_info['alert_count'] = intrusions.count()
                
    except AttributeError as e:
        error_message = f"Profile error: {str(e)}"
        debug_info['error'] = str(e)
    except Exception as e:
        error_message = f"Unexpected error: {str(e)}"
        debug_info['error'] = str(e)
    
    context = {
        'intrusions': intrusions,
        'error_message': error_message,
        'debug_info': debug_info,
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
    ).order_by('-created_at')
    
    # Mark as read
    notifications.filter(is_read=False).update(is_read=True)
    
    return render(request, 'officer/notifications.html', {'notifications': notifications})


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
                alerts = AnimalAlert.objects.filter(station=station).order_by('-detected_at')
                debug_info['alert_count'] = alerts.count()
                
    except AttributeError as e:
        error_message = f"Profile error: {str(e)}"
        debug_info['error'] = str(e)
    except Exception as e:
        error_message = f"Unexpected error: {str(e)}"
        debug_info['error'] = str(e)
    
    context = {
        'alerts': alerts,
        'error_message': error_message,
        'debug_info': debug_info,
    }
    return render(request, 'officer/animal_alerts.html', context)

# ================================
# 10. MY REPORTS
# ================================
@officer_required
def view_my_reports(request):
    """View officer's own submitted reports"""
    reports = Report.objects.filter(officer=request.user).order_by('-submitted_at')
    return render(request, 'officer/my_reports.html', {'reports': reports})

# ================================
# 11. FIRE ALERT STATUS UPDATE
# ================================
@officer_required
def update_fire_alert_status(request, pk):
    """Update fire alert status"""
    alert = get_object_or_404(FireAlert, pk=pk)
    
    if request.method == 'POST':
        status = request.POST.get('status')
        alert.status = status
        
        if status == 'RESOLVED':
            alert.resolved_at = timezone.now()
            try:
                alert.resolved_by = request.user.officer_profile
            except:
                pass
        
        alert.save()
        messages.success(request, 'Fire alert status updated successfully!')
        return redirect('view_fire_alerts_officer')
    
    return render(request, 'officer/update_fire_alert.html', {'alert': alert})

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
