from django.db import models
from admin_module.models import CustomUser, ForestStation

class ForestOfficer(models.Model):
    """
    Stores extra details for Forest Officers.
    Linked to the main CustomUser (login info) and their workspace (ForestStation).
    """
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='officer_profile')
    station = models.ForeignKey(ForestStation, on_delete=models.SET_NULL, null=True, blank=True)
    designation = models.CharField(max_length=100) # e.g. "Range Officer"
    badge_number = models.CharField(max_length=50, blank=True)

    def __str__(self):
        return f"{self.user.username} - {self.designation}"
