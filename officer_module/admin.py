from django.contrib import admin
from .models import ForestOfficer

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
