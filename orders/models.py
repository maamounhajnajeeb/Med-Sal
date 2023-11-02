from django.contrib.auth import get_user_model
from django.db import models

from service_providers.models import ServiceProviderLocations
from products.models import Product


User = get_user_model()

class Orders(models.Model):
    
    class StatusChoices(models.TextChoices):
        PENDING = ("PENDING", "Pending")
        REJECTED = ("REJECTED", "Rejected")
        ACCEPTED = ("ACCEPTED", "Accepted")
    
    patient = models.ForeignKey(User, on_delete=models.CASCADE, null=False)
    service_provider_location = models.ForeignKey(ServiceProviderLocations, on_delete=models.PROTECT, null=False)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, null=False)
    status = models.CharField(max_length=16, null=False, choices=StatusChoices.choices)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class RejectedOrders(models.Model):
    order = models.OneToOneField(Orders, null=False, on_delete=models.CASCADE)
    reason = models.TextField(null=False)
    attachment = models.FileField(null=True, upload_to="rejected_orders_attachments/")
    read = models.BooleanField(default=False, null=False)
    