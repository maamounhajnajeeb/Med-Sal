from django.db import models
from category.models import Category
from users.models import Users, Admins











class ServiceProvider(models.Model):
    
    class AccountStatus(models.TextChoices):
        REJECTED = ('rejected', 'Rejected')
        PENDING = ('pending', 'Pending')
        ACCEPTED = ('accepted', 'Accepted')

    user = models.OneToOneField(Users, on_delete = models.CASCADE, related_name = 'service_provider')
    
    approved_by = models.ForeignKey(Admins, on_delete = models.SET_NULL, null = True, blank = True, related_name='approved_service_providers')    

    category = models.ForeignKey(Category, blank=True, null=True, on_delete = models.CASCADE)
    
    business_name = models.CharField(max_length = 128, null = True) 
    
    contact_number = models.CharField(max_length = 32, null = True)
    
    bank_name = models.CharField(max_length = 128, null = True)
    
    iban = models.CharField(max_length = 32, null = True)
    
    swift_code = models.CharField(max_length = 32, null = True)
    
    provider_file = models.FileField(upload_to = "service_providers/documents/", null = True)
    
    account_status = models.CharField(max_length = 20, choices = AccountStatus.choices, default = AccountStatus.PENDING)
    
    created_at = models.DateTimeField(auto_now_add = True)
    
    updated_at = models.DateTimeField(auto_now = True)
    
    base_type = Users.Types.SERVICE_PROVIDER

    def __str__(self):
        return str(self.user)
    
    # class Meta:
    #     ordering = ['date_joined']
    #     verbose_name = "ServiceProvider"
    #     verbose_name_plural = "ServiceProvider"

    class Meta:
        ordering = ['user']
