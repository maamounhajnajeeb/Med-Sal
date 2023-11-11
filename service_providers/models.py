from django.contrib.gis.db import models

from .helpers import get_file_path

from category.models import Category
from users.models import Users, Admins


class ServiceProvider(Users):
    
    class AccountStatus(models.TextChoices):
        REJECTED = ('rejected', 'Rejected')
        PENDING = ('pending', 'Pending')
        ACCEPTED = ('accepted', 'Accepted')
    
    user = models.OneToOneField(Users, on_delete=models.CASCADE, related_name='service_provider', null=True)
    approved_by = models.ForeignKey(Admins,
                on_delete=models.PROTECT, null=True, related_name='accepted_services')
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="services_providerd")
    business_name = models.CharField(max_length=128, null=False, unique=True)
    bank_name = models.CharField(max_length=128, null=False)
    iban = models.CharField(max_length=40, null=False, unique=True)
    swift_code = models.CharField(max_length=16, null=False, unique=True)
    provider_file = models.FileField(upload_to=get_file_path, null=False)
    account_status = models.CharField(max_length=16,
            choices=AccountStatus.choices, default=AccountStatus.PENDING)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        # ordering = ['user__date_joined']
        verbose_name = "ServiceProvider"
        verbose_name_plural = "ServiceProviders"

    def __str__(self):
        return self.business_name


class ServiceProviderLocations(models.Model):
    service_provider_id = models.ForeignKey(ServiceProvider, on_delete = models.CASCADE)
    location = models.PointField(srid=4326, null=True, blank=True) # null and blank must be False
    opening = models.TimeField(null=False)
    closing = models.TimeField(null=False)
    crew = models.CharField(max_length=32, null=False)
    created_at = models.DateTimeField(auto_now_add=True, null=False)
    
    class Meta:
        verbose_name = "ServiceProviderLocations"
        verbose_name_plural = "ServiceProviderLocations"
        
    def __str__(self):
        return f"{self.service_provider_id.business_name} => {self.location}"