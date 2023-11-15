from .helpers import get_file_path

from category.models import Category
from users.models import Users, Admins

from django.contrib.gis.db import models



class ServiceProvider(Users):
    
    class AccountStatus(models.TextChoices):
        REJECTED = ('rejected', 'Rejected')
        PENDING = ('pending', 'Pending')
        ACCEPTED = ('accepted', 'Accepted')
    
    user = models.OneToOneField(Users, on_delete=models.CASCADE, related_name='service_provider', null=False)
    approved_by = models.ForeignKey(Admins,
                on_delete=models.PROTECT, null=True, related_name='accepted_services')
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="services_providerd")
    business_name = models.CharField(max_length=128, null=False, unique=True)
    bank_name = models.CharField(max_length=128, null=False)
    iban = models.CharField(max_length=40, null=False, unique=True)
    swift_code = models.CharField(max_length=16, null=False, unique=True)
    provider_file = models.FileField(upload_to=get_file_path, null=True) # null to be False
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


# class UpdateRequest(models.Model):
#     user = models.ForeignKey(ServiceProvider, on_delete=models.CASCADE)
#     updated_data = JSONField(null=True)
#     updated_at = models.DateTimeField(auto_now_add = True, null = False)

#     def __str__(self):
#         return f"UpdateRequest for {self.user.user.username}"
