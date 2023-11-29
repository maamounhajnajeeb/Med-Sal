from django.contrib.auth import get_user_model
from django.db import models

from products.models import Product


User = get_user_model()

class Orders(models.Model):
    patient = models.ForeignKey(User, on_delete=models.CASCADE, null=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class OrderItem(models.Model):
    
    class StatusChoices(models.TextChoices):
        PENDING = ("PENDING", "Pending")
        REJECTED = ("REJECTED", "Rejected")
        ACCEPTED = ("ACCEPTED", "Accepted")
    
    order = models.ForeignKey(Orders, on_delete=models.CASCADE, related_name="items", null=False)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="orders", null=False)
    quantity = models.IntegerField(default=1)
    price = models.DecimalField(null=False, max_digits=8, decimal_places=2, default=0)
    status = models.CharField(max_length=16, null=False, choices=StatusChoices.choices, default=StatusChoices.PENDING)


class Cart(models.Model):
    patient = models.ForeignKey(User, on_delete=models.CASCADE, null=False)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, null=False)
    quantity = models.IntegerField(default=1)
    price = models.DecimalField(null=False, max_digits=8, decimal_places=2, default=0)
    
    def __str__(self) -> str:
        return f"{self.patient.email}: {self.product} -> quantity: {self.quantity}"


class RejectedOrders(models.Model):
    order = models.OneToOneField(Orders, null=False, on_delete=models.CASCADE)
    reason = models.TextField(null=False)
    attachment = models.FileField(null=True, upload_to="rejected_orders_attachments/")
    read = models.BooleanField(default=False, null=False)
