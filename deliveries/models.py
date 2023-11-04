from django.db import models

from orders.models import Orders

class Delivery(models.Model):
    order = models.OneToOneField(Orders, on_delete=models.CASCADE, null=False)
    paid = models.BooleanField(default=False, null=False)
    discount_ammount = models.IntegerField(null=False, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
