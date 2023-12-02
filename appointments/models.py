from django.conf import settings
from django.db import models

from services.models import Service

class AppointmentsDraft(models.Model):
    service = models.ForeignKey(
        Service, on_delete=models.CASCADE, null=False, related_name="draft_appointments")
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=False, on_delete=models.CASCADE, related_name="draft_appointments")
    from_time = models.TimeField(null=False)
    to_time = models.TimeField(null=False)
    date = models.DateField(null=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self) -> str:
        return f"{self.service.en_title}, user: {self.user.email}"


class Appointments(models.Model):
    service = models.ForeignKey(
        Service, on_delete=models.CASCADE, null=False, related_name="appointments")
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=False, on_delete=models.CASCADE, related_name="appointments")
    from_time = models.TimeField(null=False)
    to_time = models.TimeField(null=False)
    date = models.DateField(null=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self) -> str:
        return f"{self.service.en_title}, user: {self.user.email}"


class RejectedAppointments(models.Model):
    draft_appointment = models.ForeignKey(
        AppointmentsDraft, on_delete=models.CASCADE, null=False, related_name="rejected_appointments")
    reason = models.TextField(null=False)
    read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self) -> str:
        return f"{self.draft_appointment.service.en_title}, read from admin: {self.read}"
