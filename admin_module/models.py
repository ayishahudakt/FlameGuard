from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator, MaxValueValidator

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
    division = models.ForeignKey(
        'ForestDivision',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='users',
    )

    def __str__(self):
        return f"{self.username} ({self.user_type})"

# ================================
# 2. FOREST MANAGEMENT
# ================================
class ForestDivision(models.Model):
    """
    Represents a large Forest Area (e.g., Wayanad North).
    """
    # Validator for alphabetic characters and spaces only
    alpha_space_validator = RegexValidator(
        regex=r'^[A-Za-z\s]+$',
        message='Only alphabets and spaces are allowed',
        code='invalid_name'
    )
    
    name = models.CharField(
        max_length=100,
        validators=[alpha_space_validator]
    )
    description = models.TextField(blank=True)
    location = models.CharField(
        max_length=200,
        blank=True,
        validators=[alpha_space_validator]
    )

    def __str__(self):
        return self.name

class ForestStation(models.Model):
    """
    Represents a Station inside a Division (e.g., Begur Range).
    """
    division = models.ForeignKey(ForestDivision, on_delete=models.CASCADE)
    
    # Validators
    alpha_space_validator = RegexValidator(
        regex=r'^[A-Za-z\s]+$',
        message='Only alphabets and spaces are allowed',
        code='invalid_name'
    )
    numeric_validator = RegexValidator(
        regex=r'^\d{10}$',
        message='Contact number must be exactly 10 digits',
        code='invalid_contact_number'
    )

    name = models.CharField(
        max_length=100,
        validators=[alpha_space_validator]
    )
    contact_number = models.CharField(
        max_length=15, 
        validators=[numeric_validator]
    )
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
    # Validator: Must contain at least one alphabet
    description_validator = RegexValidator(
        regex=r'[a-zA-Z]',
        message="Description must contain alphabetic characters. Numbers alone are not allowed.",
        code='invalid_description'
    )

    name = models.CharField(max_length=100) # e.g., Tiger
    scientific_name = models.CharField(max_length=100, blank=True)
    description = models.TextField(validators=[description_validator])
    is_dangerous = models.BooleanField(default=False)
    image = models.ImageField(upload_to='animals/', blank=True, null=True)

    def __str__(self):
        return self.name

# ================================
# 4. PRESERVED ANIMAL REGISTRY
# ================================
class PreservedAnimal(models.Model):
    """
    Special registry for endangered/preserved animals.
    """
    PRESERVATION_STATUS_CHOICES = (
        ('ENDANGERED', 'Endangered'),
        ('VULNERABLE', 'Vulnerable'),
        ('CRITICALLY_ENDANGERED', 'Critically Endangered'),
        ('PROTECTED', 'Protected'),
    )
    
    THREAT_LEVEL_CHOICES = (
        ('LOW', 'Low'),
        ('MEDIUM', 'Medium'),
        ('HIGH', 'High'),
        ('CRITICAL', 'Critical'),
    )
    
    animal = models.ForeignKey(Animal, on_delete=models.CASCADE, related_name='preservation_info')
    preservation_status = models.CharField(max_length=30, choices=PRESERVATION_STATUS_CHOICES)
    threat_level = models.CharField(max_length=10, choices=THREAT_LEVEL_CHOICES)
    population_estimate = models.IntegerField(
        null=True, 
        blank=True,
        validators=[MaxValueValidator(999999, message="Population estimate must be a numeric value with a maximum of 6 digits.")]
    )
    conservation_notes = models.TextField(blank=True)
    last_updated = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.animal.name} - {self.preservation_status}"

# ================================
# 5. COMPLAINT MANAGEMENT
# ================================
class Complaint(models.Model):
    """
    Complaints from Officers or Public Users.
    """
    STATUS_CHOICES = (
        ('PENDING', 'Pending'),
        ('IN_PROGRESS', 'In Progress'),
        ('RESOLVED', 'Resolved'),
    )
    
    sender = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='sent_complaints')
    subject_validator = RegexValidator(
        regex=r'^[A-Za-z\s]+$',
        message='Subject must contain only letters and spaces.',
        code='invalid_subject'
    )
    subject = models.CharField(max_length=200, validators=[subject_validator])
    message = models.TextField()
    reply = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='PENDING')
    created_at = models.DateTimeField(auto_now_add=True)
    replied_at = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.subject} - {self.sender.username}"
    
    class Meta:
        ordering = ['-created_at']

# ================================
# 6. NOTIFICATION SYSTEM
# ================================
class Notification(models.Model):
    """
    Notifications from Admin to Forest Officers.
    """
    from_admin = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='sent_notifications', limit_choices_to={'user_type': 'ADMIN'})
    to_officer = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='received_notifications', limit_choices_to={'user_type': 'OFFICER'})
    title = models.CharField(max_length=200)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.title} → {self.to_officer.username}"
    
    class Meta:
        ordering = ['-created_at']

# ================================
# 7. OFFICER REPORTS
# ================================
class Report(models.Model):
    """
    Reports submitted by Forest Officers.
    """
    officer = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='reports', limit_choices_to={'user_type': 'OFFICER'})
    title = models.CharField(max_length=200)
    content = models.TextField()
    station = models.ForeignKey(ForestStation, on_delete=models.SET_NULL, null=True, blank=True)
    submitted_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.title} by {self.officer.username}"
    
    class Meta:
        ordering = ['-submitted_at']

# ================================
# 8. FIRE ALERT SYSTEM
# ================================
class FireAlert(models.Model):
    """
    Fire detection alerts from camera module.
    """
    SEVERITY_CHOICES = (
        ('LOW', 'Low'),
        ('MEDIUM', 'Medium'),
        ('HIGH', 'High'),
        ('CRITICAL', 'Critical'),
    )
    
    STATUS_CHOICES = (
        ('ACTIVE', 'Active'),
        ('INVESTIGATING', 'Investigating'),
        ('CONTAINED', 'Contained'),
        ('RESOLVED', 'Resolved'),
    )
    
    station = models.ForeignKey(ForestStation, on_delete=models.CASCADE, related_name='fire_alerts')
    severity = models.CharField(max_length=10, choices=SEVERITY_CHOICES)
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='ACTIVE')
    detected_at = models.DateTimeField(auto_now_add=True)
    location_details = models.TextField(blank=True)
    image = models.ImageField(upload_to='fire_alerts/', blank=True, null=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
    resolved_by = models.ForeignKey('officer_module.ForestOfficer', on_delete=models.SET_NULL, null=True, blank=True, related_name='resolved_fire_alerts')
    
    def __str__(self):
        return f"Fire Alert - {self.station.name} ({self.severity})"
    
    class Meta:
        ordering = ['-detected_at']
