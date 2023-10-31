from django.db import models

from category.models import MyCategory
from users.models import Users, Admins


class ServiceProvider(models.Model):
    
    class Status(models.TextChoices):
        REJECTED = ('rejected', 'Rejected')
        PENDING = ('pending', 'Pending')
        ACCEPTED = ('accepted', 'Accepted')
    
    user = models.OneToOneField(Users, on_delete = models.CASCADE, related_name='service_provider')
    approved_by = models.ForeignKey(Admins, on_delete = models.SET_NULL, null=True,related_name='accepted_services')
    category = models.ForeignKey(MyCategory, on_delete = models.CASCADE)
    business_name = models.CharField(max_length=128, null=False, unique=True) 
    contact_number = models.CharField(max_length=16, null=False, unique=True)
    bank_name = models.CharField(max_length=128, null=False)
    iban = models.CharField(max_length=40, null=False, unique=True)
    swift_code = models.CharField(max_length=16, null=False, unique=True)
    provider_file = models.FileField(upload_to="service_providers/documents/", null=False)
    account_status = models.CharField(max_length=16, choices=Status.choices, default=Status.PENDING)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    base_type = Users.Types.SERVICE_PROVIDER
    
    def __str__(self):
        return str(self.user)
    
    class Meta:
        verbose_name = "ServiceProvider"
        verbose_name_plural = "ServiceProviders"


class ServiceProviderLocations(models.Model):
    service_provider_id = models.ForeignKey(ServiceProvider, on_delete = models.CASCADE, null = True)
    location = models.CharField(max_length=20, blank=False)
    opening = models.TimeField(blank=False)
    closing = models.TimeField(blank=False)
    crew = models.CharField(max_length = 32, blank=False)
    created_at = models.DateTimeField(auto_now_add = True, null = False)
    
    def __str__(self):
        return self.service_provider_id.business_name
    
    class Meta:
        verbose_name = "ServiceProviderLocations"
        verbose_name_plural = "ServiceProviderLocations"
