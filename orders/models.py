from django.contrib.auth import get_user_model
from django.contrib.gis.db import models

from products.models import Product


User = get_user_model()


class Orders(models.Model):
    patient = models.ForeignKey(User, on_delete=models.CASCADE, null=False)
    created_at = models.DateTimeField(auto_now_add=True)


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
    note = models.TextField(null=True)
    location = models.PointField(srid=4326, null=True) # null to be False
    last_update = models.DateTimeField(auto_now=True)


class CartItems(models.Model):
    patient = models.ForeignKey(User, on_delete=models.CASCADE, null=False, related_name="cart")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, null=False)
    quantity = models.IntegerField(default=1)
    location = models.PointField(srid=4326, null=True) # null to be False
    note = models.TextField(null=True)
    
    def __str__(self) -> str:
        return f"{self.patient.email}: {self.product} -> quantity: {self.quantity}"


class RejectedOrders(models.Model):
    order = models.OneToOneField(
        OrderItem, null=False, on_delete=models.CASCADE, related_name="reject_table", primary_key=True)
    reason = models.TextField(null=False)
    read = models.BooleanField(default=False, null=False)
    
    def __str__(self) -> str:
        return f"{self.order.id}, read: {self.read}"
    