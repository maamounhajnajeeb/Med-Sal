# from django.db import models # we don't need this after adding from django.contrib.gis.db import models
from category.models import Category
from users.models import Users, Admins

from django.contrib.gis.db import models


class ServiceProvider(Users):
    
    class AccountStatus(models.TextChoices):
        REJECTED = ('rejected', 'Rejected')
        PENDING = ('pending', 'Pending')
        ACCEPTED = ('accepted', 'Accepted')
    
    user = models.OneToOneField(Users, on_delete = models.CASCADE, related_name='service_provider')
    approved_by = models.ForeignKey(Admins, on_delete = models.SET_NULL, null=True,related_name='accepted_services')
    category = models.ForeignKey(Category, on_delete = models.CASCADE)
    business_name = models.CharField(max_length=128, null=False, unique=True) 
    contact_number = models.CharField(max_length=16, null=False, unique=True)
    bank_name = models.CharField(max_length=128, null=False)
    iban = models.CharField(max_length=40, null=False, unique=True)
    swift_code = models.CharField(max_length=16, null=False, unique=True)
    provider_file = models.FileField(upload_to="service_providers/documents/", null=False)
    account_status = models.CharField(max_length=16, choices=AccountStatus.choices, default=AccountStatus.PENDING)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['date_joined']
        verbose_name = "ServiceProvider"
        verbose_name_plural = "ServiceProviders"

    def __str__(self):
        return self.business_name


class ServiceProviderLocations(models.Model):
    service_provider_id = models.ForeignKey(ServiceProvider, on_delete = models.CASCADE)
    location = models.PointField(srid=4326, null = True, blank = True) # null and blank must be False 
    opening = models.TimeField(blank = False)
    closing = models.TimeField(blank = False)
    crew = models.CharField(max_length = 32, blank = False)
    created_at = models.DateTimeField(auto_now_add = True, null = False)
    
    class Meta:
        verbose_name = "ServiceProviderLocations"
        verbose_name_plural = "ServiceProviderLocations"

    def __str__(self):
        return f"{self.service_provider_id.business_name} => {self.location}"