from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
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
            form.save()
            messages.success(request, 'Forest Division added successfully!')
            return redirect('manage_divisions')
        else:
            # Form has validation errors, they will be displayed in template
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
            # Create user account
            user = CustomUser.objects.create_user(
                username=form.cleaned_data['username'],
                email=form.cleaned_data['email'],
                password=form.cleaned_data['password'],
                user_type='OFFICER',
                phone_number=form.cleaned_data['phone_number']
            )
            
            # Create officer profile
            ForestOfficer.objects.create(
                user=user,
                station=form.cleaned_data['station'],
                designation=form.cleaned_data['designation'],
                badge_number=form.cleaned_data['badge_number']
            )
            messages.success(request, 'Forest Officer added successfully!')
            return redirect('manage_officers')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = ForestOfficerForm()
    
    stations = ForestStation.objects.all()
    return render(request, 'admin_panel/add_officer.html', {'form': form, 'stations': stations})

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
def view_complaints(request):
    """View all complaints"""
    complaints = Complaint.objects.select_related('sender').all()
    return render(request, 'admin_panel/complaints.html', {'complaints': complaints})

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
    """Send notification to forest officers"""
    if request.method == 'POST':
        officer_id = request.POST.get('officer')
        title = request.POST.get('title')
        message = request.POST.get('message')
        
        Notification.objects.create(
            from_admin=request.user,
            to_officer_id=officer_id,
            title=title,
            message=message
        )
        messages.success(request, 'Notification sent successfully!')
        return redirect('view_sent_notifications')
    
    officers = CustomUser.objects.filter(user_type='OFFICER')
    return render(request, 'admin_panel/send_notification.html', {'officers': officers})

@admin_required
def view_sent_notifications(request):
    """View history of notifications sent by Admin"""
    sent_notifications = Notification.objects.filter(from_admin=request.user)
    return render(request, 'admin_panel/sent_notifications.html', {'notifications': sent_notifications})

# ================================
# 10. VIEW REPORTS
# ================================
@admin_required
def view_reports(request):
    """View all officer reports"""
    reports = Report.objects.select_related('officer', 'station').all()
    return render(request, 'admin_panel/reports.html', {'reports': reports})

# ================================
# 11. VIEW FIRE ALERTS
# ================================
@admin_required
def view_fire_alerts(request):
    """View all fire alerts"""
    alerts = FireAlert.objects.select_related('station').all()
    return render(request, 'admin_panel/fire_alerts.html', {'alerts': alerts})

@admin_required
def view_animal_alerts(request):
    """View all animal detection alerts"""
    from officer_module.models import AnimalAlert
    alerts = AnimalAlert.objects.select_related('station').all().order_by('-detected_at')
    return render(request, 'admin_panel/animal_alerts.html', {'alerts': alerts})

@admin_required
def view_human_intrusion_alerts(request):
    """View all human intrusion alerts"""
    from officer_module.models import HumanIntrusionAlert
    alerts = HumanIntrusionAlert.objects.select_related('station').all().order_by('-detected_at')
    return render(request, 'admin_panel/human_intrusion_alerts.html', {'alerts': alerts})

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
        # Create user account
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        phone_number = request.POST.get('phone_number')
        
        user = CustomUser.objects.create_user(
            username=username,
            email=email,
            password=password,
            user_type='OFFICER',
            phone_number=phone_number
        )
        
        # Create officer profile
        station_id = request.POST.get('station')
        designation = request.POST.get('designation')
        badge_number = request.POST.get('badge_number')
        
        ForestOfficer.objects.create(
            user=user,
            station_id=station_id if station_id else None,
            designation=designation,
            badge_number=badge_number
        )
        messages.success(request, 'Forest Officer added successfully!')
        return redirect('manage_officers')
    
    stations = ForestStation.objects.all()
    return render(request, 'admin_panel/add_officer.html', {'stations': stations})

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
def view_complaints(request):
    """View all complaints"""
    complaints = Complaint.objects.select_related('sender').all()
    return render(request, 'admin_panel/complaints.html', {'complaints': complaints})

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
    """Send notification to forest officers"""
    if request.method == 'POST':
        officer_id = request.POST.get('officer')
        title = request.POST.get('title')
        message = request.POST.get('message')
        if not officer_id or not title or not message:
            messages.error(request, 'All fields are required. Please select an officer and provide a title and message.')
            return redirect('send_notification')

        Notification.objects.create(
            from_admin=request.user,
            to_officer_id=officer_id,
            title=title,
            message=message
        )
        messages.success(request, 'Notification sent successfully!')
        return redirect('admin_dashboard')
    
    officers = CustomUser.objects.filter(user_type='OFFICER')
    return render(request, 'admin_panel/send_notification.html', {'officers': officers})

# ================================
# 10. VIEW REPORTS
# ================================
@admin_required
def view_reports(request):
    """View all officer reports"""
    reports = Report.objects.select_related('officer', 'station').all()
    return render(request, 'admin_panel/reports.html', {'reports': reports})

# ================================
# 11. VIEW FIRE ALERTS
# ================================
@admin_required
def view_fire_alerts(request):
    """View all fire alerts"""
    alerts = FireAlert.objects.select_related('station').all()
    return render(request, 'admin_panel/fire_alerts.html', {'alerts': alerts})

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
    
    return render(request, 'admin_panel/update_fire_alert.html', {'alert': alert})


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
        # Create user account
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        phone_number = request.POST.get('phone_number')
        
        user = CustomUser.objects.create_user(
            username=username,
            email=email,
            password=password,
            user_type='OFFICER',
            phone_number=phone_number
        )
        
        # Create officer profile
        station_id = request.POST.get('station')
        designation = request.POST.get('designation')
        badge_number = request.POST.get('badge_number')
        
        ForestOfficer.objects.create(
            user=user,
            station_id=station_id if station_id else None,
            designation=designation,
            badge_number=badge_number
        )
        messages.success(request, 'Forest Officer added successfully!')
        return redirect('manage_officers')
    
    stations = ForestStation.objects.all()
    return render(request, 'admin_panel/add_officer.html', {'stations': stations})

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
def view_complaints(request):
    """View all complaints"""
    complaints = Complaint.objects.select_related('sender').all()
    return render(request, 'admin_panel/complaints.html', {'complaints': complaints})

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
    """Send notification to forest officers"""
    if request.method == 'POST':
        officer_id = request.POST.get('officer')
        title = request.POST.get('title')
        message = request.POST.get('message')
        
        Notification.objects.create(
            from_admin=request.user,
            to_officer_id=officer_id,
            title=title,
            message=message
        )
        messages.success(request, 'Notification sent successfully!')
        return redirect('admin_dashboard')
    
    officers = CustomUser.objects.filter(user_type='OFFICER')
    return render(request, 'admin_panel/send_notification.html', {'officers': officers})

# ================================
# 10. VIEW REPORTS
# ================================
@admin_required
def view_reports(request):
    """View all officer reports"""
    reports = Report.objects.select_related('officer', 'station').all()
    return render(request, 'admin_panel/reports.html', {'reports': reports})

# ================================
# 11. VIEW FIRE ALERTS
# ================================
@admin_required
def view_fire_alerts(request):
    """View all fire alerts"""
    alerts = FireAlert.objects.select_related('station').all()
    return render(request, 'admin_panel/fire_alerts.html', {'alerts': alerts})

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
    
    return render(request, 'admin_panel/update_fire_alert.html', {'alert': alert})


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


@admin_required
def edit_officer(request, pk):
    """Edit forest officer"""
    officer = get_object_or_404(ForestOfficer, pk=pk)
    
    if request.method == 'POST':
        form = ForestOfficerEditForm(request.POST)
        if form.is_valid():
            # Update user details
            officer.user.username = form.cleaned_data['username']
            officer.user.email = form.cleaned_data['email']
            officer.user.phone_number = form.cleaned_data['phone_number']
            officer.user.save()
            
            # Update officer details
            officer.station = form.cleaned_data['station']
            officer.designation = form.cleaned_data['designation']
            officer.badge_number = form.cleaned_data['badge_number']
            officer.save()
            
            messages.success(request, 'Officer updated successfully!')
            return redirect('manage_officers')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        # Pre-fill form with existing data
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
