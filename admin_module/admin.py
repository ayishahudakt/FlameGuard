from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, ForestDivision, ForestStation, Animal, Notification, Report, FireAlert, PreservedAnimal, UserComplaint, OfficerComplaint

# ================================
# 1. CUSTOM USER ADMIN
# ================================
@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    """
    Custom admin for our CustomUser model.
    Shows user_type and phone_number in the list.
    """
    list_display = ('username', 'email', 'user_type', 'phone_number', 'is_staff', 'is_active')
    list_filter = ('user_type', 'is_staff', 'is_active')
    search_fields = ('username', 'email', 'phone_number')
    
    # Add user_type to the form
    fieldsets = UserAdmin.fieldsets + (
        ('Additional Info', {'fields': ('user_type', 'phone_number', 'address')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Additional Info', {'fields': ('user_type', 'phone_number', 'address')}),
    )

# ================================
# 2. FOREST DIVISION ADMIN
# ================================
@admin.register(ForestDivision)
class ForestDivisionAdmin(admin.ModelAdmin):
    list_display = ('name', 'location', 'description')
    search_fields = ('name', 'location')

# ================================
# 3. FOREST STATION ADMIN
# ================================
@admin.register(ForestStation)
class ForestStationAdmin(admin.ModelAdmin):
    list_display = ('name', 'division', 'contact_number')
    list_filter = ('division',)
    search_fields = ('name', 'contact_number')

# ================================
# 4. ANIMAL ADMIN
# ================================
@admin.register(Animal)
class AnimalAdmin(admin.ModelAdmin):
    list_display = ('name', 'scientific_name', 'is_dangerous')
    list_filter = ('is_dangerous',)
    search_fields = ('name', 'scientific_name')

# ================================
# PRESERVED ANIMAL ADMIN
# ================================
@admin.register(PreservedAnimal)
class PreservedAnimalAdmin(admin.ModelAdmin):
    list_display = ('animal', 'preservation_status', 'threat_level', 'population_estimate', 'last_updated')
    list_filter = ('preservation_status', 'threat_level')
    search_fields = ('animal__name',)

# ================================
# 5. USER COMPLAINT ADMIN
# ================================
@admin.register(UserComplaint)
class UserComplaintAdmin(admin.ModelAdmin):
    list_display = ('subject', 'sender', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('subject', 'sender__username')

    def get_queryset(self, request):
        return super().get_queryset(request).filter(sender__user_type='USER')

# ================================
# OFFICER COMPLAINT ADMIN
# ================================
@admin.register(OfficerComplaint)
class OfficerComplaintAdmin(admin.ModelAdmin):
    list_display = ('subject', 'sender', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('subject', 'sender__username')

    def get_queryset(self, request):
        return super().get_queryset(request).filter(sender__user_type='OFFICER')

# ================================
# 6. NOTIFICATION ADMIN
# ================================
@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('title', 'from_admin', 'to_officer', 'is_read', 'created_at')
    list_filter = ('is_read', 'created_at')
    search_fields = ('title', 'from_admin__username', 'to_officer__username')

# ================================
# 7. REPORT ADMIN
# ================================
@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ('title', 'officer', 'station', 'submitted_at')
    list_filter = ('station', 'submitted_at')
    search_fields = ('title', 'officer__username')

# ================================
# 8. FIRE ALERT ADMIN
# ================================
@admin.register(FireAlert)
class FireAlertAdmin(admin.ModelAdmin):
    list_display = ('station', 'severity', 'status', 'detected_at')
    list_filter = ('severity', 'status', 'detected_at')
    search_fields = ('station__name',)
