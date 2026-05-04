from django.contrib import admin
from .models import ForestOfficer, UserAlert, HumanIntrusionAlert, UserNotification, AnimalAlert

@admin.register(ForestOfficer)
class ForestOfficerAdmin(admin.ModelAdmin):
    """
    Admin interface for Forest Officers.
    Shows officer details and their assigned station.
    """
    list_display = ('user', 'designation', 'station', 'badge_number')
    list_filter = ('designation', 'station')
    search_fields = ('user__username', 'badge_number', 'designation')
    
    # Make it easier to select user and station
    autocomplete_fields = ['user', 'station']

# ================================
# USER ALERT ADMIN
# ================================
@admin.register(UserAlert)
class UserAlertAdmin(admin.ModelAdmin):
    list_display = ('title', 'officer', 'alert_type', 'is_active', 'created_at')
    list_filter = ('alert_type', 'is_active')
    search_fields = ('title', 'officer__username')

# ================================
# HUMAN INTRUSION ALERT ADMIN
# ================================
@admin.register(HumanIntrusionAlert)
class HumanIntrusionAlertAdmin(admin.ModelAdmin):
    list_display = ('station', 'status', 'detected_at', 'officer_notified')
    list_filter = ('status', 'officer_notified')
    search_fields = ('station__name',)

# ================================
# USER NOTIFICATION ADMIN
# ================================
@admin.register(UserNotification)
class UserNotificationAdmin(admin.ModelAdmin):
    list_display = ('title', 'recipient', 'notif_type', 'is_read', 'created_at')
    list_filter = ('notif_type', 'is_read')
    search_fields = ('title', 'recipient__username')

# ================================
# ANIMAL ALERT ADMIN
# ================================
@admin.register(AnimalAlert)
class AnimalAlertAdmin(admin.ModelAdmin):
    list_display = ('animal_type', 'station', 'severity', 'status', 'detected_at')
    list_filter = ('severity', 'status')
    search_fields = ('animal_type', 'station__name')
