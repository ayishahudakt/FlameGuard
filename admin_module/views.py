from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.db.models import Count, Q
from .models import (CustomUser, ForestDivision, ForestStation, Animal, 
                     PreservedAnimal, Complaint, Notification, Report, FireAlert)
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
        name = request.POST.get('name')
        description = request.POST.get('description')
        location = request.POST.get('location')
        
        ForestDivision.objects.create(
            name=name,
            description=description,
            location=location
        )
        messages.success(request, 'Forest Division added successfully!')
        return redirect('manage_divisions')
    
    return render(request, 'admin_panel/add_division.html')

@admin_required
def edit_division(request, pk):
    """Edit forest division"""
    division = get_object_or_404(ForestDivision, pk=pk)
    
    if request.method == 'POST':
        division.name = request.POST.get('name')
        division.description = request.POST.get('description')
        division.location = request.POST.get('location')
        division.save()
        messages.success(request, 'Division updated successfully!')
        return redirect('manage_divisions')
    
    return render(request, 'admin_panel/edit_division.html', {'division': division})

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
        division_id = request.POST.get('division')
        name = request.POST.get('name')
        contact_number = request.POST.get('contact_number')
        address = request.POST.get('address')
        
        ForestStation.objects.create(
            division_id=division_id,
            name=name,
            contact_number=contact_number,
            address=address
        )
        messages.success(request, 'Forest Station added successfully!')
        return redirect('manage_stations')
    
    divisions = ForestDivision.objects.all()
    return render(request, 'admin_panel/add_station.html', {'divisions': divisions})

@admin_required
def edit_station(request, pk):
    """Edit forest station"""
    station = get_object_or_404(ForestStation, pk=pk)
    
    if request.method == 'POST':
        station.division_id = request.POST.get('division')
        station.name = request.POST.get('name')
        station.contact_number = request.POST.get('contact_number')
        station.address = request.POST.get('address')
        station.save()
        messages.success(request, 'Station updated successfully!')
        return redirect('manage_stations')
    
    divisions = ForestDivision.objects.all()
    return render(request, 'admin_panel/edit_station.html', {'station': station, 'divisions': divisions})

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
        name = request.POST.get('name')
        scientific_name = request.POST.get('scientific_name')
        description = request.POST.get('description')
        is_dangerous = request.POST.get('is_dangerous') == 'on'
        image = request.FILES.get('image')
        
        Animal.objects.create(
            name=name,
            scientific_name=scientific_name,
            description=description,
            is_dangerous=is_dangerous,
            image=image
        )
        messages.success(request, 'Animal added successfully!')
        return redirect('manage_animals')
    
    return render(request, 'admin_panel/add_animal.html')

@admin_required
def edit_animal(request, pk):
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
