from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.utils.dateparse import parse_date
from django.utils.timezone import make_aware
from datetime import datetime, time
from django.db.models import Count, Q
from .models import (CustomUser, ForestDivision, ForestStation, Animal, 
                     PreservedAnimal, Complaint, Notification, Report, FireAlert)
from .forms import ForestDivisionForm, ForestStationForm, AnimalForm, PreservedAnimalForm, ForestOfficerForm, ForestOfficerEditForm
from officer_module.models import ForestOfficer

# ================================
# HELPER DECORATOR
# ================================
def admin_required(view_func):
    """Decorator to ensure only Admin users can access the view"""
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('admin_login')
        if request.user.user_type != 'ADMIN':
            messages.error(request, 'Access denied. Admin privileges required.')
            return redirect('admin_login')
        return view_func(request, *args, **kwargs)
    return wrapper

# ================================
# 1. ADMIN LOGIN
# ================================
def admin_login(request):
    """Custom admin login page"""
    if request.user.is_authenticated and request.user.user_type == 'ADMIN':
        return redirect('admin_dashboard')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None and user.user_type == 'ADMIN':
            login(request, user)
            messages.success(request, f'Welcome back, {user.username}!')
            return redirect('admin_dashboard')
        else:
            messages.error(request, 'Invalid credentials or not an admin user.')
    
    return render(request, 'admin_panel/login.html')

def admin_logout(request):
    """Logout admin user"""
    logout(request)
    messages.success(request, 'Logged out successfully.')
    return redirect('admin_login')

# ================================
# 2. ADMIN DASHBOARD
# ================================
@admin_required
def admin_dashboard(request):
    """Main admin dashboard with statistics"""
    context = {
        'total_divisions': ForestDivision.objects.count(),
        'total_stations': ForestStation.objects.count(),
        'total_animals': Animal.objects.count(),
        'total_preserved': PreservedAnimal.objects.count(),
        'total_officers': ForestOfficer.objects.count(),
        'pending_complaints': Complaint.objects.filter(status='PENDING').count(),
        'active_fire_alerts': FireAlert.objects.filter(status='ACTIVE').count(),
        'recent_reports': Report.objects.all()[:5],
        'recent_alerts': FireAlert.objects.all()[:5],
    }
    return render(request, 'admin_panel/dashboard.html', context)

# ================================
# 3. FOREST DIVISION MANAGEMENT
# ================================
@admin_required
def manage_divisions(request):
    """List all forest divisions"""
    divisions = ForestDivision.objects.all()
    return render(request, 'admin_panel/divisions.html', {'divisions': divisions})

@admin_required
def add_division(request):
    """Add new forest division"""
    if request.method == 'POST':
        form = ForestDivisionForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name'].strip()
            # Case-insensitive uniqueness check
            if ForestDivision.objects.filter(name__iexact=name).exists():
                messages.error(request, f'A division named "{name}" already exists. Division names must be unique.')
            else:
                form.save()
                messages.success(request, 'Forest Division added successfully!')
                return redirect('manage_divisions')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = ForestDivisionForm()

    return render(request, 'admin_panel/add_division.html', {'form': form})

@admin_required
def edit_division(request, pk):
    """Edit forest division"""
    division = get_object_or_404(ForestDivision, pk=pk)

    if request.method == 'POST':
        form = ForestDivisionForm(request.POST, instance=division)
        if form.is_valid():
            name = form.cleaned_data['name'].strip()
            # Case-insensitive uniqueness check — exclude the current record
            if ForestDivision.objects.filter(name__iexact=name).exclude(pk=pk).exists():
                messages.error(request, f'A division named "{name}" already exists. Division names must be unique.')
            else:
                form.save()
                messages.success(request, 'Division updated successfully!')
                return redirect('manage_divisions')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = ForestDivisionForm(instance=division)

    return render(request, 'admin_panel/edit_division.html', {'form': form, 'division': division})

@admin_required
def delete_division(request, pk):
    """Delete forest division"""
    division = get_object_or_404(ForestDivision, pk=pk)
    division.delete()
    messages.success(request, 'Division deleted successfully!')
    return redirect('manage_divisions')

# ================================
# 4. FOREST STATION MANAGEMENT
# ================================
@admin_required
def manage_stations(request):
    """List all forest stations"""
    stations = ForestStation.objects.select_related('division').all()
    return render(request, 'admin_panel/stations.html', {'stations': stations})

@admin_required
def add_station(request):
    """Add new forest station"""
    if request.method == 'POST':
        form = ForestStationForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name'].strip()
            contact_number = form.cleaned_data['contact_number'].strip()

            # Case-insensitive duplicate name check
            if ForestStation.objects.filter(name__iexact=name).exists():
                messages.error(request, f'A station named "{name}" already exists. Station names must be unique.')
            # Duplicate contact number check
            elif ForestStation.objects.filter(contact_number=contact_number).exists():
                messages.error(request, f'The contact number "{contact_number}" is already used by another station.')
            else:
                form.save()
                messages.success(request, 'Forest Station added successfully!')
                return redirect('manage_stations')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = ForestStationForm()

    return render(request, 'admin_panel/add_station.html', {'form': form})

@admin_required
def edit_station(request, pk):
    """Edit forest station"""
    station = get_object_or_404(ForestStation, pk=pk)

    if request.method == 'POST':
        form = ForestStationForm(request.POST, instance=station)
        if form.is_valid():
            name = form.cleaned_data['name'].strip()
            contact_number = form.cleaned_data['contact_number'].strip()

            # Case-insensitive duplicate name check (exclude current station)
            if ForestStation.objects.filter(name__iexact=name).exclude(pk=pk).exists():
                messages.error(request, f'A station named "{name}" already exists. Station names must be unique.')
            # Duplicate contact number check (exclude current station)
            elif ForestStation.objects.filter(contact_number=contact_number).exclude(pk=pk).exists():
                messages.error(request, f'The contact number "{contact_number}" is already used by another station.')
            else:
                form.save()
                messages.success(request, 'Station updated successfully!')
                return redirect('manage_stations')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = ForestStationForm(instance=station)

    return render(request, 'admin_panel/edit_station.html', {'form': form, 'station': station})

@admin_required
def delete_station(request, pk):
    """Delete forest station"""
    station = get_object_or_404(ForestStation, pk=pk)
    station.delete()
    messages.success(request, 'Station deleted successfully!')
    return redirect('manage_stations')

# ================================
# 5. ANIMAL MANAGEMENT
# ================================
@admin_required
def manage_animals(request):
    """List all animals"""
    animals = Animal.objects.all()
    return render(request, 'admin_panel/animals.html', {'animals': animals})

@admin_required
def add_animal(request):
    """Add new animal"""
    if request.method == 'POST':
        form = AnimalForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Animal added successfully!')
            return redirect('manage_animals')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = AnimalForm()
    
    return render(request, 'admin_panel/add_animal.html', {'form': form})

@admin_required
def edit_animal(request, pk):
    """Edit animal"""
    animal = get_object_or_404(Animal, pk=pk)
    
    if request.method == 'POST':
        form = AnimalForm(request.POST, request.FILES, instance=animal)
        if form.is_valid():
            form.save()
            messages.success(request, 'Animal updated successfully!')
            return redirect('manage_animals')
        else:
             messages.error(request, 'Please correct the errors below.')
    else:
        form = AnimalForm(instance=animal)
    
    return render(request, 'admin_panel/edit_animal.html', {'form': form, 'animal': animal})

@admin_required
def delete_animal(request, pk):
    """Delete animal"""
    animal = get_object_or_404(Animal, pk=pk)
    animal.delete()
    messages.success(request, 'Animal deleted successfully!')
    return redirect('manage_animals')

# ================================
# 6. PRESERVED ANIMAL MANAGEMENT
# ================================
@admin_required
def manage_preserved_animals(request):
    """List all preserved animals"""
    preserved = PreservedAnimal.objects.select_related('animal').all()
    return render(request, 'admin_panel/preserved_animals.html', {'preserved_animals': preserved})

@admin_required
def add_preserved_animal(request):
    """Add animal to preserved list"""
    if request.method == 'POST':
        form = PreservedAnimalForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Preserved animal added successfully!')
            return redirect('manage_preserved_animals')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = PreservedAnimalForm()
    
    animals = Animal.objects.all()
    return render(request, 'admin_panel/add_preserved_animal.html', {'form': form, 'animals': animals})

# NOTE: manage_officers, add_officer, and allocate_officer are defined later in this file with full validation.

# ================================
# 8. COMPLAINT MANAGEMENT
# ================================
@admin_required
def view_complaints(request):
    """View all complaints"""
    complaints = Complaint.objects.select_related('sender').all()
    date_filter = request.GET.get('date_filter')
    parsed_date = parse_date(date_filter) if date_filter else None
    if parsed_date:
        start_t = make_aware(datetime.combine(parsed_date, time.min))
        end_t = make_aware(datetime.combine(parsed_date, time.max))
        complaints = complaints.filter(created_at__range=(start_t, end_t))
    complaints = complaints.order_by('-created_at')
    return render(request, 'admin_panel/complaints.html', {'complaints': complaints, 'date_filter': date_filter})

@admin_required
def reply_complaint(request, pk):
    """Reply to a complaint"""
    complaint = get_object_or_404(Complaint, pk=pk)
    
    if request.method == 'POST':
        reply = request.POST.get('reply')
        complaint.reply = reply
        complaint.status = 'RESOLVED'
        complaint.replied_at = timezone.now()
        complaint.save()
        messages.success(request, 'Reply sent successfully!')
        return redirect('view_complaints')
    
    return render(request, 'admin_panel/reply_complaint.html', {'complaint': complaint})

# ================================
# 9. NOTIFICATION SYSTEM
# ================================
@admin_required
def send_notification(request):
    """Send notification to forest officers - supports broadcast, multi-select, and single"""
    if request.method == 'POST':
        send_mode = request.POST.get('send_mode', 'selected')
        title = request.POST.get('title')
        message = request.POST.get('message')

        if send_mode == 'broadcast':
            # Send to ALL officers
            officers = CustomUser.objects.filter(user_type='OFFICER')
            count = 0
            for officer in officers:
                Notification.objects.create(
                    from_admin=request.user,
                    to_officer=officer,
                    title=title,
                    message=message
                )
                count += 1
            messages.success(request, f'Broadcast notification sent to {count} officer(s) successfully!')
        else:
            # Send to selected officer(s)
            officer_ids = request.POST.getlist('officers')
            if not officer_ids:
                messages.error(request, 'Please select at least one officer.')
                officer_profiles = ForestOfficer.objects.select_related('user', 'station', 'station__division').all()
                return render(request, 'admin_panel/send_notification.html', {'officer_profiles': officer_profiles})

            count = 0
            for officer_id in officer_ids:
                Notification.objects.create(
                    from_admin=request.user,
                    to_officer_id=officer_id,
                    title=title,
                    message=message
                )
                count += 1
            messages.success(request, f'Notification sent to {count} officer(s) successfully!')

        return redirect('view_sent_notifications')

    officer_profiles = ForestOfficer.objects.select_related('user', 'station', 'station__division').all()
    return render(request, 'admin_panel/send_notification.html', {'officer_profiles': officer_profiles})

@admin_required
def delete_sent_notification(request, pk):
    """Delete a sent notification"""
    notification = get_object_or_404(Notification, pk=pk)
    if request.method == 'POST':
        notification.delete()
        messages.success(request, 'Notification deleted successfully!')
    return redirect('view_sent_notifications')

@admin_required
def view_sent_notifications(request):
    """View history of notifications sent by Admin — groups broadcast messages together"""
    sent_notifications = Notification.objects.filter(from_admin=request.user).select_related('to_officer')
    date_filter = request.GET.get('date_filter')
    parsed_date = parse_date(date_filter) if date_filter else None
    if parsed_date:
        start_t = make_aware(datetime.combine(parsed_date, time.min))
        end_t = make_aware(datetime.combine(parsed_date, time.max))
        sent_notifications = sent_notifications.filter(created_at__range=(start_t, end_t))
    sent_notifications = sent_notifications.order_by('-created_at')

    # Group notifications: same title + message + created within 3 seconds = one group
    grouped = []
    used_ids = set()

    notifications_list = list(sent_notifications)
    for i, notif in enumerate(notifications_list):
        if notif.id in used_ids:
            continue

        # Find siblings (same title, message, created within 3 seconds)
        group_items = [notif]
        used_ids.add(notif.id)

        for j in range(i + 1, len(notifications_list)):
            other = notifications_list[j]
            if other.id in used_ids:
                continue
            if (other.title == notif.title and
                other.message == notif.message and
                abs((other.created_at - notif.created_at).total_seconds()) <= 3):
                group_items.append(other)
                used_ids.add(other.id)

        if len(group_items) > 1:
            grouped.append({
                'type': 'broadcast',
                'title': notif.title,
                'message': notif.message,
                'created_at': notif.created_at,
                'recipients': group_items,
                'count': len(group_items),
                'all_read': all(n.is_read for n in group_items),
                'read_count': sum(1 for n in group_items if n.is_read),
            })
        else:
            grouped.append({
                'type': 'single',
                'notification': notif,
            })

    return render(request, 'admin_panel/sent_notifications.html', {
        'grouped_notifications': grouped,
        'notifications': notifications_list,  # kept for delete modals
        'date_filter': date_filter
    })

# ================================
# 10. VIEW REPORTS
# ================================
@admin_required
def view_reports(request):
    """View all officer reports"""
    reports = Report.objects.select_related('officer', 'station').all()
    date_filter = request.GET.get('date_filter')
    parsed_date = parse_date(date_filter) if date_filter else None
    if parsed_date:
        start_t = make_aware(datetime.combine(parsed_date, time.min))
        end_t = make_aware(datetime.combine(parsed_date, time.max))
        reports = reports.filter(submitted_at__range=(start_t, end_t))
    reports = reports.order_by('-submitted_at')
    return render(request, 'admin_panel/reports.html', {'reports': reports, 'date_filter': date_filter})

# ================================
# 11. VIEW FIRE ALERTS
# ================================
@admin_required
def view_fire_alerts(request):
    """View all fire alerts"""
    alerts = FireAlert.objects.select_related('station').all()
    date_filter = request.GET.get('date_filter')
    parsed_date = parse_date(date_filter) if date_filter else None
    if parsed_date:
        start_t = make_aware(datetime.combine(parsed_date, time.min))
        end_t = make_aware(datetime.combine(parsed_date, time.max))
        alerts = alerts.filter(detected_at__range=(start_t, end_t))
    alerts = alerts.order_by('-detected_at')
    return render(request, 'admin_panel/fire_alerts.html', {'alerts': alerts, 'date_filter': date_filter})

@admin_required
def view_animal_alerts(request):
    """View all animal detection alerts"""
    from officer_module.models import AnimalAlert
    alerts = AnimalAlert.objects.select_related('station').all()
    date_filter = request.GET.get('date_filter')
    parsed_date = parse_date(date_filter) if date_filter else None
    if parsed_date:
        start_t = make_aware(datetime.combine(parsed_date, time.min))
        end_t = make_aware(datetime.combine(parsed_date, time.max))
        alerts = alerts.filter(detected_at__range=(start_t, end_t))
    alerts = alerts.order_by('-detected_at')
    return render(request, 'admin_panel/animal_alerts.html', {'alerts': alerts, 'date_filter': date_filter})

@admin_required
def view_human_intrusion_alerts(request):
    """View all human intrusion alerts"""
    from officer_module.models import HumanIntrusionAlert
    alerts = HumanIntrusionAlert.objects.select_related('station').all()
    date_filter = request.GET.get('date_filter')
    parsed_date = parse_date(date_filter) if date_filter else None
    if parsed_date:
        start_t = make_aware(datetime.combine(parsed_date, time.min))
        end_t = make_aware(datetime.combine(parsed_date, time.max))
        alerts = alerts.filter(detected_at__range=(start_t, end_t))
    alerts = alerts.order_by('-detected_at')
    return render(request, 'admin_panel/human_intrusion_alerts.html', {'alerts': alerts, 'date_filter': date_filter})

@admin_required
def update_fire_alert(request, pk):
    """Update fire alert status"""
    alert = get_object_or_404(FireAlert, pk=pk)
    
    if request.method == 'POST':
        status = request.POST.get('status')
        alert.status = status
        if status == 'RESOLVED':
            alert.resolved_at = timezone.now()
        alert.save()
        messages.success(request, 'Fire alert updated successfully!')
        return redirect('view_fire_alerts')
    
    """Edit animal"""
    animal = get_object_or_404(Animal, pk=pk)
    
    if request.method == 'POST':
        animal.name = request.POST.get('name')
        animal.scientific_name = request.POST.get('scientific_name')
        animal.description = request.POST.get('description')
        animal.is_dangerous = request.POST.get('is_dangerous') == 'on'
        if request.FILES.get('image'):
            animal.image = request.FILES.get('image')
        animal.save()
        messages.success(request, 'Animal updated successfully!')
        return redirect('manage_animals')
    
    return render(request, 'admin_panel/edit_animal.html', {'animal': animal})

@admin_required
def delete_animal(request, pk):
    """Delete animal"""
    animal = get_object_or_404(Animal, pk=pk)
    animal.delete()
    messages.success(request, 'Animal deleted successfully!')
    return redirect('manage_animals')

# ================================
# 6. PRESERVED ANIMAL MANAGEMENT
# ================================
@admin_required
def manage_preserved_animals(request):
    """List all preserved animals"""
    preserved = PreservedAnimal.objects.select_related('animal').all()
    return render(request, 'admin_panel/preserved_animals.html', {'preserved_animals': preserved})

@admin_required
def add_preserved_animal(request):
    """Add animal to preserved list"""
    if request.method == 'POST':
        animal_id = request.POST.get('animal')
        preservation_status = request.POST.get('preservation_status')
        threat_level = request.POST.get('threat_level')
        population_estimate = request.POST.get('population_estimate')
        conservation_notes = request.POST.get('conservation_notes')
        
        PreservedAnimal.objects.create(
            animal_id=animal_id,
            preservation_status=preservation_status,
            threat_level=threat_level,
            population_estimate=population_estimate if population_estimate else None,
            conservation_notes=conservation_notes
        )
        messages.success(request, 'Preserved animal added successfully!')
        return redirect('manage_preserved_animals')
    
    animals = Animal.objects.all()
    return render(request, 'admin_panel/add_preserved_animal.html', {'animals': animals})

# ================================
# 7. FOREST OFFICER MANAGEMENT
# ================================
@admin_required
def manage_officers(request):
    """List all forest officers"""
    officers = ForestOfficer.objects.select_related('user', 'station').all()
    return render(request, 'admin_panel/officers.html', {'officers': officers})

@admin_required
def add_officer(request):
    """Add new forest officer"""
    if request.method == 'POST':
        form = ForestOfficerForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username'].strip()
            email = form.cleaned_data['email'].strip()
            password = form.cleaned_data['password']
            phone_number = form.cleaned_data['phone_number'].strip()
            station = form.cleaned_data.get('station')
            designation = form.cleaned_data['designation'].strip()
            badge_number = form.cleaned_data['badge_number'].strip()

            errors = []

            # Uniqueness checks
            if CustomUser.objects.filter(username__iexact=username).exists():
                errors.append(f'Username "{username}" is already taken.')
            if CustomUser.objects.filter(email__iexact=email).exists():
                errors.append(f'Email "{email}" is already registered.')
            if CustomUser.objects.filter(phone_number=phone_number).exists():
                errors.append(f'Phone number "{phone_number}" is already in use.')
            if badge_number and ForestOfficer.objects.filter(badge_number__iexact=badge_number).exists():
                errors.append(f'Badge number "{badge_number}" is already assigned to another officer.')

            if errors:
                for error in errors:
                    messages.error(request, error)
            else:
                user = CustomUser.objects.create_user(
                    username=username,
                    email=email,
                    password=password,
                    user_type='OFFICER',
                    phone_number=phone_number
                )
                ForestOfficer.objects.create(
                    user=user,
                    station_id=station.pk if station else None,
                    designation=designation,
                    badge_number=badge_number
                )
                messages.success(request, 'Forest Officer added successfully!')
                return redirect('manage_officers')
        else:
            # Show form validation errors (password, username, email, phone format)
            for field, field_errors in form.errors.items():
                for error in field_errors:
                    messages.error(request, error)
    else:
        form = ForestOfficerForm()

    stations = ForestStation.objects.all()
    return render(request, 'admin_panel/add_officer.html', {'stations': stations, 'form': form})

@admin_required
def allocate_officer(request, pk):
    """Allocate officer to a station"""
    officer = get_object_or_404(ForestOfficer, pk=pk)
    
    if request.method == 'POST':
        station_id = request.POST.get('station')
        officer.station_id = station_id if station_id else None
        officer.save()
        messages.success(request, 'Officer allocated successfully!')
        return redirect('manage_officers')
    
    stations = ForestStation.objects.all()
    return render(request, 'admin_panel/allocate_officer.html', {'officer': officer, 'stations': stations})

# ================================
# 8. COMPLAINT MANAGEMENT
# ================================
@admin_required



















































































def edit_preserved_animal(request, pk):
    """Edit preserved animal"""
    preserved = get_object_or_404(PreservedAnimal, pk=pk)
    
    if request.method == 'POST':
        preserved.animal_id = request.POST.get('animal')
        preserved.preservation_status = request.POST.get('preservation_status')
        preserved.threat_level = request.POST.get('threat_level')
        preserved.population_estimate = request.POST.get('population_estimate') if request.POST.get('population_estimate') else None
        preserved.conservation_notes = request.POST.get('conservation_notes')
        preserved.save()
        messages.success(request, 'Preserved animal updated successfully!')
        return redirect('manage_preserved_animals')
    
    animals = Animal.objects.all()
    return render(request, 'admin_panel/edit_preserved_animal.html', {'preserved': preserved, 'animals': animals})

@admin_required
def delete_preserved_animal(request, pk):
    """Delete preserved animal"""
    preserved = get_object_or_404(PreservedAnimal, pk=pk)
    preserved.delete()
    messages.success(request, 'Preserved animal removed successfully!')
    return redirect('manage_preserved_animals')

# ================================
# 8. COMPLAINT MANAGEMENT
# ================================
@admin_required











































































































def edit_officer(request, pk):
    """Edit forest officer"""
    officer = get_object_or_404(ForestOfficer, pk=pk)
    user_pk = officer.user.pk

    if request.method == 'POST':
        form = ForestOfficerEditForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username'].strip()
            email = form.cleaned_data['email'].strip()
            phone_number = form.cleaned_data['phone_number'].strip()
            badge_number = form.cleaned_data['badge_number'].strip()

            errors = []

            # Uniqueness checks (exclude the current officer's own user record)
            if CustomUser.objects.filter(username__iexact=username).exclude(pk=user_pk).exists():
                errors.append(f'Username "{username}" is already taken.')
            if CustomUser.objects.filter(email__iexact=email).exclude(pk=user_pk).exists():
                errors.append(f'Email "{email}" is already registered.')
            if CustomUser.objects.filter(phone_number=phone_number).exclude(pk=user_pk).exists():
                errors.append(f'Phone number "{phone_number}" is already in use.')
            if badge_number and ForestOfficer.objects.filter(badge_number__iexact=badge_number).exclude(pk=pk).exists():
                errors.append(f'Badge number "{badge_number}" is already assigned to another officer.')

            if errors:
                for error in errors:
                    messages.error(request, error)
            else:
                # Update user details
                officer.user.username = username
                officer.user.email = email
                officer.user.phone_number = phone_number
                officer.user.save()

                # Update officer profile
                officer.station = form.cleaned_data['station']
                officer.designation = form.cleaned_data['designation']
                officer.badge_number = badge_number
                officer.save()

                messages.success(request, 'Officer updated successfully!')
                return redirect('manage_officers')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        initial_data = {
            'username': officer.user.username,
            'email': officer.user.email,
            'phone_number': officer.user.phone_number,
            'station': officer.station,
            'designation': officer.designation,
            'badge_number': officer.badge_number,
        }
        form = ForestOfficerEditForm(initial=initial_data)

    stations = ForestStation.objects.all()
    return render(request, 'admin_panel/edit_officer.html', {'officer': officer, 'stations': stations, 'form': form})

@admin_required
def delete_officer(request, pk):
    """Delete forest officer"""
    officer = get_object_or_404(ForestOfficer, pk=pk)
    user = officer.user
    officer.delete()
    user.delete()  # Also delete the user account
    messages.success(request, 'Officer deleted successfully!')
    return redirect('manage_officers')
