from django.db import models

from service_providers.models import ServiceProviderLocations



class Product(models.Model):
    service_provider_location = models.ForeignKey(ServiceProviderLocations, on_delete=models.CASCADE, null=False)
    quantity = models.IntegerField()
    ar_title = models.CharField(max_length=128, null=False)
    en_title = models.CharField(max_length=128, null=False)
    ar_description = models.TextField(null=False)
    en_description = models.TextField(null=False)
    images = models.CharField(max_length=128)
    price = models.DecimalField(null=False, max_digits=8, decimal_places=2)
    created_at = models.DateField(auto_now_add=True)
    updated_at = models.DateField(auto_now=True)
    
    def __str__(self) -> str:
        category = self.service_provider_location.service_provider.category
        return f"prt_id: {self.id}, prt_en_title: {self.en_title}, prt_category: {category}"
