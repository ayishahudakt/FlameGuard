from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, ForestDivision, ForestStation, Animal

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
