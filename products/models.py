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
    created_at = models.DateField(auto_now_add=True)
    updated_at = models.DateField(auto_now=True)
    
    def __str__(self) -> str:
        return f"{self.id} -> {self.category}"
    
class ProductStock(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="stock")
    quantity = models.IntegerField()
    created_at = models.DateField(auto_now_add=True, null=False)
    updated_at = models.DateField(auto_now=True, null=False)

    def __str__(self) -> str:
        return f"{self.product} => qty: {self.quantity}, last_update: {self.updated_at}"