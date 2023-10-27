from django.db import models

from category.models import Category
from users.models import Users, Admins

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
    account_status = models.CharField(max_length=16,
                choices=AccountStatus.choices, default=AccountStatus.PENDING)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.business_name
    
    class Meta:
        ordering = ['date_joined']
        verbose_name = "ServiceProvider"
        verbose_name_plural = "ServiceProvider"

