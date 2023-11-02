from django.db import models

from service_providers.models import ServiceProviderLocations
from category.models import Category

class Product(models.Model):
    service_provider_location = models.ForeignKey(ServiceProviderLocations, on_delete=models.CASCADE, null=False)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, null=False)
    ar_title = models.CharField(max_length=128, null=False)
    en_title = models.CharField(max_length=128, null=False)
    ar_description = models.TextField(null=False)
    en_description = models.TextField(null=False)
    images = models.CharField(max_length=128)
    price = models.DecimalField(null=False, max_digits=8, decimal_places=2)
    quantity = models.IntegerField(null=False)
    discounted = models.BooleanField(default=False)
    discount_ammount = models.IntegerField(null=True)
    created_at = models.DateField(auto_now_add=True)
    updated_at = models.DateField(auto_now=True)
    
    def __str__(self) -> str:
        return f"{self.id} -> {self.category}"