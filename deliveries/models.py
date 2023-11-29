from django.db import models

from orders.models import Orders



class Delivery(models.Model):
    order = models.OneToOneField(Orders, on_delete=models.CASCADE, null=False, related_name="delivery")
    paid = models.BooleanField(default=False, null=False)
    delivered = models.BooleanField(default=False)
