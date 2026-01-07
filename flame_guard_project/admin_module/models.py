from django.db import models
from django.contrib.auth.models import AbstractUser

# ================================
# 1. CUSTOM USER MODEL
# ================================
class CustomUser(AbstractUser):
    """
    Our custom 'ID Card'.
    Replaces the default Django User.
    Distinguishes between Admin, Officer, and Public User.
    """
    USER_TYPE_CHOICES = (
        ('ADMIN', 'Admin'),
        ('OFFICER', 'Forest Officer'),
        ('USER', 'Public User'),
    )
    
    user_type = models.CharField(max_length=10, choices=USER_TYPE_CHOICES, default='USER')
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    address = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.username} ({self.user_type})"

# ================================
# 2. FOREST MANAGEMENT
# ================================
class ForestDivision(models.Model):
    """
    Represents a large Forest Area (e.g., Wayanad North).
    """
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    location = models.CharField(max_length=200, blank=True)

    def __str__(self):
        return self.name

class ForestStation(models.Model):
    """
    Represents a Station inside a Division (e.g., Begur Range).
    """
    division = models.ForeignKey(ForestDivision, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    contact_number = models.CharField(max_length=15)
    address = models.TextField()

    def __str__(self):
        return f"{self.name} ({self.division.name})"

# ================================
# 3. ANIMAL REGISTRY
# ================================
class Animal(models.Model):
    """
    Database of animals we want to protect/detect.
    """
    name = models.CharField(max_length=100) # e.g., Tiger
    scientific_name = models.CharField(max_length=100, blank=True)
    description = models.TextField()
    is_dangerous = models.BooleanField(default=False)
    image = models.ImageField(upload_to='animals/', blank=True, null=True)

    def __str__(self):
        return self.name
