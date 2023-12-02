from django.db import models

from service_providers.models import ServiceProviderLocations
from category.models import Category



class Service(models.Model):
    provider_location = models.ForeignKey(
        ServiceProviderLocations, on_delete=models.CASCADE, related_name="services", null=False)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="services", null=False)
    ar_title = models.CharField(max_length=127, null=False)
    en_title = models.CharField(max_length=127, null=False)
    ar_description = models.TextField(null=False)
    en_description = models.TextField(null=False)
    image = models.CharField(max_length=256, null=False)
    price = models.IntegerField()
    created_at = models.DateTimeField(auto_now=True)
    updated_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self) -> str:
        return f"{self.en_title}, category: {self.category.en_name}, provider: {self.provider_location.service_provider.business_name}"


