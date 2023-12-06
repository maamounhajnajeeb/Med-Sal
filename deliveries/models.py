from django.db import models

from orders.models import OrderItem



class Delivery(models.Model):
    order = models.OneToOneField(OrderItem, on_delete=models.CASCADE, null=False, related_name="delivery")
    delivered = models.BooleanField(default=False)
